"use client";

import { useEffect, useId, useMemo, useState } from "react";
import {
  Pencil,
  Plus,
  Search,
  ShieldAlert,
  ShieldCheck,
  Trash2,
  UserPlus,
  Users,
} from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { fmtTs } from "@/lib/prefs";
import { useAuth } from "@/lib/auth";
import { PERM, ROLE_META, ROLE_ORDER } from "@/lib/permissions";
import type { RoleName, UserOut } from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function RoleBadge({ role }: { role: RoleName }) {
  const meta = ROLE_META[role];
  return (
    <Badge variant="outline" className={meta.badgeClass}>
      {meta.tier}
    </Badge>
  );
}

function UserDialog({
  user,
  onOpenChange,
  onSaved,
}: {
  user: UserOut | null | "new";
  onOpenChange: (o: boolean) => void;
  onSaved: () => void;
}) {
  const target = user === "new" ? null : user;
  const editing = target !== null;
  const [form, setForm] = useState({
    username: "",
    password: "",
    role: "viewer" as RoleName,
  });
  const [busy, setBusy] = useState(false);
  const uid = useId();

  useEffect(() => {
    if (user !== null) {
      setForm({
        username: target?.username ?? "",
        password: "",
        role: target?.role ?? "viewer",
      });
    }
  }, [user, target]);

  const submit = async () => {
    setBusy(true);
    try {
      if (target) {
        await api.patch(`/api/v1/users/${target.id}`, {
          username: form.username,
          role: form.role,
          ...(form.password ? { password: form.password } : {}),
        });
        toast.success(`Updated ${form.username}`);
      } else {
        await api.post("/api/v1/users", {
          username: form.username,
          password: form.password,
          role: form.role,
        });
        toast.success(`Created ${form.username}`, {
          description: "Share the temporary password — they can change it under Account & Security.",
        });
      }
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const valid =
    form.username.trim().length > 0 &&
    (editing ? form.password === "" || form.password.length >= 8 : form.password.length >= 8);

  return (
    <Dialog open={user !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{target ? `Edit ${target.username}` : "New user"}</DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-username`}>Username</Label>
            <Input
              id={`${uid}-username`}
              autoComplete="off"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-password`}>
              {editing ? "New password (leave blank to keep)" : "Temporary password"}
            </Label>
            <Input
              id={`${uid}-password`}
              type="password"
              autoComplete="new-password"
              placeholder={editing ? "unchanged" : "min 8 characters"}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            {editing && form.password && (
              <p className="text-xs text-muted-foreground">
                Setting a new password signs this user out everywhere.
              </p>
            )}
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-role`}>Role</Label>
            <Select
              value={form.role}
              onValueChange={(v) => setForm({ ...form, role: v as RoleName })}
            >
              <SelectTrigger id={`${uid}-role`}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ROLE_ORDER.map((r) => (
                  <SelectItem key={r} value={r}>
                    {ROLE_META[r].label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {ROLE_META[form.role].summary}
            </p>
          </div>
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !valid}>
            {busy ? "Saving…" : editing ? "Save" : "Create user"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DeleteUserDialog({
  user,
  onOpenChange,
  onDeleted,
}: {
  user: UserOut | null;
  onOpenChange: (o: boolean) => void;
  onDeleted: () => void;
}) {
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!user) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/users/${user.id}`);
      toast.success(`Deleted ${user.username}`);
      onOpenChange(false);
      onDeleted();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={user !== null} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete user</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Delete <span className="font-medium text-foreground">{user?.username}</span>?
          Their sessions are revoked immediately. This cannot be undone.
        </p>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={submit} disabled={busy}>
            {busy ? "Deleting…" : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function UsersPage() {
  const { status, can } = useAuth();
  const usersQ = useAsyncData(async () =>
    can(PERM.USERS_MANAGE) ? api.get<UserOut[]>("/api/v1/users") : []
  );
  const [q, setQ] = useState("");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [editing, setEditing] = useState<UserOut | "new" | null>(null);
  const [deleting, setDeleting] = useState<UserOut | null>(null);

  const users = usersQ.data ?? [];
  const refresh = () => void usersQ.reload();

  const counts = useMemo(() => {
    const c = { total: users.length } as Record<string, number>;
    for (const r of ROLE_ORDER) c[r] = 0;
    for (const u of users) c[u.role] = (c[u.role] ?? 0) + 1;
    return c;
  }, [users]);

  const adminCount = counts["admin"] ?? 0;

  const filtered = useMemo(() => {
    const ql = q.trim().toLowerCase();
    return users.filter((u) => {
      if (ql && !u.username.toLowerCase().includes(ql)) return false;
      if (roleFilter !== "all" && u.role !== roleFilter) return false;
      return true;
    });
  }, [users, q, roleFilter]);

  if (!can(PERM.USERS_MANAGE)) {
    return (
      <div className="space-y-6">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">Users &amp; Roles <DocsLink slug="settings" /></h1>
        <Card className="border-amber-500/30">
          <CardContent className="flex items-start gap-3 pt-6 text-sm text-muted-foreground">
            <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
            User administration requires the Administrator role.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-1.5 text-xl font-semibold">Users &amp; Roles <DocsLink slug="settings" /></h1>
          <p className="text-sm text-muted-foreground">
            Accounts, role assignments and access tiers.
          </p>
        </div>
        <Button size="sm" onClick={() => setEditing("new")}>
          <UserPlus /> New user
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Users className="h-3.5 w-3.5" /> Total users
            </div>
            <div className="mt-1 text-2xl font-semibold">{counts.total}</div>
          </CardContent>
        </Card>
        {ROLE_ORDER.map((r) => (
          <Card key={r}>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <ShieldCheck className="h-3.5 w-3.5" /> {ROLE_META[r].tier}
              </div>
              <div className="mt-1 text-2xl font-semibold">{counts[r]}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="flex gap-3">
        <div className="relative max-w-xs flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search users…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="pl-8"
          />
        </div>
        <Select value={roleFilter} onValueChange={setRoleFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All roles" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All roles</SelectItem>
            {ROLE_ORDER.map((r) => (
              <SelectItem key={r} value={r}>
                {ROLE_META[r].label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={usersQ.loading}
          error={usersQ.error}
          onRetry={usersQ.reload}
          empty={users.length === 0}
          emptyMessage="No users yet."
        >
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Username</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Access</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((u) => {
              const isSelf = status?.username === u.username;
              const soleAdmin = u.role === "admin" && adminCount <= 1;
              return (
                <TableRow key={u.id}>
                  <TableCell className="font-medium">
                    {u.username}
                    {isSelf && (
                      <Badge
                        variant="outline"
                        className="ml-2 border-emerald-500/40 text-[10px] text-emerald-400"
                      >
                        you
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <RoleBadge role={u.role} />
                  </TableCell>
                  <TableCell className="max-w-72 truncate text-xs text-muted-foreground">
                    {ROLE_META[u.role].summary}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {fmtTs(u.created_at)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Edit user ${u.username}`}
                        title="Edit user"
                        onClick={() => setEditing(u)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      {!isSelf && (
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={
                            soleAdmin
                              ? "Cannot delete the only administrator"
                              : `Delete user ${u.username}`
                          }
                          title={soleAdmin ? "Cannot delete the only administrator" : "Delete user"}
                          onClick={() => setDeleting(u)}
                        >
                          <Trash2 className="h-4 w-4 text-rose-400" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
            {filtered.length === 0 && users.length > 0 && (
              <TableRow>
                <TableCell colSpan={5} className="py-10 text-center text-muted-foreground">
                  No users match the filters.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        </AsyncPanel>
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Role reference</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2">
          {ROLE_ORDER.map((r) => (
            <div key={r} className="flex items-start gap-3 rounded-md border p-3">
              <RoleBadge role={r} />
              <p className="text-xs text-muted-foreground">{ROLE_META[r].summary}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <UserDialog user={editing} onOpenChange={(o) => !o && setEditing(null)} onSaved={refresh} />
      <DeleteUserDialog
        user={deleting}
        onOpenChange={(o) => !o && setDeleting(null)}
        onDeleted={refresh}
      />
    </div>
  );
}
