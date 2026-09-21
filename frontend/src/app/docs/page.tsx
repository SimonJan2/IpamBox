import type { Metadata } from "next";
import { Suspense } from "react";

import DocsIndexClient from "./docs-index-client";

export const metadata: Metadata = { title: "Docs" };

export default function Page() {
  return (
    <Suspense>
      <DocsIndexClient />
    </Suspense>
  );
}
