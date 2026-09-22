"use client";

import { Palette } from "lucide-react";

import { THEMES, resolveTheme, usePrefs } from "@/lib/prefs";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { SettingField } from "@/components/settings/field";
import { DocsLink } from "@/components/docs/docs-link";

export default function AppearancePage() {
  const [prefs, setPrefs] = usePrefs();
  const resolved = resolveTheme(prefs.theme);
  const isTn = resolved.startsWith("tokyonight");
  const isCp = resolved.startsWith("cyberpunk");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">Appearance <DocsLink slug="settings" /></h1>
        <p className="text-sm text-muted-foreground">
          Per-browser preferences — stored locally, applied instantly, never
          sent to the server.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Palette className="h-4 w-4" /> Look &amp; feel
          </CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <SettingField label="Theme" hint="System follows your OS setting.">
            <Select
              value={prefs.theme}
              onValueChange={(v) => setPrefs({ theme: v as typeof prefs.theme })}
            >
              <SelectTrigger aria-label="Theme">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {THEMES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
                <SelectItem value="system">System</SelectItem>
              </SelectContent>
            </Select>
          </SettingField>

          <SettingField label="Table density">
            <Select
              value={prefs.density}
              onValueChange={(v) =>
                setPrefs({ density: v as typeof prefs.density })
              }
            >
              <SelectTrigger aria-label="Table density">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="comfortable">Comfortable</SelectItem>
                <SelectItem value="compact">Compact</SelectItem>
              </SelectContent>
            </Select>
          </SettingField>

          <SettingField
            label="Timestamp format"
            hint="How dates render across the UI."
          >
            <Select
              value={prefs.tsFormat}
              onValueChange={(v) =>
                setPrefs({ tsFormat: v as typeof prefs.tsFormat })
              }
            >
              <SelectTrigger aria-label="Timestamp format">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="local">Local (browser locale)</SelectItem>
                <SelectItem value="iso">ISO 8601 UTC</SelectItem>
              </SelectContent>
            </Select>
          </SettingField>

          <SettingField
            label="Rows per page"
            hint="Default page size for paged tables."
          >
            <Select
              value={String(prefs.pageSize)}
              onValueChange={(v) => setPrefs({ pageSize: Number(v) })}
            >
              <SelectTrigger aria-label="Rows per page">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {[25, 50, 100, 250].map((n) => (
                  <SelectItem key={n} value={String(n)}>
                    {n}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </SettingField>

          <SettingField
            label="Show slugs"
            hint="Show site/tag slugs next to names."
          >
            <Switch
              checked={prefs.showSlugs}
              onCheckedChange={(v) => setPrefs({ showSlugs: v })}
            />
          </SettingField>

          {(isTn || isCp) && (
            <>
              <SettingField
                label="Ambient effects"
                hint="Theme ambience — Calm keeps the look but stops motion, Off strips the extras."
              >
                <Select
                  value={prefs.fx}
                  onValueChange={(v) => setPrefs({ fx: v as typeof prefs.fx })}
                >
                  <SelectTrigger aria-label="Ambient effects">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="full">Full</SelectItem>
                    <SelectItem value="calm">Calm (no motion)</SelectItem>
                    <SelectItem value="off">Off (flat)</SelectItem>
                  </SelectContent>
                </Select>
              </SettingField>

              {prefs.fx === "full" && isTn && (
                <>
                  <SettingField
                    label="Starfield"
                    hint="Night-sky dots in the background."
                  >
                    <Switch
                      checked={prefs.fxStars}
                      onCheckedChange={(v) => setPrefs({ fxStars: v })}
                    />
                  </SettingField>

                  <SettingField
                    label="Film grain"
                    hint="Subtle texture over the page."
                  >
                    <Switch
                      checked={prefs.fxGrain}
                      onCheckedChange={(v) => setPrefs({ fxGrain: v })}
                    />
                  </SettingField>

                  <SettingField
                    label="Login neon ring"
                    hint="Spinning border on the sign-in card."
                  >
                    <Switch
                      checked={prefs.fxSpin}
                      onCheckedChange={(v) => setPrefs({ fxSpin: v })}
                    />
                  </SettingField>
                </>
              )}

              {prefs.fx === "full" && isCp && (
                <>
                  <SettingField
                    label="Scanlines"
                    hint="CRT line texture over the page."
                  >
                    <Switch
                      checked={prefs.fxScanlines}
                      onCheckedChange={(v) => setPrefs({ fxScanlines: v })}
                    />
                  </SettingField>

                  <SettingField
                    label="RGB glitch"
                    hint="Chromatic aberration on headings and hovers."
                  >
                    <Switch
                      checked={prefs.fxGlitch}
                      onCheckedChange={(v) => setPrefs({ fxGlitch: v })}
                    />
                  </SettingField>

                  <SettingField
                    label="HUD frame"
                    hint="Corner brackets on the viewport."
                  >
                    <Switch
                      checked={prefs.fxHud}
                      onCheckedChange={(v) => setPrefs({ fxHud: v })}
                    />
                  </SettingField>
                </>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
