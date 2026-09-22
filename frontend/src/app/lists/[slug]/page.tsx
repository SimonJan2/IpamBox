import type { Metadata } from "next";
import { Suspense } from "react";

import ListClient from "./list-client";

export const metadata: Metadata = { title: "List" };

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug: raw } = await params;
  // Hebrew (and any non-ASCII) slugs arrive percent-encoded in params —
  // decode so they match the stored slug. Malformed input falls back to raw.
  let slug = raw;
  try {
    slug = decodeURIComponent(raw);
  } catch {
    /* keep raw */
  }
  return (
    <Suspense>
      <ListClient slug={slug} />
    </Suspense>
  );
}
