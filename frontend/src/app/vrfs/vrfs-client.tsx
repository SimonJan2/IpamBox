"use client";

import { useCallback, useEffect, useId, useMemo, useState } from "react";
import { History, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { useFeatureFlag } from "@/lib/features";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import { slugify } from "@/lib/utils";
import { useUrlText } from "@/lib/url-state";
import { useRowNav } from "@/lib/row-nav";
import { useRowColor, rowTintStyle } from "@/lib/row-color";
import { useRowOrder } from "@/lib/row-order";
import { cn } from "@/lib/utils";
import {
  DragHandle,
  PinToggle,
  PinnedDivider,
  RowOrderDnd,
  SortableRow,
} from "@/components/row-order";
import type { Page, Site, Vrf } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { HistoryDialog } from "@/components/history-panel";
import { InlineText } from "@/components/inline-edit";
import { RowColorLegend, RowColorPicker } from "@/components/row-color";
import { SavedViews } from "@/components/saved-views";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const NONE = "__none__";

// Same convention as the workbook importer (_vrf_name_for): the site code,
// then site-N, then a slug of the name.
const vrfNameFor = (s: Site) =>
  s.code ??
  (s.site_number != null ? `site-${s.site_number}` : slugify(s.name));

function VrfDialog({
  open,
  onOpenChange,
  vrf,
  sites,
  followSiteCode,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  vrf: Vrf | null;
  sites: Site[];
  followSiteCode: boolean;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: "",
    rd: "",
    site_id: NONE,
    description: "",
  });
  const [autoName, setAutoName] = useState(true);
  const [busy, setBusy] = useState(false);
  const uid = useId();

  useEffect(() => {
    if (open) {
      const site = sites.find((s) => s.id === vrf?.site_id);
      const stale = site != null && vrf != null && vrf.name !== vrfNameFor(site);
      setForm({
        name: followSiteCode && stale ? vrfNameFor(site) : (vrf?.name ?? ""),
        rd: vrf?.rd ?? "",
        site_id: vrf?.site_id ? String(vrf.site_id) : NONE,
        description: vrf?.description ?? "",
      });
      // Only assume the convention when the existing name already matches
      // what the site would produce — protects Global/custom names.
      // followSiteCode (Settings > Features) treats the mismatch as stale
      // instead: re-derive the name and keep the toggle on.
      setAutoName(
        vrf == null ? true : site != null && (followSiteCode || vrf.name === vrfNameFor(site))
      );
    }
  }, [open, vrf, sites, followSiteCode]);

  const onSiteChange = (v: string) => {
    const site = sites.find((s) => String(s.id) === v);
    setForm({
      ...form,
      site_id: v,
      ...(autoName ? { name: site ? vrfNameFor(site) : "" } : {}),
    });
  };

  const onAutoName = (on: boolean) => {
    setAutoName(on);
    if (on) {
      const site = sites.find((s) => String(s.id) === form.site_id);
      setForm({ ...form, name: site ? vrfNameFor(site) : "" });
    }
  };

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        name: form.name,
        rd: form.rd || null,
        site_id: form.site_id === NONE ? null : Number(form.site_id),
        description: form.description || null,
      };
      if (vrf) {
        await api.patch(`/api/v1/vrfs/${vrf.id}`, body);
        toast.success("VRF updated");
      } else {
        await api.post("/api/v1/vrfs", body);
        toast.success("VRF created");
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
          <DialogTitle>{vrf ? "Edit VRF" : "New VRF"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-site`}>Site</Label>
            <Select value={form.site_id} onValueChange={onSiteChange}>
              <SelectTrigger id={`${uid}-site`}>
                <SelectValue placeholder="None" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={NONE}>None</SelectItem>
                {sites.map((s) => (
                  <SelectItem key={s.id} value={String(s.id)}>
                    <span dir="auto">
                      {s.code ? `${s.code} — ` : ""}
                      {s.name}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor={`${uid}-name`}>Name</Label>
              <label className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Switch
                  checked={autoName}
                  onCheckedChange={onAutoName}
                  aria-label="Derive name from site code"
                />
                from site code
              </label>
            </div>
            <Input
              id={`${uid}-name`}
              placeholder={autoName ? "select a site" : "production"}
              value={form.name}
              disabled={autoName}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-rd`}>Route distinguisher</Label>
            <Input
              id={`${uid}-rd`}
              placeholder="65000:1 (optional)"
              value={form.rd}
              onChange={(e) => setForm({ ...form, rd: e.target.value })}
            />
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
            {busy ? "Saving…" : vrf ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DeleteDialog({
  vrf,
  onOpenChange,
  onDeleted,
}: {
  vrf: Vrf | null;
  onOpenChange: (o: boolean) => void;
  onDeleted: () => void;
}) {
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!vrf) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/vrfs/${vrf.id}`);
      toast.success(`Deleted ${vrf.name}`);
      onOpenChange(false);
      onDeleted();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={vrf !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete VRF</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Delete <span className="font-medium text-foreground">{vrf?.name}</span>?
          All prefixes and IP addresses inside it will be removed. This cannot be
          undone.
        </p>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={submit} disabled={busy}>
            {busy ? "Deleting…" : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function VrfsPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const followSiteCode = useFeatureFlag("site_code_follow_site");
  const vrfsQ = useAsyncData(() => api.get<Vrf[]>("/api/v1/vrfs"));
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Site>>("/api/v1/sites").then((p) => p.items);
    } catch (e) {
      toast.error("Could not load sites", { description: String(e) });
      return [];
    }
  });
  const [q, setQ] = useUrlText("q");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Vrf | null>(null);
  const [deleting, setDeleting] = useState<Vrf | null>(null);
  const [historyFor, setHistoryFor] = useState<Vrf | null>(null);

  const vrfs = vrfsQ.data ?? [];
  const sites = sitesQ.data ?? [];
  const refresh = () => void vrfsQ.reload();

  // Optimistic single-field patch for inline-editable cells.
  const saveField = useCallback(
    async (id: number, field: "description", value: string | null) => {
      let prev: Vrf | undefined;
      vrfsQ.setData((cur) => {
        prev = (cur ?? []).find((v) => v.id === id);
        return (cur ?? []).map((v) =>
          v.id === id ? { ...v, [field]: value } : v
        );
      });
      try {
        await api.patch(`/api/v1/vrfs/${id}`, { [field]: value });
      } catch (e) {
        vrfsQ.setData((cur) =>
          (cur ?? []).map((v) => (v.id === id && prev ? prev : v))
        );
        toast.error("Save failed", { description: String(e) });
        throw e;
      }
    },
    [vrfsQ.setData]
  );

  const siteName = useMemo(
    () => Object.fromEntries(sites.map((s) => [s.id, s.name])),
    [sites]
  );

  const filtered = vrfs.filter(
    (v) =>
      v.name.toLowerCase().includes(q.toLowerCase()) ||
      (v.rd ?? "").toLowerCase().includes(q.toLowerCase())
  );

  // No column sort on this page — only the search box blocks reordering.
  const orderBlock = q
    ? "Row order is fixed while searching — clear the search to drag."
    : null;
  const order = useRowOrder<Vrf>({
    path: "/api/v1/vrfs",
    items: vrfs,
    setData: vrfsQ.setData,
    getVisibleIds: (): number[] => filtered.map((v) => v.id),
    enabled: canWrite && !orderBlock,
  });
  const setRowColor = useRowColor<Vrf>({
    path: "/api/v1/vrfs",
    setData: vrfsQ.setData,
  });

  const { rowProps, focusRow } = useRowNav({
    count: filtered.length,
    onOpen: (i) => {
      const v = filtered[i];
      if (!v) return;
      if (canWrite) {
        setEditing(v);
        setDialogOpen(true);
      } else {
        setHistoryFor(v);
      }
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">VRFs</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New VRF
          </Button>
        )}
      </div>

      <div className="flex items-center gap-2">
        <Input
          placeholder="Search VRFs…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <RowColorLegend />
        <SavedViews pageKey="vrfs" className="ml-auto" />
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={vrfsQ.loading}
          error={vrfsQ.error}
          onRetry={vrfsQ.reload}
          empty={vrfs.length === 0}
          emptyMessage="No VRFs yet — create the first one."
        >
        <RowOrderDnd ids={filtered.map((v) => v.id)} onDragEnd={order.onDragEnd}>
        <Table>
          <TableHeader>
            <TableRow>
              {canWrite && (
                <TableHead className="w-8">
                  <span className="sr-only">Reorder</span>
                </TableHead>
              )}
              <TableHead>Name</TableHead>
              <TableHead>RD</TableHead>
              <TableHead>Site</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered[0]?.pinned && (
              <PinnedDivider colSpan={canWrite ? 7 : 6} />
            )}
            {filtered.map((v, i) => {
              const rp = rowProps(i);
              return (
              <SortableRow
                key={v.id}
                rowId={v.id}
                dragDisabled={!order.enabled}
                {...rp}
                onKeyDown={(e) => {
                  const ni = order.keyDown(i, e);
                  if (ni === null) rp.onKeyDown(e);
                  else focusRow(ni);
                }}
                style={rowTintStyle(v.display_color)}
                className={cn(
                  v.pinned && "bg-muted/30",
                  "focus-visible:bg-muted/50 focus-visible:outline-none"
                )}
              >
                {canWrite && (
                  <TableCell>
                    <DragHandle
                      reason={orderBlock}
                      label={`Reorder VRF ${v.name}`}
                    />
                  </TableCell>
                )}
                <TableCell className="font-medium">{v.name}</TableCell>
                <TableCell className="font-mono text-muted-foreground">
                  {v.rd ?? "—"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {v.site_id ? siteName[v.site_id] ?? "—" : "—"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  <InlineText
                    value={v.description}
                    onSave={(nv) => saveField(v.id, "description", nv || null)}
                    disabled={!canWrite}
                    dir="auto"
                    label={`Edit description for ${v.name}`}
                  />
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {fmtTs(v.created_at)}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    {canWrite && (
                      <PinToggle
                        pinned={v.pinned}
                        name={v.name}
                        onToggle={() => order.setPinned(v.id, !v.pinned)}
                      />
                    )}
                    {canWrite && (
                      <RowColorPicker
                        value={v.row_color}
                        displayColor={v.display_color}
                        name={v.name}
                        onPick={(color) => setRowColor(v.id, color)}
                      />
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`History of ${v.name}`}
                      onClick={() => setHistoryFor(v)}
                    >
                      <History className="h-4 w-4" />
                    </Button>
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Edit ${v.name}`}
                        onClick={() => {
                          setEditing(v);
                          setDialogOpen(true);
                        }}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                    )}
                    {canDelete && (
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Delete ${v.name}`}
                        onClick={() => setDeleting(v)}
                      >
                        <Trash2 className="h-4 w-4 text-rose-400" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </SortableRow>
              );
            })}
            {filtered.length === 0 && vrfs.length > 0 && (
              <TableRow>
                <TableCell
                  colSpan={canWrite ? 7 : 6}
                  className="py-10 text-center text-muted-foreground"
                >
                  No VRFs match this filter.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </RowOrderDnd>
        </AsyncPanel>
      </div>

      <VrfDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        vrf={editing}
        sites={sites}
        followSiteCode={followSiteCode}
        onSaved={refresh}
      />
      <DeleteDialog
        vrf={deleting}
        onOpenChange={() => setDeleting(null)}
        onDeleted={refresh}
      />
      <HistoryDialog
        open={historyFor !== null}
        onOpenChange={() => setHistoryFor(null)}
        objectType="VRF"
        objectId={historyFor?.id ?? null}
        title={historyFor?.name}
      />
    </div>
  );
}
