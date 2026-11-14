// Left navigation rail per SPEC §2. Highlights the active route via usePathname.
// Links to the six screens we actually build; Decision Lab + Brief + Frontier land later.

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type Item = { href: string; label: string; stage?: string; disabled?: boolean };

const ITEMS: Item[] = [
  { href: "/", label: "Mission Control", stage: "Stage 5" },
  { href: "/atlas", label: "Signal Atlas", stage: "Stage 6" },
  { href: "/trend-lab", label: "Trend Lab", stage: "Stage 6" },
  { href: "/compare", label: "Compare", stage: "Stage 8", disabled: true },
  { href: "/decision-lab", label: "Decision Lab", stage: "Stage 9", disabled: true },
  { href: "/brief", label: "Brief", stage: "Stage 9", disabled: true },
  { href: "/frontier", label: "Frontier", stage: "Stage 10", disabled: true },
];

export function LeftRail() {
  const pathname = usePathname();
  return (
    <nav
      aria-label="Primary"
      className="w-60 shrink-0 bg-surface/90 backdrop-blur border-r border-border py-4 flex flex-col text-sm"
    >
      <div className="px-5 pb-3 text-[10px] uppercase tracking-widest text-muted">
        Case file
      </div>
      {ITEMS.map((item) => {
        const active = pathname === item.href;
        if (item.disabled) {
          return (
            <span
              key={item.href}
              title={`Arrives at ${item.stage}`}
              className="px-5 py-2 text-muted opacity-50 cursor-not-allowed flex justify-between items-center"
            >
              <span>{item.label}</span>
              <span className="text-[10px]">{item.stage}</span>
            </span>
          );
        }
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={`px-5 py-2 flex justify-between items-center border-l-2 transition-colors ${
              active
                ? "border-accent bg-accent/10 text-accent"
                : "border-transparent text-text hover:bg-surface-2"
            }`}
          >
            <span>{item.label}</span>
            {active ? <span className="text-accent">●</span> : null}
          </Link>
        );
      })}
      <div className="mt-auto px-5 pt-6 text-[10px] text-muted leading-snug border-t border-border">
        NASA Space Apps 2026<br />
        Be an Earth System Trend Detective
      </div>
    </nav>
  );
}
