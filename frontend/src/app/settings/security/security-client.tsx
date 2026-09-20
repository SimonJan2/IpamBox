"use client";

import { useId, useState } from "react";
import { KeyRound, MonitorSmartphone, ShieldAlert, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { fmtTs } from "@/lib/prefs";
import { useAuth } from "@/lib/auth";
import { ROLE_META } from "@/lib/permissions";
import type { SessionOut } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function fmtAgo(seconds: number | null): string {
  if (seconds == null) return "—";
  if (seconds < 120) return `${seconds}s`;
  if (seconds < 7200) return `${Math.round(seconds / 60)}m`;
  if (seconds < 172800) return `${Math.round(seconds / 3600)}h`;
  return `${Math.round(seconds / 86400)}d`;
}

export default function SecurityPage() {
  const { status: auth } = useAuth();
  const sessionsQ = useAsyncData(() =>
    api.get<SessionOut[]>("/api/v1/auth/sessions")
  );
  const [pw, setPw] = useState({ current: "", next: "", logout: true });
  const [pwBusy, setPwBusy] = useState(false);
  const uid = useId();

  const sessions = sessionsQ.data ?? [];
  const refresh = () => void sessionsQ.reload();

  const changePassword = async () => {
    setPwBusy(true);
    try {
      await api.post("/api/v1/auth/change-password", {
        current_password: pw.current,
        new_password: pw.next,
        logout_others: pw.logout,
      });
      toast.success("Password changed", {
        description: pw.logout ? "Other sessions were signed out." : undefined,
      });
      setPw({ current: "", next: "", logout: true });
      refresh();
    } catch (e) {
      toast.error("Password change failed", { description: String(e) });
    } finally {
      setPwBusy(false);
    }
  };

  const revoke = async (id: string) => {
    try {
      await api.del(`/api/v1/auth/sessions/${id}`);
      refresh();
    } catch (e) {
      toast.error("Revoke failed", { description: String(e) });
    }
  };

  const revokeOthers = async () => {
    try {
      const r = await api.post<{ revoked_sessions: number }>(
        "/api/v1/auth/sessions/revoke-others"
      );
      toast.success(`Signed out ${r.revoked_sessions} other session(s)`);
      refresh();
    } catch (e) {
      toast.error("Failed", { description: String(e) });
    }
  };

  if (auth?.allow_insecure) {
    return (
      <div className="space-y-6">
        <h1 className="text-xl font-semibold">Account &amp; Security</h1>
        <Card className="border-amber-500/30">
          <CardContent className="flex items-start gap-3 pt-6 text-sm text-muted-foreground">
            <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
            Authentication is disabled (<code>IPAMBOX_ALLOW_INSECURE=true</code>).
            Accounts, passwords and sessions are managed by your reverse proxy.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Account &amp; Security</h1>
        <p className="text-sm text-muted-foreground">
          Your password and active sessions.
          {auth?.role && (
            <>
              {" "}
              You are signed in as{" "}
              <Badge
                variant="outline"
                className={ROLE_META[auth.role].badgeClass}
              >
                {ROLE_META[auth.role].label}
              </Badge>
              .
            </>
          )}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <KeyRound className="h-4 w-4" /> Change your password
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-current`}>Current password</Label>
              <Input
                id={`${uid}-current`}
                type="password"
                autoComplete="current-password"
                value={pw.current}
                onChange={(e) => setPw({ ...pw, current: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-next`}>New password (min 8 chars)</Label>
              <Input
                id={`${uid}-next`}
                type="password"
                autoComplete="new-password"
                value={pw.next}
                onChange={(e) => setPw({ ...pw, next: e.target.value })}
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <Checkbox
              checked={pw.logout}
              onCheckedChange={(v) => setPw({ ...pw, logout: v })}
              aria-label="Sign out all other sessions"
            />
            Sign out all other sessions
          </label>
          <Button
            size="sm"
            disabled={pwBusy || !pw.current || pw.next.length < 8}
            onClick={changePassword}
          >
            {pwBusy ? "Changing…" : "Change password"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <MonitorSmartphone className="h-4 w-4" /> Active sessions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <AsyncPanel
            loading={sessionsQ.loading}
            error={sessionsQ.error}
            onRetry={sessionsQ.reload}
            empty={sessions.length === 0}
            emptyMessage="No sessions found."
          >
            <div className="rounded-lg border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Session</TableHead>
                    <TableHead>IP</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Expires in</TableHead>
                    <TableHead className="w-20 text-right"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessions.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell className="font-mono text-xs">
                        …{s.id}
                        {s.current && (
                          <Badge
                            variant="outline"
                            className="ml-2 border-emerald-500/40 text-[10px] text-emerald-400"
                          >
                            this session
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        {s.ip ?? "—"}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {fmtTs(s.created_at)}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {fmtAgo(s.expires_in)}
                      </TableCell>
                      <TableCell className="text-right">
                        {!s.current && (
                          <Button
                            variant="ghost"
                            size="icon"
                            aria-label={`Revoke session ${s.id}`}
                            title="Revoke"
                            onClick={() => revoke(s.id)}
                          >
                            <Trash2 className="h-4 w-4 text-rose-400" />
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </AsyncPanel>
          {sessions.some((s) => !s.current) && (
            <Button size="sm" variant="outline" onClick={revokeOthers}>
              Sign out all other sessions
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
