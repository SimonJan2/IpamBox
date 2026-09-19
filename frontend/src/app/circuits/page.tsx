import type { Metadata } from "next";
import { Suspense } from "react";

import CircuitsClient from "./circuits-client";

export const metadata: Metadata = { title: "Circuits" };

export default function Page() {
  return (
    <Suspense>
      <CircuitsClient />
    </Suspense>
  );
}
