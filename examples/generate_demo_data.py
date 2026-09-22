#!/usr/bin/env python3
"""Generate fictional demo import files for IpamBox.

Every value is INVENTED — site names, IPs, serials, MACs, circuit IDs,
contacts and paths are synthetic and do not describe any real network.
The files mirror the *shape* of a real-world Network_Address.xlsx so the
import wizard exercises every sheet family and parser edge case.

Regenerate:  python3 examples/generate_demo_data.py
Requires:    openpyxl (already a backend dependency)
Output:      this directory (files listed in main())
"""
from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import openpyxl

SEED = 20260922
HERE = Path(__file__).resolve().parent
EXCEL_EPOCH = date(1899, 12, 30)
# fixed workbook timestamps -> deterministic zip bytes across runs
_FIXED_TS = datetime(2026, 9, 22, 12, 0, 0)


def excel_serial(d: date) -> int:
    return (d - EXCEL_EPOCH).days


# ---------------------------------------------------------------------------
# fictional data pools — nothing below maps to a real site, person or device
# ---------------------------------------------------------------------------

HEBREW_SITE_NAMES = [
    "צפון דמו", "דרום דמו", "מזרח דמו", "מערב דמו", "גבעת דוגמה",
    "נחל דמה", "כפר דוגמה", "עין דמה", "רמת דמה", "שדה דוגמה",
    "מפרץ דמה", "בקעת דמה", "הר דוגמה", "עמק דמה", "צוק דמה",
    "מעבר דמה", "נמל דמה", "תל דמה", "גן דוגמה", "מחנה דמה",
    "תחנת דמה", "קריית דוגמה", "מרכז דמה", "שער דמה", "חוות דוגמה",
    "מעוז דמה", "מצודת דמה", "סלע דמה", "פסגת דמה", "אגם דמה",
    "יער דמה", "מדבר דמה", "חוף דמה", "גשר דמה", "טיילת דמה",
]

ENGLISH_SITE_NAMES = [
    "Harbor View", "Northgate", "Cedar Ridge", "Ironbridge", "Lakepoint",
    "Stonefield", "Westbrook", "Maple Court", "Red Canyon", "Foxglove",
    "Windmere", "Oakhaven", "Pinecrest", "Rivergate", "Summit Point",
    "Goldfield", "Mariner Bay", "Cloudrest", "Ferndale", "Briarcliff",
    "Elm Crossing", "Saltmarsh", "Kestrel Point", "Driftwood", "Copperline",
    "Silverleaf", "Longmeadow", "Ashford", "Blackpine", "Coral Bay",
    "Dunmore", "Eastvale", "Fairbanks", "Greenhollow", "Highmarsh",
    "Inverness", "Juniper Flats", "Kingsport", "Larkspur", "Millbrook",
    "Newhaven", "Otter Creek", "Pembroke", "Quarry Hill", "Rosemont",
    "Stonebridge", "Tanglewood", "Upland", "Vernon Falls", "Whitecliff",
    "Yarrow Point", "Zephyr Cove", "Amberfield", "Brookside", "Coldwater",
    "Deephaven", "Edgewater", "Glenwood", "Holloway", "Ivydale",
    "Jasper Ridge", "Lakeshore", "Moonstone", "Oyster Bay", "Pinnacle",
    "Ravenna", "Starling", "Tidewater", "Willowbend",
]

EN_ONLY_SITE_NAMES = [
    "Alpine Gate", "Beacon Hill", "Cobalt Bay", "Dover Plains", "Elm Park",
    "Falcon Ridge", "Granite Falls", "Hollybrook", "Iron Gate", "Jade Cove",
    "Keystone", "Lion Rock", "Misty Vale", "Nova Point", "Orchard Hill",
    "Palm Harbor", "Quartz Ridge", "Redwood", "Sandy Hook", "Thunder Bay",
    "Union Mills", "Valley Forge", "Walnut Grove", "Xavier Field", "Yaletown",
    "Zebra Crossing", "Anchor Point", "Birchwood", "Cliffside", "Deer Creek",
]

HE_SIZES = ["גדול", "בינוני", "קטן"]
EN_SIZES = ["Large", "Medium", "Small"]

HOST_PREFIXES = ["srv", "prt", "cam", "sw", "rt", "pc", "ups", "ap", "nvr", "plc"]

# Designed enterprise VLAN scheme — (vid, name, group). Each site maps its
# subnets onto a subset of these, so subnet <-> VLAN is consistent inside a
# sheet and VLAN records get created with readable names on commit.
VLAN_PLAN = [
    (5,   "MGMT",        "Infrastructure"),
    (6,   "OOB",         "Infrastructure"),
    (10,  "USERS",       "Corporate"),
    (20,  "VOICE",       "Corporate"),
    (30,  "PRINTERS",    "Corporate"),
    (40,  "GUEST",       "Corporate"),
    (50,  "WIFI-CORP",   "Corporate"),
    (100, "SERVERS",     "Data Center"),
    (110, "STORAGE",     "Data Center"),
    (120, "BACKUP",      "Data Center"),
    (200, "IOT",         "OT & IoT"),
    (210, "CAMERAS",     "OT & IoT"),
    (220, "ACCESS-CTRL", "OT & IoT"),
    (999, "QUARANTINE",  "Security"),
]

# which functional VLANs a site of each size would run
_SIZE_VLANS = {
    "גדול":  [5, 6, 10, 20, 30, 50, 100, 110, 120, 210],
    "Large": [5, 6, 10, 20, 30, 50, 100, 110, 120, 210],
    "בינוני": [10, 20, 30, 50, 200, 220],
    "Medium": [10, 20, 30, 50, 200, 220],
    "קטן":   [10, 30, 40],
    "Small": [10, 30, 40],
}
_VLANS_BY_VID = {vid: (vid, name, grp) for vid, name, grp in VLAN_PLAN}


def vlan_cell(vid: int, name: str) -> str:
    """Cell text that parses to (vid, 'VLANx-NAME') in the importer."""
    return f"VLAN{vid}-{name}"


def _site_vlans(site: dict) -> list[tuple[int, str, str]]:
    """The VLAN set a site of this size runs — deterministic per site."""
    vids = _SIZE_VLANS.get(site["size"], _SIZE_VLANS["Small"])
    return [_VLANS_BY_VID[v] for v in vids]


def _vlan_for(site: dict, subnet: int) -> str:
    v = site.get("_vlan_map", {}).get(subnet)
    return vlan_cell(v[0], v[1]) if v else ""

MODELS = [
    "Cisco C9300-48P", "Aruba 2930F", "Dell PowerEdge R640",
    "HPE ProLiant DL380", "DemoSwitch 48", "DemoRouter XR",
    "Axis DemoCam P32", "Kyocera DemoPrint 4000", "APC DemoUPS 3000",
]

EN_DESCRIPTIONS = [
    "demo workstation", "demo printer", "uplink to core", "demo camera",
    "reserved for demo", "dhcp pool - demo", "demo access point",
    "demo plc controller", "spare - demo", "demo voip phone",
]

HE_DESCRIPTIONS = [
    "עמדת דמו", "מדפסת דמו", "שרת דמו", "מצלמת דמו", "שמור לדמו",
    "נקודת גישה דמו", "טלפון דמו", "מתג דמו", "תחנת דמו",
]

HE_NOTES = [
    "פעיל", "פעיל", "פעיל", "בהקמה", "לא פעיל", "", "", "",
    "הוסר - נשאר לתיעוד", "הועבר לקומה 2", "",
]

EN_NOTES = [
    "active", "active", "in build", "offline", "", "", "",
    "moved to floor 2", "kept for records", "",
]

OWNERS = ["ops-lead", "noc-team", "infra-demo", "sysdesk"]

GUEST_OS = [
    "Microsoft Windows Server 2022 (64-bit)",
    "Microsoft Windows 11 (64-bit)",
    "Ubuntu Linux (64-bit)",
    "Rocky Linux 9 (64-bit)",
    "VMware Photon OS (64-bit)",
]

VENDORS = ["Dell", "HPE", "F5", "VMware", "Check Point", "Cisco", "DemoSoft"]

CERT_PLATFORMS = ["F5", "IIS", "NGINX", "Apache", "DemoLB"]

DEMO_DOMAINS = [
    "api.demo.local", "web.demo.local", "*.demo.local",
    "mail.demo.local", "vpn.demo.local", "files.demo.local",
]

# TEST-NET-3 (RFC 5737) — documentation-only range, safe for WAN demos
WAN_BASE = "203.0.113."

# 10.x second-octet pools verified unused by the real workbook — demo sites
# never share an octet block with a real site.
MIXED_OCTETS = (list(range(130, 160)) + list(range(201, 226))
                + list(range(227, 234)))
MIXED_EXTRA_OCTETS = (list(range(234, 246)) + list(range(185, 190))
                      + list(range(194, 200)) + list(range(165, 170))
                      + list(range(161, 164)))
EN_OCTETS = (list(range(52, 61)) + [63, 65, 66, 68, 69, 74, 75, 77, 89, 92]
             + [98, 99, 101, 102, 103] + [106, 108] + list(range(110, 115))
             + list(range(116, 121)) + list(range(122, 126)))
EN_EXTRA_OCTETS = list(range(246, 254))


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def make_code(name: str, used: set[str], idx: int) -> str:
    letters = [c for c in name.upper() if "A" <= c <= "Z"]
    code = "".join(letters[:4]) or f"DEMO{idx}"
    while code in used or len(code) < 3:
        code = (code + "X")[:5] if code not in used else code + "1"
        if code in used:
            code = code[:4] + str(idx % 10)
    used.add(code)
    return code


def demo_mac(rng: random.Random, bad_ok: bool = True) -> str:
    """Documentation/local-admin MACs in the formats the importer knows."""
    tail = [rng.randrange(256) for _ in range(3)]
    style = rng.randrange(10)
    if style < 4:
        return "00:00:5E:%02X:%02X:%02X" % tuple(tail)          # canonical
    if style < 7:
        return "00005e%02x%02x%02x" % tuple(tail)             # bare 12-hex
    if style < 9 or not bad_ok:
        return "0000.5e%02x.%02x%02x" % tuple(tail)           # cisco dotted
    return "00-OF-%02d-%02d-%02d" % tuple(tail)               # invalid -> mac_raw


def heb_or_en(rng: random.Random, he: list[str], en: list[str], p_he: float) -> str:
    return rng.choice(he if rng.random() < p_he else en)


# ---------------------------------------------------------------------------
# family builders — each returns the full row matrix for one sheet
# ---------------------------------------------------------------------------

def sites_master_rows(sites: list[dict], lang: str) -> list[list]:
    """Name/Code/type + fragment columns -> 10.N.0.0/24 (or 172.x for the
    integration row). Mirrors the real 'רשימת אתרים' sheet layout."""
    if lang == "he":
        header = ["Name", "Code", "type", "Subet range", "", "", "",
                  "Subet", "הערות", "", "", "", "הערות"]
    else:
        header = ["Name", "Code", "Type", "Subet range", "", "", "",
                  "Subet", "Notes"]
    rows = [header]
    for s in sites:
        notes = s.get("master_notes", "")
        if s.get("extra_pair"):  # non-10.x block, e.g. (172, 31)
            a, b = s["extra_pair"]
            frags = [str(a), str(b), ".0.", "0/24"]
        elif s.get("partial"):   # '10','N' only -> site number, no CIDR
            frags = ["10", str(s["number"]), "", ""]
        else:
            frags = ["10", str(s["number"]), ".0.", "0/24"]
        row = [s["name"], s["code"], s["size"], *frags,
               s.get("mask", "255.255.255.0"), notes]
        if lang == "he":
            row += ["", "", "", s.get("master_notes2", "")]
        rows.append(row)
    return rows


def _site_header(variant: str, lang: str) -> list:
    if variant == "full":
        return ["IP Address", "end ip", "Subnet mask", "Defult Gatway",
                "VLAN/LAN", "Node Name", "Counter/Location", "MAC", "Model",
                "description", "Serial Number", "switch", "port", "הערות"]
    if variant == "campus":  # the 020 NTBG-style wide sheet
        return ["IP Address", "end ip", "Subnet mask", "Defult Gatway",
                "VLAN/LAN", "Node Name", "Counter/Location", "MAC",
                "description", "switch", "port", "מס דלפק באפלקציה ",
                "מוגדר תחת אתר"]
    if variant == "lean":    # the 006-style narrow sheet
        return ["IP Address", "end ip", "VLAN/LAN", "Node Name", "Model",
                "description", "הערות", "Serial Number"]
    if variant == "intl":    # the 016 INTEGRATION-style header set
        return ["IP ", " End", "Server Name", "Description", "Env",
                "Location", "Remarks"]
    if variant == "hebrew":
        return ["כתובת IP", "", "VLAN/LAN", "Node Name", "הערות"]
    if variant == "minimal":
        return ["IP Address", "end ip", "description"]
    if variant == "blankip":  # header cell over the IP column left blank
        return ["", "end ip", "Subnet mask", "Defult Gatway", "Node Name",
                "MAC", "description"]
    if variant == "dupblocks":  # two duplicated column groups (031-style)
        return ["IP Address", "end ip", "Node Name", "description", "",
                "IP Address", "end ip", "Node Name", "description"]
    if variant == "fullip":
        return ["IP Address", "Node Name", "VLAN/LAN", "description", "הערות"]
    return ["IP Address", "end ip", "VLAN/LAN", "Node Name", "description",
            "הערות"]


def _site_row(rng: random.Random, site: dict, subnet: int, host,
              variant: str, lang: str, notes: str = "",
              bad_macs: bool = True) -> list:
    """One address row in the site's own column layout."""
    p_he = 0.6 if lang == "he" else 0.0
    base = f"10.{site['number']}.{subnet}." if site.get("number") is not None \
        else f"{site['extra_pair'][0]}.{site['extra_pair'][1]}.{subnet}."
    end = str(host) if not isinstance(host, str) else host
    mask = "255.255.255.0"
    oct3 = subnet
    gw = base + "254" if end else ""
    suffix = f"{int(end):02x}" if str(end).isdigit() else "00"
    node = f"{rng.choice(HOST_PREFIXES)}-{site['code'].lower()}-{oct3}{suffix}"[:28]
    vlan = _vlan_for(site, subnet)
    mac = demo_mac(rng, bad_ok=bad_macs)
    model = rng.choice(MODELS)
    desc = heb_or_en(rng, HE_DESCRIPTIONS, EN_DESCRIPTIONS, p_he)
    serial = f"DEMO-{rng.randrange(10**8):08d}"
    sw = f"sw-{site['code'].lower()}-01"
    port = f"Gi1/0/{rng.randrange(1, 48)}"
    counter = f"demo counter {rng.randrange(1, 40)}"
    if variant == "full":
        return [base, end, mask, gw, vlan, node, counter, mac, model,
                desc, serial, sw, port, notes]
    if variant == "campus":
        under = site.get("under_site", "") if rng.random() < 0.12 else ""
        return [base, end, mask, gw, vlan, node, counter, mac, desc,
                sw, port, str(rng.randrange(1, 30)), under]
    if variant == "lean":
        return [base, end, vlan, node, model, desc, notes, serial]
    if variant == "intl":
        return [base[:-1] if rng.random() < 0.3 else base, end, node, desc,
                rng.choice(["HQ", "DR"]), f"demo room {rng.randrange(1, 9)}",
                notes or rng.choice(["", "demo row"])]
    if variant == "hebrew":
        return [base, end, vlan, node, notes]
    if variant == "minimal":
        return [base, end, desc]
    if variant == "blankip":
        return [base, end, mask, gw, node, mac, desc]
    if variant == "dupblocks":
        b2 = base
        e2 = str(rng.randrange(1, 250))
        return [base, end, node, desc, "", b2, e2,
                f"cam-{site['code'].lower()}-{e2}", "demo second block"]
    if variant == "fullip":
        return [base + end, node, vlan, desc, notes]
    return [base, end, vlan, node, desc, notes]


def site_sheet_rows(rng: random.Random, site: dict, n_rows: int,
                    variant: str, lang: str, preamble: bool = False,
                    echo: bool = False, junk_marks: bool = False,
                    headerless: bool = False, clean: bool = False) -> list[list]:
    """A site sheet: header (or not) + n address-ish rows.

    clean=True produces a 'perfect' sheet: every (subnet, host) unique, hosts
    in .1-.199, ranges in .201-.250 (never overlapping), no label/continuation
    rows, valid MACs only — the import preview is all creates.
    clean=False mirrors a real messy file: subnet declarations, section
    labels, continuation rows, junk markers, echoed headers, bad MACs.
    """
    rows: list[list] = []
    if preamble and not clean:
        rows.append(["", "", ""])
        rows.append([f"DEMO sheet — fictional data ({site['name']})", "", "",
                     "", "last updated by demo-generator", "", "",
                     "סינטטי לחלוטין"])
        rows.append(["", "", ""])
    header = _site_header(variant, lang)
    if not headerless:
        rows.append(header)

    width = len(header) if not headerless else 8
    subnets = rng.sample(range(1, 14), k=min(6, 13))
    # map each subnet onto one of the site's VLANs -> subnet<->VLAN is
    # stable within the sheet, and subnet-declaration rows tag the prefix
    site_vlans = _site_vlans(site)
    rng.shuffle(site_vlans)  # different subset order per site
    site["_vlan_map"] = {
        s: site_vlans[i % len(site_vlans)] for i, s in enumerate(subnets)
    }
    used: set[tuple[int, int]] = set()
    i = 0
    while i < n_rows:
        subnet = rng.choice(subnets)
        r = rng.random()
        if clean:
            if r < 0.04 and variant in ("full", "campus", "lean"):
                # subnet declaration row: 3-octet fragment, empty 'end'
                rows.append(_site_row(rng, site, subnet, "", variant, lang,
                                      bad_macs=False))
            elif r < 0.10 and variant != "fullip":
                # a '201-240' range in the band host rows never use —
                # only where the sheet has a dedicated 'end' column
                lo = rng.randrange(201, 235)
                hi = min(lo + rng.randrange(8, 15), 250)
                rows.append(_site_row(rng, site, subnet, f"{lo}-{hi}",
                                      variant, lang, bad_macs=False))
            else:
                host = rng.randrange(1, 200)
                tries = 0
                while (subnet, host) in used and tries < 40:
                    host = rng.randrange(1, 200)
                    tries += 1
                if (subnet, host) in used:
                    continue
                used.add((subnet, host))
                notes = ""
                if rng.random() < 0.15:
                    notes = heb_or_en(rng, HE_NOTES, EN_NOTES,
                                      0.8 if lang == "he" else 0.0)
                rows.append(_site_row(rng, site, subnet, host, variant, lang,
                                      notes=notes, bad_macs=False))
            i += 1
            continue
        if r < 0.05 and variant in ("full", "campus", "lean"):
            # subnet declaration row: 3-octet fragment, empty 'end'
            rows.append(_site_row(rng, site, subnet, "", variant, lang))
        elif r < 0.09:
            # section label row — non-IP text in the IP column
            label = rng.choice(["שרתים", "מדפסות", "End of block", "---",
                                "ציוד תקשורת"]) if lang == "he" else \
                rng.choice(["Servers", "Printers", "End of block", "---"])
            rows.append([label] + [""] * (width - 1))
        elif r < 0.14:
            # a range row: '101-200' style end value
            rows.append(_site_row(rng, site, subnet,
                                  f"{rng.randrange(60, 120)}-{rng.randrange(150, 240)}",
                                  variant, lang))
        elif r < 0.17 and i > 2 and variant in ("full", "lean", "minimal"):
            # continuation row: empty IP column inherits the previous base
            rows.append(_site_row(rng, site, subnet,
                                  str(rng.randrange(1, 254)), variant, lang))
            rows[-1][0] = ""
        else:
            notes = ""
            if rng.random() < 0.18:
                notes = heb_or_en(rng, HE_NOTES, EN_NOTES,
                                  0.8 if lang == "he" else 0.0)
            row = _site_row(rng, site, subnet, rng.randrange(1, 254),
                            variant, lang, notes=notes)
            if junk_marks and rng.random() < 0.25:
                row = row + [rng.choice(["yes", "no ping"])]
            elif rng.random() < 0.08:
                row = row + [rng.choice(["ISP-DEMO", "port 48",
                                         "checked 01/26", ""])]
            rows.append(row)
        if echo and i == n_rows // 2 and not headerless:
            rows.append(list(header))  # repeated-header echo mid-sheet
        i += 1
    # one intentional in-batch duplicate -> conflict merge demo
    if not clean and n_rows > 30 and variant in ("full", "lean"):
        dup = _site_row(rng, site, subnets[0], 42, variant, lang)
        rows.insert(len(header if not headerless else []) + 5, dup)
        rows.insert(len(header if not headerless else []) + 25, list(dup))
    return rows


def circuits_rows(rng: random.Random, sites: list[dict], n: int,
                  retired: bool, lang: str) -> list[list]:
    if lang == "he":
        header = ["סביבת חיבור", "מאתר", "סוג האתר", "מספר אתר", "קידומת האתר",
                  "סוג הקו", "קוד בבזק", "צומת", "רוחב פס Download",
                  "רוחב פס Upload", "כתובת WAN", "מספר קוד באפלקציה",
                  "שם לקוח באפל'", "סוג שירות באפלקציה",
                  "איש קשר וכתובת האתר", "הערות"]
    else:
        # no English aliases exist for circuits -> lands as 'unknown' and the
        # wizard suggests Custom list (demonstrated on purpose)
        header = ["Env", "Site", "Site Type", "Site No", "Site Prefix",
                  "Line Type", "Circuit ID", "Node", "BW Down", "BW Up",
                  "WAN IP", "App Client No", "App Client", "App Service",
                  "Contact & Address", "Notes"]
    rows = [header]
    pool = [s for s in sites if s.get("number") is not None]
    for i in range(n):
        s = rng.choice(pool)
        if retired:
            line = rng.choice(["sdh", "pstn", "isdn"])
            bw = rng.choice(["2", "4", "10", "30"])
            cid = f"DEMO-OLD-{i:05d}"
        else:
            line = rng.choice(["ipvpn", "fiber", "mpls", "sdh"])
            bw = rng.choice(["100", "200", "500", "1000"])
            cid = f"DEMO-9{i:05d}"
        rows.append([
            rng.choice(["DC-Demo", "DR-Demo", "Backup-Demo"]),
            s["name"], rng.choice(["פעיל", "פעיל", "לא פעיל"]) if lang == "he"
            else rng.choice(["active", "active", "closed"]),
            str(s["number"]), s["code"], line, cid,
            f"88{rng.randrange(10**5):05d}", bw,
            str(int(bw) if rng.random() < 0.7 else rng.choice(["100", "500"])),
            WAN_BASE + str(rng.randrange(1, 250)) if rng.random() < 0.8 else "",
            f"{rng.randrange(10**6):06d}", "DEMO-CLIENT",
            rng.choice(["demo-ipvpn", "demo-internet", "demo-voice"]),
            rng.choice(["", "ops team", "noc-team"]),
            rng.choice(["קו דמו", "פעיל", "", "חיבור דמו ראשי"])
            if lang == "he" else rng.choice(["demo line", "active", ""]),
        ])
    return rows


def servers_rows(rng: random.Random, site: dict, n: int, lang: str) -> list[list]:
    rows = [["Name", "Guest OS", "IP Address", "Cert", "License", ""]]
    num = site["number"]
    used: set[int] = set()

    def host() -> int:
        h = rng.randrange(2, 250)
        while h in used:
            h = rng.randrange(2, 250)
        used.add(h)
        return h

    for i in range(n):
        name = f"SRV-{site['code']}-{i:03d}"
        ip = f"10.{num}.8.{host()}"
        if rng.random() < 0.15:
            ip += f", 10.{num}.8.{host()}"
        if rng.random() < 0.06:
            ip += f" 169.254.{rng.randrange(1, 254)}.{rng.randrange(1, 254)}"
        rows.append([
            name, rng.choice(GUEST_OS), ip,
            rng.choice(["DEMO-WC-2027", "", "DEMO-CERT"]),
            rng.choice(["DEMO-LIC", "", "OEM"]),
            rng.choice(OWNERS),
        ])
    rows.append(["SRV-STANDALONE-DEMO", rng.choice(GUEST_OS), "", "", "",
                 "noc-team"])  # host with no IP -> asset record
    return rows


def assets_rows(rng: random.Random, n: int, lang: str) -> list[list]:
    if lang == "he":
        rows = [["סוג", "חברה", "דגם", "שם התוכנה", "ייעוד", "גירסה", "EOL",
                 "חברה תומכת", "שם איש סיסטם", "Logs", "Service Company"]]
        kinds = ["חומרה", "חומרה", "תוכנה"]
        purposes = ["שרתים פיזיים", "ניהול חומרה", "תשתיות דמו", "מערכת דמו"]
        contact_hdr = "אחראי דמו"
    else:
        rows = [["Type", "Vendor", "Model", "Software", "Purpose", "Version",
                 "EOL", "Support Vendor", "Sys Contact", "Logs", "Service Co"]]
        kinds = ["hardware", "hardware", "software"]
        purposes = ["physical servers", "mgmt plane", "demo infra", "demo app"]
        contact_hdr = "demo owner"
    for _ in range(n):
        kind = rng.choice(kinds)
        rows.append([
            kind, rng.choice(VENDORS), rng.choice(MODELS),
            rng.choice(["iRMC", "DemoOS", "DemoSuite", ""]) if kind != "חומרה"
            else "",
            rng.choice(purposes),
            f"v{rng.randrange(1, 9)}.{rng.randrange(0, 9)}" if lang == "en"
            else f"{rng.randrange(1, 9)}.{rng.randrange(0, 9)}",
            rng.choice([excel_serial(date(2027, rng.randrange(1, 12),
                                     rng.randrange(1, 28))),
                        f"{rng.randrange(1, 28)}/{rng.randrange(1, 12)}/27", ""]),
            rng.choice(["DemoSupport Ltd", "", "Self"]),
            contact_hdr, rng.choice(["", "on", "syslog-demo"]),
            rng.choice(["", "DemoCare"]),
        ])
    return rows


def certificates_rows(rng: random.Random, n: int) -> list[list]:
    rows = [["Software"]]  # single-cell header -> certificates family
    for i in range(n):
        exp = rng.choice([
            excel_serial(date(2026, 10, 1) + timedelta(days=i * 37)),
            excel_serial(date(2027, 6, 15) + timedelta(days=i * 11)),
            f"{rng.randrange(1, 28):02d}/{rng.randrange(1, 12):02d}/2{rng.randrange(6, 9)}",
            date(2028, 3, 1) + timedelta(days=i * 5),
        ])
        rows.append([
            rng.choice(CERT_PLATFORMS),
            f"VS_DEMO_{rng.choice(['API', 'WEB', 'MAIL', 'VPN'])}",
            rng.choice(DEMO_DOMAINS),
            rng.choice(["DEMO_Wildcard_2027", "DEMO_Cert_RSA",
                        "DEMO_LetsEncrypt"]),
            exp,
            *[rng.choice(["", "auto-renew", "manual"])],
        ])
    return rows


def services_rows(rng: random.Random, sites: list[dict], n: int,
                  lang: str) -> list[list]:
    if lang == "he":
        rows = [["מס' סידורי", "שם השירות", "מי הגורם שנהנה מהשירות",
                 "שייך לקוד אתר", "מיקום קובץ/תיקייה מפורט", "תיאור קצר",
                 "בדיקת תקינות"]]
        names = ["דוח תפוסה יומי", "סנכרון לילי דמו", "מוניטור דמו",
                 "גיבוי דמו", "דיווח דמו", "שירות דוגמה"]
        beneficiaries = ["צוות תפעול", "מנהל דמו", "משתמשי דמו", ""]
        test = ["בדיקה חודשית", "יומי", "", "ידני"]
    else:
        rows = [["Seq", "Service", "Beneficiary", "Site Code", "Doc Path",
                 "Description", "Health Check"]]
        names = ["Daily Usage Report", "Demo Nightly Sync", "Demo Monitor",
                 "Demo Backup", "Demo Reporter", "Sample Service"]
        beneficiaries = ["ops team", "demo manager", "demo users", ""]
        test = ["monthly", "daily", "", "manual"]
    for i in range(n):
        s = rng.choice(sites)
        rows.append([
            i + 1, rng.choice(names), rng.choice(beneficiaries),
            rng.choice([s["code"], str(s.get("number") or ""), ""]),
            f"\\\\demo-share\\ops\\procedures\\demo_{i:02d}.docx",
            rng.choice(["שירות דמו לבדיקות", "demo service", ""]),
            rng.choice(test),
        ])
    return rows


def switches_sn_rows(rng: random.Random, sites: list[dict], n: int) -> list[list]:
    rows = [["Serial Number", "Version", "Device"]]
    for i in range(n):
        s = rng.choice(sites)
        rows.append([f"DEMO{rng.randrange(36**8):X}",
                     rng.choice(["DemoSwitch 9300", "DemoSwitch 2530",
                                 "DemoSwitch 48"]),
                     f"sw-{s['code'].lower()}-{i % 3 + 1}"])
    return rows


def routers_sn_rows(rng: random.Random, sites: list[dict]) -> list[list]:
    """Site/Hostname/Serial Numbers with multi-line 'PCB Serial' blob cells —
    mirrors the real Routers S.N sheet that split_serial_blob() handles."""
    rows = [["Site ", "Hostname", "Serial Numbers"]]
    for i, s in enumerate(sites[:18]):
        rows.append([
            s["name"], f"rt-{s['code'].lower()}-01",
            f"   PCB Serial Number        : DEMO{i:08X}",
        ])
        rows.append(["", "",
                     f"        PCB Serial Number        : DEMO{i + 90:08X}"])
        if i % 4 == 0:
            rows.append(["", f"rt-{s['code'].lower()}-02",
                         "   PCB Serial Number        : "
                         f"DEMO{i + 180:08X}\n   Chassis Serial             :"
                         f" DEMOCH{i:05d}"])
    return rows


def readme_rows() -> list[list]:
    return [
        ["DEMO DATA — ALL FICTIONAL"],
        [""],
        ["This workbook is generated by examples/generate_demo_data.py."],
        ["Every site, IP, serial, MAC, circuit ID and contact is invented."],
        ["It mirrors the *shape* of a real Network_Address.xlsx so the"],
        ["import wizard can be exercised end-to-end with zero real data."],
        [""],
        ["This sheet has no recognized header — the wizard will suggest"],
        ["importing it as a Custom list. That is intentional."],
    ]


def contacts_rows(rng: random.Random, n: int) -> list[list]:
    rows = [["Vendor", "Product", "Contact Role", "Email", "Phone", "SLA",
             "Notes"]]
    prods = ["DemoSwitch", "DemoRouter", "DemoFirewall", "DemoVM",
             "DemoLink", "DemoCam"]
    roles = ["TAM", "NOC", "Sales", "Support", "Escalation"]
    for i in range(n):
        rows.append([
            rng.choice(VENDORS) + " Demo",
            rng.choice(prods), rng.choice(roles),
            f"contact{i}@demo-vendor.example",
            f"555-01{rng.randrange(100)}",
            rng.choice(["8x5", "24x7", "best effort"]),
            rng.choice(["", "renewal Q3", "demo only"]),
        ])
    return rows


def classes_rows(rng: random.Random, n: int) -> list[list]:
    rows = [["Class", "Room", "Capacity", "Instructor", "When"]]
    for i in range(n):
        rows.append([
            f"Demo Training {i + 1}", f"R-{rng.randrange(100, 400)}",
            rng.randrange(6, 30), "demo-instructor",
            rng.choice(["Sun AM", "Wed PM", "on demand"]),
        ])
    return rows


# ---------------------------------------------------------------------------
# site registry + workbook assembly
# ---------------------------------------------------------------------------

def build_sites(names: list[str], sizes: list[str], octets: list[int],
                rng: random.Random) -> list[dict]:
    used: set[str] = set()
    sites = []
    for i, name in enumerate(names):
        sites.append({
            "name": name,
            "code": make_code(name, used, i),
            "size": rng.choice(sizes),
            "number": octets[i],
            "active": True,
            "mask": "255.255.255.0",
        })
    return sites


def _mixed_sites(rng: random.Random) -> tuple[list[dict], list[dict]]:
    """Master rows for the clean Hebrew+English flagship workbook.

    Every row has name + code + site number + a clean CIDR. The only
    'real-world' touches kept: two inactive (לא פעיל) rows and one non-10.x
    integration site — all resolve cleanly with no warnings."""
    names = HEBREW_SITE_NAMES + ENGLISH_SITE_NAMES  # 35 + 69 = 104
    rng.shuffle(names)
    sites = build_sites(names[:55], HE_SIZES, MIXED_OCTETS, rng)

    # two inactive (closed) sites — normal in a master list; no sheets
    for s in sites[3:5]:
        s["active"] = False
        s["master_notes"] = "לא פעיל"
    # non-10.x integration site on 172.31.x — clean single block + CIDR
    sites[6].update(name="INTEGRATION Demo", code="INTD", number=None,
                    extra_pair=(172, 31))
    # dedicated server farm: master row but no site sheet — the servers
    # sheet's addresses octet-match here without colliding with a sheet
    sites[7].update(name="Demo Server Farm", code="DMSF", no_sheet=True)
    return sites, []


def _en_sites(rng: random.Random) -> tuple[list[dict], list[dict]]:
    names = EN_ONLY_SITE_NAMES
    sites = build_sites(names[:30], EN_SIZES, EN_OCTETS, rng)
    # nameless row -> 'Site 10.N' synthetic name, claimed by a sheet title
    sites[5]["name"] = ""
    # non-10.x integration block works in English too
    sites[6]["extra_pair"] = (172, 31)
    sites[6]["number"] = None
    sites[6]["name"] = "Integration Demo"
    sites[6]["code"] = "INTD"
    extras = build_sites(ENGLISH_SITE_NAMES[:8], EN_SIZES,
                         EN_EXTRA_OCTETS, rng)
    return sites, extras


def _pick_variant(rng: random.Random, lang: str) -> str:
    pool = ["full"] * 4 + ["lean"] * 3 + ["campus", "intl", "minimal"]
    if lang == "he":
        pool.append("hebrew")
    return rng.choice(pool + ["full"])


def _assign_site_sheets_clean(rng: random.Random, sites: list[dict],
                              lang: str) -> list[dict]:
    """Flagship layout: every master site gets one sheet titled after it;
    rows are unique and warning-free. Two extra sheets create octet-new
    sites (a normal 'site discovered from its sheet' flow)."""
    variants = ["full", "full", "lean", "lean", "campus", "intl", "minimal"]
    if lang == "he":
        variants += ["hebrew", "fullip"]
    specs: list[dict] = []
    for s in sites:
        if not s["active"] or not s["name"] or s.get("no_sheet"):
            continue
        big = s["size"] in ("גדול", "Large")
        n = rng.randrange(80, 220) if big else rng.randrange(8, 60)
        specs.append({"site": s, "sheet": s["name"][:31], "n": n,
                      "variant": rng.choice(variants)})
    # the two large sheets (~450 / ~300 rows like the real 006/020)
    specs[0]["n"], specs[0]["sheet"] = 450, "Demo Core DC"
    specs[0]["site"].update(name="Demo Core DC", code="CORE")
    specs[1]["n"], specs[1]["variant"], specs[1]["sheet"] = \
        300, "campus", "Demo Campus Users"
    specs[1]["site"].update(name="Demo Campus Users", code="CAMP")
    specs[1]["site"]["under_site"] = specs[2]["site"]["name"]

    # two sheet-only sites -> 'octet-new' creates (clean, no warnings)
    for name, num in (("Quarry Annex", MIXED_EXTRA_OCTETS[0]),
                      ("Telemetry Hut", MIXED_EXTRA_OCTETS[1])):
        specs.append({"site": {"name": name, "code": name[:4].upper(),
                               "size": "קטן" if lang == "he" else "Small",
                               "number": num},
                      "sheet": name, "n": 18, "variant": "full"})
    return specs


def _assign_site_sheets(rng: random.Random, sites: list[dict],
                        extras: list[dict], lang: str) -> list[dict]:
    """Decide which sites get a sheet and with which quirk variant."""
    specs: list[dict] = []
    master_with_sheets = [s for s in sites if s.get("active", True)
                          and s.get("name") and s["number"] is not None][:55]
    for s in master_with_sheets:
        big = s["size"] == "גדול" or s["size"] == "Large"
        n = rng.randrange(60, 180) if big else rng.randrange(5, 60)
        specs.append({"site": s, "sheet": s["name"][:31], "n": n,
                      "variant": _pick_variant(rng, lang)})
    # the two large sheets (~450 / ~300 rows like the real 006/020)
    specs[0]["n"], specs[0]["sheet"] = 450, "Demo Core DC"
    specs[0]["site"].update(name="Demo Core DC", code="CORE")
    specs[1]["n"], specs[1]["variant"], specs[1]["sheet"] = \
        300, "campus", "Demo Campus Users"
    specs[1]["site"].update(name="Demo Campus Users", code="CAMP")
    specs[1]["site"]["under_site"] = specs[2]["site"]["name"]

    # nameless master row -> its sheet claims the synthetic name
    nameless = next((s for s in sites if s["name"] == ""), None)
    if nameless is not None:
        claim = "גלבוע דמה" if lang == "he" else "Beacon Annex"
        specs.append({"site": nameless, "sheet": claim[:31], "n": 25,
                      "variant": "lean"})

    # a sheet whose octet block belongs to an inactive site -> octet-new.
    # The title must NOT word-match any site name (a shared 'demo' would
    # title-hit), so the retired-anchor path actually fires.
    inactive = next((s for s in sites if not s["active"]), None)
    if inactive is not None:
        specs.append({"site": dict(inactive, name="Reclaimed Segment"),
                      "sheet": "Reclaimed Segment", "n": 20,
                      "variant": "lean"})

    # the integration site's own sheet on 172.31.x
    integ = next((s for s in sites if s.get("extra_pair")), None)
    if integ is not None:
        specs.append({"site": integ, "sheet": integ["name"][:31], "n": 60,
                      "variant": "intl"})

    # edge-case sheets
    ec = [
        ("Headerless Demo", "headerless", 18),
        ("Blank Header Demo", "blankip", 20),
        ("Dup Blocks Demo", "dupblocks", 24),
        ("Full IP Demo", "fullip", 22),
        ("Junk Markers Demo", "lean", 26),
    ]
    for i, (title, variant, n) in enumerate(ec):
        specs.append({"site": extras[i], "sheet": title, "n": n,
                      "variant": variant})
    # remaining extras: octet-new sites / holding-site candidates
    for s in extras[len(ec):]:
        specs.append({"site": s, "sheet": s["name"][:31],
                      "n": rng.randrange(5, 40),
                      "variant": _pick_variant(rng, lang)})
    # undeclared non-10.x sheet with an unrelated title -> holding site
    specs.append({"site": {"name": "Unlisted Net", "code": "UNLS",
                           "number": None, "extra_pair": (172, 33),
                           "size": "קטן" if lang == "he" else "Small"},
                  "sheet": "Orphan Range", "n": 15, "variant": "intl"})
    for spec in specs:
        spec["preamble"] = rng.random() < 0.15
        spec["echo"] = rng.random() < 0.10
        spec["junk"] = spec["sheet"] == "Junk Markers Demo" or rng.random() < 0.08
    return specs


def _save_workbook(path: Path, sheets: list[tuple[str, list[list]]]):
    wb = openpyxl.Workbook()
    wb.properties.created = _FIXED_TS
    wb.properties.modified = _FIXED_TS
    wb.properties.title = "DEMO DATA — fictional"
    first = True
    for title, rows in sheets:
        ws = wb.active if first else wb.create_sheet()
        first = False
        ws.title = title[:31]
        for r in rows:
            ws.append(r)
    wb.save(path)


def build_mixed_workbook(rng: random.Random) -> list[tuple[str, list[list]]]:
    """The flagship: clean and complete — every site has name/code/number,
    every sheet title matches its site, every row a clean create."""
    sites, _extras = _mixed_sites(rng)
    specs = _assign_site_sheets_clean(rng, sites, "he")
    farm = next(s for s in sites if s.get("no_sheet"))
    sheets: list[tuple[str, list[list]]] = [
        ("רשימת אתרים", sites_master_rows(sites, "he")),
        ("קוי-SDH-IPVPN", circuits_rows(rng, sites, 50, False, "he")),
        ("קוי בזק ישן", circuits_rows(rng, sites, 30, True, "he")),
        ("שרתים בייצור", servers_rows(rng, farm, 40, "he")),
        ("תוכנות וחומרות", assets_rows(rng, 30, "he")),
        ("תוקף תעודות", certificates_rows(rng, 50)),
        ("שירותים", services_rows(rng, sites, 15, "he")),
        ("Switches S.N", switches_sn_rows(rng, sites, 12)),
        ("Routers S.N", routers_sn_rows(rng, sites)),
    ]
    for spec in specs:
        sheets.append((spec["sheet"], site_sheet_rows(
            rng, spec["site"], spec["n"], spec["variant"], "he",
            clean=True)))
    return sheets


def build_en_workbook(rng: random.Random) -> list[tuple[str, list[list]]]:
    sites, extras = _en_sites(rng)
    specs = _assign_site_sheets(rng, sites, extras, "en")
    # trim to ~33 site sheets for the compact international workbook
    specs = specs[:33]
    sheets: list[tuple[str, list[list]]] = [
        ("README — DEMO DATA", readme_rows()),
        ("Sites Master", sites_master_rows(sites, "en")),
        ("WAN Circuits", circuits_rows(rng, sites, 30, False, "en")),
        ("Prod Servers", servers_rows(rng, sites[0], 30, "en")),
        ("Hw-Sw Assets", assets_rows(rng, 20, "en")),
        ("Certificates", certificates_rows(rng, 30)),
        ("Services", services_rows(rng, sites, 12, "en")),
        ("Switch Serials", switches_sn_rows(rng, sites, 10)),
        ("Router Serials", routers_sn_rows(rng, sites)),
    ]
    for spec in specs:
        sheets.append((spec["sheet"], site_sheet_rows(
            rng, spec["site"], spec["n"], spec["variant"], "en",
            preamble=spec["preamble"], echo=spec["echo"],
            junk_marks=spec["junk"],
            headerless=spec["variant"] == "headerless")))
    sheets.append(("Vendor Contacts", contacts_rows(rng, 12)))
    sheets.append(("Empty Sheet", []))
    return sheets


# ---------------------------------------------------------------------------
# CSV artifacts
# ---------------------------------------------------------------------------

def _write_csv(path: Path, rows: list[list], encoding: str):
    with open(path, "w", newline="", encoding=encoding) as f:
        csv.writer(f).writerows(rows)


def write_csvs(rng: random.Random, demo_site: dict):
    """One canonical site sheet in both encodings + the flat address CSV +
    a contacts list for the /lists import flow."""
    rows = [["IP Address", "end ip", "Subnet mask", "Defult Gatway",
             "VLAN/LAN", "Node Name", "Counter/Location", "MAC",
             "description", "switch", "port", "מס דלפק באפלקציה ",
             "מוגדר תחת אתר", "הערות"]]
    num = demo_site["number"]
    used: set[tuple[int, int]] = set()
    for i in range(1, 60):
        pair = (rng.choice([1, 2, 3]), rng.randrange(1, 254))
        while pair in used:
            pair = (rng.choice([1, 2, 3]), rng.randrange(1, 254))
        used.add(pair)
        v = _VLANS_BY_VID[[10, 20, 30][pair[0] - 1]]
        rows.append([
            f"10.{num}.{pair[0]}.", str(pair[1]),
            "255.255.255.0", f"10.{num}.1.254", vlan_cell(v[0], v[1]),
            f"pc-{demo_site['code'].lower()}-{i:03d}",
            f"demo counter {rng.randrange(1, 30)}", demo_mac(rng),
            rng.choice(HE_DESCRIPTIONS + EN_DESCRIPTIONS),
            f"sw-{demo_site['code'].lower()}-01",
            f"Gi1/0/{rng.randrange(1, 48)}", str(rng.randrange(1, 30)), "",
            rng.choice(HE_NOTES),
        ])
    _write_csv(HERE / "demo-site-utf8.csv", rows, "utf-8-sig")
    _write_csv(HERE / "demo-site-cp1255.csv", rows, "cp1255")

    # flat CSV for /api/v1/addresses/import — prefixes are the site blocks
    # the demo workbook's master list creates (import the xlsx first)
    addr = [["address", "prefix", "hostname", "mac_address", "status",
             "role", "notes"]]
    prefixes = [f"10.{num}.0.0/24", "10.131.0.0/24", "10.132.0.0/24"]
    used_addr: set[str] = set()
    for i in range(60):
        pfx = rng.choice(prefixes)
        ip = pfx.replace("0/24", str(rng.randrange(2, 250)))
        while ip in used_addr:
            ip = pfx.replace("0/24", str(rng.randrange(2, 250)))
        used_addr.add(ip)
        addr.append([
            ip,
            pfx, f"csv-host-{i:03d}",
            demo_mac(rng) if rng.random() < 0.7 else "",
            rng.choice(["active", "active", "reserved", "dhcp"]),
            rng.choice(["", "", "vip", "vrrp", "hsrp"]),
            rng.choice(["csv demo row", "", "imported example"]),
        ])
    _write_csv(HERE / "demo-addresses.csv", addr, "utf-8-sig")
    _write_csv(HERE / "demo-contacts-list.csv", contacts_rows(rng, 20),
               "utf-8-sig")

    # the VLAN scheme as a reference table -> /lists import. VLAN groups
    # themselves are managed on the VLANs page (the workbook import has no
    # group field); the sheets' VLAN cells auto-create these per site.
    vl = [["vid", "name", "group", "scope", "description"]]
    vlan_meta = {
        5:   ("all sites", "switch/AP management"),
        6:   ("DC + large sites", "out-of-band management"),
        10:  ("all sites", "wired workstations"),
        20:  ("all sites", "VoIP phones"),
        30:  ("all sites", "network printers"),
        40:  ("small sites", "guest wireless"),
        50:  ("medium+ sites", "corporate wireless"),
        100: ("large sites", "server segment"),
        110: ("large sites", "storage / SAN"),
        120: ("large sites", "backup traffic"),
        200: ("medium+ sites", "iot sensors"),
        210: ("large sites", "cctv cameras"),
        220: ("medium+ sites", "door controllers"),
        999: ("all sites", "isolation / quarantine"),
    }
    for vid, name, grp in VLAN_PLAN:
        scope, desc = vlan_meta[vid]
        vl.append([str(vid), f"VLAN{vid}-{name}", grp, scope,
                   f"{desc} — demo"])
    _write_csv(HERE / "demo-vlans.csv", vl, "utf-8-sig")

    # a servers-table CSV for the /lists "Import a file" wizard — mirrors
    # the real 002_שרתים בייצור.csv shape (Name, Guest OS, IP Address,
    # Cert, License + owner column) plus columns that hit every inferred
    # list type: date (expiry badges), url, number, owner, select.
    # IPs point at the demo server-farm site so ticking "also import to
    # IPAM" lands them on the right site.
    farm_num = MIXED_OCTETS[7]
    sv = [["Name", "Guest OS", "IP Address", "Cert", "Cert Expiry",
           "License", "Mgmt URL", "vCPUs", "Owner"]]
    used_h: set[int] = set()
    for i in range(72):
        h = rng.randrange(2, 250)
        while h in used_h:
            h = rng.randrange(2, 250)
        used_h.add(h)
        ip = f"10.{farm_num}.8.{h}"
        if rng.random() < 0.15:
            h2 = rng.randrange(2, 250)
            while h2 in used_h:
                h2 = rng.randrange(2, 250)
            used_h.add(h2)
            ip += f", 10.{farm_num}.8.{h2}"
        if rng.random() < 0.05:
            ip += (f" 169.254.{rng.randrange(1, 254)}"
                   f".{rng.randrange(1, 254)}")
        name = f"SRV-DMSF-{i:03d}"
        # d/m/yyyy dates — a few expired for the expiry-badge demo
        if rng.random() < 0.85:
            year = rng.choice([2025, 2026, 2026, 2027, 2027, 2028])
            expiry = f"{rng.randrange(1, 28)}/{rng.randrange(1, 13)}/{year}"
        else:
            expiry = ""
        sv.append([
            name, rng.choice(GUEST_OS), ip,
            rng.choice(["DEMO-WC-2027", "DEMO-CERT", "INTERNAL-DEMO-CA", ""]),
            expiry,
            rng.choice(["OEM", "DEMO-LIC", "Volume"]),
            f"https://{name.lower()}.demo.local" if rng.random() < 0.8 else "",
            str(rng.choice([2, 4, 8, 16])),
            rng.choice(OWNERS),  # last column: parse_servers reads owner
        ])
    _write_csv(HERE / "demo-servers-list.csv", sv, "utf-8-sig")


def main():
    rng = random.Random(SEED)
    mixed = build_mixed_workbook(rng)
    _save_workbook(HERE / "Network_Address_DEMO.xlsx", mixed)
    en = build_en_workbook(random.Random(SEED + 1))
    _save_workbook(HERE / "Network_Address_DEMO_EN.xlsx", en)
    write_csvs(rng, {"number": MIXED_OCTETS[0], "code": "DEMOCSV"})
    print(f"Network_Address_DEMO.xlsx    : {len(mixed)} sheets")
    print(f"Network_Address_DEMO_EN.xlsx : {len(en)} sheets")
    print("demo-site-utf8.csv, demo-site-cp1255.csv, demo-addresses.csv, "
          "demo-contacts-list.csv, demo-vlans.csv, demo-servers-list.csv")


if __name__ == "__main__":
    main()
