import { describe, it, expect } from "vitest";
import { formatCI, formatP, formatSlope, directionSymbol } from "../lib/format";

describe("formatSlope", () => {
  it("adds + sign on positive", () => {
    expect(formatSlope(0.00147)).toMatch(/^\+0\.00147$/);
  });
  it("renders negative with - sign", () => {
    // |0.5| picks 3 decimal digits via the dynamic-precision rule
    expect(formatSlope(-0.5)).toMatch(/^-0\.5\d*$/);
    expect(formatSlope(-0.5)).toContain("-");
  });
  it("includes units when given", () => {
    expect(formatSlope(0.1, "NDVI/yr")).toMatch(/NDVI\/yr$/);
  });
});

describe("formatP", () => {
  it("never shows 0.000", () => {
    expect(formatP(0)).toBe("p < 0.001");
    expect(formatP(0.0001)).toBe("p < 0.001");
  });
  it("shows p = 0.034 above threshold", () => {
    expect(formatP(0.034)).toBe("p = 0.034");
  });
});

describe("formatCI", () => {
  it("wraps in parentheses with the 95% CI label", () => {
    expect(formatCI([0.001, 0.002])).toContain("95% CI");
  });
});

describe("directionSymbol", () => {
  it("uses ↑/↓/— pairs", () => {
    expect(directionSymbol("increasing")).toBe("↑");
    expect(directionSymbol("decreasing")).toBe("↓");
    expect(directionSymbol("no trend")).toBe("—");
  });
});
