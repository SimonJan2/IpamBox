import type { Metadata } from "next";
import { Suspense } from "react";

import LabelClient from "./label-client";

export const metadata: Metadata = { title: "Rack label" };

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <Suspense>
      <LabelClient id={id} />
    </Suspense>
  );
}
