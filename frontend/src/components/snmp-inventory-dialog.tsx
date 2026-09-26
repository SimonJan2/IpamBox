"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ChevronRight,
  DownloadCloud,
  Loader2,
  Network,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type {
  DeviceDetail,
  Site,
  SnmpInventoryResult,
  SnmpInventoryRow,
  Vrf,
} from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// ---------------------------------------------------------------------------
// SNMP inventory sync (V8.3): preview the device's own VLAN/SVI/ARP tables,
// review per-row verdicts, apply the selection in one transaction.
// ---------------------------------------------------------------------------

const ACTION_STYLE: Record<string, string> = {
  create: "text-emerald-400",
  update: "text-sky-400",
  exists: "text-muted-foreground",
  skip: "text-muted-foreground",
  conflict: "text-rose-400",
  error: "text-rose-400",
};

const SECTION_LABEL: Record<string, string> = {
  vlans: "VLANs",
  subnets: "Subnets",
  addresses: "Addresses",
};

/** Rows the user can elect to write — everything else is informational. */
const APPLYABLE = new Set(["create", "update"]);
const NONE = "__none__";

function fmt(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  return String(v);
}

/** Routes for applied rows — where a created/updated thing lives in the UI. */
function refHref(row: SnmpInventoryRow): string | null {
  const r = row.result;
  if (!r) return null;
  if (r.kind === "prefix" && r.id != null) return `/prefixes/${r.id}`;
  if (r.kind === "vlan") return "/vlans";
  if (r.kind === "address" && r.prefix_id != null)
    return `/prefixes/${r.prefix_id}`;
  return null;
}

function CountCards({ counts }: { counts: Record<string, number> }) {
  const order = ["create", "update", "exists", "conflict", "skip", "error"];
  return (
    <div className="flex flex-wrap gap-2">
      {order
        .filter((k) => (counts[k] ?? 0) > 0)
        .map((k) => (
          <div
            key={k}
            className="rounded-lg border bg-card px-3 py-1.5 text-center"
          >
            <div className={`text-lg font-semibold ${ACTION_STYLE[k]}`}>
              {counts[k]}
            </div>
            <div className="text-[11px] capitalize text-muted-foreground">
              {k}
            </div>
          </div>
        ))}
    </div>
  );
}

function SectionTable({
  section,
  rows,
  selected,
  onToggle,
  onToggleAll,
  committed,
}: {
  section: string;
  rows: SnmpInventoryRow[];
  selected: Set<string>;
  onToggle: (key: string, on: boolean) => void;
  onToggleAll: (rows: SnmpInventoryRow[], on: boolean) => void;
  committed: boolean;
}) {
  const [open, setOpen] = useState<Set<string>>(new Set());
  const applyable = rows.filter((r) => APPLYABLE.has(r.action));
  const allChecked =
    applyable.length > 0 && applyable.every((r) => selected.has(r.key));
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {applyable.length > 0 && !committed && (
          <Checkbox
            checked={allChecked}
            onCheckedChange={(v) => onToggleAll(applyable, v === true)}
            aria-label={`Toggle all ${section}`}
          />
        )}
        {SECTION_LABEL[section] ?? section}
        <Badge variant="secondary" className="text-[10px]">
          {rows.length}
        </Badge>
      </div>
      <div className="max-h-56 overflow-auto rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-8" />
              <TableHead className="w-24">Action</TableHead>
              <TableHead>Detail</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((r) => {
              const hasDiff = r.diff && Object.keys(r.diff).length > 0;
              const isOpen = open.has(r.key);
              const applyable = APPLYABLE.has(r.action);
              return (
                <Fragment key={r.key}>
                  <TableRow
                    className={cn(
                      hasDiff ? "cursor-pointer" : undefined,
                      r.action === "conflict" && "bg-rose-950/20",
                      r.action === "error" && "bg-rose-950/30"
                    )}
                    onClick={() => {
                      if (!hasDiff) return;
                      const next = new Set(open);
                      if (isOpen) next.delete(r.key);
                      else next.add(r.key);
                      setOpen(next);
                    }}
                  >
                    <TableCell className="w-8">
                      {applyable && !committed ? (
                        <Checkbox
                          checked={selected.has(r.key)}
                          onCheckedChange={(v) => onToggle(r.key, v === true)}
                          onClick={(e) => e.stopPropagation()}
                          aria-label={`Apply ${r.key}`}
                        />
                      ) : (
                        hasDiff && (
                          <ChevronRight
                            className={cn(
                              "h-3 w-3 text-muted-foreground transition-transform",
                              isOpen && "rotate-90"
                            )}
                          />
                        )
                      )}
                    </TableCell>
                    <TableCell className={ACTION_STYLE[r.action] ?? ""}>
                      {r.action}
                    </TableCell>
                    <TableCell dir="auto" className="text-muted-foreground">
                      <span className="flex items-center gap-1.5">
                        {hasDiff && applyable && (
                          <ChevronRight
                            className={cn(
                              "h-3 w-3 shrink-0 transition-transform",
                              isOpen && "rotate-90"
                            )}
                          />
                        )}
                        <span>
                          {r.detail}
                          {r.result && (
                            <>
                              {" "}
                              <ResultLink row={r} />
                            </>
                          )}
                          {r.ref && r.action !== "exists" && (
                            <span className="ml-1 text-xs opacity-70">
                              ({r.ref.label})
                            </span>
                          )}
                        </span>
                      </span>
                    </TableCell>
                  </TableRow>
                  {hasDiff && isOpen && (
                    <TableRow>
                      <TableCell />
                      <TableCell colSpan={2}>
                        <div className="space-y-0.5 py-1 font-mono text-xs">
                          {Object.entries(r.diff!).map(([f, [o, n]]) => (
                            <div key={f}>
                              <span className="text-muted-foreground">
                                {f}:
                              </span>{" "}
                              <span className="text-rose-400 line-through">
                                {fmt(o)}
                              </span>{" "}
                              →{" "}
                              <span className="text-emerald-400">
                                {fmt(n)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </Fragment>
              );
            })}
            {rows.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={3}
                  className="py-6 text-center text-muted-foreground"
                >
                  Nothing reported.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

function ResultLink({ row }: { row: SnmpInventoryRow }) {
  const href = refHref(row);
  if (!href || !row.result) return null;
  return (
    <Link
      href={href}
      className="text-xs text-emerald-400 underline-offset-2 hover:underline"
      onClick={(e) => e.stopPropagation()}
    >
      {row.result.label} →
    </Link>
  );
}

export function SnmpInventoryDialog({
  device,
  open,
  onOpenChange,
  onCommitted,
}: {
  device: DeviceDetail;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCommitted: () => void;
}) {
  const [vrfs, setVrfs] = useState<Vrf[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [vrfId, setVrfId] = useState<string>("");
  const [siteId, setSiteId] = useState<string>(
    device.site ? String(device.site.id) : NONE
  );
  const [result, setResult] = useState<SnmpInventoryResult | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState(false);
  const [committed, setCommitted] = useState(false);

  useEffect(() => {
    if (!open) return;
    api
      .get<Vrf[]>("/api/v1/vrfs")
      .then((list) => {
        setVrfs(list);
        if (!vrfId) {
          const global =
            list.find((v) => v.rd === null && !v.site_id) ?? list[0];
          if (global) setVrfId(String(global.id));
        }
      })
      .catch((e) =>
        toast.error("Could not load VRFs", { description: String(e) })
      );
    api
      .get<{ items: Site[] }>("/api/v1/sites")
      .then((p) => setSites(p.items))
      .catch((e) =>
        toast.error("Could not load sites", { description: String(e) })
      );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const sections = useMemo(() => {
    const by: Record<string, SnmpInventoryRow[]> = {
      vlans: [],
      subnets: [],
      addresses: [],
    };
    for (const r of result?.rows ?? []) {
      (by[r.section] ?? (by[r.section] = [])).push(r);
    }
    return by;
  }, [result]);

  const preview = async () => {
    if (!vrfId) {
      toast.error("Pick a VRF first");
      return;
    }
    setBusy(true);
    setCommitted(false);
    try {
      const r = await api.post<SnmpInventoryResult>(
        `/api/v1/devices/${device.id}/snmp/inventory-preview`,
        {
          vrf_id: Number(vrfId),
          site_id: siteId === NONE ? null : Number(siteId),
        }
      );
      setResult(r);
      // Default: every applyable row selected (the tick-the-scope pattern).
      setSelected(
        new Set(r.rows.filter((x) => APPLYABLE.has(x.action)).map((x) => x.key))
      );
      if (!r.up) toast.error("SNMP unreachable", { description: r.error });
      else if (r.errors.length)
        toast.warning("Some tables failed", {
          description: r.errors.join(" · "),
        });
    } catch (e) {
      toast.error("Preview failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const toggle = (key: string, on: boolean) => {
    setSelected((cur) => {
      const next = new Set(cur);
      if (on) next.add(key);
      else next.delete(key);
      return next;
    });
  };

  const toggleAll = (rows: SnmpInventoryRow[], on: boolean) => {
    setSelected((cur) => {
      const next = new Set(cur);
      for (const r of rows) {
        if (on) next.add(r.key);
        else next.delete(r.key);
      }
      return next;
    });
  };

  const apply = async () => {
    if (!result) return;
    setBusy(true);
    try {
      const selections: Record<string, string[]> = {};
      for (const [sec, rows] of Object.entries(sections)) {
        selections[sec] = rows
          .filter((r) => selected.has(r.key))
          .map((r) => r.key);
      }
      const r = await api.post<SnmpInventoryResult>(
        `/api/v1/devices/${device.id}/snmp/inventory-apply`,
        {
          vrf_id: Number(vrfId),
          site_id: siteId === NONE ? null : Number(siteId),
          selections,
        }
      );
      setResult(r);
      setCommitted(r.committed);
      if (r.committed) {
        toast.success("Inventory synced", {
          description:
            `${r.counts.create ?? 0} created, ${r.counts.update ?? 0} updated` +
            (r.batch_id ? ` — batch #${r.batch_id}` : ""),
        });
        onCommitted();
      }
    } catch (e) {
      toast.error("Apply failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const reset = () => {
    setResult(null);
    setSelected(new Set());
    setCommitted(false);
  };

  const applyableCount = (result?.rows ?? []).filter(
    (r) => APPLYABLE.has(r.action) && selected.has(r.key)
  ).length;

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) reset();
        onOpenChange(v);
      }}
    >
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Network className="h-5 w-5 text-emerald-400" /> Pull inventory
          </DialogTitle>
          <DialogDescription>
            Read the device's own VLANs, routed interfaces and ARP table over
            SNMP (read-only), review the plan, then apply in one transaction.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Target VRF</Label>
              <Select
                value={vrfId}
                onValueChange={(v) => {
                  setVrfId(v);
                  setResult(null);
                  setCommitted(false);
                }}
                disabled={committed}
              >
                <SelectTrigger>
                  <SelectValue placeholder="pick a VRF" />
                </SelectTrigger>
                <SelectContent>
                  {vrfs.map((v) => (
                    <SelectItem key={v.id} value={String(v.id)}>
                      {v.name}
                      {v.rd ? ` (${v.rd})` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Site (for created VLANs/subnets)</Label>
              <Select
                value={siteId}
                onValueChange={setSiteId}
                disabled={committed}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={NONE}>
                    <span className="text-muted-foreground">(none)</span>
                  </SelectItem>
                  {sites.map((s) => (
                    <SelectItem key={s.id} value={String(s.id)}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {result && !result.up && (
            <div className="rounded border border-rose-700/50 bg-rose-950/20 p-2 text-xs text-rose-300">
              {result.error || "no answer"}
            </div>
          )}
          {result?.errors.length ? (
            <div className="space-y-1">
              {result.errors.map((e) => (
                <p key={e} className="text-xs text-amber-400">
                  {e}
                </p>
              ))}
            </div>
          ) : null}

          {result?.up && (
            <>
              <CountCards counts={result.counts} />
              {(["vlans", "subnets", "addresses"] as const).map((sec) => (
                <SectionTable
                  key={sec}
                  section={sec}
                  rows={sections[sec] ?? []}
                  selected={selected}
                  onToggle={toggle}
                  onToggleAll={toggleAll}
                  committed={committed}
                />
              ))}
              {committed && (
                <p className="text-xs text-muted-foreground">
                  Committed — provenance lives on import batch #
                  {result.batch_id}.
                </p>
              )}
            </>
          )}
        </div>

        <DialogFooter className="gap-2">
          {!result?.up ? (
            <Button onClick={() => void preview()} disabled={busy || !vrfId}>
              {busy && <Loader2 className="h-4 w-4 animate-spin" />}
              <DownloadCloud className="h-4 w-4" /> Preview
            </Button>
          ) : (
            <>
              <Button
                variant="outline"
                onClick={() => void preview()}
                disabled={busy || committed}
              >
                Re-preview
              </Button>
              <Button
                onClick={() => void apply()}
                disabled={busy || committed || applyableCount === 0}
              >
                {busy && <Loader2 className="h-4 w-4 animate-spin" />}
                Apply ({applyableCount})
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
