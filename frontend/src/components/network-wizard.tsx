"use client";

import { useId, useState } from "react";
import { useRouter } from "next/navigation";
import { Check } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type {
  NetworkCreate,
  NetworkOut,
  PrefixStatus,
  Site,
  Vlan,
  VlanGroup,
  Vrf,
} from "@/types";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input, Textarea } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const STEPS = [
  { id: "vlan", label: "VLAN" },
  { id: "prefix", label: "Subnet" },
  { id: "tech", label: "Gateway & DNS" },
  { id: "dhcp", label: "DHCP pool" },
  { id: "review", label: "Review" },
] as const;
type Step = (typeof STEPS)[number]["id"];

function Stepper({ step }: { step: Step }) {
  const idx = STEPS.findIndex((s) => s.id === step);
  return (
    <ol className="flex flex-wrap items-center gap-x-2 gap-y-1.5 text-xs">
      {STEPS.map((s, i) => (
        <li key={s.id} className="flex items-center gap-1.5">
          {i > 0 && <span className="h-px w-4 bg-border" />}
          <span
            className={cn(
              "flex h-5 w-5 items-center justify-center rounded-full border text-[10px]",
              i <= idx
                ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-400"
                : "text-muted-foreground"
            )}
          >
            {i < idx ? <Check className="h-2.5 w-2.5" /> : i + 1}
          </span>
          <span className={i === idx ? "font-medium" : "text-muted-foreground"}>
            {s.label}
          </span>
        </li>
      ))}
    </ol>
  );
}

const IP_RE = /^\d{1,3}(\.\d{1,3}){3}$/;
const looksLikeIpv4 = (v: string) => IP_RE.test(v.trim());

/** "Add network" — VLAN + subnet + gateway/DNS + DHCP pool in one
 *  transactional POST /networks (V6.1). Steps mirror the import wizard. */
export function NetworkWizard({
  open,
  onOpenChange,
  vrfs,
  sites,
  vlans,
  groups,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  vrfs: Vrf[];
  sites: Site[];
  vlans: Vlan[];
  groups: VlanGroup[];
  onCreated: () => void;
}) {
  const router = useRouter();
  const uid = useId();
  const [step, setStep] = useState<Step>("vlan");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [vlanMode, setVlanMode] = useState<"new" | "existing">("new");
  const [vlanId, setVlanId] = useState("");
  const [vlanForm, setVlanForm] = useState({ vid: "", name: "", group_id: "none" });
  const [prefixForm, setPrefixForm] = useState({
    cidr: "",
    vrf_id: "",
    site_id: "none",
    status: "active" as PrefixStatus,
    description: "",
  });
  const [techForm, setTechForm] = useState({ gateway: "", dns: "" });
  const [dhcp, setDhcp] = useState({
    enabled: true,
    start: "",
    end: "",
    description: "",
  });

  const reset = () => {
    setStep("vlan");
    setErr(null);
    setVlanMode("new");
    setVlanId("");
    setVlanForm({ vid: "", name: "", group_id: "none" });
    setPrefixForm({
      cidr: "",
      vrf_id: "",
      site_id: "none",
      status: "active",
      description: "",
    });
    setTechForm({ gateway: "", dns: "" });
    setDhcp({ enabled: true, start: "", end: "", description: "" });
  };

  const dnsList = techForm.dns
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  /** Per-step client-side gate; the server re-validates everything. */
  const stepOk = (): boolean => {
    switch (step) {
      case "vlan":
        if (vlanMode === "existing") return vlanId !== "";
        const vid = Number(vlanForm.vid);
        return (
          Number.isInteger(vid) && vid >= 1 && vid <= 4094 && !!vlanForm.name
        );
      case "prefix":
        return !!prefixForm.cidr && !!prefixForm.vrf_id;
      case "tech":
        if (techForm.gateway && !looksLikeIpv4(techForm.gateway)) return false;
        return dnsList.every(looksLikeIpv4) && dnsList.length <= 4;
      case "dhcp":
        return (
          !dhcp.enabled ||
          (looksLikeIpv4(dhcp.start) && looksLikeIpv4(dhcp.end))
        );
      case "review":
        return true;
    }
  };

  const next = () => {
    const i = STEPS.findIndex((s) => s.id === step);
    setErr(null);
    setStep(STEPS[Math.min(i + 1, STEPS.length - 1)].id);
  };
  const back = () => {
    const i = STEPS.findIndex((s) => s.id === step);
    setErr(null);
    setStep(STEPS[Math.max(i - 1, 0)].id);
  };

  const submit = async () => {
    setBusy(true);
    setErr(null);
    try {
      const payload: NetworkCreate = {
        site_id:
          prefixForm.site_id === "none" ? null : Number(prefixForm.site_id),
        ...(vlanMode === "existing"
          ? { vlan_id: Number(vlanId) }
          : {
              vlan: {
                vid: Number(vlanForm.vid),
                name: vlanForm.name,
                group_id:
                  vlanForm.group_id === "none"
                    ? null
                    : Number(vlanForm.group_id),
              },
            }),
        prefix: {
          cidr: prefixForm.cidr,
          vrf_id: Number(prefixForm.vrf_id),
          status: prefixForm.status,
          description: prefixForm.description || null,
        },
        gateway: techForm.gateway || null,
        dns_servers: dnsList.length ? dnsList : null,
        dhcp_range: dhcp.enabled
          ? {
              start: dhcp.start,
              end: dhcp.end,
              description: dhcp.description || null,
            }
          : null,
      };
      const out = await api.post<NetworkOut>("/api/v1/networks", payload);
      toast.success("Network created", {
        description: `prefix #${out.prefix_id} — VLAN #${out.vlan_id}` +
          (out.ip_range_id ? `, pool #${out.ip_range_id}` : ""),
      });
      onOpenChange(false);
      reset();
      onCreated();
      router.push(`/prefixes/${out.prefix_id}`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const vlanLabel =
    vlanMode === "existing"
      ? vlans.find((v) => String(v.id) === vlanId)
      : null;

  return (
    <Dialog
      open={open}
      onOpenChange={(o) => {
        onOpenChange(o);
        if (!o) reset();
      }}
    >
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Add network</DialogTitle>
          <DialogDescription>
            VLAN + subnet + gateway/DNS + DHCP pool in one step — one
            transaction, all or nothing.
          </DialogDescription>
        </DialogHeader>

        <Stepper step={step} />

        {step === "vlan" && (
          <div className="grid gap-3">
            <div className="flex gap-4">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="radio"
                  name={`${uid}-vlanmode`}
                  checked={vlanMode === "new"}
                  onChange={() => setVlanMode("new")}
                />
                New VLAN
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="radio"
                  name={`${uid}-vlanmode`}
                  checked={vlanMode === "existing"}
                  onChange={() => setVlanMode("existing")}
                />
                Existing VLAN
              </label>
            </div>
            {vlanMode === "new" ? (
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label htmlFor={`${uid}-vid`}>VID</Label>
                  <Input
                    id={`${uid}-vid`}
                    inputMode="numeric"
                    placeholder="10"
                    value={vlanForm.vid}
                    onChange={(e) =>
                      setVlanForm({ ...vlanForm, vid: e.target.value })
                    }
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor={`${uid}-vname`}>Name</Label>
                  <Input
                    id={`${uid}-vname`}
                    placeholder="LAN-10"
                    value={vlanForm.name}
                    onChange={(e) =>
                      setVlanForm({ ...vlanForm, name: e.target.value })
                    }
                  />
                </div>
                <div className="col-span-2 grid gap-1.5">
                  <Label htmlFor={`${uid}-vgroup`}>Group</Label>
                  <Select
                    value={vlanForm.group_id}
                    onValueChange={(v) =>
                      setVlanForm({ ...vlanForm, group_id: v })
                    }
                  >
                    <SelectTrigger id={`${uid}-vgroup`}>
                      <SelectValue placeholder="None" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      {groups.map((g) => (
                        <SelectItem key={g.id} value={String(g.id)}>
                          {g.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            ) : (
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-vlanpick`}>VLAN</Label>
                <Select value={vlanId} onValueChange={setVlanId}>
                  <SelectTrigger id={`${uid}-vlanpick`}>
                    <SelectValue placeholder="Select VLAN" />
                  </SelectTrigger>
                  <SelectContent>
                    {vlans.map((v) => (
                      <SelectItem key={v.id} value={String(v.id)}>
                        {v.vid} · {v.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
        )}

        {step === "prefix" && (
          <div className="grid gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-cidr`}>Subnet (CIDR)</Label>
              <Input
                id={`${uid}-cidr`}
                placeholder="10.10.0.0/24"
                className="font-mono"
                value={prefixForm.cidr}
                onChange={(e) =>
                  setPrefixForm({ ...prefixForm, cidr: e.target.value })
                }
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-vrf`}>VRF</Label>
                <Select
                  value={prefixForm.vrf_id}
                  onValueChange={(v) =>
                    setPrefixForm({ ...prefixForm, vrf_id: v })
                  }
                >
                  <SelectTrigger id={`${uid}-vrf`}>
                    <SelectValue placeholder="Select VRF" />
                  </SelectTrigger>
                  <SelectContent>
                    {vrfs.map((v) => (
                      <SelectItem key={v.id} value={String(v.id)}>
                        {v.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor={`${uid}-site`}>Site</Label>
                <Select
                  value={prefixForm.site_id}
                  onValueChange={(v) =>
                    setPrefixForm({ ...prefixForm, site_id: v })
                  }
                >
                  <SelectTrigger id={`${uid}-site`}>
                    <SelectValue placeholder="None" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">None</SelectItem>
                    {sites.map((s) => (
                      <SelectItem key={s.id} value={String(s.id)}>
                        {s.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-status`}>Status</Label>
              <Select
                value={prefixForm.status}
                onValueChange={(v) =>
                  setPrefixForm({ ...prefixForm, status: v as PrefixStatus })
                }
              >
                <SelectTrigger id={`${uid}-status`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["active", "container", "reserved", "deprecated"].map(
                    (s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    )
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-desc`}>Description</Label>
              <Textarea
                id={`${uid}-desc`}
                value={prefixForm.description}
                onChange={(e) =>
                  setPrefixForm({ ...prefixForm, description: e.target.value })
                }
              />
            </div>
          </div>
        )}

        {step === "tech" && (
          <div className="grid gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-gw`}>Gateway (optional)</Label>
              <Input
                id={`${uid}-gw`}
                placeholder="10.10.0.1"
                className="font-mono"
                value={techForm.gateway}
                onChange={(e) =>
                  setTechForm({ ...techForm, gateway: e.target.value })
                }
              />
              <p className="text-xs text-muted-foreground">
                Must be inside the subnet — a protected reserved address row
                is created for it.
              </p>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-dns`}>DNS resolvers (optional)</Label>
              <Input
                id={`${uid}-dns`}
                placeholder="10.10.0.2, 8.8.8.8"
                className="font-mono"
                value={techForm.dns}
                onChange={(e) =>
                  setTechForm({ ...techForm, dns: e.target.value })
                }
              />
              <p className="text-xs text-muted-foreground">
                Comma-separated, up to 4. Resolvers may live outside the
                subnet.
              </p>
            </div>
          </div>
        )}

        {step === "dhcp" && (
          <div className="grid gap-3">
            <div className="flex items-center gap-2 text-sm">
              <Checkbox
                id={`${uid}-dhcp-on`}
                aria-labelledby={`${uid}-dhcp-on-label`}
                checked={dhcp.enabled}
                onCheckedChange={(v) => setDhcp({ ...dhcp, enabled: !!v })}
              />
              <Label id={`${uid}-dhcp-on-label`} htmlFor={`${uid}-dhcp-on`}>
                This subnet has a DHCP pool
              </Label>
            </div>
            {dhcp.enabled && (
              <>
                <div className="grid grid-cols-2 gap-3">
                  <div className="grid gap-1.5">
                    <Label htmlFor={`${uid}-dstart`}>Start</Label>
                    <Input
                      id={`${uid}-dstart`}
                      placeholder="10.10.0.100"
                      className="font-mono"
                      value={dhcp.start}
                      onChange={(e) =>
                        setDhcp({ ...dhcp, start: e.target.value })
                      }
                    />
                  </div>
                  <div className="grid gap-1.5">
                    <Label htmlFor={`${uid}-dend`}>End</Label>
                    <Input
                      id={`${uid}-dend`}
                      placeholder="10.10.0.199"
                      className="font-mono"
                      value={dhcp.end}
                      onChange={(e) =>
                        setDhcp({ ...dhcp, end: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor={`${uid}-ddesc`}>Description</Label>
                  <Input
                    id={`${uid}-ddesc`}
                    placeholder="e.g. LAN DHCP scope"
                    value={dhcp.description}
                    onChange={(e) =>
                      setDhcp({ ...dhcp, description: e.target.value })
                    }
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Addresses in the pool are excluded from next-IP allocation;
                  static assignments inside it are rejected unless forced.
                </p>
              </>
            )}
          </div>
        )}

        {step === "review" && (
          <div className="space-y-2 rounded-md border p-3 text-sm">
            <div>
              <span className="text-muted-foreground">VLAN: </span>
              {vlanMode === "existing" ? (
                <span className="font-mono">
                  {vlanLabel ? `${vlanLabel.vid} · ${vlanLabel.name}` : vlanId}
                </span>
              ) : (
                <span className="font-mono">
                  {vlanForm.vid} · {vlanForm.name} (new)
                </span>
              )}
            </div>
            <div>
              <span className="text-muted-foreground">Subnet: </span>
              <span className="font-mono">{prefixForm.cidr}</span>
              <span className="text-muted-foreground">
                {" "}
                · {vrfs.find((v) => String(v.id) === prefixForm.vrf_id)?.name} ·{" "}
                {prefixForm.status}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Gateway: </span>
              <span className="font-mono">{techForm.gateway || "—"}</span>
            </div>
            <div>
              <span className="text-muted-foreground">DNS: </span>
              <span className="font-mono">
                {dnsList.length ? dnsList.join(", ") : "—"}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">DHCP pool: </span>
              <span className="font-mono">
                {dhcp.enabled ? `${dhcp.start}–${dhcp.end}` : "—"}
              </span>
            </div>
          </div>
        )}

        {err && (
          <p className="rounded-md border border-rose-500/40 bg-rose-500/10 p-2 text-xs text-rose-400">
            {err}
          </p>
        )}

        <DialogFooter className="gap-2">
          {step !== "vlan" && (
            <Button variant="ghost" onClick={back} disabled={busy}>
              Back
            </Button>
          )}
          {step !== "review" ? (
            <Button onClick={next} disabled={!stepOk()}>
              Next
            </Button>
          ) : (
            <Button onClick={submit} disabled={busy}>
              {busy ? "Creating…" : "Create network"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
