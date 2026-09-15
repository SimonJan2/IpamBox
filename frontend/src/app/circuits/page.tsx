"use client";

import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const EMPTY = {
  env: "",
  site_name: "",
  site_code: "",
  line_type: "",
  bezeq_circuit_id: "",
  node: "",
  bw_down: "",
  bw_up: "",
  wan_ip: "",
  status: "",
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
              site_name: circuit.site_name ?? "",
              site_code: circuit.site_code ?? "",
              line_type: circuit.line_type ?? "",
              bezeq_circuit_id: circuit.bezeq_circuit_id ?? "",
              node: circuit.node ?? "",
              bw_down: circuit.bw_down ?? "",
              bw_up: circuit.bw_up ?? "",
              wan_ip: circuit.wan_ip ?? "",
              status: circuit.status ?? "",
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
        Object.entries(form).map(([k, v]) => [k, v || null])
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
    ["site_name", "Site name"],
    ["site_code", "Site code"],
    ["line_type", "Line type"],
    ["bezeq_circuit_id", "Bezeq circuit ID"],
    ["node", "Node"],
    ["bw_down", "BW down"],
    ["bw_up", "BW up"],
    ["wan_ip", "WAN IP"],
    ["status", "Status"],
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
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Circuit | null>(null);
  const [deleting, setDeleting] = useState<Circuit | null>(null);

  const refresh = () => {
    api.get<Circuit[]>("/api/v1/circuits").then(setItems).catch(() => {});
  };
  useEffect(refresh, []);

  const filtered = items.filter((c) => {
    const s = q.toLowerCase();
    return [c.site_name, c.site_code, c.bezeq_circuit_id, c.node, c.line_type]
      .filter(Boolean)
      .some((v) => v!.toLowerCase().includes(s));
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

      <Input
        placeholder="Search circuits…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="max-w-xs"
      />

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Site</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Bezeq ID</TableHead>
              <TableHead>Node</TableHead>
              <TableHead>BW ↓/↑</TableHead>
              <TableHead>WAN IP</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((c) => (
              <TableRow key={c.id}>
                <TableCell dir="auto" className="font-medium">
                  {c.site_name ?? "—"}
                  {c.site_code && (
                    <span className="ml-1 text-xs text-muted-foreground">
                      {c.site_code}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  {c.line_type && <Badge variant="outline">{c.line_type}</Badge>}
                </TableCell>
                <TableCell dir="ltr" className="font-mono text-muted-foreground">
                  {c.bezeq_circuit_id ?? "—"}
                </TableCell>
                <TableCell dir="auto" className="text-muted-foreground">
                  {c.node ?? "—"}
                </TableCell>
                <TableCell dir="ltr" className="font-mono text-muted-foreground">
                  {c.bw_down || c.bw_up
                    ? `${c.bw_down ?? "?"}/${c.bw_up ?? "?"}`
                    : "—"}
                </TableCell>
                <TableCell dir="ltr" className="font-mono text-muted-foreground">
                  {c.wan_ip ?? "—"}
                </TableCell>
                <TableCell dir="auto" className="text-muted-foreground">
                  {c.status ?? "—"}
                </TableCell>
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
                  colSpan={8}
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
