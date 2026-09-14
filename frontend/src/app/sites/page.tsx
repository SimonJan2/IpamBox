"use client";

import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import type { Site } from "@/types";
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

function SiteDialog({
  open,
  onOpenChange,
  site,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  site: Site | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({ name: "", slug: "", description: "" });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open) {
      setForm({
        name: site?.name ?? "",
        slug: site?.slug ?? "",
        description: site?.description ?? "",
      });
    }
  }, [open, site]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        name: form.name,
        slug: form.slug || undefined,
        description: form.description || null,
      };
      if (site) {
        await api.patch(`/api/v1/sites/${site.id}`, body);
        toast.success("Site updated");
      } else {
        await api.post("/api/v1/sites", body);
        toast.success("Site created");
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
          <DialogTitle>{site ? "Edit site" : "New site"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label>Name</Label>
            <Input
              placeholder="DC-East"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label>Slug</Label>
            <Input
              placeholder="dc-east (auto if empty)"
              value={form.slug}
              onChange={(e) => setForm({ ...form, slug: e.target.value })}
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
          <Button onClick={submit} disabled={busy || !form.name}>
            {busy ? "Saving…" : site ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DeleteDialog({
  site,
  onOpenChange,
  onDeleted,
}: {
  site: Site | null;
  onOpenChange: (o: boolean) => void;
  onDeleted: () => void;
}) {
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!site) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/sites/${site.id}`);
      toast.success(`Deleted ${site.name}`);
      onOpenChange(false);
      onDeleted();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={site !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete site</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Delete <span className="font-medium text-foreground">{site?.name}</span>?
          This cannot be undone.
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

export default function SitesPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [sites, setSites] = useState<Site[]>([]);
  const [q, setQ] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Site | null>(null);
  const [deleting, setDeleting] = useState<Site | null>(null);

  const refresh = () => {
    api.get<Site[]>("/api/v1/sites").then(setSites).catch(() => {});
  };
  useEffect(refresh, []);

  const filtered = sites.filter(
    (s) =>
      s.name.toLowerCase().includes(q.toLowerCase()) ||
      s.slug.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Sites</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New site
          </Button>
        )}
      </div>

      <Input
        placeholder="Search sites…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="max-w-xs"
      />

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Slug</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((s) => (
              <TableRow key={s.id}>
                <TableCell className="font-medium">{s.name}</TableCell>
                <TableCell className="font-mono text-muted-foreground">
                  {s.slug}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {s.description ?? "—"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {new Date(s.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(s);
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
                        onClick={() => setDeleting(s)}
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
                  colSpan={5}
                  className="py-10 text-center text-muted-foreground"
                >
                  No sites found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <SiteDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        site={editing}
        onSaved={refresh}
      />
      <DeleteDialog
        site={deleting}
        onOpenChange={() => setDeleting(null)}
        onDeleted={refresh}
      />
    </div>
  );
}
