"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useId, useState } from "react";
import { Bookmark, Check, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { usePrefs, type SavedView } from "@/lib/prefs";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

/** Named presets on top of URL state: "Save view" captures the current
 *  query string; applying one is a replace navigation to the stored query.
 *  Stored in prefs under `savedViews[pageKey]`. */
export function SavedViews({
  pageKey,
  builtins = [],
  className,
}: {
  /** Stable key identifying this page's view namespace in prefs. */
  pageKey: string;
  /** Built-in presets — always listed first, not stored, not deletable. */
  builtins?: SavedView[];
  className?: string;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [prefs, setPrefs] = usePrefs();
  const [saveOpen, setSaveOpen] = useState(false);
  const [manageOpen, setManageOpen] = useState(false);
  const [name, setName] = useState("");
  const uid = useId();

  const current = searchParams.toString();
  const views = prefs.savedViews[pageKey] ?? [];

  const apply = (query: string) =>
    router.replace(query ? `${pathname}?${query}` : pathname, {
      scroll: false,
    });

  const writeViews = (next: SavedView[]) =>
    setPrefs({ savedViews: { ...prefs.savedViews, [pageKey]: next } });

  const save = () => {
    const n = name.trim();
    if (!n) return;
    writeViews([
      ...views.filter((v) => v.name !== n),
      { name: n, query: current },
    ]);
    toast.success(`View "${n}" saved`);
    setSaveOpen(false);
  };

  const activeName = (v: SavedView) => v.query === current;

  return (
    <div className={cn("flex items-center", className)}>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" aria-label="Saved views">
            <Bookmark /> Views
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56 bg-card">
          {builtins.length > 0 && (
            <>
              <DropdownMenuLabel>Built-in</DropdownMenuLabel>
              {builtins.map((v) => (
                <DropdownMenuItem
                  key={v.name}
                  onClick={() => apply(v.query)}
                  className="justify-between"
                >
                  <span dir="auto" className="truncate">
                    {v.name}
                  </span>
                  {activeName(v) && <Check className="h-3.5 w-3.5" />}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
            </>
          )}
          <DropdownMenuLabel>Your views</DropdownMenuLabel>
          {views.length === 0 && (
            <div className="px-2 py-1.5 text-xs text-muted-foreground">
              Nothing saved yet — set filters, then
              &quot;Save current view&quot;.
            </div>
          )}
          {views.map((v) => (
            <DropdownMenuItem
              key={v.name}
              onClick={() => apply(v.query)}
              className="justify-between"
            >
              <span dir="auto" className="truncate">
                {v.name}
              </span>
              {activeName(v) && <Check className="h-3.5 w-3.5" />}
            </DropdownMenuItem>
          ))}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={() => {
              setName("");
              setSaveOpen(true);
            }}
          >
            Save current view…
          </DropdownMenuItem>
          <DropdownMenuItem
            disabled={views.length === 0}
            onClick={() => setManageOpen(true)}
          >
            Manage views…
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog open={saveOpen} onOpenChange={setSaveOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Save current view</DialogTitle>
          </DialogHeader>
          <div className="grid gap-1.5">
            <Label htmlFor={`${uid}-name`}>Name</Label>
            <Input
              id={`${uid}-name`}
              dir="auto"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") save();
              }}
              placeholder="e.g. Free addresses in DC-East"
            />
            {current ? (
              <p className="truncate font-mono text-xs text-muted-foreground">
                ?{current}
              </p>
            ) : (
              <p className="text-xs text-muted-foreground">
                The unfiltered view.
              </p>
            )}
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setSaveOpen(false)}>
              Cancel
            </Button>
            <Button onClick={save} disabled={!name.trim()}>
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={manageOpen} onOpenChange={setManageOpen}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Manage views</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            {views.map((v, i) => (
              <div key={i} className="flex items-center gap-2">
                <Input
                  dir="auto"
                  value={v.name}
                  aria-label={`Rename view ${v.name}`}
                  onChange={(e) => {
                    const next = [...views];
                    next[i] = { ...v, name: e.target.value };
                    writeViews(next);
                  }}
                />
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Delete view ${v.name}`}
                  onClick={() => writeViews(views.filter((_, j) => j !== i))}
                >
                  <Trash2 className="h-4 w-4 text-rose-400" />
                </Button>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
