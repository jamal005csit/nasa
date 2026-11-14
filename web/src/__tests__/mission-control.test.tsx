// Mission Control component tests. We stub the globe (ssr:false + three.js
// isn't test-friendly) and verify every number on screen comes from the loaded
// summary JSON, plus the DEMO banner logic.

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Stub the globe before any component that transitively imports it.
vi.mock("../components/PlanetGlobe", () => ({
  default: () => <div data-testid="planet-globe-stub">stub</div>,
}));

import { MissionControl } from "../components/MissionControl";
import { DemoBanner } from "../components/DemoBanner";
import { FeaturedFindingCard } from "../components/FeaturedFindingCard";
import { TopNavigation } from "../components/TopNavigation";
import { SummaryProvider } from "../lib/summary-context";
import type { SummaryT } from "../lib/schemas";

const DATA = resolve(__dirname, "..", "..", "public", "data");
const summary = JSON.parse(
  readFileSync(resolve(DATA, "summary.json"), "utf-8")
) as SummaryT;

beforeEach(() => {
  // Mock fetch for loadSummary — MissionControl pulls /data/summary.json
  // from the dev server at runtime; in jsdom we serve it directly.
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const name = url.replace(/^\/data\//, "");
      const path = resolve(DATA, name);
      return new Response(readFileSync(path, "utf-8"), { status: 200 });
    })
  );
});

describe("DemoBanner", () => {
  // Tests build their own SourceLabel rather than relying on whatever
  // summary.json is on disk right now (it flips DEMO ↔ NASA as real data
  // arrives, and these tests exist to pin the UI branch logic, not the data).
  it("shows when source.kind === 'DEMO'", () => {
    const s = { ...summary,
      source: { kind: "DEMO" as const, note: "Illustrative — not NASA data." } };
    render(<DemoBanner summary={s} />);
    expect(screen.getByTestId("demo-banner")).toBeInTheDocument();
    expect(screen.getByTestId("demo-banner").textContent?.toLowerCase())
      .toContain("not nasa data");
  });

  it("hides when source.kind === 'NASA'", () => {
    const s = { ...summary, source: { kind: "NASA" as const, note: "real data" } };
    const { container } = render(<DemoBanner summary={s} />);
    expect(container.firstChild).toBeNull();
  });
});

describe("TopNavigation", () => {
  it("renders dataset chip from summary (no hardcoded dataset name)", () => {
    render(<TopNavigation summary={summary} />);
    const chip = screen.getByTestId("dataset-chip");
    expect(chip.textContent).toContain(summary.dataset_short_name);
    expect(chip.textContent).toContain(summary.dataset_version);
  });
});

describe("FeaturedFindingCard", () => {
  it("every number on the card maps to summary.featured_finding.*", () => {
    render(<FeaturedFindingCard summary={summary} />);
    const f = summary.featured_finding;
    // slope: tolerant string check (format helper uses +sign + up to 5 digits)
    const slopeText = screen.getByTestId("featured-slope").textContent ?? "";
    const expectedAbs = Math.abs(f.slope_per_year).toFixed(5);
    expect(slopeText.replace(/[^\d.]/g, "")).toContain(expectedAbs.slice(0, 5));
    // sentence copied verbatim from JSON (deterministic template)
    expect(screen.getByTestId("featured-sentence").textContent).toBe(f.sentence);
  });
});

describe("MissionControl integration (inside SummaryProvider)", () => {
  it("loads summary via fetch and renders the featured finding", async () => {
    render(
      <SummaryProvider>
        <MissionControl />
      </SummaryProvider>,
    );
    await waitFor(() => {
      expect(screen.getByTestId("featured-finding")).toBeInTheDocument();
    });
    expect(screen.getByTestId("featured-sentence").textContent)
      .toBe(summary.featured_finding.sentence);
  });
});
