"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { arrayMove } from "@dnd-kit/sortable";
import type { DragEndEvent } from "@dnd-kit/core";
import { Pencil, Plus, ShieldAlert, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { cn } from "@/lib/utils";
import { ROW_COLOR_PALETTE } from "@/lib/row-color";
import type {
  ColorRule,
  ColorRuleFieldMeta,
  ColorRuleOperator,
} from "@/types";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { DragHandle, RowOrderDnd, SortableRow } from "@/components/row-order";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

/** Must mirror COLORABLE in backend/app/services/colors.py. */
const ENTITIES: { key: string; label: string }[] = [
  { key: "sites", label: "Sites" },
  { key: "vrfs", label: "VRFs" },
  { key: "vlans", label: "VLANs" },
  { key: "circuits", label: "Circuits" },
  { key: "certificates", label: "Certificates" },
  { key: "assets", label: "Assets" },
  { key: "services", label: "Services" },
  { key: "tags", label: "Tags" },
  { key: "addresses", label: "Addresses" },
];

const OP_LABEL: Record<ColorRuleOperator, string> = {
  eq: "equals",
  neq: "doesn't equal",
  contains: "contains",
  lt: "before / less than",
  gt: "after / more than",
  within_days: "within the next N days",
};

/** Operators offered per field type — keeps the picker typed and honest. */
const OPS_BY_TYPE: Record<ColorRuleFieldMeta["type"], ColorRuleOperator[]> = {
  text: ["eq", "neq", "contains", "lt", "gt"],
  number: ["eq", "neq", "lt", "gt"],
  date: ["eq", "neq", "lt", "gt", "within_days"],
  bool: ["eq", "neq"],
  enum: ["eq", "neq", "contains"],
};

function opsFor(field: ColorRuleFieldMeta | undefined): ColorRuleOperator[] {
  return OPS_BY_TYPE[field?.type ?? "text"];
}

function ColorDot({ color }: { color: string }) {
  return (
    <span
      className="inline-block h-4 w-4 rounded-full border border-border"
      style={{ background: color }}
    />
  );
}

type Draft = {
  field: string;
  operator: ColorRuleOperator;
  value: string;
  color: string;
};

function RuleDialog({
  open,
  onOpenChange,
  entityType,
  fields,
  rule,
  onSaved,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
  entityType: string;
  fields: ColorRuleFieldMeta[];
  rule: ColorRule | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<Draft>({
    field: "",
    operator: "eq",
    value: "",
    color: ROW_COLOR_PALETTE[0],
  });
  const [busy, setBusy] = useState(false);
  const [preview, setPreview] = useState<number | null>(null);

  useEffect(() => {
    if (open) {
      setForm({
        field: rule?.field ?? "",
        operator: rule?.operator ?? "eq",
        value: rule?.value ?? "",
        color: rule?.color ?? ROW_COLOR_PALETTE[0],
      });
      setPreview(null);
    }
  }, [open, rule]);

  const fieldMeta = fields.find((f) => f.name === form.field);
  const ops = opsFor(fieldMeta);

  // Keep the operator legal when the field (and thus its type) changes.
  useEffect(() => {
    if (form.operator && !ops.includes(form.operator)) {
      setForm((f) => ({ ...f, operator: ops[0] }));
    }
  }, [form.operator, ops]);

  // Live "N rows match" preview — the server runs the same matcher that
  // stamps rows, so the count is authoritative.
  useEffect(() => {
    if (!open || !form.field || !form.operator || form.value === "") {
      setPreview(null);
      return;
    }
    const t = setTimeout(() => {
      api
        .get<{ count: number }>(
          `/api/v1/color-rules/preview?entity_type=${entityType}` +
            `&field=${encodeURIComponent(form.field)}` +
            `&operator=${form.operator}` +
            `&value=${encodeURIComponent(form.value)}`
        )
        .then((r) => setPreview(r.count))
        .catch(() => setPreview(null));
    }, 250);
    return () => clearTimeout(t);
  }, [open, entityType, form.field, form.operator, form.value]);

  const valid =
    form.field !== "" && form.operator !== undefined && form.value !== "";

  const submit = async () => {
    setBusy(true);
    try {
      const body = {
        entity_type: entityType,
        field: form.field,
        operator: form.operator,
        value: form.value,
        color: form.color,
      };
      if (rule) {
        await api.patch(`/api/v1/color-rules/${rule.id}`, body);
        toast.success("Rule updated");
      } else {
        await api.post("/api/v1/color-rules", body);
        toast.success("Rule created");
      }
      onOpenChange(false);
      onSaved();
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {rule ? "Edit rule" : "New rule"} —{" "}
            {ENTITIES.find((e) => e.key === entityType)?.label}
          </DialogTitle>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5">
              <Label>Field</Label>
              <Select
                value={form.field}
                onValueChange={(v) => setForm({ ...form, field: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Pick a column…" />
                </SelectTrigger>
                <SelectContent>
                  {fields.map((f) => (
                    <SelectItem key={f.name} value={f.name}>
                      {f.name}
                      <span className="ml-1 text-xs text-muted-foreground">
                        {f.type}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-1.5">
              <Label>Operator</Label>
              <Select
                value={form.operator}
                onValueChange={(v) =>
                  setForm({ ...form, operator: v as ColorRuleOperator })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ops.map((op) => (
                    <SelectItem key={op} value={op}>
                      {OP_LABEL[op]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid gap-1.5">
            <Label>Value</Label>
            {fieldMeta?.type === "bool" ? (
              <Select
                value={form.value}
                onValueChange={(v) => setForm({ ...form, value: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="true / false" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="true">true</SelectItem>
                  <SelectItem value="false">false</SelectItem>
                </SelectContent>
              </Select>
            ) : fieldMeta?.type === "enum" && fieldMeta.values?.length ? (
              <Select
                value={form.value}
                onValueChange={(v) => setForm({ ...form, value: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Pick a value…" />
                </SelectTrigger>
                <SelectContent>
                  {fieldMeta.values.map((v) => (
                    <SelectItem key={v} value={v}>
                      {v}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Input
                dir="ltr"
                type={
                  form.operator === "within_days" || fieldMeta?.type === "number"
                    ? "number"
                    : fieldMeta?.type === "date"
                      ? "date"
                      : "text"
                }
                placeholder={
                  form.operator === "within_days"
                    ? "7"
                    : "value to compare against"
                }
                value={form.value}
                onChange={(e) => setForm({ ...form, value: e.target.value })}
              />
            )}
          </div>
          <div className="grid gap-1.5">
            <Label>Color</Label>
            <div role="radiogroup" className="flex gap-1.5">
              {ROW_COLOR_PALETTE.map((c) => (
                <button
                  key={c}
                  type="button"
                  role="radio"
                  aria-checked={form.color === c}
                  aria-label={c}
                  onClick={() => setForm({ ...form, color: c })}
                  className={cn(
                    "h-7 w-7 rounded-md border-2 transition-all",
                    form.color === c
                      ? "border-foreground"
                      : "border-transparent"
                  )}
                  style={{ background: c }}
                />
              ))}
            </div>
          </div>
          {valid && preview !== null && (
            <p className="text-sm text-muted-foreground">
              Matches <span className="font-medium text-foreground">
                {preview}
              </span>{" "}
              {ENTITIES.find((e) => e.key === entityType)?.label.toLowerCase()}{" "}
              right now.
            </p>
          )}
        </div>
        <DialogFooter>
          <Button onClick={submit} disabled={busy || !valid}>
            {busy ? "Saving…" : rule ? "Save" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function ColorRulesPage() {
  const { can } = useAuth();
  const canAdmin = can(PERM.SYSTEM_ADMIN);
  const [entity, setEntity] = useState("certificates");
  const rulesQ = useAsyncData(
    () =>
      canAdmin
        ? api.get<ColorRule[]>(`/api/v1/color-rules?entity_type=${entity}`)
        : Promise.resolve([]),
    [entity, canAdmin]
  );
  const fieldsQ = useAsyncData(
    () =>
      canAdmin
        ? api.get<ColorRuleFieldMeta[]>(
            `/api/v1/color-rules/fields?entity_type=${entity}`
          )
        : Promise.resolve([]),
    [entity, canAdmin]
  );
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<ColorRule | null>(null);
  const [matches, setMatches] = useState<Record<number, number>>({});

  const rules = useMemo(() => rulesQ.data ?? [], [rulesQ.data]);
  const refresh = () => void rulesQ.reload();

  // Per-rule live match counts — same matcher the server uses to stamp.
  useEffect(() => {
    setMatches({});
    for (const r of rules) {
      api
        .get<{ count: number }>(
          `/api/v1/color-rules/preview?entity_type=${r.entity_type}` +
            `&field=${encodeURIComponent(r.field)}` +
            `&operator=${r.operator}` +
            `&value=${encodeURIComponent(r.value)}`
        )
        .then((p) => setMatches((m) => ({ ...m, [r.id]: p.count })))
        .catch(() => {});
    }
  }, [rules]);

  // Priority = position: first match wins. Reuses the row-curation dnd
  // plumbing — the reorder POST permutes only the submitted ids.
  const onDragEnd = useCallback(
    (e: DragEndEvent) => {
      const { active, over } = e;
      if (!over || active.id === over.id) return;
      const ids = rules.map((r) => r.id);
      const next = arrayMove(
        ids,
        ids.indexOf(Number(active.id)),
        ids.indexOf(Number(over.id))
      );
      const byId = new Map(rules.map((r) => [r.id, r]));
      rulesQ.setData(
        next.map((id, i) => ({ ...byId.get(id)!, position: i + 1 }))
      );
      api
        .post("/api/v1/color-rules/reorder", { entity_type: entity, ids: next })
        .catch((e) => {
          rulesQ.setData(rules);
          toast.error("Couldn't save rule order", { description: String(e) });
        });
    },
    [rules, entity, rulesQ]
  );

  const remove = async (r: ColorRule) => {
    try {
      await api.del(`/api/v1/color-rules/${r.id}`);
      toast.success("Rule deleted");
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  if (!canAdmin) {
    return (
      <div className="space-y-6">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">Color Rules <DocsLink slug="row-colors" /></h1>
        <Card className="border-amber-500/30">
          <CardContent className="flex items-start gap-3 pt-6 text-sm text-muted-foreground">
            <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
            Color rules change what every user sees — editing them requires
            the Administrator role.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">Color Rules <DocsLink slug="row-colors" /></h1>
        <p className="text-sm text-muted-foreground">
          Automatic row colors shared by all users. The first matching rule
          (top of the list) wins; a manual row color always beats rules.
        </p>
      </div>

      <div className="flex items-center gap-2">
        <Select value={entity} onValueChange={setEntity}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {ENTITIES.map((e) => (
              <SelectItem key={e.key} value={e.key}>
                {e.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <span className="ml-auto text-sm text-muted-foreground">
          {rules.length} rule{rules.length === 1 ? "" : "s"}
        </span>
        <Button
          size="sm"
          onClick={() => {
            setEditing(null);
            setDialogOpen(true);
          }}
        >
          <Plus /> New rule
        </Button>
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={rulesQ.loading}
          error={rulesQ.error}
          onRetry={rulesQ.reload}
          empty={rules.length === 0}
          emptyMessage="No rules for this entity — matching rows stay uncolored."
        >
          <RowOrderDnd ids={rules.map((r) => r.id)} onDragEnd={onDragEnd}>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-8">
                    <span className="sr-only">Reorder</span>
                  </TableHead>
                  <TableHead className="w-12">Color</TableHead>
                  <TableHead>When</TableHead>
                  <TableHead>Matches</TableHead>
                  <TableHead className="w-24 text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rules.map((r) => (
                  <SortableRow key={r.id} rowId={r.id}>
                    <TableCell>
                      <DragHandle
                        label={`Move rule ${r.field} ${r.operator} ${r.value}`}
                      />
                    </TableCell>
                    <TableCell>
                      <ColorDot color={r.color} />
                    </TableCell>
                    <TableCell>
                      <span className="font-mono text-xs">{r.field}</span>{" "}
                      <span className="text-muted-foreground">
                        {OP_LABEL[r.operator]}
                      </span>{" "}
                      <Badge variant="outline" className="font-mono text-xs">
                        {r.value}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {matches[r.id] !== undefined
                        ? `${matches[r.id]} rows`
                        : "…"}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Edit rule ${r.id}`}
                          onClick={() => {
                            setEditing(r);
                            setDialogOpen(true);
                          }}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Delete rule ${r.id}`}
                          onClick={() => remove(r)}
                        >
                          <Trash2 className="h-4 w-4 text-rose-400" />
                        </Button>
                      </div>
                    </TableCell>
                  </SortableRow>
                ))}
              </TableBody>
            </Table>
          </RowOrderDnd>
        </AsyncPanel>
      </div>

      <RuleDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        entityType={entity}
        fields={fieldsQ.data ?? []}
        rule={editing}
        onSaved={refresh}
      />
    </div>
  );
}
