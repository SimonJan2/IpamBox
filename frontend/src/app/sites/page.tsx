import type { Metadata } from "next";
import { Suspense } from "react";

import SitesClient from "./sites-client";

export const metadata: Metadata = { title: "Sites" };

export default function Page() {
  return (
    <Suspense>
      <SitesClient />
    </Suspense>
  );
}
