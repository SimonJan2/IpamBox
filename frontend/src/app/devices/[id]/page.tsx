import type { Metadata } from "next";
import { Suspense } from "react";

import DeviceDetailClient from "./device-detail-client";

export const metadata: Metadata = { title: "Device" };

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <Suspense>
      <DeviceDetailClient id={id} />
    </Suspense>
  );
}
