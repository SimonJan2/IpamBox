"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Play } from "lucide-react";
import { toast } from "sonner";

import { api, scanStreamUrl } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type { ScanJob, Vrf } from "@/types";
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

export default function ScansPage() {
  const [scans, setScans] = useState<ScanJob[]>([]);
  const [vrfs, setVrfs] = useState<Record<number, string>>({});
  const streams = useRef<Map<number, EventSource>>(new Map());

  const refresh = useCallback(() => {
    api.get<ScanJob[]>("/api/v1/scans?limit=50").then(setScans).catch(() => {});
  }, []);

  useEffect(() => {
    refresh();
    api.get<Vrf[]>("/api/v1/vrfs").then((vs) =>
      setVrfs(Object.fromEntries(vs.map((v) => [v.id, v.name])))
    ).catch(() => {});
    const t = setInterval(refresh, 10000);
    return () => {
      clearInterval(t);
      streams.current.forEach((es) => es.close());
    };
  }, [refresh]);

  // attach an SSE stream to every live scan
  useEffect(() => {
    for (const s of scans) {
      if ((s.status === "running" || s.status === "queued") && !streams.current.has(s.id)) {
        const es = new EventSource(scanStreamUrl(s.id));
        es.onmessage = (m) => {
          try {
            const d = JSON.parse(m.data);
            setScans((prev) =>
              prev.map((p) =>
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
            if (d.status === "completed" || d.status === "failed") {
              es.close();
              streams.current.delete(s.id);
              refresh();
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
  }, [scans, refresh]);

  const startScan = async () => {
    try {
      await api.post("/api/v1/scans", {});
      toast.success("Scan queued");
      refresh();
    } catch (e) {
      toast.error("Failed to queue scan", { description: String(e) });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Scans</h1>
        <Button size="sm" onClick={startScan}>
          <Play /> Scan LAN (auto-detect)
        </Button>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Job history</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>#</TableHead>
                <TableHead>CIDR</TableHead>
                <TableHead>VRF</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-48">Progress</TableHead>
                <TableHead>Hosts</TableHead>
                <TableHead>New</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Started</TableHead>
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
                      <span className="text-xs text-muted-foreground">
                        {Math.round(s.progress)}%
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
                </TableRow>
              ))}
              {scans.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9} className="py-10 text-center text-muted-foreground">
                    No scans yet — hit &quot;Scan LAN&quot; to run one.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
