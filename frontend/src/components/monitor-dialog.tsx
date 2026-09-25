"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import type {
  Device,
  IpAddress,
  MonitorKind,
  MonitorTarget,
  Page,
} from "@/types";
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

export interface MonitorPrefill {
  device_id?: number;
  address_id?: number;
  /** Label shown in the locked anchor field when prefilled. */
  label?: string;
}

const KINDS: { value: MonitorKind; label: string; hint: string }[] = [
  { value: "ping", label: "Ping (ICMP)", hint: "echo reply = up" },
  { value: "tcp", label: "TCP port", hint: "connect succeeds = up" },
  { value: "http", label: "HTTP", hint: "GET matches expectation = up" },
];

export function MonitorDialog({
  open,
  onOpenChange,
  target,
  prefill,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  /** Edit mode when set. */
  target?: MonitorTarget | null;
  /** Lock the anchor to this device/address (device detail / IP drawer). */
  prefill?: MonitorPrefill | null;
  onSaved: () => void;
}) {
  const uid = useId();
  const [anchor, setAnchor] = useState<"device" | "address">("address");
  const [pick, setPick] = useState("");
  const [resolvedId, setResolvedId] = useState<number | null>(null);
  const [options, setOptions] = useState<{ id: number; label: string }[]>([]);
  const [form, setForm] = useState({
    kind: "ping" as MonitorKind,
    port: "",
    http_path: "/",
    http_expect: "",
    interval_seconds: 60,
    down_after: 2,
    enabled: true,
    notes: "",
  });
  const [busy, setBusy] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const lockedDevice = prefill?.device_id != null;
  const lockedAddress = prefill?.address_id != null;
  const locked = lockedDevice || lockedAddress;

  useEffect(() => {
    if (!open) return;
    if (target) {
      setAnchor(target.device_id != null ? "device" : "address");
      setPick(target.target_label ?? "");
      setResolvedId(target.device_id ?? target.address_id);
      setForm({
        kind: target.kind,
        port: target.port != null ? String(target.port) : "",
        http_path: target.http_path || "/",
        http_expect: target.http_expect ?? "",
        interval_seconds: target.interval_seconds,
        down_after: target.down_after,
        enabled: target.enabled,
        notes: target.notes ?? "",
      });
    } else {
      setAnchor(
        lockedDevice ? "device" : lockedAddress ? "address" : "address"
      );
      setPick(prefill?.label ?? "");
      setResolvedId(prefill?.device_id ?? prefill?.address_id ?? null);
      setOptions([]);
      setForm({
        kind: "ping",
        port: "",
        http_path: "/",
        http_expect: "",
        interval_seconds: 60,
        down_after: 2,
        enabled: true,
        notes: "",
      });
    }
  }, [open, target, prefill, lockedDevice, lockedAddress]);

  const fetchOptions = useCallback(
    async (q: string) => {
      try {
        if (anchor === "device") {
          const p = await api.get<Page<Device>>(
            `/api/v1/devices?limit=25${q ? `&q=${encodeURIComponent(q)}` : ""}`
          );
          setOptions(
            p.items.map((d) => ({ id: d.id, label: d.name ?? `#${d.id}` }))
          );
        } else {
          const rows = await api.get<IpAddress[]>(
            `/api/v1/addresses?limit=25${q ? `&q=${encodeURIComponent(q)}` : ""}`
          );
          setOptions(
            rows.map((a) => ({
              id: a.id,
              label: a.hostname ? `${a.address} — ${a.hostname}` : a.address,
            }))
          );
        }
      } catch {
        setOptions([]);
      }
    },
    [anchor]
  );

  const onPick = (v: string) => {
    setPick(v);
    setResolvedId(null);
    const hit = options.find(
      (o) => o.label === v || o.label.startsWith(`${v} `) || o.label === v
    );
    if (hit) setResolvedId(hit.id);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => void fetchOptions(v), 250);
  };

  const needsPort = form.kind !== "ping";
  const isHttp = form.kind === "http";

  const submit = async () => {
    const body: Record<string, unknown> = {
      kind: form.kind,
      interval_seconds: form.interval_seconds,
      down_after: form.down_after,
      enabled: form.enabled,
      notes: form.notes || null,
      port: needsPort && form.port ? Number(form.port) : null,
      http_path: isHttp ? form.http_path || "/" : "/",
      http_expect: isHttp && form.http_expect ? form.http_expect : null,
    };
    if (lockedDevice) body.device_id = prefill!.device_id;
    else if (lockedAddress) body.address_id = prefill!.address_id;
    else if (anchor === "device") body.device_id = resolvedId;
    else body.address_id = resolvedId;
    if (!target && body.device_id == null && body.address_id == null) {
      toast.error("Pick a device or an IP address to monitor");
      return;
    }
    if (needsPort && body.port == null) {
      toast.error(`port is required for ${form.kind} checks`);
      return;
    }
    setBusy(true);
    try {
      if (target) {
        await api.patch(`/api/v1/monitor-targets/${target.id}`, body);
        toast.success("Monitor updated");
      } else {
        await api.post("/api/v1/monitor-targets", body);
        toast.success("Monitor created");
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
          <DialogTitle>
            {target ? "Edit monitor" : "New monitor"}
          </DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label id={`${uid}-anchor`}>Target</Label>
            {locked ? (
              <Input
                value={prefill?.label ?? pick}
                disabled
                dir="auto"
                aria-label="Target"
              />
            ) : (
              <div className="flex gap-2">
                <Select
                  value={anchor}
                  onValueChange={(v) => {
                    setAnchor(v as "device" | "address");
                    setPick("");
                    setResolvedId(null);
                    setOptions([]);
                  }}
                >
                  <SelectTrigger className="w-28" aria-label="Target type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="address">IP address</SelectItem>
                    <SelectItem value="device">Device</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  value={pick}
                  onChange={(e) => onPick(e.target.value)}
                  onFocus={() => void fetchOptions("")}
                  placeholder={
                    anchor === "device"
                      ? "Search devices…"
                      : "Search IP addresses…"
                  }
                  className="font-mono text-sm"
                  list={`${uid}-candidates`}
                  aria-label="Target"
                />
                <datalist id={`${uid}-candidates`}>
                  {options.map((o) => (
                    <option key={o.id} value={o.label} />
                  ))}
                </datalist>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label id={`${uid}-kind`}>Check kind</Label>
              <Select
                value={form.kind}
                onValueChange={(v) =>
                  setForm({ ...form, kind: v as MonitorKind })
                }
              >
                <SelectTrigger aria-label="Check kind">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {KINDS.map((k) => (
                    <SelectItem key={k.value} value={k.value}>
                      {k.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {needsPort && (
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-port`}>Port</Label>
                <Input
                  id={`${uid}-port`}
                  type="number"
                  min={1}
                  max={65535}
                  value={form.port}
                  onChange={(e) => setForm({ ...form, port: e.target.value })}
                  placeholder={isHttp ? "80" : "443"}
                />
              </div>
            )}
          </div>

          {isHttp && (
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-path`}>HTTP path</Label>
                <Input
                  id={`${uid}-path`}
                  dir="ltr"
                  className="font-mono text-sm"
                  placeholder="/healthz"
                  value={form.http_path}
                  onChange={(e) =>
                    setForm({ ...form, http_path: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-expect`}>Expect</Label>
                <Input
                  id={`${uid}-expect`}
                  dir="ltr"
                  className="font-mono text-sm"
                  placeholder="status:200 or body text"
                  value={form.http_expect}
                  onChange={(e) =>
                    setForm({ ...form, http_expect: e.target.value })
                  }
                />
              </div>
            </div>
          )}

          <div className="grid grid-cols-3 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-interval`}>Interval (s)</Label>
              <Input
                id={`${uid}-interval`}
                type="number"
                min={5}
                max={86400}
                value={form.interval_seconds}
                onChange={(e) =>
                  setForm({
                    ...form,
                    interval_seconds: Number(e.target.value) || 60,
                  })
                }
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-downafter`}>Down after</Label>
              <Input
                id={`${uid}-downafter`}
                type="number"
                min={1}
                max={100}
                value={form.down_after}
                onChange={(e) =>
                  setForm({
                    ...form,
                    down_after: Number(e.target.value) || 1,
                  })
                }
              />
            </div>
            <div className="grid gap-1.5">
              <Label id={`${uid}-enabled`}>Enabled</Label>
              <Switch
                aria-label="Enabled"
                checked={form.enabled}
                onCheckedChange={(v) => setForm({ ...form, enabled: v })}
              />
            </div>
          </div>

          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-notes`}>Notes</Label>
            <Input
              id={`${uid}-notes`}
              dir="auto"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy}>
            {busy ? "Saving…" : target ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
