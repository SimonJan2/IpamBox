"use client";

import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type { ChangeLogEntry, IpAddress, IpStatus } from "@/types";
import { IpStatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Input, Textarea } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

const STATUSES: IpStatus[] = ["active", "reserved", "dhcp", "discovered", "offline"];

export function IpDrawer({
  open,
  onOpenChange,
  ip,
  addr,
  prefixId,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  ip: string;
  addr: IpAddress | null;
  prefixId: number;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    hostname: "",
    mac_address: "",
    status: "active" as IpStatus,
    notes: "",
  });
  const [busy, setBusy] = useState(false);
  const [history, setHistory] = useState<ChangeLogEntry[]>([]);

  useEffect(() => {
    setForm({
      hostname: addr?.hostname ?? "",
      mac_address: addr?.mac_address ?? "",
      status: addr?.status ?? "active",
      notes: addr?.notes ?? "",
    });
    if (open && addr) {
      api
        .get<ChangeLogEntry[]>(
          `/api/v1/changelog?object_type=IPAddress&object_id=${addr.id}&limit=20`
        )
        .then(setHistory)
        .catch(() => setHistory([]));
    } else {
      setHistory([]);
    }
  }, [addr, open]);

  const save = async () => {
    setBusy(true);
    try {
      if (addr) {
        await api.patch(`/api/v1/addresses/${addr.id}`, {
          hostname: form.hostname || null,
          mac_address: form.mac_address || null,
          status: form.status,
          notes: form.notes || null,
        });
      } else {
        await api.post("/api/v1/addresses", {
          address: ip,
          prefix_id: prefixId,
          hostname: form.hostname || null,
          mac_address: form.mac_address || null,
          status: form.status,
          notes: form.notes || null,
        });
      }
      toast.success(addr ? "Address updated" : "Address reserved");
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const remove = async () => {
    if (!addr) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/addresses/${addr.id}`);
      toast.success("Address deleted");
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle className="font-mono">{ip}</SheetTitle>
          <SheetDescription>
            {addr ? (
              <span className="flex items-center gap-2">
                Current status <IpStatusBadge s={addr.status} />
              </span>
            ) : (
              "Free address — fill in to reserve it"
            )}
          </SheetDescription>
        </SheetHeader>

        <div className="grid gap-4">
          {addr && (
            <div className="rounded-md border p-3 text-sm text-muted-foreground space-y-1">
              {addr.vendor && <div>vendor: {addr.vendor}</div>}
              {addr.last_seen && (
                <div>last seen: {new Date(addr.last_seen).toLocaleString()}</div>
              )}
            </div>
          )}
          <div className="grid gap-1.5">
            <Label>Hostname</Label>
            <Input
              value={form.hostname}
              onChange={(e) => setForm({ ...form, hostname: e.target.value })}
              placeholder="host.lan"
            />
          </div>
          <div className="grid gap-1.5">
            <Label>MAC address</Label>
            <Input
              value={form.mac_address}
              onChange={(e) => setForm({ ...form, mac_address: e.target.value })}
              placeholder="AA:BB:CC:DD:EE:FF"
              className="font-mono"
            />
          </div>
          <div className="grid gap-1.5">
            <Label>Status</Label>
            <Select
              value={form.status}
              onValueChange={(v) => setForm({ ...form, status: v as IpStatus })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STATUSES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label>Notes</Label>
            <Textarea
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </div>
          <div className="flex gap-2 pt-2">
            <Button onClick={save} disabled={busy} className="flex-1">
              {busy ? "Saving…" : addr ? "Save" : "Reserve"}
            </Button>
            {addr && (
              <Button variant="destructive" size="icon" onClick={remove} disabled={busy}>
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>

          {history.length > 0 && (
            <div className="border-t pt-3">
              <div className="mb-2 text-xs font-medium text-muted-foreground">
                History
              </div>
              <div className="space-y-1.5 text-xs text-muted-foreground">
                {history.map((h) => (
                  <div key={h.id} className="flex items-baseline gap-2">
                    <span
                      className={
                        h.action === "create"
                          ? "text-emerald-400"
                          : h.action === "delete"
                            ? "text-rose-400"
                            : "text-amber-400"
                      }
                    >
                      {h.action}
                    </span>
                    <span className="flex-1 truncate">
                      {h.action === "update"
                        ? h.changes
                            .map((c) => c.field)
                            .slice(0, 3)
                            .join(", ")
                        : h.actor}
                    </span>
                    <span className="shrink-0">{timeAgo(h.ts)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
