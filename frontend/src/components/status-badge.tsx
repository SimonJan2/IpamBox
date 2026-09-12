import { Badge } from "@/components/ui/badge";
import type { IpStatus, PrefixStatus, ScanStatus } from "@/types";

const ipVariant: Record<IpStatus, "default" | "amber" | "violet" | "cyan" | "zinc"> = {
  active: "default",
  reserved: "amber",
  dhcp: "cyan",
  discovered: "violet",
  offline: "zinc",
};

const prefixVariant: Record<PrefixStatus, "secondary" | "default" | "amber" | "zinc"> = {
  container: "secondary",
  active: "default",
  reserved: "amber",
  deprecated: "zinc",
};

const scanVariant: Record<ScanStatus, "secondary" | "cyan" | "default" | "red"> = {
  queued: "secondary",
  running: "cyan",
  completed: "default",
  failed: "red",
};

export const IpStatusBadge = ({ s }: { s: IpStatus }) => (
  <Badge variant={ipVariant[s]}>{s}</Badge>
);
export const PrefixStatusBadge = ({ s }: { s: PrefixStatus }) => (
  <Badge variant={prefixVariant[s]}>{s}</Badge>
);
export const ScanStatusBadge = ({ s }: { s: ScanStatus }) => (
  <Badge variant={scanVariant[s]}>{s}</Badge>
);
