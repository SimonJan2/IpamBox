import type { Metadata } from "next";
import { Suspense } from "react";

import FeaturesClient from "./features-client";

export const metadata: Metadata = { title: "Features" };

export default function Page() {
  return (
    <Suspense>
      <FeaturesClient />
    </Suspense>
  );
}
