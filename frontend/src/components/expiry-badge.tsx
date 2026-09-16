import { Badge } from "@/components/ui/badge";

export function expiryBadge(expiresOn: string | null) {
  if (!expiresOn) return <span className="text-muted-foreground">—</span>;
  const days = Math.ceil(
    (new Date(expiresOn).getTime() - Date.now()) / 86_400_000
  );
  const cls =
    days < 0
      ? "border-rose-500/40 text-rose-400"
      : days < 30
        ? "border-amber-500/40 text-amber-400"
        : "border-emerald-500/40 text-emerald-400";
  return (
    <Badge variant="outline" className={cls}>
      {days < 0 ? `expired ${-days}d ago` : `${days}d left`}
    </Badge>
  );
}
