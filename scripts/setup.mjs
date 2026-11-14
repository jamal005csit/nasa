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

if (!existsSync(venvPy)) {
  console.log("Creating Python venv in science/.venv ...");
  run("python", ["-m", "venv", "science/.venv"]);
}

console.log("Installing Python deps ...");
run(venvPy, ["-m", "pip", "install", "--upgrade", "pip", "-q"]);
run(venvPy, ["-m", "pip", "install", "-e", "./science[dev]", "-q"]);

console.log("Installing web deps ...");
run("pnpm", ["--dir", "web", "install"]);

console.log("\nSetup complete.");
