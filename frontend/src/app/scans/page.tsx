import type { Metadata } from "next";
import { Suspense } from "react";

import ScansClient from "./scans-client";

export const metadata: Metadata = { title: "Scans" };

export default function Page() {
  return (
    <Suspense>
      <ScansClient />
    </Suspense>
  );
}
