"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Check, Plus, Search, X } from "lucide-react";

import { cn } from "@/lib/utils";
import type { IpAddress, IpStatus, Tag } from "@/types";
import { TagDialog } from "@/components/tag-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const STATUSES: IpStatus[] = [
  "active",
  "reserved",
  "dhcp",
  "discovered",
  "offline",
];

const STATUS_DOT: Record<IpStatus, string> = {
  active: "bg-emerald-500/70",
  reserved: "bg-amber-500/70",
  dhcp: "bg-cyan-500/70",
  discovered: "bg-violet-500/70",
  offline: "bg-zinc-500/70",
};

const MAX_RESULTS = 200;

export function AddressFilterPanel({
  items,
  filtered,
  tags,
  addrTags,
  search,
  onSearch,
  statusSel,
  onToggleStatus,
  tagSel,
  onToggleTag,
  untagged,
  onToggleUntagged,
  onClear,
  onSelectMatching,
  onPick,
  onTagsChanged,
}: {
  items: IpAddress[];
  filtered: IpAddress[];
  tags: Tag[];
  addrTags: Map<number, Tag[]>;
  search: string;
  onSearch: (v: string) => void;
  statusSel: Set<IpStatus>;
  onToggleStatus: (s: IpStatus) => void;
  tagSel: Set<number>;
  onToggleTag: (id: number) => void;
  untagged: boolean;
  onToggleUntagged: () => void;
  onClear: () => void;
  onSelectMatching: () => void;
  onPick: (a: IpAddress) => void;
  onTagsChanged: () => void;
}) {
  const [newTagOpen, setNewTagOpen] = useState(false);
  const active = !!search || statusSel.size > 0 || tagSel.size > 0 || untagged;

  const statusCounts = useMemo(() => {
    const m = new Map<IpStatus, number>();
    for (const a of items) m.set(a.status, (m.get(a.status) ?? 0) + 1);
    return m;
  }, [items]);

  const { tagCounts, untaggedCount } = useMemo(() => {
    const ids = new Set(items.map((a) => a.id));
    const counts = new Map<number, number>();
    for (const [oid, list] of addrTags) {
      if (!ids.has(oid)) continue;
      for (const t of list) counts.set(t.id, (counts.get(t.id) ?? 0) + 1);
    }
    return {
      tagCounts: counts,
      untaggedCount: items.filter((a) => !(addrTags.get(a.id)?.length)).length,
    };
  }, [items, addrTags]);

  const shown = filtered.slice(0, MAX_RESULTS);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Filters</span>
        {active && (
          <Button variant="ghost" size="sm" className="h-7 px-2" onClick={onClear}>
            <X className="h-3.5 w-3.5" /> Clear
          </Button>
        )}
      </div>

      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          placeholder="IP, hostname, MAC, vendor…"
          className="pl-8"
        />
      </div>

      <div>
        <div className="mb-1.5 text-xs font-medium text-muted-foreground">Status</div>
        <div className="flex flex-wrap gap-1.5">
          {STATUSES.map((s) => {
            const on = statusSel.has(s);
            return (
              <button
                key={s}
                onClick={() => onToggleStatus(s)}
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs transition-colors",
                  on
                    ? "border-foreground/40 bg-accent text-foreground"
                    : "border-transparent text-muted-foreground hover:bg-accent/50"
                )}
              >
                <i className={cn("h-2 w-2 rounded-full", STATUS_DOT[s])} />
                {s}
                <span className="text-muted-foreground">
                  {statusCounts.get(s) ?? 0}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <div className="mb-1.5 flex items-center justify-between">
          <span className="text-xs font-medium text-muted-foreground">Tags</span>
          <button
            onClick={() => setNewTagOpen(true)}
            className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
          >
            <Plus className="h-3 w-3" /> New tag
          </button>
        </div>
        <div className="max-h-56 space-y-0.5 overflow-auto pr-1">
          <button
            onClick={onToggleUntagged}
            className={cn(
              "flex w-full items-center gap-2 rounded-md px-2 py-1 text-sm transition-colors",
              untagged ? "bg-accent" : "hover:bg-accent/50"
            )}
          >
            <i className="h-2 w-2 rounded-full border border-dashed border-muted-foreground" />
            <span className="flex-1 text-left italic text-muted-foreground">
              untagged
            </span>
            {untagged && <Check className="h-3.5 w-3.5" />}
            <span className="text-xs text-muted-foreground">{untaggedCount}</span>
          </button>
          {tags.map((t) => {
            const on = tagSel.has(t.id);
            const count = tagCounts.get(t.id) ?? 0;
            return (
              <button
                key={t.id}
                onClick={() => onToggleTag(t.id)}
                className={cn(
                  "flex w-full items-center gap-2 rounded-md px-2 py-1 text-sm transition-colors",
                  on ? "bg-accent" : "hover:bg-accent/50",
                  count === 0 && !on && "opacity-50"
                )}
              >
                <i
                  className="h-2 w-2 rounded-full"
                  style={{ background: t.color }}
                />
                <span className="flex-1 truncate text-left">{t.name}</span>
                {on && <Check className="h-3.5 w-3.5" />}
                <span className="text-xs text-muted-foreground">{count}</span>
              </button>
            );
          })}
        </div>
        <Link
          href="/tags"
          className="mt-1 inline-block text-xs text-muted-foreground hover:text-foreground"
        >
          Manage tags →
        </Link>
      </div>

      {active && (
        <div className="border-t pt-3">
          <div className="mb-1.5 flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">
              {filtered.length} matching
            </span>
            <Button
              variant="outline"
              size="sm"
              className="h-7 px-2 text-xs"
              disabled={filtered.length === 0}
              onClick={onSelectMatching}
            >
              Select matching
            </Button>
          </div>
          <div className="max-h-64 space-y-0.5 overflow-auto pr-1">
            {shown.map((a) => {
              const aTags = addrTags.get(a.id) ?? [];
              return (
                <button
                  key={a.id}
                  onClick={() => onPick(a)}
                  className="flex w-full items-center gap-2 rounded-md px-2 py-1 text-left hover:bg-accent/50"
                >
                  <i
                    className={cn("h-2 w-2 shrink-0 rounded-full", STATUS_DOT[a.status])}
                  />
                  <span className="font-mono text-xs">{a.address}</span>
                  <span className="flex-1 truncate text-xs text-muted-foreground">
                    {a.hostname ?? ""}
                  </span>
                  {aTags.slice(0, 3).map((t) => (
                    <i
                      key={t.id}
                      title={t.name}
                      className="h-2 w-2 shrink-0 rounded-full"
                      style={{ background: t.color }}
                    />
                  ))}
                </button>
              );
            })}
            {filtered.length > shown.length && (
              <div className="px-2 py-1 text-xs text-muted-foreground">
                +{filtered.length - shown.length} more
              </div>
            )}
            {filtered.length === 0 && (
              <div className="px-2 py-1 text-xs text-muted-foreground">
                No addresses match.
              </div>
            )}
          </div>
        </div>
      )}

      <TagDialog
        open={newTagOpen}
        onOpenChange={setNewTagOpen}
        tag={null}
        onSaved={onTagsChanged}
      />
    </div>
  );
}
