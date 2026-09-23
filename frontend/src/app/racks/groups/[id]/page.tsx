import type { Metadata } from "next";

import GroupClient from "./group-client";

export const metadata: Metadata = { title: "Rack group" };

export default async function RackGroupPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <GroupClient id={id} />;
}
