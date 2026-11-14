// Zod schemas for every JSON exported under web/public/data/.
// Mirror the pydantic models in science/src/earthnext/schemas.py.
// Keep the two in sync; the Stage-4 round-trip test will catch drift.

import { z } from "zod";

export const SourceLabel = z.object({
  kind: z.enum(["DEMO", "NASA"]),
  note: z.string(),
});

export const BBox = z.object({
  min_lat: z.number(),
  max_lat: z.number(),
  min_lon: z.number(),
  max_lon: z.number(),
});

export const RegionMeta = z.object({
  slug: z.string(),
  name: z.string(),
  bbox: BBox,
});

export const AnnualSeries = z.object({
  years: z.array(z.number().int()),
  values: z.array(z.number().nullable()),
  valid_months_per_year: z.array(z.number().int()),
});

export const TrendResult = z.object({
  estimator: z.literal("theil_sen"),
  slope_per_year: z.number(),
  slope_ci95: z.tuple([z.number(), z.number()]),
  slope_ci_excludes_zero: z.boolean(),
  intercept: z.number(),
  n: z.number().int(),
  units: z.string(),
});

export const SignificanceResult = z.object({
  test: z.enum(["original", "hamed_rao", "prewhitened"]),
  p: z.number(),
  z: z.number(),
  tau: z.number(),
  trend_direction: z.enum(["increasing", "decreasing", "no trend"]),
  lag1_autocorr: z.number().nullable(),
  significant_at_005: z.boolean(),
  p_display: z.string(),
});

export const Coverage = z.object({
  n_valid_years: z.number().int(),
  n_total_years: z.number().int(),
  missing_pct: z.number(),
});

export const Method = z.object({
  estimator: z.string().nullable(),
  test: z.string().nullable(),
  fdr_method: z.string().nullable(),
  alpha: z.number().nullable(),
});

export const Provenance = z.object({
  dataset: z.string(),
  source_url: z.string(),
  variable: z.string(),
  units: z.string(),
  time_range: z.tuple([z.string(), z.string()]),
  spatial_extent: BBox,
  resolution: z.string(),
  filters_applied: z.array(z.string()),
  method: Method,
  n_valid: z.number().int().nullable(),
  missing_pct: z.number().nullable(),
  slope: z.number().nullable(),
  slope_ci95: z.tuple([z.number(), z.number()]).nullable(),
  p: z.number().nullable(),
  q: z.number().nullable(),
  script_commit: z.string(),
  config_hash: z.string(),
  data_checksum: z.string(),
  library_versions: z.record(z.string(), z.string()),
  generated_at: z.string(),
});

export const FeaturedFinding = z.object({
  region_slug: z.string(),
  sentence: z.string(),
  slope_per_year: z.number(),
  slope_ci95: z.tuple([z.number(), z.number()]),
  p: z.number(),
  esi_grade: z.enum(["A", "B", "C", "D"]).nullable(),
});

export const Summary = z.object({
  source: SourceLabel,
  generated_at: z.string(),
  dataset_short_name: z.string(),
  dataset_version: z.string(),
  variable: z.string(),
  units: z.string(),
  time_range: z.tuple([z.string(), z.string()]),
  regions: z.array(RegionMeta),
  featured_finding: FeaturedFinding,
});

export const RegionExport = z.object({
  source: SourceLabel,
  region: RegionMeta,
  annual: AnnualSeries,
  trend: TrendResult,
  significance: SignificanceResult,
  coverage: Coverage,
  provenance: Provenance,
});

export type SummaryT = z.infer<typeof Summary>;
export type RegionExportT = z.infer<typeof RegionExport>;
