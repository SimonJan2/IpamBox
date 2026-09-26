import { PageEdit } from "@/components/docs/page-edit";

export default async function EditDocPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <PageEdit slug={slug} />;
}
