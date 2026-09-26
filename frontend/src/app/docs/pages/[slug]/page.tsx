import { PageView } from "@/components/docs/page-view";

// User pages render here — /docs/pages/<slug>. Builtin help keeps
// /docs/<slug> (statically generated), so a user page can never shadow
// or be shadowed by a builtin article.
export default async function UserDocPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <PageView slug={slug} />;
}
