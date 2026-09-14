"use client";

import { useEffect, useMemo, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import type { Site, Vrf } from "@/types";
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

const NONE = "__none__";

function VrfDialog({
  open,
  onOpenChange,
  vrf,
  sites,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  vrf: Vrf | null;
  sites: Site[];
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: "",
    rd: "",
    site_id: NONE,
    description: "",
  });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) {
      setForm({
        name: vrf?.name ?? "",
        rd: vrf?.rd ?? "",
        site_id: vrf?.site_id ? String(vrf.site_id) : NONE,
        description: vrf?.description ?? "",
      });
    }
  }, [open, vrf]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        name: form.name,
        rd: form.rd || null,
        site_id: form.site_id === NONE ? null : Number(form.site_id),
        description: form.description || null,
      };
      if (vrf) {
        await api.patch(`/api/v1/vrfs/${vrf.id}`, body);
        toast.success("VRF updated");
      } else {
        await api.post("/api/v1/vrfs", body);
        toast.success("VRF created");
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
          <DialogTitle>{vrf ? "Edit VRF" : "New VRF"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label>Name</Label>
            <Input
              placeholder="production"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label>Route distinguisher</Label>
            <Input
              placeholder="65000:1 (optional)"
              value={form.rd}
              onChange={(e) => setForm({ ...form, rd: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label>Site</Label>
            <Select
              value={form.site_id}
              onValueChange={(v) => setForm({ ...form, site_id: v })}
            >
              <SelectTrigger>
                <SelectValue placeholder="None" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={NONE}>None</SelectItem>
                {sites.map((s) => (
                  <SelectItem key={s.id} value={String(s.id)}>
                    {s.name}
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
          <Button onClick={submit} disabled={busy || !form.name}>
            {busy ? "Saving…" : vrf ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DeleteDialog({
  vrf,
  onOpenChange,
  onDeleted,
}: {
  vrf: Vrf | null;
  onOpenChange: (o: boolean) => void;
  onDeleted: () => void;
}) {
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!vrf) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/vrfs/${vrf.id}`);
      toast.success(`Deleted ${vrf.name}`);
      onOpenChange(false);
      onDeleted();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={vrf !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete VRF</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Delete <span className="font-medium text-foreground">{vrf?.name}</span>?
          All prefixes and IP addresses inside it will be removed. This cannot be
          undone.
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

export default function VrfsPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [vrfs, setVrfs] = useState<Vrf[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [q, setQ] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Vrf | null>(null);
  const [deleting, setDeleting] = useState<Vrf | null>(null);

  const refresh = () => {
    api.get<Vrf[]>("/api/v1/vrfs").then(setVrfs).catch(() => {});
    api.get<Site[]>("/api/v1/sites").then(setSites).catch(() => {});
  };
  useEffect(refresh, []);

  const siteName = useMemo(
    () => Object.fromEntries(sites.map((s) => [s.id, s.name])),
    [sites]
  );

  const filtered = vrfs.filter(
    (v) =>
      v.name.toLowerCase().includes(q.toLowerCase()) ||
      (v.rd ?? "").toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">VRFs</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New VRF
          </Button>
        )}
      </div>

      <Input
        placeholder="Search VRFs…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="max-w-xs"
      />

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>RD</TableHead>
              <TableHead>Site</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((v) => (
              <TableRow key={v.id}>
                <TableCell className="font-medium">{v.name}</TableCell>
                <TableCell className="font-mono text-muted-foreground">
                  {v.rd ?? "—"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {v.site_id ? siteName[v.site_id] ?? "—" : "—"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {v.description ?? "—"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {new Date(v.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(v);
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
                        onClick={() => setDeleting(v)}
                      >
                        <Trash2 className="h-4 w-4 text-rose-400" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {filtered.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="py-10 text-center text-muted-foreground"
                >
                  No VRFs found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <VrfDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        vrf={editing}
        sites={sites}
        onSaved={refresh}
      />
      <DeleteDialog
        vrf={deleting}
        onOpenChange={() => setDeleting(null)}
        onDeleted={refresh}
      />
    </div>
  );
}
