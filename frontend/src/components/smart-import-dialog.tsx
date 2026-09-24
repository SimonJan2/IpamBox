"use client";

import { Fragment, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  ChevronRight,
  FileSpreadsheet,
  Loader2,
  Play,
  Upload,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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

// ---------------------------------------------------------------------------
// Reusable smart-import dialog: file -> auto-map -> dry-run preview -> commit.
// The backend endpoint drives everything; the dialog is a thin client over
// detect=1 / dry_run=1 / dry_run=0 posts of the same file — no staging.
// ---------------------------------------------------------------------------

export interface FieldOption {
  value: string; // canonical backend field, e.g. "serial_number"
  label: string; // display label, e.g. "Serial number"
}

/** Mode controls rendered between the mapping table and the commit row.
 * `param` is appended to the import query string verbatim. */
export type ImportOption =
  | {
      kind: "select";
      param: string;
      label: string;
      choices: { value: string; label: string }[];
      defaultValue: string;
    }
  | { kind: "flag"; param: string; label: string; defaultValue?: boolean };

interface ColumnMap {
  header: string;
  field: string | null;
}

interface RowResult {
  row: number;
  ok: boolean;
  action: "create" | "update" | "skip" | "error" | string;
  detail: string;
  diff?: Record<string, [unknown, unknown]>;
  /** Bundle imports tag each row with the sheet it came from (V5C). */
  sheet?: string;
}

interface DetectResp {
  columns: ColumnMap[];
  unmapped: string[];
  row_count: number;
  warnings?: string[];
  sheets?: { name: string; family: string | null; row_count: number }[];
}

interface ImportResp {
  counts: Record<string, number>;
  rows: RowResult[];
  columns: ColumnMap[];
  unmapped: string[];
  committed: boolean;
  warnings?: string[];
}

export interface SmartImportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** e.g. "/api/v1/devices/import" — must accept the V5B smart-import
   * contract (detect/dry_run/on_match/mapping/force params). */
  endpoint: string;
  /** Canonical fields offered in the mapping selects, in display order. */
  fields: FieldOption[];
  title?: string;
  description?: string;
  /** Endpoint-specific mode radios (on_match, unracked_on_missing, ...). */
  options?: ImportOption[];
  /** Constant query params appended to every request (e.g. group_id). */
  extraParams?: Record<string, string>;
  /** Called after a successful commit — reload the page's data here. */
  onCommitted?: () => void;
}

const ACTION_STYLE: Record<string, string> = {
  create: "text-emerald-400",
  update: "text-sky-400",
  skip: "text-muted-foreground",
  error: "text-rose-400",
};

const UNMAPPED = "__none__";
const ROW_CAP = 400;

function fmt(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  return String(v);
}

function CountCards({ counts }: { counts: Record<string, number> }) {
  const order = ["create", "update", "skip", "error"];
  return (
    <div className="flex flex-wrap gap-3">
      {order
        .filter((k) => (counts[k] ?? 0) > 0)
        .map((k) => (
          <div key={k} className="rounded-lg border bg-card px-4 py-2 text-center">
            <div className={`text-xl font-semibold ${ACTION_STYLE[k]}`}>
              {counts[k]}
            </div>
            <div className="text-xs capitalize text-muted-foreground">{k}</div>
          </div>
        ))}
    </div>
  );
}

function ResultRows({ rows }: { rows: RowResult[] }) {
  const [open, setOpen] = useState<Set<string>>(new Set());
  // Bundle imports (V5C) tag rows with their sheet — group the preview so
  // group/rack/device/interface/cable verdicts stay readable.
  const sections = useMemo(() => {
    const order: string[] = [];
    const by: Record<string, RowResult[]> = {};
    for (const r of rows) {
      const s = r.sheet ?? "";
      if (!(s in by)) {
        by[s] = [];
        order.push(s);
      }
      by[s].push(r);
    }
    return order.map((s) => [s, by[s]] as const);
  }, [rows]);
  const grouped = sections.some(([s]) => s !== "");
  return (
    <div className="max-h-72 overflow-auto rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-16">Row</TableHead>
            <TableHead className="w-24">Action</TableHead>
            <TableHead>Detail</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {(() => {
            let shown = 0;
            return sections.flatMap(([sheet, srows]) => {
              const visible = srows.slice(0, Math.max(0, ROW_CAP - shown));
              shown += srows.length;
              return [
            ...(grouped
              ? [
                  <TableRow key={`s-${sheet}`} className="bg-muted/40">
                    <TableCell
                      colSpan={3}
                      className="py-1 text-xs font-medium uppercase tracking-wide text-muted-foreground"
                    >
                      {sheet || "rows"}
                    </TableCell>
                  </TableRow>,
                ]
              : []),
            ...visible.map((r) => {
            const rowKey = `${sheet}-${r.row}`;
            const hasDiff = r.diff && Object.keys(r.diff).length > 0;
            const isOpen = open.has(rowKey);
            return (
              <Fragment key={rowKey}>
                <TableRow
                  className={hasDiff ? "cursor-pointer" : undefined}
                  onClick={() => {
                    if (!hasDiff) return;
                    const next = new Set(open);
                    if (isOpen) next.delete(rowKey);
                    else next.add(rowKey);
                    setOpen(next);
                  }}
                >
                  <TableCell className="font-mono text-muted-foreground">
                    <span className="inline-flex items-center gap-1">
                      {hasDiff && (
                        <ChevronRight
                          className={cn(
                            "h-3 w-3 transition-transform",
                            isOpen && "rotate-90"
                          )}
                        />
                      )}
                      {r.row}
                    </span>
                  </TableCell>
                  <TableCell className={ACTION_STYLE[r.action] ?? ""}>
                    {r.action}
                  </TableCell>
                  <TableCell dir="auto" className="text-muted-foreground">
                    {r.detail}
                  </TableCell>
                </TableRow>
                {hasDiff && isOpen && (
                  <TableRow>
                    <TableCell />
                    <TableCell colSpan={2}>
                      <div className="space-y-0.5 py-1 font-mono text-xs">
                        {Object.entries(r.diff!).map(([f, [o, n]]) => (
                          <div key={f}>
                            <span className="text-muted-foreground">{f}:</span>{" "}
                            <span className="text-rose-400 line-through">
                              {fmt(o)}
                            </span>{" "}
                            →{" "}
                            <span className="text-emerald-400">{fmt(n)}</span>
                          </div>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </Fragment>
            );
            }),
              ];
            });
          })()}
          {rows.length === 0 && (
            <TableRow>
              <TableCell
                colSpan={3}
                className="py-8 text-center text-muted-foreground"
              >
                No rows reported.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      {rows.length > ROW_CAP && (
        <p className="border-t px-3 py-2 text-xs text-muted-foreground">
          Showing first {ROW_CAP} of {rows.length} rows.
        </p>
      )}
    </div>
  );
}

export function SmartImportDialog({
  open,
  onOpenChange,
  endpoint,
  fields,
  title = "Import",
  description = "Upload a CSV or XLSX file — headers are auto-mapped, then a dry-run preview shows every row's action before anything is written.",
  options = [],
  extraParams,
  onCommitted,
}: SmartImportDialogProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [columns, setColumns] = useState<ColumnMap[]>([]);
  const [unmapped, setUnmapped] = useState<string[]>([]);
  const [sheetsFound, setSheetsFound] = useState<DetectResp["sheets"]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [result, setResult] = useState<ImportResp | null>(null);
  const [committed, setCommitted] = useState(false);
  const [busy, setBusy] = useState(false);
  const [optValues, setOptValues] = useState<Record<string, string | boolean>>(
    () =>
      Object.fromEntries(
        options.map((o) => [
          o.param,
          o.kind === "select" ? o.defaultValue : (o.defaultValue ?? false),
        ])
      )
  );

  const queryFor = (
    opts: Record<string, string | boolean>,
    extra: Record<string, string>
  ) => {
    const p = new URLSearchParams({ ...extraParams, ...extra });
    for (const o of options) {
      const v = opts[o.param];
      p.set(o.param, o.kind === "flag" ? (v ? "1" : "0") : String(v));
    }
    const overrides = Object.fromEntries(
      columns.filter((c) => c.field).map((c) => [c.header, c.field!])
    );
    p.set("mapping", JSON.stringify(overrides));
    return p.toString();
  };

  const post = async (extra: Record<string, string>) => {
    if (!file) throw new Error("no file");
    return api.upload<ImportResp>(
      `${endpoint}?${queryFor(optValues, { filename: file.name, ...extra })}`,
      file,
      "application/octet-stream"
    );
  };

  const pick = async (f: File) => {
    setBusy(true);
    setFile(f);
    setResult(null);
    setCommitted(false);
    try {
      const r = await api.upload<DetectResp>(
        `${endpoint}?${queryFor(optValues, {
          filename: f.name,
          detect: "1",
        })}`,
        f,
        "application/octet-stream"
      );
      setColumns(r.columns);
      setUnmapped(r.unmapped);
      setSheetsFound(r.sheets ?? []);
      setWarnings(r.warnings ?? []);
    } catch (e) {
      toast.error("Could not read file", { description: String(e) });
      setFile(null);
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const preview = () => previewWith(optValues);

  const commit = async () => {
    setBusy(true);
    try {
      const r = await post({ dry_run: "0" });
      setResult(r);
      setCommitted(r.committed);
      if (r.committed) {
        toast.success("Import committed", {
          description: `${r.counts.create ?? 0} created, ${r.counts.update ?? 0} updated, ${r.counts.skip ?? 0} skipped`,
        });
        onCommitted?.();
      } else {
        toast.warning("Commit refused", {
          description: `${r.counts.error ?? 0} error row(s) — fix the file or enable force to commit the valid rows`,
        });
      }
    } catch (e) {
      toast.error("Commit failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  // An option flip invalidates a shown preview — re-run it so the counts
  // and rows on screen always match the selected mode.
  const setOpt = (param: string, v: string | boolean) => {
    const next = { ...optValues, [param]: v };
    setOptValues(next);
    if (result) void previewWith(next);
  };

  const previewWith = async (opts: Record<string, string | boolean>) => {
    if (!file) return;
    setBusy(true);
    try {
      const r = await api.upload<ImportResp>(
        `${endpoint}?${queryFor(opts, { filename: file.name, dry_run: "1" })}`,
        file,
        "application/octet-stream"
      );
      setResult(r);
      if (r.warnings?.length) setWarnings(r.warnings);
      setCommitted(false);
    } catch (e) {
      toast.error("Preview failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const reset = () => {
    setFile(null);
    setColumns([]);
    setUnmapped([]);
    setSheetsFound([]);
    setWarnings([]);
    setResult(null);
    setCommitted(false);
  };

  const errorCount = result?.counts?.error ?? 0;
  // Live unmapped set — remapping a header clears its flag immediately.
  const unmappedNow = columns.filter(
    (c) => c.field === null && unmapped.includes(c.header)
  );
  const hasUnmapped = unmappedNow.length > 0;

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) reset();
        onOpenChange(v);
      }}
    >
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>

        <input
          ref={fileRef}
          type="file"
          accept=".csv,.xlsx"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) void pick(f);
          }}
        />

        {!file ? (
          <button
            onClick={() => fileRef.current?.click()}
            disabled={busy}
            className="flex flex-col items-center gap-2 rounded-lg border border-dashed bg-card p-8 text-center hover:bg-accent/40"
          >
            {busy ? (
              <Loader2 className="h-7 w-7 animate-spin text-emerald-400" />
            ) : (
              <FileSpreadsheet className="h-7 w-7 text-emerald-400" />
            )}
            <span className="font-medium">Choose a .csv or .xlsx file</span>
            <span className="text-sm text-muted-foreground">
              CSV or multi-sheet XLSX; export files from this app re-import
              cleanly.
            </span>
          </button>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm">
              <FileSpreadsheet className="h-4 w-4 text-emerald-400" />
              <span dir="auto" className="font-medium">
                {file.name}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => fileRef.current?.click()}
              >
                <Upload className="h-3.5 w-3.5" /> Change file
              </Button>
            </div>

            {sheetsFound && sheetsFound.length > 1 && (
              <p className="text-xs text-muted-foreground">
                Sheets:{" "}
                {sheetsFound
                  .map((s) =>
                    s.family
                      ? `${s.name} (${s.row_count})`
                      : `${s.name} — ignored`
                  )
                  .join(" · ")}
              </p>
            )}
            {warnings.length > 0 && (
              <div className="space-y-1">
                {warnings.map((w) => (
                  <p
                    key={w}
                    className="flex items-center gap-1.5 text-xs text-amber-400"
                  >
                    <AlertTriangle className="h-3 w-3" />
                    {w}
                  </p>
                ))}
              </div>
            )}

            {columns.length > 0 && (
              <div className="space-y-1.5">
                <div className="flex items-center gap-2 text-sm font-medium">
                  Column mapping
                  {hasUnmapped && (
                    <Badge
                      variant="outline"
                      className="gap-1 border-amber-500/40 text-amber-400"
                    >
                      <AlertTriangle className="h-3 w-3" />
                      {unmappedNow.length} unmapped
                    </Badge>
                  )}
                </div>
                <div className="max-h-48 overflow-auto rounded-lg border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>File header</TableHead>
                        <TableHead className="w-56">Imports as</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {columns.map((c) => (
                        <TableRow key={c.header}>
                          <TableCell dir="auto" className="font-medium">
                            {c.header}
                          </TableCell>
                          <TableCell>
                            <Select
                              value={c.field ?? UNMAPPED}
                              onValueChange={(v) =>
                                setColumns((cur) =>
                                  cur.map((x) =>
                                    x.header === c.header
                                      ? { ...x, field: v === UNMAPPED ? null : v }
                                      : x
                                  )
                                )
                              }
                            >
                              <SelectTrigger
                                className={cn(
                                  "h-8",
                                  c.field === null &&
                                    unmapped.includes(c.header) &&
                                    "border-amber-500/50 text-amber-400"
                                )}
                              >
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value={UNMAPPED}>
                                  <span className="text-muted-foreground">
                                    (skip column)
                                  </span>
                                </SelectItem>
                                {fields.map((f) => (
                                  <SelectItem key={f.value} value={f.value}>
                                    {f.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>
            )}

            {options.length > 0 && (
              <div className="flex flex-wrap items-center gap-4">
                {options.map((o) =>
                  o.kind === "select" ? (
                    <div key={o.param} className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">
                        {o.label}
                      </span>
                      <Select
                        value={String(optValues[o.param])}
                        onValueChange={(v) => setOpt(o.param, v)}
                      >
                        <SelectTrigger className="h-8 w-44">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {o.choices.map((c) => (
                            <SelectItem key={c.value} value={c.value}>
                              {c.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  ) : (
                    <label
                      key={o.param}
                      className="flex items-center gap-2 text-sm"
                    >
                      <Checkbox
                        aria-label={o.label}
                        checked={Boolean(optValues[o.param])}
                        onCheckedChange={(v) => setOpt(o.param, v === true)}
                      />
                      {o.label}
                    </label>
                  )
                )}
              </div>
            )}

            {result && (
              <div className="space-y-2">
                <CountCards counts={result.counts} />
                {errorCount > 0 && !committed && (
                  <p className="flex items-center gap-1.5 text-sm text-amber-400">
                    <AlertTriangle className="h-4 w-4" />
                    {errorCount} error row(s) block the commit — fix them or
                    enable force to import the valid rows only.
                  </p>
                )}
                <ResultRows rows={result.rows} />
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            {committed ? "Close" : "Cancel"}
          </Button>
          {file && !committed && (
            <>
              <Button
                variant="outline"
                disabled={busy || columns.length === 0}
                onClick={preview}
              >
                {busy ? (
                  <Loader2 className="animate-spin" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                Run preview
              </Button>
              <Button
                disabled={busy || !result || (errorCount > 0 && !optValues.force)}
                onClick={commit}
              >
                Commit import
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
