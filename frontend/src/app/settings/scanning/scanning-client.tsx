"use client";

import { useEffect, useState } from "react";
import { ChevronDown, ChevronRight, Radar } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
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
import { SettingField } from "@/components/settings/field";
import { CidrListEditor } from "@/components/settings/cidr-list-editor";

type Key = keyof SettingsValues;

export default function ScanningPage() {
  const { can } = useAuth();
  const canAdmin = can(PERM.SYSTEM_ADMIN);
  const [s, setS] = useState<SettingsOut | null>(null);
  const [draft, setDraft] = useState<SettingsValues | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [advanced, setAdvanced] = useState(false);

  useEffect(() => {
    api
      .get<SettingsOut>("/api/v1/settings")
      .then((o) => {
        setS(o);
        setDraft(o.values);
      })
      .catch(() => {});
  }, []);

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
      toast.success("Scanning settings saved", {
        description: "Schedule changes apply within ~1 minute.",
      });
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
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }

  const num =
    (k: Key) => (e: React.ChangeEvent<HTMLInputElement>) =>
      set(k, (e.target.value === "" ? 0 : Number(e.target.value)) as never);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Scanning</h1>
        <p className="text-sm text-muted-foreground">
          Which networks the worker scans and how. Saved changes take effect
          immediately for manual scans and within ~1 minute for schedules — no
          restart needed.
          {s?.system.lan.cidr && (
            <>
              {" "}
              Detected LAN:{" "}
              <code className="text-emerald-400">
                {s.system.lan.cidr}
                {s.system.lan.iface ? ` on ${s.system.lan.iface}` : ""}
              </code>
              {s.system.lan.source === "local" && " (api container)"}
            </>
          )}
        </p>
      </div>

      <fieldset disabled={!canAdmin} className="contents">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Radar className="h-4 w-4" /> Networks
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <SettingField
            label="Scan networks"
            hint="Scheduled scans cover these CIDRs. Empty = auto-detected LAN."
            source={src("scan_networks")}
            onReset={canAdmin ? () => resetKey("scan_networks") : undefined}
            error={errors.scan_networks}
          >
            <CidrListEditor
              value={draft.scan_networks}
              onChange={(v) => set("scan_networks", v)}
            />
          </SettingField>

          <SettingField
            label="Excluded networks"
            hint="Never scanned — blocks manual scans of these CIDRs too."
            source={src("scan_exclude_networks")}
            onReset={canAdmin ? () => resetKey("scan_exclude_networks") : undefined}
            error={errors.scan_exclude_networks}
          >
            <CidrListEditor
              value={draft.scan_exclude_networks}
              onChange={(v) => set("scan_exclude_networks", v)}
            />
          </SettingField>

          <SettingField
            label="Only scan configured networks"
            hint="Refuse any scan outside the networks list above."
            source={src("scan_only_configured")}
            onReset={canAdmin ? () => resetKey("scan_only_configured") : undefined}
            error={errors.scan_only_configured}
          >
            <Switch
              checked={draft.scan_only_configured}
              onCheckedChange={(v) => set("scan_only_configured", v)}
            />
          </SettingField>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Schedule & rate limit</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <SettingField
            label="Scheduled scan interval (minutes)"
            hint="0 = manual scans only. E.g. 60 hourly, 1440 daily."
            source={src("scan_interval_minutes")}
            onReset={canAdmin ? () => resetKey("scan_interval_minutes") : undefined}
            error={errors.scan_interval_minutes}
          >
            <Input
              type="number"
              min={0}
              max={10080}
              value={draft.scan_interval_minutes}
              onChange={num("scan_interval_minutes")}
            />
          </SettingField>
          <SettingField
            label="Min seconds between scans of same CIDR"
            hint="Rate limit for manual scans."
            source={src("scan_min_interval_seconds")}
            onReset={canAdmin ? () => resetKey("scan_min_interval_seconds") : undefined}
            error={errors.scan_min_interval_seconds}
          >
            <Input
              type="number"
              min={0}
              max={3600}
              value={draft.scan_min_interval_seconds}
              onChange={num("scan_min_interval_seconds")}
            />
          </SettingField>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Probing</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <SettingField
            label="TCP ports probed per host"
            hint="Used for service/device typing. Comma-separated."
            source={src("scan_tcp_ports")}
            onReset={canAdmin ? () => resetKey("scan_tcp_ports") : undefined}
            error={errors.scan_tcp_ports}
          >
            <Input
              className="font-mono text-xs"
              value={draft.scan_tcp_ports.join(",")}
              onChange={(e) =>
                set(
                  "scan_tcp_ports",
                  e.target.value
                    .split(",")
                    .map((p) => p.trim())
                    .filter(Boolean)
                    .map((p) => Number(p))
                )
              }
            />
          </SettingField>

          <button
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setAdvanced(!advanced)}
          >
            {advanced ? (
              <ChevronDown className="h-3.5 w-3.5" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5" />
            )}
            Advanced
          </button>

          {advanced && (
            <div className="grid gap-4 border-l pl-4 sm:grid-cols-3">
              <SettingField
                label="Interface"
                hint="Empty = default-route interface."
                source={src("scan_interface")}
                onReset={canAdmin ? () => resetKey("scan_interface") : undefined}
                error={errors.scan_interface}
              >
                <Input
                  className="font-mono text-xs"
                  placeholder="auto"
                  value={draft.scan_interface}
                  onChange={(e) => set("scan_interface", e.target.value)}
                />
              </SettingField>
              <SettingField
                label="ICMP timeout (s)"
                source={src("scan_icmp_timeout")}
                onReset={canAdmin ? () => resetKey("scan_icmp_timeout") : undefined}
                error={errors.scan_icmp_timeout}
              >
                <Input
                  type="number"
                  step={0.1}
                  min={0.1}
                  max={10}
                  value={draft.scan_icmp_timeout}
                  onChange={num("scan_icmp_timeout")}
                />
              </SettingField>
              <SettingField
                label="TCP timeout (s)"
                source={src("scan_tcp_timeout")}
                onReset={canAdmin ? () => resetKey("scan_tcp_timeout") : undefined}
                error={errors.scan_tcp_timeout}
              >
                <Input
                  type="number"
                  step={0.1}
                  min={0.1}
                  max={10}
                  value={draft.scan_tcp_timeout}
                  onChange={num("scan_tcp_timeout")}
                />
              </SettingField>
              <SettingField
                label="Concurrency"
                hint="Parallel probes."
                source={src("scan_concurrency")}
                onReset={canAdmin ? () => resetKey("scan_concurrency") : undefined}
                error={errors.scan_concurrency}
              >
                <Input
                  type="number"
                  min={1}
                  max={1024}
                  value={draft.scan_concurrency}
                  onChange={num("scan_concurrency")}
                />
              </SettingField>
            </div>
          )}
        </CardContent>
      </Card>
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
          Read-only — changing scanning settings requires the Administrator
          role.
        </p>
      )}
    </div>
  );
}
