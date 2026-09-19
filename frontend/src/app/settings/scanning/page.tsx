import type { Metadata } from "next";
import { Suspense } from "react";

import ScanningClient from "./scanning-client";

export const metadata: Metadata = { title: "Scanning" };

export default function Page() {
  return (
    <Suspense>
      <ScanningClient />
    </Suspense>
  );
}
