import { SettingsNav } from "@/components/settings/settings-nav";

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      <SettingsNav />
      <div className="min-w-0 max-w-3xl flex-1 pb-10">{children}</div>
    </div>
  );
}
