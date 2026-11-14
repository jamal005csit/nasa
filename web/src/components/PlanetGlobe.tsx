// 3D globe using react-globe.gl. Client-only (three.js in the browser).
// Falls back to a static 2D map if WebGL is unavailable.

"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";

import type { SummaryT } from "@/lib/schemas";

type Props = { summary: SummaryT };

// react-globe.gl is browser-only. Dynamic import with ssr:false.
const Globe = dynamic(() => import("react-globe.gl").then((m) => m.default), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 flex items-center justify-center text-muted">
      Loading globe…
    </div>
  ),
});

function webglSupported(): boolean {
  if (typeof window === "undefined") return false;
  try {
    const canvas = document.createElement("canvas");
    const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    return !!gl;
  } catch {
    return false;
  }
}

function prefersReducedMotion(): boolean {
  if (typeof window === "undefined") return false;
  return window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches ?? false;
}

export default function PlanetGlobe({ summary }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mode, setMode] = useState<"loading" | "3d" | "2d">("loading");
  const [size, setSize] = useState<{ w: number; h: number }>({ w: 800, h: 600 });
  // react-globe.gl exposes an imperative handle for controls; we cast to avoid
  // dragging three.js types into our bundle.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const globeRef = useRef<any>(null);

  useEffect(() => {
    if (!webglSupported()) {
      setMode("2d");
      return;
    }
    setMode("3d");
  }, []);

  // Keep the globe sized to its container (SPEC: first-class at 1440 and 1280x720).
  useEffect(() => {
    if (mode !== "3d" || !containerRef.current) return;
    const el = containerRef.current;
    const measure = () => setSize({ w: el.clientWidth, h: el.clientHeight });
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [mode]);

  // Auto-rotate unless reduced motion is preferred.
  useEffect(() => {
    if (mode !== "3d" || !globeRef.current) return;
    const controls = globeRef.current.controls?.();
    if (controls) {
      controls.autoRotate = !prefersReducedMotion();
      controls.autoRotateSpeed = 0.35;
    }
  }, [mode, size]);

  if (mode === "2d") {
    return <PlanetGlobe2DFallback summary={summary} reason="no WebGL" />;
  }

  const points = summary.regions.map((r) => ({
    lat: (r.bbox.min_lat + r.bbox.max_lat) / 2,
    lng: (r.bbox.min_lon + r.bbox.max_lon) / 2,
    label: r.name,
  }));

  return (
    <div
      ref={containerRef}
      className="absolute inset-0"
      data-testid="planet-globe-mount"
      aria-label="Rotating 3D globe showing study regions"
      role="img"
    >
      <Globe
        ref={globeRef}
        width={size.w}
        height={size.h}
        backgroundColor="#070B14"
        globeImageUrl="/textures/earth.jpg"
        showAtmosphere
        atmosphereColor="#38D7FF"
        atmosphereAltitude={0.18}
        pointsData={points}
        pointColor={() => "#38D7FF"}
        pointAltitude={0.03}
        pointRadius={0.6}
        pointLabel={(p: object) => (p as { label: string }).label}
      />
    </div>
  );
}

function PlanetGlobe2DFallback({
  summary,
  reason,
}: {
  summary: SummaryT;
  reason: string;
}) {
  return (
    <div
      className="absolute inset-0 flex items-center justify-center bg-bg"
      data-testid="planet-globe-fallback"
      role="img"
      aria-label={`2D map fallback (${reason})`}
    >
      <svg viewBox="-180 -90 360 180" className="w-full max-w-4xl h-auto" aria-hidden="true">
        <rect x="-180" y="-90" width="360" height="180" fill="#0E1624" stroke="#1C2A44" />
        <line x1="-180" y1="0" x2="180" y2="0" stroke="#1C2A44" strokeDasharray="2 2" />
        <line x1="0" y1="-90" x2="0" y2="90" stroke="#1C2A44" strokeDasharray="2 2" />
        {summary.regions.map((r) => {
          const cx = (r.bbox.min_lon + r.bbox.max_lon) / 2;
          const cy = -((r.bbox.min_lat + r.bbox.max_lat) / 2);
          return (
            <g key={r.slug}>
              <rect
                x={r.bbox.min_lon}
                y={-r.bbox.max_lat}
                width={r.bbox.max_lon - r.bbox.min_lon}
                height={r.bbox.max_lat - r.bbox.min_lat}
                fill="#38D7FF22"
                stroke="#38D7FF"
                strokeWidth={0.5}
              />
              <circle cx={cx} cy={cy} r={1.5} fill="#38D7FF" />
              <text
                x={cx + 2}
                y={cy + 1}
                fontSize={4}
                fill="#EAF1FB"
                style={{ fontFamily: "sans-serif" }}
              >
                {r.name}
              </text>
            </g>
          );
        })}
      </svg>
      <p className="absolute bottom-4 left-1/2 -translate-x-1/2 text-xs text-muted">
        2D map ({reason}). Globe view unavailable.
      </p>
    </div>
  );
}
