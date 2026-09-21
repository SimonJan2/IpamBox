import { DocsNav } from "@/components/docs/docs-nav";

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      <DocsNav />
      <div className="min-w-0 max-w-3xl flex-1 pb-10">{children}</div>
    </div>
  );
}
