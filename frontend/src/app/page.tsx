"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  Cable,
  Globe,
  HardDrive,
  Inbox,
  Network,
  Percent,
  Server,
  ShieldCheck,
} from "lucide-react";
import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip as RTooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type { DashboardStats, Prefix, ScanJob } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScanStatusBadge } from "@/components/status-badge";
import { Skeleton } from "@/components/ui/separator";

function StatCard({
  title,
  value,
  sub,
  icon: Icon,
}: {
  title: string;
  value: React.ReactNode;
  sub?: string;
  icon: React.ElementType;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="h-4 w-4 text-emerald-400" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {sub && <p className="mt-1 text-xs text-muted-foreground">{sub}</p>}
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [prefixes, setPrefixes] = useState<Prefix[]>([]);
  const [scans, setScans] = useState<ScanJob[]>([]);

  const refresh = useCallback(() => {
    api.get<DashboardStats>("/api/v1/dashboard/stats").then(setStats).catch(() => {});
    api.get<Prefix[]>("/api/v1/prefixes").then(setPrefixes).catch(() => {});
    api.get<ScanJob[]>("/api/v1/scans?limit=6").then(setScans).catch(() => {});
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 8000);
    const onEv = () => refresh();
    window.addEventListener("ipam:refresh", onEv);
    return () => {
      clearInterval(t);
      window.removeEventListener("ipam:refresh", onEv);
    };
  }, [refresh]);

  const chartData = [...prefixes]
    .filter((p) => p.status !== "container")
    .sort((a, b) => b.utilization_pct - a.utilization_pct)
    .slice(0, 12)
    .map((p) => ({ name: p.prefix, pct: p.utilization_pct }));

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Dashboard</h1>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Managed subnets"
          value={stats?.prefixes_total ?? <Skeleton className="h-7 w-12" />}
          sub={`${stats?.sites_total ?? 0} sites · ${stats?.vrfs_total ?? 0} VRFs`}
          icon={Network}
        />
        <StatCard
          title="IPs tracked"
          value={
            stats ? `${stats.ips_used.toLocaleString()} / ${stats.ips_total.toLocaleString()}` : "—"
          }
          sub={`${stats?.ips_free.toLocaleString() ?? 0} free`}
          icon={Globe}
        />
        <StatCard
          title="Utilization"
          value={stats ? `${stats.utilization_pct}%` : "—"}
          sub="of usable space"
          icon={Percent}
        />
        <StatCard
          title="Active devices"
          value={stats?.devices_active ?? "—"}
          sub={`${stats?.devices_discovered ?? 0} pending review`}
          icon={Activity}
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Circuits"
          value={stats?.circuits_total ?? "—"}
          icon={Cable}
        />
        <StatCard
          title="Certificates"
          value={stats?.certificates_total ?? "—"}
          sub={
            stats && stats.certs_expiring_30d > 0
              ? `${stats.certs_expiring_30d} expiring within 30d`
              : "none expiring soon"
          }
          icon={ShieldCheck}
        />
        <StatCard
          title="Assets"
          value={stats?.assets_total ?? "—"}
          icon={HardDrive}
        />
        <StatCard
          title="Services"
          value={stats?.services_total ?? "—"}
          sub={
            stats && stats.mac_mismatches > 0
              ? `${stats.mac_mismatches} MAC mismatch(es) flagged`
              : undefined
          }
          icon={Server}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Subnet utilization</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            {chartData.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                No prefixes yet — run a scan or create one.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
                  <XAxis
                    dataKey="name"
                    tick={{ fill: "#71717a", fontSize: 11 }}
                    interval={0}
                    angle={-35}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis tick={{ fill: "#71717a", fontSize: 11 }} unit="%" width={42} />
                  <RTooltip
                    cursor={{ fill: "rgba(255,255,255,0.04)" }}
                    contentStyle={{
                      background: "#18181b",
                      border: "1px solid #27272a",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                    formatter={(v) => [`${v}%`, "utilization"]}
                  />
                  <Bar dataKey="pct" radius={[4, 4, 0, 0]}>
                    {chartData.map((d) => (
                      <Cell
                        key={d.name}
                        fill={d.pct > 80 ? "#f43f5e" : d.pct > 50 ? "#f59e0b" : "#10b981"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent scans</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {scans.length === 0 && (
              <p className="text-sm text-muted-foreground">No scans yet.</p>
            )}
            {scans.map((s) => (
              <Link
                key={s.id}
                href="/scans"
                className="block rounded-md border p-3 transition-colors hover:bg-accent"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm">{s.cidr || "auto"}</span>
                  <ScanStatusBadge s={s.status} />
                </div>
                <div className="mt-2 flex items-center gap-3">
                  <Progress value={s.progress} className="h-1.5" />
                  <span className="whitespace-nowrap text-xs text-muted-foreground">
                    {s.hosts_discovered} hosts · {timeAgo(s.created_at)}
                  </span>
                </div>
              </Link>
            ))}
            {stats && stats.devices_discovered > 0 && (
              <Link
                href="/discovery"
                className="flex items-center gap-2 rounded-md border border-violet-500/30 bg-violet-500/10 p-3 text-sm text-violet-300"
              >
                <Inbox className="h-4 w-4" />
                {stats.devices_discovered} discovered hosts await review
              </Link>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
