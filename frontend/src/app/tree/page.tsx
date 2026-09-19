import type { Metadata } from "next";
import { Suspense } from "react";

import TreeClient from "./tree-client";

export const metadata: Metadata = { title: "Hierarchy" };

export default function Page() {
  return (
    <Suspense>
      <TreeClient />
    </Suspense>
  );
}
