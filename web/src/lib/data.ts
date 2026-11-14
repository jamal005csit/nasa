// Data loader for every exported JSON under /data/.
// Every number in the UI flows through this module; components never hardcode.

import { RegionExport, Summary, type RegionExportT, type SummaryT } from "./schemas";

const BASE = (typeof window === "undefined" ? "" : "") + "/data";

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`fetch ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

export async function loadSummary(): Promise<SummaryT> {
  return Summary.parse(await fetchJson("/summary.json"));
}

export async function loadRegion(slug: string): Promise<RegionExportT> {
  return RegionExport.parse(await fetchJson(`/regions/${slug}.json`));
}
