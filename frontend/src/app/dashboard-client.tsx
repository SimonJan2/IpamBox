"use client";

import { useCallback, useEffect } from "react";
import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  Cable,
  Globe,
  HardDrive,
  History,
  Inbox,
  Network,
  Percent,
  Server,
  ShieldAlert,
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
import { useAsyncData } from "@/lib/use-async-data";
import { useChartTheme } from "@/lib/use-chart-theme";
import { usePolling } from "@/lib/use-polling";
import { timeAgo } from "@/lib/utils";
import type { ChangeLogEntry, DashboardStats, Page, Prefix, ScanJob } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { ExpiryBadge } from "@/components/expiry-badge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ScanStatusBadge } from "@/components/status-badge";
import { Skeleton } from "@/components/ui/separator";

const ACTION_STYLES: Record<string, string> = {
  create: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
  update: "border-amber-500/30 bg-amber-500/10 text-amber-400",
  delete: "border-rose-500/30 bg-rose-500/10 text-rose-400",
};

function StatCard({
  title,
  value,
  sub,
  icon: Icon,
  href,
}: {
  title: string;
  value: React.ReactNode;
  sub?: string;
  icon: React.ElementType;
  href: string;
}) {
  return (
    <Link href={href} className="block">
      <Card className="h-full transition-colors hover:border-emerald-500/30">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <Icon className="h-4 w-4 text-emerald-400" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          {sub && <p className="mt-1 text-xs text-muted-foreground">{sub}</p>}
        </CardContent>
      </Card>
    </Link>
  );
}

export default function DashboardPage() {
  const statsQ = useAsyncData(() =>
    api.get<DashboardStats>("/api/v1/dashboard/stats")
  );
  const prefixesQ = useAsyncData(() =>
    // the chart renders the top 12 by utilization — ask for exactly that
    api.get<Prefix[]>("/api/v1/prefixes?order_by=utilization&limit=12")
  );
  const scansQ = useAsyncData(() =>
    api.get<ScanJob[]>("/api/v1/scans?limit=6")
  );
  const activityQ = useAsyncData(() =>
    api.get<Page<ChangeLogEntry>>("/api/v1/changelog?limit=6").then((p) => p.items)
  );

  const refresh = useCallback(async () => {
    const r = await Promise.all([
      statsQ.reload(),
      prefixesQ.reload(),
      scansQ.reload(),
      activityQ.reload(),
    ]);
    return JSON.stringify(r);
  }, [statsQ.reload, prefixesQ.reload, scansQ.reload, activityQ.reload]);

  usePolling(refresh, { interval: 8000 });

  useEffect(() => {
    const onEv = () => void refresh();
    window.addEventListener("ipam:refresh", onEv);
    return () => window.removeEventListener("ipam:refresh", onEv);
  }, [refresh]);

  const chartTheme = useChartTheme();
  const stats = statsQ.data;
  const prefixes = prefixesQ.data ?? [];
  const scans = scansQ.data ?? [];
  const activity = activityQ.data ?? [];

  const chartData = [...prefixes]
    // IPv6 prefixes report no utilization — nothing to chart
    .filter((p) => p.status !== "container" && p.utilization_pct !== null)
    .sort((a, b) => (b.utilization_pct ?? 0) - (a.utilization_pct ?? 0))
    .slice(0, 12)
    .map((p) => ({ name: p.prefix, pct: p.utilization_pct ?? 0 }));

  return (
    <div className="space-y-6">
      <h1 className="flex items-center gap-1.5 text-xl font-semibold">Dashboard <DocsLink slug="overview" /></h1>

      <AsyncPanel
        loading={statsQ.loading}
        error={statsQ.error}
        onRetry={statsQ.reload}
        skeleton={<Skeleton className="h-44 w-full" />}
      >
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Managed subnets"
          value={stats?.prefixes_total ?? <Skeleton className="h-7 w-12" />}
          sub={`${stats?.sites_total ?? 0} sites · ${stats?.vrfs_total ?? 0} VRFs`}
          icon={Network}
          href="/prefixes"
        />
        <StatCard
          title="IPs tracked"
          value={
            stats ? `${stats.ips_used.toLocaleString()} / ${stats.ips_total.toLocaleString()}` : "—"
          }
          sub={`${stats?.ips_free.toLocaleString() ?? 0} free`}
          icon={Globe}
          href="/prefixes"
        />
        <StatCard
          title="Utilization"
          value={stats ? `${stats.utilization_pct}%` : "—"}
          sub="of usable space"
          icon={Percent}
          href="/prefixes"
        />
        <StatCard
          title="Active devices"
          value={stats?.devices_active ?? "—"}
          sub={`${stats?.devices_discovered ?? 0} pending review`}
          icon={Activity}
          href="/discovery"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Circuits"
          value={stats?.circuits_total ?? "—"}
          icon={Cable}
          href="/circuits"
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
          href="/certificates"
        />
        <StatCard
          title="Assets"
          value={stats?.assets_total ?? "—"}
          icon={HardDrive}
          href="/inventory"
        />
        <StatCard
          title="Services"
          value={stats?.services_total ?? "—"}
          icon={Server}
          href="/services"
        />
      </div>
      </AsyncPanel>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="flex items-center gap-2 text-base">
              <ShieldAlert className="h-4 w-4 text-amber-400" />
              Certificates expiring soon
            </CardTitle>
            <Link
              href="/certificates"
              className="text-xs text-muted-foreground hover:underline"
            >
              {stats && stats.certs_expiring_30d > 0
                ? `${stats.certs_expiring_30d} total · view all`
                : "view all"}
            </Link>
          </CardHeader>
          <CardContent className="space-y-2">
            <AsyncPanel
              loading={statsQ.loading}
              error={statsQ.error}
              onRetry={statsQ.reload}
              empty={stats?.certs_expiring.length === 0}
              emptyMessage="No certificates expiring within 30 days."
            >
              {stats?.certs_expiring.map((c) => (
                <Link
                  key={c.id}
                  href="/certificates"
                  className="flex items-center justify-between gap-3 rounded-md border p-2.5 transition-colors hover:bg-accent"
                >
                  <span className="min-w-0">
                    <span dir="auto" className="block truncate text-sm font-medium">
                      {c.cert_name ?? c.server_name ?? `certificate #${c.id}`}
                    </span>
                    <span
                      dir="auto"
                      className="block truncate text-xs text-muted-foreground"
                    >
                      {[c.platform, c.server_name].filter(Boolean).join(" · ") || "—"}
                    </span>
                  </span>
                  <ExpiryBadge expiresOn={c.expires_on} />
                </Link>
              ))}
            </AsyncPanel>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="h-4 w-4 text-amber-400" />
              MAC mismatches
            </CardTitle>
            {stats && stats.mac_mismatches > 0 && (
              <span className="text-xs text-muted-foreground">
                {stats.mac_mismatches} flagged
              </span>
            )}
          </CardHeader>
          <CardContent className="space-y-2">
            <AsyncPanel
              loading={statsQ.loading}
              error={statsQ.error}
              onRetry={statsQ.reload}
              empty={stats?.mac_mismatch_items.length === 0}
              emptyMessage="No mismatches flagged."
            >
              {stats?.mac_mismatch_items.map((m) => (
                <Link
                  key={m.id}
                  href={`/prefixes/${m.prefix_id}`}
                  className="flex items-center gap-3 rounded-md border p-2.5 transition-colors hover:bg-accent"
                >
                  <span dir="ltr" className="font-mono text-sm">
                    {m.address}
                  </span>
                  <span
                    dir="ltr"
                    className="min-w-0 truncate font-mono text-xs text-muted-foreground"
                  >
                    {m.mac_was ?? "?"} → {m.mac_seen ?? "?"}
                  </span>
                  <span className="ml-auto whitespace-nowrap text-xs text-muted-foreground">
                    {timeAgo(m.flagged_at)}
                  </span>
                </Link>
              ))}
            </AsyncPanel>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Subnet utilization</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            <AsyncPanel
              loading={prefixesQ.loading}
              error={prefixesQ.error}
              onRetry={prefixesQ.reload}
              empty={chartData.length === 0}
              emptyMessage="No prefixes yet — run a scan or create one."
              skeleton={<Skeleton className="h-full w-full" />}
              className="h-full"
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
                  <XAxis
                    dataKey="name"
                    tick={{ fill: chartTheme.axis, fontSize: 11 }}
                    interval={0}
                    angle={-35}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis
                    tick={{ fill: chartTheme.axis, fontSize: 11 }}
                    unit="%"
                    width={42}
                  />
                  <RTooltip
                    cursor={{ fill: chartTheme.cursor }}
                    contentStyle={{
                      background: chartTheme.tooltipBg,
                      border: `1px solid ${chartTheme.tooltipBorder}`,
                      borderRadius: 8,
                      fontSize: 12,
                      color: chartTheme.tooltipText,
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
            </AsyncPanel>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent scans</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <AsyncPanel
              loading={scansQ.loading}
              error={scansQ.error}
              onRetry={scansQ.reload}
              empty={scans.length === 0}
              emptyMessage="No scans yet."
            >
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
            </AsyncPanel>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="flex items-center gap-2 text-base">
            <History className="h-4 w-4 text-emerald-400" />
            Recent activity
          </CardTitle>
          <Link
            href="/changelog"
            className="text-xs text-muted-foreground hover:underline"
          >
            view all
          </Link>
        </CardHeader>
        <CardContent className="space-y-1.5">
          <AsyncPanel
            loading={activityQ.loading}
            error={activityQ.error}
            onRetry={activityQ.reload}
            empty={activity.length === 0}
            emptyMessage="No changes recorded yet."
          >
          {activity.map((e) => (
            <div
              key={e.id}
              className="flex items-center gap-3 rounded-md border p-2.5"
            >
              <Badge variant="outline" className={ACTION_STYLES[e.action]}>
                {e.action}
              </Badge>
              <span className="min-w-0 truncate text-sm">
                <span className="text-muted-foreground">{e.object_type}</span>{" "}
                <span dir="auto" className="font-mono text-xs">
                  {e.object_repr}
                </span>
              </span>
              <span className="ml-auto whitespace-nowrap text-xs text-muted-foreground">
                {e.actor} · {timeAgo(e.ts)}
              </span>
            </div>
          ))}
          </AsyncPanel>
        </CardContent>
      </Card>
    </div>
  );
}
