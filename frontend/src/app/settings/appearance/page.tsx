import type { Metadata } from "next";
import { Suspense } from "react";

import AppearanceClient from "./appearance-client";

export const metadata: Metadata = { title: "Appearance" };

export default function Page() {
  return (
    <Suspense>
      <AppearanceClient />
    </Suspense>
  );
}
