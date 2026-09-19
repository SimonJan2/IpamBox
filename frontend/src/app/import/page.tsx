import type { Metadata } from "next";
import { Suspense } from "react";

import ImportClient from "./import-client";

export const metadata: Metadata = { title: "Import" };

export default function Page() {
  return (
    <Suspense>
      <ImportClient />
    </Suspense>
  );
}
