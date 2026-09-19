import type { Metadata } from "next";
import { Suspense } from "react";

import DashboardClient from "./dashboard-client";

// Root segment ignores the layout's title.template — set it absolutely.
export const metadata: Metadata = { title: { absolute: "Dashboard · IpamBox" } };

export default function Page() {
  return (
    <Suspense>
      <DashboardClient />
    </Suspense>
  );
}
