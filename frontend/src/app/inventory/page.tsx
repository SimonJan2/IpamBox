"use client";

import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import type { Asset, AssetKind } from "@/types";
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
  kind: "hardware" as AssetKind,
  category: "",
  vendor: "",
  model: "",
  purpose: "",
  version: "",
  eol_on: "",
  support_status: "",
  serial_number: "",
  notes: "",
};

export default function InventoryPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [items, setItems] = useState<Asset[]>([]);
  const [q, setQ] = useState("");
  const [kindFilter, setKindFilter] = useState("all");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Asset | null>(null);
  const [deleting, setDeleting] = useState<Asset | null>(null);
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  const refresh = () => {
    api.get<Asset[]>("/api/v1/assets").then(setItems).catch(() => {});
  };
  useEffect(refresh, []);

  useEffect(() => {
    if (dialogOpen) {
      setForm(
        editing
          ? {
              kind: editing.kind,
              category: editing.category ?? "",
              vendor: editing.vendor ?? "",
              model: editing.model ?? "",
              purpose: editing.purpose ?? "",
              version: editing.version ?? "",
              eol_on: editing.eol_on ?? "",
              support_status: editing.support_status ?? "",
              serial_number: editing.serial_number ?? "",
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
        kind: form.kind,
        eol_on: form.eol_on || null,
      };
      if (editing) {
        await api.patch(`/api/v1/assets/${editing.id}`, body);
        toast.success("Asset updated");
      } else {
        await api.post("/api/v1/assets", body);
        toast.success("Asset added");
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
      await api.del(`/api/v1/assets/${deleting.id}`);
      toast.success("Asset deleted");
      setDeleting(null);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const filtered = items.filter((a) => {
    if (kindFilter !== "all" && a.kind !== kindFilter) return false;
    const s = q.toLowerCase();
    return [a.vendor, a.model, a.serial_number, a.purpose, a.category]
      .filter(Boolean)
      .some((v) => v!.toLowerCase().includes(s));
  });

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });

  const eolBadge = (eol: string | null) => {
    if (!eol) return null;
    const past = new Date(eol).getTime() < Date.now();
    return (
      <Badge
        variant="outline"
        className={
          past
            ? "border-rose-500/40 text-rose-400"
            : "border-amber-500/40 text-amber-400"
        }
      >
        {past ? "EOL" : `EOL ${eol}`}
      </Badge>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Inventory</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New asset
          </Button>
        )}
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="Search inventory…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <Select value={kindFilter} onValueChange={setKindFilter}>
          <SelectTrigger className="w-36">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All kinds</SelectItem>
            <SelectItem value="hardware">Hardware</SelectItem>
            <SelectItem value="software">Software</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Model</TableHead>
              <TableHead>Kind</TableHead>
              <TableHead>Vendor</TableHead>
              <TableHead>Serial</TableHead>
              <TableHead>Purpose</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>EOL</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((a) => (
              <TableRow key={a.id}>
                <TableCell dir="auto" className="font-medium">
                  {a.model ?? a.category ?? "—"}
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{a.kind}</Badge>
                </TableCell>
                <TableCell dir="auto" className="text-muted-foreground">
                  {a.vendor ?? "—"}
                </TableCell>
                <TableCell dir="ltr" className="font-mono text-muted-foreground">
                  {a.serial_number ?? "—"}
                </TableCell>
                <TableCell dir="auto" className="text-muted-foreground">
                  {a.purpose ?? "—"}
                </TableCell>
                <TableCell dir="ltr" className="font-mono text-muted-foreground">
                  {a.version ?? "—"}
                </TableCell>
                <TableCell>{eolBadge(a.eol_on)}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(a);
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
                        onClick={() => setDeleting(a)}
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
                  colSpan={8}
                  className="py-10 text-center text-muted-foreground"
                >
                  No assets found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit asset" : "New asset"}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Kind</Label>
              <Select
                value={form.kind}
                onValueChange={(v) => setForm({ ...form, kind: v as AssetKind })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hardware">Hardware</SelectItem>
                  <SelectItem value="software">Software</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Category</Label>
              <Input dir="auto" value={form.category} onChange={set("category")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Vendor</Label>
              <Input dir="auto" value={form.vendor} onChange={set("vendor")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Model</Label>
              <Input dir="auto" value={form.model} onChange={set("model")} />
            </div>
            <div className="grid gap-1.5">
              <Label>Serial number</Label>
              <Input
                dir="ltr"
                value={form.serial_number}
                onChange={set("serial_number")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Version</Label>
              <Input dir="ltr" value={form.version} onChange={set("version")} />
            </div>
            <div className="grid gap-1.5">
              <Label>EOL date</Label>
              <Input
                type="date"
                dir="ltr"
                value={form.eol_on}
                onChange={set("eol_on")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Support status</Label>
              <Input
                dir="auto"
                value={form.support_status}
                onChange={set("support_status")}
              />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Purpose</Label>
              <Input dir="auto" value={form.purpose} onChange={set("purpose")} />
            </div>
            <div className="col-span-2 grid gap-1.5">
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
            <DialogTitle>Delete asset</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.model ?? deleting?.serial_number}
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
