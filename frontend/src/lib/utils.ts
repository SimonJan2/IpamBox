import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function ipToInt(ip: string): number {
  return ip.split(".").reduce((acc, o) => (acc << 8) + parseInt(o, 10), 0) >>> 0;
}

export function intToIp(n: number): string {
  return [(n >>> 24) & 255, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join(".");
}

export function timeAgo(iso: string | null): string {
  if (!iso) return "never";
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return `${Math.floor(s)}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

// Hebrew final letters -> regular form, so search treats םןץףך == מנצפכ.
// Mirrors backend fold_hebrew.
const HE_FINALS: Record<string, string> = {
  "ם": "מ",
  "ן": "נ",
  "ץ": "צ",
  "ף": "פ",
  "ך": "כ",
};

export function foldHebrew(s: string): string {
  return s.replace(/[םןץףך]/g, (c) => HE_FINALS[c] ?? c);
}

// Mirrors backend slugify (app/services/ipam.py): NFKC + lowercase,
// non-word runs -> "-", keeps Hebrew letters; "site" when empty.
export function slugify(name: string): string {
  const slug = name
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}_]+/gu, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "site";
}
