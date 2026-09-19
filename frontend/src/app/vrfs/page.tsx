import type { Metadata } from "next";
import { Suspense } from "react";

import VrfsClient from "./vrfs-client";

export const metadata: Metadata = { title: "VRFs" };

export default function Page() {
  return (
    <Suspense>
      <VrfsClient />
    </Suspense>
  );
}
