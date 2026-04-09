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
  });

  it("dry-run does not modify files", async () => {
    const result = await runSkill({
      skill: "repair-cookbook",
      args: "--dry-run",
      cwd: cookbookDir,
    });
    fileContains(cookbookDir, "principles/simplicity.md", 'approved-by: ""');
  });
});
