"use client";

import { useEffect, useId, useMemo, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { usePrefs } from "@/lib/prefs";
import { PERM } from "@/lib/permissions";
import { foldHebrew } from "@/lib/utils";
import { useUrlSorting, useUrlText } from "@/lib/url-state";
import { SortHeader, columnAriaSort } from "@/components/sort-header";
import { AsyncPanel } from "@/components/async-panel";
import type { Site } from "@/types";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function SiteDialog({
  open,
  onOpenChange,
  site,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  site: Site | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: "",
    slug: "",
    description: "",
    code: "",
    site_number: "",
    size: "",
    is_active: true,
    contact: "",
    address: "",
  });
  const [busy, setBusy] = useState(false);
  const uid = useId();

  useEffect(() => {
    if (open) {
      setForm({
        name: site?.name ?? "",
        slug: site?.slug ?? "",
        description: site?.description ?? "",
        code: site?.code ?? "",
        site_number: site?.site_number?.toString() ?? "",
        size: site?.size ?? "",
        is_active: site?.is_active ?? true,
        contact: site?.contact ?? "",
        address: site?.address ?? "",
      });
    }
  }, [open, site]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        name: form.name,
        slug: form.slug || undefined,
        description: form.description || null,
        code: form.code || null,
        site_number: form.site_number ? +form.site_number : null,
        size: form.size || null,
        is_active: form.is_active,
        contact: form.contact || null,
        address: form.address || null,
      };
      if (site) {
        await api.patch(`/api/v1/sites/${site.id}`, body);
        toast.success("Site updated");
      } else {
        await api.post("/api/v1/sites", body);
        toast.success("Site created");
      }
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{site ? "Edit site" : "New site"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-name`}>Name</Label>
            <Input
              id={`${uid}-name`}
              placeholder="DC-East"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-slug`}>Slug</Label>
            <Input
              id={`${uid}-slug`}
              placeholder="dc-east (auto if empty)"
              value={form.slug}
              onChange={(e) => setForm({ ...form, slug: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-description`}>Description</Label>
            <Input
              id={`${uid}-description`}
              dir="auto"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-code`}>Code</Label>
              <Input
                id={`${uid}-code`}
                dir="ltr"
                placeholder="ALNB"
                value={form.code}
                onChange={(e) => setForm({ ...form, code: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-site-number`}>Site number</Label>
              <Input
                id={`${uid}-site-number`}
                dir="ltr"
                placeholder="2"
                value={form.site_number}
                onChange={(e) =>
                  setForm({ ...form, site_number: e.target.value })
                }
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-size`}>Size</Label>
              <Input
                id={`${uid}-size`}
                dir="auto"
                placeholder="קטן/בינוני/גדול"
                value={form.size}
                onChange={(e) => setForm({ ...form, size: e.target.value })}
              />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-contact`}>Contact</Label>
            <Input
              id={`${uid}-contact`}
              dir="auto"
              value={form.contact}
              onChange={(e) => setForm({ ...form, contact: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-address`}>Address</Label>
            <Input
              id={`${uid}-address`}
              dir="auto"
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
            />
            Active site
          </label>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !form.name}>
            {busy ? "Saving…" : site ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DeleteDialog({
  site,
  onOpenChange,
  onDeleted,
}: {
  site: Site | null;
  onOpenChange: (o: boolean) => void;
  onDeleted: () => void;
}) {
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!site) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/sites/${site.id}`);
      toast.success(`Deleted ${site.name}`);
      onOpenChange(false);
      onDeleted();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={site !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete site</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Delete <span className="font-medium text-foreground">{site?.name}</span>?
          This cannot be undone.
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

export default function SitesPage() {
  const { can } = useAuth();
  const [prefs] = usePrefs();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const sitesQ = useAsyncData(() => api.get<Site[]>("/api/v1/sites"));
  const [q, setQ] = useUrlText("q");
  const [sorting, setSorting] = useUrlSorting();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Site | null>(null);
  const [deleting, setDeleting] = useState<Site | null>(null);

  const sites = sitesQ.data ?? [];
  const refresh = () => void sitesQ.reload();

  const filtered = useMemo(() => {
    const needle = foldHebrew(q.toLowerCase());
    return sites.filter(
      (s) =>
        foldHebrew(s.name.toLowerCase()).includes(needle) ||
        foldHebrew(s.slug.toLowerCase()).includes(needle) ||
        foldHebrew((s.code ?? "").toLowerCase()).includes(needle) ||
        foldHebrew((s.size ?? "").toLowerCase()).includes(needle) ||
        foldHebrew((s.contact ?? "").toLowerCase()).includes(needle) ||
        (s.site_number?.toString() ?? "").includes(q)
    );
  }, [sites, q]);

  const columns = useMemo<ColumnDef<Site>[]>(
    () => [
      {
        accessorKey: "name",
        header: ({ column }) => <SortHeader column={column}>Name</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="font-medium">
            {c.getValue<string>()}
            {prefs.showSlugs && (
              <span className="ml-2 font-mono text-xs text-muted-foreground">
                {c.row.original.slug}
              </span>
            )}
          </span>
        ),
      },
      {
        accessorKey: "code",
        header: ({ column }) => <SortHeader column={column}>Code</SortHeader>,
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "site_number",
        header: ({ column }) => <SortHeader column={column}>#</SortHeader>,
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<number | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "size",
        header: ({ column }) => <SortHeader column={column}>Size</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "is_active",
        header: ({ column }) => (
          <SortHeader column={column}>Status</SortHeader>
        ),
        cell: (c) => (
          <Badge
            variant="outline"
            className={
              c.getValue<boolean>()
                ? "border-emerald-500/40 text-emerald-400"
                : "border-muted-foreground/40 text-muted-foreground"
            }
          >
            {c.getValue<boolean>() ? "active" : "inactive"}
          </Badge>
        ),
      },
      {
        accessorKey: "description",
        header: ({ column }) => (
          <SortHeader column={column}>Description</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
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
                aria-label={`Edit ${c.row.original.name}`}
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
                aria-label={`Delete ${c.row.original.name}`}
                onClick={() => setDeleting(c.row.original)}
              >
                <Trash2 className="h-4 w-4 text-rose-400" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [canWrite, canDelete, prefs.showSlugs]
  );

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: { sorting },
    onSortingChange: setSorting,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Sites</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New site
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search sites…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <span className="ml-auto text-sm text-muted-foreground">
          {table.getRowModel().rows.length} of {sites.length}
        </span>
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={sitesQ.loading}
          error={sitesQ.error}
          onRetry={sitesQ.reload}
          empty={sites.length === 0}
          emptyMessage="No sites yet — create the first one."
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
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
            {table.getRowModel().rows.length === 0 && sites.length > 0 && (
              <TableRow>
                <TableCell
                  colSpan={7}
                  className="py-10 text-center text-muted-foreground"
                >
                  No sites match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </AsyncPanel>
      </div>

      <SiteDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        site={editing}
        onSaved={refresh}
      />
      <DeleteDialog
        site={deleting}
        onOpenChange={() => setDeleting(null)}
        onDeleted={refresh}
      />
    </div>
  );
}
