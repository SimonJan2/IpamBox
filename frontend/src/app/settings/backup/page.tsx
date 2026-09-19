import type { Metadata } from "next";
import { Suspense } from "react";

import BackupClient from "./backup-client";

export const metadata: Metadata = { title: "Backup & Restore" };

export default function Page() {
  return (
    <Suspense>
      <BackupClient />
    </Suspense>
  );
}
