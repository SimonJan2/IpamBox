"use client";

import { useEffect, useId, useMemo, useState } from "react";
import Link from "next/link";
import { Boxes, History, ListFilter, Pencil, Plus, Trash2, X } from "lucide-react";
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
import { formatKg, formatWatts } from "@/lib/rack-capacity";
import { useUrlParam, useUrlSorting, useUrlText } from "@/lib/url-state";
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
import { SortHeader, columnAriaSort } from "@/components/sort-header";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { HistoryDialog } from "@/components/history-panel";
import { RowColorLegend, RowColorPicker } from "@/components/row-color";
import type { Page, Rack, RackGroup, Site } from "@/types";
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
  name: "",
  site_id: "none",
  group_id: "none",
  group_position: "",
  room: "",
  height_u: "42",
  width: "19",
  description: "",
  notes: "",
};

type RackRow = Rack & { site_name: string };

function GroupDialog({
  open,
  onOpenChange,
  group,
  sites,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  group: RackGroup | null;
  sites: Site[];
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: "",
    site_id: "none",
    description: "",
  });
  const [busy, setBusy] = useState(false);
  const uid = useId();

  useEffect(() => {
    if (open) {
      setForm({
        name: group?.name ?? "",
        site_id: group?.site_id ? String(group.site_id) : "none",
        description: group?.description ?? "",
      });
    }
  }, [open, group]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        name: form.name,
        site_id: form.site_id === "none" ? null : Number(form.site_id),
        description: form.description || null,
      };
      if (group) {
        await api.patch(`/api/v1/rack-groups/${group.id}`, body);
        toast.success("Group updated");
      } else {
        await api.post("/api/v1/rack-groups", body);
        toast.success("Group created");
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
          <DialogTitle>{group ? "Edit group" : "New group"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-gname`}>Name</Label>
            <Input
              id={`${uid}-gname`}
              dir="auto"
              placeholder="e.g. Row A, Cage 4…"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-gsite`}>Site</Label>
            <Select
              value={form.site_id}
              onValueChange={(v) => setForm({ ...form, site_id: v })}
            >
              <SelectTrigger id={`${uid}-gsite`}>
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
            <Label htmlFor={`${uid}-gdesc`}>Description</Label>
            <Input
              id={`${uid}-gdesc`}
              dir="auto"
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !form.name.trim()}>
            {busy ? "Saving…" : group ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function RacksPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [filterGroup, setFilterGroupRaw] = useUrlParam("group");
  const setFilterGroup = (id: number | null) =>
    setFilterGroupRaw(id === null ? "" : String(id));
  const itemsQ = useAsyncData(
    () =>
      api.get<Page<Rack>>(
        `/api/v1/racks${filterGroup ? `?group_id=${filterGroup}` : ""}`
      ).then((p) => p.items),
    [filterGroup]
  );
  const groupsQ = useAsyncData(async () => {
    try {
      return await api.get<RackGroup[]>("/api/v1/rack-groups");
    } catch {
      return [];
    }
  });
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Site>>("/api/v1/sites").then((p) => p.items);
    } catch {
      return [];
    }
  });
  const [q, setQ] = useUrlText("q");
  const [sorting, setSorting] = useUrlSorting();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Rack | null>(null);
  const [deleting, setDeleting] = useState<Rack | null>(null);
  const [groupDialogOpen, setGroupDialogOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState<RackGroup | null>(null);
  const [historyFor, setHistoryFor] = useState<{
    type: "Rack" | "RackGroup";
    id: number;
    title: string;
  } | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  const items = itemsQ.data ?? [];
  const groups = groupsQ.data ?? [];
  const sites = sitesQ.data ?? [];
  const refresh = () => {
    void itemsQ.reload();
    void groupsQ.reload();
  };

  useEffect(() => {
    if (dialogOpen) {
      setForm(
        editing
          ? {
              name: editing.name,
              site_id: editing.site_id ? String(editing.site_id) : "none",
              group_id: editing.group_id ? String(editing.group_id) : "none",
              group_position:
                editing.group_position != null
                  ? String(editing.group_position)
                  : "",
              room: editing.room ?? "",
              height_u: String(editing.height_u),
              width: String(editing.width),
              description: editing.description ?? "",
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
        name: form.name,
        site_id: form.site_id === "none" ? null : Number(form.site_id),
        group_id: form.group_id === "none" ? null : Number(form.group_id),
        group_position:
          form.group_id !== "none" && form.group_position !== ""
            ? Number(form.group_position)
            : null,
        room: form.room || null,
        height_u: Number(form.height_u),
        width: Number(form.width),
        description: form.description || null,
        notes: form.notes || null,
      };
      if (editing) {
        await api.patch(`/api/v1/racks/${editing.id}`, body);
        toast.success("Rack updated");
      } else {
        await api.post("/api/v1/racks", body);
        toast.success("Rack added");
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
      await api.del(`/api/v1/racks/${deleting.id}`);
      toast.success("Rack deleted");
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

  const rows = useMemo<RackRow[]>(
    () =>
      items.map((r) => ({
        ...r,
        site_name: r.site_id ? (siteName[r.site_id] ?? "") : "",
      })),
    [items, siteName]
  );

  const filtered = useMemo(() => {
    const needle = foldHebrew(q.toLowerCase());
    if (!needle) return rows;
    return rows.filter((r) =>
      [r.name, r.room, r.description, r.site_name].some(
        (f) => f != null && foldHebrew(f.toLowerCase()).includes(needle)
      )
    );
  }, [rows, q]);

  const orderBlock = sorting.length
    ? "Row order is fixed while a column sort is on — clear the sort to drag."
    : q
      ? "Row order is fixed while searching — clear the search to drag."
      : null;
  const order = useRowOrder<Rack>({
    path: "/api/v1/racks",
    items,
    setData: itemsQ.setData,
    getVisibleIds: (): number[] => tableRows.map((r) => r.original.id),
    enabled: canWrite && !orderBlock,
  });
  const setRowColor = useRowColor<Rack>({
    path: "/api/v1/racks",
    setData: itemsQ.setData,
  });
  const setGroupColor = useRowColor<RackGroup>({
    path: "/api/v1/rack-groups",
    setData: groupsQ.setData,
  });

  const removeGroup = async (g: RackGroup) => {
    try {
      await api.del(`/api/v1/rack-groups/${g.id}`);
      if (filterGroup === String(g.id)) setFilterGroup(null);
      toast.success(`Deleted group ${g.name}`);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const columns = useMemo<ColumnDef<RackRow>[]>(
    () => [
      ...(canWrite
        ? [
            {
              id: "order",
              enableSorting: false,
              enableHiding: false,
              header: () => <span className="sr-only">Reorder</span>,
              cell: (c) => (
                <DragHandle
                  reason={orderBlock}
                  label={`Reorder rack ${c.row.original.name}`}
                />
              ),
            } satisfies ColumnDef<RackRow>,
          ]
        : []),
      {
        accessorKey: "name",
        header: ({ column }) => <SortHeader column={column}>Name</SortHeader>,
        cell: (c) => (
          <Link
            href={`/racks/${c.row.original.id}`}
            className="font-medium text-emerald-400 hover:underline"
          >
            <span dir="auto">{c.getValue<string>()}</span>
          </Link>
        ),
      },
      {
        id: "room",
        accessorFn: (r) => r.room ?? "",
        header: ({ column }) => <SortHeader column={column}>Room</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        id: "site",
        accessorKey: "site_name",
        header: ({ column }) => <SortHeader column={column}>Site</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        id: "group",
        accessorKey: "group_name",
        header: ({ column }) => <SortHeader column={column}>Group</SortHeader>,
        cell: (c) => {
          const r = c.row.original;
          if (!r.group_id) {
            return <span className="text-muted-foreground">—</span>;
          }
          return (
            <Link
              href={`/racks/groups/${r.group_id}`}
              className="text-muted-foreground hover:text-emerald-400"
              dir="auto"
            >
              {c.getValue<string>() || `#${r.group_id}`}
            </Link>
          );
        },
      },
      {
        id: "devices",
        accessorKey: "device_count",
        header: ({ column }) => <SortHeader column={column}>Devices</SortHeader>,
        cell: (c) => c.getValue<number>(),
      },
      {
        id: "used",
        accessorKey: "used_u",
        header: ({ column }) => <SortHeader column={column}>Used</SortHeader>,
        cell: (c) => {
          const r = c.row.original;
          const pct = r.height_u ? Math.round((r.used_u / r.height_u) * 100) : 0;
          return (
            <div className="flex items-center gap-2">
              <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full bg-emerald-500/70"
                  style={{ width: `${Math.min(100, pct)}%` }}
                />
              </div>
              <span dir="ltr" className="text-xs text-muted-foreground">
                {r.used_u}/{r.height_u}U
              </span>
            </div>
          );
        },
      },
      {
        accessorKey: "height_u",
        header: ({ column }) => <SortHeader column={column}>Height</SortHeader>,
        cell: (c) => <span dir="ltr">{c.getValue<number>()}U</span>,
      },
      {
        id: "capacity",
        accessorFn: (r) => r.power_w ?? -1,
        header: ({ column }) => (
          <SortHeader column={column}>Capacity</SortHeader>
        ),
        cell: (c) => {
          const r = c.row.original;
          if (r.power_w == null && r.weight_kg == null) {
            return <span className="text-muted-foreground">—</span>;
          }
          return (
            <span dir="ltr" className="whitespace-nowrap text-muted-foreground">
              {[
                r.power_w != null ? formatWatts(r.power_w) : null,
                r.weight_kg != null ? formatKg(r.weight_kg) : null,
              ]
                .filter(Boolean)
                .join(" · ")}
            </span>
          );
        },
      },
      {
        id: "actions",
        header: () => <div className="text-right">Actions</div>,
        enableSorting: false,
        enableHiding: false,
        cell: (c) => (
          <div className="flex justify-end gap-1">
            {canWrite && (
              <PinToggle
                pinned={c.row.original.pinned}
                name={`rack ${c.row.original.name}`}
                onToggle={() =>
                  order.setPinned(c.row.original.id, !c.row.original.pinned)
                }
              />
            )}
            {canWrite && (
              <RowColorPicker
                value={c.row.original.row_color}
                displayColor={c.row.original.display_color}
                name={`rack ${c.row.original.name}`}
                onPick={(color) => setRowColor(c.row.original.id, color)}
              />
            )}
            <Button
              variant="ghost"
              size="icon"
              aria-label={`History of rack ${c.row.original.name}`}
              onClick={() =>
                setHistoryFor({
                  type: "Rack",
                  id: c.row.original.id,
                  title: c.row.original.name,
                })
              }
            >
              <History className="h-4 w-4" />
            </Button>
            {canWrite && (
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Edit rack ${c.row.original.name}`}
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
                aria-label={`Delete rack ${c.row.original.name}`}
                onClick={() => setDeleting(c.row.original)}
              >
                <Trash2 className="h-4 w-4 text-rose-400" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [canWrite, canDelete, order.setPinned, orderBlock, setRowColor]
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
      const r = tableRows[i]?.original;
      if (r) window.location.href = `/racks/${r.id}`;
    },
  });

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });
  const uid = useId();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">
          Racks <DocsLink slug="racks" />
        </h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New rack
          </Button>
        )}
      </div>

      <div className="rounded-lg border">
        <div className="flex items-center justify-between border-b px-3 py-2">
          <span className="flex items-center gap-1.5 text-sm font-medium">
            <Boxes className="h-4 w-4 text-muted-foreground" /> Rack groups
          </span>
          {canWrite && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setEditingGroup(null);
                setGroupDialogOpen(true);
              }}
            >
              <Plus /> New group
            </Button>
          )}
        </div>
        <AsyncPanel
          loading={groupsQ.loading}
          error={groupsQ.error}
          onRetry={groupsQ.reload}
          empty={groups.length === 0}
          emptyMessage="No groups yet — a group renders its racks side by side as a bayed row."
        >
        <Table>
          <TableBody>
            {groups.map((g) => (
              <TableRow key={g.id} style={rowTintStyle(g.display_color)}>
                <TableCell className="font-medium">
                  <Link
                    href={`/racks/groups/${g.id}`}
                    className="text-emerald-400 hover:underline"
                  >
                    <span dir="auto">{g.name}</span>
                  </Link>
                </TableCell>
                <TableCell className="text-muted-foreground">
                  <span dir="auto">
                    {g.site_id ? siteName[g.site_id] ?? "" : ""}
                    {g.site_id && g.description ? " · " : ""}
                    {g.description ?? ""}
                    {!g.site_id && !g.description ? "—" : ""}
                  </span>
                </TableCell>
                <TableCell className="w-24">
                  <Badge variant="outline">
                    {g.rack_count} rack{g.rack_count === 1 ? "" : "s"}
                  </Badge>
                </TableCell>
                <TableCell className="w-44 text-right">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Show racks in group ${g.name}`}
                      title="Show racks in group"
                      onClick={() => setFilterGroup(g.id)}
                    >
                      <ListFilter className="h-4 w-4" />
                    </Button>
                    {canWrite && (
                      <RowColorPicker
                        value={g.row_color}
                        displayColor={g.display_color}
                        name={`group ${g.name}`}
                        onPick={(color) => setGroupColor(g.id, color)}
                      />
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`History of group ${g.name}`}
                      onClick={() =>
                        setHistoryFor({
                          type: "RackGroup",
                          id: g.id,
                          title: g.name,
                        })
                      }
                    >
                      <History className="h-4 w-4" />
                    </Button>
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Edit group ${g.name}`}
                        onClick={() => {
                          setEditingGroup(g);
                          setGroupDialogOpen(true);
                        }}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                    )}
                    {canDelete && (
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Delete group ${g.name}`}
                        onClick={() => removeGroup(g)}
                      >
                        <Trash2 className="h-4 w-4 text-rose-400" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        </AsyncPanel>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search racks…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        {filterGroup !== "" && (
          <Badge variant="secondary" className="gap-1.5">
            <span dir="auto">
              Group: {groups.find((g) => g.id === Number(filterGroup))?.name ?? filterGroup}
            </span>
            <button
              aria-label="Clear group filter"
              onClick={() => setFilterGroup(null)}
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        )}
        <span className="ml-auto text-sm text-muted-foreground">
          {tableRows.length} of {items.length}
        </span>
        <RowColorLegend />
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={itemsQ.loading}
          error={itemsQ.error}
          onRetry={itemsQ.reload}
          empty={items.length === 0}
          emptyMessage="No racks yet — add the first one."
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
            {tableRows.length === 0 && items.length > 0 && (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="py-10 text-center text-muted-foreground"
                >
                  No racks match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </RowOrderDnd>
        </AsyncPanel>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit rack" : "New rack"}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor={`${uid}-name`}>Name</Label>
              <Input id={`${uid}-name`} dir="auto" value={form.name} onChange={set("name")} />
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
                      <span dir="auto">{s.name}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-room`}>Room</Label>
              <Input id={`${uid}-room`} dir="auto" value={form.room} onChange={set("room")} />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-group`}>Rack group</Label>
              <Select
                value={form.group_id}
                onValueChange={(v) => setForm({ ...form, group_id: v })}
              >
                <SelectTrigger id={`${uid}-group`}>
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {groups.map((g) => (
                    <SelectItem key={g.id} value={String(g.id)}>
                      <span dir="auto">{g.name}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-gpos`}>Position in group</Label>
              <Input
                id={`${uid}-gpos`}
                dir="ltr"
                type="number"
                min={1}
                disabled={form.group_id === "none"}
                placeholder="auto (append)"
                value={form.group_position}
                onChange={set("group_position")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-height`}>Height (U)</Label>
              <Input
                id={`${uid}-height`}
                dir="ltr"
                type="number"
                min={1}
                max={100}
                value={form.height_u}
                onChange={set("height_u")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-width`}>Rail width</Label>
              <Select
                value={form.width}
                onValueChange={(v) => setForm({ ...form, width: v })}
              >
                <SelectTrigger id={`${uid}-width`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="19">19″</SelectItem>
                  <SelectItem value="10">10″</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor={`${uid}-desc`}>Description</Label>
              <Input id={`${uid}-desc`} dir="auto" value={form.description} onChange={set("description")} />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor={`${uid}-notes`}>Notes</Label>
              <Input id={`${uid}-notes`} dir="auto" value={form.notes} onChange={set("notes")} />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={submit} disabled={busy || !form.name}>
              {busy ? "Saving…" : editing ? "Save" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleting !== null} onOpenChange={() => setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete rack</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.name}
            </span>
            ? All {deleting?.device_count ?? 0} device placements in it are
            removed too.
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

      <GroupDialog
        open={groupDialogOpen}
        onOpenChange={setGroupDialogOpen}
        group={editingGroup}
        sites={sites}
        onSaved={refresh}
      />

      <HistoryDialog
        open={historyFor !== null}
        onOpenChange={() => setHistoryFor(null)}
        objectType={historyFor?.type ?? null}
        objectId={historyFor?.id ?? null}
        title={historyFor?.title}
      />
    </div>
  );
}
