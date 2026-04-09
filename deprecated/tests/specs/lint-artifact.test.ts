import { describe, it, beforeAll, afterAll } from "vitest";
import { runSkill } from "../lib/runner.js";
import { createTestCookbook, copyFixture, cleanup } from "../lib/fixtures.js";
import {
  lintPasses,
  lintFails,
  hasFailure,
  outputContains,
  outputMatches,
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
    // type: document causes early exit — skill says "not a lintable artifact type"
    // OR it runs checks and reports NOT CLEAN. Either way, it should indicate failure.
    outputMatches(result.output, /not a lintable|NOT CLEAN|FAIL/i);
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
