"use client";

import { useEffect, useState } from "react";
import { SlidersHorizontal } from "lucide-react";
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
import { Switch } from "@/components/ui/switch";
import { AsyncPanel } from "@/components/async-panel";
import { SettingField } from "@/components/settings/field";

type Key = keyof SettingsValues;

/**
 * Feature toggles — boolean behavior switches editable at runtime.
 * To add one: Settings field in config.py, EDITABLE entry in
 * runtime_settings.py, SettingsPatch field, SettingsValues key, and a
 * FEATURES entry below. Read it anywhere via useFeatureFlag(key).
 */
const FEATURES: { key: Key; label: string; hint: string }[] = [
  {
    key: "site_code_follow_site",
    label: "Site codes follow site changes",
    hint: "When a site's code/number/name changes, linked VRF names and circuit/service site fields that were following it update automatically — and edit dialogs treat remaining mismatches as stale. Off = mismatched stored values are kept as deliberate manual overrides.",
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
        <h1 className="text-xl font-semibold">Features</h1>
        <p className="text-sm text-muted-foreground">
          Behavior switches — how the app treats imported and site-derived
          data. Saved changes take effect immediately; no restart needed.
        </p>
      </div>

      <fieldset disabled={!canAdmin} className="contents">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <SlidersHorizontal className="h-4 w-4" /> Feature toggles
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {FEATURES.map((f) => (
              <SettingField
                key={f.key}
                label={f.label}
                hint={f.hint}
                source={src(f.key)}
                onReset={canAdmin ? () => resetKey(f.key) : undefined}
                error={errors[f.key]}
              >
                <Switch
                  checked={Boolean(draft[f.key])}
                  onCheckedChange={(v) => set(f.key, v as never)}
                />
              </SettingField>
            ))}
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
          Read-only — changing feature toggles requires the Administrator
          role.
        </p>
      )}
    </div>
  );
}
