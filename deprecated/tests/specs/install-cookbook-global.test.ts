import { describe, it, afterAll } from "vitest";
import { mkdtempSync } from "fs";
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
