"use client";

import { useEffect, useId, useState } from "react";
import {
  Activity,
  Pencil,
  Plus,
  Send,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import type {
  ChannelKind,
  ChannelTestOut,
  NotificationChannel,
  NotificationLogEntry,
  Page,
  SettingsOut,
  SettingsValues,
} from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { SettingField } from "@/components/settings/field";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type Key = keyof SettingsValues;

const KIND_LABEL: Record<ChannelKind, string> = {
  webhook: "Webhook",
  smtp: "SMTP email",
  discord: "Discord",
  telegram: "Telegram",
};

const KIND_SECRET_HINT: Record<ChannelKind, string> = {
  webhook: "Webhook URL (token in path — stored encrypted)",
  discord: "Discord webhook URL (stored encrypted)",
  telegram: "Bot token from @BotFather (stored encrypted)",
  smtp: "SMTP password — leave empty for unauthenticated relay",
};

function configSummary(c: NotificationChannel): string {
  const cfg = c.config ?? {};
  switch (c.kind) {
    case "webhook":
      return `${cfg.method ?? "POST"} · URL ${c.secret_set ? "configured" : "missing"}`;
    case "discord":
      return `webhook ${c.secret_set ? "configured" : "missing"}`;
    case "telegram":
      return `chat ${cfg.chat_id ?? "?"} · token ${c.secret_set ? "configured" : "missing"}`;
    case "smtp":
      return `${cfg.host ?? "?"}:${cfg.port ?? 587} → ${(cfg.to as string[] | undefined)?.join(", ") || "?"}`;
  }
}

export default function MonitoringSettingsPage() {
  const { can } = useAuth();
  const canAdmin = can(PERM.SYSTEM_ADMIN);
  const settingsQ = useAsyncData(() =>
    api.get<SettingsOut>("/api/v1/settings")
  );
  const channelsQ = useAsyncData(() =>
    api.get<Page<NotificationChannel>>("/api/v1/notification-channels")
  );
  const logQ = useAsyncData(() =>
    api.get<Page<NotificationLogEntry>>("/api/v1/notification-log?limit=100")
  );
  const s = settingsQ.data;
  const [draft, setDraft] = useState<SettingsValues | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<NotificationChannel | null>(null);
  const [deleting, setDeleting] = useState<NotificationChannel | null>(null);
  const [testing, setTesting] = useState<number | null>(null);

  useEffect(() => {
    if (s) setDraft(s.values);
  }, [s]);

  const channels = channelsQ.data?.items ?? [];
  const log = logQ.data?.items ?? [];

  const set = <K extends Key>(k: K, v: SettingsValues[K]) =>
    setDraft((d) => (d ? { ...d, [k]: v } : d));
  const src = (k: Key) => s?.sources[k];
  const resetKey = async (k: Key) => {
    try {
      const out = await api.patch<SettingsOut>("/api/v1/settings", {
        [k]: null,
      });
      settingsQ.setData(out);
      setDraft(out.values);
      toast.success(`${k} reset to .env / default`);
    } catch (e) {
      toast.error("Reset failed", { description: String(e) });
    }
  };

  const dirty: Partial<SettingsValues> = {};
  const KEYS: Key[] = [
    "monitoring_enabled",
    "monitor_concurrency",
    "monitor_http_timeout",
    "notify_retention_days",
    "report_email_weekly",
  ];
  if (s && draft) {
    for (const k of KEYS) {
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
      settingsQ.setData(out);
      setDraft(out.values);
      toast.success("Monitoring settings saved", {
        description: "The monitor tick picks changes up within ~1 minute.",
      });
    } catch (e) {
      const f = (e as Error & { fields?: Record<string, string> }).fields;
      if (f) setErrors(f);
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const testChannel = async (c: NotificationChannel) => {
    setTesting(c.id);
    try {
      const out = await api.post<ChannelTestOut>(
        `/api/v1/notification-channels/${c.id}/test`,
        {}
      );
      if (out.ok) toast.success(`Test event sent to ${c.name}`);
      else
        toast.error(`Test to ${c.name} failed`, {
          description: out.error ?? "unknown error",
        });
      void logQ.reload();
    } catch (e) {
      toast.error("Test failed", { description: String(e) });
    } finally {
      setTesting(null);
    }
  };

  const doDelete = async () => {
    if (!deleting) return;
    try {
      await api.del(`/api/v1/notification-channels/${deleting.id}`);
      toast.success("Channel deleted");
      setDeleting(null);
      void channelsQ.reload();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const toggleChannel = async (c: NotificationChannel) => {
    try {
      await api.patch(`/api/v1/notification-channels/${c.id}`, {
        enabled: !c.enabled,
      });
      void channelsQ.reload();
    } catch (e) {
      toast.error("Update failed", { description: String(e) });
    }
  };

  if (!canAdmin) {
    return (
      <p className="text-sm text-muted-foreground">
        Notification channels and their secrets require the Administrator
        role.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">
          Monitoring <DocsLink slug="monitoring" />
        </h1>
        <p className="text-sm text-muted-foreground">
          Health checks run from the worker on a per-minute tick; transitions
          fan out to every enabled channel below. Secrets are stored
          encrypted and are write-only — the API never returns them.
        </p>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="flex items-center gap-2 text-base">
            <Send className="h-4 w-4" /> Notification channels
          </CardTitle>
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New channel
          </Button>
        </CardHeader>
        <CardContent>
          <AsyncPanel
            loading={channelsQ.loading}
            error={channelsQ.error}
            onRetry={channelsQ.reload}
            empty={channels.length === 0}
            emptyMessage="No channels yet — monitor transitions, cert warnings, scan failures and MAC mismatches go nowhere until one is added."
          >
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Kind</TableHead>
                  <TableHead>Config</TableHead>
                  <TableHead className="w-8">On</TableHead>
                  <TableHead className="w-28" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {channels.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell dir="auto" className="font-medium">
                      {c.name}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">{KIND_LABEL[c.kind]}</Badge>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {configSummary(c)}
                    </TableCell>
                    <TableCell>
                      <Switch
                        checked={c.enabled}
                        aria-label={`Enable ${c.name}`}
                        onCheckedChange={() => toggleChannel(c)}
                      />
                    </TableCell>
                    <TableCell>
                      <div className="flex justify-end gap-0.5">
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Test ${c.name}`}
                          title="Send test event"
                          disabled={testing === c.id}
                          onClick={() => testChannel(c)}
                        >
                          <Send className="h-3.5 w-3.5 text-cyan-400" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Edit ${c.name}`}
                          onClick={() => {
                            setEditing(c);
                            setDialogOpen(true);
                          }}
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Delete ${c.name}`}
                          onClick={() => setDeleting(c)}
                        >
                          <Trash2 className="h-3.5 w-3.5 text-rose-400" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </AsyncPanel>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Activity className="h-4 w-4" /> Check lane
          </CardTitle>
        </CardHeader>
        {draft && (
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <SettingField
              label="Monitoring enabled"
              hint="Master switch — off pauses the per-minute monitor tick entirely (checks never run, no events fire)."
              source={src("monitoring_enabled")}
              onReset={() => resetKey("monitoring_enabled")}
              error={errors.monitoring_enabled}
            >
              <Switch
                checked={draft.monitoring_enabled}
                onCheckedChange={(v) => set("monitoring_enabled", v)}
              />
            </SettingField>
            <SettingField
              label="Check concurrency"
              hint="Parallel probes inside one sweep job — the sweep itself is a single worker job, so this stays inside the max_jobs budget."
              source={src("monitor_concurrency")}
              onReset={() => resetKey("monitor_concurrency")}
              error={errors.monitor_concurrency}
            >
              <Input
                type="number"
                min={1}
                max={512}
                value={draft.monitor_concurrency}
                onChange={(e) =>
                  set("monitor_concurrency", Number(e.target.value) || 1)
                }
              />
            </SettingField>
            <SettingField
              label="HTTP check timeout (s)"
              hint="Per-request timeout for http checks; ping/tcp reuse the scanner's timeouts."
              source={src("monitor_http_timeout")}
              onReset={() => resetKey("monitor_http_timeout")}
              error={errors.monitor_http_timeout}
            >
              <Input
                type="number"
                step={0.5}
                min={0.5}
                max={30}
                value={draft.monitor_http_timeout}
                onChange={(e) =>
                  set("monitor_http_timeout", Number(e.target.value) || 5)
                }
              />
            </SettingField>
            <SettingField
              label="Notification log retention (days)"
              hint="0 = keep forever. Older notification_log rows are swept by the scheduler tick."
              source={src("notify_retention_days")}
              onReset={() => resetKey("notify_retention_days")}
              error={errors.notify_retention_days}
            >
              <Input
                type="number"
                min={0}
                max={3650}
                value={draft.notify_retention_days}
                onChange={(e) =>
                  set("notify_retention_days", Number(e.target.value) || 0)
                }
              />
            </SettingField>
            <SettingField
              label="Weekly report digest"
              hint="Off by default. Sends the /reports estate summary to every enabled channel once a week (text + link, no attachment)."
              source={src("report_email_weekly")}
              onReset={() => resetKey("report_email_weekly")}
              error={errors.report_email_weekly}
            >
              <Switch
                checked={draft.report_email_weekly}
                onCheckedChange={(v) => set("report_email_weekly", v)}
              />
            </SettingField>
          </CardContent>
        )}
        {draft && (
          <CardContent className="pt-0">
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
          </CardContent>
        )}
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Notification log</CardTitle>
        </CardHeader>
        <CardContent>
          <AsyncPanel
            loading={logQ.loading}
            error={logQ.error}
            onRetry={logQ.reload}
            empty={log.length === 0}
            emptyMessage="Nothing delivered (or attempted) yet."
          >
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>When</TableHead>
                  <TableHead>Channel</TableHead>
                  <TableHead>Event</TableHead>
                  <TableHead>Summary</TableHead>
                  <TableHead>Result</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {log.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="whitespace-nowrap text-muted-foreground">
                      {fmtTs(r.created_at)}
                    </TableCell>
                    <TableCell dir="auto">
                      {r.channel_name ??
                        (r.channel_id != null ? `#${r.channel_id}` : "—")}
                    </TableCell>
                    <TableCell className="font-mono text-xs">
                      {r.event_type}
                    </TableCell>
                    <TableCell
                      dir="auto"
                      className="max-w-72 truncate text-xs"
                      title={r.summary}
                    >
                      {r.summary}
                    </TableCell>
                    <TableCell>
                      {r.ok ? (
                        <Badge variant="default">sent</Badge>
                      ) : (
                        <Badge
                          variant="red"
                          title={r.error ?? "failed"}
                          className="cursor-help"
                        >
                          failed
                        </Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </AsyncPanel>
        </CardContent>
      </Card>

      <ChannelDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        channel={editing}
        onSaved={() => void channelsQ.reload()}
      />

      <Dialog
        open={deleting != null}
        onOpenChange={(o) => !o && setDeleting(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete {deleting?.name}?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Events keep firing to other enabled channels; this channel&apos;s
            log rows are kept with a null channel reference.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// ---------------------------------------------------------------------------

const EMPTY = {
  name: "",
  kind: "webhook" as ChannelKind,
  enabled: true,
  secret: "",
  webhook_method: "POST",
  smtp_host: "",
  smtp_port: "587",
  smtp_from: "",
  smtp_to: "",
  smtp_starttls: true,
  smtp_username: "",
  telegram_chat_id: "",
};

function ChannelDialog({
  open,
  onOpenChange,
  channel,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  channel: NotificationChannel | null;
  onSaved: () => void;
}) {
  const uid = useId();
  const [form, setForm] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!open) return;
    if (!channel) {
      setForm(EMPTY);
      return;
    }
    const cfg = channel.config ?? {};
    setForm({
      name: channel.name,
      kind: channel.kind,
      enabled: channel.enabled,
      secret: "", // write-only — server keeps the stored blob
      webhook_method: (cfg.method as string) ?? "POST",
      smtp_host: (cfg.host as string) ?? "",
      smtp_port: String(cfg.port ?? 587),
      smtp_from: (cfg.from as string) ?? "",
      smtp_to: ((cfg.to as string[]) ?? []).join(", "),
      smtp_starttls: (cfg.starttls as boolean) ?? true,
      smtp_username: (cfg.username as string) ?? "",
      telegram_chat_id: (cfg.chat_id as string) ?? "",
    });
  }, [open, channel]);

  const submit = async () => {
    const body: Record<string, unknown> = {
      name: form.name,
      kind: form.kind,
      enabled: form.enabled,
    };
    if (form.secret) body.secret = form.secret;
    if (form.kind === "webhook") body.webhook_method = form.webhook_method;
    if (form.kind === "telegram")
      body.telegram_chat_id = form.telegram_chat_id;
    if (form.kind === "smtp") {
      body.smtp_host = form.smtp_host;
      body.smtp_port = Number(form.smtp_port) || 587;
      body.smtp_from = form.smtp_from;
      body.smtp_to = form.smtp_to
        .split(",")
        .map((x) => x.trim())
        .filter(Boolean);
      body.smtp_starttls = form.smtp_starttls;
      if (form.smtp_username) body.smtp_username = form.smtp_username;
    }
    setBusy(true);
    try {
      if (channel) {
        await api.patch(
          `/api/v1/notification-channels/${channel.id}`,
          body
        );
        toast.success("Channel updated");
      } else {
        await api.post("/api/v1/notification-channels", body);
        toast.success("Channel created");
      }
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  // webhook/discord/telegram can't work without their URL/token; smtp's
  // password is optional (unauthenticated relay).
  const secretRequired =
    form.kind !== "smtp" && !channel?.secret_set && !form.secret;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {channel ? `Edit ${channel.name}` : "New channel"}
          </DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-[1fr_10rem] gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-name`}>Name</Label>
              <Input
                id={`${uid}-name`}
                dir="auto"
                placeholder="ops-webhook, noc-mail…"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label id={`${uid}-kind`}>Kind</Label>
              <Select
                value={form.kind}
                onValueChange={(v) =>
                  setForm({ ...form, kind: v as ChannelKind })
                }
              >
                <SelectTrigger aria-label="Channel kind">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(Object.keys(KIND_LABEL) as ChannelKind[]).map((k) => (
                    <SelectItem key={k} value={k}>
                      {KIND_LABEL[k]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {(form.kind === "webhook" || form.kind === "discord") && (
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-secret`}>
                {KIND_SECRET_HINT[form.kind]}
                {channel?.secret_set && (
                  <Badge variant="secondary" className="ml-2">
                    configured
                  </Badge>
                )}
              </Label>
              <Input
                id={`${uid}-secret`}
                type="password"
                dir="ltr"
                autoComplete="new-password"
                placeholder={
                  channel?.secret_set
                    ? "••• stored — type to replace"
                    : "https://…"
                }
                value={form.secret}
                onChange={(e) => setForm({ ...form, secret: e.target.value })}
              />
            </div>
          )}
          {form.kind === "webhook" && (
            <div className="grid gap-1.5">
              <Label id={`${uid}-method`}>HTTP method</Label>
              <Select
                value={form.webhook_method}
                onValueChange={(v) =>
                  setForm({ ...form, webhook_method: v })
                }
              >
                <SelectTrigger className="w-32" aria-label="HTTP method">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="POST">POST</SelectItem>
                  <SelectItem value="PUT">PUT</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {form.kind === "telegram" && (
            <div className="grid gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-secret`}>
                  {KIND_SECRET_HINT.telegram}
                  {channel?.secret_set && (
                    <Badge variant="secondary" className="ml-2">
                      configured
                    </Badge>
                  )}
                </Label>
                <Input
                  id={`${uid}-secret`}
                  type="password"
                  dir="ltr"
                  autoComplete="new-password"
                  placeholder={
                    channel?.secret_set ? "••• stored — type to replace" : ""
                  }
                  value={form.secret}
                  onChange={(e) =>
                    setForm({ ...form, secret: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-chat`}>Chat ID</Label>
                <Input
                  id={`${uid}-chat`}
                  dir="ltr"
                  className="font-mono text-sm"
                  placeholder="-1001234567890 or @channel"
                  value={form.telegram_chat_id}
                  onChange={(e) =>
                    setForm({ ...form, telegram_chat_id: e.target.value })
                  }
                />
              </div>
            </div>
          )}

          {form.kind === "smtp" && (
            <div className="grid gap-3">
              <div className="grid grid-cols-[1fr_6rem] gap-3">
                <div className="grid gap-1.5">
                  <Label htmlFor={`${uid}-host`}>SMTP host</Label>
                  <Input
                    id={`${uid}-host`}
                    dir="ltr"
                    className="font-mono text-sm"
                    placeholder="smtp.example.com"
                    value={form.smtp_host}
                    onChange={(e) =>
                      setForm({ ...form, smtp_host: e.target.value })
                    }
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor={`${uid}-port`}>Port</Label>
                  <Input
                    id={`${uid}-port`}
                    type="number"
                    value={form.smtp_port}
                    onChange={(e) =>
                      setForm({ ...form, smtp_port: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label htmlFor={`${uid}-from`}>From</Label>
                  <Input
                    id={`${uid}-from`}
                    dir="ltr"
                    placeholder="ipambox@example.com"
                    value={form.smtp_from}
                    onChange={(e) =>
                      setForm({ ...form, smtp_from: e.target.value })
                    }
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor={`${uid}-to`}>To (comma-separated)</Label>
                  <Input
                    id={`${uid}-to`}
                    dir="ltr"
                    placeholder="noc@example.com, oncall@…"
                    value={form.smtp_to}
                    onChange={(e) =>
                      setForm({ ...form, smtp_to: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label htmlFor={`${uid}-user`}>Username (optional)</Label>
                  <Input
                    id={`${uid}-user`}
                    dir="ltr"
                    autoComplete="off"
                    value={form.smtp_username}
                    onChange={(e) =>
                      setForm({ ...form, smtp_username: e.target.value })
                    }
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label id={`${uid}-tls`}>STARTTLS</Label>
                  <Switch
                    aria-label="STARTTLS"
                    checked={form.smtp_starttls}
                    onCheckedChange={(v) =>
                      setForm({ ...form, smtp_starttls: v })
                    }
                  />
                </div>
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-secret`}>
                  {KIND_SECRET_HINT.smtp}
                  {channel?.secret_set && (
                    <Badge variant="secondary" className="ml-2">
                      configured
                    </Badge>
                  )}
                </Label>
                <Input
                  id={`${uid}-secret`}
                  type="password"
                  dir="ltr"
                  autoComplete="new-password"
                  placeholder={
                    channel?.secret_set ? "••• stored — type to replace" : ""
                  }
                  value={form.secret}
                  onChange={(e) =>
                    setForm({ ...form, secret: e.target.value })
                  }
                />
              </div>
            </div>
          )}

          <div className="flex items-center gap-2">
            <Switch
              aria-label="Enabled"
              checked={form.enabled}
              onCheckedChange={(v) => setForm({ ...form, enabled: v })}
            />
            <Label>Enabled</Label>
          </div>
        </div>
        <DialogFooter>
          <Button
            onClick={submit}
            disabled={busy || !form.name || secretRequired}
          >
            {busy ? "Saving…" : channel ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
