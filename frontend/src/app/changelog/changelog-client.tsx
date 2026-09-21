"use client";

import { useState } from "react";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { usePolling } from "@/lib/use-polling";
import { timeAgo } from "@/lib/utils";
import { useUrlParams, useUrlText } from "@/lib/url-state";
import type { ChangeLogEntry, Page } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { ChangeDiff } from "@/components/history-panel";
import { SavedViews } from "@/components/saved-views";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const ACTION_STYLES: Record<string, string> = {
  create: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
  update: "border-amber-500/30 bg-amber-500/10 text-amber-400",
  delete: "border-rose-500/30 bg-rose-500/10 text-rose-400",
};

const INLINE_MAX = 4;

/** First few field diffs inline; longer change sets expand per entry. */
function ChangeSummary({ entry }: { entry: ChangeLogEntry }) {
  const [open, setOpen] = useState(false);
  const total = entry.changes.length;
  const shown = open ? entry.changes : entry.changes.slice(0, INLINE_MAX);
  return (
    <div>
      <ChangeDiff changes={shown} action={entry.action} />
      {total > INLINE_MAX && (
        <button
          type="button"
          aria-expanded={open}
          onClick={() => setOpen(!open)}
          className="font-mono text-xs text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
        >
          {open ? "show less" : `+${total - INLINE_MAX} more`}
        </button>
      )}
    </div>
  );
}

export default function ChangelogPage() {
  const { searchParams, setParams } = useUrlParams();
  const objectType = searchParams.get("object_type");
  const objectId = searchParams.get("object_id");
  const scoped = objectType !== null || objectId !== null;
  const scopedUrl =
    "/api/v1/changelog?limit=300" +
    (objectType ? `&object_type=${encodeURIComponent(objectType)}` : "") +
    (objectId ? `&object_id=${encodeURIComponent(objectId)}` : "");
  const entriesQ = useAsyncData(
    () => api.get<Page<ChangeLogEntry>>(scopedUrl).then((p) => p.items),
    [scopedUrl]
  );
  const [q, setQ] = useUrlText("q");

  usePolling(
    async () => JSON.stringify(await entriesQ.reload()),
    { interval: 10000 }
  );

  const entries = entriesQ.data ?? [];

  const filtered = entries.filter(
    (e) =>
      e.object_repr.toLowerCase().includes(q.toLowerCase()) ||
      e.object_type.toLowerCase().includes(q.toLowerCase()) ||
      e.actor.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Changelog</h1>
      </div>
      <p className="text-sm text-muted-foreground">
        Every change to sites, VRFs, prefixes and addresses — who did it and
        what changed.
      </p>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Filter by object, type or actor…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        {scoped && (
          <Badge variant="secondary" className="gap-1.5">
            Scoped to {objectType ?? "any type"}
            {objectId !== null && ` #${objectId}`}
            <button
              type="button"
              aria-label="Clear object filter"
              className="ml-0.5 hover:text-foreground"
              onClick={() =>
                setParams({ object_type: null, object_id: null })
              }
            >
              ✕
            </button>
          </Badge>
        )}
        <SavedViews pageKey="changelog" className="ml-auto" />
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={entriesQ.loading}
          error={entriesQ.error}
          onRetry={entriesQ.reload}
          empty={entries.length === 0}
          emptyMessage="No changes recorded yet."
        >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>When</TableHead>
              <TableHead>Actor</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Object</TableHead>
              <TableHead>Changes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((e) => (
              <TableRow key={e.id}>
                <TableCell className="whitespace-nowrap text-muted-foreground">
                  {timeAgo(e.ts)}
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{e.actor}</Badge>
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className={ACTION_STYLES[e.action]}>
                    {e.action}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="text-sm">{e.object_type}</div>
                  <div className="font-mono text-xs text-muted-foreground">
                    {e.object_repr}
                    {e.object_id !== null && ` #${e.object_id}`}
                  </div>
                </TableCell>
                <TableCell className="max-w-md">
                  <ChangeSummary entry={e} />
                </TableCell>
              </TableRow>
            ))}
            {filtered.length === 0 && entries.length > 0 && (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="py-10 text-center text-muted-foreground"
                >
                  No entries match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </AsyncPanel>
      </div>
    </div>
  );
}
