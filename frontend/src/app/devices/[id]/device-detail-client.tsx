"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Container,
  ExternalLink,
  History,
  Link2,
  Link2Off,
  Pencil,
  Plus,
  Trash2,
  TriangleAlert,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import { cn } from "@/lib/utils";
import type { DeviceDetail, IpAddress, RackFace } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { AttachmentStrip } from "@/components/attachments";
import { DocsLink } from "@/components/docs/docs-link";
import { HistoryDialog, HistoryPanel } from "@/components/history-panel";
import { InlineText } from "@/components/inline-edit";
import { InterfacesPanel } from "@/components/interfaces-panel";
import { MonitorSection } from "@/components/monitor-section";
import { SnmpCard } from "@/components/snmp-card";
import { IpStatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const FACE_BADGE: Record<RackFace, string> = {
  front: "Front",
  rear: "Rear",
  both: "Front+Rear",
};

export default function DeviceDetailClient({ id }: { id: string }) {
  const router = useRouter();
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const deviceQ = useAsyncData(() =>
    api.get<DeviceDetail>(`/api/v1/devices/${id}`)
  );
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [ipPick, setIpPick] = useState("");
  const [ipOptions, setIpOptions] = useState<IpAddress[]>([]);
  const ipTouched = useRef(false);
  const ipTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [busy, setBusy] = useState(false);
  const uid = useId();

  const d = deviceQ.data;
  const refresh = () => void deviceQ.reload();

  const fetchIps = useCallback(async (q: string) => {
    try {
      const rows = await api.get<IpAddress[]>(
        `/api/v1/addresses?limit=25${q ? `&q=${encodeURIComponent(q)}` : ""}`
      );
      setIpOptions(rows);
    } catch {
      setIpOptions([]);
    }
  }, []);

  const scheduleIps = (q: string) => {
    if (ipTimer.current) clearTimeout(ipTimer.current);
    ipTimer.current = setTimeout(() => void fetchIps(q), 250);
  };

  useEffect(
    () => () => {
      if (ipTimer.current) clearTimeout(ipTimer.current);
    },
    []
  );

  const linkIp = async () => {
    const ip = ipOptions.find(
      (a) => a.address === ipPick.trim() || String(a.id) === ipPick.trim()
    );
    if (!ip) {
      toast.error("Pick an existing address from the suggestions");
      return;
    }
    setBusy(true);
    try {
      await api.patch(`/api/v1/addresses/${ip.id}`, {
        device_id: Number(id),
      });
      toast.success(`${ip.address} linked`);
      setIpPick("");
      setIpOptions([]);
      ipTouched.current = false;
      refresh();
    } catch (e) {
      toast.error("Link failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const unlinkIp = async (ipId: number, address: string) => {
    try {
      await api.patch(`/api/v1/addresses/${ipId}`, { device_id: null });
      toast.success(`${address} unlinked`);
      refresh();
    } catch (e) {
      toast.error("Unlink failed", { description: String(e) });
    }
  };

  const doDelete = async () => {
    setBusy(true);
    try {
      await api.del(`/api/v1/devices/${id}`);
      toast.success("Device deleted");
      router.push("/devices");
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/devices")}
          aria-label="Back to devices"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="flex min-w-0 items-center gap-2 text-xl font-semibold">
          <span dir="auto" className="truncate">
            {d?.name ?? "Device"}
          </span>
          <DocsLink slug="devices" />
        </h1>
        <div className="ml-auto flex items-center gap-1">
          {d != null && d.flagged_count > 0 && (
            <Badge
              variant="outline"
              className="border-amber-700/60 bg-amber-950/40 text-amber-300"
              title={`${d.flagged_count} port(s) carrying a cable_mismatch flag — see Interfaces`}
            >
              <TriangleAlert className="mr-1 h-3 w-3" />
              {d.flagged_count} cable flag{d.flagged_count === 1 ? "" : "s"}
            </Badge>
          )}
          {d?.health && <IpStatusBadge s={d.health} />}
          <Button
            variant="ghost"
            size="icon"
            aria-label="Device history"
            onClick={() => setHistoryOpen(true)}
          >
            <History className="h-4 w-4" />
          </Button>
          {canWrite && (
            <Button
              variant="ghost"
              size="icon"
              aria-label="Edit device"
              onClick={() => setEditOpen(true)}
            >
              <Pencil className="h-4 w-4" />
            </Button>
          )}
          {canDelete && (
            <Button
              variant="ghost"
              size="icon"
              aria-label="Delete device"
              onClick={() => setDeleteOpen(true)}
            >
              <Trash2 className="h-4 w-4 text-rose-400" />
            </Button>
          )}
        </div>
      </div>

      <AsyncPanel
        loading={deviceQ.loading}
        error={deviceQ.error}
        onRetry={deviceQ.reload}
        empty={!d}
        emptyMessage="Device not found."
      >
        {d && (
          <div className="grid gap-4 lg:grid-cols-[20rem_1fr]">
            <div className="space-y-4">
              {/* Placement card */}
              <div className="space-y-1.5 rounded-lg border bg-card p-3 text-sm">
                <div className="flex items-center gap-1.5 font-medium">
                  <Container className="h-4 w-4" /> Placement
                </div>
                {d.rack ? (
                  <>
                    <p>
                      <Link
                        href={`/racks/${d.rack.id}?device=${d.id}`}
                        className="text-emerald-400 hover:underline"
                        dir="auto"
                      >
                        {d.rack.label}
                      </Link>
                      <span dir="ltr" className="text-muted-foreground">
                        {" "}
                        · U{d.u_position}
                        {(d.u_height ?? 1) > 1
                          ? `–${(d.u_position ?? 0) + (d.u_height ?? 1) - 1}`
                          : ""}{" "}
                        · {d.u_height ?? 1}U
                      </span>
                    </p>
                    {d.face && (
                      <Badge variant="outline">{FACE_BADGE[d.face]}</Badge>
                    )}
                  </>
                ) : (
                  <p className="text-muted-foreground">
                    Unracked — no rack placement.
                  </p>
                )}
                {d.carrier && (
                  <p className="text-muted-foreground" dir="auto">
                    Mounted in{" "}
                    <Link
                      href={`/devices/${d.carrier.id}`}
                      className="text-emerald-400 hover:underline"
                    >
                      {d.carrier.label}
                    </Link>
                    , slot {(d.slot ?? 0) + 1}
                  </p>
                )}
                {d.slot_layout && (
                  <p className="text-muted-foreground">
                    Carrier tray — {d.slot_layout}
                  </p>
                )}
                {d.interface_count > 0 && (
                  <p className="text-muted-foreground" dir="ltr">
                    Ports: {d.cabled_count}/{d.interface_count} cabled
                    {d.flagged_count > 0 && (
                      <span className="text-amber-400">
                        {" "}· ⚠ {d.flagged_count} flagged
                      </span>
                    )}
                  </p>
                )}
              </div>

              {/* Identity card */}
              <div className="space-y-1.5 rounded-lg border bg-card p-3 text-sm">
                <div className="font-medium">Identity</div>
                {[d.manufacturer, d.model].filter(Boolean).length > 0 && (
                  <p dir="auto" className="text-muted-foreground">
                    {[d.manufacturer, d.model].filter(Boolean).join(" ")}
                  </p>
                )}
                {d.device_type && (
                  <p className="text-muted-foreground">type: {d.device_type}</p>
                )}
                {d.serial_number && (
                  <p dir="ltr" className="font-mono text-muted-foreground">
                    {d.serial_number}
                  </p>
                )}
                {d.mac_address && (
                  <p dir="ltr" className="font-mono text-muted-foreground">
                    {d.mac_address}
                  </p>
                )}
                {d.site && (
                  <p>
                    Site:{" "}
                    <Link
                      href={`/sites?q=${encodeURIComponent(d.site.label)}`}
                      className="text-emerald-400 hover:underline"
                      dir="auto"
                    >
                      {d.site.label}
                    </Link>
                  </p>
                )}
                {d.asset && (
                  <p>
                    Asset:{" "}
                    <Link
                      href={`/inventory?q=${encodeURIComponent(d.asset.label)}`}
                      className="text-emerald-400 hover:underline"
                      dir="auto"
                    >
                      {d.asset.label}
                    </Link>
                  </p>
                )}
                {(d.watts != null || d.weight_kg != null) && (
                  <p dir="ltr" className="text-muted-foreground">
                    {d.watts != null ? `${d.watts} W` : ""}
                    {d.watts != null && d.weight_kg != null ? " · " : ""}
                    {d.weight_kg != null ? `${d.weight_kg} kg` : ""}
                  </p>
                )}
              </div>

              <div className="rounded-lg border bg-card p-3 text-sm">
                <div className="mb-1 font-medium">Notes</div>
                <InlineText
                  value={d.notes}
                  onSave={async (v) => {
                    try {
                      await api.patch(`/api/v1/devices/${d.id}`, {
                        notes: v || null,
                      });
                      refresh();
                    } catch (e) {
                      toast.error("Save failed", { description: String(e) });
                    }
                  }}
                  disabled={!canWrite}
                  dir="auto"
                  label={`Edit notes for ${d.name}`}
                />
              </div>

              <AttachmentStrip entityType="device" entityId={d.id} />
              <MonitorSection deviceId={d.id} anchorLabel={d.name} />
              <SnmpCard device={d} onChanged={refresh} />
            </div>

            {/* IPs table + link picker */}
            <div className="space-y-4">
              <div className="rounded-lg border">
                <div className="flex items-center justify-between border-b px-3 py-2">
                  <span className="text-sm font-medium">
                    IP addresses
                    {d.health && (
                      <span className="ml-2 text-xs font-normal text-muted-foreground">
                        health = worst linked status
                      </span>
                    )}
                  </span>
                  {d.health && <IpStatusBadge s={d.health} />}
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Address</TableHead>
                      <TableHead>Hostname</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Last seen</TableHead>
                      {canWrite && <TableHead className="w-10" />}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {d.ips.map((ip) => (
                      <TableRow key={ip.id}>
                        <TableCell>
                          <Link
                            href={`/prefixes/${ip.prefix_id}?q=${encodeURIComponent(ip.address)}`}
                            className="font-mono text-emerald-400 hover:underline"
                            dir="ltr"
                          >
                            {ip.address}
                          </Link>
                        </TableCell>
                        <TableCell dir="auto" className="text-muted-foreground">
                          {ip.hostname ?? "—"}
                        </TableCell>
                        <TableCell>
                          <IpStatusBadge s={ip.status} />
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {ip.last_seen ? fmtTs(ip.last_seen) : "—"}
                        </TableCell>
                        {canWrite && (
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={`Unlink ${ip.address}`}
                              onClick={() => unlinkIp(ip.id, ip.address)}
                            >
                              <Link2Off className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                    {d.ips.length === 0 && (
                      <TableRow>
                        <TableCell
                          colSpan={canWrite ? 5 : 4}
                          className="py-8 text-center text-muted-foreground"
                        >
                          No linked addresses — link mgmt, service and iLO IPs
                          here.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
                {canWrite && (
                  <div className="flex items-center gap-2 border-t p-2">
                    <Input
                      value={ipPick}
                      onChange={(e) => {
                        setIpPick(e.target.value);
                        scheduleIps(e.target.value);
                      }}
                      onFocus={() => {
                        if (!ipTouched.current) {
                          ipTouched.current = true;
                          void fetchIps("");
                        }
                      }}
                      placeholder="Link an existing address — type to search"
                      className="h-8 font-mono text-sm"
                      list="device-ip-candidates"
                      aria-label="Address to link"
                    />
                    <datalist id="device-ip-candidates">
                      {ipOptions
                        .filter((a) => a.device_id !== d.id)
                        .map((a) => (
                          <option key={a.id} value={a.address}>
                            {a.hostname ??
                              (a.device_id ? `on ${a.device_name}` : "free")}
                          </option>
                        ))}
                    </datalist>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={linkIp}
                      disabled={busy || !ipPick.trim()}
                    >
                      <Link2 className="h-4 w-4" /> Link
                    </Button>
                  </div>
                )}
              </div>

              <InterfacesPanel device={d} />

              <div className="rounded-lg border p-3">
                <div className="mb-2 text-xs font-medium text-muted-foreground">
                  History
                </div>
                <HistoryPanel objectType="Device" objectId={d.id} limit={20} />
              </div>
            </div>
          </div>
        )}
      </AsyncPanel>

      <EditDialog
        device={d ?? undefined}
        open={editOpen}
        onOpenChange={setEditOpen}
        onSaved={refresh}
      />

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete {d?.name}?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            The {d?.ips.length ?? 0} linked IP(s) keep their addresses but lose
            the device link. Carrier children are unmounted.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete} disabled={busy}>
              {busy ? "Deleting…" : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <HistoryDialog
        open={historyOpen}
        onOpenChange={setHistoryOpen}
        objectType="Device"
        objectId={d?.id ?? null}
        title={d?.name}
      />
    </div>
  );
}

const EMPTY_EDIT = {
  name: "",
  device_type: "",
  serial_number: "",
  manufacturer: "",
  model: "",
  mac_address: "",
  category: "",
  notes: "",
};

function EditDialog({
  device,
  open,
  onOpenChange,
  onSaved,
}: {
  device: DeviceDetail | undefined;
  open: boolean;
  onOpenChange: (o: boolean) => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState(EMPTY_EDIT);
  const [busy, setBusy] = useState(false);
  const uid = useId();

  useEffect(() => {
    if (open && device) {
      setForm({
        name: device.name ?? "",
        device_type: device.device_type ?? "",
        serial_number: device.serial_number ?? "",
        manufacturer: device.manufacturer ?? "",
        model: device.model ?? "",
        mac_address: device.mac_address ?? "",
        category: device.category ?? "",
        notes: device.notes ?? "",
      });
    }
  }, [open, device]);

  const set =
    (k: keyof typeof EMPTY_EDIT) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm({ ...form, [k]: e.target.value });

  const submit = async () => {
    if (!device) return;
    setBusy(true);
    try {
      await api.patch(
        `/api/v1/devices/${device.id}`,
        Object.fromEntries(
          Object.entries(form).map(([k, v]) => [k, v || null])
        )
      );
      toast.success("Device updated");
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
          <DialogTitle>Edit device</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-name`}>Name</Label>
            <Input id={`${uid}-name`} dir="auto" value={form.name} onChange={set("name")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-manufacturer`}>Manufacturer</Label>
              <Input
                id={`${uid}-manufacturer`}
                dir="auto"
                value={form.manufacturer}
                onChange={set("manufacturer")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-model`}>Model</Label>
              <Input id={`${uid}-model`} dir="auto" value={form.model} onChange={set("model")} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-serial`}>Serial number</Label>
              <Input
                id={`${uid}-serial`}
                dir="ltr"
                value={form.serial_number}
                onChange={set("serial_number")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-mac`}>MAC address</Label>
              <Input
                id={`${uid}-mac`}
                dir="ltr"
                className="font-mono"
                value={form.mac_address}
                onChange={set("mac_address")}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-type`}>Device type</Label>
              <Input
                id={`${uid}-type`}
                dir="auto"
                value={form.device_type}
                onChange={set("device_type")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-category`}>Category</Label>
              <Input
                id={`${uid}-category`}
                dir="auto"
                value={form.category}
                onChange={set("category")}
              />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-notes`}>Notes</Label>
            <Textarea id={`${uid}-notes`} dir="auto" value={form.notes} onChange={set("notes")} />
          </div>
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
