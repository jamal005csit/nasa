#!/usr/bin/env node
// Data-processing pipeline. Stage 2: ingest + validate.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const isWin = process.platform === "win32";
const py = isWin
  ? join(root, "science", ".venv", "Scripts", "python.exe")
  : join(root, "science", ".venv", "bin", "python");

if (!existsSync(py)) {
  console.error("Python venv not found. Run: npm run setup");
  process.exit(1);
}

const r = spawnSync(py, ["-m", "earthnext.pipeline"], { stdio: "inherit" });
process.exit(r.status ?? 1);
