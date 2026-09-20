"use client";

import { useEffect, useState } from "react";

/**
 * Recharts needs concrete color values (not classes), so we resolve the
 * theme's CSS variables through getComputedStyle. A MutationObserver on
 * <html data-theme> re-resolves whenever the theme flips — no reload needed.
 */
export interface ChartTheme {
  axis: string;
  cursor: string;
  tooltipBg: string;
  tooltipBorder: string;
  tooltipText: string;
}

// Pre-mount placeholder — replaced on first effect. Dark values so SSR/first
// paint can't flash light-theme chrome on the (default) dark theme.
const FALLBACK: ChartTheme = {
  axis: "hsl(240 5% 64.9%)",
  cursor: "hsl(0 0% 98% / 0.05)",
  tooltipBg: "hsl(240 10% 5.5%)",
  tooltipBorder: "hsl(240 3.7% 15.9%)",
  tooltipText: "hsl(0 0% 98%)",
};

function readTheme(): ChartTheme {
  const s = getComputedStyle(document.documentElement);
  const v = (name: string) => s.getPropertyValue(name).trim();
  return {
    axis: `hsl(${v("--muted-foreground")})`,
    cursor: `hsl(${v("--foreground")} / 0.05)`,
    tooltipBg: `hsl(${v("--card")})`,
    tooltipBorder: `hsl(${v("--border")})`,
    tooltipText: `hsl(${v("--card-foreground")})`,
  };
}

export function useChartTheme(): ChartTheme {
  const [theme, setTheme] = useState<ChartTheme>(FALLBACK);

  useEffect(() => {
    const update = () => setTheme(readTheme());
    update();
    const mo = new MutationObserver(update);
    mo.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    return () => mo.disconnect();
  }, []);

  return theme;
}
