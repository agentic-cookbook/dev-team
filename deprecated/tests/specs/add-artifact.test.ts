import { describe, it, beforeEach, afterAll } from "vitest";
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
