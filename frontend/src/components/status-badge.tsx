import { STATUS_TOKENS } from "@/lib/status-tokens";
import { Badge } from "@/components/ui/badge";
import type { IpStatus, PrefixStatus, ScanStatus } from "@/types";

const prefixVariant: Record<PrefixStatus, "secondary" | "default" | "amber" | "zinc"> = {
  container: "secondary",
  active: "default",
  reserved: "amber",
  deprecated: "zinc",
};

const scanVariant: Record<ScanStatus, "secondary" | "cyan" | "default" | "red" | "zinc"> = {
  queued: "secondary",
  running: "cyan",
  completed: "default",
  failed: "red",
  cancelled: "zinc",
};

export const IpStatusBadge = ({ s }: { s: IpStatus }) => (
  <Badge variant={STATUS_TOKENS[s].badge}>{s}</Badge>
);
export const PrefixStatusBadge = ({ s }: { s: PrefixStatus }) => (
  <Badge variant={prefixVariant[s]}>{s}</Badge>
);
export const ScanStatusBadge = ({ s }: { s: ScanStatus }) => (
  <Badge variant={scanVariant[s]}>{s}</Badge>
);
