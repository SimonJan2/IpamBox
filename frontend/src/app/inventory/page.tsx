import type { Metadata } from "next";
import { Suspense } from "react";

import InventoryClient from "./inventory-client";

export const metadata: Metadata = { title: "Inventory" };

export default function Page() {
  return (
    <Suspense>
      <InventoryClient />
    </Suspense>
  );
}
