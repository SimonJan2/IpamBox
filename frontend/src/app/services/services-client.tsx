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
import { useFeatureFlag } from "@/lib/features";
import { PERM } from "@/lib/permissions";
import { foldHebrew } from "@/lib/utils";
import { useUrlSorting, useUrlText } from "@/lib/url-state";
import { SortHeader } from "@/components/sort-header";
import { AsyncPanel } from "@/components/async-panel";
import type { Service, Site } from "@/types";
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

const EMPTY = {
  name: "",
  beneficiary: "",
  site_id: "none",
  site_code: "",
  doc_path: "",
  test_info: "",
  notes: "",
};

// Lookup names are baked into the row objects: TanStack caches accessorFn
// results per row for the lifetime of `data`, so reading siteName inside
// accessorFn leaves "" cached when the sites fetch resolves after the
// services fetch.
type ServiceRow = Service & { site_name: string };

export default function ServicesPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const itemsQ = useAsyncData(() => api.get<Service[]>("/api/v1/services"));
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Site[]>("/api/v1/sites");
    } catch (e) {
      toast.error("Could not load sites", { description: String(e) });
      return [];
    }
  });
  const [q, setQ] = useUrlText("q");
  const [sorting, setSorting] = useUrlSorting();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Service | null>(null);
  const [deleting, setDeleting] = useState<Service | null>(null);
  const followSiteCode = useFeatureFlag("site_code_follow_site");
  const [form, setForm] = useState(EMPTY);
  const [codeManual, setCodeManual] = useState(false);
  const [busy, setBusy] = useState(false);

  const items = itemsQ.data ?? [];
  const sites = sitesQ.data ?? [];
  const refresh = () => void itemsQ.reload();

  useEffect(() => {
    if (dialogOpen) {
      const site = sites.find((s) => s.id === editing?.site_id);
      // A stored code that disagrees with the linked site (or exists with no
      // site) is a deliberate override — don't clobber it on open. With
      // site_code_follow_site (Settings > Features) it's treated as stale.
      const manual =
        !followSiteCode &&
        Boolean(editing?.site_code) &&
        editing?.site_code !== site?.code;
      setForm(
        editing
          ? {
              name: editing.name ?? "",
              beneficiary: editing.beneficiary ?? "",
              site_id: editing.site_id ? String(editing.site_id) : "none",
              site_code: manual
                ? editing.site_code ?? ""
                : site?.code || editing.site_code || "",
              doc_path: editing.doc_path ?? "",
              test_info: editing.test_info ?? "",
              notes: editing.notes ?? "",
            }
          : EMPTY
      );
      setCodeManual(manual);
    }
  }, [dialogOpen, editing, sites, followSiteCode]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        ...Object.fromEntries(
          Object.entries(form)
            .filter(([k]) => k !== "site_id")
            .map(([k, v]) => [k, v || null])
        ),
        site_id: form.site_id === "none" ? null : Number(form.site_id),
      };
      if (editing) {
        await api.patch(`/api/v1/services/${editing.id}`, body);
        toast.success("Service updated");
      } else {
        await api.post("/api/v1/services", body);
        toast.success("Service added");
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
      await api.del(`/api/v1/services/${deleting.id}`);
      toast.success("Service deleted");
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

  const formSite = sites.find((s) => String(s.id) === form.site_id);
  const codeLocked = Boolean(formSite?.code) && !codeManual;

  const onSiteChange = (v: string) => {
    const s = sites.find((x) => String(x.id) === v);
    setForm({
      ...form,
      site_id: v,
      ...(s && !codeManual ? { site_code: s.code ?? "" } : {}),
    });
  };

  const onCodeAuto = (on: boolean) => {
    setCodeManual(!on);
    if (on && formSite) setForm({ ...form, site_code: formSite.code ?? "" });
  };

  const rows = useMemo<ServiceRow[]>(
    () =>
      items.map((s) => ({
        ...s,
        site_name: s.site_id ? (siteName[s.site_id] ?? "") : "",
      })),
    [items, siteName]
  );

  const filtered = useMemo(() => {
    if (!q) return rows;
    const needle = foldHebrew(q.toLowerCase());
    return rows.filter((s) =>
      [
        s.name,
        s.beneficiary,
        s.site_code,
        s.doc_path,
        s.test_info,
        s.notes,
        s.site_name,
      ].some((f) => f != null && foldHebrew(f.toLowerCase()).includes(needle))
    );
  }, [rows, q]);

  const columns = useMemo<ColumnDef<ServiceRow>[]>(
    () => [
      {
        accessorKey: "name",
        header: ({ column }) => <SortHeader column={column}>Name</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="font-medium">
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "beneficiary",
        header: ({ column }) => (
          <SortHeader column={column}>Beneficiary</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
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
        accessorKey: "doc_path",
        header: ({ column }) => (
          <SortHeader column={column}>Documentation</SortHeader>
        ),
        cell: (c) => (
          <span
            dir="ltr"
            title={c.getValue<string | null>() ?? undefined}
            className="block max-w-64 truncate font-mono text-muted-foreground"
          >
            {c.getValue<string | null>() ?? "—"}
          </span>
        ),
      },
      {
        accessorKey: "test_info",
        header: ({ column }) => <SortHeader column={column}>Test</SortHeader>,
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
        <h1 className="text-xl font-semibold">Services</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New service
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search services…"
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
          emptyMessage="No services yet — add the first one."
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
                  colSpan={8}
                  className="py-10 text-center text-muted-foreground"
                >
                  No services match this filter.
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
            <DialogTitle>{editing ? "Edit service" : "New service"}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <div className="grid gap-1.5">
              <Label>Name</Label>
              <Input dir="auto" value={form.name} onChange={set("name")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Beneficiary</Label>
              <Input
                dir="auto"
                value={form.beneficiary}
                onChange={set("beneficiary")}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label>Site</Label>
                <Select value={form.site_id} onValueChange={onSiteChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="None" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
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
                  {formSite?.code && (
                    <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Switch
                        checked={!codeManual}
                        onCheckedChange={onCodeAuto}
                      />
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
            </div>
            <div className="grid gap-1.5">
              <Label>Documentation path</Label>
              <Input
                dir="ltr"
                value={form.doc_path}
                onChange={set("doc_path")}
                placeholder="\\server\share\doc"
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Test info</Label>
              <Input
                dir="auto"
                value={form.test_info}
                onChange={set("test_info")}
              />
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
            <DialogTitle>Delete service</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.name}
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
