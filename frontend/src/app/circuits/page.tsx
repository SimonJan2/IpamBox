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
import { PERM } from "@/lib/permissions";
import { foldHebrew } from "@/lib/utils";
import { SortHeader } from "@/components/sort-header";
import type { Circuit } from "@/types";
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
  env: "",
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
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  circuit: Circuit | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) {
      setForm(
        circuit
          ? {
              env: circuit.env ?? "",
              site_number: circuit.site_number?.toString() ?? "",
              site_name: circuit.site_name ?? "",
              site_code: circuit.site_code ?? "",
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
    }
  }, [open, circuit]);

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });

  const submit = async () => {
    setBusy(true);
    try {
      const body = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [
          k,
          k === "site_number" ? (v ? parseInt(v, 10) : null) : v || null,
        ])
      );
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
    ["site_number", "Site #"],
    ["site_name", "Site name"],
    ["site_code", "Site code"],
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
        <div className="grid grid-cols-2 gap-3">
          {fields.map(([k, label]) => (
            <div key={k} className={k === "notes" ? "col-span-2" : "grid gap-1.5"}>
              <Label>{label}</Label>
              <Input
                dir={k === "wan_ip" || k === "bezeq_circuit_id" ? "ltr" : "auto"}
                value={form[k]}
                onChange={set(k)}
              />
            </div>
          ))}
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
  const [items, setItems] = useState<Circuit[]>([]);
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
  };
  useEffect(refresh, []);

  // distinct values for the filter dropdowns, built from the data itself
  const distinct = (k: keyof Circuit) =>
    [...new Set(items.map((c) => c[k]).filter(Boolean) as string[])].sort();
  const envs = useMemo(() => distinct("env"), [items]);
  const types = useMemo(() => distinct("line_type"), [items]);
  const statuses = useMemo(() => distinct("status"), [items]);

  const filtered = useMemo(
    () =>
      items.filter(
        (c) =>
          (envFilter === "all" || c.env === envFilter) &&
          (typeFilter === "all" || c.line_type === typeFilter) &&
          (statusFilter === "all" || c.status === statusFilter)
      ),
    [items, envFilter, typeFilter, statusFilter]
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
            {c.row.original.site_code && (
              <span className="ml-1 text-xs text-muted-foreground">
                {c.row.original.site_code}
              </span>
            )}
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
        <h1 className="text-xl font-semibold">Circuits</h1>
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
                  colSpan={12}
                  className="py-10 text-center text-muted-foreground"
                >
                  No circuits found.
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
