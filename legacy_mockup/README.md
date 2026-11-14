# Legacy mockup — NOT the EARTH//NEXT app

These two files were in the repo before Stage 1 started. They are a visual
design prototype, not the project this repo now builds.

- `index.html` — single-file Three.js globe UI, ~400 lines. Hardcoded regional
  numbers (Amazon Basin "+1.4°C", confidence "92%", etc.), fetches live from
  NASA POWER / FIRMS / EONET at runtime, has an "AI INSIGHTS" tab.
- `server.js` — Express proxy for the above.

**Neither file is used by the shipped app.** The shipped app lives under
`../web/` (Next.js static export) and is served by `npm run dev` from the
project root at http://localhost:3000. Its UI reads from exported JSON under
`web/public/data/`, never from live network calls.

Kept here because the visual language (dark navy + cyan accent, left data-layer
rail, right regional card, bottom time scrubber) is a useful reference for the
Stage-10 design polish pass. Safe to delete at Stage 11 if not needed.
