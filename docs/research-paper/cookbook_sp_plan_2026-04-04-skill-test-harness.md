# Skill Test Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Vitest-based test harness in `.claude/tests/` that tests all 7 cookbook skills by invoking them via `claude -p` against temp sandbox directories in `/tmp/`.

**Architecture:** Adapted from dev-team's proven pattern. Runner reads SKILL.md, substitutes variables, invokes Claude CLI. Fixtures create minimal cookbook copies in `/tmp/cookbook-test-*/`. Assertions check filesystem outcomes and CLI output. All execution is sandboxed — the real repo is never modified.

**Tech Stack:** Vitest 3.x, TypeScript (ESNext/bundler), Node.js child_process, Claude CLI

---

### Task 1: Scaffold project and configuration

**Files:**
- Create: `.claude/tests/package.json`
- Create: `.claude/tests/tsconfig.json`
- Create: `.claude/tests/vitest.config.ts`
- Create: `.claude/tests/vitest.e2e.config.ts`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "cookbook-skill-tests",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "test:e2e": "vitest run --config vitest.e2e.config.ts",
    "test:lint": "vitest run specs/lint-artifact.test.ts",
    "test:approve": "vitest run specs/approve-artifact.test.ts",
    "test:add": "vitest run specs/add-artifact.test.ts",
    "test:create": "vitest run --config vitest.e2e.config.ts specs/create-artifact.test.ts",
    "test:website": "vitest run specs/update-website.test.ts",
    "test:repair": "vitest run specs/repair-cookbook.test.ts",
    "test:install": "vitest run specs/install-cookbook-global.test.ts",
    "test:smoke": "vitest run specs/lint-artifact.test.ts specs/approve-artifact.test.ts"
  },
  "devDependencies": {
    "vitest": "^3.2.1"
  }
}
```

- [ ] **Step 2: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist"
  },
  "include": ["lib/**/*.ts", "specs/**/*.ts"]
}
```

- [ ] **Step 3: Create vitest.config.ts**

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    include: ["specs/**/*.test.ts"],
    testTimeout: 600_000,
    hookTimeout: 30_000,
    reporters: ["verbose"],
    pool: "threads",
    poolOptions: {
      threads: { maxThreads: 1 },
    },
  },
});
```

- [ ] **Step 4: Create vitest.e2e.config.ts**

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    include: ["specs/*.test.ts"],
    testTimeout: 1_860_000,
    hookTimeout: 1_860_000,
    reporters: ["verbose"],
    pool: "threads",
    poolOptions: {
      threads: { maxThreads: 1 },
    },
  },
});
```

- [ ] **Step 5: Run npm install**

Run: `cd .claude/tests && npm install`
Expected: `node_modules/` created, no errors

- [ ] **Step 6: Commit**

```bash
git add .claude/tests/package.json .claude/tests/tsconfig.json .claude/tests/vitest.config.ts .claude/tests/vitest.e2e.config.ts .claude/tests/package-lock.json
git commit -m "Scaffold test harness: package.json, tsconfig, vitest configs"
```

---

### Task 2: Build the runner

**Files:**
- Create: `.claude/tests/lib/runner.ts`

- [ ] **Step 1: Create runner.ts**

```typescript
import { execFile } from "child_process";
import { readFileSync, appendFileSync, mkdirSync, existsSync } from "fs";
import { resolve, join } from "path";

export interface RunResult {
  output: string;
  exitCode: number;
  raw: string;
}

export interface RunOptions {
  skill: string;
  args: string;
  cwd: string;
  maxTurns?: number;
  timeout?: number;
  env?: Record<string, string>;
}

const DEFAULT_TIMEOUT = 600_000;
const MAX_BUFFER = 1024 * 1024 * 10;

function repoRoot(): string {
  // .claude/tests/lib/runner.ts -> ../../.. gets to repo root
  return resolve(import.meta.dirname, "../../..");
}

function skillsDir(): string {
  return join(repoRoot(), ".claude/skills");
}

function logDir(): string {
  const dir = join(import.meta.dirname, "../.logs");
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  return dir;
}

function log(logFile: string, msg: string): void {
  appendFileSync(logFile, `[${new Date().toISOString()}] ${msg}\n`);
}

export async function runSkill(opts: RunOptions): Promise<RunResult> {
  const timeout = opts.timeout ?? DEFAULT_TIMEOUT;
  const maxTurns = opts.maxTurns ?? 30;
  const root = repoRoot();
  const skillDir = join(skillsDir(), opts.skill);
  const logFile = join(logDir(), `run-${opts.skill}-${Date.now()}.log`);

  log(logFile, `=== Skill Test: ${opts.skill} ===`);
  log(logFile, `cwd: ${opts.cwd}`);
  log(logFile, `args: ${opts.args}`);

  // Read SKILL.md and strip YAML frontmatter
  const skillPath = join(skillDir, "SKILL.md");
  let skillContent = readFileSync(skillPath, "utf-8");

  const fmMatch = skillContent.match(/^---\n[\s\S]*?\n---\n/);
  if (fmMatch) {
    skillContent = skillContent.slice(fmMatch[0].length);
  }

  // Substitute variables
  let prompt = skillContent
    .replace(/\$ARGUMENTS/g, opts.args)
    .replace(/\$\{ARGUMENTS\}/g, opts.args)
    .replace(/\$CLAUDE_SKILL_DIR/g, skillDir)
    .replace(/\$\{CLAUDE_SKILL_DIR\}/g, skillDir);

  // Append execution instruction
  prompt += `\n\n---\n\n## EXECUTE NOW\n\nExecute the skill above immediately with arguments: ${opts.args}\n\nThe skill directory is: ${skillDir}\nThe working directory is: ${opts.cwd}\n\nIMPORTANT:\n- Auto-approve all prompts — do not pause for user input\n- Run to completion\n- Start NOW.\n`;

  log(logFile, `Prompt length: ${prompt.length} chars`);

  const args = [
    "-p", prompt,
    "--output-format", "json",
    "--dangerously-skip-permissions",
    "--max-turns", String(maxTurns),
  ];

  return new Promise((resolvePromise) => {
    execFile(
      "claude",
      args,
      {
        cwd: opts.cwd,
        timeout,
        maxBuffer: MAX_BUFFER,
        env: {
          ...process.env,
          CLAUDE_SKILL_DIR: skillDir,
          ...(opts.env ?? {}),
        },
      },
      (error, stdout, stderr) => {
        log(logFile, `Exited. error: ${error?.message ?? "none"}`);
        log(logFile, `stdout: ${stdout?.length ?? 0} chars`);

        if (error && !stdout) {
          resolvePromise({
            output: stderr || error.message,
            exitCode: typeof error.code === "number" ? error.code : 1,
            raw: stdout || "",
          });
          return;
        }

        try {
          const parsed = JSON.parse(stdout);
          resolvePromise({
            output: parsed.result ?? "",
            exitCode: 0,
            raw: stdout,
          });
        } catch {
          resolvePromise({
            output: stdout || stderr || "",
            exitCode: typeof error?.code === "number" ? error.code : 0,
            raw: stdout,
          });
        }
      }
    );
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add .claude/tests/lib/runner.ts
git commit -m "Add skill runner: invokes skills via claude -p CLI"
```

---

### Task 3: Build fixtures

**Files:**
- Create: `.claude/tests/lib/fixtures.ts`
- Create: `.claude/tests/fixtures/valid-principle.md`
- Create: `.claude/tests/fixtures/valid-guideline.md`
- Create: `.claude/tests/fixtures/valid-recipe.md`
- Create: `.claude/tests/fixtures/bad-frontmatter.md`
- Create: `.claude/tests/fixtures/bad-structure.md`

- [ ] **Step 1: Create fixtures.ts**

```typescript
import {
  cpSync,
  mkdtempSync,
  mkdirSync,
  rmSync,
  writeFileSync,
  copyFileSync,
  existsSync,
} from "fs";
import { join, resolve } from "path";
import { tmpdir } from "os";

const FIXTURES_DIR = join(import.meta.dirname, "../fixtures");

function repoRoot(): string {
  return resolve(import.meta.dirname, "../../..");
}

export function createTestCookbook(name: string): string {
  const dest = mkdtempSync(join(tmpdir(), `cookbook-test-${name}-`));
  const root = repoRoot();

  // Create directory structure
  const dirs = [
    "principles",
    "guidelines/testing",
    "recipes/infrastructure",
    "compliance/artifact-formatting",
    "introduction",
    ".claude",
  ];
  for (const d of dirs) {
    mkdirSync(join(dest, d), { recursive: true });
  }

  // Copy fixture artifacts
  copyFileSync(
    join(FIXTURES_DIR, "valid-principle.md"),
    join(dest, "principles/simplicity.md")
  );
  copyFileSync(
    join(FIXTURES_DIR, "valid-guideline.md"),
    join(dest, "guidelines/testing/test-pyramid.md")
  );
  copyFileSync(
    join(FIXTURES_DIR, "valid-recipe.md"),
    join(dest, "recipes/infrastructure/logging.md")
  );

  // Copy compliance files from real repo
  const complianceFiles = [
    "principle-formatting.md",
    "guideline-formatting.md",
    "recipe-formatting.md",
  ];
  for (const f of complianceFiles) {
    const src = join(root, "compliance/artifact-formatting", f);
    if (existsSync(src)) {
      copyFileSync(src, join(dest, "compliance/artifact-formatting", f));
    }
  }

  // Copy conventions and glossary from real repo
  for (const f of ["conventions.md", "glossary.md"]) {
    const src = join(root, "introduction", f);
    if (existsSync(src)) {
      copyFileSync(src, join(dest, "introduction", f));
    }
  }

  // Write minimal index.md
  writeFileSync(
    join(dest, "index.md"),
    `# Index\n\n## Principles\n\n- [Simplicity](principles/simplicity.md)\n\n## Guidelines\n\n- [Test Pyramid](guidelines/testing/test-pyramid.md)\n\n## Recipes\n\n- [Logging](recipes/infrastructure/logging.md)\n`
  );

  // Write minimal README.md
  writeFileSync(
    join(dest, "README.md"),
    `# Test Cookbook\n\n### Principles (1 files)\n\n### Guidelines (1 files)\n\n### Recipes (1 files)\n`
  );

  // Write minimal CLAUDE.md
  writeFileSync(
    join(dest, ".claude/CLAUDE.md"),
    `# Test Cookbook\n\n| Type | Count |\n|------|-------|\n| Principle | 1 |\n| Guideline | 1 |\n| Recipe | 1 |\n`
  );

  // Init bare git repo so skills can run git commands
  mkdirSync(join(dest, ".git"));
  writeFileSync(
    join(dest, ".git/config"),
    `[core]\n\trepositoryformatversion = 0\n`
  );
  writeFileSync(join(dest, ".git/HEAD"), "ref: refs/heads/main\n");

  return dest;
}

export function createTestWebsite(name: string): string {
  const dest = mkdtempSync(join(tmpdir(), `cookbook-web-test-${name}-`));
  mkdirSync(join(dest, "cookbook"), { recursive: true });
  return dest;
}

export function copyFixture(
  fixtureName: string,
  destDir: string,
  destPath: string
): void {
  const src = join(FIXTURES_DIR, fixtureName);
  const dest = join(destDir, destPath);
  mkdirSync(join(dest, ".."), { recursive: true });
  copyFileSync(src, dest);
}

export function cleanup(dir: string | undefined): void {
  if (dir && dir.startsWith(tmpdir())) {
    rmSync(dir, { recursive: true, force: true });
  }
}
```

- [ ] **Step 2: Create fixtures/valid-principle.md**

```markdown
---
id: 00000000-0000-0000-0000-000000000001
title: "Test Principle"
domain: agentic-cookbook://principles/test-principle
type: principle
version: 1.0.0
status: accepted
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "A test principle used by the skill test harness to verify lint and approve behavior."
platforms: []
tags:
  - test
depends-on: []
related: []
references: []
approved-by: ""
approved-date: ""
---

# Test Principle

Keep things simple. Every additional layer of abstraction is a cost that must be justified by a concrete, current need.

- Before adding a new abstraction, confirm a current requirement demands it
- Favor direct solutions over clever indirection
- Complexity compounds — resist it at introduction time

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-04-04 | Mike Fullerton | Initial creation |
```

- [ ] **Step 3: Create fixtures/valid-guideline.md**

```markdown
---
id: 00000000-0000-0000-0000-000000000002
title: "Test Guideline"
domain: agentic-cookbook://guidelines/testing/test-guideline
type: guideline
version: 1.0.0
status: accepted
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "A test guideline used by the skill test harness to verify lint and approve behavior."
platforms: []
tags:
  - test
depends-on: []
related: []
references: []
approved-by: ""
approved-date: ""
---

# Test Guideline

Every change MUST have tests. Every bug fix MUST include a regression test.

- Unit tests MUST cover all business logic
- Integration tests SHOULD verify component boundaries
- E2E tests MAY be used for critical user journeys only

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-04-04 | Mike Fullerton | Initial creation |
```

- [ ] **Step 4: Create fixtures/valid-recipe.md**

```markdown
---
id: 00000000-0000-0000-0000-000000000003
title: "Test Recipe"
domain: agentic-cookbook://recipes/infrastructure/test-recipe
type: recipe
version: 1.0.0
status: accepted
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "A test recipe used by the skill test harness to verify lint and approve behavior."
platforms: []
tags:
  - test
depends-on: []
related: []
references: []
approved-by: ""
approved-date: ""
---

# Test Recipe

## Overview

A minimal infrastructure recipe for testing the lint and approve skills.

## Behavioral Requirements

- **data-persistence**: The service MUST persist data to disk on every write operation.
- **graceful-shutdown**: The service MUST complete all pending writes before shutting down.

## Appearance

Not applicable — infrastructure recipe with no visual UI.

## States

Not applicable — infrastructure recipe.

## Accessibility

Not applicable — infrastructure recipe with no user-facing interface.

## Conformance Test Vectors

| ID | Requirements | Input | Expected |
|----|-------------|-------|----------|
| tr-001 | data-persistence | Write 1 record | Record exists on disk |
| tr-002 | graceful-shutdown | Send shutdown signal during write | Write completes before exit |

## Edge Cases

- Empty write: zero-byte payload MUST be accepted without error
- Concurrent writes: two simultaneous writes MUST NOT corrupt data

## Logging

Subsystem: `{{bundle_id}}` | Category: `TestRecipe`

| Event | Level | Message |
|-------|-------|---------|
| Write completed | debug | `TestRecipe: wrote {{bytes}} bytes` |

## Platform Notes

- **Swift**: Use `FileManager` for atomic writes.
- **TypeScript**: Use `fs.writeFileSync` with a temp file and rename.

## Design Decisions

**Decision**: Use atomic file writes. **Rationale**: Prevents partial writes on crash. **Approved**: yes

## Compliance

| Check | Status | Category |
|-------|--------|----------|
| [explicit-error-handling](agentic-cookbook://compliance/best-practices#explicit-error-handling) | passed | Best Practices |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-04-04 | Mike Fullerton | Initial creation |
```

- [ ] **Step 5: Create fixtures/bad-frontmatter.md**

```markdown
---
title: "Bad Frontmatter"
domain: agentic-cookbook://principles/bad-frontmatter
type: document
version: 1.0
status: accepted
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "short"
platforms: []
tags: []
depends-on: []
related: []
references: []
---

# Bad Frontmatter

This file has multiple frontmatter issues for testing.

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0 | 2026-04-04 | Mike Fullerton | Initial creation |
```

Missing: `id`, `approved-by`, `approved-date`. Wrong: `type` is "document", `version` is "1.0" not "1.0.0", `summary` is under 10 chars.

- [ ] **Step 6: Create fixtures/bad-structure.md**

```markdown
---
id: 00000000-0000-0000-0000-000000000005
title: "Bad Structure"
domain: agentic-cookbook://recipes/infrastructure/bad-structure
type: recipe
version: 1.0.0
status: accepted
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "A recipe with missing required sections for testing lint failure detection."
platforms: []
tags:
  - test
depends-on: []
related: []
references: []
approved-by: ""
approved-date: ""
---

# Bad Structure

TODO: fill in the overview section later.

This recipe is intentionally missing required sections.
```

Missing: Overview, Behavioral Requirements, Appearance, States, Accessibility, Test Vectors, Edge Cases, Logging, Platform Notes, Design Decisions, Compliance, Change History. Has TODO text.

- [ ] **Step 7: Commit**

```bash
git add .claude/tests/lib/fixtures.ts .claude/tests/fixtures/
git commit -m "Add fixtures: test cookbook builder and 5 fixture files"
```

---

### Task 4: Build assertions

**Files:**
- Create: `.claude/tests/lib/assertions.ts`

- [ ] **Step 1: Create assertions.ts**

```typescript
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
    /^approved-by:\s*"approve-artifact/m
  );
  expect(content, `${path} should have non-empty approved-date`).toMatch(
    /^approved-date:\s*"\d{4}-\d{2}-\d{2}"/m
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
```

- [ ] **Step 2: Commit**

```bash
git add .claude/tests/lib/assertions.ts
git commit -m "Add assertions: file, frontmatter, output, and lint helpers"
```

---

### Task 5: Write lint-artifact tests

**Files:**
- Create: `.claude/tests/specs/lint-artifact.test.ts`

- [ ] **Step 1: Create lint-artifact.test.ts**

```typescript
import { describe, it, beforeAll, afterAll } from "vitest";
import { runSkill } from "../lib/runner.js";
import { createTestCookbook, copyFixture, cleanup } from "../lib/fixtures.js";
import {
  lintPasses,
  lintFails,
  hasFailure,
  outputContains,
} from "../lib/assertions.js";

describe("lint-artifact", () => {
  let cookbookDir: string;

  beforeAll(() => {
    cookbookDir = createTestCookbook("lint");
  });

  afterAll(() => {
    cleanup(cookbookDir);
  });

  it("passes a valid principle", async () => {
    const result = await runSkill({
      skill: "lint-artifact",
      args: "principles/simplicity.md",
      cwd: cookbookDir,
    });
    lintPasses(result.output);
    outputContains(result.output, "Type: principle");
  });

  it("passes a valid guideline", async () => {
    copyFixture("valid-guideline.md", cookbookDir, "guidelines/testing/test-guideline.md");
    const result = await runSkill({
      skill: "lint-artifact",
      args: "guidelines/testing/test-guideline.md",
      cwd: cookbookDir,
    });
    lintPasses(result.output);
    outputContains(result.output, "Type: guideline");
  });

  it("passes a valid recipe", async () => {
    copyFixture("valid-recipe.md", cookbookDir, "recipes/infrastructure/test-recipe.md");
    const result = await runSkill({
      skill: "lint-artifact",
      args: "recipes/infrastructure/test-recipe.md",
      cwd: cookbookDir,
    });
    lintPasses(result.output);
    outputContains(result.output, "Type: recipe");
  });

  it("fails bad frontmatter", async () => {
    copyFixture("bad-frontmatter.md", cookbookDir, "principles/bad-frontmatter.md");
    const result = await runSkill({
      skill: "lint-artifact",
      args: "principles/bad-frontmatter.md",
      cwd: cookbookDir,
    });
    lintFails(result.output);
    hasFailure(result.output, "FM-02");
    hasFailure(result.output, "FM-04");
    hasFailure(result.output, "FM-06");
  });

  it("fails bad structure", async () => {
    copyFixture("bad-structure.md", cookbookDir, "recipes/infrastructure/bad-structure.md");
    const result = await runSkill({
      skill: "lint-artifact",
      args: "recipes/infrastructure/bad-structure.md",
      cwd: cookbookDir,
    });
    lintFails(result.output);
    hasFailure(result.output, "RF-01");
    hasFailure(result.output, "RF-02");
    hasFailure(result.output, "FM-13");
  });

  it("reports version", async () => {
    const result = await runSkill({
      skill: "lint-artifact",
      args: "--version",
      cwd: cookbookDir,
    });
    outputContains(result.output, "lint-artifact v1.0.0");
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add .claude/tests/specs/lint-artifact.test.ts
git commit -m "Add lint-artifact tests: valid/invalid fixtures, version check"
```

---

### Task 6: Write approve-artifact tests

**Files:**
- Create: `.claude/tests/specs/approve-artifact.test.ts`

- [ ] **Step 1: Create approve-artifact.test.ts**

```typescript
import { describe, it, beforeEach, afterAll } from "vitest";
import { runSkill } from "../lib/runner.js";
import { createTestCookbook, copyFixture, cleanup } from "../lib/fixtures.js";
import {
  hasApproval,
  outputContains,
  fileContains,
} from "../lib/assertions.js";

describe("approve-artifact", () => {
  let cookbookDir: string;

  beforeEach(() => {
    cookbookDir = createTestCookbook("approve");
  });

  afterAll(() => {
    cleanup(cookbookDir);
  });

  it("stamps approval on clean artifact", async () => {
    const result = await runSkill({
      skill: "approve-artifact",
      args: "principles/simplicity.md",
      cwd: cookbookDir,
    });
    outputContains(result.output, "APPROVED");
    hasApproval(cookbookDir, "principles/simplicity.md");
  });

  it("refuses failing artifact", async () => {
    copyFixture("bad-frontmatter.md", cookbookDir, "principles/bad-frontmatter.md");
    const result = await runSkill({
      skill: "approve-artifact",
      args: "principles/bad-frontmatter.md",
      cwd: cookbookDir,
    });
    outputContains(result.output, "NOT APPROVED");
    fileContains(cookbookDir, "principles/bad-frontmatter.md", 'approved-by: ""');
  });

  it("reports version", async () => {
    const result = await runSkill({
      skill: "approve-artifact",
      args: "--version",
      cwd: cookbookDir,
    });
    outputContains(result.output, "approve-artifact v1.0.0");
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add .claude/tests/specs/approve-artifact.test.ts
git commit -m "Add approve-artifact tests: stamp, refuse, version"
```

---

### Task 7: Write add-artifact tests

**Files:**
- Create: `.claude/tests/specs/add-artifact.test.ts`

- [ ] **Step 1: Create add-artifact.test.ts**

```typescript
import { describe, it, beforeEach, afterAll } from "vitest";
import { copyFileSync } from "fs";
import { join } from "path";
import { runSkill } from "../lib/runner.js";
import { createTestCookbook, copyFixture, cleanup } from "../lib/fixtures.js";
import {
  fileContains,
  hasApproval,
  outputContains,
} from "../lib/assertions.js";

describe("add-artifact", () => {
  let cookbookDir: string;

  beforeEach(() => {
    cookbookDir = createTestCookbook("add");
  });

  afterAll(() => {
    cleanup(cookbookDir);
  });

  it("updates index after adding a principle", async () => {
    copyFixture("valid-principle.md", cookbookDir, "principles/new-principle.md");
    const result = await runSkill({
      skill: "add-artifact",
      args: "principles/new-principle.md",
      cwd: cookbookDir,
    });
    outputContains(result.output, "COMPLETE");
    fileContains(cookbookDir, "index.md", "new-principle");
    hasApproval(cookbookDir, "principles/new-principle.md");
  });

  it("refuses bad artifact", async () => {
    copyFixture("bad-frontmatter.md", cookbookDir, "principles/bad.md");
    const result = await runSkill({
      skill: "add-artifact",
      args: "principles/bad.md",
      cwd: cookbookDir,
    });
    outputContains(result.output, "fail");
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add .claude/tests/specs/add-artifact.test.ts
git commit -m "Add add-artifact tests: index update, refuse bad artifact"
```

---

### Task 8: Write update-website tests

**Files:**
- Create: `.claude/tests/specs/update-website.test.ts`

- [ ] **Step 1: Create update-website.test.ts**

```typescript
import { describe, it, beforeEach, afterAll } from "vitest";
import { runSkill } from "../lib/runner.js";
import {
  createTestCookbook,
  createTestWebsite,
  cleanup,
} from "../lib/fixtures.js";
import { fileExists, fileNotExists, outputContains } from "../lib/assertions.js";

describe("update-website", () => {
  let cookbookDir: string;
  let websiteDir: string | undefined;

  beforeEach(() => {
    cookbookDir = createTestCookbook("website");
  });

  afterAll(() => {
    cleanup(cookbookDir);
    cleanup(websiteDir);
  });

  it("syncs content to website directory", async () => {
    websiteDir = createTestWebsite("website");
    const result = await runSkill({
      skill: "update-website",
      args: "",
      cwd: cookbookDir,
      env: { COOKBOOK_WEB_PATH: `${websiteDir}/cookbook` },
    });
    outputContains(result.output, "SYNC COMPLETE");
    fileExists(websiteDir!, "cookbook/principles/simplicity.md");
    fileExists(websiteDir!, "cookbook/index.md");
  });

  it("excludes .claude from sync", async () => {
    websiteDir = createTestWebsite("website-exclude");
    await runSkill({
      skill: "update-website",
      args: "",
      cwd: cookbookDir,
      env: { COOKBOOK_WEB_PATH: `${websiteDir}/cookbook` },
    });
    fileNotExists(websiteDir!, "cookbook/.claude");
  });

  it("reports dry-run without writing", async () => {
    websiteDir = createTestWebsite("website-dry");
    const result = await runSkill({
      skill: "update-website",
      args: "--dry-run",
      cwd: cookbookDir,
      env: { COOKBOOK_WEB_PATH: `${websiteDir}/cookbook` },
    });
    outputContains(result.output, "SYNC PREVIEW");
    fileNotExists(websiteDir!, "cookbook/principles/simplicity.md");
  });

  it("reports error when website not found", async () => {
    const result = await runSkill({
      skill: "update-website",
      args: "",
      cwd: cookbookDir,
    });
    outputContains(result.output, "not found");
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add .claude/tests/specs/update-website.test.ts
git commit -m "Add update-website tests: sync, exclude, dry-run, missing"
```

---

### Task 9: Write repair-cookbook tests

**Files:**
- Create: `.claude/tests/specs/repair-cookbook.test.ts`

- [ ] **Step 1: Create repair-cookbook.test.ts**

```typescript
import { describe, it, beforeEach, afterAll } from "vitest";
import { writeFileSync } from "fs";
import { join } from "path";
import { runSkill } from "../lib/runner.js";
import { createTestCookbook, cleanup } from "../lib/fixtures.js";
import { outputContains, fileContains } from "../lib/assertions.js";

describe("repair-cookbook", () => {
  let cookbookDir: string;

  beforeEach(() => {
    cookbookDir = createTestCookbook("repair");
  });

  afterAll(() => {
    cleanup(cookbookDir);
  });

  it("detects broken cross-reference", async () => {
    // Inject a broken reference into a file
    const brokenFile = join(cookbookDir, "principles/simplicity.md");
    const content = `---
id: 00000000-0000-0000-0000-000000000001
title: "Test Principle"
domain: agentic-cookbook://principles/simplicity
type: principle
version: 1.0.0
status: accepted
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "A test principle with a broken reference for testing repair-cookbook."
platforms: []
tags: [test]
depends-on:
  - agentic-cookbook://guidelines/nonexistent/broken-ref
related: []
references: []
approved-by: ""
approved-date: ""
---

# Test Principle

This principle references a nonexistent guideline.

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-04-04 | Mike Fullerton | Initial creation |
`;
    writeFileSync(brokenFile, content);
    const result = await runSkill({
      skill: "repair-cookbook",
      args: "--dry-run",
      cwd: cookbookDir,
    });
    outputContains(result.output, "FAIL");
    outputContains(result.output, "broken");
  });

  it("dry-run does not modify files", async () => {
    const result = await runSkill({
      skill: "repair-cookbook",
      args: "--dry-run",
      cwd: cookbookDir,
    });
    // Verify original fixture is unchanged
    fileContains(cookbookDir, "principles/simplicity.md", 'approved-by: ""');
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add .claude/tests/specs/repair-cookbook.test.ts
git commit -m "Add repair-cookbook tests: broken ref detection, dry-run safety"
```

---

### Task 10: Write create-artifact and install-cookbook-global tests

**Files:**
- Create: `.claude/tests/specs/create-artifact.test.ts`
- Create: `.claude/tests/specs/install-cookbook-global.test.ts`

- [ ] **Step 1: Create create-artifact.test.ts**

```typescript
import { describe, it, beforeEach, afterAll } from "vitest";
import { runSkill } from "../lib/runner.js";
import { createTestCookbook, cleanup } from "../lib/fixtures.js";
import { fileExists, hasField, outputContains } from "../lib/assertions.js";

describe("create-artifact", { timeout: 1_860_000 }, () => {
  let cookbookDir: string;

  beforeEach(() => {
    cookbookDir = createTestCookbook("create");
  });

  afterAll(() => {
    cleanup(cookbookDir);
  });

  it("creates a principle in test mode", async () => {
    const result = await runSkill({
      skill: "create-artifact",
      args: '--test-mode principle --title "Test Created Principle"',
      cwd: cookbookDir,
      maxTurns: 50,
      timeout: 1_860_000,
    });
    outputContains(result.output, "ARTIFACT CREATED");
    fileExists(cookbookDir, "principles/test-created-principle.md");
    hasField(cookbookDir, "principles/test-created-principle.md", "type", "principle");
  });
});
```

- [ ] **Step 2: Create install-cookbook-global.test.ts**

```typescript
import { describe, it, afterAll } from "vitest";
import { mkdtempSync, existsSync } from "fs";
import { join } from "path";
import { tmpdir } from "os";
import { runSkill } from "../lib/runner.js";
import { cleanup } from "../lib/fixtures.js";
import { fileExists } from "../lib/assertions.js";

describe("install-cookbook-global", () => {
  let fakeHome: string;

  afterAll(() => {
    cleanup(fakeHome);
  });

  it("installs skill to ~/.claude/skills/", async () => {
    fakeHome = mkdtempSync(join(tmpdir(), "cookbook-test-home-"));
    const result = await runSkill({
      skill: "install-cookbook-global",
      args: "",
      cwd: fakeHome,
      env: { HOME: fakeHome },
    });
    fileExists(fakeHome, ".claude/skills/install-cookbook/SKILL.md");
  });
});
```

- [ ] **Step 3: Commit**

```bash
git add .claude/tests/specs/create-artifact.test.ts .claude/tests/specs/install-cookbook-global.test.ts
git commit -m "Add create-artifact and install-cookbook-global tests"
```

---

### Task 11: Add --test-mode to create-artifact and repair-cookbook skills

**Files:**
- Modify: `.claude/skills/create-artifact/SKILL.md`
- Modify: `.claude/skills/repair-cookbook/SKILL.md`

- [ ] **Step 1: Add test-mode to create-artifact**

In `.claude/skills/create-artifact/SKILL.md`, after the version check section, add:

```markdown
## Test Mode

If `$ARGUMENTS` contains `--test-mode`:
1. Print `[TEST MODE]` at startup.
2. Auto-approve all AskUserQuestion prompts to the first/default option.
3. For title: use the `--title` argument value if provided, otherwise use "Test Artifact".
4. For location: accept the proposed default path.
5. For summary: use "Test artifact created in test mode."
6. For platforms: use empty list.
7. For section content: generate minimal valid content that passes lint.
```

- [ ] **Step 2: Add test-mode to repair-cookbook**

In `.claude/skills/repair-cookbook/SKILL.md`, after the version check section, add:

```markdown
## Test Mode

If `$ARGUMENTS` contains `--test-mode`:
1. Print `[TEST MODE]` at startup.
2. Auto-approve all AskUserQuestion prompts to the first/default option (e.g., "yes" for batch fixes, option "a" for ambiguous fixes).
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/create-artifact/SKILL.md .claude/skills/repair-cookbook/SKILL.md
git commit -m "Add --test-mode to create-artifact and repair-cookbook skills"
```

---

### Task 12: Add .gitignore and verify

**Files:**
- Create: `.claude/tests/.gitignore`

- [ ] **Step 1: Create .gitignore**

```
node_modules/
dist/
.logs/
```

- [ ] **Step 2: Run the smoke tests**

Run: `cd .claude/tests && npm test -- specs/lint-artifact.test.ts`
Expected: All lint-artifact tests pass

- [ ] **Step 3: Commit .gitignore**

```bash
git add .claude/tests/.gitignore
git commit -m "Add .gitignore for test harness (node_modules, dist, logs)"
```
