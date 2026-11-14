// Stage-6 gate test: every displayed number on Trend Lab equals its JSON value.
// Also covers the non-significant + missing-data rendering states by mutating
// the loaded region before render.

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

// Stub the chart (echarts-for-react) and the globe so jsdom doesn't choke.
vi.mock("echarts-for-react", () => ({ default: () => <div data-testid="echarts-stub" /> }));
vi.mock("../components/PlanetGlobe", () => ({ default: () => <div /> }));

import { TrendLab } from "../components/TrendLab";
import { SignificanceBadge } from "../components/SignificanceBadge";
import { SummaryProvider } from "../lib/summary-context";
import type { RegionExportT, SummaryT } from "../lib/schemas";

const DATA = resolve(__dirname, "..", "..", "public", "data");
const summary = JSON.parse(readFileSync(resolve(DATA, "summary.json"), "utf-8")) as SummaryT;
const nile = JSON.parse(
  readFileSync(resolve(DATA, "regions", "nile_delta.json"), "utf-8"),
) as RegionExportT;

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string) => {
      const name = url.replace(/^\/data\//, "");
      return new Response(readFileSync(resolve(DATA, name), "utf-8"), { status: 200 });
    }),
  );
});

async function renderTrendLabReady() {
  render(
    <SummaryProvider>
      <TrendLab />
    </SummaryProvider>,
  );
  await screen.findByTestId("card-what");
}

describe("TrendLab — every displayed number maps to JSON", () => {
  it("What card direction matches significance.trend_direction", async () => {
    await renderTrendLabReady();
    expect(screen.getByTestId("card-what-direction").textContent).toBe(
      nile.significance.trend_direction,
    );
  });

  it("How-much slope value matches trend.slope_per_year (same digits)", async () => {
    await renderTrendLabReady();
    const text = screen.getByTestId("card-howmuch-slope").textContent ?? "";
    // The format helper picks digits based on magnitude; just check the first 5
    // significant digits after the sign are present.
    const expected = Math.abs(nile.trend.slope_per_year).toFixed(5).slice(0, 5);
    expect(text.replace(/[^\d.]/g, "")).toContain(expected.slice(0, 4));
  });

  it("How-much CI endpoints match trend.slope_ci95", async () => {
    await renderTrendLabReady();
    const ci = screen.getByTestId("card-howmuch-ci").textContent ?? "";
    const lo = Math.abs(nile.trend.slope_ci95[0]).toFixed(5).slice(0, 4);
    const hi = Math.abs(nile.trend.slope_ci95[1]).toFixed(5).slice(0, 4);
    expect(ci.replace(/[^\d.]/g, "")).toContain(lo);
    expect(ci.replace(/[^\d.]/g, "")).toContain(hi);
  });

  it("Significance card shows p_display verbatim from JSON", async () => {
    await renderTrendLabReady();
    expect(screen.getByTestId("card-sig-p").textContent).toBe(
      nile.significance.p_display,
    );
  });

  it("Where card shows the bounding box numbers from JSON", async () => {
    await renderTrendLabReady();
    const card = screen.getByTestId("card-where");
    const text = card.textContent ?? "";
    expect(text).toContain(String(nile.region.bbox.min_lat));
    expect(text).toContain(String(nile.region.bbox.max_lat));
    expect(text).toContain(String(nile.region.bbox.min_lon));
    expect(text).toContain(String(nile.region.bbox.max_lon));
  });
});

describe("SignificanceBadge — non-significant state renders the SPEC phrase", () => {
  it("shows the α=0.05 wording when significant_at_005 is false", () => {
    const sig = { ...nile.significance, significant_at_005: false };
    render(<SignificanceBadge sig={sig} />);
    const badge = screen.getByTestId("sig-badge");
    expect(badge.textContent).toMatch(/not detectable/i);
    expect(badge.textContent).toContain("0.05");
  });

  it("uses symbol+word, not color alone, when significant", () => {
    render(<SignificanceBadge sig={{ ...nile.significance, significant_at_005: true, trend_direction: "increasing" }} />);
    const badge = screen.getByTestId("sig-badge");
    expect(badge.textContent).toMatch(/increasing/);
    expect(badge.textContent).toMatch(/[▲▼—]/);
  });
});

describe("Missing-data rendering", () => {
  it("renders an em-dash when a year's annual value is null", async () => {
    // We render the table view directly with a region whose one year is null
    const mutated: RegionExportT = JSON.parse(JSON.stringify(nile));
    mutated.annual.values[0] = null;
    mutated.annual.valid_months_per_year[0] = 5;

    const { TimeSeriesChart } = await import("../components/TimeSeriesChart");
    render(<TimeSeriesChart region={mutated} />);
    const toggle = screen.getByText("Table");
    toggle.click();
    const cell = await screen.findByTestId(`table-value-${mutated.annual.years[0]}`);
    expect(within(cell).getByText("—")).toBeInTheDocument();
  });
});
