"use client";

import { useId, useMemo, useState } from "react";
import Link from "next/link";
import { FileUp, History, ListPlus, ListTree, Trash2, Upload } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { foldHebrew } from "@/lib/utils";
import { useUrlText } from "@/lib/url-state";
import { fmtTs } from "@/lib/prefs";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { HistoryDialog } from "@/components/history-panel";
import { ImportListDialog } from "./import-list-dialog";
import type { CustomList, Page } from "@/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input, Textarea } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function ListsClient() {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const listsQ = useAsyncData(() =>
    api.get<Page<CustomList>>("/api/v1/lists").then((p) => p.items)
  );
  const [q, setQ] = useUrlText("q");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [deleting, setDeleting] = useState<CustomList | null>(null);
  const [historyFor, setHistoryFor] = useState<CustomList | null>(null);
  const [form, setForm] = useState({ name: "", description: "" });
  const [busy, setBusy] = useState(false);
  const uid = useId();

  const lists = useMemo(() => {
    const needle = foldHebrew(q.toLowerCase());
    return (listsQ.data ?? []).filter(
      (l) =>
        !q ||
        foldHebrew(l.name.toLowerCase()).includes(needle) ||
        (l.description &&
          foldHebrew(l.description.toLowerCase()).includes(needle)) ||
        (l.source_sheet &&
          foldHebrew(l.source_sheet.toLowerCase()).includes(needle))
    );
  }, [listsQ.data, q]);

  const submit = async () => {
    setBusy(true);
    try {
      const created = await api.post<CustomList>("/api/v1/lists", {
        name: form.name,
        description: form.description || null,
        columns: [],
      });
      toast.success("List created — open it to add columns and rows");
      setDialogOpen(false);
      setForm({ name: "", description: "" });
      void listsQ.reload();
      window.location.assign(`/lists/${created.slug}`);
    } catch (e) {
      toast.error("Create failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const doDelete = async () => {
    if (!deleting) return;
    try {
      await api.del(`/api/v1/lists/${deleting.id}`);
      toast.success(`List "${deleting.name}" deleted`);
      setDeleting(null);
      void listsQ.reload();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">
          Lists <DocsLink slug="lists" />
        </h1>
        {canWrite && (
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setImportOpen(true)}
            >
              <FileUp /> Import file
            </Button>
            <Button size="sm" onClick={() => setDialogOpen(true)}>
              <ListPlus /> New list
            </Button>
          </div>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Input
          placeholder="Search lists…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="max-w-xs"
        />
        <span className="ml-auto text-sm text-muted-foreground">
          {lists.length} lists
        </span>
      </div>

      <div className="rounded-lg border">
        <AsyncPanel
          loading={listsQ.loading}
          error={listsQ.error}
          onRetry={listsQ.reload}
          empty={(listsQ.data ?? []).length === 0}
          emptyMessage="No lists yet — create one, or import a workbook sheet as a list."
        >
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Rows</TableHead>
                <TableHead>Source sheet</TableHead>
                <TableHead>Last import</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {lists.map((l) => (
                <TableRow key={l.id}>
                  <TableCell>
                    <Link
                      href={`/lists/${l.slug}`}
                      className="font-medium hover:underline"
                    >
                      <span dir="auto" className="inline-flex items-center gap-2">
                        <ListTree className="h-4 w-4 text-muted-foreground" />
                        {l.name}
                      </span>
                    </Link>
                    {l.description && (
                      <div
                        dir="auto"
                        className="mt-0.5 text-xs text-muted-foreground"
                      >
                        {l.description}
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{l.row_count}</Badge>
                  </TableCell>
                  <TableCell>
                    {l.source_sheet ? (
                      <span
                        dir="auto"
                        className="inline-flex items-center gap-1.5 text-muted-foreground"
                      >
                        <Upload className="h-3.5 w-3.5" />
                        {l.source_sheet}
                      </span>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {l.import_batch_id ? fmtTs(l.created_at) : "—"}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`History of ${l.name}`}
                      onClick={() => setHistoryFor(l)}
                    >
                      <History className="h-4 w-4" />
                    </Button>
                    {canDelete && (
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label={`Delete list ${l.name}`}
                        onClick={() => setDeleting(l)}
                      >
                        <Trash2 className="h-4 w-4 text-rose-400" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </AsyncPanel>
      </div>

      <ImportListDialog
        open={importOpen}
        onOpenChange={setImportOpen}
        onImported={listsQ.reload}
      />

      <HistoryDialog
        open={historyFor !== null}
        onOpenChange={() => setHistoryFor(null)}
        objectType="CustomList"
        objectId={historyFor?.id ?? null}
        title={historyFor?.name}
      />

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>New list</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-name`}>Name</Label>
              <Input
                id={`${uid}-name`}
                dir="auto"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. שרתים בייצור"
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor={`${uid}-desc`}>Description</Label>
              <Textarea
                id={`${uid}-desc`}
                dir="auto"
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              onClick={submit}
              disabled={busy || !form.name.trim()}
            >
              {busy ? "Creating…" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleting !== null} onOpenChange={() => setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete list</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.name}
            </span>
            ? This removes the list and all {deleting?.row_count ?? 0} rows in
            it.
          </p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
