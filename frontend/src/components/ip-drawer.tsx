"use client";

import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type { ChangeLogEntry, IpAddress, IpRole, IpStatus } from "@/types";
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
const ROLES: (IpRole | "none")[] = ["none", "vip", "vrrp", "hsrp", "glbp", "carp", "secondary"];

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
    role: "none" as IpRole | "none",
    nat_inside: "",
    notes: "",
  });
  const [busy, setBusy] = useState(false);
  const [history, setHistory] = useState<ChangeLogEntry[]>([]);
  const [natOptions, setNatOptions] = useState<IpAddress[]>([]);

  useEffect(() => {
    setForm({
      hostname: addr?.hostname ?? "",
      mac_address: addr?.mac_address ?? "",
      status: addr?.status ?? "active",
      role: addr?.role ?? "none",
      nat_inside: "",
      notes: addr?.notes ?? "",
    });
    if (addr?.nat_inside_id) {
      api
        .get<IpAddress>(`/api/v1/addresses/${addr.nat_inside_id}`)
        .then((a) => setForm((f) => ({ ...f, nat_inside: a.address })))
        .catch(() => {});
    }
    api
      .get<IpAddress[]>(`/api/v1/addresses?prefix_id=${prefixId}&limit=2000`)
      .then(setNatOptions)
      .catch(() => setNatOptions([]));
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
      const natId = form.nat_inside
        ? natOptions.find((a) => a.address === form.nat_inside)?.id
        : null;
      if (form.nat_inside && natId == null) {
        toast.error("NAT inside address not found in this prefix");
        setBusy(false);
        return;
      }
      const body = {
        hostname: form.hostname || null,
        mac_address: form.mac_address || null,
        status: form.status,
        role: form.role === "none" ? null : form.role,
        nat_inside_id: natId,
        notes: form.notes || null,
      };
      if (addr) {
        await api.patch(`/api/v1/addresses/${addr.id}`, body);
      } else {
        await api.post("/api/v1/addresses", {
          address: ip,
          prefix_id: prefixId,
          ...body,
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
              {addr.device_type && <div>type: {addr.device_type}</div>}
              {!!addr.open_ports?.length && (
                <div>
                  open ports:{" "}
                  <span className="font-mono text-xs">{addr.open_ports.join("  ")}</span>
                </div>
              )}
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
          <div className="grid grid-cols-2 gap-3">
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
              <Label>Role</Label>
              <Select
                value={form.role}
                onValueChange={(v) => setForm({ ...form, role: v as IpRole | "none" })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ROLES.map((r) => (
                    <SelectItem key={r} value={r}>
                      {r}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label>NAT inside address</Label>
            <Input
              value={form.nat_inside}
              onChange={(e) => setForm({ ...form, nat_inside: e.target.value })}
              placeholder="e.g. 10.0.0.5 (must exist in this prefix)"
              className="font-mono"
              list="nat-candidates"
            />
            <datalist id="nat-candidates">
              {natOptions
                .filter((a) => a.id !== addr?.id)
                .map((a) => (
                  <option key={a.id} value={a.address} />
                ))}
            </datalist>
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
