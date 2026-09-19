import type { Metadata } from "next";
import { Suspense } from "react";

import DiscoveryClient from "./discovery-client";

export const metadata: Metadata = { title: "Discovery Inbox" };

export default function Page() {
  return (
    <Suspense>
      <DiscoveryClient />
    </Suspense>
  );
}
