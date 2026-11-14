// Evidence Receipt drawer. Opens on click; shows the provenance record that
// backs the displayed numbers. Fulfils SPEC §2 item 3's receipt requirement.

"use client";

import { useEffect, useState } from "react";
import type { RegionExportT } from "@/lib/schemas";

export function EvidenceReceipt({ region }: { region: RegionExportT }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="text-xs text-accent border border-accent/40 rounded px-2 py-1 hover:bg-accent/10"
        data-testid="evidence-receipt-open"
      >
        Evidence Receipt
      </button>

      {open ? (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Evidence Receipt"
          className="fixed inset-0 z-50 bg-bg/80 flex justify-end"
          onClick={() => setOpen(false)}
        >
          <aside
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-xl h-full bg-surface border-l border-border overflow-y-auto p-6"
            data-testid="evidence-receipt-panel"
          >
            <header className="flex justify-between items-center mb-4">
              <h2 className="text-lg">Evidence Receipt</h2>
              <button
                onClick={() => setOpen(false)}
                aria-label="Close"
                className="text-muted hover:text-text text-2xl leading-none"
              >
                ×
              </button>
            </header>

            <Section title="What was computed">
              <Field name="Variable" value={region.provenance.variable} />
              <Field name="Dataset" value={region.provenance.dataset} />
              <Field name="Region" value={region.region.name} />
              <Field
                name="Time range"
                value={`${region.provenance.time_range[0]} → ${region.provenance.time_range[1]}`}
              />
              <Field name="Resolution" value={region.provenance.resolution} />
            </Section>

            <Section title="How it was computed">
              <Field name="Estimator" value={region.provenance.method.estimator ?? "—"} />
              <Field name="Significance test" value={region.provenance.method.test ?? "—"} />
              <Field name="Alpha" value={String(region.provenance.method.alpha ?? "—")} />
              <Field name="FDR method" value={region.provenance.method.fdr_method ?? "—"} />
              <div className="pt-2">
                <div className="text-xs text-muted mb-1">Filters applied</div>
                <ul className="list-disc ml-4 text-sm text-muted space-y-0.5">
                  {region.provenance.filters_applied.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>
            </Section>

            <Section title="Coverage">
              <Field
                name="Valid annual means"
                value={`${region.coverage.n_valid_years}/${region.coverage.n_total_years}`}
              />
              <Field
                name="Missing months"
                value={`${region.coverage.missing_pct.toFixed(2)} %`}
              />
            </Section>

            <Section title="Reproducibility">
              <Field name="Script commit" value={region.provenance.script_commit} />
              <Field name="Config hash" value={shorten(region.provenance.config_hash)} />
              <Field name="Data checksum" value={shorten(region.provenance.data_checksum)} />
              <Field name="Generated at" value={region.provenance.generated_at} />
              <div className="pt-2">
                <div className="text-xs text-muted mb-1">Library versions</div>
                <ul className="text-xs text-muted font-mono grid grid-cols-2 gap-x-6">
                  {Object.entries(region.provenance.library_versions).map(([k, v]) => (
                    <li key={k} className="flex justify-between">
                      <span>{k}</span>
                      <span>{v}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </Section>

            <Section title="Source">
              <a
                href={region.provenance.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-accent underline break-all"
              >
                {region.provenance.source_url}
              </a>
            </Section>

            <p className="text-xs text-muted pt-6 border-t border-border">
              Every number shown on this screen can be re-derived from exactly these
              inputs. Change one field in the config and the hash changes.
            </p>
          </aside>
        </div>
      ) : null}
    </>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-6">
      <h3 className="text-xs uppercase tracking-widest text-muted mb-2">{title}</h3>
      <div className="space-y-1 text-sm">{children}</div>
    </section>
  );
}

function Field({ name, value }: { name: string; value: string }) {
  return (
    <div className="flex justify-between gap-4">
      <span className="text-muted">{name}</span>
      <span className="font-mono text-right">{value}</span>
    </div>
  );
}

function shorten(h: string): string {
  if (h.length <= 16) return h;
  return `${h.slice(0, 8)}…${h.slice(-4)}`;
}
