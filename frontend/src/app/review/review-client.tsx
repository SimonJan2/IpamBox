"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Check,
  ChevronDown,
  ClipboardCheck,
  Container,
  Copy,
  EyeOff,
  Inbox,
  Loader2,
  RotateCcw,
  ShieldAlert,
  Trash2,
  Unplug,
  Wand2,
  WifiOff,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { useAsyncData } from "@/lib/use-async-data";
import { cn, timeAgo } from "@/lib/utils";
import type {
  MatchFreeTextReport,
  ReviewEntityType,
  ReviewItem,
  ReviewOut,
  ReviewSection,
} from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { ConfirmDialog } from "@/components/confirm-action";
import { DocsLink } from "@/components/docs/docs-link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const ENC = encodeURIComponent;

const SECTION_ICONS: Record<string, React.ElementType> = {
  mac_mismatch: AlertTriangle,
  dup_mac: Copy,
  aging_discovery: Inbox,
  offline: WifiOff,
  cert_expiry: ShieldAlert,
  unmatched_switch: Unplug,
  uncabled: Unplug,
  unracked: Container,
};

/** Entity row DELETE endpoint — deletion goes through the entity's own
 *  endpoint so the changelog records a real delete. mac_group is virtual:
 *  no single row to delete, so no button. */
const DELETE_PATH: Record<ReviewEntityType, string | null> = {
  ip_address: "/api/v1/addresses",
  device: "/api/v1/devices",
  certificate: "/api/v1/certificates",
  mac_group: null,
};

function entityHref(item: ReviewItem): string | null {
  const prefixId = item.detail.prefix_id;
  switch (item.entity_type) {
    case "ip_address":
      return typeof prefixId === "number"
        ? `/prefixes/${prefixId}?q=${ENC(item.label)}`
        : "/prefixes";
    case "device":
      return `/devices/${item.entity_id}`;
    case "certificate":
      return `/certificates?q=${ENC(item.label)}`;
    case "mac_group":
      return null;
  }
}

/** The "why flagged" cell — per-section detail rendering. */
function WhyCell({ kind, item }: { kind: string; item: ReviewItem }) {
  const d = item.detail;
  switch (kind) {
    case "mac_mismatch":
      return (
        <span dir="ltr" className="font-mono text-xs">
          <span className="text-muted-foreground">{String(d.mac_was ?? "?")}</span>
          {" → "}
          <span className="text-amber-400">{String(d.mac_seen ?? "?")}</span>
        </span>
      );
    case "dup_mac": {
      const members = (d.members ?? []) as {
        id: number;
        address: string;
        hostname: string | null;
        prefix_id: number;
      }[];
      return (
        <span className="flex flex-wrap gap-x-2 gap-y-0.5 font-mono text-xs">
          {members.map((m) => (
            <Link
              key={m.id}
              href={`/prefixes/${m.prefix_id}?q=${ENC(m.address)}`}
              className="text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
            >
              {m.address}
            </Link>
          ))}
        </span>
      );
    }
    case "aging_discovery":
      return (
        <span className="text-muted-foreground">
          {item.flagged_at
            ? `last seen ${timeAgo(item.flagged_at)}`
            : "never seen"}
          {" · "}expires after {String(d.expire_days ?? "?")}d
        </span>
      );
    case "offline":
      return (
        <span className="text-muted-foreground">
          {String(d.missed_scans ?? "?")} missed scans
          {item.flagged_at ? ` · last seen ${timeAgo(item.flagged_at)}` : ""}
        </span>
      );
    case "cert_expiry": {
      const days = typeof d.days === "number" ? d.days : null;
      return (
        <span className={cn(days !== null && days < 0 && "text-red-400")}>
          expires {String(d.expires_on ?? "?")}
          {days !== null &&
            (days < 0 ? ` (${-days}d ago)` : ` (in ${days}d)`)}
        </span>
      );
    }
    case "unmatched_switch":
      return (
        <span className="text-muted-foreground">
          free text never matched an interface — run the resolver
        </span>
      );
    case "uncabled":
      return (
        <span className="text-muted-foreground">
          {String(d.interface_count ?? "?")} interfaces, zero cables
        </span>
      );
    case "unracked":
      return (
        <span className="text-muted-foreground">
          no rack placement
          {d.source ? ` · source ${String(d.source)}` : ""}
        </span>
      );
    default:
      return null;
  }
}

interface DismissTarget {
  kind: string;
  item: ReviewItem;
}

interface DeleteTarget {
  kind: string;
  item: ReviewItem;
}

export default function ReviewPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);

  const reviewQ = useAsyncData(() => api.get<ReviewOut>("/api/v1/review"));
  const sections = reviewQ.data?.sections ?? [];
  const openTotal = sections.reduce((n, s) => n + s.count, 0);

  const [openSecs, setOpenSecs] = useState<Record<string, boolean>>({});
  const [showDismissed, setShowDismissed] = useState<Record<string, boolean>>({});
  const [busy, setBusy] = useState<Set<string>>(new Set());
  const [dismissTarget, setDismissTarget] = useState<DismissTarget | null>(null);
  const [dismissNotes, setDismissNotes] = useState("");
  const [dismissBusy, setDismissBusy] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null);
  const [resolverBusy, setResolverBusy] = useState(false);
  const [resolverReport, setResolverReport] =
    useState<MatchFreeTextReport | null>(null);

  const reload = () => void reviewQ.reload();

  useEffect(() => {
    const onEv = () => void reviewQ.reload();
    window.addEventListener("ipam:refresh", onEv);
    return () => window.removeEventListener("ipam:refresh", onEv);
  }, [reviewQ.reload]);

  const key = (kind: string, it: ReviewItem) =>
    `${kind}:${it.entity_type}:${it.entity_id}:${it.fingerprint}`;

  const setBusyKey = (k: string, on: boolean) =>
    setBusy((s) => {
      const n = new Set(s);
      if (on) n.add(k);
      else n.delete(k);
      return n;
    });

  const act = async (kind: string, it: ReviewItem, fn: () => Promise<unknown>, ok: string) => {
    const k = key(kind, it);
    if (busy.has(k)) return;
    setBusyKey(k, true);
    try {
      await fn();
      toast.success(ok);
      await reviewQ.reload();
    } catch (e) {
      toast.error("Action failed", { description: String(e) });
    } finally {
      setBusyKey(k, false);
    }
  };

  const confirmDiscovery = (kind: string, it: ReviewItem) =>
    act(
      kind,
      it,
      () => api.post(`/api/v1/discovery/${it.entity_id}/confirm`, { status: "active" }),
      `${it.label} marked active`
    );

  const macAccept = (it: ReviewItem) =>
    act(
      "mac_mismatch",
      it,
      () => api.post(`/api/v1/review/mac_mismatch/${it.entity_id}/accept`),
      `${it.label}: scanned MAC accepted`
    );

  const macKeep = (it: ReviewItem) =>
    act(
      "mac_mismatch",
      it,
      () => api.post(`/api/v1/review/mac_mismatch/${it.entity_id}/keep`),
      `${it.label}: kept stored MAC (dismissed)`
    );

  const undismiss = (kind: string, it: ReviewItem) =>
    act(
      kind,
      it,
      () =>
        api.post("/api/v1/review/undismiss", {
          kind,
          entity_type: it.entity_type,
          entity_id: it.entity_id,
          fingerprint: it.fingerprint,
        }),
      `${it.label} restored to the queue`
    );

  const submitDismiss = async () => {
    if (!dismissTarget) return;
    setDismissBusy(true);
    try {
      await api.post("/api/v1/review/dismiss", {
        kind: dismissTarget.kind,
        entity_type: dismissTarget.item.entity_type,
        entity_id: dismissTarget.item.entity_id,
        fingerprint: dismissTarget.item.fingerprint,
        notes: dismissNotes.trim() || null,
      });
      toast.success(`${dismissTarget.item.label} dismissed`);
      setDismissTarget(null);
      await reviewQ.reload();
    } catch (e) {
      toast.error("Dismiss failed", { description: String(e) });
    } finally {
      setDismissBusy(false);
    }
  };

  const deleteItem = async (t: DeleteTarget) => {
    const base = DELETE_PATH[t.item.entity_type];
    if (!base) return;
    await api.del(`${base}/${t.item.entity_id}`);
    toast.success(`${t.item.label} deleted`);
    await reviewQ.reload();
  };

  const runResolver = async () => {
    setResolverBusy(true);
    try {
      const rep = await api.post<MatchFreeTextReport>(
        "/api/v1/review/resolve-switch-fields"
      );
      setResolverReport(rep);
      toast.success(
        `Resolver: ${rep.matched} matched, ${rep.ambiguous} ambiguous, ${rep.unmatched} unmatched`
      );
      await reviewQ.reload();
    } catch (e) {
      toast.error("Resolver failed", { description: String(e) });
    } finally {
      setResolverBusy(false);
    }
  };

  const rowActions = (sec: ReviewSection, it: ReviewItem) => {
    const k = key(sec.key, it);
    const spinning = busy.has(k);
    return (
      <div className="flex justify-end gap-1">
        {spinning ? (
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        ) : (
          <>
            {canWrite && sec.key === "mac_mismatch" && (
              <>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => macAccept(it)}
                  title="Write the scanned MAC to the address"
                >
                  <Check className="text-emerald-400" /> Accept scanned
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => macKeep(it)}
                  title="Restore the documented MAC and dismiss this pair permanently"
                >
                  <ShieldAlert className="text-amber-400" /> Keep stored
                </Button>
              </>
            )}
            {canWrite && sec.key === "aging_discovery" && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => confirmDiscovery(sec.key, it)}
                title="Confirm this host as active (normal discovery confirm)"
              >
                <Check className="text-emerald-400" /> Confirm
              </Button>
            )}
            {canWrite && (
              <Button
                size="sm"
                variant="ghost"
                aria-label={`Dismiss ${it.label}`}
                title="Dismiss — recallable, not deleted"
                onClick={() => {
                  setDismissNotes("");
                  setDismissTarget({ kind: sec.key, item: it });
                }}
              >
                <EyeOff />
              </Button>
            )}
            {canDelete && DELETE_PATH[it.entity_type] && (
              <Button
                size="sm"
                variant="ghost"
                aria-label={`Delete ${it.label}`}
                onClick={() => setDeleteTarget({ kind: sec.key, item: it })}
              >
                <Trash2 className="text-red-400" />
              </Button>
            )}
          </>
        )}
      </div>
    );
  };

  const entityCell = (it: ReviewItem) => {
    const href = entityHref(it);
    const label = (
      <span dir="auto" className={cn("font-medium", it.entity_type === "ip_address" || it.entity_type === "mac_group" ? "font-mono" : "")}>
        {it.label}
      </span>
    );
    return (
      <span>
        {href ? (
          <Link href={href} className="underline-offset-2 hover:underline">
            {label}
          </Link>
        ) : (
          label
        )}
        {it.sub && (
          <span dir="auto" className="block text-xs text-muted-foreground">
            {it.sub}
          </span>
        )}
      </span>
    );
  };

  return (
    <div className="space-y-4">
      <h1 className="flex items-center gap-1.5 text-xl font-semibold">
        Review <DocsLink slug="review" />
      </h1>
      <p className="text-sm text-muted-foreground">
        {openTotal === 0
          ? "Queue clear — every flag the system raises lands here."
          : `${openTotal} open finding${openTotal === 1 ? "" : "s"} across ${sections.filter((s) => s.count > 0).length} sections.`}
      </p>

      <AsyncPanel
        loading={reviewQ.loading}
        error={reviewQ.error}
        onRetry={reviewQ.reload}
        empty={sections.length === 0}
        emptyMessage="No review sections."
      >
        <div className="space-y-4">
          {sections.map((sec) => {
            const Icon = SECTION_ICONS[sec.key] ?? ClipboardCheck;
            const open = openSecs[sec.key] ?? sec.count > 0;
            const dismissedOpen = showDismissed[sec.key] ?? false;
            return (
              <Card key={sec.key}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Icon
                      className={cn(
                        "h-4 w-4",
                        sec.count > 0 ? "text-amber-400" : "text-muted-foreground"
                      )}
                    />
                    {sec.title}
                    <Badge
                      variant="outline"
                      className={cn(
                        sec.count > 0
                          ? "border-amber-500/30 text-amber-400"
                          : "text-muted-foreground"
                      )}
                    >
                      {sec.count}
                    </Badge>
                    {sec.dismissed.length > 0 && (
                      <button
                        type="button"
                        onClick={() =>
                          setShowDismissed((s) => ({
                            ...s,
                            [sec.key]: !dismissedOpen,
                          }))
                        }
                        className="text-xs font-normal text-muted-foreground underline-offset-2 hover:underline"
                      >
                        {sec.dismissed.length} dismissed
                      </button>
                    )}
                  </CardTitle>
                  <div className="flex items-center gap-1">
                    {sec.key === "unmatched_switch" && canWrite && (
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={resolverBusy}
                        onClick={runResolver}
                      >
                        {resolverBusy ? (
                          <Loader2 className="animate-spin" />
                        ) : (
                          <Wand2 />
                        )}
                        Run resolver
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      aria-expanded={open}
                      aria-label={`Toggle ${sec.title}`}
                      onClick={() =>
                        setOpenSecs((s) => ({ ...s, [sec.key]: !open }))
                      }
                    >
                      <ChevronDown
                        className={cn(
                          "transition-transform",
                          !open && "-rotate-90"
                        )}
                      />
                    </Button>
                  </div>
                </CardHeader>
                {open && (
                  <CardContent className="space-y-3">
                    {sec.note && (
                      <p className="text-xs text-muted-foreground">{sec.note}</p>
                    )}
                    {sec.key === "unmatched_switch" && resolverReport && (
                      <div className="flex flex-wrap items-center gap-2 rounded-md border p-2.5 text-xs">
                        <span className="font-medium">Last resolver run:</span>
                        <Badge
                          variant="outline"
                          className="border-emerald-500/30 text-emerald-400"
                        >
                          {resolverReport.matched} matched
                        </Badge>
                        <Badge
                          variant="outline"
                          className="border-amber-500/30 text-amber-400"
                        >
                          {resolverReport.ambiguous} ambiguous
                        </Badge>
                        <Badge
                          variant="outline"
                          className="border-rose-500/30 text-rose-400"
                        >
                          {resolverReport.unmatched} unmatched
                        </Badge>
                        {resolverReport.matched_ids.length > 0 && (
                          <span className="font-mono text-muted-foreground">
                            linked: {resolverReport.matched_ids.map((i) => `#${i}`).join(" ")}
                          </span>
                        )}
                      </div>
                    )}
                    {sec.items.length === 0 ? (
                      <p className="py-2 text-sm text-muted-foreground">
                        Nothing open here.
                      </p>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Entity</TableHead>
                            <TableHead>Why flagged</TableHead>
                            <TableHead>Flagged</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {sec.items.map((it) => (
                            <TableRow key={key(sec.key, it)}>
                              <TableCell>{entityCell(it)}</TableCell>
                              <TableCell>
                                <WhyCell kind={sec.key} item={it} />
                              </TableCell>
                              <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                                {timeAgo(it.flagged_at)}
                              </TableCell>
                              <TableCell className="text-right">
                                {rowActions(sec, it)}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                    {sec.count > sec.items.length && (
                      <p className="text-xs text-muted-foreground">
                        Showing {sec.items.length} of {sec.count} — narrow it
                        down on the entity page.
                      </p>
                    )}
                    {dismissedOpen && sec.dismissed.length > 0 && (
                      <div className="rounded-md border border-dashed p-2">
                        <Table>
                          <TableBody>
                            {sec.dismissed.map((it) => (
                              <TableRow key={`d-${key(sec.key, it)}`}>
                                <TableCell className="text-muted-foreground">
                                  {entityCell(it)}
                                </TableCell>
                                <TableCell className="text-xs text-muted-foreground">
                                  dismissed by {it.dismissed_by}{" "}
                                  {timeAgo(it.dismissed_at)}
                                  {it.dismiss_notes ? ` — ${it.dismiss_notes}` : ""}
                                </TableCell>
                                <TableCell className="text-right">
                                  {canWrite && (
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      disabled={busy.has(key(sec.key, it))}
                                      onClick={() => undismiss(sec.key, it)}
                                    >
                                      <RotateCcw /> Restore
                                    </Button>
                                  )}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            );
          })}
        </div>
      </AsyncPanel>

      <Dialog
        open={dismissTarget !== null}
        onOpenChange={(o) => !o && setDismissTarget(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Dismiss{" "}
              <span className="font-mono">{dismissTarget?.item.label}</span>
            </DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            The finding leaves the queue but is kept — it stays recallable
            under &quot;dismissed&quot; and survives re-flagging of the same
            fingerprint.
          </p>
          <div className="grid gap-1.5">
            <Label className="text-xs" htmlFor="dismiss-notes">
              Note (optional)
            </Label>
            <Input
              id="dismiss-notes"
              value={dismissNotes}
              onChange={(e) => setDismissNotes(e.target.value)}
              placeholder="e.g. shared laptop dock MAC"
              autoComplete="off"
            />
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDismissTarget(null)}>
              Cancel
            </Button>
            <Button disabled={dismissBusy} onClick={submitDismiss}>
              {dismissBusy ? "Working…" : "Dismiss"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={deleteTarget !== null}
        onOpenChange={(o) => !o && setDeleteTarget(null)}
        title="Delete flagged entity"
        description={
          <>
            Permanently delete{" "}
            <span className="font-mono text-foreground">
              {deleteTarget?.item.label}
            </span>
            ? This removes the underlying{" "}
            {deleteTarget?.item.entity_type.replace("_", " ")} row — not just
            its review entry — and cannot be undone.
          </>
        }
        confirmWord="DELETE"
        actionLabel="Delete"
        onAction={async () => {
          if (deleteTarget) await deleteItem(deleteTarget);
        }}
      />
    </div>
  );
}
