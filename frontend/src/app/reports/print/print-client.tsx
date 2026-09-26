"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, Printer } from "lucide-react";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { fmtTs } from "@/lib/prefs";
import type { ReportSummary } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

/** Printable estate report: one flat table per section, no charts, no
 *  virtualization — window.print() captures every (bounded) row. Same
 *  convention as the prefix/rack print routes. */
export default function PrintClient() {
  const params = useSearchParams();
  const siteId = params.get("site_id");
  const scope = siteId ? `?site_id=${siteId}` : "";
  const reportQ = useAsyncData(
    () => api.get<ReportSummary>(`/api/v1/reports/summary${scope}`),
    [scope]
  );
  const report = reportQ.data;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      {/* Screen-only toolbar */}
      <div className="flex items-center gap-2 print:hidden">
        <Button variant="ghost" size="icon" aria-label="Back to reports" asChild>
          <Link href={`/reports${scope}`}>
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="text-sm text-muted-foreground">
          Report preview — every section expanded to its full (bounded) table.
        </span>
        <Button size="sm" className="ml-auto" onClick={() => window.print()}>
          <Printer /> Print / save as PDF
        </Button>
      </div>

      <AsyncPanel
        loading={reportQ.loading}
        error={reportQ.error}
        onRetry={reportQ.reload}
        empty={!report}
        emptyMessage="No report data."
      >
        {report && (
          <article className="space-y-8 print:space-y-6">
            <header className="space-y-1 border-b pb-3">
              <div className="flex flex-wrap items-baseline gap-3">
                <h1 className="text-2xl font-semibold">Estate report</h1>
                <span className="text-sm text-muted-foreground">
                  {report.site ? report.site.name : "All sites"}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                Generated {fmtTs(report.generated_at)} ·{" "}
                {report.metrics
                  .map((m) => `${m.label} ${m.value ?? "—"}`)
                  .join(" · ")}
              </p>
            </header>

            {report.sections.map((s) => (
              <section key={s.key} className="space-y-2">
                <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 break-after-avoid">
                  <h2 className="text-lg font-semibold">{s.title}</h2>
                  {s.metrics.map((m) => (
                    <span key={m.label} className="text-xs text-muted-foreground">
                      {m.label} <span className="text-foreground">{m.value ?? "—"}</span>
                    </span>
                  ))}
                </div>
                {s.note && (
                  <p className="text-xs text-muted-foreground">{s.note}</p>
                )}
                <Table>
                  <TableHeader>
                    <TableRow>
                      {s.columns.map((c) => (
                        <TableHead key={c}>{c.replaceAll("_", " ")}</TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {s.rows.map((row, i) => (
                      <TableRow key={i}>
                        {row.map((v, j) => (
                          <TableCell key={j} dir="auto">
                            {v == null || v === "" ? "—" : String(v)}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                    {s.rows.length === 0 && (
                      <TableRow>
                        <TableCell
                          colSpan={s.columns.length || 1}
                          className="text-center text-muted-foreground"
                        >
                          nothing to report
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
                {s.truncated && (
                  <p className="text-xs">
                    showing the first {s.rows.length.toLocaleString()} of{" "}
                    {s.total_rows.toLocaleString()} rows
                  </p>
                )}
              </section>
            ))}

            <footer className="border-t pt-2 text-xs text-muted-foreground">
              IpamBox estate report — generated {fmtTs(report.generated_at)}.
              Sections are bounded; full data lives on the linked pages.
            </footer>
          </article>
        )}
      </AsyncPanel>
    </div>
  );
}
