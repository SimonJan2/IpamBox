"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import {
  ArrowRight,
  FileDown,
  Mail,
  Printer,
} from "lucide-react";
import { toast } from "sonner";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip as RTooltip,
  XAxis,
  YAxis,
} from "recharts";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { useChartTheme } from "@/lib/use-chart-theme";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import { formatKg, formatWatts } from "@/lib/rack-capacity";
import type {
  IpStatus,
  MonitorState,
  Page,
  ReportCell,
  ReportSection,
  ReportSummary,
  ScanStatus,
  Site,
} from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { ExpiryBadge } from "@/components/expiry-badge";
import {
  IpStatusBadge,
  MonitorStateBadge,
  ScanStatusBadge,
} from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// Donut colors mirror STATUS_TOKENS badge variants (emerald/amber/cyan/
// violet/zinc) — the same vocabulary the dashboard and grid legend use.
const STATUS_HEX: Record<string, string> = {
  active: "#10b981",
  reserved: "#f59e0b",
  dhcp: "#06b6d4",
  discovered: "#8b5cf6",
  offline: "#71717a",
};

function pctCell(v: ReportCell) {
  if (v == null || v === "") return <span className="text-muted-foreground">—</span>;
  const n = Number(v);
  const cls =
    n > 80 ? "text-rose-400" : n > 50 ? "text-amber-400" : "text-emerald-400";
  return <span className={`tabular-nums ${cls}`}>{n}%</span>;
}

/** Column-aware cell rendering — keys are the CSV column names emitted by
 *  the backend so the table on screen matches the downloaded file. */
function cell(key: string, col: string, v: ReportCell): React.ReactNode {
  if (v == null || v === "")
    return <span className="text-muted-foreground">—</span>;
  if (key === "status" && col === "status")
    return <IpStatusBadge s={v as IpStatus} />;
  if (key === "scans" && col === "status")
    return <ScanStatusBadge s={v as ScanStatus} />;
  if (key === "monitors" && col === "value" && ["up", "down", "unknown"].includes(String(v)))
    return <MonitorStateBadge s={v as MonitorState} />;
  if (key === "certs" && col === "expires_on") return <ExpiryBadge expiresOn={String(v)} />;
  if (col.endsWith("_pct")) return pctCell(v);
  if (col === "power_w") return formatWatts(Number(v));
  if (col === "weight_kg") return formatKg(Number(v));
  if (col === "prefix" || col === "cidr") return <span className="font-mono">{v}</span>;
  if (key === "utilization" && col === "bucket")
    return (
      <Badge variant={v === "fullest" ? "amber" : "secondary"}>{v}</Badge>
    );
  if (typeof v === "number") return <span className="tabular-nums">{v.toLocaleString()}</span>;
  return String(v);
}

function SectionTable({ section }: { section: ReportSection }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {section.columns.map((c) => (
            <TableHead key={c}>{c.replaceAll("_", " ")}</TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {section.rows.map((row, i) => (
          <TableRow key={i}>
            {row.map((v, j) => (
              <TableCell key={j} className="whitespace-nowrap" dir="auto">
                {cell(section.key, section.columns[j], v)}
              </TableCell>
            ))}
          </TableRow>
        ))}
        {section.rows.length === 0 && (
          <TableRow>
            <TableCell
              colSpan={section.columns.length || 1}
              className="text-center text-muted-foreground"
            >
              nothing to report
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}

function StatusDonut({ section }: { section: ReportSection }) {
  const theme = useChartTheme();
  const data = section.rows
    .filter((r) => Number(r[1]) > 0)
    .map((r) => ({ name: String(r[0]), value: Number(r[1]) }));
  if (!data.length) return null;
  return (
    <div className="h-44 w-full print:hidden">
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius="55%"
            outerRadius="80%"
            strokeWidth={1}
            stroke={theme.tooltipBorder}
          >
            {data.map((d) => (
              <Cell key={d.name} fill={STATUS_HEX[d.name] ?? "#71717a"} />
            ))}
          </Pie>
          <RTooltip
            contentStyle={{
              background: theme.tooltipBg,
              border: `1px solid ${theme.tooltipBorder}`,
              color: theme.tooltipText,
              borderRadius: 8,
              fontSize: 12,
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

function CapacityBars({ section }: { section: ReportSection }) {
  const theme = useChartTheme();
  const data = section.rows.map((r) => ({
    name: String(r[0]),
    pct: r[6] == null ? 0 : Number(r[6]),
    used: Number(r[3]),
    free: Number(r[4]),
  }));
  if (!data.length) return null;
  return (
    <div className="h-44 w-full print:hidden">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: -12 }}>
          <XAxis
            dataKey="name"
            tick={{ fill: theme.axis, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            unit="%"
            tick={{ fill: theme.axis, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
          />
          <RTooltip
            cursor={{ fill: theme.cursor }}
            contentStyle={{
              background: theme.tooltipBg,
              border: `1px solid ${theme.tooltipBorder}`,
              color: theme.tooltipText,
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(v) => [`${v}%`, "fill"]}
          />
          <Bar dataKey="pct" radius={[4, 4, 0, 0]}>
            {data.map((d) => (
              <Cell
                key={d.name}
                fill={d.pct > 80 ? "#f43f5e" : d.pct > 50 ? "#f59e0b" : "#10b981"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function ReportsClient() {
  const router = useRouter();
  const params = useSearchParams();
  const siteId = params.get("site_id") ?? "";
  const scope = siteId ? `?site_id=${siteId}` : "";
  const { can } = useAuth();
  const [emailing, setEmailing] = useState(false);

  const reportQ = useAsyncData(
    () => api.get<ReportSummary>(`/api/v1/reports/summary${scope}`),
    [scope]
  );
  const sitesQ = useAsyncData(() =>
    api.get<Page<Site>>("/api/v1/sites").then((p) => p.items)
  );
  const report = reportQ.data;

  const setSite = (v: string) =>
    router.replace(v === "all" ? "/reports" : `/reports?site_id=${v}`);

  const email = async () => {
    setEmailing(true);
    try {
      const out = await api.post<{ channels: number }>(
        `/api/v1/reports/email${scope}`
      );
      toast.success(
        out.channels
          ? `Report sent to ${out.channels} channel${out.channels === 1 ? "" : "s"}`
          : "No notification channels are enabled",
        { description: "Channels live under Settings → Monitoring." }
      );
    } catch (e) {
      toast.error("Could not send report", { description: String(e) });
    } finally {
      setEmailing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header row — screen only (the print route has its own header). */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="mr-auto">
          <h1 className="flex items-center gap-1.5 text-xl font-semibold">
            Reports <DocsLink slug="reports" />
          </h1>
          <p className="text-sm text-muted-foreground">
            The whole estate on one page — every number is the same aggregate
            the underlying page shows.
            {report && (
              <span className="ml-1">
                Generated {fmtTs(report.generated_at)}
                {report.site ? ` · scoped to ${report.site.name}` : ""}.
              </span>
            )}
          </p>
        </div>
        <Select value={siteId || "all"} onValueChange={setSite}>
          <SelectTrigger className="w-44" aria-label="Site scope">
            <SelectValue placeholder="All sites" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All sites</SelectItem>
            {(sitesQ.data ?? []).map((s) => (
              <SelectItem key={s.id} value={String(s.id)}>
                {s.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button variant="outline" size="sm" asChild>
          <Link href={`/reports/print${scope}`}>
            <Printer /> Print
          </Link>
        </Button>
        <Button variant="outline" size="sm" asChild>
          <a href={`/api/v1/reports/export.xlsx${scope}`} download>
            <FileDown /> Export .xlsx
          </a>
        </Button>
        {can(PERM.DATA_WRITE) && (
          <Button
            variant="outline"
            size="sm"
            onClick={email}
            disabled={emailing}
            title="Send the digest to every enabled notification channel"
          >
            <Mail /> Email
          </Button>
        )}
      </div>

      <AsyncPanel
        loading={reportQ.loading}
        error={reportQ.error}
        onRetry={reportQ.reload}
        empty={!report}
        emptyMessage="No report data."
      >
        {report && (
          <div className="space-y-6">
            {/* Headline strip — the dashboard's own totals for the scope. */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
              {report.metrics.map((m) => (
                <Card key={m.label}>
                  <CardContent className="p-3">
                    <p className="text-xs text-muted-foreground">{m.label}</p>
                    <p className="mt-0.5 truncate text-sm font-semibold">
                      {m.value ?? "—"}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {report.sections.map((s) => (
              <Card key={s.key} id={`report-${s.key}`}>
                <CardHeader className="flex flex-row items-center justify-between gap-3 space-y-0">
                  <div className="flex min-w-0 flex-wrap items-baseline gap-x-3 gap-y-1">
                    <CardTitle className="text-base">{s.title}</CardTitle>
                    {s.metrics.map((m) => (
                      <span
                        key={m.label}
                        className="text-xs text-muted-foreground"
                      >
                        {m.label}{" "}
                        <span className="font-medium text-foreground">
                          {m.value ?? "—"}
                        </span>
                      </span>
                    ))}
                  </div>
                  <div className="flex shrink-0 items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      asChild
                      title={`Download ${s.title} as CSV`}
                      aria-label={`Download ${s.title} as CSV`}
                    >
                      <a
                        href={`/api/v1/reports/${s.key}.csv${scope}`}
                        download
                      >
                        <FileDown className="h-4 w-4" />
                      </a>
                    </Button>
                    {s.href && (
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={s.href}>
                          view all <ArrowRight className="h-3.5 w-3.5" />
                        </Link>
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {s.key === "status" && <StatusDonut section={s} />}
                  {s.key === "capacity" && <CapacityBars section={s} />}
                  {s.note && (
                    <p className="text-xs text-muted-foreground">{s.note}</p>
                  )}
                  <SectionTable section={s} />
                  {s.truncated && (
                    <p className="text-xs text-amber-400">
                      showing the first {s.rows.length.toLocaleString()} of{" "}
                      {s.total_rows.toLocaleString()} rows
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </AsyncPanel>
    </div>
  );
}
