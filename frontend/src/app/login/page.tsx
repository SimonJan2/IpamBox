import type { Metadata } from "next";
import { Suspense } from "react";

import LoginClient from "./login-client";

export const metadata: Metadata = { title: "Sign in" };

export default function Page() {
  return (
    <Suspense>
      <LoginClient />
    </Suspense>
  );
}
