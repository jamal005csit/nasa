// Shared summary loader + context. One fetch per visit; all screens share it.

"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { loadSummary } from "./data";
import type { SummaryT } from "./schemas";

type State =
  | { kind: "loading" }
  | { kind: "ready"; summary: SummaryT }
  | { kind: "error"; message: string };

const SummaryContext = createContext<State>({ kind: "loading" });

export function SummaryProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    loadSummary()
      .then((s) => !cancelled && setState({ kind: "ready", summary: s }))
      .catch((e) => !cancelled && setState({ kind: "error", message: String(e) }));
    return () => {
      cancelled = true;
    };
  }, []);

  return <SummaryContext.Provider value={state}>{children}</SummaryContext.Provider>;
}

export function useSummary(): State {
  return useContext(SummaryContext);
}
