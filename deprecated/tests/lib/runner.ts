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
