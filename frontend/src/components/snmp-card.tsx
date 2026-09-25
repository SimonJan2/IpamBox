"use client";

import { useState } from "react";
import { Antenna, FlaskConical, RefreshCw } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { useFeatureFlag } from "@/lib/features";
import { timeAgo } from "@/lib/utils";
import type {
  DeviceDetail,
  SnmpPollResult,
  SnmpTestResult,
  SnmpVersion,
} from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

const VERSIONS: SnmpVersion[] = ["v1", "v2c", "v3"];
const AUTH_PROTOS = ["sha", "md5", "sha224", "sha256", "sha384", "sha512"];
const PRIV_PROTOS = ["aes128", "aes192", "aes256", "des", "3des"];

const EMPTY_CRED = {
  community: "",
  user: "",
  auth_key: "",
  priv_key: "",
  auth_proto: "sha",
  priv_proto: "aes128",
  context: "",
};

/** Per-device SNMP config + live test/poll — the V8 card on device detail.
 *  The credential fields are write-only (they start empty even when a
 *  credential is stored; `snmp_cred_set` is the "configured" chip). */
export function SnmpCard({
  device,
  onChanged,
}: {
  device: DeviceDetail;
  onChanged: () => void;
}) {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const laneOn = useFeatureFlag("snmp_enabled");
  const [version, setVersion] = useState<SnmpVersion>(
    device.snmp_version ?? "v2c"
  );
  const [port, setPort] = useState(String(device.snmp_port || 161));
  const [cred, setCred] = useState(EMPTY_CRED);
  const [busy, setBusy] = useState(false);
  const [test, setTest] = useState<SnmpTestResult | null>(null);

  const credTyped = Boolean(
    cred.community || cred.user || cred.auth_key || cred.priv_key ||
      cred.context
  );
  const dirty =
    version !== device.snmp_version ||
    port !== String(device.snmp_port || 161) ||
    credTyped;

  const save = async (extra: Record<string, unknown> = {}) => {
    setBusy(true);
    try {
      const body: Record<string, unknown> = {
        snmp_version: version,
        snmp_port: Number(port) || 161,
        ...extra,
      };
      if (credTyped) {
        body.snmp_cred = Object.fromEntries(
          Object.entries(cred).filter(([, v]) => v !== "")
        );
      }
      await api.patch(`/api/v1/devices/${device.id}`, body);
      setCred(EMPTY_CRED);
      setTest(null);
      onChanged();
    } catch (e) {
      toast.error("SNMP save failed", { description: String(e) });
      throw e;
    } finally {
      setBusy(false);
    }
  };

  const toggle = async (on: boolean) => {
    // Enabling bundles any pending form fields so one click provisions the
    // device end-to-end; disabling is a bare flag flip (creds stay stored).
    try {
      await save(on ? { snmp_enabled: true } : { snmp_enabled: false });
      toast.success(on ? "SNMP enabled" : "SNMP disabled");
    } catch {
      /* save() already toasted */
    }
  };

  const clearCred = async () => {
    setBusy(true);
    try {
      await api.patch(`/api/v1/devices/${device.id}`, { snmp_cred: null });
      toast.success("Credential cleared");
      onChanged();
    } catch (e) {
      toast.error("Clear failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const runTest = async () => {
    setBusy(true);
    setTest(null);
    try {
      const r = await api.post<SnmpTestResult>(
        `/api/v1/devices/${device.id}/snmp/test`,
        {}
      );
      setTest(r);
      if (!r.up) toast.error("SNMP unreachable", { description: r.error });
    } catch (e) {
      toast.error("Test failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const runPoll = async () => {
    setBusy(true);
    try {
      const r = await api.post<SnmpPollResult>(
        `/api/v1/devices/${device.id}/snmp/poll`,
        {}
      );
      if (r.up) {
        toast.success("Poll complete", {
          description:
            `${r.interfaces_seen} ports seen` +
            (r.interfaces_created
              ? `, ${r.interfaces_created} created`
              : "") +
            (r.links_applied ? `, ${r.links_applied} links applied` : "") +
            (r.error ? ` — ${r.error}` : ""),
        });
      } else {
        toast.error("Poll failed", { description: r.error });
      }
      onChanged();
    } catch (e) {
      toast.error("Poll failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-1.5 rounded-lg border bg-card p-3 text-sm">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1.5 font-medium">
          <Antenna className="h-4 w-4" /> SNMP
          {device.snmp_cred_set && (
            <Badge variant="secondary" className="text-[10px]">
              credential set
            </Badge>
          )}
        </span>
        <Switch
          checked={device.snmp_enabled}
          onCheckedChange={(v) => void toggle(v)}
          disabled={!canWrite || busy}
          aria-label="Enable SNMP polling"
        />
      </div>
      {!device.snmp_enabled ? null : (
        <div className="space-y-2 pt-1">
          {!laneOn && (
            <p className="text-xs text-amber-400/90">
              The global SNMP lane is off (Settings → Features) — Test and
              Poll still work; scheduled polls are paused.
            </p>
          )}
          <div className="grid grid-cols-2 gap-2">
            <div className="grid gap-1">
              <Label htmlFor="snmp-version" className="text-xs">
                Version
              </Label>
              <Select
                value={version}
                onValueChange={(v) => setVersion(v as SnmpVersion)}
                disabled={!canWrite}
              >
                <SelectTrigger id="snmp-version" className="h-8">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {VERSIONS.map((v) => (
                    <SelectItem key={v} value={v}>
                      {v}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1">
              <Label htmlFor="snmp-port" className="text-xs">
                UDP port
              </Label>
              <Input
                id="snmp-port"
                dir="ltr"
                className="h-8"
                inputMode="numeric"
                value={port}
                onChange={(e) => setPort(e.target.value)}
                disabled={!canWrite}
              />
            </div>
          </div>
          {version === "v3" ? (
            <div className="grid gap-2">
              <div className="grid gap-1">
                <Label htmlFor="snmp-user" className="text-xs">
                  User
                </Label>
                <Input
                  id="snmp-user"
                  dir="ltr"
                  className="h-8 font-mono"
                  autoComplete="off"
                  value={cred.user}
                  onChange={(e) => setCred({ ...cred, user: e.target.value })}
                  disabled={!canWrite}
                  placeholder={device.snmp_cred_set ? "••• stored" : ""}
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="grid gap-1">
                  <Label htmlFor="snmp-auth" className="text-xs">
                    Auth key
                  </Label>
                  <Input
                    id="snmp-auth"
                    type="password"
                    className="h-8 font-mono"
                    autoComplete="off"
                    value={cred.auth_key}
                    onChange={(e) =>
                      setCred({ ...cred, auth_key: e.target.value })
                    }
                    disabled={!canWrite}
                  />
                </div>
                <div className="grid gap-1">
                  <Label htmlFor="snmp-authproto" className="text-xs">
                    Auth proto
                  </Label>
                  <Select
                    value={cred.auth_proto}
                    onValueChange={(v) =>
                      setCred({ ...cred, auth_proto: v })
                    }
                    disabled={!canWrite}
                  >
                    <SelectTrigger id="snmp-authproto" className="h-8">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {AUTH_PROTOS.map((p) => (
                        <SelectItem key={p} value={p}>
                          {p}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="grid gap-1">
                  <Label htmlFor="snmp-priv" className="text-xs">
                    Priv key
                  </Label>
                  <Input
                    id="snmp-priv"
                    type="password"
                    className="h-8 font-mono"
                    autoComplete="off"
                    value={cred.priv_key}
                    onChange={(e) =>
                      setCred({ ...cred, priv_key: e.target.value })
                    }
                    disabled={!canWrite}
                  />
                </div>
                <div className="grid gap-1">
                  <Label htmlFor="snmp-privproto" className="text-xs">
                    Priv proto
                  </Label>
                  <Select
                    value={cred.priv_proto}
                    onValueChange={(v) =>
                      setCred({ ...cred, priv_proto: v })
                    }
                    disabled={!canWrite}
                  >
                    <SelectTrigger id="snmp-privproto" className="h-8">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PRIV_PROTOS.map((p) => (
                        <SelectItem key={p} value={p}>
                          {p}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid gap-1">
                <Label htmlFor="snmp-context" className="text-xs">
                  Context{" "}
                  <span className="text-muted-foreground">(optional)</span>
                </Label>
                <Input
                  id="snmp-context"
                  dir="ltr"
                  className="h-8 font-mono"
                  autoComplete="off"
                  value={cred.context}
                  onChange={(e) =>
                    setCred({ ...cred, context: e.target.value })
                  }
                  disabled={!canWrite}
                  placeholder="default"
                />
              </div>
            </div>
          ) : (
            <div className="grid gap-1">
              <Label htmlFor="snmp-community" className="text-xs">
                Community
              </Label>
              <Input
                id="snmp-community"
                type="password"
                className="h-8 font-mono"
                autoComplete="off"
                value={cred.community}
                onChange={(e) =>
                  setCred({ ...cred, community: e.target.value })
                }
                disabled={!canWrite}
                placeholder={device.snmp_cred_set ? "••• stored" : ""}
              />
            </div>
          )}
          {device.snmp_cred_set && canWrite && (
            <button
              type="button"
              className="text-xs text-muted-foreground hover:text-rose-400"
              onClick={clearCred}
              disabled={busy}
            >
              clear stored credential
            </button>
          )}
          <div className="flex items-center gap-2">
            {canWrite && (
              <>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7"
                  onClick={() => void save()}
                  disabled={busy || !dirty}
                >
                  Save
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7"
                  onClick={() => void runTest()}
                  disabled={busy || !device.snmp_cred_set && !credTyped}
                  title="GET sysName + sysDescr"
                >
                  <FlaskConical className="h-3.5 w-3.5" /> Test
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7"
                  onClick={() => void runPoll()}
                  disabled={busy || !device.snmp_cred_set && !credTyped}
                  title="Full enrichment pass: IF-MIB + bridge MACs + LLDP"
                >
                  <RefreshCw className="h-3.5 w-3.5" /> Poll now
                </Button>
              </>
            )}
          </div>
          {test &&
            (test.up ? (
              <div className="rounded border border-emerald-700/50 bg-emerald-950/20 p-2 text-xs">
                <div className="font-medium text-emerald-300">
                  {test.sys_name || "up"}
                </div>
                {test.sys_descr && (
                  <div className="mt-0.5 line-clamp-3 text-muted-foreground">
                    {test.sys_descr}
                  </div>
                )}
              </div>
            ) : (
              <div className="rounded border border-rose-700/50 bg-rose-950/20 p-2 text-xs text-rose-300">
                {test.error || "no answer"}
              </div>
            ))}
          <div className="text-xs text-muted-foreground">
            {device.snmp_sys_name && (
              <span dir="auto">sysName: {device.snmp_sys_name} · </span>
            )}
            last ok:{" "}
            {device.snmp_last_ok_at ? timeAgo(device.snmp_last_ok_at) : "never"}
            {" · "}last trap:{" "}
            {device.snmp_last_trap_at
              ? timeAgo(device.snmp_last_trap_at)
              : "never"}
          </div>
          {device.snmp_last_error && (
            <div
              className="line-clamp-2 text-xs text-rose-400/90"
              title={device.snmp_last_error}
            >
              {device.snmp_last_error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
