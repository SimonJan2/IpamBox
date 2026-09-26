import type { Metadata } from "next";
import { Suspense } from "react";

import PrintClient from "./print-client";

export const metadata: Metadata = { title: "Estate report" };

export default function Page() {
  return (
    <Suspense>
      <PrintClient />
    </Suspense>
  );
}
