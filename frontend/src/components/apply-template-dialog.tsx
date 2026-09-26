"use client";

import { useEffect, useId, useState } from "react";
import { LayoutTemplate } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { foldHebrew } from "@/lib/utils";
import { cn } from "@/lib/utils";
import type {
  DeviceTemplate,
  Page,
  TemplateApplyResult,
} from "@/types";
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

export function portCount(t: DeviceTemplate): number {
  return (t.interfaces?.length ?? 0) + (t.power_ports?.length ?? 0);
}

/** Apply-template picker: search the template catalog, choose merge
 *  (add missing ports, existing names report as skipped) or replace
 *  (wipe + restamp — refused server-side when any port is cabled). */
export function ApplyTemplateDialog({
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
  const [templates, setTemplates] = useState<DeviceTemplate[]>([]);
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<DeviceTemplate | null>(null);
  const [mode, setMode] = useState<"merge" | "replace">("merge");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return;
    setFilter("");
    setSelected(null);
    setMode("merge");
    api
      .get<Page<DeviceTemplate>>("/api/v1/device-templates?limit=500")
      .then((p) => setTemplates(p.items))
      .catch(() => setTemplates([]));
  }, [open]);

  const needle = foldHebrew(filter.toLowerCase().trim());
  const matches = needle
    ? templates.filter((t) =>
        [t.name, t.manufacturer, t.model, t.device_type].some(
          (f) => f && foldHebrew(f.toLowerCase()).includes(needle)
        )
      )
    : templates;

  const submit = async () => {
    if (!selected) return;
    setBusy(true);
    try {
      const r = await api.post<TemplateApplyResult>(
        `/api/v1/devices/${deviceId}/apply-template`,
        { template_id: selected.id, mode }
      );
      const parts = [`created ${r.created}`];
      if (r.skipped.length) parts.push(`skipped ${r.skipped.length}`);
      if (r.blocked.length)
        parts.push(`blocked: ${r.blocked.join(", ")}`);
      toast.success(`Applied ${selected.name}`, {
        description: parts.join(" · "),
      });
      onOpenChange(false);
      onDone();
    } catch (e) {
      toast.error("Apply failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Apply a device template</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-q`}>Template</Label>
            <Input
              id={`${uid}-q`}
              dir="auto"
              placeholder="Search name, manufacturer, model…"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
            <div className="max-h-48 overflow-y-auto rounded-md border">
              {matches.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setSelected(t)}
                  className={cn(
                    "flex w-full items-center gap-2 px-2.5 py-1.5 text-left text-sm hover:bg-accent/50",
                    selected?.id === t.id && "bg-accent/60"
                  )}
                >
                  <LayoutTemplate className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                  <span dir="auto" className="min-w-0 truncate font-medium">
                    {t.name}
                  </span>
                  <span className="min-w-0 truncate text-xs text-muted-foreground">
                    {[t.manufacturer, t.model].filter(Boolean).join(" ")}
                  </span>
                  <span className="ml-auto flex shrink-0 items-center gap-1">
                    {t.source === "builtin" && (
                      <Badge variant="outline" className="px-1 py-0 text-[10px]">
                        builtin
                      </Badge>
                    )}
                    <Badge variant="outline" className="px-1 py-0 text-[10px]">
                      {portCount(t)} ports
                    </Badge>
                  </span>
                </button>
              ))}
              {matches.length === 0 && (
                <p className="px-2.5 py-2 text-sm text-muted-foreground">
                  No templates match — manage them under Devices → Templates.
                </p>
              )}
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label>Mode</Label>
            <div role="radiogroup" className="flex gap-1.5">
              {(
                [
                  ["merge", "Merge — keep existing ports"],
                  ["replace", "Replace — wipe then stamp"],
                ] as const
              ).map(([value, label]) => (
                <button
                  key={value}
                  type="button"
                  role="radio"
                  aria-checked={mode === value}
                  onClick={() => setMode(value)}
                  className={cn(
                    "flex-1 rounded-md border px-2.5 py-1.5 text-left text-xs transition-colors",
                    mode === value
                      ? "border-emerald-600/60 bg-emerald-950/30 text-emerald-300"
                      : "border-border text-muted-foreground hover:bg-accent/50"
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
            <p className="text-xs text-muted-foreground">
              {mode === "merge"
                ? "Ports the device already has are skipped and reported."
                : "Deletes this device's ports first — refused if any are cabled."}
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={busy || !selected}>
            {busy
              ? "Applying…"
              : `Apply${selected ? ` (${portCount(selected)} ports)` : ""}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
