"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

// Light client-side sanity check; the API remains the real validator.
const CIDR_RE =
  /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$|^([0-9a-fA-F:]+|::)\/\d{1,3}$/;

export function CidrListEditor({
  value,
  onChange,
  placeholder = "10.0.0.0/8",
}: {
  value: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
}) {
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);

  const add = () => {
    const v = draft.trim();
    if (!v) return;
    if (!CIDR_RE.test(v)) {
      setError("not a CIDR (e.g. 192.168.1.0/24)");
      return;
    }
    if (value.includes(v)) {
      setError("already in the list");
      return;
    }
    onChange([...value, v]);
    setDraft("");
    setError(null);
  };

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <Input
          value={draft}
          placeholder={placeholder}
          onChange={(e) => {
            setDraft(e.target.value);
            setError(null);
          }}
          onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), add())}
          className="font-mono text-xs"
        />
        <Button type="button" variant="outline" size="sm" onClick={add}>
          <Plus /> Add
        </Button>
      </div>
      {error && <p className="text-xs text-rose-400">{error}</p>}
      {value.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {value.map((cidr) => (
            <span
              key={cidr}
              className="inline-flex items-center gap-1 rounded-md border px-2 py-0.5 font-mono text-xs"
            >
              {cidr}
              <button
                type="button"
                className="text-muted-foreground hover:text-rose-400"
                onClick={() => onChange(value.filter((c) => c !== cidr))}
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
