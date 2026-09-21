"use client";

import Link from "next/link";
import { useState } from "react";
import { ChevronRight } from "lucide-react";

import { api } from "@/lib/api";
import { fmtTs } from "@/lib/prefs";
import { useAsyncData } from "@/lib/use-async-data";
import { cn, timeAgo } from "@/lib/utils";
import type { ChangeField, ChangeLogEntry, Page } from "@/types";
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
const MAX_VAL = 96;

/** One changelog value for display: null → "—", booleans → yes/no,
 *  ISO datetimes → fmtTs, objects → compact JSON, long text truncated. */
export function fmtChangeVal(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "boolean") return v ? "yes" : "no";
  if (typeof v === "object") return JSON.stringify(v);
  const s = String(v);
  // datetime strings (date-only values like expires_on stay untouched)
  if (/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}/.test(s)) return fmtTs(s);
  return s;
}

function ChangeVal({ v, old }: { v: unknown; old?: boolean }) {
  const full = fmtChangeVal(v);
  const shown = full.length > MAX_VAL ? `${full.slice(0, MAX_VAL - 1)}…` : full;
  return (
    <span
      dir="auto"
      title={full}
      className={cn(
        "truncate",
        full === "—" ? "text-muted-foreground" : old ? "chg-old" : "chg-new"
      )}
    >
      {shown}
    </span>
  );
}

/** Per-field `before → after` rows for one changelog entry. On creates the
 *  before side is always empty so only the new value renders; updates and
 *  deletes show both ends. */
export function ChangeDiff({
  changes,
  action,
}: {
  changes: ChangeField[];
  action: ChangeLogEntry["action"];
}) {
  return (
    <div className="space-y-0.5 font-mono text-xs text-muted-foreground">
      {changes.map((c) => (
        <div key={c.field} className="flex min-w-0 items-baseline gap-1">
          <span className="shrink-0 text-foreground/80">{c.field}:</span>
          {action !== "create" && (
            <>
              <ChangeVal v={c.before} old />
              <span aria-hidden="true" className="shrink-0">
                →
              </span>
            </>
          )}
          <ChangeVal v={c.after} />
        </div>
      ))}
    </div>
  );
}

function summary(e: ChangeLogEntry): string {
  if (e.action === "update") {
    const fields = e.changes.map((c) => c.field);
    return fields.length > 3
      ? `${fields.slice(0, 3).join(", ")} +${fields.length - 3} more`
      : fields.join(", ");
  }
  return e.actor;
}

/** One entry: collapsed scan line by default; entries carrying field
 *  changes expand in place to the full before → after diff. */
function HistoryEntry({ e }: { e: ChangeLogEntry }) {
  const [open, setOpen] = useState(false);
  const expandable = e.changes.length > 0;
  return (
    <div>
      <div className="flex items-baseline gap-2">
        <span className={ACTION_STYLES[e.action]}>{e.action}</span>
        {expandable ? (
          <button
            type="button"
            aria-expanded={open}
            onClick={() => setOpen(!open)}
            title={open ? "Hide values" : "Show changed values"}
            className="flex min-w-0 flex-1 items-baseline gap-1 text-left hover:text-foreground"
          >
            <ChevronRight
              aria-hidden="true"
              className={cn(
                "h-3 w-3 shrink-0 translate-y-px transition-transform",
                open && "rotate-90"
              )}
            />
            <span dir="auto" className="truncate">
              {summary(e)}
            </span>
          </button>
        ) : (
          <span dir="auto" className="min-w-0 flex-1 truncate">
            {summary(e)}
          </span>
        )}
        {e.action === "update" && (
          <span className="shrink-0 opacity-70">{e.actor}</span>
        )}
        <span className="shrink-0">{timeAgo(e.ts)}</span>
      </div>
      {open && expandable && (
        <div className="ml-2 mt-1 border-l-2 border-border pl-2">
          <ChangeDiff changes={e.changes} action={e.action} />
        </div>
      )}
    </div>
  );
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
      api.get<Page<ChangeLogEntry>>(
        `/api/v1/changelog?object_type=${encodeURIComponent(objectType)}&object_id=${objectId}&limit=${limit + 1}`
      ).then((p) => p.items),
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
            <HistoryEntry key={h.id} e={h} />
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
