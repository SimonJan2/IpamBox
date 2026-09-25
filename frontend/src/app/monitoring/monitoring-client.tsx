"use client";

import { useState } from "react";
import Link from "next/link";
import { Activity, Pencil, Plus, Trash2, Zap } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { usePolling } from "@/lib/use-polling";
import { PERM } from "@/lib/permissions";
import { timeAgo } from "@/lib/utils";
import type { MonitorSummary, MonitorTarget, Page } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { MonitorDialog } from "@/components/monitor-dialog";
import { MonitorStateBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

function targetLink(t: MonitorTarget): { href: string; label: string } {
  if (t.device_id != null)
    return {
      href: `/devices/${t.device_id}`,
      label: t.device_name ?? `device #${t.device_id}`,
    };
  return {
    href: t.resolved_ip
      ? `/prefixes?q=${encodeURIComponent(t.resolved_ip)}`
      : "/monitoring",
    label: t.target_label ?? `address #${t.address_id}`,
  };
}

export default function MonitoringPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const targetsQ = useAsyncData(() =>
    api.get<Page<MonitorTarget>>("/api/v1/monitor-targets?limit=500")
  );
  const summaryQ = useAsyncData(() =>
    api.get<MonitorSummary>("/api/v1/monitor-targets/summary")
  );
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<MonitorTarget | null>(null);
  const [deleting, setDeleting] = useState<MonitorTarget | null>(null);

  const targets = targetsQ.data?.items ?? [];
  const summary = summaryQ.data;

  // The live board — 12s cadence with backoff while nothing changes.
  usePolling(
    async () => {
      const [t, s] = await Promise.all([
        targetsQ.reload(),
        summaryQ.reload(),
      ]);
      return JSON.stringify([t, s]);
    },
    { interval: 12_000 }
  );

  const toggle = async (t: MonitorTarget) => {
    try {
      await api.patch(`/api/v1/monitor-targets/${t.id}`, {
        enabled: !t.enabled,
      });
      void targetsQ.reload();
    } catch (e) {
      toast.error("Update failed", { description: String(e) });
    }
  };

  const checkNow = async (t: MonitorTarget) => {
    try {
      const out = await api.post<MonitorTarget>(
        `/api/v1/monitor-targets/${t.id}/check`,
        {}
      );
      toast.success(
        out.state === "up" ? "Check passed — up" : `Check ran — ${out.state}`,
        { description: out.last_error ?? undefined }
      );
      void targetsQ.reload();
      void summaryQ.reload();
    } catch (e) {
      toast.error("Check failed", { description: String(e) });
    }
  };

  const doDelete = async () => {
    if (!deleting) return;
    try {
      await api.del(`/api/v1/monitor-targets/${deleting.id}`);
      toast.success("Monitor deleted");
      setDeleting(null);
      void targetsQ.reload();
      void summaryQ.reload();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const describe = (t: MonitorTarget) =>
    t.kind === "ping"
      ? "ping"
      : t.kind === "tcp"
        ? `tcp:${t.port}`
        : `http ${t.port ?? 80}${t.http_path}${t.http_expect ? ` · expect ${t.http_expect}` : ""}`;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">
          Monitoring <DocsLink slug="monitoring" />
        </h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New monitor
          </Button>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <span className="h-3 w-3 rounded-full bg-emerald-500/70" />
            <span className="text-2xl font-bold">{summary?.up ?? "—"}</span>
            <span className="text-sm text-muted-foreground">up</span>
          </CardContent>
        </Card>
        <Card
          className={
            summary?.down
              ? "border-red-500/40 bg-red-500/5"
              : undefined
          }
        >
          <CardContent className="flex items-center gap-3 p-4">
            <span className="h-3 w-3 rounded-full bg-red-500/70" />
            <span
              className={`text-2xl font-bold ${summary?.down ? "text-red-400" : ""}`}
            >
              {summary?.down ?? "—"}
            </span>
            <span className="text-sm text-muted-foreground">down</span>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-4">
            <span className="h-3 w-3 rounded-full bg-zinc-500/70" />
            <span className="text-2xl font-bold">
              {summary?.unknown ?? "—"}
            </span>
            <span className="text-sm text-muted-foreground">
              unknown{summary?.due ? ` · ${summary.due} due` : ""}
            </span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="pt-4">
          <AsyncPanel
            loading={targetsQ.loading}
            error={targetsQ.error}
            onRetry={targetsQ.reload}
            empty={targets.length === 0}
            emptyMessage='No monitors yet — hit "New monitor" to watch a device or IP.'
          >
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Target</TableHead>
                  <TableHead>Check</TableHead>
                  <TableHead>State</TableHead>
                  <TableHead>Last checked</TableHead>
                  <TableHead>Since</TableHead>
                  <TableHead className="w-8">On</TableHead>
                  {canWrite && <TableHead className="w-28" />}
                </TableRow>
              </TableHeader>
              <TableBody>
                {targets.map((t) => {
                  const link = targetLink(t);
                  return (
                    <TableRow key={t.id}>
                      <TableCell>
                        <Link
                          href={link.href}
                          className="text-emerald-400 hover:underline"
                          dir="auto"
                        >
                          {t.target_label ?? link.label}
                        </Link>
                        {t.resolved_ip && t.device_id != null && (
                          <span
                            dir="ltr"
                            className="ml-2 font-mono text-xs text-muted-foreground"
                          >
                            {t.resolved_ip}
                          </span>
                        )}
                      </TableCell>
                      <TableCell className="whitespace-nowrap font-mono text-xs">
                        {describe(t)}
                        <span className="ml-2 text-muted-foreground">
                          every {t.interval_seconds}s
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className="flex items-center gap-2">
                          <MonitorStateBadge s={t.state} />
                          {t.last_error && (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <span className="max-w-52 cursor-help truncate text-xs text-red-400">
                                  {t.last_error}
                                </span>
                              </TooltipTrigger>
                              <TooltipContent className="max-w-sm">
                                {t.last_error}
                              </TooltipContent>
                            </Tooltip>
                          )}
                        </span>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {t.last_checked_at ? timeAgo(t.last_checked_at) : "—"}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {t.last_change_at ? timeAgo(t.last_change_at) : "—"}
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={t.enabled}
                          disabled={!canWrite}
                          aria-label={`Enable monitor ${t.id}`}
                          onCheckedChange={() => toggle(t)}
                        />
                      </TableCell>
                      {canWrite && (
                        <TableCell>
                          <div className="flex justify-end gap-0.5">
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={`Check ${t.target_label ?? t.id} now`}
                              title="Check now"
                              onClick={() => checkNow(t)}
                            >
                              <Zap className="h-3.5 w-3.5 text-cyan-400" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={`Edit monitor ${t.id}`}
                              onClick={() => {
                                setEditing(t);
                                setDialogOpen(true);
                              }}
                            >
                              <Pencil className="h-3.5 w-3.5" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={`Delete monitor ${t.id}`}
                              onClick={() => setDeleting(t)}
                            >
                              <Trash2 className="h-3.5 w-3.5 text-rose-400" />
                            </Button>
                          </div>
                        </TableCell>
                      )}
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </AsyncPanel>
        </CardContent>
      </Card>

      <MonitorDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        target={editing}
        onSaved={() => {
          void targetsQ.reload();
          void summaryQ.reload();
        }}
      />
      <Dialog
        open={deleting != null}
        onOpenChange={(o) => !o && setDeleting(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Delete monitor{deleting ? ` #${deleting.id}` : ""}?
            </DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            The target stays; only the health check is removed.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
