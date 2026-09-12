"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Zap } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import type { AddressPage, IpAddress, Prefix } from "@/types";
import { IpDrawer } from "@/components/ip-drawer";
import { PrefixStatusBadge } from "@/components/status-badge";
import { SubnetGrid } from "@/components/subnet-grid";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/separator";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { IpStatusBadge } from "@/components/status-badge";
import { timeAgo } from "@/lib/utils";

const MAX_GRID = 65536; // /16 and smaller render as a grid; bigger -> table

export default function PrefixDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const prefixId = Number(id);
  const [prefix, setPrefix] = useState<Prefix | null>(null);
  const [page, setPage] = useState<AddressPage | null>(null);
  const [drawer, setDrawer] = useState<{ ip: string; addr: IpAddress | null } | null>(null);

  const refresh = useCallback(() => {
    api.get<Prefix>(`/api/v1/prefixes/${prefixId}`).then(setPrefix).catch(() => {});
    api
      .get<AddressPage>(`/api/v1/prefixes/${prefixId}/addresses?limit=20000`)
      .then(setPage)
      .catch(() => {});
  }, [prefixId]);

  useEffect(refresh, [refresh]);

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

  const isV4 = !!prefix && !prefix.prefix.includes(":");
  const showGrid = isV4 && (page?.total ?? 0) <= MAX_GRID;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/prefixes">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        {prefix ? (
          <>
            <h1 className="font-mono text-xl font-semibold">{prefix.prefix}</h1>
            <PrefixStatusBadge s={prefix.status} />
            {prefix.vlan_id && (
              <span className="text-sm text-muted-foreground">
                VLAN {prefix.vlan_id}
                {prefix.vlan_name ? ` · ${prefix.vlan_name}` : ""}
              </span>
            )}
          </>
        ) : (
          <Skeleton className="h-7 w-48" />
        )}
        <div className="ml-auto">
          <Button size="sm" variant="outline" onClick={allocNext}>
            <Zap /> Allocate next free IP
          </Button>
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
            {prefix.description && (
              <span className="ml-auto text-muted-foreground">{prefix.description}</span>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-base">
            Address map
            <span className="flex gap-3 text-xs font-normal text-muted-foreground">
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-emerald-500/60" />active</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-violet-500/60" />discovered</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-amber-500/60" />reserved</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-cyan-500/60" />dhcp</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-zinc-600/60" />offline</i>
              <i className="flex items-center gap-1"><i className="h-2.5 w-2.5 rounded-sm bg-zinc-800" />free</i>
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!page ? (
            <Skeleton className="h-64 w-full" />
          ) : showGrid ? (
            <SubnetGrid
              page={page}
              onSelect={(ip, addr) => setDrawer({ ip, addr })}
            />
          ) : (
            <AddressTable items={page.items} onSelect={(a) => setDrawer({ ip: a.address, addr: a })} />
          )}
        </CardContent>
      </Card>

      {drawer && (
        <IpDrawer
          open
          onOpenChange={(o) => !o && setDrawer(null)}
          ip={drawer.ip}
          addr={drawer.addr}
          prefixId={prefixId}
          onSaved={refresh}
        />
      )}
    </div>
  );
}

function AddressTable({
  items,
  onSelect,
}: {
  items: IpAddress[];
  onSelect: (a: IpAddress) => void;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Address</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Hostname</TableHead>
          <TableHead>MAC</TableHead>
          <TableHead>Vendor</TableHead>
          <TableHead>Last seen</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((a) => (
          <TableRow key={a.id} className="cursor-pointer" onClick={() => onSelect(a)}>
            <TableCell className="font-mono">{a.address}</TableCell>
            <TableCell>
              <IpStatusBadge s={a.status} />
            </TableCell>
            <TableCell>{a.hostname ?? "—"}</TableCell>
            <TableCell className="font-mono text-xs">{a.mac_address ?? "—"}</TableCell>
            <TableCell className="text-muted-foreground">{a.vendor ?? "—"}</TableCell>
            <TableCell className="text-muted-foreground">{timeAgo(a.last_seen)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
