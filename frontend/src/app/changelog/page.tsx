import type { Metadata } from "next";
import { Suspense } from "react";

import ChangelogClient from "./changelog-client";

export const metadata: Metadata = { title: "Changelog" };

export default function Page() {
  return (
    <Suspense>
      <ChangelogClient />
    </Suspense>
  );
}
