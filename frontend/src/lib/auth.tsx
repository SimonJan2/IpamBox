"use client";

import { createContext, useContext } from "react";

import type { AuthStatus, RoleName } from "@/types";
import { PERM } from "@/lib/permissions";

export interface AuthCtx {
  status: AuthStatus | null;
  role: RoleName | null;
  /** True when the session holds the given permission (always true in
   * allow_insecure mode — the backend returns the full set). */
  can: (perm: string) => boolean;
  isAdmin: boolean;
}

const FALLBACK: AuthCtx = {
  status: null,
  role: null,
  can: () => false,
  isAdmin: false,
};

const AuthContext = createContext<AuthCtx>(FALLBACK);

export const AuthProvider = AuthContext.Provider;

export function useAuth(): AuthCtx {
  return useContext(AuthContext);
}

export function authCtxValue(status: AuthStatus | null): AuthCtx {
  const perms = new Set(status?.permissions ?? []);
  return {
    status,
    role: status?.role ?? null,
    can: (perm) => Boolean(status?.allow_insecure) || perms.has(perm),
    isAdmin:
      Boolean(status?.allow_insecure) || perms.has(PERM.USERS_MANAGE),
  };
}
