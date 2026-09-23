"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Printer } from "lucide-react";
import QRCode from "react-qr-code";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

/** URL the QR encodes — the live elevation, reachable from a phone on the LAN. */
export function rackUrl(id: number): string {
  return `${window.location.origin}/racks/${id}`;
}

/** Pure-SVG QR of the rack's live URL (no canvas — prints crisply). */
export function RackQrCode({ id, size = 128 }: { id: number; size?: number }) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => setUrl(rackUrl(id)), [id]);
  if (!url) return <div style={{ width: size, height: size }} />;
  return <QRCode value={url} size={size} bgColor="#FFFFFF" fgColor="#000000" />;
}

export function RackQrDialog({
  open,
  onOpenChange,
  rackId,
  name,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  rackId: number;
  name: string;
}) {
  const [url, setUrl] = useState("");
  useEffect(() => {
    if (open) setUrl(rackUrl(rackId));
  }, [open, rackId]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xs">
        <DialogHeader>
          <DialogTitle>Rack QR code</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col items-center gap-3">
          <div className="rounded-lg bg-white p-3">
            <RackQrCode id={rackId} />
          </div>
          <p dir="auto" className="font-medium">{name}</p>
          <p dir="ltr" className="break-all text-center text-xs text-muted-foreground">
            {url}
          </p>
          <Button size="sm" asChild>
            <Link href={`/racks/${rackId}/label`} target="_blank">
              <Printer /> Print label
            </Link>
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
