"use client";

import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Download,
  History,
  Loader2,
  Plus,
  Printer,
  Radar,
  Split,
  Trash2,
  Upload,
  Zap,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { usePrefs } from "@/lib/prefs";
import {
  useUrlFlag,
  useUrlParams,
  useUrlSet,
  useUrlText,
} from "@/lib/url-state";
import { cn, intToIp } from "@/lib/utils";
import type {
  AddressPage,
  IpAddress,
  IpRange,
  IpRole,
  IpStatus,
  Prefix,
  Tag,
} from "@/types";
import { AddressFilterPanel } from "@/components/address-filter-panel";
import { AsyncPanel } from "@/components/async-panel";
import { PrefixBreadcrumbs } from "@/components/breadcrumbs";
import { AddressList, AddrMapViewSwitcher } from "@/components/address-list";
import { HistoryDialog } from "@/components/history-panel";
import { IpDrawer } from "@/components/ip-drawer";
import { usePrefixScanOverlay } from "@/components/quick-scan";
import { SavedViews } from "@/components/saved-views";
import { PrefixStatusBadge } from "@/components/status-badge";
import { SubnetGrid } from "@/components/subnet-grid";
import { TagChip, useTags } from "@/components/tag-picker";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/separator";
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

const MAX_GRID = 65536; // /16 and smaller render as a grid; bigger -> table
const IP_STATUSES: IpStatus[] = [
  "active",
  "reserved",
  "dhcp",
  "discovered",
  "offline",
];
const IP_ROLES: IpRole[] = ["vip", "vrrp", "hsrp", "glbp", "carp", "secondary"];
const RANGE_ROLES = ["dhcp", "pool", "reserved"];

function toggleIn<T>(set: Set<T>, v: T): Set<T> {
  const next = new Set(set);
  if (next.has(v)) next.delete(v);
  else next.add(v);
  return next;
}

function RangeDialog({
  open,
  onOpenChange,
  prefix,
  onSaved,
  initial,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  prefix: Prefix;
  onSaved: () => void;
  /** Pre-filled bounds, e.g. from a subnet-grid span selection. */
  initial?: { start: string; end: string } | null;
}) {
  const [form, setForm] = useState({ start: "", end: "", role: "dhcp", description: "" });
  const [busy, setBusy] = useState(false);
  const uid = useId();

  useEffect(() => {
    if (open)
      setForm({
        start: initial?.start ?? "",
        end: initial?.end ?? "",
        role: "dhcp",
        description: "",
      });
  }, [open, initial]);

  const submit = async () => {
    setBusy(true);
    try {
      await api.post("/api/v1/ranges", {
        prefix_id: prefix.id,
        start_address: form.start,
        end_address: form.end,
        role: form.role,
        description: form.description || null,
      });
      toast.success("Range created");
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New IP range in {prefix.prefix}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-start`}>Start address</Label>
              <Input
                id={`${uid}-start`}
                placeholder="10.0.0.100"
                value={form.start}
                onChange={(e) => setForm({ ...form, start: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-end`}>End address</Label>
              <Input
                id={`${uid}-end`}
                placeholder="10.0.0.199"
                value={form.end}
                onChange={(e) => setForm({ ...form, end: e.target.value })}
              />
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-role`}>Role</Label>
            <Select
              value={form.role}
              onValueChange={(v) => setForm({ ...form, role: v })}
            >
              <SelectTrigger id={`${uid}-role`}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {RANGE_ROLES.map((r) => (
                  <SelectItem key={r} value={r}>
                    {r}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-description`}>Description</Label>
            <Input
              id={`${uid}-description`}
              placeholder="e.g. DHCP pool"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !form.start || !form.end}>
            {busy ? "Creating…" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

interface SplitPlan {
  mask: number;
  children: string[];
  existing: string[];
}

function SplitDialog({
  open,
  onOpenChange,
  prefix,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  prefix: Prefix;
  onSaved: () => void;
}) {
  const curMask = Number(prefix.prefix.split("/")[1] ?? 0);
  const isV4 = !prefix.prefix.includes(":");
  // Cap at 64 children per split — beyond that bulk-create is unwieldy.
  const maxMask = Math.min(curMask + 6, isV4 ? 32 : 128);
  const maskOptions = useMemo(
    () =>
      Array.from(
        { length: Math.max(0, maxMask - curMask) },
        (_, i) => curMask + i + 1
      ),
    [curMask, maxMask]
  );

  const [mask, setMask] = useState(curMask + 1);
  const [childStatus, setChildStatus] = useState("active");
  const [plan, setPlan] = useState<SplitPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [sel, setSel] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState(false);
  const uid = useId();

  const loadPlan = useCallback(
    async (m: number) => {
      setLoading(true);
      try {
        const r = await api.get<SplitPlan>(
          `/api/v1/prefixes/${prefix.id}/split?mask=${m}`
        );
        setPlan(r);
        const existing = new Set(r.existing);
        setSel(new Set(r.children.filter((c) => !existing.has(c))));
      } catch (e) {
        setPlan(null);
        setSel(new Set());
        toast.error("Split preview failed", { description: String(e) });
      } finally {
        setLoading(false);
      }
    },
    [prefix.id]
  );

  useEffect(() => {
    if (open) {
      setMask(curMask + 1);
      setChildStatus("active");
      void loadPlan(curMask + 1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reset on each open
  }, [open]);

  const existingSet = useMemo(
    () => new Set(plan?.existing ?? []),
    [plan]
  );
  const creatable = plan ? plan.children.length - existingSet.size : 0;
  const isContainer = prefix.status === "container";

  const toggleAll = () => {
    if (!plan) return;
    setSel(
      sel.size >= creatable
        ? new Set()
        : new Set(plan.children.filter((c) => !existingSet.has(c)))
    );
  };

  const create = async () => {
    if (!plan) return;
    setBusy(true);
    let created = 0;
    const failed: string[] = [];
    for (const c of plan.children.filter((c) => sel.has(c))) {
      try {
        await api.post("/api/v1/prefixes", {
          prefix: c,
          vrf_id: prefix.vrf_id,
          site_id: prefix.site_id,
          vlan_id: prefix.vlan_id,
          status: childStatus,
        });
        created++;
      } catch {
        failed.push(c);
      }
    }
    setBusy(false);
    if (created > 0) {
      toast.success(`Created ${created} subnet${created === 1 ? "" : "s"}`);
      onSaved();
    }
    if (failed.length > 0) {
      toast.error(`${failed.length} subnet(s) could not be created`, {
        description:
          failed.slice(0, 3).join(", ") + (failed.length > 3 ? "…" : ""),
      });
      void loadPlan(mask); // refresh so new children show as existing
    } else {
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Split {prefix.prefix}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-mask`}>New mask</Label>
              <Select
                value={String(mask)}
                onValueChange={(v) => {
                  const m = Number(v);
                  setMask(m);
                  void loadPlan(m);
                }}
              >
                <SelectTrigger id={`${uid}-mask`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {maskOptions.map((m) => (
                    <SelectItem key={m} value={String(m)}>
                      /{m} · {2 ** (m - curMask)} subnets
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-child-status`}>Child status</Label>
              <Select value={childStatus} onValueChange={setChildStatus}>
                <SelectTrigger id={`${uid}-child-status`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["active", "container", "reserved"].map((s) => (
                    <SelectItem key={s} value={s}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {!isContainer && (
            <p className="rounded-md border border-amber-500/40 bg-amber-500/10 p-2 text-xs text-amber-400">
              Children of a &quot;{prefix.status}&quot; prefix overlap it and
              will be rejected — set the prefix status to &quot;container&quot;
              first.
            </p>
          )}

          <div className="grid gap-1.5">
            <div className="flex items-center justify-between">
              <Label id={`${uid}-subnets`}>Subnets to create</Label>
              {plan && creatable > 0 && (
                <button
                  onClick={toggleAll}
                  className="text-xs text-muted-foreground hover:text-foreground"
                >
                  {sel.size >= creatable ? "Deselect all" : "Select all"}
                </button>
              )}
            </div>
            <div
              role="group"
              aria-labelledby={`${uid}-subnets`}
              className="max-h-56 space-y-0.5 overflow-auto rounded-md border p-2"
            >
              {loading && (
                <div className="flex items-center gap-2 p-2 text-xs text-muted-foreground">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" /> Computing…
                </div>
              )}
              {!loading && !plan && (
                <p className="p-2 text-xs text-muted-foreground">
                  No split plan available.
                </p>
              )}
              {!loading &&
                plan?.children.map((c) => {
                  const exists = existingSet.has(c);
                  return (
                    <div
                      key={c}
                      onClick={() => {
                        if (exists) return;
                        const next = new Set(sel);
                        if (next.has(c)) next.delete(c);
                        else next.add(c);
                        setSel(next);
                      }}
                      className={cn(
                        "flex items-center gap-2 rounded px-1.5 py-1 font-mono text-xs",
                        exists
                          ? "text-muted-foreground"
                          : "cursor-pointer hover:bg-accent/50"
                      )}
                    >
                      <Checkbox
                        checked={exists || sel.has(c)}
                        disabled={exists}
                        aria-label={
                          exists ? `${c} (already exists)` : `Select ${c}`
                        }
                        onCheckedChange={(v) => {
                          const next = new Set(sel);
                          if (v) next.add(c);
                          else next.delete(c);
                          setSel(next);
                        }}
                      />
                      {c}
                      {exists && (
                        <Badge variant="outline" className="ml-auto">
                          exists
                        </Badge>
                      )}
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button
            onClick={create}
            disabled={busy || sel.size === 0 || !isContainer}
            title={
              !isContainer
                ? "Only container prefixes can be split"
                : undefined
            }
          >
            {busy
              ? "Creating…"
              : `Create ${sel.size} subnet${sel.size === 1 ? "" : "s"}`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function PrefixDetailPage({ id }: { id: string }) {
  const prefixId = Number(id);
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [prefs, setPrefs] = usePrefs();
  const prefixQ = useAsyncData(
    () => api.get<Prefix>(`/api/v1/prefixes/${prefixId}`),
    [prefixId]
  );
  const pageQ = useAsyncData(
    () =>
      api.get<AddressPage>(
        `/api/v1/prefixes/${prefixId}/addresses?limit=20000`
      ),
    [prefixId]
  );
  const rangesQ = useAsyncData(async () => {
    try {
      return await api.get<IpRange[]>(`/api/v1/ranges?prefix_id=${prefixId}`);
    } catch (e) {
      toast.error("Could not load IP ranges", { description: String(e) });
      return [];
    }
  }, [prefixId]);
  const prefix = prefixQ.data;
  const page = pageQ.data;
  const ranges = rangesQ.data ?? [];
  const [drawer, setDrawer] = useState<{ ip: string; addr: IpAddress | null } | null>(null);
  const [rangeOpen, setRangeOpen] = useState(false);
  const [rangePrefill, setRangePrefill] = useState<{
    start: string;
    end: string;
  } | null>(null);
  const [splitOpen, setSplitOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  // Subnet-grid span selection (W7) — address-int bounds, not DOM nodes.
  const [spanSel, setSpanSel] = useState<{ lo: number; hi: number } | null>(
    null
  );
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [search, setSearch, setSearchNow] = useUrlText("q");
  const [statusSel, setStatusSel] = useUrlSet<IpStatus>("status");
  const [tagSelRaw, setTagSelRaw] = useUrlSet("tags");
  const tagSel = useMemo(
    () => new Set([...tagSelRaw].map(Number).filter((n) => !isNaN(n))),
    [tagSelRaw]
  );
  const setTagSel = (s: Set<number>) =>
    setTagSelRaw(new Set([...s].map(String)));
  const [untagged, setUntagged] = useUrlFlag("untagged");
  const { searchParams, setParams } = useUrlParams();
  const [focusInt, setFocusInt] = useState<number | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const { tags, byObject: addrTags, refresh: refreshTags } = useTags("IPAddress");

  // Live scan overlay (F15): when a queued/running scan covers this prefix,
  // stream its found-host deltas and light up the matching grid cells.
  const settleScan = useCallback(() => void pageQ.reload(), [pageQ.reload]);
  const { found: scanFound, scanning } = usePrefixScanOverlay(
    prefixId,
    prefix?.prefix ?? null,
    settleScan
  );

  const refresh = useCallback(() => {
    void prefixQ.reload();
    void pageQ.reload();
    void rangesQ.reload();
    refreshTags();
    setSelected(new Set());
  }, [prefixQ.reload, pageQ.reload, rangesQ.reload, refreshTags]);

  const allocNext = async () => {
    try {
      const r = await api.post<{ address: string }>(
        `/api/v1/prefixes/${prefixId}/available-ips`,
        {}
      );
      toast.success(`Reserved ${r.address}`);
      refresh();
    } catch (e) {
      toast.error("Allocation failed", { description: String(e) });
    }
  };

  const removeRange = async (r: IpRange) => {
    try {
      await api.del(`/api/v1/ranges/${r.id}`);
      toast.success("Range deleted");
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const importCsv = async (file: File) => {
    try {
      const rows = await api.postRaw<{ row: number; ok: boolean; detail: string }[]>(
        "/api/v1/addresses/import",
        await file.text()
      );
      const ok = rows.filter((r) => r.ok).length;
      const bad = rows.filter((r) => !r.ok);
      toast.success(`Imported ${ok} addresses`, {
        description: bad.length
          ? `${bad.length} rows skipped — nothing imported (fix errors and retry)`
          : undefined,
      });
      if (bad.length) console.warn("import errors", bad);
      refresh();
    } catch (e) {
      toast.error("Import failed", { description: String(e) });
    }
  };

  const bulk = async (
    payload: {
      action: string;
      status?: IpStatus;
      role?: IpRole | null;
      tag_id?: number;
    },
    ids: number[] = [...selected]
  ) => {
    try {
      const r = await api.post<{ affected: number; not_found: number[] }>(
        "/api/v1/addresses/bulk",
        { ids, ...payload }
      );
      const verb = payload.action === "delete" ? "deleted" : "updated";
      toast.success(`${r.affected} of ${ids.length} ${verb}`, {
        description: r.not_found?.length
          ? `${r.not_found.length} not found (already gone)`
          : undefined,
      });
      refresh();
    } catch (e) {
      toast.error("Bulk update failed", { description: String(e) });
    }
  };

  // Optimistic single-field patch used by the inline-editable cells in the
  // address list — rolls the field back on failure.
  const patchAddr = async (id: number, patch: Partial<IpAddress>) => {
    let prev: IpAddress | undefined;
    pageQ.setData((cur) => {
      if (!cur) return cur;
      prev = cur.items.find((a) => a.id === id);
      return {
        ...cur,
        items: cur.items.map((a) => (a.id === id ? { ...a, ...patch } : a)),
      };
    });
    try {
      const saved = await api.patch<IpAddress>(`/api/v1/addresses/${id}`, patch);
      // display_color is server-computed (manual > rule) — take it back so
      // clearing a manual color restores the rule tint without a refetch.
      pageQ.setData((cur) =>
        cur
          ? {
              ...cur,
              items: cur.items.map((a) =>
                a.id === id
                  ? {
                      ...a,
                      row_color: saved.row_color,
                      display_color: saved.display_color,
                    }
                  : a
              ),
            }
          : cur
      );
    } catch (e) {
      pageQ.setData((cur) =>
        cur
          ? {
              ...cur,
              items: cur.items.map((a) =>
                a.id === id && prev ? prev : a
              ),
            }
          : cur
      );
      toast.error("Save failed", { description: String(e) });
      throw e;
    }
  };

  const spanIds = useMemo(
    () =>
      spanSel == null
        ? []
        : (page?.items ?? [])
            .filter(
              (a) =>
                Number(a.address_int) >= spanSel.lo &&
                Number(a.address_int) <= spanSel.hi
            )
            .map((a) => a.id),
    [spanSel, page]
  );

  const isV4 = !!prefix && !prefix.prefix.includes(":");
  const showGrid = isV4 && (page?.total ?? 0) <= MAX_GRID;
  // ?view= overrides the stored pref; absent param -> pref.
  const viewParam = searchParams.get("view");
  const viewSel =
    viewParam === "list" || viewParam === "grid" ? viewParam : prefs.addrMapView;
  const view = showGrid && viewSel === "grid" ? "grid" : "list";

  const filtersActive =
    !!search || statusSel.size > 0 || tagSel.size > 0 || untagged;

  const filtered = useMemo(() => {
    const ql = search.trim().toLowerCase();
    return (page?.items ?? []).filter((a) => {
      if (ql) {
        const hay = [a.address, a.hostname, a.mac_address, a.vendor];
        if (!hay.some((v) => v && v.toLowerCase().includes(ql))) return false;
      }
      if (statusSel.size && !statusSel.has(a.status)) return false;
      const at = addrTags.get(a.id) ?? [];
      if (untagged && at.length > 0) return false;
      if (tagSel.size && !at.some((t) => tagSel.has(t.id))) return false;
      return true;
    });
  }, [page, search, statusSel, tagSel, untagged, addrTags]);

  const matchIds = useMemo(
    () => (filtersActive ? new Set(filtered.map((a) => a.id)) : null),
    [filtersActive, filtered]
  );

  const highlight = useMemo(() => {
    const m = new Map<number, string>();
    if (!tagSel.size) return m;
    for (const a of filtered) {
      const hit = (addrTags.get(a.id) ?? []).find((t) => tagSel.has(t.id));
      if (hit) m.set(a.id, hit.color);
    }
    return m;
  }, [filtered, tagSel, addrTags]);

  const clearFilters = () =>
    setSearchNow("", { status: null, tags: null, untagged: null });

  // Export mirrors the on-screen filter state — same params the backend
  // export endpoint accepts; display-only params (view, sort) stay out.
  const exportHref = useMemo(() => {
    const p = new URLSearchParams({ prefix_id: String(prefixId) });
    if (search.trim()) p.set("q", search.trim());
    if (statusSel.size) p.set("status", [...statusSel].join(","));
    if (tagSel.size) p.set("tags", [...tagSel].join(","));
    if (untagged) p.set("untagged", "1");
    return `/api/v1/addresses/export.csv?${p}`;
  }, [prefixId, search, statusSel, tagSel, untagged]);

  const pickAddress = (a: IpAddress) => {
    setFocusInt(Number(a.address_int));
    setDrawer({ ip: a.address, addr: a });
  };

  const allChecked =
    filtered.length > 0 && filtered.every((a) => selected.has(a.id));

  return (
    <div className="space-y-4">
      <PrefixBreadcrumbs prefixId={prefixId} />
      <div className="flex flex-wrap items-center gap-3">
        <Button variant="ghost" size="icon" aria-label="Back to subnets" asChild>
          <Link href="/prefixes" aria-label="Back to subnets">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        {prefix ? (
          <>
            <h1 className="font-mono text-xl font-semibold">{prefix.prefix}</h1>
            <PrefixStatusBadge s={prefix.status} />
            {prefix.vlan && (
              <span className="text-sm text-muted-foreground">
                VLAN {prefix.vlan.vid} · {prefix.vlan.name}
              </span>
            )}
          </>
        ) : prefixQ.loading ? (
          <Skeleton className="h-7 w-48" />
        ) : (
          <span className="text-sm text-rose-400">
            Couldn&apos;t load prefix — {prefixQ.error}
          </span>
        )}
        <div className="ml-auto flex gap-2">
          {canWrite && (
            <>
              <Button size="sm" variant="outline" onClick={() => fileRef.current?.click()}>
                <Upload /> Import
              </Button>
              <input
                ref={fileRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) importCsv(f);
                  e.target.value = "";
                }}
              />
            </>
          )}
          <Button size="sm" variant="outline" asChild>
            <a href={exportHref} download title="Downloads the rows the current filters show">
              <Download /> {filtersActive ? "Export filtered" : "Export"}
            </a>
          </Button>
          <Button size="sm" variant="outline" asChild>
            <Link href={`/prefixes/${prefixId}/print`}>
              <Printer /> Print report
            </Link>
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setHistoryOpen(true)}
          >
            <History /> History
          </Button>
          <SavedViews pageKey="prefix-detail" />
          {canWrite && (
            <>
              <Button size="sm" variant="outline" onClick={() => setRangeOpen(true)}>
                <Plus /> IP range
              </Button>
              {prefix && Number(prefix.prefix.split("/")[1]) < (isV4 ? 32 : 128) && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setSplitOpen(true)}
                >
                  <Split /> Split subnet
                </Button>
              )}
              <Button size="sm" onClick={allocNext}>
                <Zap /> Allocate next free IP
              </Button>
            </>
          )}
        </div>
      </div>

      {prefix && (
        <Card>
          <CardContent className="flex items-center gap-6 p-4 text-sm">
            <div className="w-56">
              <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                <span>utilization</span>
                <span>{prefix.utilization_pct}%</span>
              </div>
              <Progress value={prefix.utilization_pct} />
            </div>
            <span>{prefix.used_ips.toLocaleString()} used</span>
            <span className="text-muted-foreground">
              {prefix.free_ips.toLocaleString()} free of{" "}
              {prefix.usable_ips.toLocaleString()} usable
            </span>
            {ranges.length > 0 && (
              <span className="text-sky-400">
                {ranges.length} range{ranges.length > 1 ? "s" : ""}
              </span>
            )}
            {prefix.description && (
              <span className="ml-auto text-muted-foreground">{prefix.description}</span>
            )}
          </CardContent>
        </Card>
      )}

      {ranges.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">IP ranges</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Range</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead className="w-16 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ranges.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-mono">
                      {r.start_address} – {r.end_address}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{r.role}</Badge>
                    </TableCell>
                    <TableCell>
                      {(Number(r.end_int) - Number(r.start_int) + 1).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {r.description ?? "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      {canDelete && (
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Delete range ${r.start_address}–${r.end_address}`}
                          onClick={() => removeRange(r)}
                        >
                          <Trash2 className="h-4 w-4 text-rose-400" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            <span className="flex items-center gap-3">
              Address map
              {scanning && (
                <Badge
                  variant="outline"
                  role="status"
                  className="gap-1.5 border-emerald-500/50 font-normal text-emerald-600 dark:text-emerald-400"
                >
                  <Radar className="h-3 w-3 animate-pulse" aria-hidden="true" />
                  Scanning — {scanFound.size} found
                </Badge>
              )}
              {showGrid && (
                <AddrMapViewSwitcher
                  view={view}
                  onChange={(v) => {
                    setPrefs({ addrMapView: v });
                    setParams({ view: v });
                  }}
                />
              )}
            </span>
            <span className="flex gap-3 text-xs font-normal text-muted-foreground">
              <i className="flex items-center gap-1"><i className="ipcell-active h-2.5 w-2.5 rounded-sm" />active</i>
              <i className="flex items-center gap-1"><i className="ipcell-discovered h-2.5 w-2.5 rounded-sm" />discovered</i>
              <i className="flex items-center gap-1"><i className="ipcell-reserved h-2.5 w-2.5 rounded-sm" />reserved</i>
              <i className="flex items-center gap-1"><i className="ipcell-dhcp h-2.5 w-2.5 rounded-sm" />dhcp</i>
              <i className="flex items-center gap-1"><i className="ipcell-range h-2.5 w-2.5 rounded-sm" />range</i>
              <i className="flex items-center gap-1"><i className="ipcell-offline h-2.5 w-2.5 rounded-sm" />offline</i>
              <i className="flex items-center gap-1"><i className="ipcell-free h-2.5 w-2.5 rounded-sm" />free</i>
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AsyncPanel
            loading={pageQ.loading}
            error={pageQ.error}
            onRetry={pageQ.reload}
            skeleton={<Skeleton className="h-64 w-full" />}
            empty={!page}
            emptyMessage="No addresses in this prefix."
          >
            {page && (
            <div className="flex flex-col gap-4 lg:flex-row">
              <div className="min-w-0 flex-1">
                {view === "grid" ? (
                  <SubnetGrid
                    page={page}
                    ranges={ranges}
                    onSelect={(ip, addr) => setDrawer({ ip, addr })}
                    tags={addrTags}
                    matchIds={matchIds}
                    highlight={highlight}
                    focusInt={focusInt}
                    spanSel={spanSel}
                    onSpanSelect={(lo, hi) => setSpanSel({ lo, hi })}
                    onClearSpan={() => setSpanSel(null)}
                    spanSelectable={canWrite}
                    liveFound={scanFound}
                  />
                ) : (
                  <AddressList
                    page={page}
                    ranges={ranges}
                    filtered={filtered}
                    filtersActive={filtersActive}
                    tags={addrTags}
                    allTags={tags}
                    highlight={highlight}
                    focusInt={focusInt}
                    selectable={canWrite}
                    canDelete={canDelete}
                    onPatchAddr={patchAddr}
                    editable={canWrite}
                    selected={selected}
                    onToggle={(id, on) => {
                      const next = new Set(selected);
                      if (on) next.add(id);
                      else next.delete(id);
                      setSelected(next);
                    }}
                    onToggleAll={(on) =>
                      setSelected(
                        on ? new Set(filtered.map((a) => a.id)) : new Set()
                      )
                    }
                    allChecked={allChecked}
                    onTagsChanged={refreshTags}
                    onSelect={(a) => setDrawer({ ip: a.address, addr: a })}
                    onSelectFree={(ip) => setDrawer({ ip, addr: null })}
                    onChanged={refresh}
                  />
                )}
              </div>
              <aside className="w-full shrink-0 lg:w-72">
                <AddressFilterPanel
                  items={page.items}
                  filtered={filtered}
                  tags={tags}
                  addrTags={addrTags}
                  search={search}
                  onSearch={setSearch}
                  statusSel={statusSel}
                  onToggleStatus={(s) => setStatusSel(toggleIn(statusSel, s))}
                  tagSel={tagSel}
                  onToggleTag={(id) => setTagSel(toggleIn(tagSel, id))}
                  untagged={untagged}
                  onToggleUntagged={() => setUntagged(!untagged)}
                  onClear={clearFilters}
                  onSelectMatching={() =>
                    setSelected(new Set(filtered.map((a) => a.id)))
                  }
                  onPick={pickAddress}
                  onTagsChanged={refreshTags}
                />
              </aside>
            </div>
            )}
          </AsyncPanel>
        </CardContent>
      </Card>

      {spanSel !== null && canWrite && view === "grid" && (
        <div className="sticky bottom-4 z-10 mx-auto flex w-fit items-center gap-3 rounded-lg border bg-card px-4 py-2 shadow-lg">
          <span role="status" className="text-sm text-muted-foreground">
            {spanSel.hi - spanSel.lo + 1} selected (
            <span className="font-mono">
              {intToIp(spanSel.lo)}–{intToIp(spanSel.hi)}
            </span>
            )
          </span>
          <Select
            onValueChange={(v) =>
              void bulk(
                { action: "set_status", status: v as IpStatus },
                spanIds
              ).then(() => setSpanSel(null))
            }
            disabled={spanIds.length === 0}
          >
            <SelectTrigger className="h-8 w-40">
              <SelectValue
                placeholder={
                  spanIds.length
                    ? `Set status (${spanIds.length} addrs)…`
                    : "No addresses in span"
                }
              />
            </SelectTrigger>
            <SelectContent>
              {IP_STATUSES.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setRangePrefill({
                start: intToIp(spanSel.lo),
                end: intToIp(spanSel.hi),
              });
              setRangeOpen(true);
            }}
          >
            <Plus /> Create range
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSpanSel(null)}
          >
            Clear
          </Button>
        </div>
      )}

      {selected.size > 0 && canWrite && (
        <div className="sticky bottom-4 z-10 mx-auto flex w-fit items-center gap-3 rounded-lg border bg-card px-4 py-2 shadow-lg">
          <span role="status" className="text-sm text-muted-foreground">
            {selected.size} selected
          </span>
          <Select onValueChange={(v) => bulk({ action: "set_status", status: v as IpStatus })}>
            <SelectTrigger className="h-8 w-36">
              <SelectValue placeholder="Set status…" />
            </SelectTrigger>
            <SelectContent>
              {IP_STATUSES.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select onValueChange={(v) => bulk({ action: "set_role", role: v as IpRole })}>
            <SelectTrigger className="h-8 w-32">
              <SelectValue placeholder="Set role…" />
            </SelectTrigger>
            <SelectContent>
              {IP_ROLES.map((r) => (
                <SelectItem key={r} value={r}>
                  {r}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                Tags
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Apply tag</DropdownMenuLabel>
              {tags.map((t) => (
                <DropdownMenuItem key={t.id} onClick={() => bulk({ action: "add_tag", tag_id: t.id })}>
                  <TagChip tag={t} />
                </DropdownMenuItem>
              ))}
              {tags.length > 0 && <DropdownMenuSeparator />}
              <DropdownMenuLabel>Remove tag</DropdownMenuLabel>
              {tags.map((t) => (
                <DropdownMenuItem
                  key={t.id}
                  onClick={() => bulk({ action: "remove_tag", tag_id: t.id })}
                >
                  <TagChip tag={t} />
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          {canDelete && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => bulk({ action: "delete" })}
            >
              <Trash2 /> Delete
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={() => setSelected(new Set())}>
            Clear
          </Button>
        </div>
      )}

      {drawer && (
        <IpDrawer
          open
          onOpenChange={(o) => !o && setDrawer(null)}
          ip={drawer.ip}
          addr={drawer.addr}
          prefixId={prefixId}
          onSaved={refresh}
          allTags={tags}
          assigned={drawer.addr ? (addrTags.get(drawer.addr.id) ?? []) : []}
          onTagsChanged={refreshTags}
        />
      )}
      {prefix && (
        <RangeDialog
          open={rangeOpen}
          onOpenChange={(o) => {
            setRangeOpen(o);
            if (!o) setRangePrefill(null);
          }}
          prefix={prefix}
          onSaved={refresh}
          initial={rangePrefill}
        />
      )}
      <HistoryDialog
        open={historyOpen}
        onOpenChange={setHistoryOpen}
        objectType="Prefix"
        objectId={prefixId}
        title={prefix?.prefix}
      />
      {prefix && (
        <SplitDialog
          open={splitOpen}
          onOpenChange={setSplitOpen}
          prefix={prefix}
          onSaved={refresh}
        />
      )}
    </div>
  );
}
