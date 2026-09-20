"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  DatabaseZap,
  FileArchive,
  Info,
  Palette,
  Radar,
  ShieldCheck,
  SlidersHorizontal,
  Users,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";

export const SETTINGS_SECTIONS = [
  { href: "/settings", label: "General", icon: Info, perm: PERM.DATA_READ },
  { href: "/settings/features", label: "Features", icon: SlidersHorizontal, perm: PERM.DATA_READ },
  { href: "/settings/scanning", label: "Scanning", icon: Radar, perm: PERM.DATA_READ },
  { href: "/settings/backup", label: "Backup & Restore", icon: FileArchive, perm: PERM.BACKUP_ACCESS },
  { href: "/settings/security", label: "Account & Security", icon: ShieldCheck, perm: PERM.DATA_READ },
  { href: "/settings/users", label: "Users & Roles", icon: Users, perm: PERM.USERS_MANAGE },
  { href: "/settings/appearance", label: "Appearance", icon: Palette, perm: PERM.DATA_READ },
  { href: "/settings/data", label: "Data & Maintenance", icon: DatabaseZap, perm: PERM.DATA_READ },
];

export function SettingsNav() {
  const pathname = usePathname();
  const { can } = useAuth();
  return (
    <nav className="flex w-48 shrink-0 flex-col gap-0.5 overflow-x-auto lg:sticky lg:top-20">
      {SETTINGS_SECTIONS.filter((item) => can(item.perm)).map((item) => {
        const active =
          item.href === "/settings"
            ? pathname === "/settings"
            : pathname.startsWith(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex items-center gap-2.5 rounded-md border-l-2 px-3 py-1.5 text-sm transition-colors",
              active
                ? "border-emerald-400 bg-emerald-500/10 font-semibold text-emerald-400"
                : "border-transparent text-muted-foreground hover:bg-accent hover:text-foreground"
            )}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
