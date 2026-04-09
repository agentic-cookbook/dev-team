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
