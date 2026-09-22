"use client";

import { useId, useMemo, useRef, useState } from "react";
import { FileArchive, Link2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import {
  decodeShareUrl,
  parseZip,
  previewImport,
  type ParsedImport,
} from "@/lib/rackula";
import { cn } from "@/lib/utils";
import type { RackDevice, RackImportResult } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const STATUS_BADGE = {
  add: "border-emerald-500/40 text-emerald-400",
  conflict: "border-amber-500/40 text-amber-400",
  skipped: "border-muted-foreground/40 text-muted-foreground",
} as const;

export function RackulaImportDialog({
  open,
  onOpenChange,
  rackId,
  heightU,
  existing,
  onImported,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  rackId: number;
  heightU: number;
  existing: RackDevice[];
  onImported: () => void;
}) {
  const [url, setUrl] = useState("");
  const [parsed, setParsed] = useState<ParsedImport | null>(null);
  const [mode, setMode] = useState<"merge" | "replace">("merge");
  const [busy, setBusy] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const uid = useId();

  const reset = (o: boolean) => {
    if (!o) {
      setUrl("");
      setParsed(null);
      setMode("merge");
    }
    onOpenChange(o);
  };

  const preview = useMemo(
    () =>
      parsed
        ? [
            ...previewImport(parsed, existing, heightU, mode),
            ...parsed.skipped.map((s) => ({
              name: s.name ?? "device",
              device_type: null,
              u_position: s.u_position ?? 0,
              u_height: 0,
              face: "front" as const,
              colour: null,
              category: null,
              manufacturer: null,
              model: null,
              notes: null,
              status: "skipped" as const,
              reason: s.reason,
            })),
          ]
        : [],
    [parsed, existing, heightU, mode]
  );

  const parseUrl = () => {
    try {
      setParsed(decodeShareUrl(url));
    } catch (e) {
      toast.error("Couldn't read share link", { description: String(e) });
    }
  };

  const parseFile = async (f: File) => {
    try {
      setParsed(await parseZip(await f.arrayBuffer()));
    } catch (e) {
      toast.error("Couldn't read .Rackula.zip", { description: String(e) });
    }
  };

  const doImport = async () => {
    if (!parsed) return;
    setBusy(true);
    try {
      const res = await api.post<RackImportResult>(
        `/api/v1/racks/${rackId}/devices/import`,
        {
          mode,
          devices: parsed.devices.map((d) => ({ ...d, source: "rackula" })),
        }
      );
      toast.success(
        `Imported ${res.created} device${res.created === 1 ? "" : "s"}` +
          (res.skipped.length ? `, skipped ${res.skipped.length}` : "")
      );
      reset(false);
      onImported();
    } catch (e) {
      toast.error("Import failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={reset}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Import from Rackula</DialogTitle>
        </DialogHeader>

        <div className="flex flex-wrap items-end gap-2">
          <div className="grid min-w-64 flex-1 gap-1.5">
            <Label htmlFor={`${uid}-url`}>Share URL</Label>
            <div className="flex gap-2">
              <Input
                id={`${uid}-url`}
                dir="ltr"
                placeholder="https://rackula…/?l=…"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <Button variant="secondary" onClick={parseUrl} disabled={!url}>
                <Link2 /> Parse
              </Button>
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label>or .Rackula.zip</Label>
            <input
              ref={fileRef}
              type="file"
              accept=".zip,application/zip"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void parseFile(f);
                e.target.value = "";
              }}
            />
            <Button variant="secondary" onClick={() => fileRef.current?.click()}>
              <FileArchive /> Choose file
            </Button>
          </div>
        </div>

        {parsed && (
          <>
            <div className="space-y-1 text-sm text-muted-foreground">
              {parsed.rack_name && (
                <p dir="auto">
                  Rack “{parsed.rack_name}”
                  {parsed.rack_height ? `, ${parsed.rack_height}U` : ""}
                </p>
              )}
              {parsed.notes.map((n, i) => (
                <p key={i}>{n}</p>
              ))}
            </div>

            <div className="max-h-72 overflow-y-auto rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>U</TableHead>
                    <TableHead>Face</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {preview.map((d, i) => (
                    <TableRow key={i}>
                      <TableCell>
                        <span dir="auto" className="font-medium">{d.name}</span>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {d.device_type ?? "—"}
                      </TableCell>
                      <TableCell dir="ltr">
                        {d.u_position > 0
                          ? `U${d.u_position}${d.u_height > 1 ? `–${d.u_position + d.u_height - 1}` : ""}`
                          : "—"}
                      </TableCell>
                      <TableCell className="capitalize">{d.face}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={cn(STATUS_BADGE[d.status])}>
                          {d.status}
                          {d.reason ? ` — ${d.reason}` : ""}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div role="radiogroup" aria-label="Import mode" className="flex gap-4">
              {(
                [
                  ["merge", "Merge — keep existing, skip conflicts"],
                  ["replace", "Replace — wipe current devices first"],
                ] as const
              ).map(([v, label]) => (
                <label key={v} className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name={`${uid}-mode`}
                    checked={mode === v}
                    onChange={() => setMode(v)}
                  />
                  {label}
                </label>
              ))}
            </div>
          </>
        )}

        <DialogFooter>
          <Button onClick={doImport} disabled={busy || !parsed || parsed.devices.length === 0}>
            {busy ? "Importing…" : "Import"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
