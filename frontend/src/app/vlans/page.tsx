import type { Metadata } from "next";
import { Suspense } from "react";

import VlansClient from "./vlans-client";

export const metadata: Metadata = { title: "VLANs" };

export default function Page() {
  return (
    <Suspense>
      <VlansClient />
    </Suspense>
  );
}
