import type { Metadata } from "next";
import { Suspense } from "react";

import RackDetailClient from "./rack-detail-client";

export const metadata: Metadata = { title: "Rack" };

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <Suspense>
      <RackDetailClient id={id} />
    </Suspense>
  );
}
