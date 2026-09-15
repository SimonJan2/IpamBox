"use client";

import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import type { Service } from "@/types";
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
  name: "",
  beneficiary: "",
  site_code: "",
  doc_path: "",
  test_info: "",
  notes: "",
};

export default function ServicesPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [items, setItems] = useState<Service[]>([]);
  const [q, setQ] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Service | null>(null);
  const [deleting, setDeleting] = useState<Service | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = () => {
    api.get<Service[]>("/api/v1/services").then(setItems).catch(() => {});
  };
  useEffect(refresh, []);

  useEffect(() => {
    if (dialogOpen) {
      setForm(
        editing
          ? {
              name: editing.name ?? "",
              beneficiary: editing.beneficiary ?? "",
              site_code: editing.site_code ?? "",
              doc_path: editing.doc_path ?? "",
              test_info: editing.test_info ?? "",
              notes: editing.notes ?? "",
            }
          : EMPTY
      );
    }
  }, [dialogOpen, editing]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [k, v || null])
      );
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

  const filtered = items.filter((s) => {
    const needle = q.toLowerCase();
    return [s.name, s.beneficiary, s.site_code, s.doc_path]
      .filter(Boolean)
      .some((v) => v!.toLowerCase().includes(needle));
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

      <Input
        placeholder="Search services…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="max-w-xs"
      />

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Beneficiary</TableHead>
              <TableHead>Site code</TableHead>
              <TableHead>Documentation</TableHead>
              <TableHead>Test</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((s) => (
              <TableRow key={s.id}>
                <TableCell dir="auto" className="font-medium">
                  {s.name ?? "—"}
                </TableCell>
                <TableCell dir="auto" className="text-muted-foreground">
                  {s.beneficiary ?? "—"}
                </TableCell>
                <TableCell dir="ltr" className="font-mono text-muted-foreground">
                  {s.site_code ?? "—"}
                </TableCell>
                <TableCell dir="ltr" className="max-w-64 truncate font-mono text-muted-foreground">
                  {s.doc_path ?? "—"}
                </TableCell>
                <TableCell dir="auto" className="text-muted-foreground">
                  {s.test_info ?? "—"}
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
                  colSpan={6}
                  className="py-10 text-center text-muted-foreground"
                >
                  No services found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
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
            <div className="grid gap-1.5">
              <Label>Site code</Label>
              <Input
                dir="ltr"
                value={form.site_code}
                onChange={set("site_code")}
              />
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
