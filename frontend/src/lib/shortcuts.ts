"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { moveRowNav } from "@/lib/row-nav";

// Global keyboard shortcuts — registered once in app-shell. Single-key
// shortcuts never fire inside editable elements or while a dialog/sheet is
// open (the palette is itself a dialog, so ⌘K stays reachable as its toggle
// while plain keys stay inert). `g` starts a navigation chord with a timeout.

const CHORD_TIMEOUT_MS = 800;

/** g-chord -> route. Kept next to NAV_GROUPS destinations in app-shell. */
export const G_CHORDS: Record<string, { href: string; label: string }> = {
  d: { href: "/", label: "Dashboard" },
  p: { href: "/prefixes", label: "Subnets" },
  s: { href: "/scans", label: "Scans" },
  i: { href: "/discovery", label: "Discovery inbox" },
  c: { href: "/changelog", label: "Changelog" },
  h: { href: "/docs", label: "Docs" },
};

export function isEditableTarget(el: EventTarget | null): boolean {
  if (!(el instanceof HTMLElement)) return false;
  const tag = el.tagName;
  return (
    tag === "INPUT" ||
    tag === "TEXTAREA" ||
    tag === "SELECT" ||
    el.isContentEditable
  );
}

function modalOpen(): boolean {
  // Radix dialogs plus popups that capture keys: dropdown menus and Select
  // listboxes — j/k must not move table rows behind an open menu.
  return Boolean(
    document.querySelector(
      '[role="dialog"], [role="alertdialog"], [role="menu"], [role="listbox"]'
    )
  );
}

export function useGlobalShortcuts({
  onPaletteToggle,
  onPaletteOpen,
  onHelpOpen,
  enabled = true,
}: {
  onPaletteToggle: () => void;
  onPaletteOpen: () => void;
  onHelpOpen: () => void;
  enabled?: boolean;
}) {
  const router = useRouter();

  useEffect(() => {
    if (!enabled) return;
    let chord = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const cancelChord = () => {
      chord = false;
      if (timer) clearTimeout(timer);
      timer = undefined;
    };

    const onKey = (e: KeyboardEvent) => {
      // ⌘K / Ctrl+K toggles the palette from anywhere, dialogs included.
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        onPaletteToggle();
        return;
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (isEditableTarget(e.target) || modalOpen()) {
        cancelChord();
        return;
      }

      if (chord) {
        cancelChord();
        const dest = G_CHORDS[e.key.toLowerCase()];
        if (dest) {
          e.preventDefault();
          router.push(dest.href);
        }
        return;
      }

      switch (e.key) {
        case "/":
          e.preventDefault();
          onPaletteOpen();
          break;
        case "?":
          e.preventDefault();
          onHelpOpen();
          break;
        case "g":
          chord = true;
          timer = setTimeout(cancelChord, CHORD_TIMEOUT_MS);
          break;
        case "j":
          if (moveRowNav(1)) e.preventDefault();
          break;
        case "k":
          if (moveRowNav(-1)) e.preventDefault();
          break;
      }
    };

    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
      cancelChord();
    };
  }, [enabled, router, onPaletteToggle, onPaletteOpen, onHelpOpen]);
}
