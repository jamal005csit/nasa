// Pure formatting helpers. No side effects, trivially unit-testable.

export function formatSlope(slope: number, units = ""): string {
  const abs = Math.abs(slope);
  const digits = abs === 0 ? 4 : Math.max(2, Math.min(5, -Math.floor(Math.log10(abs)) + 2));
  const sign = slope >= 0 ? "+" : "";
  const body = `${sign}${slope.toFixed(digits)}`;
  return units ? `${body} ${units}` : body;
}

export function formatCI([lo, hi]: readonly [number, number]): string {
  return `(95% CI ${formatSlope(lo)}, ${formatSlope(hi)})`;
}

/** SPEC §3 rule 13: p is displayed as "p < 0.001" or "p = 0.034", never 0.000. */
export function formatP(p: number): string {
  if (p < 0.001) return "p < 0.001";
  return `p = ${p.toFixed(3)}`;
}

export function directionSymbol(dir: "increasing" | "decreasing" | "no trend"): string {
  if (dir === "increasing") return "↑";
  if (dir === "decreasing") return "↓";
  return "—";
}
