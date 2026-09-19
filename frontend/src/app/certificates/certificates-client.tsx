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
} from "@tanstack/react-table";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { foldHebrew } from "@/lib/utils";
import { useUrlSorting, useUrlText } from "@/lib/url-state";
import { expiryBadge } from "@/components/expiry-badge";
import { AsyncPanel } from "@/components/async-panel";
import { SortHeader } from "@/components/sort-header";
import type { Certificate } from "@/types";
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

const EMPTY = {
  platform: "",
  target: "",
  server_name: "",
  cert_name: "",
  expires_on: "",
  serial_raw: "",
  notes: "",
};

export default function CertificatesPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const itemsQ = useAsyncData(() =>
    api.get<Certificate[]>("/api/v1/certificates")
  );
  const [q, setQ] = useUrlText("q");
  const [sorting, setSorting] = useUrlSorting([
    { id: "expires_on", desc: false },
  ]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Certificate | null>(null);
  const [deleting, setDeleting] = useState<Certificate | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  const items = itemsQ.data ?? [];
  const refresh = () => void itemsQ.reload();

  useEffect(() => {
    if (dialogOpen) {
      setForm(
        editing
          ? {
              platform: editing.platform ?? "",
              target: editing.target ?? "",
              server_name: editing.server_name ?? "",
              cert_name: editing.cert_name ?? "",
              expires_on: editing.expires_on ?? "",
              serial_raw: editing.serial_raw ?? "",
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
          Object.entries(form).map(([k, v]) => [k, v || null])
        ),
        expires_on: form.expires_on || null,
      };
      if (editing) {
        await api.patch(`/api/v1/certificates/${editing.id}`, body);
        toast.success("Certificate updated");
      } else {
        await api.post("/api/v1/certificates", body);
        toast.success("Certificate added");
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
      await api.del(`/api/v1/certificates/${deleting.id}`);
      toast.success("Certificate deleted");
      setDeleting(null);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const filtered = useMemo(() => {
    if (!q) return items;
    const needle = foldHebrew(q.toLowerCase());
    return items.filter((c) =>
      [
        c.platform,
        c.target,
        c.server_name,
        c.cert_name,
        c.serial_raw,
        c.notes,
      ].some((f) => f != null && foldHebrew(f.toLowerCase()).includes(needle))
    );
  }, [items, q]);

  const columns = useMemo<ColumnDef<Certificate>[]>(
    () => [
      {
        accessorKey: "cert_name",
        header: ({ column }) => (
          <SortHeader column={column}>Certificate</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="font-medium">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "platform",
        header: ({ column }) => (
          <SortHeader column={column}>Platform</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        id: "server",
        accessorFn: (c) =>
          [c.server_name, c.target].filter(Boolean).join(" · "),
        header: ({ column }) => (
          <SortHeader column={column}>Server / VS</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "expires_on",
        header: ({ column }) => (
          <SortHeader column={column}>Expires</SortHeader>
        ),
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        id: "countdown",
        header: "Countdown",
        enableSorting: false,
        cell: (c) => expiryBadge(c.row.original.expires_on),
      },
      {
        accessorKey: "notes",
        header: "Notes",
        enableSorting: false,
        cell: (c) => (
          <span
            dir="auto"
            title={c.getValue<string | null>() ?? undefined}
            className="block max-w-[220px] truncate text-muted-foreground"
          >
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
    [canWrite, canDelete]
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
        <h1 className="text-xl font-semibold">Certificates</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New certificate
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search certificates…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <span className="ml-auto text-sm text-muted-foreground">
          {table.getRowModel().rows.length} of {items.length}
        </span>
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={itemsQ.loading}
          error={itemsQ.error}
          onRetry={itemsQ.reload}
          empty={items.length === 0}
          emptyMessage="No certificates yet — add the first one."
        >
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
            {table.getRowModel().rows.length === 0 && items.length > 0 && (
              <TableRow>
                <TableCell
                  colSpan={7}
                  className="py-10 text-center text-muted-foreground"
                >
                  No certificates match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </AsyncPanel>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editing ? "Edit certificate" : "New certificate"}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <div className="grid gap-1.5">
              <Label>Certificate name</Label>
              <Input dir="auto" value={form.cert_name} onChange={set("cert_name")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Platform</Label>
              <Input dir="auto" value={form.platform} onChange={set("platform")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Server name</Label>
              <Input
                dir="auto"
                value={form.server_name}
                onChange={set("server_name")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Target / VS</Label>
              <Input dir="auto" value={form.target} onChange={set("target")} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label>Expires on</Label>
                <Input
                  type="date"
                  dir="ltr"
                  value={form.expires_on}
                  onChange={set("expires_on")}
                />
              </div>
              <div className="grid gap-1.5">
                <Label>Serial</Label>
                <Input
                  dir="ltr"
                  className="font-mono"
                  value={form.serial_raw}
                  onChange={set("serial_raw")}
                />
              </div>
            </div>
            <div className="grid gap-1.5">
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
            <DialogTitle>Delete certificate</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.cert_name}
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
