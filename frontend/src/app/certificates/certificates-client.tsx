"use client";

import { useCallback, useEffect, useId, useMemo, useState } from "react";
import { History, Pencil, Plus, Trash2 } from "lucide-react";
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
import { cn, foldHebrew } from "@/lib/utils";
import { useUrlSorting, useUrlText } from "@/lib/url-state";
import { useRowNav } from "@/lib/row-nav";
import { useRowColor, rowTintStyle } from "@/lib/row-color";
import { useRowOrder } from "@/lib/row-order";
import {
  DragHandle,
  PinToggle,
  PinnedDivider,
  RowOrderDnd,
  SortableRow,
} from "@/components/row-order";
import { ExpiryBadge } from "@/components/expiry-badge";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { HistoryDialog } from "@/components/history-panel";
import { InlineText } from "@/components/inline-edit";
import { RowColorLegend, RowColorPicker } from "@/components/row-color";
import { SavedViews } from "@/components/saved-views";
import { SortHeader, columnAriaSort } from "@/components/sort-header";
import type { Certificate, Page } from "@/types";
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
    api.get<Page<Certificate>>("/api/v1/certificates").then((p) => p.items)
  );
  const [q, setQ] = useUrlText("q");
  // Default view is the manual order (migration backfilled it by expiry);
  // the Expires header still sorts on demand.
  const [sorting, setSorting] = useUrlSorting();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Certificate | null>(null);
  const [deleting, setDeleting] = useState<Certificate | null>(null);
  const [historyFor, setHistoryFor] = useState<Certificate | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  const items = itemsQ.data ?? [];
  const refresh = () => void itemsQ.reload();

  // Optimistic single-field patch for inline-editable cells.
  const saveField = useCallback(
    async (id: number, field: "notes", value: string | null) => {
      let prev: Certificate | undefined;
      itemsQ.setData((cur) => {
        prev = (cur ?? []).find((c) => c.id === id);
        return (cur ?? []).map((c) =>
          c.id === id ? { ...c, [field]: value } : c
        );
      });
      try {
        await api.patch(`/api/v1/certificates/${id}`, { [field]: value });
      } catch (e) {
        itemsQ.setData((cur) =>
          (cur ?? []).map((c) => (c.id === id && prev ? prev : c))
        );
        toast.error("Save failed", { description: String(e) });
        throw e;
      }
    },
    [itemsQ.setData]
  );

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

  const orderBlock = sorting.length
    ? "Row order is fixed while a column sort is on — clear the sort to drag."
    : q
      ? "Row order is fixed while searching — clear the search to drag."
      : null;
  const order = useRowOrder<Certificate>({
    path: "/api/v1/certificates",
    items,
    setData: itemsQ.setData,
    getVisibleIds: (): number[] => tableRows.map((r) => r.original.id),
    enabled: canWrite && !orderBlock,
  });
  const setRowColor = useRowColor<Certificate>({
    path: "/api/v1/certificates",
    setData: itemsQ.setData,
  });

  const columns = useMemo<ColumnDef<Certificate>[]>(
    () => [
      ...(canWrite
        ? [
            {
              id: "order",
              enableSorting: false,
              header: () => <span className="sr-only">Reorder</span>,
              cell: (c) => (
                <DragHandle
                  reason={orderBlock}
                  label={`Reorder certificate ${c.row.original.cert_name ?? c.row.original.server_name ?? c.row.original.id}`}
                />
              ),
            } satisfies ColumnDef<Certificate>,
          ]
        : []),
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
        cell: (c) => <ExpiryBadge expiresOn={c.row.original.expires_on} />,
      },
      {
        accessorKey: "notes",
        header: "Notes",
        enableSorting: false,
        cell: (c) => (
          <InlineText
            value={c.getValue<string | null>()}
            onSave={(v) => saveField(c.row.original.id, "notes", v || null)}
            disabled={!canWrite}
            dir="auto"
            label={`Edit notes for ${c.row.original.cert_name ?? c.row.original.id}`}
            className="max-w-[220px]"
          />
        ),
      },
      {
        id: "actions",
        header: () => <div className="text-right">Actions</div>,
        enableSorting: false,
        cell: (c) => (
          <div className="flex justify-end gap-1">
            {canWrite && (
              <PinToggle
                pinned={c.row.original.pinned}
                name={`certificate ${c.row.original.cert_name ?? c.row.original.server_name ?? c.row.original.id}`}
                onToggle={() =>
                  order.setPinned(c.row.original.id, !c.row.original.pinned)
                }
              />
            )}
            {canWrite && (
              <RowColorPicker
                value={c.row.original.row_color}
                displayColor={c.row.original.display_color}
                name={`certificate ${c.row.original.cert_name ?? c.row.original.server_name ?? c.row.original.id}`}
                onPick={(color) => setRowColor(c.row.original.id, color)}
              />
            )}
            <Button
              variant="ghost"
              size="icon"
              aria-label={`History of certificate ${c.row.original.cert_name ?? c.row.original.server_name ?? c.row.original.id}`}
              onClick={() => setHistoryFor(c.row.original)}
            >
              <History className="h-4 w-4" />
            </Button>
            {canWrite && (
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Edit certificate ${c.row.original.cert_name ?? c.row.original.server_name ?? c.row.original.id}`}
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
                aria-label={`Delete certificate ${c.row.original.cert_name ?? c.row.original.server_name ?? c.row.original.id}`}
                onClick={() => setDeleting(c.row.original)}
              >
                <Trash2 className="h-4 w-4 text-rose-400" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [canWrite, canDelete, saveField, order.setPinned, orderBlock, setRowColor]
  );

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: { sorting },
    onSortingChange: setSorting,
  });

  const tableRows = table.getRowModel().rows;
  const visibleIds = tableRows.map((r) => r.original.id);
  const { rowProps, focusRow } = useRowNav({
    count: tableRows.length,
    onOpen: (i) => {
      const cert = tableRows[i]?.original;
      if (!cert) return;
      if (canWrite) {
        setEditing(cert);
        setDialogOpen(true);
      } else {
        setHistoryFor(cert);
      }
    },
  });

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });
  const uid = useId();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">Certificates <DocsLink slug="certificates" /></h1>
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
          {tableRows.length} of {items.length}
        </span>
        <RowColorLegend />
        <SavedViews pageKey="certificates" />
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={itemsQ.loading}
          error={itemsQ.error}
          onRetry={itemsQ.reload}
          empty={items.length === 0}
          emptyMessage="No certificates yet — add the first one."
        >
        <RowOrderDnd ids={visibleIds} onDragEnd={order.onDragEnd}>
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
            {sorting.length === 0 && tableRows[0]?.original.pinned && (
              <PinnedDivider colSpan={columns.length} />
            )}
            {tableRows.map((row, i) => {
              const rp = rowProps(i);
              return (
                <SortableRow
                  key={row.id}
                  rowId={row.original.id}
                  dragDisabled={!order.enabled}
                  {...rp}
                  onKeyDown={(e) => {
                    const ni = order.keyDown(i, e);
                    if (ni === null) rp.onKeyDown(e);
                    else focusRow(ni);
                  }}
                  style={rowTintStyle(row.original.display_color)}
                  className={cn(
                    row.original.pinned && "bg-muted/30",
                    "focus-visible:bg-muted/50 focus-visible:outline-none"
                  )}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </SortableRow>
              );
            })}
            {tableRows.length === 0 && items.length > 0 && (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="py-10 text-center text-muted-foreground"
                >
                  No certificates match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </RowOrderDnd>
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
              <Label htmlFor={`${uid}-name`}>Certificate name</Label>
              <Input
                id={`${uid}-name`}
                dir="auto"
                value={form.cert_name}
                onChange={set("cert_name")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-platform`}>Platform</Label>
              <Input
                id={`${uid}-platform`}
                dir="auto"
                value={form.platform}
                onChange={set("platform")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-server`}>Server name</Label>
              <Input
                id={`${uid}-server`}
                dir="auto"
                value={form.server_name}
                onChange={set("server_name")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-target`}>Target / VS</Label>
              <Input
                id={`${uid}-target`}
                dir="auto"
                value={form.target}
                onChange={set("target")}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-expires`}>Expires on</Label>
                <Input
                  id={`${uid}-expires`}
                  type="date"
                  dir="ltr"
                  value={form.expires_on}
                  onChange={set("expires_on")}
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-serial`}>Serial</Label>
                <Input
                  id={`${uid}-serial`}
                  dir="ltr"
                  className="font-mono"
                  value={form.serial_raw}
                  onChange={set("serial_raw")}
                />
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-notes`}>Notes</Label>
              <Input
                id={`${uid}-notes`}
                dir="auto"
                value={form.notes}
                onChange={set("notes")}
              />
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

      <HistoryDialog
        open={historyFor !== null}
        onOpenChange={() => setHistoryFor(null)}
        objectType="Certificate"
        objectId={historyFor?.id ?? null}
        title={historyFor?.cert_name}
      />
    </div>
  );
}
