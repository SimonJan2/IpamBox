"use client";

import { useCallback, useEffect, useId, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Download,
  FileUp,
  History,
  LayoutTemplate,
  Pencil,
  Plus,
  SlidersHorizontal,
  Trash2,
} from "lucide-react";
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
import { cn } from "@/lib/utils";
import { useUrlSorting } from "@/lib/url-state";
import type { SavedView } from "@/lib/prefs";
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
import { InlineText } from "@/components/inline-edit";
import {
  SmartImportDialog,
  type FieldOption,
  type ImportOption,
} from "@/components/smart-import-dialog";
import { RowColorLegend, RowColorPicker } from "@/components/row-color";
import { SavedViews } from "@/components/saved-views";
import { IpStatusBadge } from "@/components/status-badge";
import {
  DeviceFilterPanel,
  filterDevices,
  useDeviceFilterState,
  type DeviceTextParam,
} from "@/components/device-filter-panel";
import { FilterChip, chipSummary } from "@/components/filter-ui";
import type {
  Device,
  DeviceTemplate,
  Page,
  Rack,
  RackGroup,
  Site,
  TemplateInstantiateResult,
} from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input, Textarea } from "@/components/ui/input";
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
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const EMPTY = {
  name: "",
  device_type: "",
  serial_number: "",
  manufacturer: "",
  model: "",
  mac_address: "",
  category: "",
  site_id: "none",
  notes: "",
};

// Lookup names are baked into rows (TanStack caches accessorFn results per
// row — lookups resolved inside the cell would go stale).
type DeviceRow = Device & { rack_name: string; site_name: string };

const DEVICE_VIEWS: SavedView[] = [
  { name: "Unracked inventory", query: "unracked=1" },
  { name: "Offline", query: "health=offline" },
  { name: "No IP linked", query: "has_ip=0" },
];

const TEXT_CHIP_LABELS: [DeviceTextParam, string][] = [
  ["manufacturer", "Manufacturer"],
  ["model", "Model"],
  ["category", "Category"],
  ["device_type", "Device type"],
];

// Canonical fields the smart importer can write/match on — mirrors
// DEVICE_IMPORT_FIELDS on the backend.
const IMPORT_FIELDS: FieldOption[] = [
  { value: "id", label: "ID (exact match)" },
  { value: "name", label: "Name" },
  { value: "device_type", label: "Device type" },
  { value: "manufacturer", label: "Manufacturer" },
  { value: "model", label: "Model" },
  { value: "category", label: "Category" },
  { value: "serial_number", label: "Serial number" },
  { value: "mac_address", label: "MAC address" },
  { value: "site", label: "Site" },
  { value: "rack", label: "Rack" },
  { value: "rack_group", label: "Rack group" },
  { value: "u_position", label: "U position" },
  { value: "u_height", label: "U height" },
  { value: "face", label: "Face" },
  { value: "carrier", label: "Carrier" },
  { value: "slot", label: "Slot" },
  { value: "slot_layout", label: "Slot layout" },
  { value: "watts", label: "Watts" },
  { value: "weight_kg", label: "Weight (kg)" },
  { value: "ips", label: "IPs (space-separated)" },
  { value: "notes", label: "Notes" },
];

const IMPORT_OPTIONS: ImportOption[] = [
  {
    kind: "select",
    param: "on_match",
    label: "When a row matches",
    defaultValue: "skip",
    choices: [
      { value: "skip", label: "Skip existing" },
      { value: "update", label: "Update matched" },
    ],
  },
  {
    kind: "flag",
    param: "unracked_on_missing",
    label: "Unracked when rack/group missing",
  },
  {
    kind: "flag",
    param: "force",
    label: "Force (commit valid rows despite errors)",
  },
];

export default function DevicesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const itemsQ = useAsyncData(() =>
    api.get<Page<Device>>("/api/v1/devices").then((p) => p.items)
  );
  const racksQ = useAsyncData(() =>
    api.get<Page<Rack>>("/api/v1/racks").then((p) => p.items).catch(() => [])
  );
  const sitesQ = useAsyncData(() =>
    api.get<Page<Site>>("/api/v1/sites").then((p) => p.items).catch(() => [])
  );
  const groupsQ = useAsyncData(() =>
    api.get<RackGroup[]>("/api/v1/rack-groups").catch(() => [])
  );
  const f = useDeviceFilterState();
  const [sorting, setSorting] = useUrlSorting();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [editing, setEditing] = useState<Device | null>(null);
  const [deleting, setDeleting] = useState<Device | null>(null);
  const [historyFor, setHistoryFor] = useState<Device | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [tplId, setTplId] = useState("none");
  const [busy, setBusy] = useState(false);
  const templatesQ = useAsyncData(
    () =>
      api
        .get<Page<DeviceTemplate>>("/api/v1/device-templates?limit=500")
        .then((p) => p.items)
        .catch(() => []),
    [dialogOpen]
  );

  const items = itemsQ.data ?? [];
  const racks = racksQ.data ?? [];
  const sites = sitesQ.data ?? [];
  const groups = groupsQ.data ?? [];
  const refresh = () => void itemsQ.reload();

  useEffect(() => {
    if (dialogOpen) {
      setForm(
        editing
          ? {
              name: editing.name ?? "",
              device_type: editing.device_type ?? "",
              serial_number: editing.serial_number ?? "",
              manufacturer: editing.manufacturer ?? "",
              model: editing.model ?? "",
              mac_address: editing.mac_address ?? "",
              category: editing.category ?? "",
              site_id: editing.site_id ? String(editing.site_id) : "none",
              notes: editing.notes ?? "",
            }
          : EMPTY
      );
      setTplId("none");
    }
  }, [dialogOpen, editing]);

  // Picking a template prefills the catalog fields; instantiate stamps the
  // port layout on the new device in the same server transaction.
  const pickTemplate = (v: string) => {
    setTplId(v);
    const t = (templatesQ.data ?? []).find((x) => String(x.id) === v);
    if (!t) return;
    setForm((f) => ({
      ...f,
      device_type: t.device_type ?? f.device_type,
      manufacturer: t.manufacturer ?? f.manufacturer,
      model: t.model ?? f.model,
      category: t.category ?? f.category,
    }));
  };

  const submit = async () => {
    setBusy(true);
    try {
      const { site_id, ...rest } = form;
      const body = {
        ...Object.fromEntries(
          Object.entries(rest).map(([k, v]) => [k, v || null])
        ),
        site_id: site_id === "none" ? null : Number(site_id),
      };
      if (editing) {
        await api.patch(`/api/v1/devices/${editing.id}`, body);
        toast.success("Device updated");
      } else if (tplId !== "none") {
        const r = await api.post<TemplateInstantiateResult>(
          `/api/v1/device-templates/${tplId}/instantiate`,
          body
        );
        toast.success(
          `Device added — ${r.created} port${r.created === 1 ? "" : "s"} stamped`
        );
      } else {
        await api.post("/api/v1/devices", body);
        toast.success("Device added");
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
      await api.del(`/api/v1/devices/${deleting.id}`);
      toast.success("Device deleted");
      setDeleting(null);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const rackName = useMemo(
    () => Object.fromEntries(racks.map((r) => [r.id, r.name])),
    [racks]
  );
  const siteName = useMemo(
    () => Object.fromEntries(sites.map((s) => [s.id, s.name])),
    [sites]
  );
  const groupName = useMemo(
    () => Object.fromEntries(groups.map((g) => [g.id, g.name])),
    [groups]
  );
  /** rack_id -> group_id — the device "rack group" facet joins through the
   *  device's rack, same as the backend's group_id param. */
  const rackGroup = useMemo(
    () => new Map(racks.map((r) => [r.id, r.group_id] as const)),
    [racks]
  );

  const saveField = useCallback(
    async (id: number, field: "notes", value: string | null) => {
      let prev: Device | undefined;
      itemsQ.setData((cur) => {
        prev = (cur ?? []).find((d) => d.id === id);
        return (cur ?? []).map((d) =>
          d.id === id ? { ...d, [field]: value } : d
        );
      });
      try {
        await api.patch(`/api/v1/devices/${id}`, { [field]: value });
      } catch (e) {
        itemsQ.setData((cur) =>
          (cur ?? []).map((d) => (d.id === id && prev ? prev : d))
        );
        toast.error("Save failed", { description: String(e) });
        throw e;
      }
    },
    [itemsQ.setData]
  );

  const rows = useMemo<DeviceRow[]>(
    () =>
      items.map((d) => ({
        ...d,
        rack_name: d.rack_id ? (rackName[d.rack_id] ?? "") : "",
        site_name: d.site_id ? (siteName[d.site_id] ?? "") : "",
      })),
    [items, rackName, siteName]
  );

  const filtered = useMemo(
    () => filterDevices(rows, f, rackGroup),
    [rows, f, rackGroup]
  );

  const orderBlock = sorting.length
    ? "Row order is fixed while a column sort is on — clear the sort to drag."
    : f.activeCount
      ? "Row order is fixed while filtering — clear filters to drag."
      : null;
  const order = useRowOrder<Device>({
    path: "/api/v1/devices",
    items,
    setData: itemsQ.setData,
    getVisibleIds: (): number[] => tableRows.map((r) => r.original.id),
    enabled: canWrite && !orderBlock,
  });
  const setRowColor = useRowColor<Device>({
    path: "/api/v1/devices",
    setData: itemsQ.setData,
  });

  const columns = useMemo<ColumnDef<DeviceRow>[]>(
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
                  label={`Reorder device ${c.row.original.name}`}
                />
              ),
            } satisfies ColumnDef<DeviceRow>,
          ]
        : []),
      {
        accessorKey: "name",
        header: ({ column }) => <SortHeader column={column}>Name</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="font-medium">
            {c.getValue<string>()}
            {c.row.original.slot_layout && (
              <Badge
                variant="outline"
                className="ml-1.5 text-muted-foreground"
              >
                {c.row.original.slot_layout} carrier
              </Badge>
            )}
          </span>
        ),
      },
      {
        id: "model",
        accessorFn: (d) =>
          [d.manufacturer, d.model].filter(Boolean).join(" "),
        header: ({ column }) => <SortHeader column={column}>Model</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "serial_number",
        header: ({ column }) => <SortHeader column={column}>Serial</SortHeader>,
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        id: "placement",
        accessorFn: (d) =>
          d.rack_id == null
            ? "unracked"
            : `${d.rack_name} U${d.u_position ?? "?"}`,
        header: ({ column }) => (
          <SortHeader column={column}>Placement</SortHeader>
        ),
        cell: (c) =>
          c.row.original.rack_id == null ? (
            <span className="text-muted-foreground">unracked</span>
          ) : (
            <span dir="ltr" className="text-muted-foreground">
              {c.row.original.rack_name} · U{c.row.original.u_position}
              {(c.row.original.u_height ?? 1) > 1
                ? `–${(c.row.original.u_position ?? 0) + (c.row.original.u_height ?? 1) - 1}`
                : ""}
              {c.row.original.face ? ` · ${c.row.original.face}` : ""}
            </span>
          ),
      },
      {
        accessorKey: "ip_count",
        header: ({ column }) => <SortHeader column={column}>IPs</SortHeader>,
        cell: (c) => (
          <span className="text-muted-foreground">
            {c.getValue<number>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "health",
        header: ({ column }) => <SortHeader column={column}>Health</SortHeader>,
        cell: (c) =>
          c.getValue<Device["health"]>() ? (
            <IpStatusBadge s={c.getValue<NonNullable<Device["health"]>>()!} />
          ) : (
            <span className="text-muted-foreground">—</span>
          ),
      },
      {
        accessorKey: "site_name",
        header: ({ column }) => <SortHeader column={column}>Site</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
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
            label={`Edit notes for ${c.row.original.name}`}
            className="max-w-[200px]"
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
                name={`device ${c.row.original.name}`}
                onToggle={() =>
                  order.setPinned(c.row.original.id, !c.row.original.pinned)
                }
              />
            )}
            {canWrite && (
              <RowColorPicker
                value={c.row.original.row_color}
                displayColor={c.row.original.display_color}
                name={`device ${c.row.original.name}`}
                onPick={(color) => setRowColor(c.row.original.id, color)}
              />
            )}
            <Button
              variant="ghost"
              size="icon"
              aria-label={`History of device ${c.row.original.name}`}
              onClick={() => setHistoryFor(c.row.original)}
            >
              <History className="h-4 w-4" />
            </Button>
            {canWrite && (
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Edit device ${c.row.original.name}`}
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
                aria-label={`Delete device ${c.row.original.name}`}
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

  // Toolbar chips — one per active facet; X clears just that facet. Text
  // params clear via setTextsNow so a pending debounce can't resurrect them.
  const chips = useMemo(() => {
    const t = f.texts;
    const clear =
      (patch: Record<string, string | null>) => () => f.setTextsNow(patch);
    const c: { key: string; label: string; clear: () => void }[] = [];
    if (t.q)
      c.push({ key: "q", label: `Search: ${t.q}`, clear: clear({ q: null }) });
    if (f.health.size)
      c.push({
        key: "health",
        label: `Health: ${chipSummary([...f.health])}`,
        clear: clear({ health: null }),
      });
    if (f.unracked === "1")
      c.push({ key: "unracked", label: "Unracked", clear: clear({ unracked: null }) });
    else if (f.unracked === "0")
      c.push({ key: "racked", label: "Racked", clear: clear({ unracked: null }) });
    if (f.mounted)
      c.push({ key: "mounted", label: "In carrier", clear: clear({ mounted: null }) });
    if (f.siteIds.size)
      c.push({
        key: "site_id",
        label: `Site: ${chipSummary(
          [...f.siteIds].map((id) => siteName[Number(id)] ?? `#${id}`)
        )}`,
        clear: clear({ site_id: null }),
      });
    if (f.rackIds.size)
      c.push({
        key: "rack_id",
        label: `Rack: ${chipSummary(
          [...f.rackIds].map((id) => rackName[Number(id)] ?? `#${id}`)
        )}`,
        clear: clear({ rack_id: null }),
      });
    if (f.groupIds.size)
      c.push({
        key: "group_id",
        label: `Group: ${chipSummary(
          [...f.groupIds].map((id) => groupName[Number(id)] ?? `#${id}`)
        )}`,
        clear: clear({ group_id: null }),
      });
    for (const [k, label] of TEXT_CHIP_LABELS)
      if (t[k])
        c.push({ key: k, label: `${label}: ${t[k]}`, clear: clear({ [k]: null }) });
    if (f.sources.size)
      c.push({
        key: "source",
        label: `Source: ${chipSummary([...f.sources])}`,
        clear: clear({ source: null }),
      });
    if (f.faces.size)
      c.push({
        key: "face",
        label: `Face: ${chipSummary([...f.faces])}`,
        clear: clear({ face: null }),
      });
    if (f.hasIp === "1")
      c.push({ key: "has_ip", label: "Has IPs", clear: clear({ has_ip: null }) });
    else if (f.hasIp === "0")
      c.push({ key: "has_ip", label: "No IPs", clear: clear({ has_ip: null }) });
    if (f.wiring.size)
      c.push({
        key: "wiring",
        label: `Wiring: ${chipSummary([...f.wiring])}`,
        clear: clear({ wiring: null }),
      });
    return c;
  }, [f, siteName, rackName, groupName]);

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

  // The export replays the CURRENT query string — every V5A facet lives in
  // the URL, so a filtered view downloads exactly the set it shows.
  const qs = searchParams.toString();
  const exportHref = (ext: "csv" | "xlsx") =>
    `/api/v1/devices/export.${ext}${qs ? `?${qs}` : ""}`;
  const { rowProps, focusRow } = useRowNav({
    count: tableRows.length,
    onOpen: (i) => {
      const d = tableRows[i]?.original;
      if (d) router.push(`/devices/${d.id}`);
    },
  });

  const set =
    (k: keyof typeof EMPTY) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm({ ...form, [k]: e.target.value });
  const uid = useId();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">
          Devices <DocsLink slug="devices" />
        </h1>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            asChild
            aria-label="Device templates"
          >
            <Link href="/devices/templates">
              <LayoutTemplate /> Templates
            </Link>
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" aria-label="Export devices">
                <Download /> Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <a href={exportHref("csv")} download>
                  CSV
                </a>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <a href={exportHref("xlsx")} download>
                  XLSX
                </a>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          {canWrite && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setImportOpen(true)}
              >
                <FileUp /> Import
              </Button>
              <Button
                size="sm"
                onClick={() => {
                  setEditing(null);
                  setDialogOpen(true);
                }}
              >
                <Plus /> New device
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="sm" aria-label="Open filters">
              <SlidersHorizontal /> Filters
              {f.activeCount > 0 && (
                <Badge variant="secondary" className="px-1.5">
                  {f.activeCount}
                </Badge>
              )}
            </Button>
          </SheetTrigger>
          <SheetContent>
            <SheetTitle className="sr-only">Device filters</SheetTitle>
            <SheetDescription className="sr-only">
              Filter devices by health, placement, site, rack, and attributes.
            </SheetDescription>
            <DeviceFilterPanel
              f={f}
              items={rows}
              filtered={filtered}
              sites={sites}
              racks={racks}
              groups={groups}
              rackGroup={rackGroup}
            />
          </SheetContent>
        </Sheet>
        {chips.map((c) => (
          <FilterChip key={c.key} label={c.label} onClear={c.clear} />
        ))}
        <span className="ml-auto text-sm text-muted-foreground">
          {tableRows.length} of {items.length}
        </span>
        <RowColorLegend />
        <SavedViews pageKey="devices" builtins={DEVICE_VIEWS} />
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={itemsQ.loading}
          error={itemsQ.error}
          onRetry={itemsQ.reload}
          empty={items.length === 0}
          emptyMessage="No devices yet — add one, or place devices from a rack."
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
                      onClick={() => router.push(`/devices/${row.original.id}`)}
                      style={rowTintStyle(row.original.display_color)}
                      className={cn(
                        "cursor-pointer",
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
                      No devices match this filter.
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
            <DialogTitle>{editing ? "Edit device" : "New device"}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            {!editing && (templatesQ.data ?? []).length > 0 && (
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-tpl`}>Device template</Label>
                <Select value={tplId} onValueChange={pickTemplate}>
                  <SelectTrigger id={`${uid}-tpl`}>
                    <SelectValue placeholder="None — blank device" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None — blank device</SelectItem>
                    {(templatesQ.data ?? []).map((t) => (
                      <SelectItem key={t.id} value={String(t.id)}>
                        {t.name}
                        {t.manufacturer || t.model
                          ? ` — ${[t.manufacturer, t.model].filter(Boolean).join(" ")}`
                          : ""}
                        {` · ${(t.interfaces?.length ?? 0) + (t.power_ports?.length ?? 0)} ports`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {tplId !== "none" && (
                  <p className="text-xs text-muted-foreground">
                    Its port layout stamps onto the new device on save.
                  </p>
                )}
              </div>
            )}
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-name`}>Name</Label>
              <Input
                id={`${uid}-name`}
                dir="auto"
                value={form.name}
                onChange={set("name")}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-manufacturer`}>Manufacturer</Label>
                <Input
                  id={`${uid}-manufacturer`}
                  dir="auto"
                  value={form.manufacturer}
                  onChange={set("manufacturer")}
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-model`}>Model</Label>
                <Input
                  id={`${uid}-model`}
                  dir="auto"
                  value={form.model}
                  onChange={set("model")}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-serial`}>Serial number</Label>
                <Input
                  id={`${uid}-serial`}
                  dir="ltr"
                  value={form.serial_number}
                  onChange={set("serial_number")}
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-mac`}>MAC address</Label>
                <Input
                  id={`${uid}-mac`}
                  dir="ltr"
                  className="font-mono"
                  value={form.mac_address}
                  onChange={set("mac_address")}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-type`}>Device type</Label>
                <Input
                  id={`${uid}-type`}
                  dir="auto"
                  placeholder="server, switch, pdu…"
                  value={form.device_type}
                  onChange={set("device_type")}
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-category`}>Category</Label>
                <Input
                  id={`${uid}-category`}
                  dir="auto"
                  value={form.category}
                  onChange={set("category")}
                />
              </div>
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
              <Label htmlFor={`${uid}-notes`}>Notes</Label>
              <Textarea
                id={`${uid}-notes`}
                dir="auto"
                value={form.notes}
                onChange={set("notes")}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={submit} disabled={busy || !form.name.trim()}>
              {busy ? "Saving…" : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleting != null} onOpenChange={() => setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete {deleting?.name}?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Linked IPs keep their addresses but lose the device link. Carrier
            children are unmounted.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete} disabled={busy}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <HistoryDialog
        open={historyFor !== null}
        onOpenChange={() => setHistoryFor(null)}
        objectType="Device"
        objectId={historyFor?.id ?? null}
        title={historyFor?.name}
      />

      <SmartImportDialog
        open={importOpen}
        onOpenChange={setImportOpen}
        endpoint="/api/v1/devices/import"
        fields={IMPORT_FIELDS}
        options={IMPORT_OPTIONS}
        title="Import devices"
        description="Upload a CSV or XLSX — headers auto-map (English, Hebrew, NetBox), the dry-run previews every row's action and diffs, then commit applies the ok rows."
        onCommitted={refresh}
      />
    </div>
  );
}
