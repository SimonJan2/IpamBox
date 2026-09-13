"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  Download,
  FileArchive,
  Play,
  RotateCcw,
  Trash2,
  Upload,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { fmtTs } from "@/lib/prefs";
import type {
  BackupFilesOut,
  BackupPreview,
  RestoreReport,
  SettingsOut,
} from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import { SettingField } from "@/components/settings/field";

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

async function downloadUrl(path: string, fallbackName: string) {
  const res = await fetch(path, { credentials: "include" });
  if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
  const blob = await res.blob();
  const cd = res.headers.get("content-disposition") ?? "";
  const name = cd.match(/filename="?([^";]+)"?/)?.[1] ?? fallbackName;
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export default function BackupSettingsPage() {
  const [files, setFiles] = useState<BackupFilesOut | null>(null);
  const [settings, setSettings] = useState<SettingsOut | null>(null);
  const [schedule, setSchedule] = useState({ interval: 0, keep: 14 });
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<BackupPreview | null>(null);
  const [report, setReport] = useState<RestoreReport | null>(null);
  const [confirmText, setConfirmText] = useState("");
  const [busy, setBusy] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  const refreshFiles = useCallback(() => {
    api.get<BackupFilesOut>("/api/v1/backup/files").then(setFiles).catch(() => {});
  }, []);

  useEffect(refreshFiles, [refreshFiles]);

  useEffect(() => {
    api.get<SettingsOut>("/api/v1/settings").then((o) => {
      setSettings(o);
      setSchedule({
        interval: o.values.backup_interval_minutes,
        keep: o.values.backup_keep,
      });
    }).catch(() => {});
  }, []);

  const downloadFresh = async () => {
    try {
      await downloadUrl("/api/v1/backup", "ipambox-backup.json.gz");
      toast.success("Backup downloaded");
    } catch (e) {
      toast.error("Backup failed", { description: String(e) });
    }
  };

  const downloadFile = async (name: string) => {
    try {
      await downloadUrl(`/api/v1/backup/files/${encodeURIComponent(name)}`, name);
    } catch (e) {
      toast.error("Download failed", { description: String(e) });
    }
  };

  const deleteFile = async (name: string) => {
    try {
      await api.del(`/api/v1/backup/files/${encodeURIComponent(name)}`);
      toast.success(`Deleted ${name}`);
      refreshFiles();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const saveSchedule = async () => {
    try {
      const out = await api.patch<SettingsOut>("/api/v1/settings", {
        backup_interval_minutes: schedule.interval,
        backup_keep: schedule.keep,
      });
      setSettings(out);
      setSchedule({
        interval: out.values.backup_interval_minutes,
        keep: out.values.backup_keep,
      });
      refreshFiles();
      toast.success("Backup schedule saved", {
        description: "Applies within ~1 minute.",
      });
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    }
  };

  const runNow = async () => {
    try {
      await api.post("/api/v1/maintenance/backup-now");
      toast.success("Backup queued", {
        description: "The worker will write a snapshot shortly.",
      });
      setTimeout(refreshFiles, 4000);
    } catch (e) {
      toast.error("Could not queue backup", { description: String(e) });
    }
  };

  const pickFile = async (f: File | null) => {
    setFile(f);
    setPreview(null);
    setReport(null);
    setConfirmText("");
    if (!f) return;
    try {
      const p = await api.upload<BackupPreview>(
        `/api/v1/backup/restore?dry_run=1&name=${encodeURIComponent(f.name)}`,
        f
      );
      setPreview(p);
    } catch (e) {
      setFile(null);
      if (fileInput.current) fileInput.current.value = "";
      toast.error("Invalid backup file", { description: String(e) });
    }
  };

  const doRestore = async () => {
    if (!file) return;
    setBusy(true);
    try {
      const r = await api.upload<RestoreReport>(
        `/api/v1/backup/restore?name=${encodeURIComponent(file.name)}`,
        file
      );
      setReport(r);
      toast.success("Restore complete", {
        description: "Reloading to pick up restored data…",
      });
      setTimeout(() => window.location.reload(), 1500);
    } catch (e) {
      toast.error("Restore failed — nothing was changed", {
        description: String(e),
      });
    } finally {
      setBusy(false);
    }
  };

  const scheduleDirty =
    settings &&
    (schedule.interval !== settings.values.backup_interval_minutes ||
      schedule.keep !== settings.values.backup_keep);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Backup &amp; Restore</h1>
        <p className="text-sm text-muted-foreground">
          Snapshot the entire IpamBox database to a single file. The login
          account is never included in backups.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Download className="h-4 w-4" /> Backup
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Download a full snapshot — sites, VRFs, VLANs, prefixes, ranges,
            addresses, tags, settings, changelog and scan history — as a single
            <code className="mx-1">.json.gz</code> file you can restore on this
            or any other IpamBox server.
          </p>
          <div className="flex gap-2">
            <Button size="sm" onClick={downloadFresh}>
              <Download /> Download backup
            </Button>
            <Button size="sm" variant="outline" onClick={runNow}>
              <Play /> Snapshot now
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <FileArchive className="h-4 w-4" /> Scheduled backups
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <SettingField
              label="Interval (minutes)"
              hint="0 = disabled. E.g. 1440 = daily."
              source={settings?.sources.backup_interval_minutes}
              onReset={async () => {
                const out = await api.patch<SettingsOut>("/api/v1/settings", {
                  backup_interval_minutes: null,
                });
                setSettings(out);
                setSchedule((s) => ({
                  ...s,
                  interval: out.values.backup_interval_minutes,
                }));
              }}
            >
              <Input
                type="number"
                min={0}
                max={10080}
                value={schedule.interval}
                onChange={(e) =>
                  setSchedule((s) => ({
                    ...s,
                    interval: Number(e.target.value) || 0,
                  }))
                }
              />
            </SettingField>
            <SettingField
              label="Keep newest N files"
              source={settings?.sources.backup_keep}
              onReset={async () => {
                const out = await api.patch<SettingsOut>("/api/v1/settings", {
                  backup_keep: null,
                });
                setSettings(out);
                setSchedule((s) => ({ ...s, keep: out.values.backup_keep }));
              }}
            >
              <Input
                type="number"
                min={1}
                max={100}
                value={schedule.keep}
                onChange={(e) =>
                  setSchedule((s) => ({
                    ...s,
                    keep: Number(e.target.value) || 1,
                  }))
                }
              />
            </SettingField>
          </div>
          {scheduleDirty && (
            <Button size="sm" onClick={saveSchedule}>
              Save schedule
            </Button>
          )}
          <p className="text-xs text-muted-foreground">
            Files are stored in <code>{settings?.env.backup_dir ?? "/backups"}</code>{" "}
            (the <code>backupdata</code> docker volume) — copy them off the host
            for real disaster recovery.
          </p>
          {files && files.files.length > 0 && (
            <div className="rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>File</TableHead>
                    <TableHead className="w-28">Size</TableHead>
                    <TableHead className="w-48">Created</TableHead>
                    <TableHead className="w-24 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {files.files.map((f) => (
                    <TableRow key={f.name}>
                      <TableCell className="font-mono text-xs">
                        {f.name}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {fmtSize(f.size)}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {fmtTs(f.created_at)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Download"
                          onClick={() => downloadFile(f.name)}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Delete"
                          onClick={() => deleteFile(f.name)}
                        >
                          <Trash2 className="h-4 w-4 text-rose-400" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-rose-500/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-rose-400">
            <RotateCcw className="h-4 w-4" /> Restore
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Replaces <b>all</b> data with the contents of the backup file —
            current sites, VRFs, prefixes, addresses, settings and history are
            wiped. Your login account and session are kept. The operation is
            atomic: if anything fails, nothing changes.
          </p>

          <div className="grid gap-1.5">
            <Label>Backup file</Label>
            <Input
              ref={fileInput}
              type="file"
              accept=".gz,.json,application/gzip,application/json"
              onChange={(e) => pickFile(e.target.files?.[0] ?? null)}
            />
          </div>

          {preview && !report && (
            <div className="space-y-3 rounded-lg border p-4">
              <div className="flex flex-wrap gap-2 text-xs">
                <Badge variant="outline">
                  created {fmtTs(preview.created_at)}
                </Badge>
                {preview.app_version && (
                  <Badge variant="outline">v{preview.app_version}</Badge>
                )}
                {preview.alembic_revision && (
                  <Badge variant="outline">
                    schema {preview.alembic_revision}
                  </Badge>
                )}
              </div>
              <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm sm:grid-cols-3">
                {Object.entries(preview.tables).map(([t, n]) => (
                  <div key={t} className="flex justify-between">
                    <span className="text-muted-foreground">{t}</span>
                    <span className="font-mono">{n}</span>
                  </div>
                ))}
              </div>
              {preview.warnings.length > 0 && (
                <ul className="list-disc pl-5 text-xs text-amber-400">
                  {preview.warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              )}
              <div className="grid gap-1.5">
                <Label>
                  Type <span className="font-mono text-rose-400">RESTORE</span>{" "}
                  to confirm
                </Label>
                <Input
                  value={confirmText}
                  onChange={(e) => setConfirmText(e.target.value)}
                  placeholder="RESTORE"
                  autoComplete="off"
                />
              </div>
              <Button
                variant="destructive"
                size="sm"
                disabled={confirmText !== "RESTORE" || busy}
                onClick={doRestore}
              >
                <Upload /> {busy ? "Restoring…" : "Restore now"}
              </Button>
            </div>
          )}

          {report && (
            <div className="space-y-2 rounded-lg border border-emerald-500/30 p-4">
              <p className="text-sm text-emerald-400">
                Restored backup from {fmtTs(report.backup_created_at)}:
              </p>
              <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm sm:grid-cols-3">
                {Object.entries(report.restored).map(([t, n]) => (
                  <div key={t} className="flex justify-between">
                    <span className="text-muted-foreground">{t}</span>
                    <span className="font-mono">{n}</span>
                  </div>
                ))}
              </div>
              {report.warnings.length > 0 && (
                <ul className="list-disc pl-5 text-xs text-amber-400">
                  {report.warnings.map((w) => (
                    <li key={w}>{w}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
