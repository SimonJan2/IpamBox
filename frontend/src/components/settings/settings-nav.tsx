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
} from "lucide-react";

import { cn } from "@/lib/utils";

export const SETTINGS_SECTIONS = [
  { href: "/settings", label: "General", icon: Info },
  { href: "/settings/scanning", label: "Scanning", icon: Radar },
  { href: "/settings/backup", label: "Backup & Restore", icon: FileArchive },
  { href: "/settings/security", label: "Account & Security", icon: ShieldCheck },
  { href: "/settings/appearance", label: "Appearance", icon: Palette },
  { href: "/settings/data", label: "Data & Maintenance", icon: DatabaseZap },
];

export function SettingsNav() {
  const pathname = usePathname();
  return (
    <nav className="flex w-48 shrink-0 flex-col gap-0.5 overflow-x-auto lg:sticky lg:top-20">
      {SETTINGS_SECTIONS.map((item) => {
        const active =
          item.href === "/settings"
            ? pathname === "/settings"
            : pathname.startsWith(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-2.5 rounded-md px-3 py-1.5 text-sm transition-colors",
              active
                ? "bg-emerald-500/10 text-emerald-400"
                : "text-muted-foreground hover:bg-accent hover:text-foreground"
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
