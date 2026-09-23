"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Download,
  ExternalLink,
  History,
  Pencil,
  Plus,
  Printer,
  QrCode,
  Trash2,
  Upload,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { useSetting } from "@/lib/features";
import { encodeShareUrl, exportZip } from "@/lib/rackula";
import { cn, timeAgo } from "@/lib/utils";
import type { RackDetail, RackDevice, Site, Page } from "@/types";
import { RackElevation, usedUSlots } from "@/components/racks/rack-elevation";
import { DeviceFormDialog } from "@/components/racks/device-form";
import { RackulaImportDialog } from "@/components/racks/rackula-import";
import { RackQrDialog } from "@/components/racks/rack-qr";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { HistoryDialog } from "@/components/history-panel";
import { IpStatusBadge } from "@/components/status-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const FACE_BADGE: Record<RackDevice["face"], string> = {
  front: "Front",
  rear: "Rear",
  both: "Front+Rear",
};

export default function RackDetailPage({ id }: { id: string }) {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const rackulaBase = useSetting("rackula_base_url");

  const rackQ = useAsyncData(() => api.get<RackDetail>(`/api/v1/racks/${id}`), [id]);
  // "Next free" hint for a 1U front device — refetches with the rack.
  const nextFreeQ = useAsyncData(async () => {
    if (!rackQ.data) return null;
    try {
      return await api
        .get<{ u_position: number | null }>(
          `/api/v1/racks/${id}/next-free-u?height=1&face=front`
        )
        .then((r) => r.u_position);
    } catch {
      return null;
    }
  }, [rackQ.data]);
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Site>>("/api/v1/sites").then((p) => p.items);
    } catch {
      return [];
    }
  });

  const [deviceOpen, setDeviceOpen] = useState(false);
  const [editing, setEditing] = useState<RackDevice | null>(null);
  const [deleting, setDeleting] = useState<RackDevice | null>(null);
  const [historyFor, setHistoryFor] = useState<RackDevice | null>(null);
  const [importOpen, setImportOpen] = useState(false);
  const [qrOpen, setQrOpen] = useState(false);
  const [selected, setSelected] = useState<RackDevice | null>(null);

  const rack = rackQ.data;
  const devices = useMemo(
    () => [...(rack?.devices ?? [])].sort((a, b) => b.u_position - a.u_position),
    [rack]
  );
  const refresh = () => {
    setSelected(null);
    void rackQ.reload();
  };

  const siteName = rack?.site_id
    ? (sitesQ.data ?? []).find((s) => s.id === rack.site_id)?.name
    : null;

  const shareUrl = rack && rackulaBase ? encodeShareUrl(rackulaBase, rack, devices) : null;

  const downloadZip = async () => {
    if (!rack) return;
    try {
      const blob = await exportZip(rack, devices);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `${rack.name}.Rackula.zip`;
      a.click();
      URL.revokeObjectURL(a.href);
    } catch (e) {
      toast.error("Export failed", { description: String(e) });
    }
  };

  const doDeleteDevice = async () => {
    if (!deleting || !rack) return;
    try {
      await api.del(`/api/v1/racks/${rack.id}/devices/${deleting.id}`);
      toast.success("Device removed");
      setDeleting(null);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">
          <Button variant="ghost" size="icon" asChild aria-label="Back to racks">
            <Link href="/racks">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <span dir="auto">{rack?.name ?? "Rack"}</span>
          {rack && (
            <span className="text-sm font-normal text-muted-foreground">
              {rack.height_u}U{siteName ? ` · ${siteName}` : ""}
              {rack.room ? ` · ${rack.room}` : ""}
              {nextFreeQ.data ? ` · next free U${nextFreeQ.data}` : ""}
            </span>
          )}
          <DocsLink slug="racks" />
        </h1>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" size="sm" onClick={() => setQrOpen(true)} disabled={!rack}>
            <QrCode /> QR
          </Button>
          <Button variant="secondary" size="sm" asChild>
            <Link href={`/racks/${id}/print`}>
              <Printer /> Print
            </Link>
          </Button>
          {shareUrl && (
            <Button variant="secondary" size="sm" asChild>
              <a href={shareUrl} target="_blank" rel="noreferrer">
                <ExternalLink /> Open in Rackula
              </a>
            </Button>
          )}
          <Button variant="secondary" size="sm" onClick={downloadZip} disabled={!rack}>
            <Download /> .Rackula.zip
          </Button>
          {canWrite && (
            <Button variant="secondary" size="sm" onClick={() => setImportOpen(true)}>
              <Upload /> Import from Rackula
            </Button>
          )}
          {canWrite && (
            <Button
              size="sm"
              onClick={() => {
                setEditing(null);
                setDeviceOpen(true);
              }}
            >
              <Plus /> Add device
            </Button>
          )}
        </div>
      </div>

      <AsyncPanel
        loading={rackQ.loading}
        error={rackQ.error}
        onRetry={rackQ.reload}
        empty={!rack}
        emptyMessage="Rack not found."
      >
        {rack && (
          <div className="grid gap-4 lg:grid-cols-[auto_1fr]">
            <div className="space-y-3">
              <RackElevation
                name={rack.name}
                heightU={rack.height_u}
                devices={devices}
                selectedId={selected?.id ?? null}
                onSelect={setSelected}
              />
              {selected && (
                <div className="max-w-sm space-y-1.5 rounded-lg border bg-card p-3 text-sm">
                  <div className="flex items-center justify-between gap-2">
                    <span dir="auto" className="font-medium">{selected.name}</span>
                    <Badge variant="outline">{FACE_BADGE[selected.face]}</Badge>
                  </div>
                  <p className="text-muted-foreground" dir="ltr">
                    U{selected.u_position}
                    {selected.u_height > 1
                      ? `–${selected.u_position + selected.u_height - 1}`
                      : ""}{" "}
                    · {selected.u_height}U
                    {selected.device_type ? ` · ${selected.device_type}` : ""}
                  </p>
                  {(selected.manufacturer || selected.model) && (
                    <p dir="auto" className="text-muted-foreground">
                      {[selected.manufacturer, selected.model].filter(Boolean).join(" ")}
                    </p>
                  )}
                  {selected.asset && (
                    <p>
                      Asset:{" "}
                      <Link
                        href={`/inventory?q=${encodeURIComponent(selected.asset.label)}`}
                        className="text-emerald-400 hover:underline"
                        dir="auto"
                      >
                        {selected.asset.label}
                      </Link>
                    </p>
                  )}
                  {selected.ip && (
                    <p className="flex items-center gap-1.5">
                      IP:{" "}
                      <Link
                        href={`/prefixes/${selected.ip.prefix_id}`}
                        className="text-emerald-400 hover:underline"
                        dir="ltr"
                      >
                        {selected.ip.label}
                      </Link>
                      {selected.ip_status && <IpStatusBadge s={selected.ip_status} />}
                    </p>
                  )}
                  {selected.ip_last_seen && (
                    <p className="text-muted-foreground">
                      Last seen {timeAgo(selected.ip_last_seen)}
                    </p>
                  )}
                  {selected.notes && (
                    <p dir="auto" className="text-muted-foreground">{selected.notes}</p>
                  )}
                  <div className="flex gap-1 pt-1">
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setEditing(selected);
                          setDeviceOpen(true);
                        }}
                      >
                        <Pencil className="h-3.5 w-3.5" /> Edit
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setHistoryFor(selected)}
                    >
                      <History className="h-3.5 w-3.5" /> History
                    </Button>
                  </div>
                </div>
              )}
            </div>

            <div className="min-w-0 rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>U</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Face</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Links</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {devices.map((d) => (
                    <TableRow
                      key={d.id}
                      onClick={() => setSelected(d.id === selected?.id ? null : d)}
                      className={cn(
                        "cursor-pointer",
                        d.id === selected?.id && "bg-muted/40"
                      )}
                    >
                      <TableCell dir="ltr" className="whitespace-nowrap">
                        U{d.u_position}
                        {d.u_height > 1 ? `–${d.u_position + d.u_height - 1}` : ""}
                      </TableCell>
                      <TableCell>
                        <span dir="auto" className="font-medium">{d.name}</span>
                        {d.source === "rackula" && (
                          <Badge variant="outline" className="ml-1.5 text-muted-foreground">
                            rackula
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="capitalize text-muted-foreground">
                        {d.face}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {d.device_type ?? "—"}
                      </TableCell>
                      <TableCell>
                        {d.ip_status ? (
                          <IpStatusBadge s={d.ip_status} />
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {[d.asset?.label, d.ip?.label].filter(Boolean).join(" · ") || "—"}
                      </TableCell>
                      <TableCell>
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            aria-label={`History of ${d.name}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              setHistoryFor(d);
                            }}
                          >
                            <History className="h-4 w-4" />
                          </Button>
                          {canWrite && (
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={`Edit ${d.name}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                setEditing(d);
                                setDeviceOpen(true);
                              }}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                          )}
                          {canDelete && (
                            <Button
                              variant="ghost"
                              size="icon"
                              aria-label={`Delete ${d.name}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                setDeleting(d);
                              }}
                            >
                              <Trash2 className="h-4 w-4 text-rose-400" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                  {devices.length === 0 && (
                    <TableRow>
                      <TableCell
                        colSpan={7}
                        className="py-10 text-center text-muted-foreground"
                      >
                        Empty rack — add a device or import a Rackula layout.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </div>
        )}
      </AsyncPanel>

      {rack && (
        <>
          <DeviceFormDialog
            open={deviceOpen}
            onOpenChange={setDeviceOpen}
            rackId={rack.id}
            heightU={rack.height_u}
            editing={editing}
            onSaved={refresh}
          />
          <RackulaImportDialog
            open={importOpen}
            onOpenChange={setImportOpen}
            rackId={rack.id}
            heightU={rack.height_u}
            existing={devices}
            onImported={refresh}
          />
          <RackQrDialog
            open={qrOpen}
            onOpenChange={setQrOpen}
            rackId={rack.id}
            name={rack.name}
          />
        </>
      )}

      <Dialog open={deleting !== null} onOpenChange={() => setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Remove device</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Remove{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.name}
            </span>{" "}
            from U{deleting?.u_position}?
          </p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDeleteDevice}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <HistoryDialog
        open={historyFor !== null}
        onOpenChange={() => setHistoryFor(null)}
        objectType="RackDevice"
        objectId={historyFor?.id ?? null}
        title={historyFor?.name}
      />
    </div>
  );
}
