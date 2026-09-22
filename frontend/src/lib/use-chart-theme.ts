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

// Pre-mount placeholder — replaced on first effect. Nightwire values so
// SSR/first paint can't flash mismatched chrome on the default theme.
const FALLBACK: ChartTheme = {
  axis: "hsl(187 7% 51%)",
  cursor: "hsl(180 8% 92% / 0.05)",
  tooltipBg: "hsl(213 22% 7%)",
  tooltipBorder: "hsl(213 21% 14%)",
  tooltipText: "hsl(180 8% 92%)",
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
