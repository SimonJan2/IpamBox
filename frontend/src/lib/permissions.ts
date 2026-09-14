import type { RoleName } from "@/types";

// Mirrors ROLE_PERMISSIONS in backend/app/core/deps.py — the backend is the
// authority; these strings are only for hiding UI affordances.
export const PERM = {
  DATA_READ: "data:read",
  DATA_WRITE: "data:write",
  DATA_DELETE: "data:delete",
  BACKUP_ACCESS: "backup:access",
  SYSTEM_ADMIN: "system:admin",
  USERS_MANAGE: "users:manage",
} as const;

export const ROLE_ORDER: RoleName[] = [
  "admin",
  "operator",
  "contributor",
  "viewer",
];

export const ROLE_META: Record<
  RoleName,
  { label: string; tier: string; badgeClass: string; summary: string }
> = {
  admin: {
    label: "Administrator",
    tier: "Admin",
    badgeClass: "border-rose-500/40 text-rose-400",
    summary:
      "Full access — manage users and roles, system settings, backups, and all data including deletions.",
  },
  operator: {
    label: "Tier-1 · Operator",
    tier: "Tier-1",
    badgeClass: "border-amber-500/40 text-amber-400",
    summary:
      "Can add, edit and delete data, and trigger/download backups. Cannot manage users or change system settings.",
  },
  contributor: {
    label: "Tier-2 · Contributor",
    tier: "Tier-2",
    badgeClass: "border-sky-500/40 text-sky-400",
    summary:
      "Can view, add and edit data. Cannot delete anything, trigger backups, or manage users.",
  },
  viewer: {
    label: "Tier-3 · Viewer",
    tier: "Tier-3",
    badgeClass: "border-emerald-500/40 text-emerald-400",
    summary:
      "Read-only access to data and reports. Cannot create, edit or delete anything.",
  },
};
