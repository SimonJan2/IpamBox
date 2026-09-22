import type { Metadata } from "next";
import { Suspense } from "react";

import RacksClient from "./racks-client";

export const metadata: Metadata = { title: "Racks" };

export default function Page() {
  return (
    <Suspense>
      <RacksClient />
    </Suspense>
  );
}
