"use client";

import { useCallback, useEffect, useState } from "react";
import { KeyRound, MonitorSmartphone, Plus, ShieldAlert, Trash2, Users } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { fmtTs } from "@/lib/prefs";
import type { AuthStatus, SessionOut, UserOut } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
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
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [users, setUsers] = useState<UserOut[]>([]);
  const [sessions, setSessions] = useState<SessionOut[]>([]);
  const [addOpen, setAddOpen] = useState(false);
  const [newUser, setNewUser] = useState({ username: "", password: "" });
  const [pw, setPw] = useState({ current: "", next: "", logout: true });
  const [pwBusy, setPwBusy] = useState(false);

  const refresh = useCallback(() => {
    api.get<AuthStatus>("/api/v1/auth/status").then(setAuth).catch(() => {});
    api.get<UserOut[]>("/api/v1/users").then(setUsers).catch(() => {});
    api
      .get<SessionOut[]>("/api/v1/auth/sessions")
      .then(setSessions)
      .catch(() => {});
  }, []);

  useEffect(refresh, [refresh]);

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

  const addUser = async () => {
    try {
      await api.post("/api/v1/users", newUser);
      toast.success(`User "${newUser.username}" created`);
      setAddOpen(false);
      setNewUser({ username: "", password: "" });
      refresh();
    } catch (e) {
      toast.error("Create failed", { description: String(e) });
    }
  };

  const deleteUser = async (u: UserOut) => {
    try {
      await api.del(`/api/v1/users/${u.id}`);
      toast.success(`User "${u.username}" deleted`);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  const resetPassword = async (u: UserOut) => {
    const next = window.prompt(`New password for ${u.username} (min 8 chars):`);
    if (!next) return;
    try {
      await api.patch(`/api/v1/users/${u.id}`, { password: next });
      toast.success(`Password reset for "${u.username}"`);
    } catch (e) {
      toast.error("Reset failed", { description: String(e) });
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
          Manage login accounts and active sessions. All users are full admins.
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
              <Label>Current password</Label>
              <Input
                type="password"
                autoComplete="current-password"
                value={pw.current}
                onChange={(e) => setPw({ ...pw, current: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>New password (min 8 chars)</Label>
              <Input
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
            <Users className="h-4 w-4" /> Users
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Username</TableHead>
                  <TableHead className="w-44">Created</TableHead>
                  <TableHead className="w-40 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((u) => (
                  <TableRow key={u.id}>
                    <TableCell className="font-medium">
                      {u.username}
                      {auth?.username === u.username && (
                        <Badge variant="outline" className="ml-2 text-[10px]">
                          you
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {fmtTs(u.created_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Reset password"
                        onClick={() => resetPassword(u)}
                      >
                        <KeyRound className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Delete user"
                        disabled={auth?.username === u.username}
                        onClick={() => deleteUser(u)}
                      >
                        <Trash2 className="h-4 w-4 text-rose-400" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <Button size="sm" variant="outline" onClick={() => setAddOpen(true)}>
            <Plus /> Add user
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
          {sessions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No sessions found.</p>
          ) : (
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
          )}
          {sessions.some((s) => !s.current) && (
            <Button size="sm" variant="outline" onClick={revokeOthers}>
              Sign out all other sessions
            </Button>
          )}
        </CardContent>
      </Card>

      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add user</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <div className="grid gap-1.5">
              <Label>Username</Label>
              <Input
                value={newUser.username}
                onChange={(e) =>
                  setNewUser({ ...newUser, username: e.target.value })
                }
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Password (min 8 chars)</Label>
              <Input
                type="password"
                autoComplete="new-password"
                value={newUser.password}
                onChange={(e) =>
                  setNewUser({ ...newUser, password: e.target.value })
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              size="sm"
              disabled={!newUser.username || newUser.password.length < 8}
              onClick={addUser}
            >
              Create user
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
