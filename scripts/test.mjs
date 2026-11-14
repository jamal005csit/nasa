#!/usr/bin/env node
// Run both test suites. Python first (cheaper), then web.
import { spawnSync } from "node:child_process";

function run(cmd, args) {
  console.log(`\n$ ${cmd} ${args.join(" ")}`);
  const r = spawnSync(cmd, args, { stdio: "inherit", shell: true });
  return r.status ?? 1;
}

const pyStatus = run("npm", ["run", "test:py"]);
const webStatus = run("npm", ["run", "test:web"]);

if (pyStatus !== 0 || webStatus !== 0) {
  console.error(`\nFAIL (python=${pyStatus}, web=${webStatus})`);
  process.exit(1);
}
console.log("\nAll tests PASS.");
