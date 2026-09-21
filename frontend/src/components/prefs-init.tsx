"use client";

import { useEffect, useState } from "react";
import { Toaster } from "sonner";

import { THEMES, useApplyPrefs } from "@/lib/prefs";

/** Applies localStorage prefs to <html> live, and themes the toaster. */
export function PrefsInit() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  useApplyPrefs();

  useEffect(() => {
    const sync = () =>
      setTheme(
        THEMES.find(
          (t) => t.value === document.documentElement.dataset.theme
        )?.mode ?? "dark"
      );
    sync();
    // Watch data-theme rather than the prefs event — it flips for both pref
    // changes and system-theme (prefers-color-scheme) changes.
    const mo = new MutationObserver(sync);
    mo.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    return () => mo.disconnect();
  }, []);

  return <Toaster theme={theme} position="bottom-right" />;
}
