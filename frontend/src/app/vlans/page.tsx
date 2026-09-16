"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ListFilter, Pencil, Plus, Trash2, X } from "lucide-react";
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
import type { Site, Vlan, VlanGroup, VlanStatus } from "@/types";
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

const VLAN_STATUSES: VlanStatus[] = ["active", "reserved", "deprecated"];

function VlanDialog({
  open,
  onOpenChange,
  vlan,
  groups,
  sites,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  vlan: Vlan | null;
  groups: VlanGroup[];
  sites: Site[];
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    vid: "",
    name: "",
    group_id: "none",
    site_id: "none",
    status: "active" as VlanStatus,
    description: "",
  });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) {
      setForm({
        vid: vlan ? String(vlan.vid) : "",
        name: vlan?.name ?? "",
        group_id: vlan?.group_id ? String(vlan.group_id) : "none",
        site_id: vlan?.site_id ? String(vlan.site_id) : "none",
        status: vlan?.status ?? "active",
        description: vlan?.description ?? "",
      });
    }
  }, [open, vlan]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        vid: Number(form.vid),
        name: form.name,
        group_id: form.group_id === "none" ? null : Number(form.group_id),
        site_id: form.site_id === "none" ? null : Number(form.site_id),
        status: form.status,
        description: form.description || null,
      };
      if (vlan) {
        await api.patch(`/api/v1/vlans/${vlan.id}`, body);
        toast.success("VLAN updated");
      } else {
        await api.post("/api/v1/vlans", body);
        toast.success("VLAN created");
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
          <DialogTitle>{vlan ? "Edit VLAN" : "New VLAN"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>VLAN ID (1–4094)</Label>
              <Input
                type="number"
                min={1}
                max={4094}
                value={form.vid}
                onChange={(e) => setForm({ ...form, vid: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Name</Label>
              <Input
                placeholder="users"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Group</Label>
              <Select
                value={form.group_id}
                onValueChange={(v) => setForm({ ...form, group_id: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {groups.map((g) => (
                    <SelectItem key={g.id} value={String(g.id)}>
                      {g.name}
                    </SelectItem>
                  ))}
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
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {sites.map((s) => (
                    <SelectItem key={s.id} value={String(s.id)}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label>Status</Label>
            <Select
              value={form.status}
              onValueChange={(v) => setForm({ ...form, status: v as VlanStatus })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {VLAN_STATUSES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Description</Label>
            <Input
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !form.vid || !form.name}>
            {busy ? "Saving…" : vlan ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function GroupDialog({
  open,
  onOpenChange,
  group,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  group: VlanGroup | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({ name: "", description: "" });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) {
      setForm({ name: group?.name ?? "", description: group?.description ?? "" });
    }
  }, [open, group]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = { name: form.name, description: form.description || null };
      if (group) {
        await api.patch(`/api/v1/vlan-groups/${group.id}`, body);
        toast.success("Group updated");
      } else {
        await api.post("/api/v1/vlan-groups", body);
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
            <Label>Name</Label>
            <Input
              placeholder="e.g. Access, Management…"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label>Description</Label>
            <Input
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
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

export default function VlansPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [vlans, setVlans] = useState<Vlan[]>([]);
  const [groups, setGroups] = useState<VlanGroup[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [q, setQ] = useState("");
  const [sorting, setSorting] = useState<SortingState>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Vlan | null>(null);
  const [groupDialogOpen, setGroupDialogOpen] = useState(false);
  const [editingGroup, setEditingGroup] = useState<VlanGroup | null>(null);
  const [filterGroup, setFilterGroup] = useState<number | null>(null);

  const refresh = useCallback(() => {
    const q = filterGroup ? `?group_id=${filterGroup}` : "";
    api.get<Vlan[]>(`/api/v1/vlans${q}`).then(setVlans).catch(() => {});
    api.get<VlanGroup[]>("/api/v1/vlan-groups").then(setGroups).catch(() => {});
    api.get<Site[]>("/api/v1/sites").then(setSites).catch(() => {});
  }, [filterGroup]);

  useEffect(refresh, [refresh]);

  const groupName = useMemo(
    () => Object.fromEntries(groups.map((g) => [g.id, g.name])),
    [groups]
  );
  const siteName = useMemo(
    () => Object.fromEntries(sites.map((s) => [s.id, s.name])),
    [sites]
  );

  const remove = useCallback(
    async (v: Vlan) => {
      try {
        await api.del(`/api/v1/vlans/${v.id}`);
        toast.success(`Deleted VLAN ${v.vid}`);
        refresh();
      } catch (e) {
        toast.error("Delete failed", { description: String(e) });
      }
    },
    [refresh]
  );

  const filtered = useMemo(() => {
    if (!q) return vlans;
    const needle = foldHebrew(q.toLowerCase());
    return vlans.filter((v) =>
      [
        String(v.vid),
        v.name,
        v.group_id ? groupName[v.group_id] : null,
        v.site_id ? siteName[v.site_id] : null,
        v.status,
        v.description,
      ].some((f) => f != null && foldHebrew(f.toLowerCase()).includes(needle))
    );
  }, [vlans, q, groupName, siteName]);

  const columns = useMemo<ColumnDef<Vlan>[]>(
    () => [
      {
        accessorKey: "vid",
        header: ({ column }) => (
          <SortHeader column={column}>VID</SortHeader>
        ),
        cell: (c) => (
          <span className="font-mono font-medium">{c.getValue<number>()}</span>
        ),
      },
      {
        accessorKey: "name",
        header: ({ column }) => <SortHeader column={column}>Name</SortHeader>,
        cell: (c) => <span dir="auto">{c.getValue<string>()}</span>,
      },
      {
        id: "group",
        accessorFn: (v) => (v.group_id ? (groupName[v.group_id] ?? "") : ""),
        header: ({ column }) => (
          <SortHeader column={column}>Group</SortHeader>
        ),
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        id: "site",
        accessorFn: (v) => (v.site_id ? (siteName[v.site_id] ?? "") : ""),
        header: ({ column }) => <SortHeader column={column}>Site</SortHeader>,
        cell: (c) => (
          <span dir="auto" className="text-muted-foreground">
            {c.getValue<string>() || "—"}
          </span>
        ),
      },
      {
        accessorKey: "status",
        header: ({ column }) => (
          <SortHeader column={column}>Status</SortHeader>
        ),
        cell: (c) => (
          <Badge variant="outline" className="capitalize">
            {c.getValue<string>()}
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
                onClick={() => remove(c.row.original)}
              >
                <Trash2 className="h-4 w-4 text-rose-400" />
              </Button>
            )}
          </div>
        ),
      },
    ],
    [groupName, siteName, canWrite, canDelete, remove]
  );

  const table = useReactTable({
    data: filtered,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    state: { sorting },
    onSortingChange: setSorting,
  });

  const removeGroup = async (g: VlanGroup) => {
    try {
      await api.del(`/api/v1/vlan-groups/${g.id}`);
      if (filterGroup === g.id) setFilterGroup(null);
      toast.success(`Deleted group ${g.name}`);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">VLANs</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New VLAN
          </Button>
        )}
      </div>

      <div className="rounded-lg border">
        <div className="flex items-center justify-between border-b px-3 py-2">
          <span className="text-sm font-medium">VLAN groups</span>
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
        <Table>
          <TableBody>
            {groups.map((g) => (
              <TableRow key={g.id}>
                <TableCell className="font-medium">{g.name}</TableCell>
                <TableCell className="text-muted-foreground">
                  {g.description ?? "—"}
                </TableCell>
                <TableCell className="w-24">
                  <Badge variant="outline">{g.vlan_count} VLANs</Badge>
                </TableCell>
                <TableCell className="w-32 text-right">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Show VLANs in group"
                      onClick={() => setFilterGroup(g.id)}
                    >
                      <ListFilter className="h-4 w-4" />
                    </Button>
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="icon"
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
                        onClick={() => removeGroup(g)}
                      >
                        <Trash2 className="h-4 w-4 text-rose-400" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {groups.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="py-6 text-center text-muted-foreground"
                >
                  No groups yet.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search VLANs…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        {filterGroup !== null && (
          <Badge variant="secondary" className="gap-1.5">
            Group: {groupName[filterGroup] ?? filterGroup}
            <button onClick={() => setFilterGroup(null)}>
              <X className="h-3 w-3" />
            </button>
          </Badge>
        )}
        <span className="ml-auto text-sm text-muted-foreground">
          {table.getRowModel().rows.length} of {vlans.length}
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
                  colSpan={7}
                  className="py-10 text-center text-muted-foreground"
                >
                  No VLANs found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <VlanDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        vlan={editing}
        groups={groups}
        sites={sites}
        onSaved={refresh}
      />
      <GroupDialog
        open={groupDialogOpen}
        onOpenChange={setGroupDialogOpen}
        group={editingGroup}
        onSaved={refresh}
      />
    </div>
  );
}
