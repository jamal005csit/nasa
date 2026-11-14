# EARTH//NEXT — Deploy

Static export. No backend. No secrets reach the browser. The whole site is
`web/out/` — ~5.5 MB. Any static host works.

**Submission requirement** (Judging & Awards Guide): a **public, no-password
URL** by Nov 15, 11:59 p.m. local.

---

## Rebuild before every deploy

```powershell
npm.cmd run process      # regenerate JSONs from current data
npm.cmd run build        # Next.js static export -> web/out/
```

The output lands in `web/out/`. Upload that folder exactly.

## Option A — Vercel (recommended, 3 min)

Vercel is free for hobby projects, zero config, custom domain included.

```powershell
# one-time
npm.cmd i -g vercel
vercel login            # opens a browser, email or GitHub

# deploy (run from project root)
vercel deploy web/out --prod
```

The first run asks four questions:
1. Set up and deploy `web/out`? → **Y**
2. Which scope? → pick your account
3. Link to existing project? → **N**
4. Project name? → `earth-next` (or any name)

You'll get back a URL like `https://earth-next-abc123.vercel.app`. That's
your public URL. Subsequent `vercel deploy web/out --prod` runs redeploy to
the same URL.

### Vercel + GitHub (auto-deploy on push)

If you push the repo to GitHub, you can import it into Vercel's dashboard once
and get automatic redeploys on every push. Build settings:
- **Build command:** `cd .. && npm run process && pnpm --dir web build`
- **Output directory:** `web/out`
- **Root directory:** `web`
- **Install command:** leave default

(Note: if you go this route, Vercel will need to run `npm run process`, which
requires the real NASA data to be reachable. Easier to pre-build locally and
upload `web/out/` directly.)

## Option B — Netlify (3 min)

```powershell
npm.cmd i -g netlify-cli
netlify login
netlify deploy --dir web/out --prod
```

Same browser-OAuth flow as Vercel.

## Option C — Cloudflare Pages (free, generous bandwidth)

Push to GitHub first, then via `pages.cloudflare.com`:
- Connect to your repo
- **Framework preset:** None (we build locally)
- **Build output directory:** `web/out`
- **Build command:** leave empty, pre-build locally and commit `web/out/`

Or via CLI:
```powershell
npm.cmd i -g wrangler
wrangler login
wrangler pages deploy web/out --project-name earth-next
```

## Option D — zero-install sanity test

Before deploying, serve `web/out/` locally and click through all three routes:

```powershell
# from the project root
npx --yes serve web/out -p 5000
# then open http://localhost:5000
```

If the globe renders + all three routes work + DEMO banner state is correct,
it'll work on any of the hosts above.

## After deploying

1. Open the public URL in an **incognito window** (confirms no leftover cookies).
2. Walk the 10-point critical test from `docs/HANDOFF.md` on the live site.
3. **Paste the URL into the project submission form** on `spaceappschallenge.org`.
4. Add the URL to `docs/PROJECT_STATE.txt` under LOCKED DECISIONS.

## If something's broken on the live site

| Symptom | Cause | Fix |
|---|---|---|
| Blank page, console error about `/data/summary.json` 404 | You uploaded `web/` instead of `web/out/` | Upload `web/out/` |
| Globe is a black sphere | `/textures/earth.jpg` 404 | Confirm `web/out/textures/earth.jpg` exists; if not, rerun `python scripts/fetch_earth_texture.py` then rebuild |
| Routes 404 ( `/atlas` etc.) | Host doesn't follow `trailingSlash: true` convention | Our next.config emits `atlas/index.html` so most hosts work; if yours needs explicit redirects, add `"trailingSlash": "always"` or similar in the host's config |
| DEMO banner showing when you expected real data | `web/public/data/*.json` wasn't regenerated with real files before the build | `rm -rf web/out && npm run process && npm run build` and redeploy |
| Stale version served | Browser cache | Add `?v=2` to the URL once, or clear the host's edge cache |
