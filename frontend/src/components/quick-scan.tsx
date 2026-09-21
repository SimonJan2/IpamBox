"use client";

import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import { Radar } from "lucide-react";
import { toast } from "sonner";

import { api, scanStreamUrl } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { usePolling } from "@/lib/use-polling";
import { ipToInt } from "@/lib/utils";
import type { ScanEvent, ScanJob, Vrf } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function useScanStream(scanId: number | null, onDone?: (e: ScanEvent) => void) {
  const [event, setEvent] = useState<ScanEvent | null>(null);
  const doneRef = useRef(onDone);
  doneRef.current = onDone;

  useEffect(() => {
    if (scanId == null) return;
    const es = new EventSource(scanStreamUrl(scanId));
    es.onmessage = (m) => {
      try {
        const data = JSON.parse(m.data) as ScanEvent;
        setEvent(data);
        if (data.status === "completed" || data.status === "failed") {
          es.close();
          doneRef.current?.(data);
        }
      } catch {
        /* ignore malformed event */
      }
    };
    es.onerror = () => es.close();
    return () => es.close();
  }, [scanId]);

  return event;
}

/** [lo, hi] address-int bounds of an IPv4 CIDR, or null for anything else. */
function v4NetBounds(cidr: string): [number, number] | null {
  const m = /^(\d{1,3}(?:\.\d{1,3}){3})\/(\d{1,2})$/.exec(cidr);
  if (!m) return null;
  const bits = Number(m[2]);
  if (bits > 32) return null;
  const size = 2 ** (32 - bits);
  const lo = Math.floor(ipToInt(m[1]) / size) * size;
  return [lo, lo + size - 1];
}

/** Live-scan overlay for the subnet grid (F15). Polls the scan list for a
 *  queued/running job whose CIDR overlaps `cidr` (or that names `prefixId`),
 *  streams its `found` deltas over SSE, and accumulates them as a set of
 *  address_ints. The stream closes and `onSettled` fires when the job
 *  reaches a terminal state or no longer matches — the caller refetches so
 *  reconciled statuses replace the overlay. */
export function usePrefixScanOverlay(
  prefixId: number | null,
  cidr: string | null,
  onSettled?: () => void
): { found: Set<number>; scanning: boolean } {
  const scansQ = useAsyncData(() =>
    api.get<ScanJob[]>("/api/v1/scans?limit=20")
  );
  // Scan discovery is a light poll — the SSE stream carries the fast path.
  usePolling(async () => JSON.stringify(await scansQ.reload()), {
    interval: 10000,
  });

  const [found, setFound] = useState<Set<number>>(new Set());
  const [activeId, setActiveId] = useState<number | null>(null);
  const esRef = useRef<EventSource | null>(null);
  const openRef = useRef(false);
  const jobRef = useRef<number | null>(null);
  const settledRef = useRef(onSettled);
  settledRef.current = onSettled;

  const live = useMemo(() => {
    const bounds = cidr ? v4NetBounds(cidr) : null;
    return (scansQ.data ?? []).find((s) => {
      if (s.status !== "running" && s.status !== "queued") return false;
      if (s.prefix_id != null && s.prefix_id === prefixId) return true;
      if (!bounds || !s.cidr) return false;
      const sb = v4NetBounds(s.cidr);
      return sb != null && sb[0] <= bounds[1] && bounds[0] <= sb[1];
    });
  }, [scansQ.data, prefixId, cidr]);

  const finish = useCallback(() => {
    const wasOpen = openRef.current;
    openRef.current = false;
    jobRef.current = null;
    esRef.current?.close();
    esRef.current = null;
    setActiveId(null);
    setFound(new Set());
    // Only a stream that actually ran settles — close-before-start or
    // unmount must not trigger a refetch.
    if (wasOpen) settledRef.current?.();
  }, []);

  // Transient drop: close so the next poll reattaches to the same job, but
  // keep the accumulated `found` set — deltas aren't replayed.
  const dropStream = useCallback(() => {
    openRef.current = false;
    esRef.current?.close();
    esRef.current = null;
    setActiveId(null);
  }, []);

  useEffect(() => {
    if (!live) {
      finish();
      return;
    }
    if (activeId === live.id && esRef.current) return; // already streaming it
    // Close whatever was open without wiping `found` — a reattach after a
    // transient drop keeps its accumulated hosts; only a different job
    // starts a fresh set.
    dropStream();
    if (jobRef.current !== live.id) setFound(new Set());
    jobRef.current = live.id;
    openRef.current = true;
    setActiveId(live.id);
    const es = new EventSource(scanStreamUrl(live.id));
    esRef.current = es;
    es.onmessage = (m) => {
      try {
        const d = JSON.parse(m.data) as ScanEvent;
        if (Array.isArray(d.found) && d.found.length) {
          setFound((prev) => {
            const next = new Set(prev);
            for (const ip of d.found!) {
              try {
                next.add(ipToInt(ip));
              } catch {
                /* ignore non-IP entries */
              }
            }
            return next;
          });
        }
        if (["completed", "failed", "cancelled"].includes(d.status)) finish();
      } catch {
        /* ignore malformed event */
      }
    };
    es.onerror = dropStream;
    // No cleanup close here — `live` gets a new identity every poll; closing
    // in cleanup would thrash the stream. Unmount + unmatch close below.
  }, [live, activeId, finish, dropStream]);

  // Close on unmount / route change.
  useEffect(() => () => esRef.current?.close(), []);

  return { found, scanning: activeId != null };
}

export function QuickScanDialog({
  open,
  onOpenChange,
  onFinished,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  onFinished?: () => void;
}) {
  const [cidr, setCidr] = useState("");
  const [vrfId, setVrfId] = useState<string>("");
  const [vrfs, setVrfs] = useState<Vrf[]>([]);
  const [job, setJob] = useState<ScanJob | null>(null);
  const [busy, setBusy] = useState(false);
  const uid = useId();
  const event = useScanStream(job?.id ?? null, (e) => {
    if (e.status === "completed") {
      toast.success("Scan finished", {
        description: `${e.hosts_discovered ?? 0} hosts live, ${e.hosts_new ?? 0} new`,
      });
    } else {
      toast.error("Scan failed", { description: e.error ?? undefined });
    }
    onFinished?.();
  });

  useEffect(() => {
    if (open) {
      api
        .get<Vrf[]>("/api/v1/vrfs")
        .then(setVrfs)
        .catch((e) =>
          toast.error("Could not load VRFs", { description: String(e) })
        );
      setJob(null);
    }
  }, [open]);

  const start = async () => {
    setBusy(true);
    try {
      const j = await api.post<ScanJob>("/api/v1/scans", {
        cidr: cidr.trim() || null,
        vrf_id: vrfId ? Number(vrfId) : null,
      });
      setJob(j);
    } catch (e) {
      toast.error("Failed to start scan", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const running = job && event?.status !== "completed" && event?.status !== "failed";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Radar className="h-5 w-5 text-emerald-400" /> Network scan
          </DialogTitle>
          <DialogDescription>
            ARP + ICMP sweep with reverse-DNS and vendor enrichment. Leave CIDR empty to
            auto-detect the LAN subnet.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-cidr`}>CIDR (optional)</Label>
            <Input
              id={`${uid}-cidr`}
              placeholder="auto-detect, e.g. 192.168.1.0/24"
              value={cidr}
              onChange={(e) => setCidr(e.target.value)}
              disabled={!!job}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-vrf`}>VRF</Label>
            <Select value={vrfId} onValueChange={setVrfId} disabled={!!job}>
              <SelectTrigger id={`${uid}-vrf`}>
                <SelectValue placeholder="Global (default)" />
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
        </div>

        {job && (
          <div
            role="status"
            aria-live="polite"
            className="space-y-2 rounded-md border p-3"
          >
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                {event?.cidr || job.cidr || "detecting…"} — {event?.phase ?? job.status}
              </span>
              <span aria-hidden="true" className="font-mono text-emerald-400">
                {Math.round(event?.progress ?? job.progress)}%
              </span>
            </div>
            <Progress value={event?.progress ?? job.progress} />
            {event?.status === "completed" && (
              <p className="text-sm text-emerald-400">
                {event.hosts_discovered} hosts live, {event.hosts_new} new
              </p>
            )}
            {event?.status === "failed" && (
              <p className="text-sm text-red-400">{event.error}</p>
            )}
          </div>
        )}

        <DialogFooter>
          {!job ? (
            <Button onClick={start} disabled={busy}>
              <Radar /> {busy ? "Queueing…" : "Start scan"}
            </Button>
          ) : (
            <Button variant="secondary" onClick={() => onOpenChange(false)} disabled={!!running && false}>
              Close
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
