import type { Metadata } from "next";

import { PageEditor } from "@/components/docs/page-editor";

export const metadata: Metadata = { title: "New page" };

export default function NewDocPage() {
  return <PageEditor page={null} />;
}
