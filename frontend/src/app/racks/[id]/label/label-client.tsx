"use client";

import { useEffect } from "react";
import Link from "next/link";
import { ArrowLeft, Printer } from "lucide-react";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import type { Rack } from "@/types";
import { RackQrCode, rackUrl } from "@/components/racks/rack-qr";
import { AsyncPanel } from "@/components/async-panel";
import { Button } from "@/components/ui/button";

/** Sticker card: QR -> live elevation, rack name, URL. Dedicated route so the
 *  print area is exactly the card — no print-area CSS hacks inside a dialog. */
export default function LabelClient({ id }: { id: string }) {
  const rackQ = useAsyncData(() => api.get<Rack>(`/api/v1/racks/${id}`), [id]);
  const rack = rackQ.data;

  // Opened via the QR dialog's "Print label" — go straight to the print dialog.
  useEffect(() => {
    if (rack) window.print();
  }, [rack]);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      {/* Screen-only toolbar */}
      <div className="flex items-center gap-2 print:hidden">
        <Button variant="ghost" size="icon" aria-label="Back to rack" asChild>
          <Link href={`/racks/${id}`}>
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="text-sm text-muted-foreground">
          Rack label — prints the sticker card only.
        </span>
        <Button
          size="sm"
          className="ml-auto"
          onClick={() => window.print()}
        >
          <Printer /> Print / save as PDF
        </Button>
      </div>

      <AsyncPanel
        loading={rackQ.loading}
        error={rackQ.error}
        onRetry={rackQ.reload}
        empty={!rack}
        emptyMessage="Rack not found."
      >
        {rack && (
          <div className="flex justify-center pt-8 print:pt-0">
            <div className="w-72 space-y-3 rounded-xl border-2 border-foreground/60 p-5 text-center">
              <div className="flex justify-center">
                <RackQrCode id={rack.id} size={200} />
              </div>
              <p dir="auto" className="text-lg font-semibold leading-tight">
                {rack.name}
              </p>
              <p dir="ltr" className="break-all text-xs text-muted-foreground">
                {rackUrl(rack.id)}
              </p>
            </div>
          </div>
        )}
      </AsyncPanel>
    </div>
  );
}
