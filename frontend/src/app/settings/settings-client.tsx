"use client";

import { Activity, Info, Link2, Server } from "lucide-react";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import type { DashboardStats, SettingsOut } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

function Row({ k, v, mono = true }: { k: string; v: React.ReactNode; mono?: boolean }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-1">
      <span className="shrink-0 text-sm text-muted-foreground">{k}</span>
      <span className={`truncate text-right text-sm ${mono ? "font-mono text-xs" : ""}`}>
        {v}
      </span>
    </div>
  );
}

export default function SettingsPage() {
  const settingsQ = useAsyncData(() =>
    api.get<SettingsOut>("/api/v1/settings")
  );
  const statsQ = useAsyncData(() =>
    api.get<DashboardStats>("/api/v1/dashboard/stats")
  );
  const settings = settingsQ.data;
  const stats = statsQ.data;
  const ready = settingsQ.loading
    ? null
    : settingsQ.error
      ? "degraded"
      : "ok";

  const lan = settings?.system.lan;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">General</h1>
        <p className="text-sm text-muted-foreground">
          System information and environment configuration. Values marked
          <Badge variant="outline" className="mx-1 text-[10px] font-normal text-muted-foreground">
            default
          </Badge>
          or
          <Badge variant="outline" className="mx-1 text-[10px] font-normal border-sky-500/40 text-sky-400">
            .env
          </Badge>
          come from the environment — edit <code>.env</code> and restart to
          change them.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Info className="h-4 w-4" /> System
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AsyncPanel
            loading={settingsQ.loading}
            error={settingsQ.error}
            onRetry={settingsQ.reload}
          >
          <Row k="IpamBox version" v={settings?.system.app_version ?? "…"} />
          <Row k="Schema revision" v={settings?.system.alembic_head ?? "…"} />
          <Row
            k="Detected LAN"
            v={
              lan?.cidr
                ? `${lan.cidr}${lan.iface ? ` on ${lan.iface}` : ""}${lan.source === "local" ? " (api container)" : ""}`
                : "detecting…"
            }
          />
          <Row
            k="API status"
            v={
              ready === "ok" ? (
                <span className="text-emerald-400">reachable</span>
              ) : ready === "degraded" ? (
                <span className="text-rose-400">error</span>
              ) : (
                "…"
              )
            }
            mono={false}
          />
          </AsyncPanel>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Activity className="h-4 w-4" /> Inventory
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-x-8 sm:grid-cols-3">
          <AsyncPanel
            loading={statsQ.loading}
            error={statsQ.error}
            onRetry={statsQ.reload}
            className="col-span-full"
          >
          <Row k="Sites" v={stats?.sites_total ?? "…"} />
          <Row k="VRFs" v={stats?.vrfs_total ?? "…"} />
          <Row k="Prefixes" v={stats?.prefixes_total ?? "…"} />
          <Row k="Addresses" v={stats?.ips_total ?? "…"} />
          <Row k="Discovered" v={stats?.devices_discovered ?? "…"} />
          <Row k="Scans run" v={stats?.scans_total ?? "…"} />
          </AsyncPanel>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Server className="h-4 w-4" /> Environment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-2 text-xs text-muted-foreground">
            Read-only — these come from <code>.env</code> / compose and need a
            container restart to change.
          </p>
          <AsyncPanel
            loading={settingsQ.loading}
            error={settingsQ.error}
            onRetry={settingsQ.reload}
          >
          <Row k="Database" v={settings?.env.database_url ?? "…"} />
          <Row k="Redis" v={settings?.env.redis_url ?? "…"} />
          <Row
            k="CORS origins"
            v={settings?.env.cors_origins.join(", ") || "—"}
          />
          <Row k="Backup dir" v={settings?.env.backup_dir ?? "…"} />
          <Row
            k="Auth disabled"
            v={settings ? String(settings.env.ipambox_allow_insecure) : "…"}
          />
          <Row
            k="Secure cookie"
            v={settings ? String(settings.env.ipambox_cookie_secure) : "…"}
          />
          <Row
            k="Password provisioned"
            v={settings ? String(settings.env.ipambox_password_set) : "…"}
          />
          </AsyncPanel>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Link2 className="h-4 w-4" /> Operations endpoints
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm text-muted-foreground">
          <p className="mb-2 text-xs">
            Served by the API container (host port <code>API_PORT</code>,
            default 8001) — not through the web proxy.
          </p>
          <Row k="Liveness" v="GET /healthz" />
          <Row k="Readiness (db + redis)" v="GET /readyz" />
          <Row k="Prometheus metrics" v="GET /metrics" />
          <Row k="OpenAPI docs" v="GET /docs" />
        </CardContent>
      </Card>
    </div>
  );
}
