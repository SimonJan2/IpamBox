"use client";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { usePolling } from "@/lib/use-polling";
import { timeAgo } from "@/lib/utils";
import { useUrlText } from "@/lib/url-state";
import type { ChangeLogEntry } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { Badge } from "@/components/ui/badge";
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

function fmt(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

function ChangeSummary({ entry }: { entry: ChangeLogEntry }) {
  const shown = entry.changes.slice(0, 4);
  const more = entry.changes.length - shown.length;
  return (
    <div className="space-y-0.5 font-mono text-xs text-muted-foreground">
      {shown.map((c) => (
        <div key={c.field} className="truncate">
          <span className="text-foreground/80">{c.field}</span>
          {entry.action !== "create" && (
            <>: <span className="line-through opacity-60">{fmt(c.before)}</span></>
          )}{" "}
          → <span>{fmt(c.after)}</span>
        </div>
      ))}
      {more > 0 && <div className="opacity-60">+{more} more</div>}
    </div>
  );
}

export default function ChangelogPage() {
  const entriesQ = useAsyncData(() =>
    api.get<ChangeLogEntry[]>("/api/v1/changelog?limit=300")
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

      <Input
        placeholder="Filter by object, type or actor…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="max-w-xs"
      />

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
