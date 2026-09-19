import type { Metadata } from "next";
import { Suspense } from "react";

import UsersClient from "./users-client";

export const metadata: Metadata = { title: "Users & Roles" };

export default function Page() {
  return (
    <Suspense>
      <UsersClient />
    </Suspense>
  );
}
