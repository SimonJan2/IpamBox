import type { Metadata } from "next";
import { Suspense } from "react";

import TagsClient from "./tags-client";

export const metadata: Metadata = { title: "Tags" };

export default function Page() {
  return (
    <Suspense>
      <TagsClient />
    </Suspense>
  );
}
