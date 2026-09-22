import type { Metadata, Viewport } from "next";

import { AppShell } from "@/components/app-shell";
import { PrefsInit } from "@/components/prefs-init";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "IpamBox",
    template: "%s · IpamBox",
  },
  description: "IP address management & network scanner",
};

// Browser chrome tint — matches the default theme (IpamBox Tokyo Night).
export const viewport: Viewport = {
  themeColor: "#1a1b26",
};

// Sets data-theme/data-density before first paint to avoid a flash of the
// wrong theme. Mirrors resolveTheme() in lib/prefs.ts.
const PREFS_SNIPPET = `try{var p=JSON.parse(localStorage.getItem("ipambox:prefs")||"{}");var t=p.theme||"tokyonight";if(t==="system")t=matchMedia("(prefers-color-scheme: light)").matches?"light":"tokyonight";var d=document.documentElement.dataset;d.theme=t;d.density=p.density||"comfortable";d.fx=p.fx||"full";d.fxStars=p.fxStars===false?"0":"1";d.fxGrain=p.fxGrain===false?"0":"1";d.fxSpin=p.fxSpin===false?"0":"1"}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: PREFS_SNIPPET }} />
      </head>
      <body>
        <TooltipProvider delayDuration={150}>
          <AppShell>{children}</AppShell>
          <PrefsInit />
        </TooltipProvider>
      </body>
    </html>
  );
}
