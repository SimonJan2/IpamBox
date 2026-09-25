"use client";

import { useState } from "react";
import Link from "next/link";
import { Activity, Plus } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { timeAgo } from "@/lib/utils";
import type { MonitorTarget, Page } from "@/types";
import { MonitorDialog } from "@/components/monitor-dialog";
import { MonitorStateBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";

/** Attached monitor targets for one device/address — used on the device
 *  detail page and inside the IP drawer. Prefills the dialog's anchor. */
export function MonitorSection({
  deviceId,
  addressId,
  anchorLabel,
}: {
  deviceId?: number;
  addressId?: number;
  anchorLabel: string;
}) {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const [dialogOpen, setDialogOpen] = useState(false);
  const q = useAsyncData(() =>
    api
      .get<Page<MonitorTarget>>(
        `/api/v1/monitor-targets?${deviceId != null ? `device_id=${deviceId}` : `address_id=${addressId}`}`
      )
      .then((p) => p.items)
  );
  const targets = q.data ?? [];

  const checkNow = async (id: number) => {
    try {
      await api.post(`/api/v1/monitor-targets/${id}/check`, {});
      toast.success("Check queued — result inline");
      void q.reload();
    } catch (e) {
      toast.error("Check failed", { description: String(e) });
    }
  };

  return (
    <div className="rounded-lg border bg-card p-3 text-sm">
      <div className="mb-2 flex items-center justify-between">
        <span className="flex items-center gap-1.5 font-medium">
          <Activity className="h-4 w-4" /> Monitor
        </span>
        {canWrite && (
          <Button
            size="sm"
            variant="outline"
            className="h-7"
            onClick={() => setDialogOpen(true)}
          >
            <Plus className="h-3.5 w-3.5" /> Add
          </Button>
        )}
      </div>
      {targets.length === 0 ? (
        <p className="text-muted-foreground">
          No monitors on this target —{" "}
          <Link href="/monitoring" className="text-emerald-400 hover:underline">
            monitoring
          </Link>
          .
        </p>
      ) : (
        <ul className="space-y-1.5">
          {targets.map((t) => (
            <li key={t.id} className="flex items-center gap-2">
              <MonitorStateBadge s={t.state} />
              <span className="font-mono text-xs">
                {t.kind}
                {t.port != null ? `:${t.port}` : ""}
                {t.kind === "http" ? t.http_path : ""}
              </span>
              <span className="min-w-0 flex-1 truncate text-xs text-muted-foreground">
                {t.last_error ??
                  (t.last_checked_at ? timeAgo(t.last_checked_at) : "never")}
              </span>
              {!t.enabled && (
                <span className="text-xs text-muted-foreground">paused</span>
              )}
              {canWrite && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-xs"
                  onClick={() => checkNow(t.id)}
                >
                  check
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}
      <MonitorDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        prefill={{
          device_id: deviceId,
          address_id: addressId,
          label: anchorLabel,
        }}
        onSaved={() => void q.reload()}
      />
    </div>
  );
}
