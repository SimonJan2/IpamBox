import type { Metadata } from "next";

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

// Sets data-theme/data-density before first paint to avoid a flash of the
// wrong theme. Mirrors resolveTheme() in lib/prefs.ts.
const PREFS_SNIPPET = `try{var p=JSON.parse(localStorage.getItem("ipambox:prefs")||"{}");var t=p.theme||"dark";if(t==="system")t=matchMedia("(prefers-color-scheme: light)").matches?"light":"dark";document.documentElement.dataset.theme=t;document.documentElement.dataset.density=p.density||"comfortable"}catch(e){}`;

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
