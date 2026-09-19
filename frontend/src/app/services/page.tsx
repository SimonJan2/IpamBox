import type { Metadata } from "next";
import { Suspense } from "react";

import ServicesClient from "./services-client";

export const metadata: Metadata = { title: "Services" };

export default function Page() {
  return (
    <Suspense>
      <ServicesClient />
    </Suspense>
  );
}
