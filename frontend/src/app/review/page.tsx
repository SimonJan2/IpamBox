import type { Metadata } from "next";
import { Suspense } from "react";

import ReviewClient from "./review-client";

export const metadata: Metadata = { title: "Review" };

export default function Page() {
  return (
    <Suspense>
      <ReviewClient />
    </Suspense>
  );
}
