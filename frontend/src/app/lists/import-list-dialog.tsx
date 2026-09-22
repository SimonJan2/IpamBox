"use client";

import { useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { FileSpreadsheet, Loader2, Upload } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type {
  CustomList,
  ImportBatch,
  Page,
  SheetPreview,
} from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type Step = "file" | "sheet" | "preview" | "done";

interface UploadResp {
  batch: ImportBatch;
  sheets: SheetPreview[];
}
interface PreviewResp {
  sheets: SheetPreview[];
  counts: Record<string, number>;
  rows: { sheet: string; row: number; action: string; detail: string }[];
}

const IPAM_FAMILIES = new Set(["site_sheet", "servers"]);

/** Upload → pick a sheet → name/key → dry-run → commit. Turns one sheet
 *  (or one CSV) into a custom list by reusing the workbook pipeline:
 *  the chosen sheet is targeted as a list and every other sheet is skipped. */
export function ImportListDialog({
  open,
  onOpenChange,
  onImported,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  onImported: () => void;
}) {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [step, setStep] = useState<Step>("file");
  const [busy, setBusy] = useState(false);
  const [batch, setBatch] = useState<ImportBatch | null>(null);
  const [sheets, setSheets] = useState<SheetPreview[]>([]);
  const [picked, setPicked] = useState<SheetPreview | null>(null);
  const [name, setName] = useState("");
  const [keyColumn, setKeyColumn] = useState("");
  const [alsoIpam, setAlsoIpam] = useState(false);
  const [preview, setPreview] = useState<PreviewResp | null>(null);
  const [doneSlug, setDoneSlug] = useState<string | null>(null);
  const [doneName, setDoneName] = useState("");

  const usable = useMemo(
    () => sheets.filter((s) => s.family !== "empty"),
    [sheets]
  );

  const reset = () => {
    setStep("file");
    setBatch(null);
    setSheets([]);
    setPicked(null);
    setName("");
    setKeyColumn("");
    setAlsoIpam(false);
    setPreview(null);
    setDoneSlug(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  const upload = async (file: File) => {
    setBusy(true);
    try {
      const r = await api.upload<UploadResp>(
        `/api/v1/imports/workbook?filename=${encodeURIComponent(file.name)}`,
        file,
        "application/octet-stream"
      );
      setBatch(r.batch);
      const ok = r.sheets.filter((s) => s.family !== "empty");
      setSheets(r.sheets);
      if (ok.length === 1) pick(ok[0]);
      setStep("sheet");
    } catch (e) {
      toast.error("Upload failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const pick = (s: SheetPreview) => {
    setPicked(s);
    setName(s.sheet);
    setKeyColumn("");
    // IP-bearing families still feed the IPAM by default (same rule as the
    // main wizard); everything else is list-only.
    setAlsoIpam(IPAM_FAMILIES.has(s.family));
  };

  const runPreview = async () => {
    if (!batch || !picked) return;
    setBusy(true);
    try {
      const r = await api.post<PreviewResp>(
        `/api/v1/imports/${batch.id}/preview`,
        {
          skip_sheets: sheets
            .map((s) => s.sheet)
            .filter((n) => n !== picked.sheet),
          list_sheets: {
            [picked.sheet]: {
              name: name.trim() || null,
              key_column: keyColumn || null,
              also_ipam: alsoIpam,
            },
          },
        }
      );
      setPreview(r);
      setStep("preview");
    } catch (e) {
      toast.error("Preview failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const commit = async () => {
    if (!batch) return;
    setBusy(true);
    try {
      const r = await api.post<{ counts: Record<string, number> }>(
        `/api/v1/imports/${batch.id}/commit`,
        {}
      );
      // the committed list carries this batch's id — reliable lookup even
      // when the slug got deduplicated
      const lists = await api
        .get<Page<CustomList>>("/api/v1/lists")
        .then((p) => p.items);
      const created = lists.find((l) => l.import_batch_id === batch.id);
      setDoneSlug(created?.slug ?? null);
      setDoneName(created?.name ?? name);
      setStep("done");
      onImported();
      toast.success("List imported", {
        description: `${r.counts.create ?? 0} rows created`,
      });
    } catch (e) {
      toast.error("Commit failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const previewSheet = preview?.sheets.find(
    (s) => s.sheet === picked?.sheet
  );
  const previewRows = (preview?.rows ?? []).filter(
    (r) => r.sheet === picked?.sheet
  );

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        if (!o) reset();
        onOpenChange(o);
      }}
    >
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Import a file as a list</DialogTitle>
        </DialogHeader>

        {step === "file" && (
          <div className="grid gap-3">
            <button
              type="button"
              disabled={busy}
              onClick={() => fileRef.current?.click()}
              className={cn(
                "flex flex-col items-center gap-2 rounded-lg border border-dashed",
                "px-6 py-10 text-muted-foreground transition-colors",
                "hover:border-emerald-500/50 hover:text-foreground"
              )}
            >
              {busy ? (
                <Loader2 className="h-8 w-8 animate-spin" />
              ) : (
                <FileSpreadsheet className="h-8 w-8" />
              )}
              <span className="font-medium">
                {busy ? "Reading file…" : "Choose an .xlsx or .csv file"}
              </span>
              <span className="text-xs">
                xlsx workbooks let you pick a sheet next; a csv imports as one
                sheet.
              </span>
            </button>
            <input
              ref={fileRef}
              type="file"
              accept=".xlsx,.csv"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void upload(f);
              }}
            />
          </div>
        )}

        {step === "sheet" && (
          <div className="grid gap-3">
            <div className="grid max-h-64 gap-1 overflow-auto rounded-md border p-1">
              {usable.map((s) => (
                <button
                  key={s.sheet}
                  type="button"
                  onClick={() => pick(s)}
                  className={cn(
                    "flex items-center gap-2 rounded-md px-3 py-2 text-left",
                    "transition-colors hover:bg-accent/60",
                    picked?.sheet === s.sheet && "bg-accent"
                  )}
                >
                  <span dir="auto" className="min-w-0 flex-1 truncate font-medium">
                    {s.sheet}
                  </span>
                  <Badge variant="outline">{s.family}</Badge>
                  <span className="text-xs text-muted-foreground">
                    {s.rows} rows
                  </span>
                </button>
              ))}
              {usable.length === 0 && (
                <p className="px-3 py-6 text-center text-sm text-muted-foreground">
                  No readable sheets in this file.
                </p>
              )}
            </div>

            {picked && (
              <div className="grid gap-3 rounded-md border p-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="grid gap-1.5">
                    <Label htmlFor="il-name">List name</Label>
                    <Input
                      id="il-name"
                      dir="auto"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>
                  <div className="grid gap-1.5">
                    <Label htmlFor="il-key">Merge key column</Label>
                    <Select
                      value={keyColumn || "__auto__"}
                      onValueChange={(v) =>
                        setKeyColumn(v === "__auto__" ? "" : v)
                      }
                    >
                      <SelectTrigger id="il-key">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="__auto__">
                          Auto (first text column)
                        </SelectItem>
                        {picked.headers.map((h) => (
                          <SelectItem key={h} value={h}>
                            <span dir="auto">{h}</span>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                {IPAM_FAMILIES.has(picked.family) && (
                  <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                    <Checkbox
                      checked={alsoIpam}
                      aria-labelledby="il-also"
                      onCheckedChange={(v) => setAlsoIpam(v === true)}
                    />
                    <span id="il-also">
                      Also import to {picked.family.replace("_", " ")} (IPs land
                      in the address table)
                    </span>
                  </div>
                )}
                <p className="text-xs text-muted-foreground">
                  Re-importing the same sheet later merges on the key column —
                  your pins, colors and hand edits survive.
                </p>
              </div>
            )}
          </div>
        )}

        {step === "preview" && preview && (
          <div className="grid gap-3">
            <div className="flex flex-wrap gap-2 text-sm">
              {["create", "update", "skip", "conflict", "error"]
                .filter((k) => (preview.counts[k] ?? 0) > 0)
                .map((k) => (
                  <Badge key={k} variant="outline">
                    {preview.counts[k]} {k}
                  </Badge>
                ))}
            </div>
            {(previewSheet?.list_columns?.length ?? 0) > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 rounded-md border p-2">
                <span className="text-xs text-muted-foreground">Columns:</span>
                {(previewSheet?.list_columns ?? []).map((c) => (
                  <Badge key={c.key} variant="outline" className="gap-1 font-normal">
                    <span dir="auto">{c.label}</span>
                    <span className="text-[10px] uppercase text-muted-foreground">
                      {c.type}
                      {c.multi ? "×n" : ""}
                    </span>
                  </Badge>
                ))}
              </div>
            )}
            <div className="max-h-56 overflow-auto rounded-md border">
              <table className="w-full text-xs">
                <tbody>
                  {previewRows.slice(0, 100).map((r, i) => (
                    <tr key={i} className="border-b last:border-0">
                      <td className="w-16 px-2 py-1 text-muted-foreground">
                        {r.action}
                      </td>
                      <td dir="auto" className="px-2 py-1">
                        {r.detail}
                      </td>
                    </tr>
                  ))}
                  {previewRows.length === 0 && (
                    <tr>
                      <td className="px-3 py-6 text-center text-muted-foreground">
                        No rows — the sheet is empty.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {step === "done" && (
          <div className="grid gap-2 py-4 text-center">
            <p className="font-medium">
              <span dir="auto">{doneName}</span> imported.
            </p>
            <p className="text-sm text-muted-foreground">
              The batch is listed under Import history — re-import the same
              sheet any time to merge updates.
            </p>
          </div>
        )}

        <DialogFooter>
          {step === "sheet" && (
            <>
              <Button variant="ghost" onClick={() => setStep("file")}>
                Back
              </Button>
              <Button
                onClick={runPreview}
                disabled={busy || !picked || !name.trim()}
              >
                {busy ? "Running…" : "Preview"}
              </Button>
            </>
          )}
          {step === "preview" && (
            <>
              <Button variant="ghost" onClick={() => setStep("sheet")}>
                Back
              </Button>
              <Button onClick={commit} disabled={busy}>
                {busy ? "Importing…" : "Import list"}
              </Button>
            </>
          )}
          {step === "done" && (
            <>
              <Button variant="ghost" onClick={() => onOpenChange(false)}>
                Close
              </Button>
              {doneSlug && (
                <Button
                  onClick={() => {
                    onOpenChange(false);
                    router.push(`/lists/${doneSlug}`);
                  }}
                >
                  <Upload className="rotate-180" /> Open list
                </Button>
              )}
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
