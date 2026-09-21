"use client";

import { useEffect, useRef, useState } from "react";
import { Play, Square } from "lucide-react";
import { toast } from "sonner";

import { api, scanStreamUrl } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useAsyncData } from "@/lib/use-async-data";
import { usePolling } from "@/lib/use-polling";
import { PERM } from "@/lib/permissions";
import { timeAgo } from "@/lib/utils";
import type { ScanConfig, ScanJob, Vrf } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { ScanStatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function fmtEta(s: number | null | undefined): string {
  if (s == null) return "";
  if (s < 60) return `~${Math.ceil(s)}s left`;
  const m = Math.floor(s / 60);
  return `~${m}m ${Math.ceil(s % 60)}s left`;
}

export default function ScansPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const scansQ = useAsyncData(() => api.get<ScanJob[]>("/api/v1/scans?limit=50"));
  const auxQ = useAsyncData(async () => {
    const [vs, cfg] = await Promise.all([
      api.get<Vrf[]>("/api/v1/vrfs"),
      api.get<ScanConfig>("/api/v1/scans/config"),
    ]);
    return {
      vrfs: Object.fromEntries(vs.map((v) => [v.id, v.name])),
      config: cfg,
    };
  });
  const [eta, setEta] = useState<Record<number, number | null>>({});
  const streams = useRef<Map<number, EventSource>>(new Map());

  const scans = scansQ.data ?? [];
  const vrfs = auxQ.data?.vrfs ?? {};
  const config = auxQ.data?.config ?? null;

  // SSE below is the live-update channel while jobs run; polling is the
  // fallback and backs off to the ceiling when nothing changes.
  usePolling(
    async () => JSON.stringify(await scansQ.reload()),
    { interval: 10000 }
  );

  useEffect(
    () => () => streams.current.forEach((es) => es.close()),
    []
  );

  // attach an SSE stream to every live scan
  useEffect(() => {
    for (const s of scans) {
      if ((s.status === "running" || s.status === "queued") && !streams.current.has(s.id)) {
        const es = new EventSource(scanStreamUrl(s.id));
        es.onmessage = (m) => {
          try {
            const d = JSON.parse(m.data);
            scansQ.setData((prev) =>
              (prev ?? []).map((p) =>
                p.id === s.id
                  ? {
                      ...p,
                      status: d.status ?? p.status,
                      progress: d.progress ?? p.progress,
                      cidr: d.cidr ?? p.cidr,
                      hosts_discovered: d.hosts_discovered ?? p.hosts_discovered,
                      hosts_new: d.hosts_new ?? p.hosts_new,
                      error: d.error ?? p.error,
                    }
                  : p
              )
            );
            setEta((prev) => ({ ...prev, [s.id]: d.eta_seconds ?? null }));
            if (["completed", "failed", "cancelled"].includes(d.status)) {
              es.close();
              streams.current.delete(s.id);
              void scansQ.reload();
            }
          } catch {
            /* ignore */
          }
        };
        es.onerror = () => {
          es.close();
          streams.current.delete(s.id);
        };
        streams.current.set(s.id, es);
      }
    }
  }, [scans, scansQ.reload, scansQ.setData]);

  const startScan = async (cidr?: string) => {
    try {
      await api.post("/api/v1/scans", cidr ? { cidr } : {});
      toast.success(cidr ? `Scan queued for ${cidr}` : "Scan queued");
      void scansQ.reload();
    } catch (e) {
      toast.error("Failed to queue scan", { description: String(e) });
    }
  };

  const cancel = async (id: number) => {
    try {
      await api.post(`/api/v1/scans/${id}/cancel`, {});
      toast.success("Scan cancelled");
      void scansQ.reload();
    } catch (e) {
      toast.error("Cancel failed", { description: String(e) });
    }
  };

  const targets = config?.networks.length
    ? config.networks
    : config?.detected_cidr
      ? [config.detected_cidr]
      : [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">Scans <DocsLink slug="scans" /></h1>
        {canWrite && (
          <Button size="sm" onClick={() => startScan()}>
            <Play /> Scan LAN (auto-detect)
          </Button>
        )}
      </div>

      {auxQ.error ? (
        <AsyncPanel error={auxQ.error} loading={false} onRetry={auxQ.reload}>
          {null}
        </AsyncPanel>
      ) : (
        config && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Scanner configuration</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <span>
              schedule:{" "}
              {config.interval_minutes > 0
                ? `every ${config.interval_minutes}m`
                : "manual only"}
            </span>
            <span>ports probed: {config.tcp_ports.join(", ") || "none"}</span>
            <span>
              detected LAN:{" "}
              <span className="font-mono">{config.detected_cidr ?? "—"}</span>
            </span>
            {config.only_configured && (
              <span className="text-amber-400">only configured networks</span>
            )}
            {config.exclude_networks.length > 0 && (
              <span>excluded: {config.exclude_networks.join(", ")}</span>
            )}
            {targets.length > 0 && canWrite && (
              <span className="ml-auto flex gap-2">
                {targets.map((n) => (
                  <Button
                    key={n}
                    size="sm"
                    variant="outline"
                    onClick={() => startScan(n)}
                  >
                    <Play /> {n}
                  </Button>
                ))}
              </span>
            )}
          </CardContent>
        </Card>
        )
      )}

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Job history</CardTitle>
        </CardHeader>
        <CardContent>
          <AsyncPanel
            loading={scansQ.loading}
            error={scansQ.error}
            onRetry={scansQ.reload}
            empty={scans.length === 0}
            emptyMessage='No scans yet — hit "Scan LAN" to run one.'
          >
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>#</TableHead>
                <TableHead>CIDR</TableHead>
                <TableHead>VRF</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-56">Progress</TableHead>
                <TableHead>Hosts</TableHead>
                <TableHead>New</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Started</TableHead>
                <TableHead className="w-16"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {scans.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-mono text-muted-foreground">{s.id}</TableCell>
                  <TableCell className="font-mono">{s.cidr || "auto-detect"}</TableCell>
                  <TableCell>{s.vrf_id ? vrfs[s.vrf_id] ?? s.vrf_id : "—"}</TableCell>
                  <TableCell>
                    <ScanStatusBadge s={s.status} />
                    {s.error && (
                      <span className="ml-2 text-xs text-red-400">{s.error}</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress value={s.progress} className="h-1.5" />
                      <span className="whitespace-nowrap text-xs text-muted-foreground">
                        {Math.round(s.progress)}%
                        {s.status === "running" && eta[s.id] != null && (
                          <span className="text-cyan-400"> · {fmtEta(eta[s.id])}</span>
                        )}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>{s.hosts_discovered}</TableCell>
                  <TableCell>{s.hosts_new}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {s.duration_seconds != null ? `${s.duration_seconds}s` : "—"}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {timeAgo(s.started_at ?? s.created_at)}
                  </TableCell>
                  <TableCell>
                    {canWrite && (s.status === "running" || s.status === "queued") && (
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Cancel scan ${s.cidr ?? s.id}`}
                        title="Cancel scan"
                        onClick={() => cancel(s.id)}
                      >
                        <Square className="h-3.5 w-3.5 text-rose-400" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          </AsyncPanel>
        </CardContent>
      </Card>
    </div>
  );
}
