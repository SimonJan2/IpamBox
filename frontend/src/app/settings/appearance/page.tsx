"use client";

import { Palette } from "lucide-react";

import { usePrefs } from "@/lib/prefs";
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
import { SettingField } from "@/components/settings/field";

export default function AppearancePage() {
  const [prefs, setPrefs] = usePrefs();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Appearance</h1>
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
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dark">Dark</SelectItem>
                <SelectItem value="light">Light</SelectItem>
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
              <SelectTrigger>
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
              <SelectTrigger>
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
              <SelectTrigger>
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
        </CardContent>
      </Card>
    </div>
  );
}
