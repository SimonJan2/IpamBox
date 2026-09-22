"use client";

import { useEffect, useId, useMemo, useState } from "react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { RACK_LIBRARY, type LibraryDevice } from "@/lib/rack-library";
import { foldHebrew } from "@/lib/utils";
import type { Asset, IpAddress, Page, RackDevice, RackFace } from "@/types";
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

const EMPTY = {
  name: "",
  device_type: "",
  u_position: "1",
  u_height: "1",
  face: "front" as RackFace,
  colour: "#475569",
  category: "",
  manufacturer: "",
  model: "",
  asset_id: "none",
  ip_address_id: "none",
  notes: "",
};

export function DeviceFormDialog({
  open,
  onOpenChange,
  rackId,
  heightU,
  editing,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  rackId: number;
  heightU: number;
  editing: RackDevice | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState(EMPTY);
  const [libFilter, setLibFilter] = useState("");
  const [busy, setBusy] = useState(false);
  const uid = useId();

  const assetsQ = useAsyncData(
    () => api.get<Page<Asset>>("/api/v1/assets?limit=200").then((p) => p.items),
    [open]
  );
  const ipsQ = useAsyncData(
    () => api.get<IpAddress[]>("/api/v1/addresses?limit=200"),
    [open]
  );

  useEffect(() => {
    if (!open) return;
    setLibFilter("");
    setForm(
      editing
        ? {
            name: editing.name,
            device_type: editing.device_type ?? "",
            u_position: String(editing.u_position),
            u_height: String(editing.u_height),
            face: editing.face,
            colour: editing.colour ?? "#475569",
            category: editing.category ?? "",
            manufacturer: editing.manufacturer ?? "",
            model: editing.model ?? "",
            asset_id: editing.asset_id ? String(editing.asset_id) : "none",
            ip_address_id: editing.ip_address_id
              ? String(editing.ip_address_id)
              : "none",
            notes: editing.notes ?? "",
          }
        : EMPTY
    );
  }, [open, editing]);

  const libMatches = useMemo(() => {
    const needle = foldHebrew(libFilter.toLowerCase());
    if (!needle) return RACK_LIBRARY;
    return RACK_LIBRARY.filter((d) =>
      [d.slug, d.name, d.manufacturer, d.model].some(
        (f) => f && foldHebrew(f.toLowerCase()).includes(needle)
      )
    );
  }, [libFilter]);

  const applyLibrary = (d: LibraryDevice) =>
    setForm((f) => ({
      ...f,
      name: f.name || d.name,
      device_type: d.slug,
      u_height: String(d.u_height),
      face: d.face_default,
      colour: d.colour,
      category: d.category,
      manufacturer: d.manufacturer ?? "",
      model: d.model ?? "",
    }));

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        name: form.name,
        device_type: form.device_type || null,
        u_position: Number(form.u_position),
        u_height: Number(form.u_height),
        face: form.face,
        colour: form.colour || null,
        category: form.category || null,
        manufacturer: form.manufacturer || null,
        model: form.model || null,
        asset_id: form.asset_id === "none" ? null : Number(form.asset_id),
        ip_address_id:
          form.ip_address_id === "none" ? null : Number(form.ip_address_id),
        notes: form.notes || null,
      };
      if (editing) {
        await api.patch(`/api/v1/racks/${rackId}/devices/${editing.id}`, body);
        toast.success("Device updated");
      } else {
        await api.post(`/api/v1/racks/${rackId}/devices`, body);
        toast.success("Device added");
      }
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const set = (k: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [k]: e.target.value });

  const assetLabel = (a: Asset) =>
    [a.vendor, a.model, a.serial_number].filter(Boolean).join(" ") ||
    `Asset ${a.id}`;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{editing ? "Edit device" : "Add device"}</DialogTitle>
        </DialogHeader>
        <div className="grid grid-cols-2 gap-3">
          {!editing && (
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor={`${uid}-lib`}>Device library</Label>
              <Input
                id={`${uid}-lib`}
                dir="auto"
                placeholder="Filter library, e.g. switch…"
                value={libFilter}
                onChange={(e) => setLibFilter(e.target.value)}
              />
              {libFilter && (
                <div className="max-h-36 overflow-y-auto rounded-md border">
                  {libMatches.map((d) => (
                    <button
                      key={d.slug}
                      type="button"
                      onClick={() => {
                        applyLibrary(d);
                        setLibFilter("");
                      }}
                      className="flex w-full items-center gap-2 px-2 py-1.5 text-left text-sm hover:bg-accent/50"
                    >
                      <span
                        className="h-3 w-3 shrink-0 rounded-sm"
                        style={{ backgroundColor: d.colour }}
                      />
                      <span dir="auto" className="truncate">{d.name}</span>
                      <span className="ml-auto text-xs text-muted-foreground">
                        {d.u_height}U
                      </span>
                    </button>
                  ))}
                  {libMatches.length === 0 && (
                    <p className="px-2 py-1.5 text-sm text-muted-foreground">
                      No library match — fill the fields manually.
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
          <div className="col-span-2 grid gap-1.5">
            <Label htmlFor={`${uid}-name`}>Name</Label>
            <Input id={`${uid}-name`} dir="auto" value={form.name} onChange={set("name")} />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-upos`}>U position (bottom)</Label>
            <Input
              id={`${uid}-upos`}
              dir="ltr"
              type="number"
              min={1}
              max={heightU}
              value={form.u_position}
              onChange={set("u_position")}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-uheight`}>Height (U)</Label>
            <Input
              id={`${uid}-uheight`}
              dir="ltr"
              type="number"
              min={1}
              max={heightU}
              value={form.u_height}
              onChange={set("u_height")}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-face`}>Face</Label>
            <Select
              value={form.face}
              onValueChange={(v) => setForm({ ...form, face: v as RackFace })}
            >
              <SelectTrigger id={`${uid}-face`}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="front">Front</SelectItem>
                <SelectItem value="rear">Rear</SelectItem>
                <SelectItem value="both">Both</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-colour`}>Colour</Label>
            <Input
              id={`${uid}-colour`}
              dir="ltr"
              type="color"
              value={form.colour}
              onChange={set("colour")}
              className="h-9 p-1"
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-dtype`}>Device type</Label>
            <Input
              id={`${uid}-dtype`}
              dir="auto"
              placeholder="e.g. server-1u"
              value={form.device_type}
              onChange={set("device_type")}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-cat`}>Category</Label>
            <Input id={`${uid}-cat`} dir="auto" value={form.category} onChange={set("category")} />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-mfr`}>Manufacturer</Label>
            <Input id={`${uid}-mfr`} dir="auto" value={form.manufacturer} onChange={set("manufacturer")} />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-model`}>Model</Label>
            <Input id={`${uid}-model`} dir="auto" value={form.model} onChange={set("model")} />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-asset`}>Linked asset</Label>
            <Select
              value={form.asset_id}
              onValueChange={(v) => setForm({ ...form, asset_id: v })}
            >
              <SelectTrigger id={`${uid}-asset`}>
                <SelectValue placeholder="None" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
                {(assetsQ.data ?? []).map((a) => (
                  <SelectItem key={a.id} value={String(a.id)}>
                    <span dir="auto">{assetLabel(a)}</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-ip`}>Linked IP</Label>
            <Select
              value={form.ip_address_id}
              onValueChange={(v) => setForm({ ...form, ip_address_id: v })}
            >
              <SelectTrigger id={`${uid}-ip`}>
                <SelectValue placeholder="None" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None</SelectItem>
                {(ipsQ.data ?? []).map((a) => (
                  <SelectItem key={a.id} value={String(a.id)}>
                    <span dir="ltr">
                      {a.address}
                      {a.hostname ? ` — ${a.hostname}` : ""}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="col-span-2 grid gap-1.5">
            <Label htmlFor={`${uid}-notes`}>Notes</Label>
            <Input id={`${uid}-notes`} dir="auto" value={form.notes} onChange={set("notes")} />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !form.name}>
            {busy ? "Saving…" : editing ? "Save" : "Add"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
