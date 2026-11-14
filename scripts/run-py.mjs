#!/usr/bin/env node
// Cross-platform shim: invokes the project's Python venv with the given args.
// On Windows the venv python lives under Scripts/, on POSIX under bin/.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const winPy = join(root, "science", ".venv", "Scripts", "python.exe");
const posixPy = join(root, "science", ".venv", "bin", "python");
const py = existsSync(winPy) ? winPy : posixPy;

if (!existsSync(py)) {
  console.error("Python venv not found. Run: npm run setup");
  process.exit(1);
}

const r = spawnSync(py, process.argv.slice(2), { stdio: "inherit" });
process.exit(r.status ?? 1);
