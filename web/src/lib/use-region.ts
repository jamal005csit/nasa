// Hook that resolves the currently-selected region slug to its loaded JSON.
// Lazy-loads the region file on first use and caches it.

"use client";

import { useEffect, useState } from "react";
import { loadRegion } from "./data";
import type { RegionExportT } from "./schemas";
import { useAppState } from "./url-state";

const cache = new Map<string, RegionExportT>();

type State =
  | { kind: "loading" }
  | { kind: "ready"; region: RegionExportT }
  | { kind: "error"; message: string };

export function useRegion(): State {
  const [state, setState] = useState<State>({ kind: "loading" });
  const [appState] = useAppState();
  const slug = appState.region;

  useEffect(() => {
    let cancelled = false;
    const cached = cache.get(slug);
    if (cached) {
      setState({ kind: "ready", region: cached });
      return;
    }
    setState({ kind: "loading" });
    loadRegion(slug)
      .then((r) => {
        if (cancelled) return;
        cache.set(slug, r);
        setState({ kind: "ready", region: r });
      })
      .catch((e) => !cancelled && setState({ kind: "error", message: String(e) }));
    return () => {
      cancelled = true;
    };
  }, [slug]);

  return state;
}
