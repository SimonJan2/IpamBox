"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { DatabaseZap, FileDown, FileUp } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ConfirmAction } from "@/components/confirm-action";

async function download(path: string, name: string) {
  const res = await fetch(path, { credentials: "include" });
  if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export default function DataPage() {
  const router = useRouter();
  const { can } = useAuth();
  const [scanDays, setScanDays] = useState("");
  const [logDays, setLogDays] = useState("");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Data &amp; Maintenance</h1>
        <p className="text-sm text-muted-foreground">
          Import/export helpers and destructive cleanup operations. Every action
          below is recorded in the changelog.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <FileDown className="h-4 w-4" /> Export
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            CSV exports of the core tables. Full database snapshots live under
            Backup &amp; Restore.
          </p>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() =>
                download("/api/v1/addresses/export.csv", "addresses.csv").catch(
                  (e) => toast.error("Export failed", { description: String(e) })
                )
              }
            >
              <FileDown /> Addresses CSV
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() =>
                download("/api/v1/prefixes/export.csv", "prefixes.csv").catch((e) =>
                  toast.error("Export failed", { description: String(e) })
                )
              }
            >
              <FileDown /> Prefixes CSV
            </Button>
          </div>
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <FileUp className="h-3.5 w-3.5" /> Address CSV import lives on the
            prefix detail page (it needs a target prefix).
          </p>
        </CardContent>
      </Card>

      {can(PERM.SYSTEM_ADMIN) && (
      <Card className="border-rose-500/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-rose-400">
            <DatabaseZap className="h-4 w-4" /> Danger zone
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ConfirmAction
            description={
              <>
                Delete finished scan jobs (queued/running jobs are kept). Leave
                the days field empty to delete <b>all</b> history.
              </>
            }
            confirmWord="PURGE"
            actionLabel="Purge scans"
            extra={
              <div className="grid max-w-56 gap-1.5">
                <Label className="text-xs">Only older than (days, optional)</Label>
                <Input
                  type="number"
                  min={1}
                  value={scanDays}
                  onChange={(e) => setScanDays(e.target.value)}
                  placeholder="all"
                />
              </div>
            }
            onAction={async () => {
              const r = await api.post<{ deleted: number }>(
                "/api/v1/maintenance/purge-scans",
                { older_than_days: scanDays ? Number(scanDays) : null }
              );
              toast.success(`Purged ${r.deleted} scan job(s)`);
            }}
          />

          <ConfirmAction
            description={
              <>
                Delete audit-trail entries. Leave the days field empty to delete
                <b> all</b> history.
              </>
            }
            confirmWord="PURGE"
            actionLabel="Purge changelog"
            extra={
              <div className="grid max-w-56 gap-1.5">
                <Label className="text-xs">Only older than (days, optional)</Label>
                <Input
                  type="number"
                  min={1}
                  value={logDays}
                  onChange={(e) => setLogDays(e.target.value)}
                  placeholder="all"
                />
              </div>
            }
            onAction={async () => {
              const r = await api.post<{ deleted: number }>(
                "/api/v1/maintenance/purge-changelog",
                { older_than_days: logDays ? Number(logDays) : null }
              );
              toast.success(`Purged ${r.deleted} changelog entries`);
            }}
          />

          <ConfirmAction
            description={
              <>
                Delete every host still pending in the{" "}
                <b>Discovery Inbox</b> (status <code>discovered</code>).
                Confirmed addresses are untouched.
              </>
            }
            confirmWord="CLEAR"
            actionLabel="Clear inbox"
            onAction={async () => {
              const r = await api.post<{ deleted: number }>(
                "/api/v1/maintenance/clear-discovery"
              );
              toast.success(`Removed ${r.deleted} discovered host(s)`);
            }}
          />

          <ConfirmAction
            description={
              <>
                <b>Factory reset.</b> Wipes every data table — sites, VRFs,
                VLANs, prefixes, addresses, tags, scans, changelog and UI
                settings — back to a clean install. Your login account and
                session survive. Take a backup first.
              </>
            }
            confirmWord="RESET"
            actionLabel="Factory reset"
            onAction={async () => {
              await api.post("/api/v1/maintenance/reset", {
                confirm: "RESET",
              });
              toast.success("IpamBox was reset");
              // Users and sessions survive a reset — refresh data in place.
              window.dispatchEvent(new Event("ipam:refresh"));
              router.push("/");
              router.refresh();
            }}
          />
        </CardContent>
      </Card>
      )}
    </div>
  );
}
