"use client";

import { useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  ChevronRight,
  FileDown,
  FileSpreadsheet,
  Loader2,
  Play,
  Trash2,
  Upload,
  XCircle,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import { cn } from "@/lib/utils";
import type { ImportBatch, Page, RowResult, SheetPreview, Site } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
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

const NEW_SITE = "__new__"; // backend sentinel: create site from sheet title

const FAMILY_LABEL: Record<string, string> = {
  sites_master: "Sites",
  site_sheet: "Site sheet",
  circuits: "Circuits",
  certificates: "Certificates",
  assets: "Assets",
  services: "Services",
  inventory: "Inventory",
  empty: "Empty",
  unknown: "Unknown",
};

type Counts = Record<string, number>;

interface UploadResp {
  batch: ImportBatch;
  sheets: SheetPreview[];
  counts: Counts;
}
interface PreviewResp {
  sheets: SheetPreview[];
  counts: Counts;
  rows: RowResult[];
}
interface CommitResp {
  counts: Counts;
  rows: RowResult[];
}

const ACTION_STYLE: Record<string, string> = {
  create: "text-emerald-400",
  update: "text-sky-400",
  skip: "text-muted-foreground",
  conflict: "text-amber-400",
  error: "text-rose-400",
};

const STEPS = [
  { id: "upload", label: "Upload" },
  { id: "sheets", label: "Sheet detection" },
  { id: "preview", label: "Preview" },
  { id: "result", label: "Commit" },
] as const;
type Step = (typeof STEPS)[number]["id"];

function Stepper({ step }: { step: Step }) {
  const idx = STEPS.findIndex((s) => s.id === step);
  return (
    <ol className="flex flex-wrap items-center gap-x-3 gap-y-2 text-sm">
      {STEPS.map((s, i) => (
        <li key={s.id} className="flex items-center gap-2">
          {i > 0 && <span className="h-px w-5 bg-border" />}
          <span
            className={cn(
              "flex h-6 w-6 items-center justify-center rounded-full border text-xs",
              i <= idx
                ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-400"
                : "text-muted-foreground"
            )}
          >
            {i < idx ? <Check className="h-3 w-3" /> : i + 1}
          </span>
          <span
            className={
              i === idx ? "font-medium" : "text-muted-foreground"
            }
          >
            {s.label}
          </span>
        </li>
      ))}
    </ol>
  );
}

function CountCards({ counts }: { counts: Counts }) {
  const order = ["create", "update", "skip", "conflict", "error"];
  return (
    <div className="flex flex-wrap gap-3">
      {order
        .filter((k) => (counts[k] ?? 0) > 0)
        .map((k) => (
          <div
            key={k}
            className="rounded-lg border bg-card px-4 py-2 text-center"
          >
            <div className={`text-xl font-semibold ${ACTION_STYLE[k]}`}>
              {counts[k]}
            </div>
            <div className="text-xs capitalize text-muted-foreground">{k}</div>
          </div>
        ))}
    </div>
  );
}

function RowsGrid({
  rows,
  showSheet = true,
}: {
  rows: RowResult[];
  showSheet?: boolean;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          {showSheet && <TableHead>Sheet</TableHead>}
          <TableHead className="w-16">Row</TableHead>
          <TableHead className="w-24">Action</TableHead>
          <TableHead>Detail</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r, i) => (
          <TableRow key={i}>
            {showSheet && (
              <TableCell dir="auto" className="font-medium">
                {r.sheet}
              </TableCell>
            )}
            <TableCell className="font-mono text-muted-foreground">
              {r.row}
            </TableCell>
            <TableCell className={ACTION_STYLE[r.action] ?? ""}>
              {r.action}
            </TableCell>
            <TableCell dir="auto" className="text-muted-foreground">
              {r.detail}
            </TableCell>
          </TableRow>
        ))}
        {rows.length === 0 && (
          <TableRow>
            <TableCell
              colSpan={showSheet ? 4 : 3}
              className="py-8 text-center text-muted-foreground"
            >
              No rows in this category.
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}

const ROW_CAP = 500;

function RowsTable({ rows }: { rows: RowResult[] }) {
  const [filter, setFilter] = useState("all");
  const filtered = useMemo(
    () => (filter === "all" ? rows : rows.filter((r) => r.action === filter)),
    [rows, filter]
  );
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Show:</span>
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All rows</SelectItem>
            <SelectItem value="conflict">Conflicts</SelectItem>
            <SelectItem value="error">Errors</SelectItem>
            <SelectItem value="skip">Skipped</SelectItem>
            <SelectItem value="create">Creates</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-sm text-muted-foreground">
          {filtered.length} of {rows.length} reported rows
        </span>
      </div>
      <div className="max-h-80 overflow-auto rounded-lg border">
        <RowsGrid rows={filtered.slice(0, ROW_CAP)} />
      </div>
      {filtered.length > ROW_CAP && (
        <p className="text-xs text-muted-foreground">
          Showing first {ROW_CAP} of {filtered.length}.
        </p>
      )}
    </div>
  );
}

const SHEET_ROW_CAP = 300;

/** Per-sheet expandable drill-down for the preview step (UX-12). */
function SheetResults({
  sheets,
  rows,
}: {
  sheets: SheetPreview[];
  rows: RowResult[];
}) {
  const bySheet = useMemo(() => {
    const m = new Map<string, RowResult[]>();
    for (const r of rows) {
      const list = m.get(r.sheet);
      if (list) list.push(r);
      else m.set(r.sheet, [r]);
    }
    return m;
  }, [rows]);

  const names = useMemo(() => {
    const order = sheets.map((s) => s.sheet);
    for (const k of bySheet.keys()) {
      if (!order.includes(k)) order.push(k);
    }
    return order;
  }, [sheets, bySheet]);

  // Sheets with errors/conflicts start expanded — they're what needs review.
  const [open, setOpen] = useState<Set<string>>(
    () =>
      new Set(
        names.filter((n) =>
          (bySheet.get(n) ?? []).some(
            (r) => r.action === "error" || r.action === "conflict"
          )
        )
      )
  );

  return (
    <div className="divide-y rounded-lg border">
      {names.map((name) => {
        const meta = sheets.find((s) => s.sheet === name);
        const sheetRows = bySheet.get(name) ?? [];
        const counts: Counts = {};
        for (const r of sheetRows) {
          counts[r.action] = (counts[r.action] ?? 0) + 1;
        }
        const isOpen = open.has(name);
        return (
          <div key={name}>
            <button
              onClick={() => {
                const next = new Set(open);
                if (isOpen) next.delete(name);
                else next.add(name);
                setOpen(next);
              }}
              className="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-accent/50"
            >
              <ChevronRight
                className={cn(
                  "h-4 w-4 shrink-0 text-muted-foreground transition-transform",
                  isOpen && "rotate-90"
                )}
              />
              <span dir="auto" className="font-medium">
                {name}
              </span>
              {meta && (
                <Badge variant="outline">
                  {FAMILY_LABEL[meta.family] ?? meta.family}
                </Badge>
              )}
              <span className="ml-auto flex gap-2 text-xs">
                {["create", "update", "skip", "conflict", "error"]
                  .filter((k) => (counts[k] ?? 0) > 0)
                  .map((k) => (
                    <span key={k} className={ACTION_STYLE[k]}>
                      {counts[k]} {k}
                    </span>
                  ))}
                {sheetRows.length === 0 && (
                  <span className="text-muted-foreground">no row results</span>
                )}
              </span>
            </button>
            {isOpen && (
              <div className="max-h-72 overflow-auto border-t">
                <RowsGrid rows={sheetRows.slice(0, SHEET_ROW_CAP)} showSheet={false} />
                {sheetRows.length > SHEET_ROW_CAP && (
                  <p className="px-3 py-2 text-xs text-muted-foreground">
                    Showing first {SHEET_ROW_CAP} of {sheetRows.length} rows.
                  </p>
                )}
              </div>
            )}
          </div>
        );
      })}
      {names.length === 0 && (
        <p className="px-3 py-6 text-center text-sm text-muted-foreground">
          No sheets in this preview.
        </p>
      )}
    </div>
  );
}

function csvCell(v: unknown): string {
  const s = String(v ?? "");
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export default function ImportPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const fileRef = useRef<HTMLInputElement>(null);

  const batchesQ = useAsyncData(() =>
    api.get<Page<ImportBatch>>("/api/v1/imports").then((p) => p.items)
  );
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Site>>("/api/v1/sites").then((p) => p.items);
    } catch (e) {
      toast.error("Could not load sites", { description: String(e) });
      return [];
    }
  });
  const [step, setStep] = useState<Step>("upload");
  const [batch, setBatch] = useState<ImportBatch | null>(null);
  const [sheets, setSheets] = useState<SheetPreview[]>([]);
  const [skipped, setSkipped] = useState<Set<string>>(new Set());
  const [overrides, setOverrides] = useState<Record<string, number | string>>(
    {}
  );
  const [preview, setPreview] = useState<PreviewResp | null>(null);
  const [commitResult, setCommitResult] = useState<CommitResp | null>(null);
  const [busy, setBusy] = useState(false);

  const batches = batchesQ.data ?? [];
  const sites = sitesQ.data ?? [];
  const refreshHistory = () => void batchesQ.reload();

  const resetWizard = () => {
    setStep("upload");
    setBatch(null);
    setSheets([]);
    setSkipped(new Set());
    setOverrides({});
    setPreview(null);
    setCommitResult(null);
  };

  const upload = async (file: File) => {
    setBusy(true);
    setPreview(null);
    setCommitResult(null);
    setOverrides({});
    setSkipped(new Set());
    try {
      const r = await api.upload<UploadResp>(
        `/api/v1/imports/workbook?filename=${encodeURIComponent(file.name)}`,
        file,
        "application/octet-stream"
      );
      setBatch(r.batch);
      setSheets(r.sheets);
      setStep("sheets");
      toast.success(`Detected ${r.sheets.length} sheets`);
    } catch (e) {
      toast.error("Upload failed", { description: String(e) });
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const runPreview = async () => {
    if (!batch) return;
    setBusy(true);
    try {
      const r = await api.post<PreviewResp>(
        `/api/v1/imports/${batch.id}/preview`,
        {
          site_overrides: overrides,
          skip_sheets: [...skipped],
          create_containers: true,
        }
      );
      setPreview(r);
      setSheets(r.sheets);
      setCommitResult(null);
      setStep("preview");
    } catch (e) {
      toast.error("Preview failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const commit = async (partial: boolean) => {
    if (!batch) return;
    setBusy(true);
    try {
      const r = await api.post<CommitResp>(
        `/api/v1/imports/${batch.id}/commit`,
        { partial }
      );
      setCommitResult(r);
      setPreview(null);
      setStep("result");
      refreshHistory();
      toast.success("Import committed", {
        description: `${r.counts.create ?? 0} rows created`,
      });
    } catch (e) {
      toast.error("Commit failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const remove = async (id: number) => {
    try {
      await api.del(`/api/v1/imports/${id}`);
      if (batch?.id === id) resetWizard();
      refreshHistory();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const downloadErrors = () => {
    if (!preview) return;
    const bad = preview.rows.filter(
      (r) => r.action === "error" || r.action === "conflict"
    );
    // \ufeff: UTF-8 BOM so Excel renders Hebrew correctly — same convention
    // as the backend csv_response helper.
    const csv =
      "\ufeffsheet,row,action,detail\n" +
      bad
        .map((r) => [r.sheet, r.row, r.action, r.detail].map(csvCell).join(","))
        .join("\n") +
      "\n";
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(batch?.filename ?? "import").replace(/\.xlsx$/i, "")}-errors.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`Exported ${bad.length} row(s)`);
  };

  const errorCount = preview?.counts?.error ?? 0;
  const issueRows =
    preview?.rows.filter(
      (r) => r.action === "error" || r.action === "conflict"
    ).length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Import workbook</h1>
        {canWrite && <Stepper step={step} />}
      </div>

      {canWrite && (
        <input
          ref={fileRef}
          type="file"
          accept=".xlsx"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) upload(f);
          }}
        />
      )}

      {canWrite && step === "upload" && (
        <div className="flex flex-col items-center gap-3 rounded-lg border border-dashed bg-card p-10 text-center">
          <FileSpreadsheet className="h-8 w-8 text-emerald-400" />
          <div>
            <p className="font-medium">Upload a Network_Address.xlsx workbook</p>
            <p className="text-sm text-muted-foreground">
              Sheets are detected, matched to sites and previewed before
              anything is written.
            </p>
          </div>
          <Button
            size="sm"
            disabled={busy}
            onClick={() => fileRef.current?.click()}
          >
            {busy ? <Loader2 className="animate-spin" /> : <Upload />}
            Choose .xlsx file
          </Button>
        </div>
      )}

      {canWrite && step === "sheets" && batch && (
        <div className="space-y-3 rounded-lg border bg-card p-4">
          <div className="flex items-center gap-2 text-sm">
            <FileSpreadsheet className="h-4 w-4 text-emerald-400" />
            <span dir="auto" className="font-medium">
              {batch.filename}
            </span>
            <span className="text-muted-foreground">
              — {sheets.length} sheets detected
            </span>
          </div>

          <div className="max-h-96 overflow-auto rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10"></TableHead>
                  <TableHead>Sheet</TableHead>
                  <TableHead>Detected as</TableHead>
                  <TableHead className="w-16">Rows</TableHead>
                  <TableHead>Site</TableHead>
                  <TableHead>Warnings</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sheets.map((s) => {
                  const off = skipped.has(s.sheet);
                  return (
                    <TableRow
                      key={s.sheet}
                      className={off ? "opacity-40" : undefined}
                    >
                      <TableCell>
                        <Checkbox
                          checked={!off}
                          aria-label={`Include sheet ${s.sheet} in import`}
                          onCheckedChange={(v) => {
                            const next = new Set(skipped);
                            if (v === true) next.delete(s.sheet);
                            else next.add(s.sheet);
                            setSkipped(next);
                          }}
                        />
                      </TableCell>
                      <TableCell dir="auto" className="font-medium">
                        {s.sheet}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {FAMILY_LABEL[s.family] ?? s.family}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-muted-foreground">
                        {s.rows}
                      </TableCell>
                      <TableCell>
                        {s.family === "site_sheet" ? (
                          <Select
                            value={
                              overrides[s.sheet]?.toString() ??
                              s.site_id?.toString() ??
                              ""
                            }
                            onValueChange={(v) =>
                              setOverrides({
                                ...overrides,
                                [s.sheet]: v === NEW_SITE ? NEW_SITE : +v,
                              })
                            }
                          >
                            <SelectTrigger className="h-8 w-48">
                              <SelectValue placeholder="auto" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value={NEW_SITE}>
                                + New site (from sheet title)
                              </SelectItem>
                              {sites.map((site) => (
                                <SelectItem
                                  key={site.id}
                                  value={site.id.toString()}
                                >
                                  <span dir="auto">{site.name}</span>
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        ) : (
                          <span dir="auto" className="text-muted-foreground">
                            {s.site_name ?? "—"}
                          </span>
                        )}
                        {s.matched_by && (
                          <span className="ml-2 text-xs text-muted-foreground">
                            ({s.matched_by})
                          </span>
                        )}
                      </TableCell>
                      <TableCell>
                        {s.warnings.length > 0 && (
                          <span
                            className="inline-flex items-center gap-1 text-xs text-amber-400"
                            title={s.warnings.join("\n")}
                          >
                            <AlertTriangle className="h-3.5 w-3.5" />
                            {s.warnings.length}
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>

          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setStep("upload")}
            >
              Back
            </Button>
            <Button size="sm" onClick={runPreview} disabled={busy}>
              <Play /> Run dry-run preview
            </Button>
            {skipped.size > 0 && (
              <span className="text-sm text-muted-foreground">
                {skipped.size} sheet(s) will be skipped
              </span>
            )}
          </div>
        </div>
      )}

      {canWrite && step === "preview" && preview && (
        <div className="space-y-3 rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold">Dry-run preview</h2>
            <Button
              size="sm"
              variant="outline"
              onClick={downloadErrors}
              disabled={issueRows === 0}
              title={
                issueRows === 0
                  ? "No errors or conflicts to export"
                  : "Download error & conflict rows as CSV"
              }
            >
              <FileDown /> Error report (CSV)
            </Button>
          </div>
          <CountCards counts={preview.counts} />
          <SheetResults sheets={preview.sheets} rows={preview.rows} />
          <div className="flex items-center gap-2 pt-1">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setStep("sheets")}
            >
              Back
            </Button>
            <Button
              onClick={() => commit(false)}
              disabled={busy || errorCount > 0}
              title={
                errorCount > 0
                  ? "Errors present — use partial commit or fix the source"
                  : "Commit all rows (all-or-nothing)"
              }
            >
              <CheckCircle2 /> Commit all
            </Button>
            <Button
              variant="outline"
              onClick={() => commit(true)}
              disabled={busy}
              title="Commit good rows; failing sheets roll back independently"
            >
              Commit partial
            </Button>
            {errorCount > 0 && (
              <span className="text-sm text-rose-400">
                {errorCount} row(s) have errors — all-or-nothing commit is
                unavailable
              </span>
            )}
          </div>
        </div>
      )}

      {canWrite && step === "result" && commitResult && (
        <div
          role="status"
          className="space-y-3 rounded-lg border border-emerald-500/30 bg-card p-4"
        >
          <h2 className="flex items-center gap-2 font-semibold text-emerald-400">
            <CheckCircle2 className="h-4 w-4" /> Import committed
          </h2>
          <CountCards counts={commitResult.counts} />
          <RowsTable rows={commitResult.rows} />
          <div>
            <Button size="sm" variant="outline" onClick={resetWizard}>
              Import another workbook
            </Button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        <h2 className="font-semibold">Import history</h2>
        <div className="rounded-lg border">
          <AsyncPanel
            loading={batchesQ.loading}
            error={batchesQ.error}
            onRetry={batchesQ.reload}
            empty={batches.length === 0}
            emptyMessage="No imports yet — upload a Network_Address.xlsx workbook."
          >
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>File</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>By</TableHead>
                <TableHead>Uploaded</TableHead>
                <TableHead>Committed</TableHead>
                <TableHead className="w-20 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {batches.map((b) => {
                const cc = (b.stats?.commit_counts ?? b.stats?.counts) as
                  | Counts
                  | undefined;
                return (
                  <TableRow key={b.id}>
                    <TableCell dir="auto" className="font-medium">
                      {b.filename}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={
                          b.status === "committed"
                            ? "border-emerald-500/40 text-emerald-400"
                            : b.status === "failed"
                              ? "border-rose-500/40 text-rose-400"
                              : ""
                        }
                      >
                        {b.status === "committed" ? (
                          <CheckCircle2 className="mr-1 h-3 w-3" />
                        ) : b.status === "failed" ? (
                          <XCircle className="mr-1 h-3 w-3" />
                        ) : null}
                        {b.status}
                        {cc?.create ? ` · ${cc.create}` : ""}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {b.actor ?? "—"}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {fmtTs(b.created_at)}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {fmtTs(b.committed_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      {canWrite && b.status !== "committed" && (
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Delete import ${b.filename}`}
                          onClick={() => remove(b.id)}
                        >
                          <Trash2 className="h-4 w-4 text-rose-400" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
          </AsyncPanel>
        </div>
      </div>
    </div>
  );
}
