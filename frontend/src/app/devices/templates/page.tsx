import type { Metadata } from "next";
import { Suspense } from "react";

import TemplatesPage from "./templates-client";

export const metadata: Metadata = { title: "Device templates" };

export default function Page() {
  return (
    <Suspense>
      <TemplatesPage />
    </Suspense>
  );
}
