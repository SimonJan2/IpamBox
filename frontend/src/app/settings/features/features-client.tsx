"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  Antenna,
  Archive,
  Container,
  Crosshair,
  FileBadge,
  Inbox,
  Network,
  Radar,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import type { SettingsOut, SettingsValues } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { SettingField } from "@/components/settings/field";

type Key = keyof SettingsValues;

/**
 * Feature toggles — behavior switches editable at runtime.
 * To add one: Settings field in config.py, EDITABLE entry in
 * runtime_settings.py, SettingsPatch field, SettingsValues key, and a
 * FEATURES entry below. Read it anywhere via useSetting(key) /
 * useFeatureFlag(key) on the client, or eff.values[key] on the backend.
 */
type FeatureDef = {
  key: Key;
  label: string;
  hint: string;
  type?: "bool" | "int" | "str";
  min?: number;
  max?: number;
  /** <input type=number> step — set for float settings (e.g. 0.5). */
  step?: number;
};

const GROUPS: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  features: FeatureDef[];
}[] = [
  {
    title: "Scanner reconciliation",
    icon: Radar,
    features: [
      {
        key: "scan_marks_offline",
        label: "Missing hosts go offline",
        hint: "Default on: a documented host absent from a scan flips to offline. Off = scans only add/refresh, never mark anything down — good for firewalled segments the scanner can't fully reach.",
      },
      {
        key: "scan_offline_grace_scans",
        label: "Consecutive misses before offline",
        type: "int",
        min: 0,
        max: 100,
        hint: "Default 0 = offline on the first missed scan. Set N to require N consecutive absent scans first — kills flapping on flaky networks.",
      },
      {
        key: "scan_reactivates_offline",
        label: "Seen hosts reactivate automatically",
        hint: "Default on: an offline host that answers a scan flips back to active. Off = stays offline until a human confirms.",
      },
      {
        key: "scan_new_hosts_discovered",
        label: "New hosts land in the Discovery inbox",
        hint: "Default on: scan-found hosts arrive as 'discovered' pending review. Off = they become active immediately — for trusted networks where the scan is authoritative.",
      },
      {
        key: "scan_stored_mac_wins",
        label: "Stored MAC is authoritative",
        hint: "Default off: a scanned MAC that disagrees with the stored one wins (flagged for review). On = keep the stored MAC and only flag — e.g. phones with randomized MACs.",
      },
      {
        key: "scan_overwrites_hostname",
        label: "DNS overwrites hostnames",
        hint: "Default off: PTR lookups only fill empty hostnames. On = DNS is authoritative and overwrites stored names.",
      },
      {
        key: "scan_infers_device_type",
        label: "Scanner infers device type",
        hint: "Default on: the scan's best-guess classification (printer, camera, …) fills device_type. Off = never overwrite an existing value — protects manual classification.",
      },
    ],
  },
  {
    title: "Scan targeting",
    icon: Crosshair,
    features: [
      {
        key: "scan_auto_create_prefix",
        label: "Auto-create prefixes for scans",
        hint: "Default on: a scan whose CIDR no prefix covers gets an auto-created active prefix. Off = the scan fails instead — enforces documented-first data.",
      },
      {
        key: "scan_infers_vrf",
        label: "Infer VRF from matching prefix",
        hint: "Default on: a scan without an explicit VRF uses the VRF of the matching/covering prefix. Off = always Global.",
      },
    ],
  },
  {
    title: "Discovery inbox",
    icon: Inbox,
    features: [
      {
        key: "discovery_expire_days",
        label: "Expire unreviewed hosts (days)",
        type: "int",
        min: 0,
        max: 3650,
        hint: "Default 0 = never expire. Set N to auto-delete 'discovered' rows that haven't been seen for N days.",
      },
    ],
  },
  {
    title: "Monitoring",
    icon: Activity,
    features: [
      {
        key: "monitoring_enabled",
        label: "Monitoring enabled",
        hint: "Default on: the per-minute monitor tick checks due targets. Off = the tick is a no-op — states freeze, no alerts fire.",
      },
      {
        key: "monitor_concurrency",
        label: "Check concurrency",
        type: "int",
        min: 1,
        max: 512,
        hint: "Default 64: parallel probes inside the single per-tick sweep job. Lower it on constrained workers.",
      },
      {
        key: "monitor_http_timeout",
        label: "HTTP check timeout (seconds)",
        type: "int",
        min: 1,
        max: 30,
        hint: "Default 5s per http check request. Ping/TCP reuse the scanner's probe timeouts.",
      },
      {
        key: "notify_retention_days",
        label: "Notification log retention (days)",
        type: "int",
        min: 0,
        max: 3650,
        hint: "Default 0 = keep forever. Set N to auto-delete notification_log rows older than N days.",
      },
    ],
  },
  {
    title: "SNMP enrichment",
    icon: Antenna,
    features: [
      {
        key: "snmp_enabled",
        label: "SNMP polling enabled",
        hint: "Default off: the per-minute tick looks for devices whose SNMP is enabled and due, and polls them in one bounded sweep. Off = the lane is a no-op; per-device Test/Poll buttons still work.",
      },
      {
        key: "snmp_interval_minutes",
        label: "Poll interval (minutes)",
        type: "int",
        min: 5,
        max: 1440,
        hint: "Default 60: a device is due when its last poll is older than this. Interfaces whose snmp_seen_at falls ~2 intervals behind are shown dimmed.",
      },
      {
        key: "snmp_concurrency",
        label: "Poll concurrency",
        type: "int",
        min: 1,
        max: 16,
        hint: "Default 4: parallel device polls inside the single per-tick sweep — a dead device costs only its own timeout, never the lane.",
      },
      {
        key: "snmp_timeout",
        label: "Per-device timeout (seconds)",
        type: "int",
        min: 0.5,
        max: 10,
        step: 0.5,
        hint: "Default 2s per SNMP request. Devices that don't answer get snmp_last_error stamped; nothing else is written.",
      },
      {
        key: "snmp_learns_interfaces",
        label: "Learn interfaces from IF-MIB",
        hint: "Default on: polls create/update ports the device reports (source 'snmp') with live oper/admin state and speed. Off = only status stamps + link filling. Manually created ports are never overwritten.",
      },
      {
        key: "snmp_fills_connected",
        label: "Fill connected IP from bridge MACs",
        hint: "Default on: learned bridge-MAC entries resolve known IPs to the port they're behind (connected_interface_id). Off = collect MACs but don't write links. Manual links always win.",
      },
    ],
  },
  {
    title: "Data retention",
    icon: Archive,
    features: [
      {
        key: "changelog_retention_days",
        label: "Changelog retention (days)",
        type: "int",
        min: 0,
        max: 3650,
        hint: "Default 0 = keep forever. Set N to auto-delete changelog entries older than N days.",
      },
      {
        key: "scan_job_retention_days",
        label: "Scan history retention (days)",
        type: "int",
        min: 0,
        max: 3650,
        hint: "Default 0 = keep forever. Set N to auto-delete finished scan jobs older than N days.",
      },
    ],
  },
  {
    title: "Certificates",
    icon: FileBadge,
    features: [
      {
        key: "cert_warn_days",
        label: "Expiry warning window (days)",
        type: "int",
        min: 1,
        max: 365,
        hint: "Default 30: certificates expiring within this many days show the amber 'Nd left' badge.",
      },
    ],
  },
  {
    title: "Rackula",
    icon: Container,
    features: [
      {
        key: "rackula_base_url",
        label: "Rackula instance URL",
        type: "str",
        hint: "Base URL of a self-hosted Rackula instance, e.g. http://rackula:8042 — enables 'Open in Rackula'. Leave empty in air-gapped setups.",
      },
    ],
  },
  {
    title: "Site cascade",
    icon: Network,
    features: [
      {
        key: "site_code_follow_site",
        label: "Site codes follow site changes",
        hint: "Default on: when a site's code/number/name changes, linked VRF names and circuit/service site fields that were following it update automatically — and edit dialogs treat remaining mismatches as stale. Off = mismatched stored values are kept as deliberate manual overrides.",
      },
    ],
  },
];

export default function FeaturesPage() {
  const { can } = useAuth();
  const canAdmin = can(PERM.SYSTEM_ADMIN);
  const settingsQ = useAsyncData(() =>
    api.get<SettingsOut>("/api/v1/settings")
  );
  const s = settingsQ.data;
  const setS = settingsQ.setData;
  const [draft, setDraft] = useState<SettingsValues | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (s) setDraft(s.values);
  }, [s]);

  const set = <K extends Key>(k: K, v: SettingsValues[K]) =>
    setDraft((d) => (d ? { ...d, [k]: v } : d));
  const src = (k: Key) => s?.sources[k];

  const dirty: Partial<SettingsValues> = {};
  if (s && draft) {
    for (const k of Object.keys(draft) as Key[]) {
      if (JSON.stringify(draft[k]) !== JSON.stringify(s.values[k]))
        dirty[k] = draft[k] as never;
    }
  }

  const save = async () => {
    if (!Object.keys(dirty).length) return;
    setBusy(true);
    setErrors({});
    try {
      const out = await api.patch<SettingsOut>("/api/v1/settings", dirty);
      setS(out);
      setDraft(out.values);
      toast.success("Feature toggles saved");
    } catch (e) {
      const f = (e as Error & { fields?: Record<string, string> }).fields;
      if (f) setErrors(f);
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const resetKey = async (k: Key) => {
    try {
      const out = await api.patch<SettingsOut>("/api/v1/settings", {
        [k]: null,
      });
      setS(out);
      setDraft(out.values);
      toast.success(`${k} reset to .env / default`);
    } catch (e) {
      toast.error("Reset failed", { description: String(e) });
    }
  };

  if (!draft) {
    return (
      <AsyncPanel
        loading={settingsQ.loading}
        error={settingsQ.error}
        onRetry={settingsQ.reload}
        empty
        emptyMessage="Settings unavailable."
      >
        {null}
      </AsyncPanel>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">Features <DocsLink slug="settings" /></h1>
        <p className="text-sm text-muted-foreground">
          Behavior switches — how the app treats scanned, imported and
          site-derived data. Saved changes take effect immediately; no restart
          needed. Defaults match the original behavior.
        </p>
      </div>

      <fieldset disabled={!canAdmin} className="contents">
        {GROUPS.map((g) => (
          <Card key={g.title}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <g.icon className="h-4 w-4" /> {g.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {g.features.map((f) => (
                <SettingField
                  key={f.key}
                  label={f.label}
                  hint={f.hint}
                  source={src(f.key)}
                  onReset={canAdmin ? () => resetKey(f.key) : undefined}
                  error={errors[f.key]}
                >
                  {f.type === "int" ? (
                    <Input
                      type="number"
                      min={f.min}
                      max={f.max}
                      step={f.step ?? 1}
                      value={draft[f.key] as number}
                      onChange={(e) =>
                        set(
                          f.key,
                          (e.target.value === ""
                            ? 0
                            : Number(e.target.value)) as never
                        )
                      }
                    />
                  ) : f.type === "str" ? (
                    <Input
                      dir="ltr"
                      value={draft[f.key] as string}
                      onChange={(e) =>
                        set(f.key, e.target.value as never)
                      }
                    />
                  ) : (
                    <Switch
                      checked={Boolean(draft[f.key])}
                      onCheckedChange={(v) => set(f.key, v as never)}
                    />
                  )}
                </SettingField>
              ))}
            </CardContent>
          </Card>
        ))}
      </fieldset>

      {canAdmin ? (
        <div className="flex items-center gap-3">
          <Button
            size="sm"
            onClick={save}
            disabled={busy || !Object.keys(dirty).length}
          >
            {busy ? "Saving…" : "Save changes"}
          </Button>
          {Object.keys(dirty).length > 0 && (
            <span className="text-xs text-muted-foreground">
              {Object.keys(dirty).length} unsaved change
              {Object.keys(dirty).length === 1 ? "" : "s"}
            </span>
          )}
        </div>
      ) : (
        <p className="text-xs text-muted-foreground">
          Read-only — changing feature toggles requires the Administrator
          role.
        </p>
      )}
    </div>
  );
}
