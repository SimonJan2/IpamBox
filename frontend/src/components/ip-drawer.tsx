"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import Link from "next/link";
import { Cpu, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import type {
  Device,
  DeviceInterface,
  IpAddress,
  IpRange,
  IpRole,
  IpStatus,
  Page,
  Tag,
} from "@/types";
import { HistoryPanel } from "@/components/history-panel";
import { IpStatusBadge } from "@/components/status-badge";
import { TagChip, TagPicker } from "@/components/tag-picker";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
  allTags = [],
  assigned = [],
  onTagsChanged,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  ip: string;
  addr: IpAddress | null;
  prefixId: number;
  onSaved: () => void;
  allTags?: Tag[];
  assigned?: Tag[];
  onTagsChanged?: () => void;
}) {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const uid = useId();
  const [form, setForm] = useState({
    hostname: "",
    mac_address: "",
    status: "active" as IpStatus,
    role: "none" as IpRole | "none",
    nat_inside: "",
    notes: "",
  });
  const [busy, setBusy] = useState(false);
  const [natOptions, setNatOptions] = useState<IpAddress[]>([]);
  const [natError, setNatError] = useState<string | null>(null);
  // Range the address sits in (V6.1) — resolved lazily from ip_range_id.
  const [pool, setPool] = useState<IpRange | null>(null);
  // Pool-guard 409 — the "assign anyway" dialog retries with ?force=1.
  const [poolConflict, setPoolConflict] = useState<string | null>(null);
  const natTouched = useRef(false);
  const natTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Device link — devText is the picker input, devId the resolved row.
  const [devId, setDevId] = useState<number | null>(null);
  const [devText, setDevText] = useState("");
  const [devOptions, setDevOptions] = useState<Device[]>([]);
  const devTouched = useRef(false);
  const devTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Connected interface — the far-end port (usually a switch's) this
  // address is patched into. Independent of the device link above.
  const [ifDevId, setIfDevId] = useState<number | null>(null);
  const [ifDevText, setIfDevText] = useState("");
  const [ifDevOptions, setIfDevOptions] = useState<Device[]>([]);
  const [ifaces, setIfaces] = useState<DeviceInterface[]>([]);
  const [ifId, setIfId] = useState("");
  const ifDevTouched = useRef(false);
  const ifDevTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

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

  const scheduleDevs = (q: string) => {
    if (devTimer.current) clearTimeout(devTimer.current);
    devTimer.current = setTimeout(() => void fetchDevs(q), 250);
  };

  const fetchIfDevs = useCallback(async (q: string) => {
    try {
      const p = await api.get<Page<Device>>(
        `/api/v1/devices?limit=25${q ? `&q=${encodeURIComponent(q)}` : ""}`
      );
      setIfDevOptions(p.items);
    } catch {
      setIfDevOptions([]);
    }
  }, []);

  const scheduleIfDevs = (q: string) => {
    if (ifDevTimer.current) clearTimeout(ifDevTimer.current);
    ifDevTimer.current = setTimeout(() => void fetchIfDevs(q), 250);
  };

  useEffect(() => {
    if (ifDevId == null) {
      setIfaces([]);
      return;
    }
    api
      .get<DeviceInterface[]>(`/api/v1/devices/${ifDevId}/interfaces`)
      .then(setIfaces)
      .catch(() => setIfaces([]));
  }, [ifDevId]);

  const createFromIp = async () => {
    if (!addr && !ip) return;
    setBusy(true);
    try {
      const created = await api.post<Device>("/api/v1/devices", {
        name: addr?.hostname || ip,
        mac_address: addr?.mac_address || null,
        manufacturer: addr?.vendor || null,
      });
      setDevId(created.id);
      setDevText(created.name);
      toast.success(`Device “${created.name}” created`);
    } catch (e) {
      toast.error("Create failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const fetchNat = useCallback(
    async (q: string) => {
      try {
        const rows = await api.get<IpAddress[]>(
          `/api/v1/addresses?prefix_id=${prefixId}` +
            (q ? `&q=${encodeURIComponent(q)}` : "") +
            "&limit=25"
        );
        setNatOptions(rows);
        setNatError(null);
      } catch (e) {
        setNatError(String(e));
      }
    },
    [prefixId]
  );

  const scheduleNat = (q: string) => {
    if (natTimer.current) clearTimeout(natTimer.current);
    natTimer.current = setTimeout(() => void fetchNat(q), 250);
  };

  useEffect(() => {
    setForm({
      hostname: addr?.hostname ?? "",
      mac_address: addr?.mac_address ?? "",
      status: addr?.status ?? "active",
      role: addr?.role ?? "none",
      nat_inside: "",
      notes: addr?.notes ?? "",
    });
    setNatOptions([]);
    setNatError(null);
    natTouched.current = false;
    setDevId(addr?.device_id ?? null);
    setDevText(addr?.device_name ?? "");
    setDevOptions([]);
    devTouched.current = false;
    setIfDevId(addr?.connected_interface?.device_id ?? null);
    setIfDevText(addr?.connected_interface?.device_name ?? "");
    setIfId(
      addr?.connected_interface_id ? String(addr.connected_interface_id) : ""
    );
    setIfDevOptions([]);
    ifDevTouched.current = false;
    if (addr?.nat_inside_id) {
      api
        .get<IpAddress>(`/api/v1/addresses/${addr.nat_inside_id}`)
        .then((a) => setForm((f) => ({ ...f, nat_inside: a.address })))
        .catch((e) =>
          toast.error("Could not resolve NAT inside address", {
            description: String(e),
          })
        );
    }
    setPool(null);
    setPoolConflict(null);
    if (addr?.ip_range_id) {
      api
        .get<Page<IpRange>>(`/api/v1/ranges?prefix_id=${prefixId}&limit=500`)
        .then((p) =>
          setPool(p.items.find((r) => r.id === addr.ip_range_id) ?? null)
        )
        .catch(() => setPool(null));
    }
    return () => {
      if (natTimer.current) clearTimeout(natTimer.current);
      if (devTimer.current) clearTimeout(devTimer.current);
    };
  }, [addr, open, prefixId]);

  const save = async (force = false) => {
    setBusy(true);
    try {
      const natVal = form.nat_inside.trim();
      let natId: number | null = null;
      if (natVal) {
        natId =
          natOptions.find((a) => a.address === natVal && a.id !== addr?.id)
            ?.id ?? null;
        if (natId == null) {
          // The datalist only holds the last 25 suggestions — resolve the
          // typed value against the API so a valid entry always saves.
          try {
            const rows = await api.get<IpAddress[]>(
              `/api/v1/addresses?prefix_id=${prefixId}&q=${encodeURIComponent(natVal)}&limit=25`
            );
            natId =
              rows.find((a) => a.address === natVal && a.id !== addr?.id)?.id ??
              null;
          } catch {
            natId = null;
          }
        }
        if (natId == null) {
          toast.error("NAT inside address not found in this prefix");
          setBusy(false);
          return;
        }
      }
      const body = {
        hostname: form.hostname || null,
        mac_address: form.mac_address || null,
        status: form.status,
        role: form.role === "none" ? null : form.role,
        nat_inside_id: natId,
        device_id: devId,
        connected_interface_id: ifId ? Number(ifId) : null,
        notes: form.notes || null,
      };
      if (addr) {
        await api.patch(
          `/api/v1/addresses/${addr.id}${force ? "?force=1" : ""}`,
          body
        );
      } else {
        await api.post(`/api/v1/addresses${force ? "?force=1" : ""}`, {
          address: ip,
          prefix_id: prefixId,
          ...body,
        });
      }
      toast.success(addr ? "Address updated" : "Address reserved");
      setPoolConflict(null);
      onOpenChange(false);
      onSaved();
    } catch (e) {
      // 409 = the pool guard — offer the auditable "assign anyway" path
      // instead of a dead-end toast.
      const msg = e instanceof Error ? e.message : String(e);
      if (!force && msg.startsWith("409")) {
        setPoolConflict(msg.replace(/^409:\s*/, ""));
      } else {
        toast.error("Save failed", { description: msg });
      }
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
                <Badge
                  variant="outline"
                  className="border-muted-foreground/30 font-normal text-muted-foreground"
                  title="Provenance — which writer created this row"
                >
                  {addr.source}
                </Badge>
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
                <div>last seen: {fmtTs(addr.last_seen)}</div>
              )}
            </div>
          )}
          {addr?.ip_range_id != null && (
            <div className="rounded-md border border-sky-500/30 bg-sky-500/5 p-3 text-sm">
              <span className="text-sky-400">
                in {addr.range_role ?? ""} pool
                {pool && (
                  <>
                    {" "}
                    <span className="font-mono">
                      {pool.start_address}–{pool.end_address}
                    </span>
                  </>
                )}
              </span>
              {pool?.description && (
                <span className="text-muted-foreground">
                  {" "}
                  · {pool.description}
                </span>
              )}
              {!!addr.custom_fields?.pool_override && (
                <div className="mt-1 text-xs text-amber-400">
                  static assignment force-allowed inside this pool
                </div>
              )}
            </div>
          )}
          {/* imported sheet metadata (guest_os, cert, license, owner…) — the
              workbook keeps these as custom_fields on the address row */}
          {addr?.custom_fields &&
            Object.keys(addr.custom_fields).length > 0 && (
              <div className="rounded-md border p-3 text-sm space-y-1">
                <div className="mb-1 text-xs font-medium text-muted-foreground">
                  Imported fields
                </div>
                {Object.entries(addr.custom_fields).map(([k, v]) =>
                  v === null || v === "" || k === "mac_mismatch" ? null : (
                    <div key={k} className="flex gap-2 text-muted-foreground">
                      <span dir="ltr" className="shrink-0 font-mono text-xs">
                        {k}:
                      </span>
                      <span dir="auto" className="break-words text-foreground/80">
                        {typeof v === "object" ? JSON.stringify(v) : String(v)}
                      </span>
                    </div>
                  )
                )}
              </div>
            )}
          <div className="grid gap-1.5">
            <Label htmlFor={addr ? `${uid}-tags` : undefined}>Tags</Label>
            {addr ? (
              <div className="flex flex-wrap items-center gap-1">
                {assigned.map((t) => (
                  <TagChip key={t.id} tag={t} />
                ))}
                <TagPicker
                  id={`${uid}-tags`}
                  objectType="IPAddress"
                  objectId={addr.id}
                  allTags={allTags}
                  assigned={assigned}
                  onChanged={() => onTagsChanged?.()}
                />
              </div>
            ) : (
              <span className="text-sm text-muted-foreground">
                Reserve this address to add tags
              </span>
            )}
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-hostname`}>Hostname</Label>
            <Input
              id={`${uid}-hostname`}
              dir="auto"
              value={form.hostname}
              onChange={(e) => setForm({ ...form, hostname: e.target.value })}
              placeholder="host.lan"
              disabled={!canWrite}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-mac`}>MAC address</Label>
            <Input
              id={`${uid}-mac`}
              dir="ltr"
              value={form.mac_address}
              onChange={(e) => setForm({ ...form, mac_address: e.target.value })}
              placeholder="AA:BB:CC:DD:EE:FF"
              className="font-mono"
              disabled={!canWrite}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-status`}>Status</Label>
              <Select
                value={form.status}
                onValueChange={(v) => setForm({ ...form, status: v as IpStatus })}
                disabled={!canWrite}
              >
                <SelectTrigger id={`${uid}-status`}>
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
              <Label htmlFor={`${uid}-role`}>Role</Label>
              <Select
                value={form.role}
                onValueChange={(v) => setForm({ ...form, role: v as IpRole | "none" })}
                disabled={!canWrite}
              >
                <SelectTrigger id={`${uid}-role`}>
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
            <Label htmlFor={`${uid}-nat`}>NAT inside address</Label>
            <Input
              id={`${uid}-nat`}
              value={form.nat_inside}
              onChange={(e) => {
                setForm({ ...form, nat_inside: e.target.value });
                scheduleNat(e.target.value);
              }}
              onFocus={() => {
                if (!natTouched.current) {
                  natTouched.current = true;
                  void fetchNat(form.nat_inside);
                }
              }}
              placeholder="e.g. 10.0.0.5 (must exist in this prefix)"
              className="font-mono"
              list="nat-candidates"
              disabled={!canWrite}
            />
            {natError && (
              <p className="text-xs text-rose-400">
                NAT suggestions unavailable: {natError}
              </p>
            )}
            <datalist id="nat-candidates">
              {natOptions
                .filter((a) => a.id !== addr?.id)
                .map((a) => (
                  <option key={a.id} value={a.address} />
                ))}
            </datalist>
          </div>
          <div className="grid gap-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor={`${uid}-device`}>Device</Label>
              {devId ? (
                <Link
                  href={`/devices/${devId}`}
                  className="flex items-center gap-1 text-xs text-emerald-400 hover:underline"
                >
                  <Cpu className="h-3 w-3" /> open device
                </Link>
              ) : (
                canWrite && (
                  <button
                    type="button"
                    onClick={createFromIp}
                    disabled={busy}
                    className="text-xs text-emerald-400 hover:underline disabled:opacity-50"
                  >
                    + create device from this IP
                  </button>
                )
              )}
            </div>
            <Input
              id={`${uid}-device`}
              dir="auto"
              value={devText}
              onChange={(e) => {
                setDevText(e.target.value);
                setDevId(
                  devOptions.find((d) => d.name === e.target.value)?.id ?? null
                );
                scheduleDevs(e.target.value);
              }}
              onFocus={() => {
                if (!devTouched.current) {
                  devTouched.current = true;
                  void fetchDevs(devText);
                }
              }}
              placeholder="link a device (name / model / serial)"
              list="device-candidates"
              disabled={!canWrite}
            />
            <datalist id="device-candidates">
              {devOptions.map((d) => (
                <option key={d.id} value={d.name}>
                  {[d.manufacturer, d.model].filter(Boolean).join(" ") ||
                    `device #${d.id}`}
                </option>
              ))}
            </datalist>
            {devText && !devId && (
              <p className="text-xs text-muted-foreground">
                No device selected — the link is cleared on save.
              </p>
            )}
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-connif`}>Connected interface</Label>
            <Input
              id={`${uid}-connif`}
              dir="auto"
              value={ifDevText}
              onChange={(e) => {
                setIfDevText(e.target.value);
                setIfDevId(
                  ifDevOptions.find((d) => d.name === e.target.value)?.id ??
                    null
                );
                if (e.target.value === "") setIfId("");
                scheduleIfDevs(e.target.value);
              }}
              onFocus={() => {
                if (!ifDevTouched.current) {
                  ifDevTouched.current = true;
                  void fetchIfDevs(ifDevText);
                }
              }}
              placeholder="switch / patch-panel device"
              list="connif-devices"
              disabled={!canWrite}
            />
            <datalist id="connif-devices">
              {ifDevOptions.map((d) => (
                <option key={d.id} value={d.name} />
              ))}
            </datalist>
            {ifDevId != null && (
              <Select value={ifId} onValueChange={setIfId} disabled={!canWrite}>
                <SelectTrigger aria-label="Interface on the picked device">
                  <SelectValue
                    placeholder={
                      ifaces.length
                        ? "pick the port"
                        : "no interfaces on this device"
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  {ifaces.map((i) => (
                    <SelectItem key={i.id} value={String(i.id)}>
                      {i.name}
                      {i.kind !== "rj45" ? ` · ${i.kind}` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            {/* The structured link replaces the free-text pair as the source
                of truth; legacy text stays visible as the import record. */}
            {addr?.connected_interface && !ifId && (
              <p className="text-xs text-muted-foreground">
                Was linked to {addr.connected_interface.device_name} ·{" "}
                {addr.connected_interface.name} — clearing on save.
              </p>
            )}
            {!ifId && (addr?.switch_name || addr?.switch_port) && (
              <p className="text-xs text-muted-foreground" dir="auto">
                legacy text: {[addr.switch_name, addr.switch_port]
                  .filter(Boolean)
                  .join(" · ")}
              </p>
            )}
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-notes`}>Notes</Label>
            <Textarea
              id={`${uid}-notes`}
              dir="auto"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              disabled={!canWrite}
            />
          </div>
          {(canWrite || (addr && canDelete)) && (
            <div className="flex gap-2 pt-2">
              {canWrite && (
                <Button onClick={() => save()} disabled={busy} className="flex-1">
                  {busy ? "Saving…" : addr ? "Save" : "Reserve"}
                </Button>
              )}
              {addr && canDelete && (
                <Button
                  variant="destructive"
                  size="icon"
                  aria-label={`Delete ${ip}`}
                  onClick={remove}
                  disabled={busy}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          )}

          {addr && open && (
            <div className="border-t pt-3">
              <div className="mb-2 text-xs font-medium text-muted-foreground">
                History
              </div>
              <HistoryPanel
                objectType="IPAddress"
                objectId={addr.id}
                limit={20}
              />
            </div>
          )}
        </div>
      </SheetContent>
      <Dialog
        open={poolConflict !== null}
        onOpenChange={(o) => !o && setPoolConflict(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Address inside a pool</DialogTitle>
            <DialogDescription className="pt-1 text-sm">
              {poolConflict}
            </DialogDescription>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Assigning a static address inside a DHCP/pool range can collide
            with leased clients. You can assign it anyway — the override is
            recorded on the address for auditing.
          </p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setPoolConflict(null)}>
              Cancel
            </Button>
            <Button onClick={() => void save(true)} disabled={busy}>
              {busy ? "Saving…" : "Assign anyway"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Sheet>
  );
}
