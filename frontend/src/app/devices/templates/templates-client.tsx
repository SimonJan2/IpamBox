"use client";

// Device-template manager (V10.1): the catalog of reusable port layouts.
// Rows list + an editor dialog with a port-grid editor (name/kind/speed/
// pair per row, plus a range expander like `Gi1/0/1..48 sfp28 25000`).
// Builtins are honest about their semantics: editing one flips it to a
// manual row (the seeded name is tombstoned, it won't re-seed), and
// Duplicate keeps the builtin untouched while cloning a manual copy.

import { useEffect, useId, useRef, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Copy,
  LayoutTemplate,
  LibraryBig,
  Pencil,
  Plus,
  Trash2,
  Wand2,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { useAsyncData } from "@/lib/use-async-data";
import { cn, foldHebrew } from "@/lib/utils";
import { libraryBySlug, loadRackLibrary } from "@/lib/rack-library";
import type {
  DeviceTemplate,
  InterfaceKind,
  Page,
  RackFace,
} from "@/types";

import { AsyncPanel } from "@/components/async-panel";
import { portCount } from "@/components/apply-template-dialog";
import { ConfirmDialog } from "@/components/confirm-action";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
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

const KINDS: InterfaceKind[] = [
  "rj45",
  "sfp",
  "sfp28",
  "qsfp",
  "console",
  "patch",
  "power",
  "other",
];
const FACES: RackFace[] = ["front", "rear", "both"];
const SPEED_PRESETS = [100, 1000, 2500, 10000, 25000, 40000, 100000];

// Editable grid row — `pair` is a sibling row's name ("" = unpaired);
// position is implicit row order on save.
type PortRow = {
  key: number;
  name: string;
  kind: InterfaceKind;
  speed: string;
  pair: string;
};

type FormState = {
  name: string;
  manufacturer: string;
  model: string;
  device_type: string;
  u_height: string;
  face_default: RackFace;
  colour: string;
  category: string;
  watts: string;
  weight_kg: string;
  notes: string;
};

const EMPTY_FORM: FormState = {
  name: "",
  manufacturer: "",
  model: "",
  device_type: "",
  u_height: "1",
  face_default: "front",
  colour: "",
  category: "",
  watts: "",
  weight_kg: "",
  notes: "",
};

/** `Gi1/0/1..48` → {prefix: "Gi1/0/", from: 1, to: 48}; null on no match. */
function parseRange(pat: string): { prefix: string; from: number; to: number } | null {
  const m = /^(.*?)(\d+)\s*\.\.\s*(\d+)$/.exec(pat.trim());
  if (!m) return null;
  const from = Number(m[2]);
  const to = Number(m[3]);
  if (to < from || to - from > 512) return null;
  return { prefix: m[1], from, to };
}

function templateToRows(t: DeviceTemplate): { ports: PortRow[]; powers: string[] } {
  const ports = (t.interfaces ?? []).map((e, i) => ({
    key: i,
    name: e.name,
    kind: e.kind,
    speed: e.speed_mbps != null ? String(e.speed_mbps) : "",
    pair: e.pair ?? "",
  }));
  const powers = (t.power_ports ?? []).map((p) => p.name);
  return { ports, powers };
}

export default function TemplatesPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);

  const q = useAsyncData(
    () =>
      api
        .get<Page<DeviceTemplate>>("/api/v1/device-templates?limit=2000")
        .then((p) => p.items),
    []
  );
  const [filter, setFilter] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<DeviceTemplate | null>(null);
  const [copying, setCopying] = useState<DeviceTemplate | null>(null);
  const [deleting, setDeleting] = useState<DeviceTemplate | null>(null);

  const needle = foldHebrew(filter.toLowerCase().trim());
  const items = (q.data ?? []).filter(
    (t) =>
      !needle ||
      [t.name, t.manufacturer, t.model, t.device_type, t.category].some(
        (f) => f && foldHebrew(f.toLowerCase()).includes(needle)
      )
  );

  const doDelete = async () => {
    if (!deleting) return;
    await api.del(`/api/v1/device-templates/${deleting.id}`);
    toast.success(`Template ${deleting.name} deleted`);
    setDeleting(null);
    void q.reload();
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild aria-label="Back to devices">
            <Link href="/devices">
              <ArrowLeft />
            </Link>
          </Button>
          <div>
            <h1 className="text-lg font-semibold">Device templates</h1>
            <p className="text-sm text-muted-foreground">
              Reusable port layouts — apply them on a device or stamp them
              while creating one.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Input
            dir="auto"
            placeholder="Filter…"
            aria-label="Filter templates"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-48"
          />
          {canWrite && (
            <Button
              size="sm"
              onClick={() => {
                setEditing(null);
                setCopying(null);
                setDialogOpen(true);
              }}
            >
              <Plus /> New template
            </Button>
          )}
        </div>
      </div>

      <AsyncPanel
        loading={q.loading}
        error={q.error}
        onRetry={() => void q.reload()}
        empty={items.length === 0}
        emptyMessage={
          needle ? "No templates match." : "No device templates yet."
        }
      >
        <ul className="divide-y rounded-lg border">
          {items.map((t) => (
            <li key={t.id} className="flex items-center gap-3 px-3 py-2">
              <LayoutTemplate className="h-4 w-4 shrink-0 text-muted-foreground" />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span dir="auto" className="truncate font-medium">
                    {t.name}
                  </span>
                  <Badge
                    variant="outline"
                    className={cn(
                      "px-1 py-0 text-[10px]",
                      t.source === "builtin" &&
                        "border-sky-500/40 text-sky-400"
                    )}
                  >
                    {t.source}
                  </Badge>
                  <Badge variant="outline" className="px-1 py-0 text-[10px]">
                    {portCount(t)} ports
                  </Badge>
                  <Badge variant="outline" className="px-1 py-0 text-[10px]">
                    {t.u_height}U
                  </Badge>
                  {t.category && (
                    <Badge variant="outline" className="px-1 py-0 text-[10px]">
                      {t.category}
                    </Badge>
                  )}
                </div>
                <p dir="auto" className="truncate text-xs text-muted-foreground">
                  {[t.manufacturer, t.model].filter(Boolean).join(" ") ||
                    t.notes ||
                    "—"}
                </p>
              </div>
              <div className="flex shrink-0 gap-1">
                {canWrite && (
                  <>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Duplicate ${t.name}`}
                      onClick={() => {
                        setEditing(null);
                        setCopying(t);
                        setDialogOpen(true);
                      }}
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Edit ${t.name}`}
                      onClick={() => {
                        setCopying(null);
                        setEditing(t);
                        setDialogOpen(true);
                      }}
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </Button>
                  </>
                )}
                {canDelete && (
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Delete ${t.name}`}
                    onClick={() => setDeleting(t)}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      </AsyncPanel>

      <TemplateDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        editing={editing}
        copying={copying}
        onSaved={() => void q.reload()}
      />
      <ConfirmDialog
        open={deleting != null}
        onOpenChange={(o) => !o && setDeleting(null)}
        title={`Delete ${deleting?.name ?? "template"}?`}
        description={
          deleting?.source === "builtin"
            ? "This is a builtin template — deleting it removes it for good (the seeder remembers it was deleted and won't re-add it)."
            : "Delete this device template? Devices already stamped keep their ports."
        }
        confirmWord="DELETE"
        actionLabel="Delete template"
        onAction={doDelete}
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Editor dialog
// ---------------------------------------------------------------------------

function TemplateDialog({
  open,
  onOpenChange,
  editing,
  copying,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  editing: DeviceTemplate | null;
  copying: DeviceTemplate | null;
  onSaved: () => void;
}) {
  const uid = useId();
  const nextKey = useRef(1);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [ports, setPorts] = useState<PortRow[]>([]);
  const [powers, setPowers] = useState<string[]>([]);
  const [rangePat, setRangePat] = useState("");
  const [rangeKind, setRangeKind] = useState<InterfaceKind>("rj45");
  const [rangeSpeed, setRangeSpeed] = useState("");
  const [rangePair, setRangePair] = useState("");
  const [busy, setBusy] = useState(false);
  const library = useAsyncData(() => loadRackLibrary(), []);

  const src = editing ?? copying;
  const mode = editing ? "edit" : copying ? "copy" : "create";

  useEffect(() => {
    if (!open) return;
    setRangePat("");
    setRangePair("");
    setRangeKind("rj45");
    setRangeSpeed("");
    if (src) {
      setForm({
        name: mode === "copy" ? `${src.name} copy` : src.name,
        manufacturer: src.manufacturer ?? "",
        model: src.model ?? "",
        device_type: src.device_type ?? "",
        u_height: String(src.u_height ?? 1),
        face_default: src.face_default,
        colour: src.colour ?? "",
        category: src.category ?? "",
        watts: src.watts != null ? String(src.watts) : "",
        weight_kg: src.weight_kg != null ? String(src.weight_kg) : "",
        notes: src.notes ?? "",
      });
      const { ports: p, powers: pw } = templateToRows(src);
      setPorts(p.map((r) => ({ ...r, key: nextKey.current++ })));
      setPowers(pw);
    } else {
      setForm(EMPTY_FORM);
      setPorts([]);
      setPowers([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reseed only on open
  }, [open, src?.id, mode]);

  const set =
    (k: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [k]: e.target.value }));

  const libraryEntry = form.device_type
    ? libraryBySlug(library.data ?? []).get(form.device_type)
    : undefined;

  const fillFromLibrary = () => {
    if (!libraryEntry) return;
    setForm((f) => ({
      ...f,
      manufacturer: libraryEntry.manufacturer || f.manufacturer,
      model: libraryEntry.model || f.model,
      u_height: String(libraryEntry.u_height || 1),
      face_default: libraryEntry.face_default ?? f.face_default,
      colour: libraryEntry.colour || f.colour,
      category: libraryEntry.category || f.category,
      watts:
        libraryEntry.watts != null ? String(libraryEntry.watts) : f.watts,
      weight_kg:
        libraryEntry.weight_kg != null
          ? String(libraryEntry.weight_kg)
          : f.weight_kg,
    }));
    toast.success(`Prefilled from ${libraryEntry.name}`, {
      description:
        "The rack library carries no port data — add the port layout below.",
    });
  };

  const updateRow = (key: number, patch: Partial<PortRow>) =>
    setPorts((prev) =>
      prev.map((r) => (r.key === key ? { ...r, ...patch } : r))
    );

  /** Pair bookkeeping — declared mutually to match the server rule:
   *  setting A.pair=B writes B.pair=A; re-pointing or clearing unwinds
   *  the other end's stale link too. */
  const setPair = (key: number, pairName: string) =>
    setPorts((prev) => {
      const next = prev.map((r) => ({ ...r }));
      const me = next.find((r) => r.key === key);
      if (!me || me.pair === pairName) return prev;
      if (me.pair) {
        const old = next.find((r) => r.name === me.pair);
        if (old && old.pair === me.name) old.pair = "";
      }
      me.pair = pairName;
      if (pairName) {
        const other = next.find((r) => r.name === pairName);
        if (other) {
          if (other.pair && other.pair !== me.name) {
            const stale = next.find((r) => r.name === other.pair);
            if (stale && stale.pair === other.name) stale.pair = "";
          }
          other.pair = me.name;
        }
      }
      return next;
    });

  const expandRange = () => {
    const front = parseRange(rangePat);
    if (!front) {
      toast.error("Range must look like Gi1/0/1..48");
      return;
    }
    const rear = rangePair.trim() ? parseRange(rangePair) : null;
    if (rangePair.trim() && !rear) {
      toast.error("Rear range must look like b1..24");
      return;
    }
    if (rear && rear.to - rear.from !== front.to - front.from) {
      toast.error("Rear range must span the same count");
      return;
    }
    const added: PortRow[] = [];
    for (let i = front.from; i <= front.to; i++) {
      const name = `${front.prefix}${i}`;
      const pair = rear
        ? `${rear.prefix}${rear.from + (i - front.from)}`
        : "";
      added.push({
        key: nextKey.current++,
        name,
        kind: rangeKind,
        speed: rangeSpeed,
        pair,
      });
    }
    if (rear) {
      for (let i = rear.from; i <= rear.to; i++) {
        added.push({
          key: nextKey.current++,
          name: `${rear.prefix}${i}`,
          kind: rangeKind,
          speed: rangeSpeed,
          pair: `${front.prefix}${front.from + (i - rear.from)}`,
        });
      }
    }
    setPorts((prev) => [...prev, ...added]);
    toast.success(
      `Expanded ${added.length} port${added.length === 1 ? "" : "s"}`
    );
  };

  const submit = async () => {
    const orNull = (s: string) => (s.trim() ? s.trim() : null);
    const interfaces = ports
      .filter((p) => p.name.trim())
      .map((p, i) => ({
        name: p.name.trim(),
        kind: p.kind,
        speed_mbps: p.speed.trim() ? Number(p.speed) : null,
        position: i,
        pair: p.pair || null,
      }));
    const powerList = powers.map((s) => s.trim()).filter(Boolean);
    const body = {
      name: form.name.trim(),
      manufacturer: orNull(form.manufacturer),
      model: orNull(form.model),
      device_type: orNull(form.device_type),
      u_height: Number(form.u_height) || 1,
      face_default: form.face_default,
      colour: orNull(form.colour),
      category: orNull(form.category),
      watts: form.watts.trim() ? Number(form.watts) : null,
      weight_kg: form.weight_kg.trim() ? Number(form.weight_kg) : null,
      interfaces,
      power_ports: powerList.map((name) => ({ name })),
      notes: orNull(form.notes),
    };
    setBusy(true);
    try {
      if (mode === "edit" && editing) {
        const res = await api.patch<DeviceTemplate>(
          `/api/v1/device-templates/${editing.id}`,
          body
        );
        toast.success(
          editing.source === "builtin" && res.source === "manual"
            ? `${res.name} saved as a manual template`
            : "Template updated",
          {
            description:
              editing.source === "builtin"
                ? "The builtin row is now yours — it won't re-seed."
                : undefined,
          }
        );
      } else {
        await api.post<DeviceTemplate>("/api/v1/device-templates", body);
        toast.success(`Template ${body.name} created`);
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
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
        <DialogHeader>
          <DialogTitle>
            {mode === "edit"
              ? `Edit ${editing?.name}`
              : mode === "copy"
                ? `Duplicate ${copying?.name}`
                : "New device template"}
          </DialogTitle>
        </DialogHeader>
        {editing?.source === "builtin" && mode === "edit" && (
          <p className="rounded-md border border-sky-500/20 bg-sky-950/20 px-3 py-2 text-xs text-sky-300">
            This is a builtin template — saving converts it to a manual
            template you own. To keep the builtin intact, close this and use
            the duplicate button instead.
          </p>
        )}
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-name`}>Name</Label>
              <Input
                id={`${uid}-name`}
                dir="auto"
                value={form.name}
                onChange={set("name")}
                placeholder="switch-48"
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-type`}>
                Device type{" "}
                <span className="text-muted-foreground">
                  (rack-library slug)
                </span>
              </Label>
              <div className="flex gap-1.5">
                <Input
                  id={`${uid}-type`}
                  dir="auto"
                  list={`${uid}-lib`}
                  value={form.device_type}
                  onChange={set("device_type")}
                  placeholder="cisco-c9300-48p"
                />
                <datalist id={`${uid}-lib`}>
                  {(library.data ?? []).map((d) => (
                    <option key={d.slug} value={d.slug}>
                      {d.name}
                    </option>
                  ))}
                </datalist>
                {libraryEntry && (
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    aria-label="Prefill from rack library"
                    title={`Prefill from ${libraryEntry.name}`}
                    onClick={fillFromLibrary}
                  >
                    <LibraryBig className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-mfr`}>Manufacturer</Label>
              <Input
                id={`${uid}-mfr`}
                dir="auto"
                value={form.manufacturer}
                onChange={set("manufacturer")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-model`}>Model</Label>
              <Input
                id={`${uid}-model`}
                dir="auto"
                value={form.model}
                onChange={set("model")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-u`}>U height</Label>
              <Input
                id={`${uid}-u`}
                type="number"
                min={1}
                value={form.u_height}
                onChange={set("u_height")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-face`}>Default face</Label>
              <Select
                value={form.face_default}
                onValueChange={(v) =>
                  setForm((f) => ({ ...f, face_default: v as RackFace }))
                }
              >
                <SelectTrigger id={`${uid}-face`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {FACES.map((f) => (
                    <SelectItem key={f} value={f}>
                      {f}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-cat`}>Category</Label>
              <Input
                id={`${uid}-cat`}
                dir="auto"
                value={form.category}
                onChange={set("category")}
                placeholder="network"
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-colour`}>Colour</Label>
              <div className="flex gap-1.5">
                <input
                  type="color"
                  aria-label="Pick colour"
                  className="h-9 w-10 shrink-0 cursor-pointer rounded-md border bg-transparent p-1"
                  value={form.colour || "#64748b"}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, colour: e.target.value }))
                  }
                />
                <Input
                  id={`${uid}-colour`}
                  dir="ltr"
                  value={form.colour}
                  onChange={set("colour")}
                  placeholder="#34d399"
                />
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-watts`}>Watts</Label>
              <Input
                id={`${uid}-watts`}
                type="number"
                min={0}
                value={form.watts}
                onChange={set("watts")}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-kg`}>Weight (kg)</Label>
              <Input
                id={`${uid}-kg`}
                type="number"
                min={0}
                step="0.1"
                value={form.weight_kg}
                onChange={set("weight_kg")}
              />
            </div>
          </div>

          <div className="grid gap-1.5">
            <Label>Ports ({ports.filter((p) => p.name.trim()).length})</Label>
            <div className="rounded-md border">
              <div className="grid grid-cols-[1fr_6.5rem_5rem_6.5rem_2rem] items-center gap-1 border-b px-2 py-1 text-[10px] uppercase tracking-wide text-muted-foreground">
                <span>Name</span>
                <span>Kind</span>
                <span>Mbps</span>
                <span>Pairs with</span>
                <span />
              </div>
              <div className="max-h-56 overflow-y-auto">
                {ports.map((r) => (
                  <div
                    key={r.key}
                    className="grid grid-cols-[1fr_6.5rem_5rem_6.5rem_2rem] items-center gap-1 px-2 py-0.5"
                  >
                    <Input
                      aria-label="Port name"
                      dir="auto"
                      value={r.name}
                      onChange={(e) =>
                        updateRow(r.key, { name: e.target.value })
                      }
                      className="h-7 px-1.5 font-mono text-xs"
                    />
                    <Select
                      value={r.kind}
                      onValueChange={(v) =>
                        updateRow(r.key, { kind: v as InterfaceKind })
                      }
                    >
                      <SelectTrigger
                        aria-label="Port kind"
                        className="h-7 px-1.5 text-xs"
                      >
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {KINDS.map((k) => (
                          <SelectItem key={k} value={k}>
                            {k}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Input
                      aria-label="Speed Mbps"
                      dir="ltr"
                      type="number"
                      min={1}
                      list={`${uid}-speeds`}
                      value={r.speed}
                      onChange={(e) =>
                        updateRow(r.key, { speed: e.target.value })
                      }
                      className="h-7 px-1.5 text-xs"
                    />
                    <Select
                      value={r.pair || "none"}
                      onValueChange={(v) =>
                        setPair(r.key, v === "none" ? "" : v)
                      }
                    >
                      <SelectTrigger
                        aria-label="Pairs with"
                        className="h-7 px-1.5 text-xs"
                      >
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">—</SelectItem>
                        {ports
                          .filter((o) => o.key !== r.key && o.name.trim())
                          .map((o) => (
                            <SelectItem key={o.key} value={o.name}>
                              {o.name}
                            </SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Remove ${r.name || "row"}`}
                      className="h-7 w-7"
                      onClick={() => {
                        if (r.pair) setPair(r.key, "");
                        setPorts((prev) =>
                          prev.filter((o) => o.key !== r.key)
                        );
                      }}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
                {ports.length === 0 && (
                  <p className="px-2 py-3 text-center text-xs text-muted-foreground">
                    No ports yet — expand a range below or add rows one at a
                    time.
                  </p>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-1.5 border-t px-2 py-1.5">
                <Input
                  aria-label="Range pattern"
                  dir="ltr"
                  placeholder="Gi1/0/1..48"
                  value={rangePat}
                  onChange={(e) => setRangePat(e.target.value)}
                  className="h-7 w-32 px-1.5 font-mono text-xs"
                />
                <Select
                  value={rangeKind}
                  onValueChange={(v) => setRangeKind(v as InterfaceKind)}
                >
                  <SelectTrigger
                    aria-label="Range kind"
                    className="h-7 w-24 px-1.5 text-xs"
                  >
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {KINDS.map((k) => (
                      <SelectItem key={k} value={k}>
                        {k}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Input
                  aria-label="Range speed Mbps"
                  dir="ltr"
                  type="number"
                  min={1}
                  placeholder="Mbps"
                  list={`${uid}-speeds`}
                  value={rangeSpeed}
                  onChange={(e) => setRangeSpeed(e.target.value)}
                  className="h-7 w-20 px-1.5 text-xs"
                />
                <Input
                  aria-label="Rear pair range (optional)"
                  dir="ltr"
                  placeholder="rear: b1..48"
                  value={rangePair}
                  onChange={(e) => setRangePair(e.target.value)}
                  className="h-7 w-28 px-1.5 font-mono text-xs"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="h-7"
                  onClick={expandRange}
                >
                  <Wand2 className="h-3 w-3" /> Expand
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-7"
                  onClick={() =>
                    setPorts((prev) => [
                      ...prev,
                      {
                        key: nextKey.current++,
                        name: "",
                        kind: "rj45",
                        speed: "",
                        pair: "",
                      },
                    ])
                  }
                >
                  <Plus className="h-3 w-3" /> Row
                </Button>
              </div>
            </div>
            <datalist id={`${uid}-speeds`}>
              {SPEED_PRESETS.map((s) => (
                <option key={s} value={s} />
              ))}
            </datalist>
          </div>

          <div className="grid gap-1.5">
            <Label>Power ports ({powers.filter(Boolean).length})</Label>
            <div className="flex flex-wrap items-center gap-1.5">
              {powers.map((p, i) => (
                <span key={i} className="flex items-center gap-0.5">
                  <Input
                    aria-label={`Power port ${i + 1}`}
                    dir="auto"
                    value={p}
                    onChange={(e) =>
                      setPowers((prev) =>
                        prev.map((x, j) => (j === i ? e.target.value : x))
                      )
                    }
                    className="h-7 w-24 px-1.5 font-mono text-xs"
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Remove power port ${p || i + 1}`}
                    className="h-6 w-6"
                    onClick={() =>
                      setPowers((prev) => prev.filter((_, j) => j !== i))
                    }
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </span>
              ))}
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7"
                onClick={() => setPowers((prev) => [...prev, ""])}
              >
                <Plus className="h-3 w-3" /> PSU/outlet
              </Button>
            </div>
          </div>

          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-notes`}>Notes</Label>
            <Input
              id={`${uid}-notes`}
              dir="auto"
              value={form.notes}
              onChange={set("notes")}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={busy || !form.name.trim()}>
            {busy
              ? "Saving…"
              : mode === "edit"
                ? "Save template"
                : "Create template"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
