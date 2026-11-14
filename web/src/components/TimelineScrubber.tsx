// Bottom timeline scrubber — "Time Machine" styling borrowed from the
// legacy_mockup, data-driven from summary.time_range.

"use client";

import type { SummaryT } from "@/lib/schemas";
import { useAppState } from "@/lib/url-state";

function yearOf(iso: string): number {
  return parseInt(iso.slice(0, 4), 10);
}

export function TimelineScrubber({ summary }: { summary: SummaryT }) {
  const [state, update] = useAppState();
  const min = yearOf(summary.time_range[0]);
  const max = yearOf(summary.time_range[1]);
  const value = state.year ?? max;

  return (
    <footer
      aria-label="Timeline"
      className="mx-4 mb-4 pill-glass !rounded-2xl !p-4 z-10"
    >
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className="w-9 h-9 rounded-full grid place-items-center bg-accent/20 text-accent text-lg border border-accent/40"
          >
            🕐
          </span>
          <div>
            <div className="text-xs text-text font-semibold tracking-wide">TIME MACHINE</div>
            <div className="text-[10px] text-muted">Explore Earth through time</div>
          </div>
        </div>
        <span className="text-muted font-mono text-xs min-w-12 text-right">{min}</span>
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          aria-label={`Year, between ${min} and ${max}`}
          onChange={(e) => update({ year: parseInt(e.target.value, 10) })}
          className="flex-1 accent-accent"
          data-testid="timeline-input"
        />
        <span className="text-muted font-mono text-xs min-w-12">{max}</span>
        <span
          className="font-mono tabular-nums text-accent text-2xl min-w-16 text-right"
          data-testid="timeline-value"
        >
          {value}
        </span>
        <button
          onClick={() => update({ year: null })}
          className="text-xs text-muted hover:text-text border border-border rounded-md px-3 py-1.5 transition-colors"
          disabled={state.year === null}
        >
          Latest
        </button>
      </div>
    </footer>
  );
}
