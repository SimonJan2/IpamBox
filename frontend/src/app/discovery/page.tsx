"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, ShieldCheck, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type { IpAddress, Prefix } from "@/types";
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

export default function DiscoveryPage() {
  const [items, setItems] = useState<IpAddress[]>([]);
  const [prefixes, setPrefixes] = useState<Record<number, string>>({});
  const [selected, setSelected] = useState<Set<number>>(new Set());

  const refresh = useCallback(() => {
    api.get<IpAddress[]>("/api/v1/discovery").then(setItems).catch(() => {});
    api.get<Prefix[]>("/api/v1/prefixes").then((ps) =>
      setPrefixes(Object.fromEntries(ps.map((p) => [p.id, p.prefix])))
    ).catch(() => {});
  }, []);

  useEffect(() => {
    refresh();
    const onEv = () => refresh();
    window.addEventListener("ipam:refresh", onEv);
    return () => window.removeEventListener("ipam:refresh", onEv);
  }, [refresh]);

  const act = async (id: number, status: "active" | "reserved") => {
    try {
      await api.post(`/api/v1/discovery/${id}/confirm`, { status });
      toast.success(status === "active" ? "Marked active" : "Marked reserved");
      refresh();
    } catch (e) {
      toast.error("Failed", { description: String(e) });
    }
  };

  const remove = async (id: number) => {
    try {
      await api.del(`/api/v1/addresses/${id}`);
      toast.success("Removed");
      refresh();
    } catch (e) {
      toast.error("Failed", { description: String(e) });
    }
  };

  const bulk = async (action: "set_status" | "delete") => {
    try {
      const r = await api.post<{ affected: number }>("/api/v1/addresses/bulk", {
        ids: [...selected],
        action,
        ...(action === "set_status" ? { status: "active" } : {}),
      });
      toast.success(`Updated ${r.affected} hosts`);
      setSelected(new Set());
      refresh();
    } catch (e) {
      toast.error("Bulk update failed", { description: String(e) });
    }
  };

  const allChecked = items.length > 0 && selected.size === items.length;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Discovery inbox</h1>
      <p className="text-sm text-muted-foreground">
        Hosts found by scanners that haven&apos;t been confirmed yet.
      </p>

      {selected.size > 0 && (
        <div className="sticky top-4 z-10 flex w-fit items-center gap-3 rounded-lg border bg-card px-4 py-2 shadow-lg">
          <span className="text-sm text-muted-foreground">
            {selected.size} selected
          </span>
          <Button size="sm" variant="outline" onClick={() => bulk("set_status")}>
            <Check /> Mark all active
          </Button>
          <Button size="sm" variant="destructive" onClick={() => bulk("delete")}>
            <Trash2 /> Delete
          </Button>
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
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-8">
                  <Checkbox
                    checked={allChecked}
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
                      <Button size="sm" variant="ghost" onClick={() => act(a.id, "active")}>
                        <Check className="text-emerald-400" /> Active
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => act(a.id, "reserved")}>
                        <ShieldCheck className="text-amber-400" /> Reserve
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => remove(a.id)}>
                        <Trash2 className="text-red-400" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={10} className="py-10 text-center text-muted-foreground">
                    Inbox zero — nothing pending review.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
