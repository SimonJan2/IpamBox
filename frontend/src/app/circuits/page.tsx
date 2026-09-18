"use client";

import { useEffect, useMemo, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useFeatureFlag } from "@/lib/features";
import { PERM } from "@/lib/permissions";
import { cn, foldHebrew } from "@/lib/utils";
import { SortHeader } from "@/components/sort-header";
import type { Circuit, Site } from "@/types";
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
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const NONE = "__none__";

const EMPTY = {
  env: "",
  site_id: NONE,
  site_number: "",
  site_name: "",
  site_code: "",
  line_type: "",
  bezeq_circuit_id: "",
  node: "",
  bw_down: "",
  bw_up: "",
  wan_ip: "",
  status: "",
  contact: "",
  notes: "",
};

function CircuitDialog({
  open,
  onOpenChange,
  circuit,
  sites,
  defaultRetired,
  followSiteCode,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  circuit: Circuit | null;
  sites: Site[];
  defaultRetired: boolean;
  followSiteCode: boolean;
  onSaved: () => void;
}) {
  const [form, setForm] = useState(EMPTY);
  const [codeManual, setCodeManual] = useState(false);
  const [retired, setRetired] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) {
      const site = sites.find((s) => s.id === circuit?.site_id);
      // A stored code that disagrees with the linked site (or exists with no
      // site) is a deliberate override — don't clobber it on open. With
      // site_code_follow_site (Settings > Features) it's treated as stale.
      const manual =
        !followSiteCode &&
        Boolean(circuit?.site_code) &&
        circuit?.site_code !== site?.code;
      setForm(
        circuit
          ? {
              env: circuit.env ?? "",
              site_id: circuit.site_id ? String(circuit.site_id) : NONE,
              // fill empty site fields from the link; keep stored values
              site_number:
                circuit.site_number?.toString() ??
                site?.site_number?.toString() ??
                "",
              site_name: circuit.site_name || site?.name || "",
              site_code: manual
                ? circuit.site_code ?? ""
                : site?.code || circuit.site_code || "",
              line_type: circuit.line_type ?? "",
              bezeq_circuit_id: circuit.bezeq_circuit_id ?? "",
              node: circuit.node ?? "",
              bw_down: circuit.bw_down ?? "",
              bw_up: circuit.bw_up ?? "",
              wan_ip: circuit.wan_ip ?? "",
              status: circuit.status ?? "",
              contact: circuit.contact ?? "",
              notes: circuit.notes ?? "",
            }
          : EMPTY
      );
      setCodeManual(manual);
      setRetired(circuit?.is_retired ?? defaultRetired);
    }
  }, [open, circuit, sites, defaultRetired, followSiteCode]);

  const site = sites.find((s) => String(s.id) === form.site_id);
  const codeLocked = Boolean(site?.code) && !codeManual;

  const onSiteChange = (v: string) => {
    const s = sites.find((x) => String(x.id) === v);
    setForm({
      ...form,
      site_id: v,
      ...(s
        ? {
            ...(codeManual ? {} : { site_code: s.code ?? "" }),
            site_name: s.name,
            site_number: s.site_number?.toString() ?? "",
          }
        : {}),
    });
  };

  const onCodeAuto = (on: boolean) => {
    setCodeManual(!on);
    if (on && site) setForm({ ...form, site_code: site.code ?? "" });
  };

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });

  const submit = async () => {
    setBusy(true);
    try {
      const body: Record<string, unknown> = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [
          k,
          k === "site_id"
            ? v === NONE
              ? null
              : Number(v)
            : k === "site_number"
              ? v
                ? parseInt(v, 10)
                : null
              : v || null,
        ])
      );
      body.is_retired = retired;
      if (circuit) {
        await api.patch(`/api/v1/circuits/${circuit.id}`, body);
        toast.success("Circuit updated");
      } else {
        await api.post("/api/v1/circuits", body);
        toast.success("Circuit created");
      }
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const fields: [keyof typeof EMPTY, string][] = [
    ["env", "Environment"],
    ["line_type", "Line type"],
    ["bezeq_circuit_id", "Bezeq circuit ID"],
    ["node", "Node"],
    ["bw_down", "BW down"],
    ["bw_up", "BW up"],
    ["wan_ip", "WAN IP"],
    ["status", "Status"],
    ["contact", "Contact"],
    ["notes", "Notes"],
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{circuit ? "Edit circuit" : "New circuit"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Site</Label>
              <Select value={form.site_id} onValueChange={onSiteChange}>
                <SelectTrigger>
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={NONE}>None</SelectItem>
                  {sites.map((s) => (
                    <SelectItem key={s.id} value={String(s.id)}>
                      <span dir="auto">
                        {s.code ? `${s.code} — ` : ""}
                        {s.name}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <div className="flex items-center justify-between">
                <Label>Site code</Label>
                {site?.code && (
                  <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Switch checked={!codeManual} onCheckedChange={onCodeAuto} />
                    from site
                  </label>
                )}
              </div>
              <Input
                dir="ltr"
                value={form.site_code}
                disabled={codeLocked}
                onChange={set("site_code")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Site name</Label>
              <Input dir="auto" value={form.site_name} onChange={set("site_name")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Site #</Label>
              <Input dir="ltr" value={form.site_number} onChange={set("site_number")} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {fields.map(([k, label]) => (
              <div
                key={k}
                className={k === "notes" ? "col-span-2" : "grid gap-1.5"}
              >
                <Label>{label}</Label>
                <Input
                  dir={k === "wan_ip" || k === "bezeq_circuit_id" ? "ltr" : "auto"}
                  value={form[k]}
                  onChange={set(k)}
                />
              </div>
            ))}
          </div>
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <Switch checked={retired} onCheckedChange={setRetired} />
            Retired — shown under Retired Circuits
          </label>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy}>
            {busy ? "Saving…" : circuit ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function CircuitsPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const followSiteCode = useFeatureFlag("site_code_follow_site");
  const [items, setItems] = useState<Circuit[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [tab, setTab] = useState<"active" | "retired">("active");
  const [q, setQ] = useState("");
  const [envFilter, setEnvFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sorting, setSorting] = useState<SortingState>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Circuit | null>(null);
  const [deleting, setDeleting] = useState<Circuit | null>(null);

  const refresh = () => {
    api.get<Circuit[]>("/api/v1/circuits").then(setItems).catch(() => {});
    api.get<Site[]>("/api/v1/sites").then(setSites).catch(() => {});
  };
  useEffect(refresh, []);

  // legacy imports (קוי בזק ישן) live in the Retired Circuits tab
  const activeItems = useMemo(() => items.filter((c) => !c.is_retired), [items]);
  const retiredItems = useMemo(() => items.filter((c) => c.is_retired), [items]);
  const scopedItems = tab === "retired" ? retiredItems : activeItems;

  // distinct values for the filter dropdowns, built from the data itself
  const distinct = (k: keyof Circuit) =>
    [...new Set(scopedItems.map((c) => c[k]).filter(Boolean) as string[])].sort();
  const envs = useMemo(() => distinct("env"), [scopedItems]);
  const types = useMemo(() => distinct("line_type"), [scopedItems]);
  const statuses = useMemo(() => distinct("status"), [scopedItems]);

  const filtered = useMemo(
    () =>
      scopedItems.filter(
        (c) =>
          (envFilter === "all" || c.env === envFilter) &&
          (typeFilter === "all" || c.line_type === typeFilter) &&
          (statusFilter === "all" || c.status === statusFilter)
      ),
    [scopedItems, envFilter, typeFilter, statusFilter]
  );

  const columns = useMemo<ColumnDef<Circuit>[]>(
    () => [
      {
        accessorKey: "env",
        header: ({ column }) => <SortHeader column={column}>Env</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "site_name",
        header: ({ column }) => <SortHeader column={column}>Site</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="font-medium">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "site_code",
        header: ({ column }) => (
          <SortHeader column={column}>Site code</SortHeader>
        ),
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "site_number",
        header: ({ column }) => (
          <SortHeader column={column}>Site #</SortHeader>
        ),
        cell: (c) => (
          <span className="font-mono text-muted-foreground">
            {c.getValue<number | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "line_type",
        header: ({ column }) => <SortHeader column={column}>Type</SortHeader>,
        cell: (c) =>
          c.getValue<string | null>() ? (
            <Badge variant="outline">{c.getValue<string>()}</Badge>
          ) : (
            "—"
          ),
      },
      {
        accessorKey: "bezeq_circuit_id",
        header: ({ column }) => (
          <SortHeader column={column}>Bezeq ID</SortHeader>
        ),
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "node",
        header: ({ column }) => <SortHeader column={column}>Node</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        id: "bw",
        header: "BW ↓/↑",
        enableSorting: false,
        cell: (c) => {
          const r = c.row.original;
          return (
            <span dir="ltr" className="font-mono text-muted-foreground">
              {r.bw_down || r.bw_up
                ? `${r.bw_down ?? "?"}/${r.bw_up ?? "?"}`
                : "—"}
            </span>
          );
        },
      },
      {
        accessorKey: "wan_ip",
        header: ({ column }) => <SortHeader column={column}>WAN IP</SortHeader>,
        cell: (c) => (
          <span dir="ltr" className="font-mono text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "status",
        header: ({ column }) => (
          <SortHeader column={column}>Status</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "contact",
        header: ({ column }) => (
          <SortHeader column={column}>Contact</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
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
        header: "",
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
    getFilteredRowModel: getFilteredRowModel(),
    state: { sorting, globalFilter: q },
    onSortingChange: setSorting,
    onGlobalFilterChange: setQ,
    globalFilterFn: (row, _id, value) => {
      const needle = foldHebrew(String(value).toLowerCase());
      return Object.values(row.original).some(
        (v) => v != null && foldHebrew(String(v).toLowerCase()).includes(needle)
      );
    },
  });

  const doDelete = async () => {
    if (!deleting) return;
    try {
      await api.del(`/api/v1/circuits/${deleting.id}`);
      toast.success("Circuit deleted");
      setDeleting(null);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const filtersActive =
    envFilter !== "all" || typeFilter !== "all" || statusFilter !== "all";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold">Circuits</h1>
          <div className="inline-flex h-8 items-center rounded-lg border bg-muted/50 p-0.5 text-muted-foreground">
            {(
              [
                ["active", "Circuits", activeItems.length],
                ["retired", "Retired Circuits", retiredItems.length],
              ] as const
            ).map(([key, label, count]) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={cn(
                  "inline-flex h-full items-center gap-1.5 rounded-md px-3 text-sm font-medium transition-colors",
                  tab === key
                    ? "bg-background text-foreground shadow-sm"
                    : "hover:text-foreground"
                )}
              >
                {label}
                <span
                  className={cn(
                    "rounded-full px-1.5 text-xs tabular-nums",
                    tab === key
                      ? "bg-muted text-muted-foreground"
                      : "text-muted-foreground/70"
                  )}
                >
                  {count}
                </span>
              </button>
            ))}
          </div>
        </div>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New circuit
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search circuits…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Select value={envFilter} onValueChange={setEnvFilter}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="All envs" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All envs</SelectItem>
            {envs.map((v) => (
              <SelectItem key={v} value={v}>
                <span dir="auto">{v}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="All types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All types</SelectItem>
            {types.map((v) => (
              <SelectItem key={v} value={v}>
                {v}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-36">
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {statuses.map((v) => (
              <SelectItem key={v} value={v}>
                <span dir="auto">{v}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {filtersActive && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setEnvFilter("all");
              setTypeFilter("all");
              setStatusFilter("all");
            }}
          >
            Clear filters
          </Button>
        )}
        <span className="ml-auto text-sm text-muted-foreground">
          {table.getRowModel().rows.length} of {scopedItems.length}
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
                  colSpan={columns.length}
                  className="py-10 text-center text-muted-foreground"
                >
                  {tab === "retired"
                    ? "No retired circuits."
                    : "No circuits found."}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <CircuitDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        circuit={editing}
        sites={sites}
        defaultRetired={tab === "retired"}
        followSiteCode={followSiteCode}
        onSaved={refresh}
      />
      <Dialog open={deleting !== null} onOpenChange={() => setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete circuit</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete circuit{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.bezeq_circuit_id ?? deleting?.site_name}
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
