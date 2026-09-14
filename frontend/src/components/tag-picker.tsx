"use client";

import { useCallback, useEffect, useState } from "react";
import { Tags } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import type { Tag, TagAssignment } from "@/types";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function TagChip({ tag }: { tag: Tag }) {
  return (
    <span
      className="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px]"
      style={{ borderColor: `${tag.color}55`, color: tag.color }}
    >
      <i className="h-1.5 w-1.5 rounded-full" style={{ background: tag.color }} />
      {tag.name}
    </span>
  );
}

/** Shared loader — returns all tags plus an object_id -> Tag[] map for a type. */
export function useTags(objectType: string) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [byObject, setByObject] = useState<Map<number, Tag[]>>(new Map());

  const refresh = useCallback(() => {
    Promise.all([
      api.get<Tag[]>("/api/v1/tags"),
      api.get<TagAssignment[]>(
        `/api/v1/tags/assignments?object_type=${objectType}`
      ),
    ])
      .then(([all, rows]) => {
        setTags(all);
        const map = new Map<number, Tag[]>();
        for (const a of rows) {
          const t = all.find((x) => x.id === a.tag_id);
          if (!t) continue;
          map.set(a.object_id, [...(map.get(a.object_id) ?? []), t]);
        }
        setByObject(map);
      })
      .catch(() => {});
  }, [objectType]);

  useEffect(refresh, [refresh]);
  return { tags, byObject, refresh };
}

export function TagPicker({
  objectType,
  objectId,
  allTags,
  assigned,
  onChanged,
}: {
  objectType: string;
  objectId: number;
  allTags: Tag[];
  assigned: Tag[];
  onChanged: () => void;
}) {
  const { can } = useAuth();
  const assignedIds = new Set(assigned.map((t) => t.id));

  const toggle = async (tagId: number, isAssigned: boolean) => {
    try {
      if (isAssigned) {
        await api.del(
          `/api/v1/tags/${tagId}/assignments/${objectType}/${objectId}`
        );
      } else {
        await api.post(`/api/v1/tags/${tagId}/assignments`, {
          object_type: objectType,
          object_id: objectId,
        });
      }
      onChanged();
    } catch (e) {
      toast.error("Tag update failed", { description: String(e) });
    }
  };

  if (!can(PERM.DATA_WRITE)) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" title="Edit tags">
          <Tags className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Tags</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {allTags.length === 0 && (
          <div className="px-2 py-1.5 text-xs text-muted-foreground">
            No tags yet — create them on the Tags page.
          </div>
        )}
        {allTags.map((t) => (
          <DropdownMenuCheckboxItem
            key={t.id}
            checked={assignedIds.has(t.id)}
            onCheckedChange={() => toggle(t.id, assignedIds.has(t.id))}
          >
            <span
              className="mr-2 inline-block h-2 w-2 rounded-full"
              style={{ background: t.color }}
            />
            {t.name}
          </DropdownMenuCheckboxItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
