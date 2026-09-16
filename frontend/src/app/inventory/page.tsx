"use client";

import { useEffect, useMemo, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { foldHebrew } from "@/lib/utils";
import { SortHeader } from "@/components/sort-header";
import type { Asset, AssetKind, Site } from "@/types";
import { Badge } from "@/components/ui/badge";
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

const EMPTY = {
  kind: "hardware" as AssetKind,
  category: "",
  vendor: "",
  model: "",
  purpose: "",
  version: "",
  eol_on: "",
  support_status: "",
  serial_number: "",
  site_id: "none",
  notes: "",
};

export default function InventoryPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [items, setItems] = useState<Asset[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [q, setQ] = useState("");
  const [kindFilter, setKindFilter] = useState("all");
  const [sorting, setSorting] = useState<SortingState>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Asset | null>(null);
  const [deleting, setDeleting] = useState<Asset | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = () => {
    api.get<Asset[]>("/api/v1/assets").then(setItems).catch(() => {});
    api.get<Site[]>("/api/v1/sites").then(setSites).catch(() => {});
  };
  useEffect(refresh, []);

  useEffect(() => {
    if (dialogOpen) {
      setForm(
        editing
          ? {
              kind: editing.kind,
              category: editing.category ?? "",
              vendor: editing.vendor ?? "",
              model: editing.model ?? "",
              purpose: editing.purpose ?? "",
              version: editing.version ?? "",
              eol_on: editing.eol_on ?? "",
              support_status: editing.support_status ?? "",
              serial_number: editing.serial_number ?? "",
              site_id: editing.site_id ? String(editing.site_id) : "none",
              notes: editing.notes ?? "",
            }
          : EMPTY
      );
    }
  }, [dialogOpen, editing]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        ...Object.fromEntries(
          Object.entries(form)
            .filter(([k]) => k !== "site_id")
            .map(([k, v]) => [k, v || null])
        ),
        kind: form.kind,
        eol_on: form.eol_on || null,
        site_id: form.site_id === "none" ? null : Number(form.site_id),
      };
      if (editing) {
        await api.patch(`/api/v1/assets/${editing.id}`, body);
        toast.success("Asset updated");
      } else {
        await api.post("/api/v1/assets", body);
        toast.success("Asset added");
      }
      setDialogOpen(false);
      refresh();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doDelete = async () => {
    if (!deleting) return;
    try {
      await api.del(`/api/v1/assets/${deleting.id}`);
      toast.success("Asset deleted");
      setDeleting(null);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const siteName = useMemo(
    () => Object.fromEntries(sites.map((s) => [s.id, s.name])),
    [sites]
  );

  const filtered = useMemo(() => {
    const needle = foldHebrew(q.toLowerCase());
    return items.filter((a) => {
      if (kindFilter !== "all" && a.kind !== kindFilter) return false;
      if (!q) return true;
      return [
        a.vendor,
        a.model,
        a.serial_number,
        a.purpose,
        a.category,
        a.version,
        a.support_status,
        a.notes,
        a.site_id ? siteName[a.site_id] : null,
      ].some((f) => f != null && foldHebrew(f.toLowerCase()).includes(needle));
    });
  }, [items, q, kindFilter, siteName]);

  const eolBadge = (eol: string | null) => {
    if (!eol) return <span className="text-muted-foreground">—</span>;
    const past = new Date(eol).getTime() < Date.now();
    return (
      <Badge
        variant="outline"
        className={
          past
            ? "border-rose-500/40 text-rose-400"
            : "border-amber-500/40 text-amber-400"
        }
      >
        {past ? "EOL" : `EOL ${eol}`}
      </Badge>
    );
  };

  const columns = useMemo<ColumnDef<Asset>[]>(
    () => [
      {
        id: "model",
        accessorFn: (a) => a.model ?? a.category ?? "",
        header: ({ column }) => (
          <SortHeader column={column}>Model</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="font-medium">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "kind",
        header: ({ column }) => <SortHeader column={column}>Kind</SortHeader>,
        cell: (c) => <Badge variant="outline">{c.getValue<string>()}</Badge>,
      },
      {
        accessorKey: "vendor",
        header: ({ column }) => (
          <SortHeader column={column}>Vendor</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "serial_number",
        header: ({ column }) => (
          <SortHeader column={column}>Serial</SortHeader>
        ),
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        id: "site",
        accessorFn: (a) => (a.site_id ? (siteName[a.site_id] ?? "") : ""),
        header: ({ column }) => <SortHeader column={column}>Site</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "purpose",
        header: ({ column }) => (
          <SortHeader column={column}>Purpose</SortHeader>
        ),
        cell: (c) => (
          <span
            dir="auto"
            title={c.getValue<string | null>() ?? undefined}
            className="block max-w-[200px] truncate text-muted-foreground"
          >
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "version",
        header: ({ column }) => (
          <SortHeader column={column}>Version</SortHeader>
        ),
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "support_status",
        header: ({ column }) => (
          <SortHeader column={column}>Support</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "eol_on",
        header: ({ column }) => <SortHeader column={column}>EOL</SortHeader>,
        cell: (c) => eolBadge(c.getValue<string | null>()),
      },
      {
        id: "actions",
        header: () => <div className="text-right">Actions</div>,
        enableSorting: false,
        cell: (c) => (
          <div className="flex justify-end gap-1">
            {canWrite && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => {
                  setEditing(c.row.original);
                  setDialogOpen(true);
                }}
              >
                <Pencil className="h-4 w-4" />
              </Button>
            )}
            {canDelete && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setDeleting(c.row.original)}
              >
                <Trash2 className="h-4 w-4 text-rose-400" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [siteName, canWrite, canDelete]
  );

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: { sorting },
    onSortingChange: setSorting,
  });

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Inventory</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New asset
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search inventory…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Select value={kindFilter} onValueChange={setKindFilter}>
          <SelectTrigger className="w-36">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All kinds</SelectItem>
            <SelectItem value="hardware">Hardware</SelectItem>
            <SelectItem value="software">Software</SelectItem>
          </SelectContent>
        </Select>
        <span className="ml-auto text-sm text-muted-foreground">
          {table.getRowModel().rows.length} of {items.length}
        </span>
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
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {table.getRowModel().rows.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={10}
                  className="py-10 text-center text-muted-foreground"
                >
                  No assets found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit asset" : "New asset"}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Kind</Label>
              <Select
                value={form.kind}
                onValueChange={(v) => setForm({ ...form, kind: v as AssetKind })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hardware">Hardware</SelectItem>
                  <SelectItem value="software">Software</SelectItem>
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
                  <SelectItem value="none">None</SelectItem>
                  {sites.map((s) => (
                    <SelectItem key={s.id} value={String(s.id)}>
                      <span dir="auto">{s.name}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Category</Label>
              <Input dir="auto" value={form.category} onChange={set("category")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Vendor</Label>
              <Input dir="auto" value={form.vendor} onChange={set("vendor")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Model</Label>
              <Input dir="auto" value={form.model} onChange={set("model")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Serial number</Label>
              <Input
                dir="ltr"
                value={form.serial_number}
                onChange={set("serial_number")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Version</Label>
              <Input dir="ltr" value={form.version} onChange={set("version")} />
            </div>
            <div className="grid gap-1.5">
              <Label>EOL date</Label>
              <Input
                type="date"
                dir="ltr"
                value={form.eol_on}
                onChange={set("eol_on")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Support status</Label>
              <Input
                dir="auto"
                value={form.support_status}
                onChange={set("support_status")}
              />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Purpose</Label>
              <Input dir="auto" value={form.purpose} onChange={set("purpose")} />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Notes</Label>
              <Input dir="auto" value={form.notes} onChange={set("notes")} />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={submit} disabled={busy}>
              {busy ? "Saving…" : editing ? "Save" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleting !== null} onOpenChange={() => setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete asset</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.model ?? deleting?.serial_number}
            </span>
            ?
          </p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
