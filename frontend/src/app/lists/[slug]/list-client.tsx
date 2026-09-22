"use client";

import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Download,
  ExternalLink,
  GripVertical,
  History,
  Loader2,
  Pencil,
  Pin,
  PinOff,
  Plus,
  Settings2,
  Trash2,
  User,
  X,
} from "lucide-react";
import { toast } from "sonner";
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
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
import { cn, foldHebrew, timeAgo } from "@/lib/utils";
import { useUrlSorting, useUrlText } from "@/lib/url-state";
import { useRowNav } from "@/lib/row-nav";
import { useRowColor, rowTintStyle } from "@/lib/row-color";
import { useRowOrder } from "@/lib/row-order";
import { STATUS_TOKENS } from "@/lib/status-tokens";
import {
  DragHandle,
  PinToggle,
  PinnedDivider,
  RowOrderDnd,
  SortableRow,
} from "@/components/row-order";
import { SortHeader, columnAriaSort } from "@/components/sort-header";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { ExpiryBadge } from "@/components/expiry-badge";
import { HistoryDialog } from "@/components/history-panel";
import { InlineText } from "@/components/inline-edit";
import { IpDrawer } from "@/components/ip-drawer";
import { RowColorLegend, RowColorPicker } from "@/components/row-color";
import { SavedViews } from "@/components/saved-views";
import type {
  CustomList,
  CustomListRow,
  IpAddress,
  IpStatus,
  ListColumn,
  ListRowsPage,
  Page,
  ResolvedIp,
} from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
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

const COL_TYPES = ["text", "ip", "date", "select", "number", "url", "owner"] as const;
const IP_SPLIT = /[,\s;/]+/;

/** Stable chip color per select option — hash into a small palette. */
const CHIP_COLORS = [
  "border-sky-500/40 text-sky-400",
  "border-violet-500/40 text-violet-400",
  "border-emerald-500/40 text-emerald-400",
  "border-amber-500/40 text-amber-400",
  "border-rose-500/40 text-rose-400",
  "border-cyan-500/40 text-cyan-400",
  "border-fuchsia-500/40 text-fuchsia-400",
  "border-lime-500/40 text-lime-400",
];

function chipColor(v: string): string {
  let h = 0;
  for (let i = 0; i < v.length; i++) h = (h * 31 + v.charCodeAt(i)) | 0;
  return CHIP_COLORS[Math.abs(h) % CHIP_COLORS.length];
}

function cellLabel(row: CustomListRow, cols: ListColumn[]): string {
  const data = row.data ?? {};
  for (const c of cols) {
    const v = data[c.key];
    if (v) return v;
  }
  return `#${row.id}`;
}

function IpCell({
  value,
  resolved,
  onOpen,
}: {
  value: string;
  resolved: Record<string, ResolvedIp>;
  onOpen: (ip: string, r: ResolvedIp) => void;
}) {
  const tokens = value.split(IP_SPLIT).filter(Boolean);
  return (
    <span dir="ltr" className="inline-flex flex-wrap items-center gap-x-2 gap-y-0.5 font-mono text-xs">
      {tokens.map((tok) => {
        const r = resolved[tok];
        if (!r) {
          // not in ip_addresses — the list claims an IP the IPAM doesn't know
          return (
            <span
              key={tok}
              title="Not in the address table"
              className="text-muted-foreground underline decoration-dashed decoration-muted-foreground/50 underline-offset-2"
            >
              {tok}
            </span>
          );
        }
        return (
          <button
            key={tok}
            type="button"
            onClick={() => onOpen(tok, r)}
            title={r.hostname ?? r.status}
            className="inline-flex items-center gap-1 hover:underline"
          >
            <span
              className={cn(
                "inline-block h-1.5 w-1.5 rounded-full",
                STATUS_TOKENS[r.status as IpStatus]?.dot ?? "bg-zinc-500/70"
              )}
            />
            {tok}
          </button>
        );
      })}
    </span>
  );
}

/** IP cell with edit affordance: the chips/dots are the display (click →
 *  IP drawer); the pencil opens a text input so the raw value stays
 *  editable without duplicating it next to the chips. Same Enter/blur
 *  commit, Esc cancel semantics as InlineText. */
function IpEditCell({
  value,
  resolved,
  onOpen,
  onSave,
  canWrite,
  label,
}: {
  value: string;
  resolved: Record<string, ResolvedIp>;
  onOpen: (ip: string, r: ResolvedIp) => void;
  onSave: (v: string) => Promise<void>;
  canWrite: boolean;
  label: string;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);

  const commit = async () => {
    const v = draft.trim();
    if (v === value) {
      setEditing(false);
      return;
    }
    setBusy(true);
    try {
      await onSave(v);
      setEditing(false);
    } catch {
      /* parent rolled back + toasted; keep editing */
    } finally {
      setBusy(false);
    }
  };

  if (!canWrite) {
    return value ? (
      <IpCell value={value} resolved={resolved} onOpen={onOpen} />
    ) : (
      <span className="text-muted-foreground">—</span>
    );
  }

  if (!editing) {
    return (
      <span className="group inline-flex items-center gap-1">
        {value ? (
          <IpCell value={value} resolved={resolved} onOpen={onOpen} />
        ) : (
          <span className="text-muted-foreground">—</span>
        )}
        <button
          type="button"
          aria-label={label}
          title="Click to edit"
          onClick={() => {
            setDraft(value);
            setEditing(true);
          }}
          className="rounded p-0.5 text-muted-foreground/50 hover:bg-muted/60 hover:text-foreground focus-visible:bg-muted/60 focus-visible:outline-none"
        >
          <Pencil className="h-3 w-3" />
        </button>
      </span>
    );
  }

  return (
    <span className="relative block">
      <Input
        autoFocus
        dir="ltr"
        aria-label={label}
        value={draft}
        disabled={busy}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={() => void commit()}
        onFocus={(e) => e.target.select()}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            void commit();
          } else if (e.key === "Escape") {
            e.preventDefault();
            e.stopPropagation();
            setEditing(false);
          }
        }}
        className="h-7 px-1.5 font-mono text-xs"
      />
      {busy && (
        <Loader2 className="absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 animate-spin text-muted-foreground" />
      )}
    </span>
  );
}

/** Sortable wrapper for the settings-dialog column editor — the drag
 *  listeners live on the grip only so the label/type inputs stay usable. */
function SortableColRow({
  id,
  label,
  children,
}: {
  id: string;
  label: string;
  children: ReactNode;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id });
  return (
    <div
      ref={setNodeRef}
      style={{
        transform: transform
          ? `translate3d(${transform.x}px, ${transform.y}px, 0)`
          : undefined,
        transition,
      }}
      className={cn(
        "flex items-center gap-2",
        isDragging && "relative z-10 rounded-md bg-muted"
      )}
    >
      <button
        type="button"
        aria-label={`Drag to reorder column ${label}`}
        className="cursor-grab touch-none text-muted-foreground active:cursor-grabbing"
        {...attributes}
        {...listeners}
      >
        <GripVertical className="h-4 w-4" />
      </button>
      {children}
    </div>
  );
}

export default function ListClient({ slug }: { slug: string }) {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const uid = useId();

  const listQ = useAsyncData(async () => {
    const p = await api.get<Page<CustomList>>("/api/v1/lists");
    const found = p.items.find((l) => l.slug === slug);
    if (!found) throw new Error("List not found");
    return found;
  }, [slug]);
  const list = listQ.data ?? null;
  const listId = list?.id ?? 0;
  const cols = useMemo(() => list?.columns ?? [], [list]);

  const rowsQ = useAsyncData(
    () =>
      listId
        ? api.get<ListRowsPage>(`/api/v1/lists/${listId}/rows`)
        : Promise.resolve(null),
    [listId]
  );
  const page = rowsQ.data;
  const rows = useMemo(() => page?.items ?? [], [page]);
  const resolved = useMemo(() => page?.resolved ?? {}, [page]);

  /** setData adapter: row-order/color hooks own CustomListRow[], the query
   *  owns the whole page envelope (items + resolved). */
  const setRows: Dispatch<SetStateAction<CustomListRow[] | null>> = useCallback(
    (v) =>
      rowsQ.setData((cur) =>
        cur
          ? {
              ...cur,
              items:
                (typeof v === "function"
                  ? (v as (c: CustomListRow[]) => CustomListRow[])(cur.items)
                  : v) ?? [],
            }
          : cur
      ),
    [rowsQ.setData]
  );

  const [q, setQ] = useUrlText("q");
  const [sorting, setSorting] = useUrlSorting();
  const [newRowOpen, setNewRowOpen] = useState(false);
  const [newRow, setNewRow] = useState<Record<string, string>>({});
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [deleting, setDeleting] = useState<CustomListRow | null>(null);
  const [historyFor, setHistoryFor] = useState<CustomListRow | null>(null);
  const [listHistoryOpen, setListHistoryOpen] = useState(false);
  const [drawer, setDrawer] = useState<{
    ip: string;
    addr: IpAddress;
  } | null>(null);
  const [busy, setBusy] = useState(false);
  const [selected, setSelected] = useState<Set<number>>(new Set());

  // drop ids that left the list (deleted rows, reloads)
  useEffect(() => {
    setSelected((s) => {
      const ids = new Set(rows.map((r) => r.id));
      const pruned = new Set([...s].filter((id) => ids.has(id)));
      return pruned.size === s.size ? s : pruned;
    });
  }, [rows]);

  const colSensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const onColDragEnd = (e: DragEndEvent) => {
    const { active, over } = e;
    if (!over || active.id === over.id) return;
    setSForm((f) => {
      const from = f.columns.findIndex((c) => c.key === String(active.id));
      const to = f.columns.findIndex((c) => c.key === String(over.id));
      if (from < 0 || to < 0) return f;
      return { ...f, columns: arrayMove(f.columns, from, to) };
    });
  };

  const toggleRow = (id: number, on: boolean) =>
    setSelected((s) => {
      const n = new Set(s);
      if (on) n.add(id);
      else n.delete(id);
      return n;
    });

  const bulk = async (action: string, row_color: string | null = null) => {
    if (!list || selected.size === 0) return;
    setBusy(true);
    try {
      const r = await api.post<{ affected: number; not_found: number[] }>(
        `/api/v1/lists/${list.id}/rows/bulk`,
        { ids: [...selected], action, row_color }
      );
      toast.success(`${r.affected} row(s) ${action.replace("_", " ")}d`);
      setSelected(new Set());
      void rowsQ.reload();
    } catch (e) {
      toast.error("Bulk action failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  // -- settings dialog state ------------------------------------------------
  const [sForm, setSForm] = useState<{
    name: string;
    description: string;
    key_column: string;
    columns: ListColumn[];
  }>({ name: "", description: "", key_column: "", columns: [] });

  const openSettings = () => {
    if (!list) return;
    setSForm({
      name: list.name,
      description: list.description ?? "",
      key_column: list.key_column ?? "",
      columns: (list.columns ?? []).map((c) => ({ ...c })),
    });
    setSettingsOpen(true);
  };

  const saveSettings = async () => {
    if (!list) return;
    setBusy(true);
    try {
      await api.patch(`/api/v1/lists/${list.id}`, {
        name: sForm.name,
        description: sForm.description || null,
        key_column: sForm.key_column || null,
        columns: sForm.columns.map((c, i) => ({
          ...c,
          label: c.label || `Column ${i + 1}`,
        })),
      });
      toast.success("List updated");
      setSettingsOpen(false);
      void listQ.reload();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  // -- cell save --------------------------------------------------------------
  const saveCell = useCallback(
    async (rowId: number, colKey: string, value: string) => {
      const stored = value === "" ? null : value;
      let prev: CustomListRow | undefined;
      setRows((cur) => {
        prev = (cur ?? []).find((r) => r.id === rowId);
        return (cur ?? []).map((r) => {
          if (r.id !== rowId) return r;
          const data = { ...(r.data ?? {}) };
          if (stored === null) delete data[colKey];
          else data[colKey] = stored;
          return { ...r, data, manually_edited: true };
        });
      });
      try {
        await api.patch(`/api/v1/lists/${listId}/rows/${rowId}`, {
          data: { [colKey]: stored },
        });
      } catch (e) {
        setRows((cur) =>
          (cur ?? []).map((r) => (r.id === rowId && prev ? prev : r))
        );
        toast.error("Save failed", { description: String(e) });
        throw e;
      }
    },
    [listId, setRows]
  );

  const openIp = useCallback(
    async (ip: string, r: ResolvedIp) => {
      try {
        const addr = await api.get<IpAddress>(`/api/v1/addresses/${r.id}`);
        setDrawer({ ip, addr });
      } catch (e) {
        toast.error("Could not load address", { description: String(e) });
      }
    },
    []
  );

  const addRow = async () => {
    if (!list) return;
    setBusy(true);
    try {
      const data = Object.fromEntries(
        Object.entries(newRow).filter(([, v]) => v.trim() !== "")
      );
      await api.post(`/api/v1/lists/${list.id}/rows`, { data });
      toast.success("Row added");
      setNewRowOpen(false);
      setNewRow({});
      void rowsQ.reload();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doDelete = async () => {
    if (!deleting) return;
    try {
      await api.del(`/api/v1/lists/${listId}/rows/${deleting.id}`);
      toast.success("Row deleted");
      setDeleting(null);
      void rowsQ.reload();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  // -- filtering ---------------------------------------------------------------
  const filtered = useMemo(() => {
    if (!q) return rows;
    const needle = foldHebrew(q.toLowerCase());
    return rows.filter((r) =>
      Object.values(r.data ?? {}).some(
        (v) => v != null && foldHebrew(String(v).toLowerCase()).includes(needle)
      )
    );
  }, [rows, q]);

  const exportCsv = () => {
    const esc = (v: string) => `"${v.replace(/"/g, '""')}"`;
    const head = cols.map((c) => esc(c.label)).join(",");
    const body = filtered
      .map((r) =>
        cols.map((c) => esc(r.data?.[c.key] ?? "")).join(",")
      )
      .join("\n");
    const blob = new Blob(["﻿" + head + "\n" + body], {
      type: "text/csv;charset=utf-8",
    });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${slug}.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const orderBlock = sorting.length
    ? "Row order is fixed while a column sort is on — clear the sort to drag."
    : q
      ? "Row order is fixed while searching — clear the search to drag."
      : null;
  const rowsPath = `/api/v1/lists/${listId}/rows`;
  const order = useRowOrder<CustomListRow>({
    path: rowsPath,
    items: rows,
    setData: setRows,
    getVisibleIds: (): number[] => tableRows.map((r) => r.original.id),
    enabled: canWrite && !orderBlock && !!list,
  });
  const setRowColor = useRowColor<CustomListRow>({
    path: rowsPath,
    setData: setRows,
  });

  // -- dynamic columns ----------------------------------------------------------
  const columns = useMemo<ColumnDef<CustomListRow>[]>(() => {
    const out: ColumnDef<CustomListRow>[] = [];
    if (canWrite) {
      out.push({
        id: "select",
        enableSorting: false,
        header: () => {
          const all =
            filtered.length > 0 &&
            filtered.every((r) => selected.has(r.id));
          return (
            <Checkbox
              checked={all}
              aria-label="Select all rows"
              onCheckedChange={(v) =>
                setSelected((s) => {
                  const n = new Set(s);
                  for (const r of filtered)
                    if (v === true) n.add(r.id);
                    else n.delete(r.id);
                  return n;
                })
              }
            />
          );
        },
        cell: (c) => (
          <Checkbox
            checked={selected.has(c.row.original.id)}
            aria-label={`Select row ${cellLabel(c.row.original, cols)}`}
            onCheckedChange={(v) =>
              toggleRow(c.row.original.id, v === true)
            }
          />
        ),
      });
      out.push({
        id: "order",
        enableSorting: false,
        header: () => <span className="sr-only">Reorder</span>,
        cell: (c) => (
          <DragHandle
            reason={orderBlock}
            label={`Reorder row ${cellLabel(c.row.original, cols)}`}
          />
        ),
      });
    }
    for (const col of cols) {
      const label = col.label;
      out.push({
        id: col.key,
        accessorFn: (r) => r.data?.[col.key] ?? "",
        sortingFn:
          col.type === "number"
            ? (a, b) =>
                (parseFloat(a.original.data?.[col.key] ?? "NaN") || 0) -
                (parseFloat(b.original.data?.[col.key] ?? "NaN") || 0)
            : "alphanumeric",
        header: ({ column }) => (
          <SortHeader column={column}>
            <span dir="auto">{label}</span>
          </SortHeader>
        ),
        cell: (c) => {
          const v = c.getValue<string>();
          const row = c.row.original;
          const edit = { disabled: !canWrite, label: `Edit ${label}` };
          if (!v && !canWrite)
            return <span className="text-muted-foreground">—</span>;
          switch (col.type) {
            case "ip":
              return (
                <IpEditCell
                  value={v}
                  resolved={resolved}
                  onOpen={openIp}
                  onSave={(nv) => saveCell(row.id, col.key, nv)}
                  canWrite={canWrite}
                  label={edit.label}
                />
              );
            case "date":
              return canWrite ? (
                <InlineText
                  value={v || null}
                  onSave={(nv) => saveCell(row.id, col.key, nv)}
                  dir="ltr"
                  label={`Edit ${label} (YYYY-MM-DD)`}
                />
              ) : (
                <span dir="ltr" className="inline-flex items-center gap-2">
                  <span className="text-muted-foreground">{v}</span>
                  <ExpiryBadge expiresOn={v || null} />
                </span>
              );
            case "select": {
              // keep the current value selectable even if the sheet's
              // option list is stale (a new value appeared in the data)
              const opts = [...(col.options ?? [])];
              if (v && !opts.includes(v)) opts.push(v);
              if (!canWrite) {
                return v ? (
                  <Badge variant="outline" className={chipColor(v)}>
                    {v}
                  </Badge>
                ) : (
                  <span className="text-muted-foreground">—</span>
                );
              }
              return (
                <Select
                  value={v || "__none__"}
                  onValueChange={(nv) =>
                    void saveCell(row.id, col.key, nv === "__none__" ? "" : nv)
                  }
                >
                  <SelectTrigger
                    aria-label={`Edit ${label}`}
                    title="Click to edit"
                    className="h-auto w-auto gap-1.5 border-0 bg-transparent p-0 shadow-none hover:bg-transparent focus:ring-1 focus:ring-offset-0 [&>svg]:h-3 [&>svg]:w-3"
                  >
                    {v ? (
                      <Badge variant="outline" className={chipColor(v)}>
                        {v}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__none__">
                      <span className="text-muted-foreground">—</span>
                    </SelectItem>
                    {opts.map((o) => (
                      <SelectItem key={o} value={o}>
                        <span dir="auto">{o}</span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              );
            }
            case "url":
              return (
                <span className="inline-flex items-center gap-1.5">
                  {v ? (
                    <a
                      href={v}
                      target="_blank"
                      rel="noreferrer"
                      aria-label={`Open ${v}`}
                      className="text-sky-400 hover:text-sky-300"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  ) : null}
                  <InlineText
                    value={v || null}
                    onSave={(nv) => saveCell(row.id, col.key, nv)}
                    dir="ltr"
                    empty=""
                    {...edit}
                  />
                </span>
              );
            case "owner":
              return canWrite ? (
                <InlineText
                  value={v || null}
                  onSave={(nv) => saveCell(row.id, col.key, nv)}
                  dir="auto"
                  {...edit}
                />
              ) : (
                <span dir="auto" className="inline-flex items-center gap-1">
                  <User className="h-3 w-3 text-muted-foreground" />
                  {v}
                </span>
              );
            case "number":
              return (
                <InlineText
                  value={v || null}
                  onSave={(nv) => saveCell(row.id, col.key, nv)}
                  dir="ltr"
                  className="font-mono"
                  {...edit}
                />
              );
            default:
              return (
                <InlineText
                  value={v || null}
                  onSave={(nv) => saveCell(row.id, col.key, nv)}
                  dir="auto"
                  {...edit}
                />
              );
          }
        },
      });
    }
    out.push({
      id: "actions",
      header: () => <div className="text-right">Actions</div>,
      enableSorting: false,
      cell: (c) => {
        const lbl = cellLabel(c.row.original, cols);
        return (
          <div className="flex justify-end gap-1">
            {c.row.original.manually_edited && (
              <span
                title="Edited in-app — a re-import won't overwrite this row"
                className="mr-1 inline-flex items-center text-[10px] text-muted-foreground"
              >
                edited
              </span>
            )}
            {canWrite && (
              <PinToggle
                pinned={c.row.original.pinned}
                name={`row ${lbl}`}
                onToggle={() =>
                  order.setPinned(c.row.original.id, !c.row.original.pinned)
                }
              />
            )}
            {canWrite && (
              <RowColorPicker
                value={c.row.original.row_color}
                displayColor={c.row.original.display_color}
                name={`row ${lbl}`}
                onPick={(color) => setRowColor(c.row.original.id, color)}
              />
            )}
            <Button
              variant="ghost"
              size="icon"
              aria-label={`History of row ${lbl}`}
              onClick={() => setHistoryFor(c.row.original)}
            >
              <History className="h-4 w-4" />
            </Button>
            {canDelete && (
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Delete row ${lbl}`}
                onClick={() => setDeleting(c.row.original)}
              >
                <Trash2 className="h-4 w-4 text-rose-400" />
              </Button>
            )}
          </div>
        );
      },
    });
    return out;
    // eslint-disable-next-line react-hooks/exhaustive-deps -- toggleRow is stable
  }, [canWrite, canDelete, cols, resolved, orderBlock, order.setPinned, saveCell, openIp, setRowColor, filtered, selected]);

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
    onOpen: () => {},
  });

  const moveCol = (i: number, d: -1 | 1) =>
    setSForm((f) => {
      const cols2 = [...f.columns];
      const j = i + d;
      if (j < 0 || j >= cols2.length) return f;
      [cols2[i], cols2[j]] = [cols2[j], cols2[i]];
      return { ...f, columns: cols2 };
    });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">
          <Link
            href="/lists"
            className="text-muted-foreground hover:text-foreground"
            aria-label="Back to lists"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <span dir="auto">{list?.name ?? "…"}</span>
          <DocsLink slug="lists" />
          {list?.source_sheet && (
            <Badge variant="outline" dir="auto" className="text-muted-foreground">
              from sheet “{list.source_sheet}”
            </Badge>
          )}
        </h1>
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setListHistoryOpen(true)}
            disabled={!list}
          >
            <History /> History
          </Button>
          {canWrite && (
            <Button
              size="sm"
              variant="outline"
              onClick={openSettings}
              disabled={!list}
            >
              <Settings2 /> Settings
            </Button>
          )}
          {canWrite && (
            <Button
              size="sm"
              disabled={!list}
              onClick={() => {
                setNewRow({});
                setNewRowOpen(true);
              }}
            >
              <Plus /> New row
            </Button>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder={`Search ${list?.name ?? "list"}…`}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Button variant="ghost" size="sm" onClick={exportCsv} title="Export filtered rows as CSV">
          <Download className="h-4 w-4" /> CSV
        </Button>
        <span className="ml-auto text-sm text-muted-foreground">
          {tableRows.length} of {rows.length}
        </span>
        <RowColorLegend />
        <SavedViews pageKey={`list:${slug}`} />
      </div>

      {selected.size > 0 && (
        <div className="flex flex-wrap items-center gap-2 rounded-lg border bg-muted/40 px-3 py-2 text-sm">
          <span className="font-medium">{selected.size} selected</span>
          <Button
            size="sm"
            variant="ghost"
            disabled={busy}
            onClick={() => void bulk("pin")}
          >
            <Pin className="h-4 w-4" /> Pin
          </Button>
          <Button
            size="sm"
            variant="ghost"
            disabled={busy}
            onClick={() => void bulk("unpin")}
          >
            <PinOff className="h-4 w-4" /> Unpin
          </Button>
          <RowColorPicker
            value={null}
            displayColor={null}
            name={`${selected.size} selected rows`}
            onPick={(color) =>
              void bulk(color === null ? "clear_color" : "set_color", color)
            }
          />
          {canDelete && (
            <Button
              size="sm"
              variant="ghost"
              disabled={busy}
              onClick={() => void bulk("delete")}
              className="text-rose-400"
            >
              <Trash2 className="h-4 w-4" /> Delete
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            className="ml-auto"
            onClick={() => setSelected(new Set())}
          >
            <X className="h-4 w-4" /> Clear
          </Button>
        </div>
      )}

      <div className="rounded-lg border">
        <AsyncPanel
          loading={listQ.loading || rowsQ.loading}
          error={listQ.error ?? rowsQ.error}
          onRetry={() => {
            void listQ.reload();
            void rowsQ.reload();
          }}
          empty={rows.length === 0}
          emptyMessage="No rows yet — add one, or re-import the source sheet."
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
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </TableCell>
                      ))}
                    </SortableRow>
                  );
                })}
                {tableRows.length === 0 && rows.length > 0 && (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length}
                      className="py-10 text-center text-muted-foreground"
                    >
                      No rows match this filter.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </RowOrderDnd>
        </AsyncPanel>
      </div>

      {/* new row */}
      <Dialog open={newRowOpen} onOpenChange={setNewRowOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>New row — {list?.name}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            {cols.map((c) => (
              <div key={c.key} className="grid gap-1.5">
                <Label htmlFor={`${uid}-${c.key}`} dir="auto">
                  {c.label}
                </Label>
                {c.type === "select" && (c.options?.length ?? 0) > 0 ? (
                  <Select
                    value={newRow[c.key] ?? ""}
                    onValueChange={(v) =>
                      setNewRow({ ...newRow, [c.key]: v })
                    }
                  >
                    <SelectTrigger id={`${uid}-${c.key}`}>
                      <SelectValue placeholder="—" />
                    </SelectTrigger>
                    <SelectContent>
                      {(c.options ?? []).map((o) => (
                        <SelectItem key={o} value={o}>
                          <span dir="auto">{o}</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    id={`${uid}-${c.key}`}
                    dir={c.type === "ip" || c.type === "number" || c.type === "url" || c.type === "date" ? "ltr" : "auto"}
                    value={newRow[c.key] ?? ""}
                    onChange={(e) =>
                      setNewRow({ ...newRow, [c.key]: e.target.value })
                    }
                    placeholder={c.type === "date" ? "YYYY-MM-DD" : undefined}
                  />
                )}
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button onClick={addRow} disabled={busy}>
              {busy ? "Saving…" : "Add row"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* list settings */}
      <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>List settings</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-lname`}>Name</Label>
                <Input
                  id={`${uid}-lname`}
                  dir="auto"
                  value={sForm.name}
                  onChange={(e) =>
                    setSForm({ ...sForm, name: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-kcol`}>Merge key column</Label>
                <Select
                  value={sForm.key_column || "__none__"}
                  onValueChange={(v) =>
                    setSForm({ ...sForm, key_column: v === "__none__" ? "" : v })
                  }
                >
                  <SelectTrigger id={`${uid}-kcol`}>
                    <SelectValue placeholder="None" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__none__">
                      <span className="text-muted-foreground">None</span>
                    </SelectItem>
                    {sForm.columns.map((c) => (
                      <SelectItem key={c.key} value={c.key}>
                        <span dir="auto">{c.label}</span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Re-imports match existing rows by this column.
                </p>
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-ldesc`}>Description</Label>
              <Input
                id={`${uid}-ldesc`}
                dir="auto"
                value={sForm.description}
                onChange={(e) =>
                  setSForm({ ...sForm, description: e.target.value })
                }
              />
            </div>
            <div className="grid gap-2">
              <Label>Columns</Label>
              <DndContext
                sensors={colSensors}
                collisionDetection={closestCenter}
                onDragEnd={onColDragEnd}
              >
                <SortableContext
                  items={sForm.columns.map((c) => c.key)}
                  strategy={verticalListSortingStrategy}
                >
                  {sForm.columns.map((c, i) => (
                    <SortableColRow key={c.key} id={c.key} label={c.label}>
                  <Input
                    dir="auto"
                    value={c.label}
                    aria-label={`Column ${i + 1} label`}
                    onChange={(e) =>
                      setSForm((f) => ({
                        ...f,
                        columns: f.columns.map((x, j) =>
                          j === i ? { ...x, label: e.target.value } : x
                        ),
                      }))
                    }
                  />
                  <Select
                    value={c.type}
                    onValueChange={(v) =>
                      setSForm((f) => ({
                        ...f,
                        columns: f.columns.map((x, j) =>
                          j === i
                            ? { ...x, type: v as ListColumn["type"] }
                            : x
                        ),
                      }))
                    }
                  >
                    <SelectTrigger
                      className="w-28"
                      aria-label={`Column ${i + 1} type`}
                    >
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {COL_TYPES.map((t) => (
                        <SelectItem key={t} value={t}>
                          {t}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Move column ${c.label} up`}
                    onClick={() => moveCol(i, -1)}
                    disabled={i === 0}
                  >
                    ↑
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Move column ${c.label} down`}
                    onClick={() => moveCol(i, 1)}
                    disabled={i === sForm.columns.length - 1}
                  >
                    ↓
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Remove column ${c.label}`}
                    title="Hides the column — cell data is kept"
                    onClick={() =>
                      setSForm((f) => ({
                        ...f,
                        columns: f.columns.filter((_, j) => j !== i),
                        key_column:
                          f.key_column === c.key ? "" : f.key_column,
                      }))
                    }
                  >
                    <Trash2 className="h-4 w-4 text-rose-400" />
                  </Button>
                    </SortableColRow>
                  ))}
                </SortableContext>
              </DndContext>
              <Button
                variant="outline"
                size="sm"
                className="w-fit"
                onClick={() =>
                  setSForm((f) => {
                    let n = f.columns.length;
                    const keys = new Set(f.columns.map((c) => c.key));
                    while (keys.has(`c${n}`)) n++;
                    return {
                      ...f,
                      columns: [
                        ...f.columns,
                        {
                          key: `c${n}`,
                          label: `Column ${f.columns.length + 1}`,
                          type: "text",
                        },
                      ],
                    };
                  })
                }
              >
                <Plus className="h-4 w-4" /> Add column
              </Button>
            </div>
          </div>
          <DialogFooter>
            <Button onClick={saveSettings} disabled={busy || !sForm.name.trim()}>
              {busy ? "Saving…" : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* delete row */}
      <Dialog open={deleting !== null} onOpenChange={() => setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete row</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete row{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting ? cellLabel(deleting, cols) : ""}
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
        objectType="CustomListRow"
        objectId={historyFor?.id ?? null}
        title={historyFor ? cellLabel(historyFor, cols) : undefined}
      />

      <HistoryDialog
        open={listHistoryOpen}
        onOpenChange={setListHistoryOpen}
        objectType="CustomList"
        objectId={list?.id ?? null}
        title={list?.name}
      />

      {drawer && (
        <IpDrawer
          open
          onOpenChange={(o) => !o && setDrawer(null)}
          ip={drawer.ip}
          addr={drawer.addr}
          prefixId={drawer.addr.prefix_id}
          onSaved={() => void rowsQ.reload()}
        />
      )}
    </div>
  );
}
