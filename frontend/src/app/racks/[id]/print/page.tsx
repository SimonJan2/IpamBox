import type { Metadata } from "next";
import { Suspense } from "react";

import PrintClient from "./print-client";

export const metadata: Metadata = { title: "Rack report" };

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <Suspense>
      <PrintClient id={id} />
    </Suspense>
  );
}
