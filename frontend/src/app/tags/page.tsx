"use client";

import { useCallback, useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { usePrefs } from "@/lib/prefs";
import { PERM } from "@/lib/permissions";
import type { Tag } from "@/types";
import { TagDialog } from "@/components/tag-dialog";
import { TagChip } from "@/components/tag-picker";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function TagsPage() {
  const { can } = useAuth();
  const [prefs] = usePrefs();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const [tags, setTags] = useState<Tag[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Tag | null>(null);

  const refresh = useCallback(() => {
    api.get<Tag[]>("/api/v1/tags").then(setTags).catch(() => {});
  }, []);

  useEffect(refresh, [refresh]);

  const remove = async (t: Tag) => {
    try {
      await api.del(`/api/v1/tags/${t.id}`);
      toast.success(`Deleted ${t.name}`);
      refresh();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Tags</h1>
        {canWrite && (
          <Button
            size="sm"
            onClick={() => {
              setEditing(null);
              setDialogOpen(true);
            }}
          >
            <Plus /> New tag
          </Button>
        )}
      </div>
      <p className="text-sm text-muted-foreground">
        Tags can be attached to sites, VRFs, prefixes and addresses.
      </p>

      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Tag</TableHead>
              {prefs.showSlugs && <TableHead>Slug</TableHead>}
              <TableHead>Description</TableHead>
              <TableHead className="w-24 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tags.map((t) => (
              <TableRow key={t.id}>
                <TableCell>
                  <TagChip tag={t} />
                </TableCell>
                {prefs.showSlugs && (
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {t.slug}
                  </TableCell>
                )}
                <TableCell className="text-muted-foreground">
                  {t.description ?? "—"}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    {canWrite && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          setEditing(t);
                          setDialogOpen(true);
                        }}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                    )}
                    {canDelete && (
                      <Button variant="ghost" size="icon" onClick={() => remove(t)}>
                        <Trash2 className="h-4 w-4 text-rose-400" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {tags.length === 0 && (
              <TableRow>
                <TableCell colSpan={prefs.showSlugs ? 4 : 3} className="py-10 text-center text-muted-foreground">
                  No tags yet.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <TagDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        tag={editing}
        onSaved={refresh}
      />
    </div>
  );
}
