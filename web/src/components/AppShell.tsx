// Shared layout: DEMO banner + top nav + left rail + page content.
// All screens live inside this shell; children is the page body.

"use client";

import { DemoBanner } from "./DemoBanner";
import { LeftRail } from "./LeftRail";
import { TopNavigation } from "./TopNavigation";
import { useSummary } from "@/lib/summary-context";

export function AppShell({ children }: { children: React.ReactNode }) {
  const state = useSummary();

  if (state.kind === "loading") {
    return (
      <main className="h-screen grid place-items-center bg-bg text-muted">
        Loading data…
      </main>
    );
  }
  if (state.kind === "error") {
    return (
      <main className="h-screen grid place-items-center bg-bg text-negative text-center">
        Could not load <code>/data/summary.json</code>.
        <br />
        <small>{state.message}</small>
      </main>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-space text-text">
      <DemoBanner summary={state.summary} />
      <TopNavigation summary={state.summary} />
      <div className="flex-1 flex overflow-hidden">
        <LeftRail />
        <section className="flex-1 overflow-auto relative">{children}</section>
      </div>
    </div>
  );
}
