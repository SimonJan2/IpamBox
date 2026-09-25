"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import Link from "next/link";
import {
  Cable as CableIcon,
  Pencil,
  Plus,
  Route,
  Trash2,
  TriangleAlert,
  Wand2,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { useSetting } from "@/lib/features";
import { cn, timeAgo } from "@/lib/utils";
import type {
  Cable,
  CableKind,
  CableTraceHop,
  Device,
  DeviceDetail,
  DeviceInterface,
  InterfaceKind,
  Page,
} from "@/types";
import { AsyncPanel } from "@/components/async-panel";
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
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const IFACE_KINDS: InterfaceKind[] = [
  "rj45",
  "sfp",
  "sfp28",
  "qsfp",
  "console",
  "patch",
  "power",
  "other",
];
const CABLE_KINDS: CableKind[] = [
  "cat5e",
  "cat6",
  "cat6a",
  "dac",
  "fiber_sm",
  "fiber_mm",
  "power",
  "console",
  "other",
];

const fmtSpeed = (mbps: number | null) =>
  mbps == null ? null : mbps >= 1000 ? `${mbps / 1000}G` : `${mbps}M`;

/** SNMP oper_status → status-token chip classes (up≈active, down≈offline). */
const OPER_CLASS: Record<string, string> = {
  up: "border-emerald-700/60 bg-emerald-950/40 text-emerald-300",
  down: "border-rose-700/60 bg-rose-950/40 text-rose-300",
  testing: "border-amber-700/60 bg-amber-950/40 text-amber-300",
  dormant: "border-amber-700/60 bg-amber-950/40 text-amber-300",
};
const operBadgeClass = (s: string | null) =>
  s ? (OPER_CLASS[s] ?? "border-border bg-muted/40 text-muted-foreground") : "";

/** V8.2 cable_mismatch reason → human label (mirrors the backend's
 *  REASON_LABELS — the flag's `detail` rides in the tooltip). */
const FLAG_REASON: Record<string, string> = {
  documented_down: "cabled but port reports down",
  far_end_absent: "peer MACs not learned on this port",
  lldp_neighbor: "LLDP neighbor on uncabled port",
};

/** An SNMP-owned port goes dim when the device stopped reporting it — its
 *  snmp_seen_at falls behind ~2 poll intervals (the port may have been
 *  renamed/removed on the device; we never delete it, just dim). */
function snmpStale(iface: DeviceInterface, intervalMin: number): boolean {
  if (iface.source !== "snmp") return false;
  if (!iface.snmp_seen_at) return true;
  return (
    Date.now() - new Date(iface.snmp_seen_at).getTime() >
    Math.max(intervalMin, 1) * 2 * 60_000
  );
}

/** Device picker backed by /devices?q= — text input + datalist, the same
 *  pattern the IP drawer uses. Resolves a device id from the typed name. */
function useDevicePick() {
  const [devId, setDevId] = useState<number | null>(null);
  const [devText, setDevText] = useState("");
  const [devOptions, setDevOptions] = useState<Device[]>([]);
  const touched = useRef(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchDevs = useCallback(async (q: string) => {
    try {
      const p = await api.get<Page<Device>>(
        `/api/v1/devices?limit=25${q ? `&q=${encodeURIComponent(q)}` : ""}`
      );
      setDevOptions(p.items);
    } catch {
      setDevOptions([]);
    }
  }, []);

  const schedule = (q: string) => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => void fetchDevs(q), 250);
  };

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current);
    },
    []
  );

  const onText = (v: string) => {
    setDevText(v);
    setDevId(devOptions.find((d) => d.name === v)?.id ?? null);
    schedule(v);
  };

  const onFocus = () => {
    if (!touched.current) {
      touched.current = true;
      void fetchDevs(devText);
    }
  };

  const reset = (text = "", id: number | null = null) => {
    setDevText(text);
    setDevId(id);
    setDevOptions([]);
    touched.current = false;
  };

  return { devId, devText, devOptions, onText, onFocus, reset, setDevId };
}

export function InterfacesPanel({ device }: { device: DeviceDetail }) {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const ifaces = useAsyncData<DeviceInterface[]>(
    () => api.get(`/api/v1/devices/${device.id}/interfaces`),
    [device.id]
  );
  const [genOpen, setGenOpen] = useState(false);
  const [addOpen, setAddOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<DeviceInterface | null>(null);
  const [cableFor, setCableFor] = useState<DeviceInterface | null>(null);
  const [traceFor, setTraceFor] = useState<DeviceInterface | null>(null);
  const [busy, setBusy] = useState<number | null>(null);
  const snmpInterval = useSetting("snmp_interval_minutes") ?? 60;

  const rows = ifaces.data ?? [];
  const byId = new Map(rows.map((i) => [i.id, i]));
  const flaggedCount = rows.filter((i) => i.validation?.cable_mismatch).length;
  const reload = () => void ifaces.reload();

  // Review's "open trace" lands here as /devices/{id}?trace={iface_id} —
  // read once (client-side URL, no Suspense needed) and honor once.
  const traceParamSeen = useRef(false);
  useEffect(() => {
    if (traceParamSeen.current || ifaces.data == null) return;
    const tid = new URLSearchParams(window.location.search).get("trace");
    if (!tid) return;
    traceParamSeen.current = true;
    const hit = ifaces.data.find((i) => i.id === Number(tid));
    if (hit) setTraceFor(hit);
  }, [ifaces.data]);

  const del = async (i: DeviceInterface) => {
    setBusy(i.id);
    try {
      await api.del(`/api/v1/devices/${device.id}/interfaces/${i.id}`);
      toast.success(`Port ${i.name} deleted`);
      reload();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="rounded-lg border">
      <div className="flex items-center justify-between border-b px-3 py-2">
        <span className="text-sm font-medium">
          Interfaces
          <span className="ml-2 text-xs font-normal text-muted-foreground">
            {rows.length ? `${device.cabled_count}/${rows.length} cabled` : "no ports yet"}
          </span>
          {flaggedCount > 0 && (
            <span
              className="ml-2 inline-flex items-center gap-0.5 text-xs font-normal text-amber-400"
              title={`${flaggedCount} port(s) carrying a cable_mismatch flag`}
            >
              <TriangleAlert className="h-3 w-3" />
              {flaggedCount} flagged
            </span>
          )}
        </span>
        {canWrite && (
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setGenOpen(true)}
              aria-label="Generate ports"
            >
              <Wand2 className="h-3.5 w-3.5" /> Generate
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setAddOpen(true)}
              aria-label="Add port"
            >
              <Plus className="h-3.5 w-3.5" /> Add port
            </Button>
          </div>
        )}
      </div>
      <AsyncPanel
        loading={ifaces.loading}
        error={ifaces.error}
        onRetry={ifaces.reload}
        empty={rows.length === 0}
        emptyMessage="No interfaces — generate a port set or add ports one by one."
      >
        <TooltipProvider>
          <div className="grid grid-cols-2 gap-2 p-3 sm:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6">
            {rows.map((i) => {
              const pair =
                i.pair_interface_id != null
                  ? byId.get(i.pair_interface_id)
                  : undefined;
              const cabled = i.peer != null;
              const stale = snmpStale(i, snmpInterval);
              return (
                <div
                  key={i.id}
                  className={cn(
                    "group relative rounded-md border px-2 py-1.5 text-xs",
                    cabled
                      ? "border-emerald-700/60 bg-emerald-950/30"
                      : "border-border bg-card",
                    stale && "opacity-50"
                  )}
                >
                  <div className="flex items-center justify-between gap-1">
                    <button
                      type="button"
                      className={cn(
                        "min-w-0 truncate font-mono font-medium",
                        cabled && "cursor-pointer text-emerald-300 hover:underline"
                      )}
                      onClick={() => cabled && setTraceFor(i)}
                      title={
                        i.peer
                          ? `${i.peer.device_name} · ${i.peer.interface_name}` +
                            (i.peer.cable_label ? ` — ${i.peer.cable_label}` : "")
                          : undefined
                      }
                    >
                      {i.name}
                    </button>
                    <span className="flex shrink-0 items-center gap-0.5">
                      {i.validation?.cable_mismatch && (
                        <Badge
                          variant="outline"
                          className="border-amber-700/60 bg-amber-950/40 px-1 py-0 text-[10px] text-amber-300"
                          title={
                            (FLAG_REASON[i.validation.cable_mismatch.reason] ??
                              i.validation.cable_mismatch.reason) +
                            (i.validation.cable_mismatch.detail
                              ? ` — ${i.validation.cable_mismatch.detail}`
                              : "")
                          }
                        >
                          <TriangleAlert className="h-2.5 w-2.5" />
                        </Badge>
                      )}
                      {i.oper_status && (
                        <Badge
                          variant="outline"
                          className={cn(
                            "px-1 py-0 text-[10px]",
                            operBadgeClass(i.oper_status),
                            stale && "opacity-70"
                          )}
                          title={
                            `oper ${i.oper_status}` +
                            (i.admin_status ? ` · admin ${i.admin_status}` : "") +
                            (i.snmp_seen_at
                              ? ` · seen ${timeAgo(i.snmp_seen_at)}`
                              : "")
                          }
                        >
                          {i.oper_status}
                        </Badge>
                      )}
                      {i.source === "snmp" && (
                        <Badge
                          variant="outline"
                          className="px-1 py-0 text-[10px] text-sky-300/80"
                          title="Discovered by SNMP polling"
                        >
                          snmp
                        </Badge>
                      )}
                      <Badge variant="outline" className="px-1 py-0 text-[10px]">
                        {i.kind}
                      </Badge>
                    </span>
                  </div>
                  <div className="mt-0.5 flex items-center gap-1.5 text-[10px] text-muted-foreground">
                    {fmtSpeed(i.speed_mbps) && <span dir="ltr">{fmtSpeed(i.speed_mbps)}</span>}
                    {i.mac_address && <span dir="ltr" className="truncate font-mono">{i.mac_address}</span>}
                    {pair && <span title={`paired with ${pair.name}`}>↔{pair.name}</span>}
                    {i.connected_ip && (
                      <Link
                        href={`/prefixes/${i.connected_ip.prefix_id}?q=${encodeURIComponent(i.connected_ip.label.split(" ")[0])}`}
                        className="truncate text-emerald-400/80 hover:underline"
                        dir="ltr"
                      >
                        {i.connected_ip.label}
                      </Link>
                    )}
                  </div>
                  <div className="mt-1 flex items-center gap-0.5">
                    {cabled ? (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <button
                            type="button"
                            className="flex min-w-0 items-center gap-1 text-[10px] text-emerald-400 hover:underline"
                            onClick={() => setTraceFor(i)}
                          >
                            <Route className="h-3 w-3 shrink-0" />
                            <span className="truncate" dir="auto">
                              {i.peer!.device_name} · {i.peer!.interface_name}
                            </span>
                          </button>
                        </TooltipTrigger>
                        <TooltipContent>
                          {i.peer!.cable_kind}
                          {i.peer!.cable_label ? ` · ${i.peer!.cable_label}` : ""}
                          {" — trace path"}
                        </TooltipContent>
                      </Tooltip>
                    ) : (
                      canWrite && (
                        <button
                          type="button"
                          className="flex items-center gap-1 text-[10px] text-muted-foreground hover:text-emerald-400"
                          onClick={() => setCableFor(i)}
                        >
                          <CableIcon className="h-3 w-3" /> cable
                        </button>
                      )
                    )}
                    <span className="ml-auto flex gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
                      {canWrite && (
                        <button
                          type="button"
                          aria-label={`Edit ${i.name}`}
                          className="text-muted-foreground hover:text-foreground"
                          onClick={() => setEditTarget(i)}
                        >
                          <Pencil className="h-3 w-3" />
                        </button>
                      )}
                      {canDelete && (
                        <button
                          type="button"
                          aria-label={`Delete ${i.name}`}
                          className="text-muted-foreground hover:text-rose-400"
                          disabled={busy === i.id}
                          onClick={() => void del(i)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      )}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </TooltipProvider>
      </AsyncPanel>

      <GenerateDialog
        deviceId={device.id}
        open={genOpen}
        onOpenChange={setGenOpen}
        onDone={reload}
      />
      <PortDialog
        device={device}
        open={addOpen}
        onOpenChange={setAddOpen}
        onDone={reload}
      />
      <PortDialog
        device={device}
        iface={editTarget ?? undefined}
        open={editTarget != null}
        onOpenChange={(o) => !o && setEditTarget(null)}
        onDone={reload}
      />
      <CableDialog
        device={device}
        local={cableFor}
        onOpenChange={(o) => !o && setCableFor(null)}
        onDone={reload}
      />
      <TraceSheet
        iface={traceFor}
        onOpenChange={(o) => !o && setTraceFor(null)}
      />
    </div>
  );
}

// --------------------------------------------------------------------------
// Generate ports — one-click port factory (switch 48x / panel front+back).
// --------------------------------------------------------------------------

function GenerateDialog({
  deviceId,
  open,
  onOpenChange,
  onDone,
}: {
  deviceId: number;
  open: boolean;
  onOpenChange: (o: boolean) => void;
  onDone: () => void;
}) {
  const uid = useId();
  const [form, setForm] = useState({
    kind: "rj45" as InterfaceKind,
    prefix: "Gi1/0/",
    count: 48,
    start_index: 1,
    speed_mbps: "",
    pair_prefix: "",
  });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (open)
      setForm({
        kind: "rj45",
        prefix: "Gi1/0/",
        count: 48,
        start_index: 1,
        speed_mbps: "",
        pair_prefix: "",
      });
  }, [open]);

  const submit = async () => {
    setBusy(true);
    try {
      const created = await api.post<DeviceInterface[]>(
        `/api/v1/devices/${deviceId}/interfaces/generate`,
        {
          kind: form.kind,
          prefix: form.prefix,
          count: form.count,
          start_index: form.start_index,
          speed_mbps: form.speed_mbps ? Number(form.speed_mbps) : null,
          pair_prefix: form.pair_prefix || null,
        }
      );
      toast.success(
        `${created.length} port${created.length === 1 ? "" : "s"} generated` +
          (form.pair_prefix ? " (paired front+back)" : "")
      );
      onOpenChange(false);
      onDone();
    } catch (e) {
      toast.error("Generate failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Generate ports</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-kind`}>Kind</Label>
              <Select
                value={form.kind}
                onValueChange={(v) =>
                  setForm({ ...form, kind: v as InterfaceKind })
                }
              >
                <SelectTrigger id={`${uid}-kind`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {IFACE_KINDS.map((k) => (
                    <SelectItem key={k} value={k}>
                      {k}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-speed`}>Speed (Mbps)</Label>
              <Input
                id={`${uid}-speed`}
                dir="ltr"
                inputMode="numeric"
                value={form.speed_mbps}
                onChange={(e) =>
                  setForm({ ...form, speed_mbps: e.target.value })
                }
                placeholder="e.g. 1000"
              />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-prefix`}>Name prefix</Label>
            <Input
              id={`${uid}-prefix`}
              dir="ltr"
              className="font-mono"
              value={form.prefix}
              onChange={(e) => setForm({ ...form, prefix: e.target.value })}
              placeholder="Gi1/0/ or p"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-count`}>Count</Label>
              <Input
                id={`${uid}-count`}
                dir="ltr"
                type="number"
                min={1}
                max={256}
                value={form.count}
                onChange={(e) =>
                  setForm({ ...form, count: Number(e.target.value) || 1 })
                }
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-start`}>Start index</Label>
              <Input
                id={`${uid}-start`}
                dir="ltr"
                type="number"
                min={0}
                value={form.start_index}
                onChange={(e) =>
                  setForm({ ...form, start_index: Number(e.target.value) || 0 })
                }
              />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-pair`}>
              Pair prefix{" "}
              <span className="text-muted-foreground">
                (patch panels — creates a paired back port per front)
              </span>
            </Label>
            <Input
              id={`${uid}-pair`}
              dir="ltr"
              className="font-mono"
              value={form.pair_prefix}
              onChange={(e) =>
                setForm({ ...form, pair_prefix: e.target.value })
              }
              placeholder="e.g. b → p1↔b1"
            />
          </div>
          <p className="text-xs text-muted-foreground" dir="ltr">
            Preview: {form.prefix}
            {form.start_index}…{form.prefix}
            {form.start_index + form.count - 1}
            {form.pair_prefix
              ? ` + ${form.pair_prefix}${form.start_index}…${form.pair_prefix}${
                  form.start_index + form.count - 1
                }`
              : ""}
          </p>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={busy || !form.prefix.trim()}>
            {busy ? "Generating…" : "Generate"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// --------------------------------------------------------------------------
// Add / edit a single port.
// --------------------------------------------------------------------------

function PortDialog({
  device,
  iface,
  open,
  onOpenChange,
  onDone,
}: {
  device: DeviceDetail;
  iface?: DeviceInterface;
  open: boolean;
  onOpenChange: (o: boolean) => void;
  onDone: () => void;
}) {
  const uid = useId();
  const editing = iface != null;
  const [form, setForm] = useState({
    name: "",
    kind: "rj45" as InterfaceKind,
    speed_mbps: "",
    mac_address: "",
    pair: "none",
  });
  const [siblings, setSiblings] = useState<DeviceInterface[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return;
    setForm({
      name: iface?.name ?? "",
      kind: iface?.kind ?? "rj45",
      speed_mbps: iface?.speed_mbps ? String(iface.speed_mbps) : "",
      mac_address: iface?.mac_address ?? "",
      pair: iface?.pair_interface_id ? String(iface.pair_interface_id) : "none",
    });
    if (editing) {
      api
        .get<DeviceInterface[]>(`/api/v1/devices/${device.id}/interfaces`)
        .then(setSiblings)
        .catch(() => setSiblings([]));
    }
  }, [open, iface, editing, device.id]);

  const submit = async () => {
    setBusy(true);
    const body = {
      name: form.name,
      kind: form.kind,
      speed_mbps: form.speed_mbps ? Number(form.speed_mbps) : null,
      mac_address: form.mac_address || null,
      ...(editing
        ? { pair_interface_id: form.pair === "none" ? null : Number(form.pair) }
        : {}),
    };
    try {
      if (editing) {
        await api.patch(
          `/api/v1/devices/${device.id}/interfaces/${iface.id}`,
          body
        );
        toast.success(`Port ${form.name} updated`);
      } else {
        await api.post(`/api/v1/devices/${device.id}/interfaces`, body);
        toast.success(`Port ${form.name} added`);
      }
      onOpenChange(false);
      onDone();
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
          <DialogTitle>{editing ? `Edit ${iface.name}` : "Add port"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-name`}>Name</Label>
              <Input
                id={`${uid}-name`}
                dir="ltr"
                className="font-mono"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="eth0 / Gi1/0/12 / p7"
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-kind`}>Kind</Label>
              <Select
                value={form.kind}
                onValueChange={(v) =>
                  setForm({ ...form, kind: v as InterfaceKind })
                }
              >
                <SelectTrigger id={`${uid}-kind`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {IFACE_KINDS.map((k) => (
                    <SelectItem key={k} value={k}>
                      {k}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-speed`}>Speed (Mbps)</Label>
              <Input
                id={`${uid}-speed`}
                dir="ltr"
                inputMode="numeric"
                value={form.speed_mbps}
                onChange={(e) =>
                  setForm({ ...form, speed_mbps: e.target.value })
                }
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-mac`}>MAC</Label>
              <Input
                id={`${uid}-mac`}
                dir="ltr"
                className="font-mono"
                value={form.mac_address}
                onChange={(e) =>
                  setForm({ ...form, mac_address: e.target.value })
                }
              />
            </div>
          </div>
          {editing && (
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-pair`}>
                Paired port{" "}
                <span className="text-muted-foreground">
                  (patch-panel front↔back)
                </span>
              </Label>
              <Select
                value={form.pair}
                onValueChange={(v) => setForm({ ...form, pair: v })}
              >
                <SelectTrigger id={`${uid}-pair`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">none</SelectItem>
                  {siblings
                    .filter(
                      (s) =>
                        s.id !== iface.id &&
                        (s.pair_interface_id == null ||
                          s.pair_interface_id === iface.id)
                    )
                    .map((s) => (
                      <SelectItem key={s.id} value={String(s.id)}>
                        {s.name}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={busy || !form.name.trim()}>
            {busy ? "Saving…" : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// --------------------------------------------------------------------------
// Cable dialog — pick a peer device's free port, then kind/color/label.
// --------------------------------------------------------------------------

function CableDialog({
  device,
  local,
  onOpenChange,
  onDone,
}: {
  device: DeviceDetail;
  local: DeviceInterface | null;
  onOpenChange: (o: boolean) => void;
  onDone: () => void;
}) {
  const uid = useId();
  const pick = useDevicePick();
  const [peerIfaces, setPeerIfaces] = useState<DeviceInterface[]>([]);
  const [peerIfaceId, setPeerIfaceId] = useState("");
  const [form, setForm] = useState({
    kind: "cat6" as CableKind,
    color: "",
    label: "",
    length_m: "",
  });
  const [busy, setBusy] = useState(false);
  const open = local != null;

  useEffect(() => {
    if (!open) return;
    pick.reset();
    setPeerIfaces([]);
    setPeerIfaceId("");
    setForm({ kind: "cat6", color: "", label: "", length_m: "" });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  useEffect(() => {
    setPeerIfaceId("");
    setPeerIfaces([]);
    if (pick.devId == null) return;
    api
      .get<DeviceInterface[]>(`/api/v1/devices/${pick.devId}/interfaces`)
      .then(setPeerIfaces)
      .catch(() => setPeerIfaces([]));
  }, [pick.devId]);

  const freePeers = peerIfaces.filter((i) => i.peer == null);

  const submit = async () => {
    if (!local || !peerIfaceId) return;
    setBusy(true);
    try {
      await api.post<Cable>("/api/v1/cables", {
        a_interface_id: local.id,
        b_interface_id: Number(peerIfaceId),
        kind: form.kind,
        color: form.color || null,
        label: form.label || null,
        length_m: form.length_m ? Number(form.length_m) : null,
      });
      toast.success(`Cable connected to ${local.name}`);
      onOpenChange(false);
      onDone();
    } catch (e) {
      toast.error("Cable failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Cable from {device.name} · {local?.name}
          </DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-peer`}>Peer device</Label>
            <Input
              id={`${uid}-peer`}
              dir="auto"
              value={pick.devText}
              onChange={(e) => pick.onText(e.target.value)}
              onFocus={pick.onFocus}
              placeholder="search devices…"
              list={`${uid}-peer-list`}
            />
            <datalist id={`${uid}-peer-list`}>
              {pick.devOptions
                .filter((d) => d.id !== device.id)
                .map((d) => (
                  <option key={d.id} value={d.name} />
                ))}
            </datalist>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-port`}>Peer interface</Label>
            <Select value={peerIfaceId} onValueChange={setPeerIfaceId}>
              <SelectTrigger id={`${uid}-port`}>
                <SelectValue
                  placeholder={
                    pick.devId == null
                      ? "pick a device first"
                      : freePeers.length
                        ? "pick a free port"
                        : "no free ports on this device"
                  }
                />
              </SelectTrigger>
              <SelectContent>
                {freePeers.map((i) => (
                  <SelectItem key={i.id} value={String(i.id)}>
                    {i.name}
                    {i.kind !== "rj45" ? ` · ${i.kind}` : ""}
                    {i.speed_mbps ? ` · ${fmtSpeed(i.speed_mbps)}` : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-kind`}>Cable kind</Label>
              <Select
                value={form.kind}
                onValueChange={(v) => setForm({ ...form, kind: v as CableKind })}
              >
                <SelectTrigger id={`${uid}-kind`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CABLE_KINDS.map((k) => (
                    <SelectItem key={k} value={k}>
                      {k}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-color`}>Color</Label>
              <Input
                id={`${uid}-color`}
                dir="auto"
                value={form.color}
                onChange={(e) => setForm({ ...form, color: e.target.value })}
                placeholder="yellow"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-label`}>Label</Label>
              <Input
                id={`${uid}-label`}
                dir="auto"
                value={form.label}
                onChange={(e) => setForm({ ...form, label: e.target.value })}
                placeholder="physical tag / collar id"
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-len`}>Length (m)</Label>
              <Input
                id={`${uid}-len`}
                dir="ltr"
                inputMode="decimal"
                value={form.length_m}
                onChange={(e) => setForm({ ...form, length_m: e.target.value })}
              />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={busy || !peerIfaceId}>
            {busy ? "Connecting…" : "Connect"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// --------------------------------------------------------------------------
// Trace drawer — the ordered L1 path through this interface.
// --------------------------------------------------------------------------

function TraceSheet({
  iface,
  onOpenChange,
}: {
  iface: DeviceInterface | null;
  onOpenChange: (o: boolean) => void;
}) {
  const open = iface != null;
  const [hops, setHops] = useState<CableTraceHop[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !iface) return;
    setHops(null);
    setError(null);
    api
      .get<CableTraceHop[]>(`/api/v1/cables/trace?interface_id=${iface.id}`)
      .then(setHops)
      .catch((e) => setError(String(e)));
  }, [open, iface]);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle className="font-mono">
            Trace — {iface?.name}
          </SheetTitle>
          <SheetDescription>
            L1 path through this interface, end to end.
          </SheetDescription>
        </SheetHeader>
        <div className="grid gap-0 pt-2">
          {error && <p className="text-sm text-rose-400">{error}</p>}
          {hops == null && !error && (
            <p className="text-sm text-muted-foreground">Tracing…</p>
          )}
          {hops?.map((h, idx) => (
            <div key={`${h.interface_id}-${idx}`}>
              {idx > 0 && (
                <div className="my-1 flex items-center gap-2 pl-3 text-[11px] text-muted-foreground">
                  <span className="h-4 w-px bg-border" />
                  {h.cable_id != null ? (
                    <span dir="ltr">
                      ├ {h.cable_kind}
                      {h.cable_label ? ` · ${h.cable_label}` : ""}
                    </span>
                  ) : (
                    <span>├ panel pass-through</span>
                  )}
                </div>
              )}
              <div
                className={cn(
                  "flex items-center gap-2 rounded-md border px-2.5 py-1.5 text-sm",
                  h.interface_id === iface?.id
                    ? "border-emerald-700/60 bg-emerald-950/30"
                    : "bg-card"
                )}
              >
                <Link
                  href={`/devices/${h.device_id}`}
                  className="min-w-0 truncate text-emerald-400 hover:underline"
                  dir="auto"
                >
                  {h.device_name}
                </Link>
                <span className="truncate font-mono text-muted-foreground" dir="ltr">
                  · {h.interface_name}
                </span>
              </div>
            </div>
          ))}
          {hops != null && hops.length === 1 && (
            <p className="pt-2 text-sm text-muted-foreground">
              Dead end — this port has no cable.
            </p>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
