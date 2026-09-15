"use client";

import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import type { Certificate } from "@/types";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const EMPTY = {
  platform: "",
  target: "",
  server_name: "",
  cert_name: "",
  expires_on: "",
  notes: "",
};

function expiryBadge(expiresOn: string | null) {
  if (!expiresOn) return <span className="text-muted-foreground">—</span>;
  const days = Math.ceil(
    (new Date(expiresOn).getTime() - Date.now()) / 86_400_000
  );
  const cls =
    days < 0
      ? "border-rose-500/40 text-rose-400"
      : days < 30
        ? "border-amber-500/40 text-amber-400"
        : "border-emerald-500/40 text-emerald-400";
  return (
    <Badge variant="outline" className={cls}>
      {days < 0 ? `expired ${-days}d ago` : `${days}d left`}
    </Badge>
  );
}

export default function CertificatesPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [items, setItems] = useState<Certificate[]>([]);
  const [q, setQ] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Certificate | null>(null);
  const [deleting, setDeleting] = useState<Certificate | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = () => {
    api
      .get<Certificate[]>("/api/v1/certificates")
      .then(setItems)
      .catch(() => {});
  };
  useEffect(refresh, []);

  useEffect(() => {
    if (dialogOpen) {
      setForm(
        editing
          ? {
              platform: editing.platform ?? "",
              target: editing.target ?? "",
              server_name: editing.server_name ?? "",
              cert_name: editing.cert_name ?? "",
              expires_on: editing.expires_on ?? "",
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
        ...Object.fromEntries(
          Object.entries(form).map(([k, v]) => [k, v || null])
        ),
        expires_on: form.expires_on || null,
      };
      if (editing) {
        await api.patch(`/api/v1/certificates/${editing.id}`, body);
        toast.success("Certificate updated");
      } else {
        await api.post("/api/v1/certificates", body);
        toast.success("Certificate added");
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
      await api.del(`/api/v1/certificates/${deleting.id}`);
      toast.success("Certificate deleted");
      setDeleting(null);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const filtered = items
    .filter((c) => {
      const s = q.toLowerCase();
      return [c.platform, c.target, c.server_name, c.cert_name]
        .filter(Boolean)
        .some((v) => v!.toLowerCase().includes(s));
    })
    .sort((a, b) => (a.expires_on ?? "9999").localeCompare(b.expires_on ?? "9999"));

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Certificates</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New certificate
          </Button>
        )}
      </div>

      <Input
        placeholder="Search certificates…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="max-w-xs"
      />

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Certificate</TableHead>
              <TableHead>Platform</TableHead>
              <TableHead>Server / VS</TableHead>
              <TableHead>Expires</TableHead>
              <TableHead>Countdown</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((c) => (
              <TableRow key={c.id}>
                <TableCell dir="auto" className="font-medium">
                  {c.cert_name ?? "—"}
                </TableCell>
                <TableCell dir="auto" className="text-muted-foreground">
                  {c.platform ?? "—"}
                </TableCell>
                <TableCell dir="auto" className="text-muted-foreground">
                  {[c.server_name, c.target].filter(Boolean).join(" · ") || "—"}
                </TableCell>
                <TableCell dir="ltr" className="font-mono text-muted-foreground">
                  {c.expires_on ?? "—"}
                </TableCell>
                <TableCell>{expiryBadge(c.expires_on)}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(c);
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
                        onClick={() => setDeleting(c)}
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
                  No certificates found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editing ? "Edit certificate" : "New certificate"}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <div className="grid gap-1.5">
              <Label>Certificate name</Label>
              <Input dir="auto" value={form.cert_name} onChange={set("cert_name")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Platform</Label>
              <Input dir="auto" value={form.platform} onChange={set("platform")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Server name</Label>
              <Input
                dir="auto"
                value={form.server_name}
                onChange={set("server_name")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Target / VS</Label>
              <Input dir="auto" value={form.target} onChange={set("target")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Expires on</Label>
              <Input
                type="date"
                dir="ltr"
                value={form.expires_on}
                onChange={set("expires_on")}
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
            <DialogTitle>Delete certificate</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.cert_name}
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
