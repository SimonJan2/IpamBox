import type { Metadata } from "next";
import { Suspense } from "react";

import DataClient from "./data-client";

export const metadata: Metadata = { title: "Data & Maintenance" };

export default function Page() {
  return (
    <Suspense>
      <DataClient />
    </Suspense>
  );
}
