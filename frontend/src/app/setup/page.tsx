import type { Metadata } from "next";
import { Suspense } from "react";

import SetupClient from "./setup-client";

export const metadata: Metadata = { title: "Setup" };

export default function Page() {
  return (
    <Suspense>
      <SetupClient />
    </Suspense>
  );
}
