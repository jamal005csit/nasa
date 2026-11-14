// Mission Control page body. Shell (top nav + rail + demo banner) is in AppShell.

"use client";

import dynamic from "next/dynamic";

import { FeaturedFindingCard } from "./FeaturedFindingCard";
import { TimelineScrubber } from "./TimelineScrubber";
import { useSummary } from "@/lib/summary-context";

const PlanetGlobe = dynamic(() => import("./PlanetGlobe"), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center text-muted">
      Loading globe…
    </div>
  ),
});

export function MissionControl() {
  const state = useSummary();
  if (state.kind !== "ready") return null; // AppShell already showed loading/error
  const { summary } = state;
  const lastUpdate = new Date(summary.generated_at).toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
  return (
    <div className="flex flex-col h-full bg-space">
      <div className="flex-1 relative overflow-hidden">
        <PlanetGlobe summary={summary} />

        {/* Last-update pill, top-left */}
        <div className="absolute top-6 left-6 z-10 pill-glass text-xs text-muted">
          <div className="uppercase tracking-widest text-[10px]">🛰 Last update</div>
          <div className="text-text font-mono mt-0.5">{lastUpdate}</div>
        </div>

        {/* Featured finding, top-right */}
        <div className="absolute top-6 right-6 z-10">
          <FeaturedFindingCard summary={summary} />
        </div>

        {/* Centered hint, bottom of globe area */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 pill-glass text-xs text-muted text-center z-10">
          <div className="text-text font-semibold">Earth · 3D view</div>
          <div className="mt-0.5">Drag to rotate · Scroll to zoom · Hover a marker for the region name</div>
        </div>
      </div>
      <TimelineScrubber summary={summary} />
    </div>
  );
}
