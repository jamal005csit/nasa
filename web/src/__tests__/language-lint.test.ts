// Language-rules lint. SPEC §3 forbids causation-implying phrases in any text
// the UI shows. The deterministic templates feeding the UI come from two
// places: (a) exported JSON string fields; (b) hand-written strings inside our
// own components. This test checks both.

import { describe, it, expect } from "vitest";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { resolve, join } from "node:path";

const DATA = resolve(__dirname, "..", "..", "public", "data");
const SRC = resolve(__dirname, "..");

// Keep in sync with science/config/analysis.yaml:language.forbidden_phrases
const FORBIDDEN = ["causes", "caused by", "due to", "proves", "proven", "proof"];

function readJson(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf-8"));
}

function walk(dir: string, files: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    const s = statSync(p);
    if (s.isDirectory()) {
      if (entry === "node_modules" || entry === ".next" || entry === "__tests__") continue;
      walk(p, files);
    } else if (p.endsWith(".tsx") || p.endsWith(".ts")) {
      files.push(p);
    }
  }
  return files;
}

function stringsInObject(obj: unknown, out: string[] = []): string[] {
  if (typeof obj === "string") out.push(obj);
  else if (Array.isArray(obj)) obj.forEach((v) => stringsInObject(v, out));
  else if (obj && typeof obj === "object") Object.values(obj).forEach((v) => stringsInObject(v, out));
  return out;
}

describe("Language rules — no causation phrases in UI text", () => {
  it("exported JSONs do not contain forbidden phrases", () => {
    const summary = readJson(resolve(DATA, "summary.json"));
    const nile = readJson(resolve(DATA, "regions", "nile_delta.json"));
    const sahara = readJson(resolve(DATA, "regions", "sahara_interior.json"));
    const all = [
      ...stringsInObject(summary),
      ...stringsInObject(nile),
      ...stringsInObject(sahara),
    ];
    for (const s of all) {
      const lower = s.toLowerCase();
      for (const bad of FORBIDDEN) {
        expect(
          lower.includes(bad),
          `Forbidden phrase "${bad}" found in exported string: "${s}"`,
        ).toBe(false);
      }
    }
  });

  it("component source files do not render forbidden phrases", () => {
    const sources = walk(SRC);
    const self = resolve(__filename);
    for (const file of sources) {
      if (file === self) continue;              // skip this test file itself
      const text = readFileSync(file, "utf-8").toLowerCase();
      // Strip single-line + block comments to avoid false positives on code annotations
      const code = text
        .replace(/\/\*[\s\S]*?\*\//g, "")
        .replace(/(^|\s)\/\/[^\n]*/g, "$1");
      for (const bad of FORBIDDEN) {
        // Only flag the phrase inside a quoted string literal (what the UI would render)
        const re = new RegExp(`['"\`][^'"\`\\n]*\\b${bad}\\b[^'"\`\\n]*['"\`]`, "i");
        expect(
          re.test(code),
          `Forbidden phrase "${bad}" found in a string literal inside ${file}`,
        ).toBe(false);
      }
    }
  });
});
