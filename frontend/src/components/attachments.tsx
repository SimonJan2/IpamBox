"use client";

import { useCallback, useRef, useState } from "react";
import {
  Download,
  File,
  FileArchive,
  FileText,
  Paperclip,
  Trash2,
  X,
  Image as ImageIcon,
} from "lucide-react";
import { toast } from "sonner";

import { api, attachmentUrl } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import { useAsyncData } from "@/lib/use-async-data";
import { cn } from "@/lib/utils";
import type { Attachment, AttachmentEntityType } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const MAX_MB = 6;

function fmtBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

function iconFor(contentType: string) {
  if (contentType.startsWith("image/")) return ImageIcon;
  if (contentType === "application/zip" || contentType === "application/x-zip-compressed")
    return FileArchive;
  if (contentType === "application/pdf" || contentType.startsWith("text/"))
    return FileText;
  return File;
}

/**
 * Compact attachment strip — one component mounted on every entity's
 * detail surface (device/rack/site cards, IP drawer, cert/circuit/asset
 * dialogs). Chips carry an icon by content type, label/filename, size and
 * an uploaded_by tooltip; image types open a lightbox instead of a bare
 * download. Upload is a file pick (or drop) + optional label.
 */
export function AttachmentStrip({
  entityType,
  entityId,
}: {
  entityType: AttachmentEntityType;
  entityId: number;
}) {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const itemsQ = useAsyncData(
    () =>
      api.get<Attachment[]>(
        `/api/v1/attachments?entity_type=${entityType}&entity_id=${entityId}`
      ),
    [entityType, entityId]
  );
  const fileRef = useRef<HTMLInputElement>(null);
  const [pending, setPending] = useState<File | null>(null);
  const [label, setLabel] = useState("");
  const [busy, setBusy] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState<Attachment | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<Attachment | null>(null);

  const items = itemsQ.data ?? [];

  const pickFile = useCallback(
    (f: File | null) => {
      if (!f) return;
      if (f.size > MAX_MB * 1024 * 1024) {
        toast.error("File too large", {
          description: `Attachments are capped at ${MAX_MB} MB.`,
        });
        return;
      }
      setLabel("");
      setPending(f);
    },
    []
  );

  const upload = async () => {
    if (!pending) return;
    setBusy(true);
    try {
      const q = new URLSearchParams({
        entity_type: entityType,
        entity_id: String(entityId),
        filename: pending.name || "file",
      });
      if (label.trim()) q.set("label", label.trim());
      await api.upload<Attachment>(
        `/api/v1/attachments?${q}`,
        pending,
        pending.type || "application/octet-stream"
      );
      toast.success(`Attached ${pending.name}`);
      setPending(null);
      void itemsQ.reload();
    } catch (e) {
      toast.error("Upload failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const openPreview = async (a: Attachment) => {
    setPreview(a);
    setPreviewUrl(null);
    try {
      // fetch the blob ourselves — Content-Disposition: attachment must not
      // turn into a forced download inside the lightbox.
      const res = await fetch(attachmentUrl(a.id), { credentials: "include" });
      if (!res.ok) throw new Error(`${res.status}`);
      setPreviewUrl(URL.createObjectURL(await res.blob()));
    } catch (e) {
      toast.error("Preview failed", { description: String(e) });
      setPreview(null);
    }
  };

  const closePreview = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreview(null);
    setPreviewUrl(null);
  };

  const doDelete = async () => {
    if (!deleting) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/attachments/${deleting.id}`);
      toast.success(`Deleted ${deleting.filename}`);
      setDeleting(null);
      void itemsQ.reload();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      className={cn(
        "rounded-lg border bg-card p-3 text-sm",
        dragOver && "border-emerald-500/60 bg-emerald-500/5"
      )}
      onDragOver={(e) => {
        if (!canWrite) return;
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        if (!canWrite) return;
        e.preventDefault();
        setDragOver(false);
        pickFile(e.dataTransfer.files?.[0] ?? null);
      }}
    >
      <div className="mb-1.5 flex items-center justify-between gap-2">
        <span className="font-medium">Attachments</span>
        {canWrite && (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 gap-1.5 px-2 text-xs"
            onClick={() => fileRef.current?.click()}
          >
            <Paperclip className="h-3.5 w-3.5" /> Attach
          </Button>
        )}
        <input
          ref={fileRef}
          type="file"
          className="hidden"
          onChange={(e) => {
            pickFile(e.target.files?.[0] ?? null);
            e.target.value = "";
          }}
        />
      </div>

      {items.length === 0 && !pending && !itemsQ.loading && (
        <p className="text-xs text-muted-foreground">
          Nothing attached{canWrite ? " — drop a file or click Attach" : ""}.
        </p>
      )}
      {itemsQ.error && (
        <p className="text-xs text-rose-400">{itemsQ.error}</p>
      )}

      <TooltipProvider delayDuration={200}>
        <div className="flex flex-wrap gap-1.5">
          {items.map((a) => {
            const Icon = iconFor(a.content_type);
            return (
              <Tooltip key={a.id}>
                <TooltipTrigger asChild>
                  <span className="group flex max-w-full items-center gap-1 rounded-md border bg-muted/40 py-1 pl-1.5 pr-1 text-xs">
                    <Icon className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                    {a.content_type.startsWith("image/") ? (
                      <button
                        type="button"
                        onClick={() => void openPreview(a)}
                        className="truncate hover:underline"
                        dir="auto"
                      >
                        {a.label || a.filename}
                      </button>
                    ) : (
                      <a
                        href={attachmentUrl(a.id)}
                        className="truncate hover:underline"
                        dir="auto"
                      >
                        {a.label || a.filename}
                      </a>
                    )}
                    <span className="shrink-0 text-muted-foreground">
                      {fmtBytes(a.size)}
                    </span>
                    <a
                      href={attachmentUrl(a.id)}
                      download={a.filename}
                      aria-label={`Download ${a.filename}`}
                      className="shrink-0 rounded p-0.5 text-muted-foreground hover:text-foreground"
                    >
                      <Download className="h-3 w-3" />
                    </a>
                    {canDelete && (
                      <button
                        type="button"
                        aria-label={`Delete ${a.filename}`}
                        onClick={() => setDeleting(a)}
                        className="shrink-0 rounded p-0.5 text-muted-foreground hover:text-rose-400"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </span>
                </TooltipTrigger>
                <TooltipContent>
                  <div dir="auto">{a.filename}</div>
                  <div className="text-muted-foreground">
                    {a.content_type} · {a.uploaded_by ?? "?"} ·{" "}
                    {fmtTs(a.created_at)}
                  </div>
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>
      </TooltipProvider>

      {pending && (
        <div className="mt-2 flex flex-wrap items-center gap-2 rounded-md border border-emerald-500/30 bg-emerald-500/5 p-2">
          <span dir="auto" className="max-w-56 truncate text-xs">
            {pending.name}
          </span>
          <span className="text-xs text-muted-foreground">
            {fmtBytes(pending.size)}
          </span>
          <Input
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="Label (optional)"
            aria-label="Attachment label"
            className="h-7 w-40 text-xs"
            dir="auto"
          />
          <Button
            size="sm"
            className="h-7 px-2 text-xs"
            onClick={upload}
            disabled={busy}
          >
            {busy ? "Uploading…" : "Upload"}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="h-7 px-2 text-xs"
            onClick={() => setPending(null)}
            disabled={busy}
          >
            Cancel
          </Button>
        </div>
      )}

      {/* image lightbox — blob fetched into an object URL so the download
          endpoint's attachment disposition can't force a save dialog */}
      <Dialog
        open={preview !== null}
        onOpenChange={(o) => !o && closePreview()}
      >
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="truncate text-sm font-normal" dir="auto">
              {preview?.label || preview?.filename}
            </DialogTitle>
          </DialogHeader>
          <div className="flex max-h-[70vh] items-center justify-center overflow-auto">
            {previewUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={previewUrl}
                alt={preview?.filename ?? "attachment"}
                className="max-h-[70vh] max-w-full object-contain"
              />
            ) : (
              <span className="py-10 text-sm text-muted-foreground">
                Loading…
              </span>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={deleting !== null} onOpenChange={(o) => !o && setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete attachment</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.label || deleting?.filename}
            </span>
            ? This cannot be undone — re-upload to replace a file instead.
          </p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete} disabled={busy}>
              {busy ? "Deleting…" : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

/** AttachmentStrip inside a modal — the paperclip row action on list pages
 *  (sites, certificates, circuits, inventory) where the row is the only
 *  detail surface. Mounts the strip only while open so each open fetches. */
export function AttachmentsDialog({
  open,
  onOpenChange,
  entityType,
  entityId,
  title,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  entityType: AttachmentEntityType;
  entityId: number | null;
  title?: React.ReactNode;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex min-w-0 items-baseline gap-2">
            Attachments
            {title && (
              <span
                dir="auto"
                className="truncate text-sm font-normal text-muted-foreground"
              >
                {title}
              </span>
            )}
          </DialogTitle>
        </DialogHeader>
        {open && entityId != null && (
          <AttachmentStrip entityType={entityType} entityId={entityId} />
        )}
      </DialogContent>
    </Dialog>
  );
}
