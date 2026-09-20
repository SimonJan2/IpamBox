"use client";

import Link from "next/link";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { timeAgo } from "@/lib/utils";
import type { ChangeLogEntry } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const ACTION_STYLES: Record<string, string> = {
  create: "text-emerald-400",
  update: "text-amber-400",
  delete: "text-rose-400",
};

const DEFAULT_LIMIT = 50;

function summary(e: ChangeLogEntry): string {
  if (e.action === "update") {
    const fields = e.changes.map((c) => c.field);
    return fields.length > 3
      ? `${fields.slice(0, 3).join(", ")} +${fields.length - 3} more`
      : fields.join(", ");
  }
  return e.actor;
}

/** Read-only, per-object changelog slice. Capped at `limit` rows with a
 *  deep link into the full changelog page carrying the same filter. */
export function HistoryPanel({
  objectType,
  objectId,
  limit = DEFAULT_LIMIT,
}: {
  objectType: string;
  objectId: number;
  limit?: number;
}) {
  const entriesQ = useAsyncData(
    () =>
      api.get<ChangeLogEntry[]>(
        `/api/v1/changelog?object_type=${encodeURIComponent(objectType)}&object_id=${objectId}&limit=${limit + 1}`
      ),
    [objectType, objectId, limit]
  );

  const entries = entriesQ.data ?? [];
  const shown = entries.slice(0, limit);
  const more = entries.length > limit;
  const changelogHref = `/changelog?object_type=${encodeURIComponent(objectType)}&object_id=${objectId}`;

  return (
    <div>
      <AsyncPanel
        loading={entriesQ.loading}
        error={entriesQ.error}
        onRetry={entriesQ.reload}
        empty={entries.length === 0}
        emptyMessage="No recorded changes for this object."
        className="py-4"
      >
        <div className="space-y-1.5 text-xs text-muted-foreground">
          {shown.map((h) => (
            <div key={h.id} className="flex items-baseline gap-2">
              <span className={ACTION_STYLES[h.action]}>{h.action}</span>
              <span dir="auto" className="flex-1 truncate">
                {summary(h)}
              </span>
              {h.action === "update" && (
                <span className="shrink-0 opacity-70">{h.actor}</span>
              )}
              <span className="shrink-0">{timeAgo(h.ts)}</span>
            </div>
          ))}
        </div>
      </AsyncPanel>
      <div className="mt-2 border-t pt-2 text-right">
        <Link
          href={changelogHref}
          className="text-xs text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
        >
          {more ? "More — view all in changelog" : "View all in changelog"}
        </Link>
      </div>
    </div>
  );
}

/** HistoryPanel inside a modal — the "History" row action on list pages.
 *  Mounts the panel only while open so each open gets a fresh fetch. */
export function HistoryDialog({
  open,
  onOpenChange,
  objectType,
  objectId,
  title,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  objectType: string | null;
  objectId: number | null;
  title?: React.ReactNode;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex min-w-0 items-baseline gap-2">
            History
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
        {open && objectType != null && objectId != null && (
          <HistoryPanel objectType={objectType} objectId={objectId} />
        )}
      </DialogContent>
    </Dialog>
  );
}
