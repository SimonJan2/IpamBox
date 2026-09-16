"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  FileSpreadsheet,
  Loader2,
  Play,
  Trash2,
  Upload,
  XCircle,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import type { ImportBatch, RowResult, SheetPreview, Site } from "@/types";
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
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Sheet</TableHead>
              <TableHead className="w-16">Row</TableHead>
              <TableHead className="w-24">Action</TableHead>
              <TableHead>Detail</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.slice(0, 500).map((r, i) => (
              <TableRow key={i}>
                <TableCell dir="auto" className="font-medium">
                  {r.sheet}
                </TableCell>
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
            {filtered.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={4}
                  className="py-8 text-center text-muted-foreground"
                >
                  No rows in this category.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      {filtered.length > 500 && (
        <p className="text-xs text-muted-foreground">
          Showing first 500 of {filtered.length}.
        </p>
      )}
    </div>
  );
}

export default function ImportPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const fileRef = useRef<HTMLInputElement>(null);

  const [batches, setBatches] = useState<ImportBatch[]>([]);
  const [batch, setBatch] = useState<ImportBatch | null>(null);
  const [sheets, setSheets] = useState<SheetPreview[]>([]);
  const [skipped, setSkipped] = useState<Set<string>>(new Set());
  const [overrides, setOverrides] = useState<Record<string, number>>({});
  const [sites, setSites] = useState<Site[]>([]);
  const [preview, setPreview] = useState<PreviewResp | null>(null);
  const [commitResult, setCommitResult] = useState<CommitResp | null>(null);
  const [busy, setBusy] = useState(false);

  const refreshHistory = () => {
    api.get<ImportBatch[]>("/api/v1/imports").then(setBatches).catch(() => {});
  };
  useEffect(() => {
    refreshHistory();
    api.get<Site[]>("/api/v1/sites").then(setSites).catch(() => {});
  }, []);

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
      if (batch?.id === id) {
        setBatch(null);
        setSheets([]);
        setPreview(null);
      }
      refreshHistory();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const errorCount = preview?.counts?.error ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Import workbook</h1>
        {canWrite && (
          <div>
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
            <Button
              size="sm"
              disabled={busy}
              onClick={() => fileRef.current?.click()}
            >
              {busy ? (
                <Loader2 className="animate-spin" />
              ) : (
                <Upload />
              )}
              Upload .xlsx
            </Button>
          </div>
        )}
      </div>

      {batch && (
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
                              setOverrides({ ...overrides, [s.sheet]: +v })
                            }
                          >
                            <SelectTrigger className="h-8 w-48">
                              <SelectValue placeholder="auto" />
                            </SelectTrigger>
                            <SelectContent>
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

      {preview && (
        <div className="space-y-3 rounded-lg border bg-card p-4">
          <h2 className="font-semibold">Dry-run preview</h2>
          <CountCards counts={preview.counts} />
          <RowsTable rows={preview.rows} />
          <div className="flex items-center gap-2 pt-1">
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

      {commitResult && (
        <div className="space-y-3 rounded-lg border border-emerald-500/30 bg-card p-4">
          <h2 className="flex items-center gap-2 font-semibold text-emerald-400">
            <CheckCircle2 className="h-4 w-4" /> Import committed
          </h2>
          <CountCards counts={commitResult.counts} />
          <RowsTable rows={commitResult.rows} />
        </div>
      )}

      <div className="space-y-3">
        <h2 className="font-semibold">Import history</h2>
        <div className="rounded-lg border">
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
                      {new Date(b.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {b.committed_at
                        ? new Date(b.committed_at).toLocaleString()
                        : "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      {canWrite && b.status !== "committed" && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => remove(b.id)}
                        >
                          <Trash2 className="h-4 w-4 text-rose-400" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
              {batches.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={6}
                    className="py-10 text-center text-muted-foreground"
                  >
                    No imports yet — upload a Network_Address.xlsx workbook.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
