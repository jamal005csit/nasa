// Stage-4 TS side of the round-trip contract: every file in web/public/data/
// must validate against the matching Zod schema. If this test fails but the
// Python test (science/tests/test_export.py) passes, the schemas have drifted.

import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, it, expect } from "vitest";
import { RegionExport, Summary } from "../lib/schemas";

const DATA = resolve(__dirname, "..", "..", "public", "data");

function load(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf-8"));
}

describe("exported JSON schema parity (zod side)", () => {
  it("summary.json parses", () => {
    const parsed = Summary.safeParse(load(resolve(DATA, "summary.json")));
    if (!parsed.success) {
      console.error(parsed.error.format());
    }
    expect(parsed.success).toBe(true);
  });

  it.each(["nile_delta", "sahara_interior"])(
    "regions/%s.json parses",
    (slug) => {
      const parsed = RegionExport.safeParse(
        load(resolve(DATA, "regions", `${slug}.json`))
      );
      if (!parsed.success) {
        console.error(parsed.error.format());
      }
      expect(parsed.success).toBe(true);
    }
  );

  it("summary featured region exists in regions list", () => {
    const summary = Summary.parse(load(resolve(DATA, "summary.json")));
    const slugs = new Set(summary.regions.map((r) => r.slug));
    expect(slugs.has(summary.featured_finding.region_slug)).toBe(true);
  });
});
