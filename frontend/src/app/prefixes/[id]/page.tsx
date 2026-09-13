"use client";

import { use, useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Download,
  Plus,
  Trash2,
  Upload,
  Zap,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type {
  AddressPage,
  IpAddress,
  IpRange,
  IpRole,
  IpStatus,
  Prefix,
  Tag,
} from "@/types";
import { AddressFilterPanel } from "@/components/address-filter-panel";
import { IpDrawer } from "@/components/ip-drawer";
import { IpStatusBadge, PrefixStatusBadge } from "@/components/status-badge";
import { SubnetGrid } from "@/components/subnet-grid";
import { TagChip, TagPicker, useTags } from "@/components/tag-picker";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const MAX_GRID = 65536; // /16 and smaller render as a grid; bigger -> table
const IP_STATUSES: IpStatus[] = [
  "active",
  "reserved",
  "dhcp",
  "discovered",
  "offline",
];
const IP_ROLES: IpRole[] = ["vip", "vrrp", "hsrp", "glbp", "carp", "secondary"];
const RANGE_ROLES = ["dhcp", "pool", "reserved"];

function toggleIn<T>(set: Set<T>, v: T): Set<T> {
  const next = new Set(set);
  if (next.has(v)) next.delete(v);
  else next.add(v);
  return next;
}

function RangeDialog({
  open,
  onOpenChange,
  prefix,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  prefix: Prefix;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({ start: "", end: "", role: "dhcp", description: "" });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) setForm({ start: "", end: "", role: "dhcp", description: "" });
  }, [open]);

  const submit = async () => {
    setBusy(true);
    try {
      await api.post("/api/v1/ranges", {
        prefix_id: prefix.id,
        start_address: form.start,
        end_address: form.end,
        role: form.role,
        description: form.description || null,
      });
      toast.success("Range created");
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New IP range in {prefix.prefix}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Start address</Label>
              <Input
                placeholder="10.0.0.100"
                value={form.start}
                onChange={(e) => setForm({ ...form, start: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>End address</Label>
              <Input
                placeholder="10.0.0.199"
                value={form.end}
                onChange={(e) => setForm({ ...form, end: e.target.value })}
              />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label>Role</Label>
            <Select
              value={form.role}
              onValueChange={(v) => setForm({ ...form, role: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {RANGE_ROLES.map((r) => (
                  <SelectItem key={r} value={r}>
                    {r}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Description</Label>
            <Input
              placeholder="e.g. DHCP pool"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !form.start || !form.end}>
            {busy ? "Creating…" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function PrefixDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const prefixId = Number(id);
  const [prefix, setPrefix] = useState<Prefix | null>(null);
  const [page, setPage] = useState<AddressPage | null>(null);
  const [ranges, setRanges] = useState<IpRange[]>([]);
  const [drawer, setDrawer] = useState<{ ip: string; addr: IpAddress | null } | null>(null);
  const [rangeOpen, setRangeOpen] = useState(false);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [search, setSearch] = useState("");
  const [statusSel, setStatusSel] = useState<Set<IpStatus>>(new Set());
  const [tagSel, setTagSel] = useState<Set<number>>(new Set());
  const [untagged, setUntagged] = useState(false);
  const [focusInt, setFocusInt] = useState<number | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const { tags, byObject: addrTags, refresh: refreshTags } = useTags("IPAddress");

  const refresh = useCallback(() => {
    api.get<Prefix>(`/api/v1/prefixes/${prefixId}`).then(setPrefix).catch(() => {});
    api
      .get<AddressPage>(`/api/v1/prefixes/${prefixId}/addresses?limit=20000`)
      .then(setPage)
      .catch(() => {});
    api
      .get<IpRange[]>(`/api/v1/ranges?prefix_id=${prefixId}`)
      .then(setRanges)
      .catch(() => {});
    refreshTags();
    setSelected(new Set());
  }, [prefixId, refreshTags]);

  useEffect(refresh, [refresh]);

  const allocNext = async () => {
    try {
      const r = await api.post<{ address: string }>(
        `/api/v1/prefixes/${prefixId}/available-ips`,
        {}
      );
      toast.success(`Reserved ${r.address}`);
      refresh();
    } catch (e) {
      toast.error("Allocation failed", { description: String(e) });
    }
  };

  const removeRange = async (r: IpRange) => {
    try {
      await api.del(`/api/v1/ranges/${r.id}`);
      toast.success("Range deleted");
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const importCsv = async (file: File) => {
    try {
      const rows = await api.postRaw<{ row: number; ok: boolean; detail: string }[]>(
        "/api/v1/addresses/import",
        await file.text()
      );
      const ok = rows.filter((r) => r.ok).length;
      const bad = rows.filter((r) => !r.ok);
      toast.success(`Imported ${ok} addresses`, {
        description: bad.length
          ? `${bad.length} rows skipped — nothing imported (fix errors and retry)`
          : undefined,
      });
      if (bad.length) console.warn("import errors", bad);
      refresh();
    } catch (e) {
      toast.error("Import failed", { description: String(e) });
    }
  };

  const bulk = async (payload: {
    action: string;
    status?: IpStatus;
    role?: IpRole | null;
    tag_id?: number;
  }) => {
    try {
      const r = await api.post<{ affected: number }>("/api/v1/addresses/bulk", {
        ids: [...selected],
        ...payload,
      });
      toast.success(`Updated ${r.affected} addresses`);
      refresh();
    } catch (e) {
      toast.error("Bulk update failed", { description: String(e) });
    }
  };

  const isV4 = !!prefix && !prefix.prefix.includes(":");
  const showGrid = isV4 && (page?.total ?? 0) <= MAX_GRID;

  const filtersActive =
    !!search || statusSel.size > 0 || tagSel.size > 0 || untagged;

  const filtered = useMemo(() => {
    const ql = search.trim().toLowerCase();
    return (page?.items ?? []).filter((a) => {
      if (ql) {
        const hay = [a.address, a.hostname, a.mac_address, a.vendor];
        if (!hay.some((v) => v && v.toLowerCase().includes(ql))) return false;
      }
      if (statusSel.size && !statusSel.has(a.status)) return false;
      const at = addrTags.get(a.id) ?? [];
      if (untagged && at.length > 0) return false;
      if (tagSel.size && !at.some((t) => tagSel.has(t.id))) return false;
      return true;
    });
  }, [page, search, statusSel, tagSel, untagged, addrTags]);

  const matchIds = useMemo(
    () => (filtersActive ? new Set(filtered.map((a) => a.id)) : null),
    [filtersActive, filtered]
  );

  const highlight = useMemo(() => {
    const m = new Map<number, string>();
    if (!tagSel.size) return m;
    for (const a of filtered) {
      const hit = (addrTags.get(a.id) ?? []).find((t) => tagSel.has(t.id));
      if (hit) m.set(a.id, hit.color);
    }
    return m;
  }, [filtered, tagSel, addrTags]);

  const clearFilters = () => {
    setSearch("");
    setStatusSel(new Set());
    setTagSel(new Set());
    setUntagged(false);
  };

  const pickAddress = (a: IpAddress) => {
    setFocusInt(Number(a.address_int));
    setDrawer({ ip: a.address, addr: a });
  };

  const allChecked =
    filtered.length > 0 && filtered.every((a) => selected.has(a.id));

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/prefixes">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        {prefix ? (
          <>
            <h1 className="font-mono text-xl font-semibold">{prefix.prefix}</h1>
            <PrefixStatusBadge s={prefix.status} />
            {prefix.vlan && (
              <span className="text-sm text-muted-foreground">
                VLAN {prefix.vlan.vid} · {prefix.vlan.name}
              </span>
            )}
          </>
        ) : (
          <Skeleton className="h-7 w-48" />
        )}
        <div className="ml-auto flex gap-2">
          <Button size="sm" variant="outline" onClick={() => fileRef.current?.click()}>
            <Upload /> Import
          </Button>
          <input
            ref={fileRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) importCsv(f);
              e.target.value = "";
            }}
          />
          <Button size="sm" variant="outline" asChild>
            <a href={`/api/v1/addresses/export.csv?prefix_id=${prefixId}`} download>
              <Download /> Export
            </a>
          </Button>
          <Button size="sm" variant="outline" onClick={() => setRangeOpen(true)}>
            <Plus /> IP range
          </Button>
          <Button size="sm" onClick={allocNext}>
            <Zap /> Allocate next free IP
          </Button>
        </div>
      </div>

      {prefix && (
        <Card>
          <CardContent className="flex items-center gap-6 p-4 text-sm">
            <div className="w-56">
              <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                <span>utilization</span>
                <span>{prefix.utilization_pct}%</span>
              </div>
              <Progress value={prefix.utilization_pct} />
            </div>
            <span>{prefix.used_ips.toLocaleString()} used</span>
            <span className="text-muted-foreground">
              {prefix.free_ips.toLocaleString()} free of{" "}
              {prefix.usable_ips.toLocaleString()} usable
            </span>
            {ranges.length > 0 && (
              <span className="text-sky-400">
                {ranges.length} range{ranges.length > 1 ? "s" : ""}
              </span>
            )}
            {prefix.description && (
              <span className="ml-auto text-muted-foreground">{prefix.description}</span>
            )}
          </CardContent>
        </Card>
      )}

      {ranges.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">IP ranges</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Range</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead className="w-16 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ranges.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-mono">
                      {r.start_address} – {r.end_address}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{r.role}</Badge>
                    </TableCell>
                    <TableCell>
                      {(Number(r.end_int) - Number(r.start_int) + 1).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {r.description ?? "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="icon" onClick={() => removeRange(r)}>
                        <Trash2 className="h-4 w-4 text-rose-400" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            Address map
            <span className="flex gap-3 text-xs font-normal text-muted-foreground">
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-emerald-500/60" />active</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-violet-500/60" />discovered</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-amber-500/60" />reserved</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-cyan-500/60" />dhcp</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm border border-dashed border-sky-700 bg-sky-900/40" />range</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-zinc-600/60" />offline</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-zinc-800" />free</i>
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!page ? (
            <Skeleton className="h-64 w-full" />
          ) : (
            <div className="flex flex-col gap-4 lg:flex-row">
              <div className="min-w-0 flex-1">
                {showGrid ? (
                  <SubnetGrid
                    page={page}
                    ranges={ranges}
                    onSelect={(ip, addr) => setDrawer({ ip, addr })}
                    tags={addrTags}
                    matchIds={matchIds}
                    highlight={highlight}
                    focusInt={focusInt}
                  />
                ) : (
                  <AddressTable
                    items={filtered}
                    tags={addrTags}
                    allTags={tags}
                    selected={selected}
                    onToggle={(id, on) => {
                      const next = new Set(selected);
                      if (on) next.add(id);
                      else next.delete(id);
                      setSelected(next);
                    }}
                    onToggleAll={(on) =>
                      setSelected(
                        on ? new Set(filtered.map((a) => a.id)) : new Set()
                      )
                    }
                    allChecked={allChecked}
                    onTagsChanged={refreshTags}
                    onSelect={(a) => setDrawer({ ip: a.address, addr: a })}
                  />
                )}
              </div>
              <aside className="w-full shrink-0 lg:w-72">
                <AddressFilterPanel
                  items={page.items}
                  filtered={filtered}
                  tags={tags}
                  addrTags={addrTags}
                  search={search}
                  onSearch={setSearch}
                  statusSel={statusSel}
                  onToggleStatus={(s) => setStatusSel(toggleIn(statusSel, s))}
                  tagSel={tagSel}
                  onToggleTag={(id) => setTagSel(toggleIn(tagSel, id))}
                  untagged={untagged}
                  onToggleUntagged={() => setUntagged(!untagged)}
                  onClear={clearFilters}
                  onSelectMatching={() =>
                    setSelected(new Set(filtered.map((a) => a.id)))
                  }
                  onPick={pickAddress}
                  onTagsChanged={refreshTags}
                />
              </aside>
            </div>
          )}
        </CardContent>
      </Card>

      {selected.size > 0 && (
        <div className="sticky bottom-4 z-10 mx-auto flex w-fit items-center gap-3 rounded-lg border bg-card px-4 py-2 shadow-lg">
          <span className="text-sm text-muted-foreground">
            {selected.size} selected
          </span>
          <Select onValueChange={(v) => bulk({ action: "set_status", status: v as IpStatus })}>
            <SelectTrigger className="h-8 w-36">
              <SelectValue placeholder="Set status…" />
            </SelectTrigger>
            <SelectContent>
              {IP_STATUSES.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select onValueChange={(v) => bulk({ action: "set_role", role: v as IpRole })}>
            <SelectTrigger className="h-8 w-32">
              <SelectValue placeholder="Set role…" />
            </SelectTrigger>
            <SelectContent>
              {IP_ROLES.map((r) => (
                <SelectItem key={r} value={r}>
                  {r}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                Tags
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Apply tag</DropdownMenuLabel>
              {tags.map((t) => (
                <DropdownMenuItem key={t.id} onClick={() => bulk({ action: "add_tag", tag_id: t.id })}>
                  <TagChip tag={t} />
                </DropdownMenuItem>
              ))}
              {tags.length > 0 && <DropdownMenuSeparator />}
              <DropdownMenuLabel>Remove tag</DropdownMenuLabel>
              {tags.map((t) => (
                <DropdownMenuItem
                  key={t.id}
                  onClick={() => bulk({ action: "remove_tag", tag_id: t.id })}
                >
                  <TagChip tag={t} />
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => bulk({ action: "delete" })}
          >
            <Trash2 /> Delete
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setSelected(new Set())}>
            Clear
          </Button>
        </div>
      )}

      {drawer && (
        <IpDrawer
          open
          onOpenChange={(o) => !o && setDrawer(null)}
          ip={drawer.ip}
          addr={drawer.addr}
          prefixId={prefixId}
          onSaved={refresh}
          allTags={tags}
          assigned={drawer.addr ? (addrTags.get(drawer.addr.id) ?? []) : []}
          onTagsChanged={refreshTags}
        />
      )}
      {prefix && (
        <RangeDialog
          open={rangeOpen}
          onOpenChange={setRangeOpen}
          prefix={prefix}
          onSaved={refresh}
        />
      )}
    </div>
  );
}

function AddressTable({
  items,
  tags,
  allTags,
  selected,
  onToggle,
  onToggleAll,
  allChecked,
  onTagsChanged,
  onSelect,
}: {
  items: IpAddress[];
  tags: Map<number, Tag[]>;
  allTags: Tag[];
  selected: Set<number>;
  onToggle: (id: number, on: boolean) => void;
  onToggleAll: (on: boolean) => void;
  allChecked: boolean;
  onTagsChanged: () => void;
  onSelect: (a: IpAddress) => void;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-8">
            <Checkbox checked={allChecked} onCheckedChange={(v) => onToggleAll(!!v)} />
          </TableHead>
          <TableHead>Address</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Role</TableHead>
          <TableHead>Tags</TableHead>
          <TableHead>Hostname</TableHead>
          <TableHead>MAC</TableHead>
          <TableHead>Vendor</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Ports</TableHead>
          <TableHead>Last seen</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((a) => {
          const assigned = tags.get(a.id) ?? [];
          return (
            <TableRow key={a.id} className="cursor-pointer" onClick={() => onSelect(a)}>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <Checkbox
                  checked={selected.has(a.id)}
                  onCheckedChange={(v) => onToggle(a.id, !!v)}
                />
              </TableCell>
              <TableCell className="font-mono">
                {a.address}
                {a.nat_inside_id && (
                  <span className="ml-1 text-xs text-sky-400" title="NAT inside">
                    ⇄
                  </span>
                )}
              </TableCell>
              <TableCell>
                <IpStatusBadge s={a.status} />
              </TableCell>
              <TableCell className="text-muted-foreground">
                {a.role ?? "—"}
              </TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center gap-1">
                  {assigned.map((t) => (
                    <TagChip key={t.id} tag={t} />
                  ))}
                  <TagPicker
                    objectType="IPAddress"
                    objectId={a.id}
                    allTags={allTags}
                    assigned={assigned}
                    onChanged={onTagsChanged}
                  />
                </div>
              </TableCell>
              <TableCell>{a.hostname ?? "—"}</TableCell>
              <TableCell className="font-mono text-xs">{a.mac_address ?? "—"}</TableCell>
              <TableCell className="text-muted-foreground">{a.vendor ?? "—"}</TableCell>
              <TableCell>
                {a.device_type ? (
                  <Badge variant="secondary" className="capitalize">
                    {a.device_type}
                  </Badge>
                ) : (
                  "—"
                )}
              </TableCell>
              <TableCell className="font-mono text-xs text-muted-foreground">
                {a.open_ports?.length ? a.open_ports.join(" ") : "—"}
              </TableCell>
              <TableCell className="text-muted-foreground">{timeAgo(a.last_seen)}</TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}
