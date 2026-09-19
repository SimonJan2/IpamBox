import type { Metadata } from "next";
import { Suspense } from "react";

import SecurityClient from "./security-client";

export const metadata: Metadata = { title: "Account & Security" };

export default function Page() {
  return (
    <Suspense>
      <SecurityClient />
    </Suspense>
  );
}
