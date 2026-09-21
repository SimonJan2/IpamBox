import type { Metadata } from "next";
import { Suspense } from "react";

import ColorRulesClient from "./color-rules-client";

export const metadata: Metadata = { title: "Color Rules" };

export default function Page() {
  return (
    <Suspense>
      <ColorRulesClient />
    </Suspense>
  );
}
