import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Wipe the DOM between tests so testId lookups don't find leftover nodes.
afterEach(() => cleanup());
