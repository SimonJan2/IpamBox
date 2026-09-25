import type { Metadata } from "next";
import { Suspense } from "react";

import MonitoringClient from "./monitoring-client";

export const metadata: Metadata = { title: "Monitoring" };

export default function Page() {
  return (
    <Suspense>
      <MonitoringClient />
    </Suspense>
  );
}
