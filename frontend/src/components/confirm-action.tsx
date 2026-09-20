"use client";

import { useEffect, useId, useState } from "react";
import { toast } from "sonner";

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

/** Danger-zone action gated behind typing a confirm word. */
export function ConfirmAction({
  description,
  confirmWord,
  actionLabel,
  onAction,
  extra,
}: {
  description: React.ReactNode;
  confirmWord: string;
  actionLabel: string;
  onAction: () => Promise<unknown>;
  extra?: React.ReactNode;
}) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const inputId = useId();

  const run = async () => {
    setBusy(true);
    try {
      await onAction();
      setText("");
    } catch (e) {
      toast.error("Action failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-3 rounded-lg border border-rose-500/20 p-4">
      <div className="text-sm text-muted-foreground">{description}</div>
      {extra}
      <div className="grid gap-1.5">
        <Label className="text-xs" htmlFor={inputId}>
          Type <span className="font-mono text-rose-400">{confirmWord}</span> to
          confirm
        </Label>
        <div className="flex gap-2">
          <Input
            id={inputId}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={confirmWord}
            autoComplete="off"
            className="max-w-48"
          />
          <Button
            variant="destructive"
            size="sm"
            disabled={text !== confirmWord || busy}
            onClick={run}
          >
            {busy ? "Working…" : actionLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}

/** Same typed-confirmation gate as ConfirmAction, as a modal for
 *  toolbar/row-level destructive actions (bulk delete, single delete). */
export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmWord,
  actionLabel,
  onAction,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  title: string;
  description: React.ReactNode;
  confirmWord: string;
  actionLabel: string;
  onAction: () => Promise<unknown>;
}) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const inputId = useId();

  useEffect(() => {
    if (open) setText("");
  }, [open]);

  const run = async () => {
    setBusy(true);
    try {
      await onAction();
      onOpenChange(false);
    } catch (e) {
      toast.error("Action failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <div className="text-sm text-muted-foreground">{description}</div>
        <div className="grid gap-1.5">
          <Label className="text-xs" htmlFor={inputId}>
            Type <span className="font-mono text-rose-400">{confirmWord}</span>{" "}
            to confirm
          </Label>
          <Input
            id={inputId}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={confirmWord}
            autoComplete="off"
            className="max-w-48"
          />
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            disabled={text !== confirmWord || busy}
            onClick={run}
          >
            {busy ? "Working…" : actionLabel}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
