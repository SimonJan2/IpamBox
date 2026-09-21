"use client";

import { useEffect, useId, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Download, History, Pencil, Plus, Trash2 } from "lucide-react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { foldHebrew, ipToInt } from "@/lib/utils";
import { useUrlParam, useUrlSorting, useUrlText } from "@/lib/url-state";
import { useRowNav } from "@/lib/row-nav";
import { SortHeader, columnAriaSort } from "@/components/sort-header";
import { AsyncPanel } from "@/components/async-panel";
import { HistoryDialog } from "@/components/history-panel";
import { SavedViews } from "@/components/saved-views";
import type { Page, Prefix, Site, Vlan, Vrf } from "@/types";
import { PrefixStatusBadge } from "@/components/status-badge";
import { TagChip, TagPicker, useTags } from "@/components/tag-picker";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
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

function utilColor(pct: number) {
  if (pct > 80) return "bg-rose-500";
  if (pct > 50) return "bg-amber-500";
  return "bg-emerald-500";
}

function NewPrefixDialog({
  open,
  onOpenChange,
  vrfs,
  sites,
  vlans,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  vrfs: Vrf[];
  sites: Site[];
  vlans: Vlan[];
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    prefix: "",
    vrf_id: "",
    site_id: "none",
    vlan_id: "none",
    status: "active",
    description: "",
  });
  const [busy, setBusy] = useState(false);
  const uid = useId();

  const submit = async () => {
    setBusy(true);
    try {
      await api.post("/api/v1/prefixes", {
        prefix: form.prefix,
        vrf_id: Number(form.vrf_id),
        site_id: form.site_id === "none" ? null : Number(form.site_id),
        vlan_id: form.vlan_id === "none" ? null : Number(form.vlan_id),
        status: form.status,
        description: form.description || null,
      });
      toast.success("Prefix created");
      onOpenChange(false);
      onCreated();
    } catch (e) {
      toast.error("Create failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New prefix</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-cidr`}>CIDR</Label>
            <Input
              id={`${uid}-cidr`}
              placeholder="192.168.20.0/24"
              value={form.prefix}
              onChange={(e) => setForm({ ...form, prefix: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-vrf`}>VRF</Label>
              <Select
                value={form.vrf_id}
                onValueChange={(v) => setForm({ ...form, vrf_id: v })}
              >
                <SelectTrigger id={`${uid}-vrf`}>
                  <SelectValue placeholder="Select VRF" />
                </SelectTrigger>
                <SelectContent>
                  {vrfs.map((v) => (
                    <SelectItem key={v.id} value={String(v.id)}>
                      {v.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-site`}>Site</Label>
              <Select
                value={form.site_id}
                onValueChange={(v) => setForm({ ...form, site_id: v })}
              >
                <SelectTrigger id={`${uid}-site`}>
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {sites.map((s) => (
                    <SelectItem key={s.id} value={String(s.id)}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-vlan`}>VLAN</Label>
            <Select
              value={form.vlan_id}
              onValueChange={(v) => setForm({ ...form, vlan_id: v })}
            >
              <SelectTrigger id={`${uid}-vlan`}>
                <SelectValue placeholder="None" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
                {vlans.map((v) => (
                  <SelectItem key={v.id} value={String(v.id)}>
                    {v.vid} · {v.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-status`}>Status</Label>
            <Select
              value={form.status}
              onValueChange={(v) => setForm({ ...form, status: v })}
            >
              <SelectTrigger id={`${uid}-status`}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {["active", "container", "reserved", "deprecated"].map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-description`}>Description</Label>
            <Input
              id={`${uid}-description`}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !form.prefix || !form.vrf_id}>
            {busy ? "Creating…" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function EditPrefixDialog({
  prefix,
  vrfs,
  sites,
  vlans,
  onOpenChange,
  onSaved,
}: {
  prefix: Prefix | null;
  vrfs: Vrf[];
  sites: Site[];
  vlans: Vlan[];
  onOpenChange: (o: boolean) => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    vrf_id: "",
    site_id: "none",
    vlan_id: "none",
    status: "active",
    description: "",
  });
  const [busy, setBusy] = useState(false);
  const uid = useId();

  useEffect(() => {
    if (prefix) {
      setForm({
        vrf_id: String(prefix.vrf_id),
        site_id: prefix.site_id ? String(prefix.site_id) : "none",
        vlan_id: prefix.vlan_id ? String(prefix.vlan_id) : "none",
        status: prefix.status,
        description: prefix.description ?? "",
      });
    }
  }, [prefix]);

  const submit = async () => {
    if (!prefix) return;
    setBusy(true);
    try {
      await api.patch(`/api/v1/prefixes/${prefix.id}`, {
        vrf_id: Number(form.vrf_id),
        site_id: form.site_id === "none" ? null : Number(form.site_id),
        vlan_id: form.vlan_id === "none" ? null : Number(form.vlan_id),
        status: form.status,
        description: form.description || null,
      });
      toast.success("Prefix updated");
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Update failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={prefix !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Edit <span className="font-mono">{prefix?.prefix}</span>
          </DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-vrf`}>VRF</Label>
              <Select
                value={form.vrf_id}
                onValueChange={(v) => setForm({ ...form, vrf_id: v })}
              >
                <SelectTrigger id={`${uid}-vrf`}>
                  <SelectValue placeholder="Select VRF" />
                </SelectTrigger>
                <SelectContent>
                  {vrfs.map((v) => (
                    <SelectItem key={v.id} value={String(v.id)}>
                      {v.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-site`}>Site</Label>
              <Select
                value={form.site_id}
                onValueChange={(v) => setForm({ ...form, site_id: v })}
              >
                <SelectTrigger id={`${uid}-site`}>
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {sites.map((s) => (
                    <SelectItem key={s.id} value={String(s.id)}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-vlan`}>VLAN</Label>
              <Select
                value={form.vlan_id}
                onValueChange={(v) => setForm({ ...form, vlan_id: v })}
              >
                <SelectTrigger id={`${uid}-vlan`}>
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {vlans.map((v) => (
                    <SelectItem key={v.id} value={String(v.id)}>
                      {v.vid} · {v.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-status`}>Status</Label>
              <Select
                value={form.status}
                onValueChange={(v) => setForm({ ...form, status: v })}
              >
                <SelectTrigger id={`${uid}-status`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["active", "container", "reserved", "deprecated"].map((s) => (
                    <SelectItem key={s} value={s}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-description`}>Description</Label>
            <Input
              id={`${uid}-description`}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy}>
            {busy ? "Saving…" : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DeletePrefixDialog({
  prefix,
  onOpenChange,
  onDeleted,
}: {
  prefix: Prefix | null;
  onOpenChange: (o: boolean) => void;
  onDeleted: () => void;
}) {
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!prefix) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/prefixes/${prefix.id}`);
      toast.success(`Deleted ${prefix.prefix}`);
      onOpenChange(false);
      onDeleted();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={prefix !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete prefix</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Delete{" "}
          <span className="font-mono font-medium text-foreground">
            {prefix?.prefix}
          </span>
          ? Its {prefix?.used_ips ?? 0} tracked IP
          {prefix?.used_ips === 1 ? "" : "s"} will be removed. This cannot be
          undone.
        </p>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={submit} disabled={busy}>
            {busy ? "Deleting…" : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Lookup names are baked into the row objects: TanStack caches accessorFn
// results per row for the lifetime of `data`, so reading vrfName/siteName
// inside accessorFn leaves "" cached when the lookup fetch resolves after
// the prefixes fetch.
type PrefixRow = Prefix & { vrf_name: string; site_name: string };

export default function PrefixesPage() {
  const router = useRouter();
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const prefixesQ = useAsyncData(() =>
    api.get<Prefix[]>("/api/v1/prefixes")
  );
  const vrfsQ = useAsyncData(async () => {
    try {
      return await api.get<Vrf[]>("/api/v1/vrfs");
    } catch (e) {
      toast.error("Could not load VRFs", { description: String(e) });
      return [];
    }
  });
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Site>>("/api/v1/sites").then((p) => p.items);
    } catch (e) {
      toast.error("Could not load sites", { description: String(e) });
      return [];
    }
  });
  const vlansQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Vlan>>("/api/v1/vlans").then((p) => p.items);
    } catch (e) {
      toast.error("Could not load VLANs", { description: String(e) });
      return [];
    }
  });
  const [q, setQRaw] = useUrlText("q");
  const setQ = (v: string | ((p: string) => string)) =>
    setQRaw(typeof v === "function" ? v(q) : v);
  const [vrfFilter, setVrfFilter] = useUrlParam("vrf", "all");
  const [sorting, setSorting] = useUrlSorting();
  const [createOpen, setCreateOpen] = useState(false);
  const [editing, setEditing] = useState<Prefix | null>(null);
  const [deleting, setDeleting] = useState<Prefix | null>(null);
  const [historyFor, setHistoryFor] = useState<Prefix | null>(null);
  const { tags, byObject: prefixTags, refresh: refreshTags } = useTags("Prefix");

  const prefixes = prefixesQ.data ?? [];
  const vrfs = vrfsQ.data ?? [];
  const sites = sitesQ.data ?? [];
  const vlans = vlansQ.data ?? [];

  const refresh = () => {
    void prefixesQ.reload();
    refreshTags();
  };

  const vrfName = useMemo(
    () => Object.fromEntries(vrfs.map((v) => [v.id, v.name])),
    [vrfs]
  );
  const siteName = useMemo(
    () => Object.fromEntries(sites.map((s) => [s.id, s.name])),
    [sites]
  );

  const columns = useMemo<ColumnDef<PrefixRow>[]>(
    () => [
      {
        accessorKey: "prefix",
        header: ({ column }) => (
          <SortHeader column={column}>Prefix</SortHeader>
        ),
        sortingFn: (a, b) => {
          const [aNet, aLen] = a.original.prefix.split("/");
          const [bNet, bLen] = b.original.prefix.split("/");
          const diff = ipToInt(aNet) - ipToInt(bNet);
          return diff !== 0 ? diff : Number(aLen) - Number(bLen);
        },
        cell: (c) => <span className="font-mono">{c.getValue<string>()}</span>,
      },
      {
        id: "vrf",
        accessorKey: "vrf_name",
        header: ({ column }) => <SortHeader column={column}>VRF</SortHeader>,
        cell: (c) => c.getValue<string>(),
      },
      {
        id: "site",
        accessorKey: "site_name",
        header: ({ column }) => <SortHeader column={column}>Site</SortHeader>,
        cell: (c) => c.getValue<string>() || "—",
      },
      {
        id: "vlan",
        accessorFn: (p) => p.vlan?.vid ?? -1,
        header: ({ column }) => <SortHeader column={column}>VLAN</SortHeader>,
        cell: (c) => {
          const v = c.row.original.vlan;
          return v ? `${v.vid} · ${v.name}` : "—";
        },
      },
      {
        id: "tags",
        header: "Tags",
        enableSorting: false,
        cell: (c) => {
          const p = c.row.original;
          const assigned = prefixTags.get(p.id) ?? [];
          return (
            <div
              className="flex items-center gap-1"
              onClick={(e) => e.stopPropagation()}
            >
              {assigned.map((t) => (
                <TagChip key={t.id} tag={t} />
              ))}
              <TagPicker
                objectType="Prefix"
                objectId={p.id}
                allTags={tags}
                assigned={assigned}
                onChanged={refreshTags}
              />
            </div>
          );
        },
      },
      {
        accessorKey: "status",
        header: ({ column }) => (
          <SortHeader column={column}>Status</SortHeader>
        ),
        cell: (c) => <PrefixStatusBadge s={c.getValue<Prefix["status"]>()} />,
      },
      {
        accessorKey: "utilization_pct",
        header: ({ column }) => (
          <SortHeader column={column}>Utilization</SortHeader>
        ),
        cell: (c) => {
          const p = c.row.original;
          if (p.usable_ips === null) {
            // IPv6 — no summarized capacity (2^n overflows the display anyway)
            return (
              <span className="whitespace-nowrap text-xs text-muted-foreground">
                {p.used_ips} tracked · —
              </span>
            );
          }
          return (
            <div className="flex w-40 items-center gap-2">
              <Progress
                value={p.utilization_pct ?? 0}
                className="h-1.5"
                indicatorClassName={utilColor(p.utilization_pct ?? 0)}
              />
              <span className="whitespace-nowrap text-xs text-muted-foreground">
                {p.used_ips}/{p.usable_ips} · {p.utilization_pct}%
              </span>
            </div>
          );
        },
      },
      {
        accessorKey: "description",
        header: ({ column }) => (
          <SortHeader column={column}>Description</SortHeader>
        ),
        cell: (c) => (
          <span className="text-muted-foreground">{c.getValue<string | null>() ?? ""}</span>
        ),
      },
      {
        id: "actions",
        header: "",
        enableSorting: false,
        cell: (c) => (
          <div
            className="flex justify-end gap-1"
            onClick={(e) => e.stopPropagation()}
          >
            <Button
              variant="ghost"
              size="icon"
              aria-label={`History of ${c.row.original.prefix}`}
              onClick={() => setHistoryFor(c.row.original)}
            >
              <History className="h-4 w-4" />
            </Button>
            {canWrite && (
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Edit ${c.row.original.prefix}`}
                onClick={() => setEditing(c.row.original)}
              >
                <Pencil className="h-4 w-4" />
              </Button>
            )}
            {canDelete && (
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Delete ${c.row.original.prefix}`}
                onClick={() => setDeleting(c.row.original)}
              >
                <Trash2 className="h-4 w-4 text-rose-400" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [tags, prefixTags, refreshTags, canWrite, canDelete]
  );

  const rows = useMemo<PrefixRow[]>(
    () =>
      prefixes.map((p) => ({
        ...p,
        vrf_name: vrfName[p.vrf_id] ?? "",
        site_name: p.site_id ? (siteName[p.site_id] ?? "") : "",
      })),
    [prefixes, vrfName, siteName]
  );

  const filtered = useMemo(
    () => (vrfFilter === "all" ? rows : rows.filter((p) => String(p.vrf_id) === vrfFilter)),
    [rows, vrfFilter]
  );

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: { sorting, globalFilter: q },
    onSortingChange: setSorting,
    onGlobalFilterChange: setQ,
    globalFilterFn: (row, _id, value) =>
      foldHebrew(JSON.stringify(row.original).toLowerCase()).includes(
        foldHebrew(String(value).toLowerCase())
      ),
  });

  const tableRows = table.getRowModel().rows;
  const { rowProps } = useRowNav({
    count: tableRows.length,
    onOpen: (i) => {
      const p = tableRows[i]?.original;
      if (p) router.push(`/prefixes/${p.id}`);
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Subnets</h1>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" asChild>
            <a
              href={
                "/api/v1/prefixes/export.csv" +
                (vrfFilter !== "all" || q
                  ? `?${new URLSearchParams({
                      ...(vrfFilter !== "all" ? { vrf_id: vrfFilter } : {}),
                      ...(q ? { q } : {}),
                    })}`
                  : "")
              }
              download
              title="Downloads the prefixes the current filters show"
            >
              <Download /> CSV
            </a>
          </Button>
          {canWrite && (
            <Button size="sm" onClick={() => setCreateOpen(true)}>
              <Plus /> New prefix
            </Button>
          )}
        </div>
      </div>

      <div className="flex gap-3">
        <Input
          placeholder="Search prefixes…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Select value={vrfFilter} onValueChange={setVrfFilter}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="All VRFs" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All VRFs</SelectItem>
            {vrfs.map((v) => (
              <SelectItem key={v.id} value={String(v.id)}>
                {v.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <SavedViews pageKey="prefixes" className="ml-auto" />
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={prefixesQ.loading}
          error={prefixesQ.error}
          onRetry={prefixesQ.reload}
          empty={prefixes.length === 0}
          emptyMessage="No prefixes yet — create the first one."
        >
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((hg) => (
              <TableRow key={hg.id}>
                {hg.headers.map((h) => (
                  <TableHead key={h.id} aria-sort={columnAriaSort(h.column)}>
                    {flexRender(h.column.columnDef.header, h.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {tableRows.map((row, i) => (
              <TableRow
                key={row.id}
                {...rowProps(i)}
                className="cursor-pointer focus-visible:bg-muted/50 focus-visible:outline-none"
                onClick={() => router.push(`/prefixes/${row.original.id}`)}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {tableRows.length === 0 && prefixes.length > 0 && (
              <TableRow>
                <TableCell colSpan={9} className="py-10 text-center text-muted-foreground">
                  No prefixes match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </AsyncPanel>
      </div>

      <NewPrefixDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        vrfs={vrfs}
        sites={sites}
        vlans={vlans}
        onCreated={refresh}
      />
      <EditPrefixDialog
        prefix={editing}
        vrfs={vrfs}
        sites={sites}
        vlans={vlans}
        onOpenChange={() => setEditing(null)}
        onSaved={refresh}
      />
      <DeletePrefixDialog
        prefix={deleting}
        onOpenChange={() => setDeleting(null)}
        onDeleted={refresh}
      />
      <HistoryDialog
        open={historyFor !== null}
        onOpenChange={() => setHistoryFor(null)}
        objectType="Prefix"
        objectId={historyFor?.id ?? null}
        title={historyFor?.prefix}
      />
    </div>
  );
}
