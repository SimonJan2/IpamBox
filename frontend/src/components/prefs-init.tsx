"use client";

import { useEffect, useState } from "react";
import { Toaster } from "sonner";

import { useApplyPrefs } from "@/lib/prefs";

/** Applies localStorage prefs to <html> live, and themes the toaster. */
export function PrefsInit() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  useApplyPrefs();

  useEffect(() => {
    const sync = () =>
      setTheme(
        document.documentElement.dataset.theme === "light" ? "light" : "dark"
      );
    sync();
    window.addEventListener("ipam:prefs-changed", sync);
    return () => window.removeEventListener("ipam:prefs-changed", sync);
  }, []);

  return <Toaster theme={theme} position="bottom-right" />;
}
