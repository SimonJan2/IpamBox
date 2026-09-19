import type { Metadata } from "next";
import { Suspense } from "react";

import PrefixDetailClient from "./prefix-detail-client";

export const metadata: Metadata = { title: "Subnet" };

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <Suspense>
      <PrefixDetailClient id={id} />
    </Suspense>
  );
}
