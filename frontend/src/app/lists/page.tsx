import type { Metadata } from "next";
import { Suspense } from "react";

import ListsClient from "./lists-client";

export const metadata: Metadata = { title: "Lists" };

export default function Page() {
  return (
    <Suspense>
      <ListsClient />
    </Suspense>
  );
}
