"use client";

import { useEffect, useId, useState } from "react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import type { Tag } from "@/types";
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
import { ROW_COLOR_PALETTE } from "@/lib/row-color";

// One palette for tag chips and row tints — canonical list lives in
// lib/row-color (ROW_COLOR_PALETTE); this stays exported for old imports.
export const TAG_COLORS: readonly string[] = ROW_COLOR_PALETTE;

export function TagDialog({
  open,
  onOpenChange,
  tag,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  tag: Tag | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({ name: "", color: TAG_COLORS[0], description: "" });
  const [busy, setBusy] = useState(false);
  const uid = useId();

  useEffect(() => {
    if (open) {
      setForm({
        name: tag?.name ?? "",
        color: tag?.color ?? TAG_COLORS[0],
        description: tag?.description ?? "",
      });
    }
  }, [open, tag]);

  const submit = async () => {
    setBusy(true);
    try {
      const body = { name: form.name, color: form.color, description: form.description || null };
      if (tag) {
        await api.patch(`/api/v1/tags/${tag.id}`, body);
        toast.success("Tag updated");
      } else {
        await api.post("/api/v1/tags", body);
        toast.success("Tag created");
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
          <DialogTitle>{tag ? "Edit tag" : "New tag"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-name`}>Name</Label>
            <Input
              id={`${uid}-name`}
              placeholder="production, iot, servers…"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label id={`${uid}-color`}>Color</Label>
            <div
              role="radiogroup"
              aria-labelledby={`${uid}-color`}
              className="flex gap-1.5"
            >
              {TAG_COLORS.map((c) => (
                <button
                  key={c}
                  type="button"
                  role="radio"
                  aria-checked={form.color === c}
                  aria-label={c}
                  onClick={() => setForm({ ...form, color: c })}
                  className={`h-7 w-7 rounded-md border-2 transition-all ${
                    form.color === c ? "border-foreground" : "border-transparent"
                  }`}
                  style={{ background: c }}
                />
              ))}
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-description`}>Description</Label>
            <Input
              id={`${uid}-description`}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !form.name}>
            {busy ? "Saving…" : tag ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
