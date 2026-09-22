"use client";

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import type { IpAddress, IpRole, IpStatus, Tag } from "@/types";
import { HistoryPanel } from "@/components/history-panel";
import { IpStatusBadge } from "@/components/status-badge";
import { TagChip, TagPicker } from "@/components/tag-picker";
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
  const natTouched = useRef(false);
  const natTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

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
    return () => {
      if (natTimer.current) clearTimeout(natTimer.current);
    };
  }, [addr, open, prefixId]);

  const save = async () => {
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
                <div>last seen: {fmtTs(addr.last_seen)}</div>
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
                <Button onClick={save} disabled={busy} className="flex-1">
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
    </Sheet>
  );
}
