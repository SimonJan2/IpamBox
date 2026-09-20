"use client";

import Link from "next/link";
import { ArrowLeft, Printer } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { fmtTs } from "@/lib/prefs";
import { timeAgo } from "@/lib/utils";
import type { AddressPage, IpRange, Prefix, Site, Vrf } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { IpStatusBadge, PrefixStatusBadge } from "@/components/status-badge";
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

/** Printable subnet report: metadata + utilization + range bands + the full
 *  address table. Deliberately rendered as one flat, non-virtualized table so
 *  window.print() captures every row. */
export default function PrintClient({ id }: { id: string }) {
  const prefixId = Number(id);
  const prefixQ = useAsyncData(
    () => api.get<Prefix>(`/api/v1/prefixes/${prefixId}`),
    [prefixId]
  );
  const pageQ = useAsyncData(
    () =>
      api.get<AddressPage>(`/api/v1/prefixes/${prefixId}/addresses?limit=20000`),
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
  const namesQ = useAsyncData(async () => {
    try {
      const [sites, vrfs] = await Promise.all([
        api.get<Site[]>("/api/v1/sites"),
        api.get<Vrf[]>("/api/v1/vrfs"),
      ]);
      return {
        sites: Object.fromEntries(sites.map((s) => [s.id, s.name])),
        vrfs: Object.fromEntries(vrfs.map((v) => [v.id, v.name])),
      };
    } catch {
      return { sites: {} as Record<number, string>, vrfs: {} as Record<number, string> };
    }
  });

  const prefix = prefixQ.data;
  const page = pageQ.data;
  const ranges = (rangesQ.data ?? []).slice().sort(
    (a, b) => Number(a.start_int) - Number(b.start_int)
  );
  const addrs = (page?.items ?? [])
    .slice()
    .sort((a, b) => Number(a.address_int) - Number(b.address_int));
  const loading = prefixQ.loading || pageQ.loading || rangesQ.loading;
  const error = prefixQ.error ?? pageQ.error;
  const generated = new Date().toISOString();

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Screen-only toolbar */}
      <div className="flex items-center gap-2 print:hidden">
        <Button variant="ghost" size="icon" aria-label="Back to subnet" asChild>
          <Link href={`/prefixes/${prefixId}`}>
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="text-sm text-muted-foreground">
          Report preview — all addresses, no virtualization.
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
        loading={loading}
        error={error}
        onRetry={() => {
          void prefixQ.reload();
          void pageQ.reload();
          void rangesQ.reload();
        }}
        empty={!prefix}
        emptyMessage="Prefix not found."
      >
        {prefix && page && (
          <article className="space-y-6 print:space-y-4">
            <header className="space-y-1 border-b pb-3">
              <div className="flex flex-wrap items-baseline gap-3">
                <h1 className="font-mono text-2xl font-semibold">
                  {prefix.prefix}
                </h1>
                <PrefixStatusBadge s={prefix.status} />
              </div>
              <p className="text-sm text-muted-foreground">
                {[prefix.description]
                  .filter(Boolean)
                  .join(" · ") || null}
              </p>
              <p className="text-sm text-muted-foreground">
                {[
                  namesQ.data?.vrfs[prefix.vrf_id]
                    ? `VRF ${namesQ.data.vrfs[prefix.vrf_id]}`
                    : null,
                  prefix.site_id && namesQ.data?.sites[prefix.site_id]
                    ? `Site ${namesQ.data.sites[prefix.site_id]}`
                    : null,
                  prefix.vlan
                    ? `VLAN ${prefix.vlan.vid} · ${prefix.vlan.name}`
                    : null,
                ]
                  .filter(Boolean)
                  .join("  ·  ") || "No VRF/site/VLAN metadata"}
              </p>
            </header>

            <section aria-label="Utilization summary">
              <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Utilization
              </h2>
              <p className="text-sm">
                <b>{prefix.utilization_pct}%</b> used —{" "}
                {prefix.used_ips.toLocaleString()} used ·{" "}
                {prefix.free_ips.toLocaleString()} free ·{" "}
                {prefix.usable_ips.toLocaleString()} usable of{" "}
                {prefix.total_ips.toLocaleString()} total
                {page.usable_first && page.usable_last && (
                  <span className="text-muted-foreground">
                    {" "}
                    (usable {page.usable_first} – {page.usable_last})
                  </span>
                )}
              </p>
            </section>

            {ranges.length > 0 && (
              <section aria-label="IP ranges">
                <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                  IP ranges ({ranges.length})
                </h2>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Range</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Size</TableHead>
                      <TableHead>Description</TableHead>
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
                          {(
                            Number(r.end_int) -
                            Number(r.start_int) +
                            1
                          ).toLocaleString()}
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {r.description ?? "—"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </section>
            )}

            <section aria-label="Addresses">
              <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Addresses ({addrs.length.toLocaleString()} allocated
                {page.total > addrs.length
                  ? ` · ${(page.total - addrs.length).toLocaleString()} free`
                  : ""}
                )
              </h2>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Address</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Hostname</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>MAC</TableHead>
                    <TableHead>Vendor</TableHead>
                    <TableHead>Last seen</TableHead>
                    <TableHead>Notes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {addrs.map((a) => (
                    <TableRow key={a.id}>
                      <TableCell className="font-mono">{a.address}</TableCell>
                      <TableCell>
                        <IpStatusBadge s={a.status} />
                      </TableCell>
                      <TableCell dir="auto">{a.hostname ?? "—"}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {a.role ?? "—"}
                      </TableCell>
                      <TableCell dir="ltr" className="font-mono text-xs">
                        {a.mac_address ?? "—"}
                      </TableCell>
                      <TableCell dir="auto" className="text-muted-foreground">
                        {a.vendor ?? "—"}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {timeAgo(a.last_seen)}
                      </TableCell>
                      <TableCell
                        dir="auto"
                        className="max-w-56 truncate text-muted-foreground"
                      >
                        {a.notes ?? "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                  {addrs.length === 0 && (
                    <TableRow>
                      <TableCell
                        colSpan={8}
                        className="py-8 text-center text-muted-foreground"
                      >
                        No addresses allocated — the whole prefix is free.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
              {page.total > 20000 && (
                <p className="mt-1 text-xs text-muted-foreground">
                  Report capped at 20,000 rows (of {page.total.toLocaleString()}{" "}
                  addresses); export CSV for the complete list.
                </p>
              )}
            </section>

            <footer className="border-t pt-2 text-xs text-muted-foreground">
              Generated {fmtTs(generated)} · IpamBox · {prefix.prefix}
            </footer>
          </article>
        )}
      </AsyncPanel>
    </div>
  );
}
