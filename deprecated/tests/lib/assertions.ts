import { existsSync, readFileSync } from "fs";
import { join } from "path";
import { expect } from "vitest";

// ── File presence ──────────────────────────────────────────────

export function fileExists(dir: string, relativePath: string): void {
  expect(existsSync(join(dir, relativePath)), `Expected file: ${relativePath}`).toBe(true);
}

export function fileNotExists(dir: string, relativePath: string): void {
  expect(existsSync(join(dir, relativePath)), `Unexpected file: ${relativePath}`).toBe(false);
}

// ── Content matching ───────────────────────────────────────────

function readContent(dir: string, relativePath: string): string {
  const p = join(dir, relativePath);
  expect(existsSync(p), `File not found: ${relativePath}`).toBe(true);
  return readFileSync(p, "utf-8");
}

export function fileContains(dir: string, path: string, substring: string): void {
  const content = readContent(dir, path);
  expect(content, `${path} should contain "${substring}"`).toContain(substring);
}

export function fileMatches(dir: string, path: string, pattern: RegExp): void {
  const content = readContent(dir, path);
  expect(content, `${path} should match ${pattern}`).toMatch(pattern);
}

export function fileNotContains(dir: string, path: string, substring: string): void {
  const content = readContent(dir, path);
  expect(content, `${path} should not contain "${substring}"`).not.toContain(substring);
}

// ── Frontmatter ────────────────────────────────────────────────

export function hasField(dir: string, path: string, field: string, value?: string): void {
  const content = readContent(dir, path);
  const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
  expect(fmMatch, `${path} should have frontmatter`).not.toBeNull();
  const fm = fmMatch![1];
  const fieldPattern = new RegExp(`^${field}:`, "m");
  expect(fm, `${path} should have field "${field}"`).toMatch(fieldPattern);
  if (value !== undefined) {
    const valuePattern = new RegExp(`^${field}:\\s*"?${value}"?`, "m");
    expect(fm, `${path}.${field} should be "${value}"`).toMatch(valuePattern);
  }
}

export function hasApproval(dir: string, path: string): void {
  const content = readContent(dir, path);
  expect(content, `${path} should have non-empty approved-by`).toMatch(
    /^approved-by:\s*"?approve-artifact/m
  );
  expect(content, `${path} should have non-empty approved-date`).toMatch(
    /^approved-date:\s*"?\d{4}-\d{2}-\d{2}"?/m
  );
}

// ── Output matching ────────────────────────────────────────────

export function outputContains(output: string, substring: string): void {
  expect(output, `Output should contain "${substring}"`).toContain(substring);
}

export function outputMatches(output: string, pattern: RegExp): void {
  expect(output, `Output should match ${pattern}`).toMatch(pattern);
}

// ── Lint results ───────────────────────────────────────────────

export function lintPasses(output: string): void {
  expect(output, "Lint should pass (CLEAN)").toMatch(/CLEAN/);
  expect(output, "Lint should not fail (NOT CLEAN)").not.toMatch(/NOT CLEAN/);
}

export function lintFails(output: string): void {
  expect(output, "Lint should fail (NOT CLEAN)").toMatch(/NOT CLEAN/);
}

export function hasFailure(output: string, checkId: string): void {
  expect(output, `Output should contain failure ${checkId}`).toContain(checkId);
}
