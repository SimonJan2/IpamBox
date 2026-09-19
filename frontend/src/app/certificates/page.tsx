import type { Metadata } from "next";
import { Suspense } from "react";

import CertificatesClient from "./certificates-client";

export const metadata: Metadata = { title: "Certificates" };

export default function Page() {
  return (
    <Suspense>
      <CertificatesClient />
    </Suspense>
  );
}
