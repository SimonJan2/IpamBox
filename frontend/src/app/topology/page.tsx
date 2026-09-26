import type { Metadata } from "next";
import { Suspense } from "react";

import TopologyClient from "./topology-client";

export const metadata: Metadata = { title: "Topology" };

export default function Page() {
  return (
    <Suspense>
      <TopologyClient />
    </Suspense>
  );
}
