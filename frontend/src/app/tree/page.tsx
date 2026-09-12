"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, ChevronDown, ChevronRight, Network, Waypoints } from "lucide-react";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { PrefixNode, SiteNode } from "@/types";
import { PrefixStatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function PrefixTreeNode({ node, depth }: { node: PrefixNode; depth: number }) {
  const [open, setOpen] = useState(true);
  return (
    <div>
      <div
        className="flex items-center gap-1.5 rounded px-1 py-1 hover:bg-accent"
        style={{ marginLeft: depth * 18 }}
      >
        <button
          className={cn("p-0.5", node.children.length === 0 && "invisible")}
          onClick={() => setOpen(!open)}
        >
          {open ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
        </button>
        <Link
          href={`/prefixes/${node.id}`}
          className="font-mono text-sm text-emerald-400 hover:underline"
        >
          {node.prefix}
        </Link>
        <PrefixStatusBadge s={node.status} />
        {node.vlan_id && (
          <span className="text-xs text-muted-foreground">VLAN {node.vlan_id}</span>
        )}
        {node.description && (
          <span className="truncate text-xs text-muted-foreground">· {node.description}</span>
        )}
      </div>
      {open &&
        node.children.map((c) => <PrefixTreeNode key={c.id} node={c} depth={depth + 1} />)}
    </div>
  );
}

function SiteSection({ site }: { site: SiteNode }) {
  const [open, setOpen] = useState(true);
  return (
    <Card>
      <CardHeader className="cursor-pointer pb-3" onClick={() => setOpen(!open)}>
        <CardTitle className="flex items-center gap-2 text-base">
          {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          <Building2 className="h-4 w-4 text-emerald-400" />
          {site.name}
        </CardTitle>
      </CardHeader>
      {open && (
        <CardContent className="space-y-4">
          {site.vrfs.length === 0 && (
            <p className="text-sm text-muted-foreground">No VRFs at this site.</p>
          )}
          {site.vrfs.map((v) => (
            <div key={v.id} className="rounded-md border p-3">
              <div className="mb-2 flex items-center gap-2">
                <Waypoints className="h-4 w-4 text-cyan-400" />
                <span className="font-medium">{v.name}</span>
                {v.rd && (
                  <span className="font-mono text-xs text-muted-foreground">RD {v.rd}</span>
                )}
              </div>
              {v.prefixes.length === 0 ? (
                <p className="pl-6 text-sm text-muted-foreground">No prefixes.</p>
              ) : (
                v.prefixes.map((p) => <PrefixTreeNode key={p.id} node={p} depth={0} />)
              )}
            </div>
          ))}
        </CardContent>
      )}
    </Card>
  );
}

export default function TreePage() {
  const [tree, setTree] = useState<SiteNode[]>([]);
  useEffect(() => {
    api.get<SiteNode[]>("/api/v1/prefixes/tree").then(setTree).catch(() => {});
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="flex items-center gap-2 text-xl font-semibold">
        <Network className="h-5 w-5 text-emerald-400" /> Prefix hierarchy
      </h1>
      {tree.length === 0 && (
        <p className="text-sm text-muted-foreground">
          Nothing here yet — create a site and prefixes.
        </p>
      )}
      {tree.map((s) => (
        <SiteSection key={s.id ?? "none"} site={s} />
      ))}
    </div>
  );
}
