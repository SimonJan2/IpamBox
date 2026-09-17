"""Build the import plan: classify+parse sheets, resolve sites/VRFs/prefixes,
dedupe against the DB and within the batch. Pure in-memory output stored in
import_batches.stats — commit executes exactly what was previewed.
"""
import ipaddress
import re
from collections import Counter, defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ip_address import IPAddress
from app.models.ip_range import IPRange
from app.models.prefix import Prefix, PrefixStatus
from app.models.site import Site
from app.models.vlan import VLAN
from app.models.vrf import VRF
from app.services import prefix_math
from app.services.ipam import slugify
from app.services.workbook import normalize as nz
from app.services.workbook.classify import classify_sheet
from app.services.workbook.parsers import PARSERS

HOLDING_SLUG = "imported-unmatched"
HOLDING_NAME = "Imported (unmatched)"
_WORD_RE = re.compile(r"[0-9a-z\u0590-\u05ff]+")


class DbState:
    """Lookup indexes over the current DB contents."""

    def __init__(self):
        self.sites_by_id: dict[int, Site] = {}
        self.site_by_number: dict[int, Site] = {}
        self.site_by_code: dict[str, Site] = {}
        self.site_by_name: dict[str, Site] = {}
        self.vrf_by_name: dict[str, VRF] = {}
        self.prefix_by_key: dict[tuple[int, str], Prefix] = {}
        self.prefix_nets: dict[int, list[tuple[object, Prefix]]] = {}
        self.vlan_by_key: dict[tuple[int | None, int], VLAN] = {}
        self.addr_by_key: dict[tuple[int, int], IPAddress] = {}
        self.range_keys: set[tuple[int, int, int]] = set()


async def load_state(session: AsyncSession) -> DbState:
    st = DbState()
    for s in (await session.execute(select(Site))).scalars():
        st.sites_by_id[s.id] = s
        if s.site_number is not None:
            st.site_by_number[s.site_number] = s
        if s.code:
            st.site_by_code[nz.fold_hebrew(s.code).lower()] = s
        st.site_by_name[nz.fold_hebrew(s.name).lower()] = s
    for v in (await session.execute(select(VRF))).scalars():
        st.vrf_by_name[v.name.lower()] = v
    for p in (await session.execute(select(Prefix))).scalars():
        net = prefix_math.to_network(p.prefix)
        st.prefix_by_key[(p.vrf_id, str(net))] = p
        st.prefix_nets.setdefault(p.vrf_id, []).append((net, p))
    for v in (await session.execute(select(VLAN))).scalars():
        st.vlan_by_key[(v.site_id, v.vid)] = v
    for a in (await session.execute(select(IPAddress))).scalars():
        st.addr_by_key[(a.vrf_id, int(a.address_int))] = a
    for r in (await session.execute(select(IPRange))).scalars():
        st.range_keys.add((r.vrf_id, int(r.start_int), int(r.end_int)))
    return st


# ---------------------------------------------------------------------------
# plan key helpers
# ---------------------------------------------------------------------------


def _site_key(site: Site | None, fallback: str) -> str:
    if site is None:
        return f"new:{fallback}"
    return f"id:{site.id}"


def _vrf_name_for(site_name: str, code: str | None, number: int | None) -> str:
    if code:
        return code
    if number is not None:
        return f"site-{number}"
    return slugify(site_name)[:60]


class _Planner:
    def __init__(self, st: DbState, options):
        self.st = st
        self.opt = options
        self.plan: dict[str, list[dict]] = {
            k: []
            for k in (
                "sites", "vrfs", "prefixes", "ranges", "addresses",
                "circuits", "certificates", "assets", "services",
            )
        }
        self.rows: list[dict] = []
        self.sheet_previews: list[dict] = []
        self._sites: dict[str, dict] = {}   # site_key -> plan site entry
        self._vrfs: dict[str, dict] = {}    # vrf_key -> plan vrf entry
        self._prefixes: dict[str, dict] = {}
        self._vlans: dict[tuple[str, int], int | None] = {}
        self._holding_key: str | None = None
        self._planned_addrs: dict[tuple[str, str], dict] = {}
        self._planned_nets: dict[str, list[tuple[object, str]]] = {}
        self._existing_vrf_for_site: dict[str, VRF] = {}
        # (first, second) octet pair -> site_key, seeded by sites-master rows
        # so non-10.x networks (Integration's 172.20-21.x) resolve correctly
        self._block_site: dict[tuple[int, int], str] = {}

    # -- reporting ------------------------------------------------------

    def report(self, sheet, row, action, detail):
        self.rows.append(
            {"sheet": sheet, "row": row, "action": action, "detail": detail}
        )

    # -- site/vrf/prefix scaffolding ------------------------------------

    def _register_site(self, site: Site) -> str:
        key = _site_key(site, "")
        if key not in self._sites:
            self._sites[key] = {
                "key": key, "action": "exists", "site_id": site.id,
                "name": site.name, "code": site.code,
                "site_number": site.site_number, "size": site.size,
                "is_active": site.is_active,
            }
        return key

    def _new_site(self, name, code=None, number=None, size=None,
                  is_active=True, notes=None) -> str:
        key = f"new:{code or (f'num{number}' if number is not None else slugify(name))}"
        if key not in self._sites:
            self._sites[key] = {
                "key": key, "action": "create", "site_id": None,
                "name": name, "code": code, "site_number": number,
                "size": size, "is_active": is_active, "notes": notes,
            }
        return key

    def _holding_site(self) -> str:
        if self._holding_key is None:
            existing = self.st.site_by_name.get(nz.fold_hebrew(HOLDING_NAME).lower())
            if existing is not None:
                self._holding_key = self._register_site(existing)
            else:
                self._holding_key = f"new:{HOLDING_SLUG}"
                self._sites[self._holding_key] = {
                    "key": self._holding_key, "action": "create",
                    "site_id": None, "name": HOLDING_NAME, "code": None,
                    "site_number": None, "size": None, "is_active": True,
                    "notes": "created by workbook import — sheets with no site match",
                }
        return self._holding_key

    def _vrf_key(self, site_key: str) -> str:
        if site_key in self._vrfs:
            return site_key
        site = self._sites[site_key]
        name = _vrf_name_for(site["name"], site.get("code"), site.get("site_number"))
        existing = self.st.vrf_by_name.get(name.lower())
        if existing is not None:
            self._vrfs[site_key] = {
                "key": site_key, "site_key": site_key, "name": existing.name,
                "action": "exists", "vrf_id": existing.id,
            }
        else:
            self._vrfs[site_key] = {
                "key": site_key, "site_key": site_key, "name": name,
                "action": "create", "vrf_id": None,
            }
        return site_key

    def _vrf_id(self, vrf_key: str) -> int | None:
        return self._vrfs[vrf_key]["vrf_id"]

    def _site_id(self, site_key: str) -> int | None:
        return self._sites[site_key]["site_id"]

    def _vlan_id(self, site_key: str, vid: int | None) -> int | None:
        if vid is None:
            return None
        sid = self._site_id(site_key)
        existing = self.st.vlan_by_key.get((sid, vid))
        return existing.id if existing else None

    def _prefix(self, vrf_key: str, site_key: str, cidr: str, *,
                status: str, description: str | None, vlan_vid=None,
                vlan_name=None) -> str:
        net = None
        try:
            net = ipaddress.ip_network(cidr, strict=False)
            cidr = str(net)
        except ValueError:
            pass  # keep raw — will surface as an error at execute time
        key = f"{vrf_key}|{cidr}"
        if key in self._prefixes:
            p = self._prefixes[key]
            if vlan_name and not p.get("vlan_name"):
                p["vlan_name"], p["vlan_vid"] = vlan_name, vlan_vid
            return key
        vrf_id = self._vrf_id(vrf_key)
        existing = self.st.prefix_by_key.get((vrf_id, cidr)) if vrf_id else None

        # The DB exclusion constraint forbids overlapping non-container
        # prefixes inside a VRF. CIDRs either nest or are disjoint, so:
        #  - inside a planned covering prefix -> covering becomes a container
        #  - inside a DB non-container prefix -> reuse it instead of nesting
        #  - covering existing children     -> this new prefix is a container
        if net is not None and existing is None:
            for other_net, pkey in self._planned_nets.get(vrf_key, []):
                if net.subnet_of(other_net):
                    self._prefixes[pkey]["status"] = "container"
                elif other_net.subnet_of(net):
                    status = "container"
            if vrf_id:
                for other_net, db_prefix in self.st.prefix_nets.get(vrf_id, []):
                    if net.subnet_of(other_net):
                        if str(other_net) == cidr:
                            break
                        if db_prefix.status != "container":
                            # reuse the existing covering prefix rather than
                            # nesting (never mutate pre-import rows)
                            cov_key = f"{vrf_key}|{other_net}"
                            if cov_key not in self._prefixes:
                                self._prefixes[cov_key] = {
                                    "key": cov_key, "vrf_key": vrf_key,
                                    "site_key": site_key,
                                    "cidr": str(other_net), "status": "active",
                                    "description": db_prefix.description,
                                    "vlan_vid": None, "vlan_name": None,
                                    "vlan_id": None, "action": "exists",
                                    "prefix_id": db_prefix.id,
                                }
                            return cov_key
                    elif other_net.subnet_of(net) and db_prefix.status != "container":
                        status = "container"
            self._planned_nets.setdefault(vrf_key, []).append((net, key))

        self._prefixes[key] = {
            "key": key, "vrf_key": vrf_key, "site_key": site_key,
            "cidr": cidr, "status": status, "description": description,
            "vlan_vid": vlan_vid, "vlan_name": vlan_name,
            "vlan_id": self._vlan_id(site_key, vlan_vid),
            "action": "exists" if existing else "create",
            "prefix_id": existing.id if existing else None,
        }
        return key

    def _prefix_id(self, prefix_key: str) -> int | None:
        return self._prefixes[prefix_key]["prefix_id"]

    # -- record handlers --------------------------------------------------

    def add_sites_master(self, records: list[dict]):
        for r in records:
            existing = None
            if r["code"]:
                existing = self.st.site_by_code.get(nz.fold_hebrew(r["code"]).lower())
            if existing is None and r["site_number"] is not None:
                existing = self.st.site_by_number.get(r["site_number"])
            if existing is None:
                existing = self.st.site_by_name.get(
                    nz.fold_hebrew(r["name"]).lower()
                )
            if existing is not None:
                key = self._register_site(existing)
                action, detail = "exists", f"site exists: {existing.name}"
            else:
                slug = r["code"] or (
                    f"num{r['site_number']}"
                    if r["site_number"] is not None
                    else slugify(r["name"])
                )
                prior = self._sites.get(f"new:{slug}")
                key = self._new_site(
                    r["name"], code=r["code"], number=r["site_number"],
                    size=r["size"], is_active=r["is_active"], notes=r["notes"],
                )
                if prior is None and r.get("synthetic_name"):
                    # name was synthesized from the row's block — a matching
                    # sheet may claim its real title later (Site 35 -> ג'למה)
                    self._sites[key]["synthetic"] = True
                if prior is not None and prior["name"] != r["name"]:
                    # e.g. Mashapan TA + MATPASH both number 200 — merging
                    # loses a name, so surface it instead of hiding it
                    action, detail = "conflict", (
                        f"{r['name']}: same site key as "
                        f"{prior['name']} — merged into it"
                    )
                elif prior is not None:
                    if prior.get("site_number") != r["site_number"]:
                        # same code/name but different number (Tarkumia 32/51)
                        # — a real ambiguity, not a clean duplicate
                        action, detail = "conflict", (
                            f"{r['name']} (site {r['site_number']}): same "
                            f"code/name as {prior['name']} (site "
                            f"{prior.get('site_number')}) — merged"
                        )
                    else:
                        action, detail = "exists", f"duplicate master row: {r['name']}"
                else:
                    for s in self._sites.values():
                        if (
                            s["key"] != key
                            and nz.fold_hebrew(s.get("name") or "").lower()
                            == nz.fold_hebrew(r["name"]).lower()
                        ):
                            action, detail = "conflict", (
                                f"{r['name']}: duplicate site name "
                                f"(also site {s.get('site_number')})"
                            )
                            break
                    else:
                        action, detail = "create", f"new site: {r['name']}"
            self.report(r["sheet"], r["row"], action, detail)
            # non-10.x blocks (and 10.x pairs) let sheet octets find this site
            for pair in r.get("blocks") or ():
                claimant = self._block_site.get(pair)
                if claimant is not None and claimant != key:
                    self.report(
                        r["sheet"], r["row"], "conflict",
                        f"block {pair[0]}.{pair[1]}.x also claimed by "
                        f"{self._sites[claimant]['name']} — first wins",
                    )
                else:
                    self._block_site[pair] = key
            # sites-master subnet becomes a real prefix under the site's VRF
            if r.get("cidr"):
                vrf_key = self._vrf_key(key)
                self._prefix(
                    vrf_key, key, r["cidr"], status="active",
                    description="from sites master list",
                )

    @staticmethod
    def _sheet_octets(records: list[dict]) -> Counter:
        """(first, second) octet-pair histogram of a sheet's addresses.
        Counting full pairs keeps non-10.x networks visible — INTEGRATION is
        mostly 172.20/21.x and must not collapse onto site 10 just because a
        few 10.10.x rows exist."""
        c: Counter = Counter()
        for r in records:
            ip = str(r.get("address") or r.get("network_base") or "")
            parts = ip.split(".")
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                c[(int(parts[0]), int(parts[1]))] += 1
        return c

    @staticmethod
    def _title_hits(title: str, name: str | None, code: str | None) -> bool:
        """Folded sheet title vs site name/code — word-boundary matching so
        'int' doesn't match 'maintenence rehvt'."""
        words = set(_WORD_RE.findall(title))
        c = nz.fold_hebrew(code or "").lower()
        if c and c in words:
            return True
        n = nz.fold_hebrew(name or "").lower()
        if n and n in title:
            return True
        return any(len(w) >= 4 and w in words for w in _WORD_RE.findall(n))

    def _match_site_title(self, title: str) -> str | None:
        """Sheet title -> site key via code/name. Checks DB sites first, then
        sites planned earlier in this batch (fresh import has only those)."""
        for site in self.st.sites_by_id.values():
            if self._title_hits(title, site.name, site.code):
                return self._register_site(site)
        for key, s in self._sites.items():
            if self._title_hits(title, s.get("name"), s.get("code")):
                return key
        return None

    def _claim_synthetic_name(self, site_key: str, sheet_name: str) -> None:
        """A sheet that octet-matches a master row with no real name gives
        the site its title — 'Site 35' becomes 'ג'למה' so users can find it.
        First claimant wins; the flag clears so later sheets don't rename."""
        s = self._sites.get(site_key)
        title = nz.clean(sheet_name)[:255]
        if s is not None and s.get("synthetic") and title:
            s["name"] = title
            s["synthetic"] = False
            self.report(
                sheet_name, 0, "update",
                "master row had no name — site named from this sheet's title",
            )

    def _site_for_10x(self, second: int, sheet_name: str) -> tuple[str, str]:
        """Resolve a 10.{second}.x sheet — site_number is only meaningful
        inside the 10.0.0.0/8 plan. Falls back to a new site named after the
        sheet ('רמון' says more than 'Site 10.100.x')."""
        site = self.st.site_by_number.get(second)
        if site is not None:
            return self._register_site(site), "octet"
        for key, s in self._sites.items():
            if s.get("site_number") == second:
                self._claim_synthetic_name(key, sheet_name)
                return key, "octet"
        title_name = nz.clean(sheet_name)[:255] or f"Site 10.{second}.x"
        return self._new_site(title_name, number=second), "octet-new"

    def resolve_sheet_site(self, sheet_name: str, octets: Counter) -> tuple[str, str | None]:
        """site_key, matched_by for a site_sheet."""
        override = self.opt.site_overrides.get(sheet_name)
        if override is not None:
            site = self.st.sites_by_id.get(override)
            if site is not None:
                return self._register_site(site), "override"
        title = nz.fold_hebrew(sheet_name).lower()
        if octets:
            first, second = octets.most_common(1)[0][0]
            block_key = self._block_site.get((first, second))
            if block_key is not None:
                self._claim_synthetic_name(block_key, sheet_name)
                return block_key, "octet"
            if first == 10:
                return self._site_for_10x(second, sheet_name)
            # non-10.x dominant block, undeclared (Cellular's 172.30.x,
            # Sapiens' 172.16.x): try the title, then let a minority 10.x
            # pair anchor the site before giving up to the holding site
            hit = self._match_site_title(title)
            if hit is not None:
                return hit, "name"
            ten = next((p for p, _n in octets.most_common() if p[0] == 10), None)
            if ten is not None:
                block_key = self._block_site.get(ten)
                if block_key is not None:
                    self._claim_synthetic_name(block_key, sheet_name)
                    return block_key, "octet"
                return self._site_for_10x(ten[1], sheet_name)
            return self._holding_site(), None
        hit = self._match_site_title(title)
        if hit is not None:
            return hit, "name"
        return self._holding_site(), None

    def add_site_records(self, sheet_name: str, site_key: str, records: list[dict]):
        vrf_key = self._vrf_key(site_key)
        site = self._sites[site_key]
        if self.opt.create_containers and site.get("site_number") is not None:
            self._prefix(
                vrf_key, site_key, f"10.{site['site_number']}.0.0/16",
                status="container", description="site block (imported)",
            )
        for r in records:
            if r["kind"] == "invalid":
                self.report(
                    sheet_name, r["row"], "skip",
                    f"needs review: {r['detail']}",
                )
                continue
            if r["kind"] == "skip":
                self.report(sheet_name, r["row"], "skip", r["detail"])
                continue
            if r["kind"] == "subnet":
                # fragment-only row -> the subnet itself (x.y.z.0/mask)
                net = nz.network_of(r["network_base"] + ".0", r["mask"]) or str(
                    ipaddress.ip_network(f"{r['network_base']}.0/24", strict=False)
                )
                self._prefix(
                    vrf_key, site_key, net, status="active",
                    description=r.get("description")
                    or f"subnet declared in {sheet_name}",
                )
                self.report(sheet_name, r["row"], "create", f"prefix {net}")
                continue
            if r["kind"] == "host_no_ip":
                # keep the row as a hardware/server asset rather than losing
                # hostname, guest OS, cert, license and owner entirely
                cf = dict(r.get("custom_fields") or {})
                bits = [
                    b
                    for b in (
                        cf.get("guest_os"), cf.get("cert"),
                        cf.get("license"), cf.get("owner"),
                    )
                    if b
                ]
                self.plan["assets"].append(
                    {
                        "sheet": sheet_name, "row": r["row"],
                        "site_key": site_key, "kind": "hardware",
                        "category": "server", "vendor": None,
                        "model": (r.get("hostname") or "server")[:255],
                        "purpose": cf.get("guest_os"), "version": None,
                        "eol_on": None, "support_status": None,
                        "serial_number": None, "site_name": None,
                        "notes": " | ".join(bits) or None,
                    }
                )
                self.report(
                    sheet_name, r["row"], "create",
                    f"{r['hostname']}: server asset (no IP)",
                )
                continue
            # 'מוגדר תחת אתר' may reassign the row — by site name/code first;
            # a bare number only. Digits inside names ('טרמינל 3 כניסה')
            # must NOT reassign the row to site 3.
            row_vrf = vrf_key
            row_site = site_key
            if r.get("under_site"):
                u = nz.clean(r["under_site"])
                alt_key = self._planned_site(name=u) or self._planned_site(code=u)
                if alt_key is None and u.isdigit():
                    alt_key = self._planned_site(number=int(u))
                if alt_key is not None:
                    row_site = alt_key
                row_vrf = self._vrf_key(row_site)

            if r["kind"] == "range":
                self._add_range(sheet_name, r, row_vrf, row_site)
                continue

            ip = r["address"]
            cidr = nz.network_of(ip, r["mask"]) or str(
                ipaddress.ip_network(f"{ip}/24", strict=False)
            )
            pkey = self._prefix(
                row_vrf, row_site, cidr, status="active",
                description=f"imported from {sheet_name}",
                vlan_vid=r.get("vlan_vid"), vlan_name=r.get("vlan_name"),
            )
            self._add_address(sheet_name, r, row_vrf, row_site, pkey, ip)

    def _add_range(self, sheet, r, vrf_key, site_key):
        lo, hi = r["range"]
        cidr = nz.network_of(lo, r["mask"]) or str(
            ipaddress.ip_network(f"{lo}/24", strict=False)
        )
        pkey = self._prefix(
            vrf_key, site_key, cidr, status="active",
            description=f"imported from {sheet}",
        )
        lo_i, hi_i = int(ipaddress.ip_address(lo)), int(ipaddress.ip_address(hi))
        vrf_id = self._vrf_id(vrf_key)
        if vrf_id is not None and (vrf_id, lo_i, hi_i) in self.st.range_keys:
            self.report(sheet, r["row"], "skip", f"range {lo}-{hi} exists")
            return
        role = "dhcp" if "dhcp" in nz.fold_hebrew(
            f"{r.get('hostname') or ''} {r.get('description') or ''}"
        ).lower() else "reserved"
        self.plan["ranges"].append(
            {
                "sheet": sheet, "row": r["row"], "vrf_key": vrf_key,
                "prefix_key": pkey, "lo": lo, "hi": hi, "role": role,
                "description": r.get("description"),
            }
        )
        self.report(sheet, r["row"], "create", f"range {lo} - {hi} ({role})")

    def _add_address(self, sheet, r, vrf_key, site_key, pkey, ip):
        status, raw = nz.map_status(r.get("status_text") or "")
        if status == "skip":
            self.report(sheet, r["row"], "skip", f"{ip}: status בוטל")
            return
        cf = dict(r.get("custom_fields") or {})
        if raw:
            cf["status_raw"] = raw
        if r.get("mask") and nz.mask_to_prefixlen(r["mask"]) is None:
            # unparseable mask fell back to /24 in network_of — keep the raw
            # value visible instead of silently discarding it
            cf.setdefault("mask_raw", r["mask"])
        if r.get("mac_raw"):
            cf["mac_raw"] = r["mac_raw"]
        if r.get("model"):
            cf.setdefault("model", r["model"])
        if r.get("description"):
            cf.setdefault("description", r["description"])

        key = (vrf_key, ip)
        prev = self._planned_addrs.get(key)
        if prev is not None:
            # same site+sheet duplicate — merge non-empty fields into first
            merged = False
            for f in ("hostname", "mac", "serial", "switch", "port", "counter"):
                if not prev["row"].get(f) and r.get(f):
                    prev["row"][f] = r[f]
                    merged = True
            self.report(
                sheet, r["row"], "conflict",
                f"{ip}: duplicate in batch — merged into earlier row"
                if merged else f"{ip}: duplicate in batch — skipped",
            )
            return

        vrf_id = self._vrf_id(vrf_key)
        existing = (
            self.st.addr_by_key.get((vrf_id, int(ipaddress.ip_address(ip))))
            if vrf_id is not None
            else None
        )
        row = {
            "sheet": sheet, "row": r["row"], "vrf_key": vrf_key,
            "prefix_key": pkey, "address": ip,
            "hostname": r.get("hostname"), "mac": r.get("mac"),
            "status": status, "serial": r.get("serial"),
            "switch": r.get("switch"), "port": r.get("port"),
            "counter": r.get("counter"), "custom_fields": cf or None,
            "notes": r.get("notes") or r.get("description"),
            "model": r.get("model"),
        }
        if existing is not None:
            fills = [
                f
                for f, cur, new in (
                    ("hostname", existing.hostname, row["hostname"]),
                    ("mac_address", existing.mac_address, row["mac"]),
                    ("serial_number", existing.serial_number, row["serial"]),
                    ("switch_name", existing.switch_name, row["switch"]),
                    ("switch_port", existing.switch_port, row["port"]),
                    ("counter_location", existing.counter_location, row["counter"]),
                    ("notes", existing.notes, row["notes"]),
                )
                if new and not cur
            ]
            action = "update" if fills else "skip"
            detail = (
                f"{ip}: exists — filling {', '.join(fills)}"
                if fills else f"{ip}: already exists"
            )
            row["target_id"] = existing.id
            row["fills"] = fills
        else:
            action, detail = "create", f"{ip}"
        self._planned_addrs[key] = {"action": action, "row": row}
        self.plan["addresses"].append({**row, "action": action})
        self.report(sheet, r["row"], action, detail)

    # -- entity families -------------------------------------------------

    def _planned_site(self, *, number=None, code=None, name=None) -> str | None:
        """Match a site among pre-existing DB rows AND sites already planned
        in this batch — the first import has every site only in _sites."""
        if number is not None:
            s = self.st.site_by_number.get(number)
            if s is not None:
                return self._register_site(s)
            for key, p in self._sites.items():
                if p.get("site_number") == number:
                    return key
        if code:
            s = self.st.site_by_code.get(nz.fold_hebrew(code).lower())
            if s is not None:
                return self._register_site(s)
            folded = nz.fold_hebrew(code).lower()
            for key, p in self._sites.items():
                if p.get("code") and nz.fold_hebrew(p["code"]).lower() == folded:
                    return key
        if name:
            s = self.st.site_by_name.get(nz.fold_hebrew(name).lower())
            if s is not None:
                return self._register_site(s)
            folded = nz.fold_hebrew(name).lower()
            for key, p in self._sites.items():
                if p.get("name") and nz.fold_hebrew(p["name"]).lower() == folded:
                    return key
        return None

    def add_circuits(self, records: list[dict]):
        for r in records:
            site_key = self._planned_site(number=r.get("site_number"))
            if site_key is None:
                site_key = self._planned_site(code=r.get("site_code"))
            self.plan["circuits"].append({**r, "site_key": site_key})
            self.report(
                r["sheet"], r["row"], "create",
                r.get("bezeq_circuit_id") or r.get("site_name") or "circuit",
            )

    def add_certificates(self, records: list[dict]):
        for r in records:
            self.plan["certificates"].append(r)
            self.report(
                r["sheet"], r["row"], "create",
                r.get("cert_name") or r.get("server_name") or "certificate",
            )

    def add_assets(self, records: list[dict]):
        for r in records:
            site_key = self._planned_site(name=r.get("site_name"))
            self.plan["assets"].append({**r, "site_key": site_key})
            self.report(
                r["sheet"], r["row"], "create",
                r.get("serial_number") or r.get("model") or "asset",
            )

    def add_services(self, records: list[dict]):
        for r in records:
            site_key = None
            if r.get("site_code"):
                site_key = self._planned_site(code=r["site_code"])
                if site_key is None and r["site_code"].isdigit():
                    site_key = self._planned_site(number=int(r["site_code"]))
            self.plan["services"].append({**r, "site_key": site_key})
            self.report(r["sheet"], r["row"], "create", r.get("name") or "service")

    def _site_warnings(self, sheet_name: str, site: dict, how: str | None) -> list[str]:
        """Honesty checks on an octet/name match — inactive sites and
        title/site disagreements surface as warnings, not silent picks."""
        out = []
        title = nz.fold_hebrew(sheet_name).lower()
        if how == "octet":
            if site.get("is_active") is False:
                out.append("matched site is marked inactive in the master list")
            if re.search(r"[a-zA-Z]", sheet_name) and not self._title_hits(
                title, site.get("name"), site.get("code")
            ):
                out.append(
                    f"sheet title doesn't resemble matched site "
                    f"'{site.get('name')}' — verify assignment"
                )
        if how == "name":
            # full name-in-title or a code word is solid; a lone shared word
            # ('Sapiens (Holon)' -> 'Sapiens(Rehovot)') is worth flagging
            n = nz.fold_hebrew(site.get("name") or "").lower()
            c = nz.fold_hebrew(site.get("code") or "").lower()
            if n not in title and c not in set(_WORD_RE.findall(title)):
                out.append(
                    f"partial name match to '{site.get('name')}' — verify"
                )
        if how is None:
            out.append("no site match — landed in Imported (unmatched)")
        return out

    # -- driver ------------------------------------------------------------

    def build(self, sheets) -> dict:
        parsed: dict[str, tuple[str, int, list, list]] = {}
        for sm in sheets:
            family, hidx, warns = classify_sheet(sm)
            records: list = []
            if family in PARSERS and family != "sites_master":
                records, pw = PARSERS[family](sm, hidx)
                warns += pw
            parsed[sm.name] = (family, hidx, records, warns)

        # sites master first — it seeds the site map everything else uses
        for sm in sheets:
            family, hidx, _rec, warns = parsed[sm.name]
            if family == "sites_master":
                records, pw = parse_sites_master_records(sm, hidx)
                self.add_sites_master(records)
                parsed[sm.name] = (family, hidx, records, warns + pw)

        # pre-pass: resolve every address sheet's site BEFORE entity families
        # run — a circuits sheet early in the workbook must still see sites
        # created by site sheets at the end of it
        for sm in sheets:
            family, _hidx, records, _warns = parsed[sm.name]
            if family in ("site_sheet", "servers") and sm.name not in self.opt.skip_sheets:
                self.resolve_sheet_site(sm.name, self._sheet_octets(records))

        for sm in sheets:
            family, _hidx, records, warns = parsed[sm.name]
            if family == "empty" or sm.name in self.opt.skip_sheets:
                self.sheet_previews.append(
                    _preview(sm, family, len(records), warns, None, None, None)
                )
                continue
            if family == "site_sheet":
                octets = self._sheet_octets(records)
                site_key, how = self.resolve_sheet_site(sm.name, octets)
                self.add_site_records(sm.name, site_key, records)
                site = self._sites[site_key]
                self.sheet_previews.append(
                    _preview(sm, family, len(records),
                             warns + self._site_warnings(sm.name, site, how),
                             site.get("site_id"), site.get("name"), how)
                )
            elif family == "circuits":
                self.add_circuits(records)
                self.sheet_previews.append(_preview(sm, family, len(records), warns, None, None, None))
            elif family == "certificates":
                self.add_certificates(records)
                self.sheet_previews.append(_preview(sm, family, len(records), warns, None, None, None))
            elif family in ("assets", "inventory"):
                self.add_assets(records)
                self.sheet_previews.append(_preview(sm, family, len(records), warns, None, None, None))
            elif family == "services":
                self.add_services(records)
                self.sheet_previews.append(_preview(sm, family, len(records), warns, None, None, None))
            elif family == "servers":
                octets = self._sheet_octets(records)
                site_key, how = self.resolve_sheet_site(sm.name, octets)
                self.add_site_records(sm.name, site_key, records)
                site = self._sites[site_key]
                self.sheet_previews.append(
                    _preview(sm, "servers", len(records),
                             warns + self._site_warnings(sm.name, site, how),
                             site.get("site_id"), site.get("name"), how)
                )
            elif family == "sites_master":
                self.sheet_previews.append(_preview(sm, family, len(records), warns, None, None, None))
            else:
                self.sheet_previews.append(
                    _preview(sm, "unknown", 0,
                             warns + ["unrecognized sheet layout — skipped"],
                             None, None, None)
                )

        self.plan["sites"] = list(self._sites.values())
        self.plan["vrfs"] = list(self._vrfs.values())
        self.plan["prefixes"] = list(self._prefixes.values())
        counts = Counter(r["action"] for r in self.rows)
        return {
            "sheets": self.sheet_previews,
            "plan": self.plan,
            "counts": dict(counts),
            "rows": self.rows,
        }


def _preview(sm, family, rows, warnings, site_id, site_name, matched_by):
    headers = []
    for row in sm.rows[:10]:
        hs = [nz.clean(c) for c in row]
        if any(hs):
            headers = [h for h in hs if h][:20]
            break
    return {
        "sheet": sm.name,
        "family": family,
        "rows": rows,
        "headers": headers,
        "site_id": site_id,
        "site_name": site_name,
        "matched_by": matched_by,
        "warnings": warnings,
    }


def parse_sites_master_records(sm, hidx):
    from app.services.workbook.parsers import parse_sites_master

    return parse_sites_master(sm, hidx)


async def build_import_plan(
    session: AsyncSession, sheets, options
) -> dict:
    st = await load_state(session)
    return _Planner(st, options).build(sheets)
