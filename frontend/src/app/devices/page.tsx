import type { Metadata } from "next";
import { Suspense } from "react";

import DevicesPage from "./devices-client";

export const metadata: Metadata = { title: "Devices" };

export default function Page() {
  return (
    <Suspense>
      <DevicesPage />
    </Suspense>
  );
}
