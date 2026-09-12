"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, ShieldCheck, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type { IpAddress, Prefix } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Discovery inbox</h1>
      <p className="text-sm text-muted-foreground">
        Hosts found by scanners that haven&apos;t been confirmed yet.
      </p>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">{items.length} pending</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Address</TableHead>
                <TableHead>Prefix</TableHead>
                <TableHead>Hostname</TableHead>
                <TableHead>MAC</TableHead>
                <TableHead>Vendor</TableHead>
                <TableHead>Last seen</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((a) => (
                <TableRow key={a.id}>
                  <TableCell className="font-mono">{a.address}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {prefixes[a.prefix_id] ?? a.prefix_id}
                  </TableCell>
                  <TableCell>{a.hostname ?? "—"}</TableCell>
                  <TableCell className="font-mono text-xs">{a.mac_address ?? "—"}</TableCell>
                  <TableCell className="text-muted-foreground">{a.vendor ?? "—"}</TableCell>
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
                  <TableCell colSpan={7} className="py-10 text-center text-muted-foreground">
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
