"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen } from "lucide-react";

import { cn } from "@/lib/utils";
import { DOC_ARTICLES, DOC_CATEGORIES, docHref } from "@/lib/docs";

export function DocsNav() {
  const pathname = usePathname();
  const linkCls = (active: boolean) =>
    cn(
      "flex items-center gap-2.5 rounded-md border-l-2 px-3 py-1.5 text-sm transition-colors",
      active
        ? "border-emerald-400 bg-emerald-500/10 font-semibold text-emerald-400"
        : "border-transparent text-muted-foreground hover:bg-accent hover:text-foreground"
    );
  return (
    <nav className="flex w-52 shrink-0 flex-col gap-3 overflow-x-auto pb-2 lg:sticky lg:top-20 lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto">
      <Link href="/docs" aria-current={pathname === "/docs" ? "page" : undefined} className={linkCls(pathname === "/docs")}>
        <BookOpen className="h-4 w-4 shrink-0" />
        All guides
      </Link>
      {DOC_CATEGORIES.map((cat) => {
        const articles = DOC_ARTICLES.filter((a) => a.category === cat.key);
        if (!articles.length) return null;
        return (
          <div key={cat.key}>
            <div className="px-3 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
              {cat.label}
            </div>
            <div className="flex flex-col gap-0.5">
              {articles.map((a) => {
                const href = docHref(a.slug);
                const active = pathname === href;
                return (
                  <Link
                    key={a.slug}
                    href={href}
                    aria-current={active ? "page" : undefined}
                    className={linkCls(active)}
                  >
                    <a.icon className="h-4 w-4 shrink-0" />
                    {a.title}
                  </Link>
                );
              })}
            </div>
          </div>
        );
      })}
    </nav>
  );
}
