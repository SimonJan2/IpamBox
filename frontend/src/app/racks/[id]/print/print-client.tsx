"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Printer } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { fmtTs } from "@/lib/prefs";
import type { Page, RackDetail, Site } from "@/types";
import { RackElevation } from "@/components/racks/rack-elevation";
import { RackQrCode, rackUrl } from "@/components/racks/rack-qr";
import { AsyncPanel } from "@/components/async-panel";
import { IpStatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const FACE_BADGE: Record<string, string> = {
  front: "Front",
  rear: "Rear",
  both: "Front+Rear",
};

/** Printable rack report: metadata, front+rear elevations side by side, and
 *  the full device table (the print-only detail table — screen shows the
 *  summary card, print shows everything). */
export default function PrintClient({ id }: { id: string }) {
  const rackQ = useAsyncData(
    () => api.get<RackDetail>(`/api/v1/racks/${id}`),
    [id]
  );
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Site>>("/api/v1/sites").then((p) => p.items);
    } catch (e) {
      toast.error("Could not load sites", { description: String(e) });
      return [];
    }
  });

  const rack = rackQ.data;
  const devices = (rack?.devices ?? [])
    .slice()
    .sort((a, b) => b.u_position - a.u_position);
  const siteName = rack?.site_id
    ? (sitesQ.data ?? []).find((s) => s.id === rack.site_id)?.name
    : null;
  const generated = new Date().toISOString();
  const [url, setUrl] = useState("");
  useEffect(() => {
    if (rack) setUrl(rackUrl(rack.id));
  }, [rack]);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Screen-only toolbar */}
      <div className="flex items-center gap-2 print:hidden">
        <Button variant="ghost" size="icon" aria-label="Back to rack" asChild>
          <Link href={`/racks/${id}`}>
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="text-sm text-muted-foreground">
          Report preview — both elevations and the full device table.
        </span>
        <Button
          size="sm"
          className="ml-auto"
          onClick={() => window.print()}
        >
          <Printer /> Print / save as PDF
        </Button>
      </div>

      <AsyncPanel
        loading={rackQ.loading}
        error={rackQ.error}
        onRetry={rackQ.reload}
        empty={!rack}
        emptyMessage="Rack not found."
      >
        {rack && (
          <article className="space-y-6 print:space-y-4">
            <header className="space-y-1 border-b pb-3">
              <div className="flex flex-wrap items-baseline gap-3">
                <h1 dir="auto" className="text-2xl font-semibold">
                  {rack.name}
                </h1>
                <Badge variant="outline">{rack.height_u}U</Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                {[
                  siteName ? `Site ${siteName}` : null,
                  rack.room ? `Room ${rack.room}` : null,
                  rack.description,
                ]
                  .filter(Boolean)
                  .join("  ·  ") || "No site/room metadata"}
              </p>
              <p className="text-sm text-muted-foreground">
                Generated {fmtTs(generated)} · {rack.used_u}/{rack.height_u}U
                used · {rack.device_count} devices
              </p>
            </header>

            <section aria-label="Elevations">
              <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Elevations
              </h2>
              <div className="grid gap-4 sm:grid-cols-2">
                <RackElevation
                  name={rack.name}
                  heightU={rack.height_u}
                  devices={devices}
                  forceView="front"
                />
                <RackElevation
                  name={rack.name}
                  heightU={rack.height_u}
                  devices={devices}
                  forceView="rear"
                />
              </div>
            </section>

            <section aria-label="Devices">
              <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Devices ({devices.length})
              </h2>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>U</TableHead>
                    <TableHead>Face</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Asset</TableHead>
                    <TableHead>IP</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {devices.map((d) => (
                    <TableRow key={d.id}>
                      <TableCell dir="ltr" className="whitespace-nowrap">
                        U{d.u_position}
                        {d.u_height > 1
                          ? `–${d.u_position + d.u_height - 1}`
                          : ""}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {FACE_BADGE[d.face]}
                      </TableCell>
                      <TableCell>
                        <span dir="auto" className="font-medium">{d.name}</span>
                        {(d.manufacturer || d.model) && (
                          <span className="block text-xs text-muted-foreground" dir="auto">
                            {[d.manufacturer, d.model].filter(Boolean).join(" ")}
                          </span>
                        )}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {d.device_type ?? "—"}
                      </TableCell>
                      <TableCell dir="auto" className="text-muted-foreground">
                        {d.asset?.label ?? "—"}
                      </TableCell>
                      <TableCell dir="ltr" className="text-muted-foreground">
                        {d.ip?.label ?? "—"}
                      </TableCell>
                      <TableCell>
                        {d.ip_status ? (
                          <IpStatusBadge s={d.ip_status} />
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {devices.length === 0 && (
                    <TableRow>
                      <TableCell
                        colSpan={7}
                        className="py-8 text-center text-muted-foreground"
                      >
                        Empty rack.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </section>

            <footer className="flex items-center gap-4 border-t pt-3 text-xs text-muted-foreground">
              <div className="shrink-0 rounded-md bg-white p-1.5">
                <RackQrCode id={rack.id} size={72} />
              </div>
              <div>
                <p>Generated {fmtTs(generated)} · IpamBox · {rack.name}</p>
                <p dir="ltr" className="mt-0.5 break-all">{url}</p>
              </div>
            </footer>
          </article>
        )}
      </AsyncPanel>
    </div>
  );
}
