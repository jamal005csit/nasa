// URL query-state as a shared React context. SPEC §2 requires the URL to carry
// state (?var=&region=&period=&scenario=). Earlier revision used a
// per-component hook, which gave each caller its own private state copy →
// RegionPicker's update never reached TrendLab. Context fixes that.

"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

export type AppState = {
  region: string;
  year: number | null; // null => "latest"
};

const DEFAULTS: AppState = { region: "nile_delta", year: null };

type Ctx = [AppState, (patch: Partial<AppState>) => void];

const AppStateContext = createContext<Ctx>([DEFAULTS, () => {}]);

function readFromUrl(): AppState {
  if (typeof window === "undefined") return DEFAULTS;
  const p = new URLSearchParams(window.location.search);
  const region = p.get("region") ?? DEFAULTS.region;
  const yearStr = p.get("year");
  const year = yearStr && /^\d{4}$/.test(yearStr) ? parseInt(yearStr, 10) : null;
  return { region, year };
}

function writeToUrl(s: AppState): void {
  if (typeof window === "undefined") return;
  const p = new URLSearchParams();
  if (s.region !== DEFAULTS.region) p.set("region", s.region);
  if (s.year !== null) p.set("year", String(s.year));
  const qs = p.toString();
  const next = qs ? `?${qs}` : window.location.pathname;
  window.history.replaceState(null, "", next);
}

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [s, setS] = useState<AppState>(DEFAULTS);

  useEffect(() => {
    setS(readFromUrl());
    const onPop = () => setS(readFromUrl());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const update = useCallback((patch: Partial<AppState>) => {
    setS((prev) => {
      const next = { ...prev, ...patch };
      writeToUrl(next);
      return next;
    });
  }, []);

  return (
    <AppStateContext.Provider value={[s, update]}>{children}</AppStateContext.Provider>
  );
}

export function useAppState(): Ctx {
  return useContext(AppStateContext);
}
