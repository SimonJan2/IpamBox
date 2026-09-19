import type { Metadata } from "next";
import { Suspense } from "react";

import PrefixesClient from "./prefixes-client";

export const metadata: Metadata = { title: "Subnets" };

export default function Page() {
  return (
    <Suspense>
      <PrefixesClient />
    </Suspense>
  );
}
