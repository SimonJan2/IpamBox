"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Pencil, Plus, Trash2 } from "lucide-react";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";
import { toast } from "sonner";

import { api } from "@/lib/api";
import type { Prefix, Site, Vrf } from "@/types";
import { PrefixStatusBadge } from "@/components/status-badge";
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
  onCreated,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  vrfs: Vrf[];
  sites: Site[];
  onCreated: () => void;
}) {
  const [form, setForm] = useState({
    prefix: "",
    vrf_id: "",
    site_id: "",
    vlan_id: "",
    vlan_name: "",
    status: "active",
    description: "",
  });
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setBusy(true);
    try {
      await api.post("/api/v1/prefixes", {
        prefix: form.prefix,
        vrf_id: Number(form.vrf_id),
        site_id: form.site_id ? Number(form.site_id) : null,
        vlan_id: form.vlan_id ? Number(form.vlan_id) : null,
        vlan_name: form.vlan_name || null,
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
            <Label>CIDR</Label>
            <Input
              placeholder="192.168.20.0/24"
              value={form.prefix}
              onChange={(e) => setForm({ ...form, prefix: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>VRF</Label>
              <Select
                value={form.vrf_id}
                onValueChange={(v) => setForm({ ...form, vrf_id: v })}
              >
                <SelectTrigger>
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
              <Label>Site</Label>
              <Select
                value={form.site_id}
                onValueChange={(v) => setForm({ ...form, site_id: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
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
              <Label>VLAN ID</Label>
              <Input
                type="number"
                min={1}
                max={4094}
                value={form.vlan_id}
                onChange={(e) => setForm({ ...form, vlan_id: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>VLAN name</Label>
              <Input
                value={form.vlan_name}
                onChange={(e) => setForm({ ...form, vlan_name: e.target.value })}
              />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label>Status</Label>
            <Select
              value={form.status}
              onValueChange={(v) => setForm({ ...form, status: v })}
            >
              <SelectTrigger>
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
            <Label>Description</Label>
            <Input
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
  sites,
  onOpenChange,
  onSaved,
}: {
  prefix: Prefix | null;
  sites: Site[];
  onOpenChange: (o: boolean) => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    site_id: "",
    vlan_id: "",
    vlan_name: "",
    status: "active",
    description: "",
  });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (prefix) {
      setForm({
        site_id: prefix.site_id ? String(prefix.site_id) : "",
        vlan_id: prefix.vlan_id ? String(prefix.vlan_id) : "",
        vlan_name: prefix.vlan_name ?? "",
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
        site_id: form.site_id ? Number(form.site_id) : null,
        vlan_id: form.vlan_id ? Number(form.vlan_id) : null,
        vlan_name: form.vlan_name || null,
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
          <div className="grid gap-1.5">
            <Label>Site</Label>
            <Select
              value={form.site_id}
              onValueChange={(v) => setForm({ ...form, site_id: v })}
            >
              <SelectTrigger>
                <SelectValue placeholder="None" />
              </SelectTrigger>
              <SelectContent>
                {sites.map((s) => (
                  <SelectItem key={s.id} value={String(s.id)}>
                    {s.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>VLAN ID</Label>
              <Input
                type="number"
                min={1}
                max={4094}
                value={form.vlan_id}
                onChange={(e) => setForm({ ...form, vlan_id: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>VLAN name</Label>
              <Input
                value={form.vlan_name}
                onChange={(e) => setForm({ ...form, vlan_name: e.target.value })}
              />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label>Status</Label>
            <Select
              value={form.status}
              onValueChange={(v) => setForm({ ...form, status: v })}
            >
              <SelectTrigger>
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
            <Label>Description</Label>
            <Input
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

export default function PrefixesPage() {
  const router = useRouter();
  const [prefixes, setPrefixes] = useState<Prefix[]>([]);
  const [vrfs, setVrfs] = useState<Vrf[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [q, setQ] = useState("");
  const [vrfFilter, setVrfFilter] = useState("all");
  const [createOpen, setCreateOpen] = useState(false);
  const [editing, setEditing] = useState<Prefix | null>(null);
  const [deleting, setDeleting] = useState<Prefix | null>(null);

  const refresh = () => {
    api.get<Prefix[]>("/api/v1/prefixes").then(setPrefixes).catch(() => {});
    api.get<Vrf[]>("/api/v1/vrfs").then(setVrfs).catch(() => {});
    api.get<Site[]>("/api/v1/sites").then(setSites).catch(() => {});
  };
  useEffect(refresh, []);

  const vrfName = useMemo(
    () => Object.fromEntries(vrfs.map((v) => [v.id, v.name])),
    [vrfs]
  );
  const siteName = useMemo(
    () => Object.fromEntries(sites.map((s) => [s.id, s.name])),
    [sites]
  );

  const columns = useMemo<ColumnDef<Prefix>[]>(
    () => [
      {
        accessorKey: "prefix",
        header: "Prefix",
        cell: (c) => <span className="font-mono">{c.getValue<string>()}</span>,
      },
      {
        accessorKey: "vrf_id",
        header: "VRF",
        cell: (c) => vrfName[c.getValue<number>()] ?? c.getValue(),
      },
      {
        accessorKey: "site_id",
        header: "Site",
        cell: (c) =>
          c.getValue<number | null>() ? siteName[c.getValue<number>()!] : "—",
      },
      {
        accessorKey: "vlan_id",
        header: "VLAN",
        cell: (c) => {
          const id = c.getValue<number | null>();
          return id ? `VLAN ${id}` : "—";
        },
      },
      {
        accessorKey: "status",
        header: "Status",
        cell: (c) => <PrefixStatusBadge s={c.getValue<Prefix["status"]>()} />,
      },
      {
        accessorKey: "utilization_pct",
        header: "Utilization",
        cell: (c) => {
          const p = c.row.original;
          return (
            <div className="flex w-40 items-center gap-2">
              <Progress
                value={p.utilization_pct}
                className="h-1.5"
                indicatorClassName={utilColor(p.utilization_pct)}
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
        header: "Description",
        cell: (c) => (
          <span className="text-muted-foreground">{c.getValue<string | null>() ?? ""}</span>
        ),
      },
      {
        id: "actions",
        header: "",
        cell: (c) => (
          <div
            className="flex justify-end gap-1"
            onClick={(e) => e.stopPropagation()}
          >
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setEditing(c.row.original)}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setDeleting(c.row.original)}
            >
              <Trash2 className="h-4 w-4 text-rose-400" />
            </Button>
          </div>
        ),
      },
    ],
    [vrfName, siteName]
  );

  const filtered = useMemo(
    () => (vrfFilter === "all" ? prefixes : prefixes.filter((p) => String(p.vrf_id) === vrfFilter)),
    [prefixes, vrfFilter]
  );

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: { globalFilter: q },
    onGlobalFilterChange: setQ,
    globalFilterFn: (row, _id, value) =>
      JSON.stringify(row.original).toLowerCase().includes(String(value).toLowerCase()),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Subnets</h1>
        <Button size="sm" onClick={() => setCreateOpen(true)}>
          <Plus /> New prefix
        </Button>
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
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((hg) => (
              <TableRow key={hg.id}>
                {hg.headers.map((h) => (
                  <TableHead key={h.id}>
                    {flexRender(h.column.columnDef.header, h.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                className="cursor-pointer"
                onClick={() => router.push(`/prefixes/${row.original.id}`)}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {table.getRowModel().rows.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} className="py-10 text-center text-muted-foreground">
                  No prefixes found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <NewPrefixDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        vrfs={vrfs}
        sites={sites}
        onCreated={refresh}
      />
      <EditPrefixDialog
        prefix={editing}
        sites={sites}
        onOpenChange={() => setEditing(null)}
        onSaved={refresh}
      />
      <DeletePrefixDialog
        prefix={deleting}
        onOpenChange={() => setDeleting(null)}
        onDeleted={refresh}
      />
    </div>
  );
}
