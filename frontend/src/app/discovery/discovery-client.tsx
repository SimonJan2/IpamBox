"use client";

import { useEffect, useState } from "react";
import { Check, Loader2, ShieldCheck, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useAsyncData } from "@/lib/use-async-data";
import { PERM } from "@/lib/permissions";
import { timeAgo } from "@/lib/utils";
import type { IpAddress, Prefix } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { ConfirmDialog } from "@/components/confirm-action";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type BulkResp = { affected: number; not_found: number[] };

export default function DiscoveryPage() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const itemsQ = useAsyncData(() => api.get<IpAddress[]>("/api/v1/discovery"));
  const prefixesQ = useAsyncData(async () => {
    const ps = await api.get<Prefix[]>("/api/v1/prefixes");
    return Object.fromEntries(ps.map((p) => [p.id, p.prefix]));
  });
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [pending, setPending] = useState<Set<number>>(new Set());
  const [bulkBusy, setBulkBusy] = useState(false);
  const [confirmDel, setConfirmDel] = useState<
    { kind: "one"; id: number } | { kind: "bulk" } | null
  >(null);

  const items = itemsQ.data ?? [];
  const prefixes = prefixesQ.data ?? {};

  useEffect(() => {
    const onEv = () => {
      void itemsQ.reload();
      void prefixesQ.reload();
    };
    window.addEventListener("ipam:refresh", onEv);
    return () => window.removeEventListener("ipam:refresh", onEv);
  }, [itemsQ.reload, prefixesQ.reload]);

  const dropSelected = (id: number) =>
    setSelected((s) => {
      if (!s.has(id)) return s;
      const n = new Set(s);
      n.delete(id);
      return n;
    });

  const act = async (id: number, status: "active" | "reserved") => {
    if (pending.has(id)) return;
    const prev = items;
    setPending((p) => new Set(p).add(id));
    itemsQ.setData((cur) => (cur ?? []).filter((a) => a.id !== id));
    try {
      await api.post(`/api/v1/discovery/${id}/confirm`, { status });
      toast.success(status === "active" ? "Marked active" : "Marked reserved");
      dropSelected(id);
    } catch (e) {
      itemsQ.setData(prev);
      toast.error("Failed", { description: String(e) });
    } finally {
      setPending((p) => {
        const n = new Set(p);
        n.delete(id);
        return n;
      });
    }
  };

  const removeOne = async (id: number) => {
    const prev = items;
    itemsQ.setData((cur) => (cur ?? []).filter((a) => a.id !== id));
    try {
      await api.del(`/api/v1/addresses/${id}`);
      toast.success("Removed");
      dropSelected(id);
    } catch (e) {
      itemsQ.setData(prev);
      throw e; // ConfirmDialog keeps the dialog open and toasts
    }
  };

  const markAllActive = async () => {
    if (bulkBusy) return;
    const ids = [...selected];
    const prev = items;
    setBulkBusy(true);
    itemsQ.setData((cur) => (cur ?? []).filter((a) => !selected.has(a.id)));
    try {
      const r = await api.post<BulkResp>("/api/v1/addresses/bulk", {
        ids,
        action: "set_status",
        status: "active",
      });
      toast.success(`${r.affected} of ${ids.length} updated`, {
        description: r.not_found.length
          ? `${r.not_found.length} not found (already gone)`
          : undefined,
      });
      setSelected(new Set());
    } catch (e) {
      itemsQ.setData(prev);
      toast.error("Bulk update failed", { description: String(e) });
    } finally {
      setBulkBusy(false);
    }
  };

  const bulkDelete = async () => {
    const ids = [...selected];
    const prev = items;
    itemsQ.setData((cur) => (cur ?? []).filter((a) => !selected.has(a.id)));
    try {
      const r = await api.post<BulkResp>("/api/v1/addresses/bulk", {
        ids,
        action: "delete",
      });
      toast.success(`${r.affected} of ${ids.length} deleted`, {
        description: r.not_found.length
          ? `${r.not_found.length} not found (already gone)`
          : undefined,
      });
      setSelected(new Set());
    } catch (e) {
      itemsQ.setData(prev);
      throw e; // ConfirmDialog keeps the dialog open and toasts
    }
  };

  const allChecked = items.length > 0 && selected.size === items.length;
  const delTarget =
    confirmDel?.kind === "one"
      ? items.find((a) => a.id === confirmDel.id)
      : null;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Discovery inbox</h1>
      <p className="text-sm text-muted-foreground">
        Hosts found by scanners that haven&apos;t been confirmed yet.
      </p>

      {selected.size > 0 && (
        <div className="sticky top-4 z-10 flex w-fit items-center gap-3 rounded-lg border bg-card px-4 py-2 shadow-lg">
          <span role="status" className="text-sm text-muted-foreground">
            {selected.size} selected
          </span>
          {canWrite && (
            <Button
              size="sm"
              variant="outline"
              disabled={bulkBusy}
              onClick={markAllActive}
            >
              {bulkBusy ? <Loader2 className="animate-spin" /> : <Check />} Mark
              all active
            </Button>
          )}
          {canDelete && (
            <Button
              size="sm"
              variant="destructive"
              disabled={bulkBusy}
              onClick={() => setConfirmDel({ kind: "bulk" })}
            >
              <Trash2 /> Delete
            </Button>
          )}
          <Button size="sm" variant="ghost" onClick={() => setSelected(new Set())}>
            Clear
          </Button>
        </div>
      )}

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">{items.length} pending</CardTitle>
        </CardHeader>
        <CardContent>
          <AsyncPanel
            loading={itemsQ.loading}
            error={itemsQ.error}
            onRetry={itemsQ.reload}
            empty={items.length === 0}
            emptyMessage="Inbox zero — nothing pending review."
          >
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-8">
                  <Checkbox
                    checked={allChecked}
                    aria-label="Select all rows"
                    onCheckedChange={(on) =>
                      setSelected(on ? new Set(items.map((a) => a.id)) : new Set())
                    }
                  />
                </TableHead>
                <TableHead>Address</TableHead>
                <TableHead>Prefix</TableHead>
                <TableHead>Hostname</TableHead>
                <TableHead>MAC</TableHead>
                <TableHead>Vendor</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Ports</TableHead>
                <TableHead>Last seen</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((a) => (
                <TableRow key={a.id}>
                  <TableCell>
                    <Checkbox
                      checked={selected.has(a.id)}
                      disabled={pending.has(a.id)}
                      aria-label={`Select ${a.address}`}
                      onCheckedChange={(on) => {
                        const next = new Set(selected);
                        if (on) next.add(a.id);
                        else next.delete(a.id);
                        setSelected(next);
                      }}
                    />
                  </TableCell>
                  <TableCell className="font-mono">{a.address}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {prefixes[a.prefix_id] ?? a.prefix_id}
                  </TableCell>
                  <TableCell>{a.hostname ?? "—"}</TableCell>
                  <TableCell className="font-mono text-xs">{a.mac_address ?? "—"}</TableCell>
                  <TableCell className="text-muted-foreground">{a.vendor ?? "—"}</TableCell>
                  <TableCell>
                    {a.device_type ? (
                      <Badge variant="secondary" className="capitalize">
                        {a.device_type}
                      </Badge>
                    ) : (
                      "—"
                    )}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {a.open_ports?.length ? a.open_ports.join(" ") : "—"}
                  </TableCell>
                  <TableCell className="text-muted-foreground">{timeAgo(a.last_seen)}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      {pending.has(a.id) ? (
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      ) : (
                        <>
                          {canWrite && (
                            <>
                              <Button
                                size="sm"
                                variant="ghost"
                                disabled={bulkBusy}
                                onClick={() => act(a.id, "active")}
                              >
                                <Check className="text-emerald-400" /> Active
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                disabled={bulkBusy}
                                onClick={() => act(a.id, "reserved")}
                              >
                                <ShieldCheck className="text-amber-400" /> Reserve
                              </Button>
                            </>
                          )}
                          {canDelete && (
                            <Button
                              size="sm"
                              variant="ghost"
                              aria-label={`Delete ${a.address}`}
                              disabled={bulkBusy}
                              onClick={() =>
                                setConfirmDel({ kind: "one", id: a.id })
                              }
                            >
                              <Trash2 className="text-red-400" />
                            </Button>
                          )}
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          </AsyncPanel>
        </CardContent>
      </Card>

      <ConfirmDialog
        open={confirmDel !== null}
        onOpenChange={(o) => !o && setConfirmDel(null)}
        title={
          confirmDel?.kind === "bulk"
            ? `Delete ${selected.size} discovered hosts`
            : "Delete discovered host"
        }
        description={
          confirmDel?.kind === "bulk" ? (
            <>
              Permanently delete the{" "}
              <b>{selected.size} selected discovered hosts</b>? They will be
              re-discovered on the next scan if they are still live. This cannot
              be undone.
            </>
          ) : (
            <>
              Permanently delete{" "}
              <span className="font-mono text-foreground">
                {delTarget?.address ?? "this host"}
              </span>
              ? It will be re-discovered on the next scan if it is still live.
            </>
          )
        }
        confirmWord="DELETE"
        actionLabel={confirmDel?.kind === "bulk" ? "Delete all" : "Delete"}
        onAction={async () => {
          if (confirmDel?.kind === "bulk") await bulkDelete();
          else if (confirmDel?.kind === "one") await removeOne(confirmDel.id);
        }}
      />
    </div>
  );
}
