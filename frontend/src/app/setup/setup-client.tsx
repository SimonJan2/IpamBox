"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Network } from "lucide-react";

import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SetupPage() {
  const router = useRouter();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.post("/api/v1/auth/setup", { username, password });
      router.replace("/");
    } catch (err) {
      setError(String(err).replace(/^\d+:\s*/, ""));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <Card className="w-full max-w-sm">
        <CardHeader className="items-center space-y-3">
          <Network className="h-8 w-8 text-emerald-400" />
          <CardTitle>Welcome to IpamBox</CardTitle>
          <p className="text-center text-sm text-muted-foreground">
            Create an admin password to finish setup. Nothing else is reachable
            until you do.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={submit} className="grid gap-4">
            <div className="grid gap-1.5">
              <Label>Username</Label>
              <Input
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Password</Label>
              <Input
                type="password"
                autoComplete="new-password"
                autoFocus
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Confirm password</Label>
              <Input
                type="password"
                autoComplete="new-password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            </div>
            {error && <p className="text-sm text-rose-400">{error}</p>}
            <Button
              type="submit"
              disabled={busy || !username || password.length < 8 || !confirm}
            >
              {busy ? "Creating…" : "Create password"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
