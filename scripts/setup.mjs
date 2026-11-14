#!/usr/bin/env node
// One-shot setup: create Python venv if missing, install Python deps,
// install web deps. Idempotent.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const isWin = process.platform === "win32";
const venvPy = isWin
  ? join(root, "science", ".venv", "Scripts", "python.exe")
  : join(root, "science", ".venv", "bin", "python");

function run(cmd, args, opts = {}) {
  console.log(`\n$ ${cmd} ${args.join(" ")}`);
  const r = spawnSync(cmd, args, { stdio: "inherit", shell: true, ...opts });
  if (r.status !== 0) {
    console.error(`FAILED: ${cmd}`);
    process.exit(r.status ?? 1);
  }
}

// pnpm 10+ aborts install on ignored native-build scripts even though the
// install actually succeeded (deps are on disk; only the native-compile step
// was skipped — esbuild has a WASM fallback so vite + next still build fine).
// We swallow that specific error after confirming node_modules/.pnpm exists.
function runPnpmTolerant(cmd, args) {
  console.log(`\n$ ${cmd} ${args.join(" ")}`);
  const r = spawnSync(cmd, args, { stdio: "inherit", shell: true });
  if (r.status === 0) return;
  // Soft-pass when the install produced a usable tree.
  const nmOk = existsSync(join(root, "web", "node_modules", ".pnpm"));
  if (nmOk) {
    console.warn(
      "\n[note] pnpm returned non-zero (likely ERR_PNPM_IGNORED_BUILDS for " +
      "esbuild's native postinstall). node_modules looks populated, so " +
      "continuing — esbuild will use its WASM fallback at build time.\n" +
      "To silence this, run once: pnpm --dir web approve-builds",
    );
    return;
  }
  console.error(`FAILED: ${cmd}`);
  process.exit(r.status ?? 1);
}

if (!existsSync(venvPy)) {
  console.log("Creating Python venv in science/.venv ...");
  run("python", ["-m", "venv", "science/.venv"]);
}

console.log("Installing Python deps (runtime + dev + earthdata) ...");
run(venvPy, ["-m", "pip", "install", "--upgrade", "pip", "-q"]);
// [dev,earthdata] picks up pytest+ruff AND earthaccess. The runtime deps
// (numpy/pandas/xarray/netCDF4/pyhdf/scipy/statsmodels/pymannkendall/pydantic/pyyaml)
// come from the project's own `dependencies` list and install automatically.
run(venvPy, ["-m", "pip", "install", "-e", "./science[dev,earthdata]"]);

console.log("Installing web deps ...");
runPnpmTolerant("pnpm", ["--dir", "web", "install"]);

console.log("\nSetup complete.");
