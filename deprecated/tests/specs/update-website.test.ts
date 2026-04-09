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
