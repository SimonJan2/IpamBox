"use client";

import { useEffect, useRef, useState } from "react";
import { Radar } from "lucide-react";
import { toast } from "sonner";

import { api, scanStreamUrl } from "@/lib/api";
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
            <Label htmlFor="cidr">CIDR (optional)</Label>
            <Input
              id="cidr"
              placeholder="auto-detect, e.g. 192.168.1.0/24"
              value={cidr}
              onChange={(e) => setCidr(e.target.value)}
              disabled={!!job}
            />
          </div>
          <div className="grid gap-1.5">
            <Label>VRF</Label>
            <Select value={vrfId} onValueChange={setVrfId} disabled={!!job}>
              <SelectTrigger>
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
          <div className="space-y-2 rounded-md border p-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                {event?.cidr || job.cidr || "detecting…"} — {event?.phase ?? job.status}
              </span>
              <span className="font-mono text-emerald-400">
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
