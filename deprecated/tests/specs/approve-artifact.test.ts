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
