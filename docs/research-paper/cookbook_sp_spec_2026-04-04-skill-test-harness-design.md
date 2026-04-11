# Skill Test Harness Design

## Context

The cookbook repo has 7 skills in `.claude/skills/` with no automated tests. The dev-team repo has a proven test harness (Vitest + Claude CLI + child_process) that we'll adapt for this repo's content-focused skills.

## Location

`.claude/tests/` — alongside the skills and rules it tests.

## Structure

```
.claude/tests/
├── package.json              # vitest, typescript, npm scripts
├── tsconfig.json
├── vitest.config.ts          # single-threaded, 600s timeout
├── vitest.e2e.config.ts      # 31-min timeout for create-artifact
├── lib/
│   ├── runner.ts             # Invokes skills via claude -p
│   ├── fixtures.ts           # Creates temp cookbook copies, test artifacts
│   └── assertions.ts         # Filesystem assertions
├── fixtures/
│   ├── valid-principle.md    # Known-good principle for lint/approve
│   ├── valid-guideline.md    # Known-good guideline
│   ├── valid-recipe.md       # Known-good recipe (minimal)
│   ├── bad-frontmatter.md    # Missing fields, wrong type
│   └── bad-structure.md      # Missing required sections
└── specs/
    ├── lint-artifact.test.ts
    ├── approve-artifact.test.ts
    ├── add-artifact.test.ts
    ├── create-artifact.test.ts
    ├── update-website.test.ts
    ├── repair-cookbook.test.ts
    └── install-cookbook-global.test.ts
```

## Execution Sandbox

All test execution happens in system temp directories (`os.tmpdir()`), never in the cookbook repo itself. The harness code lives in `.claude/tests/`, but every test creates its sandbox under `/tmp/cookbook-test-<name>-<random>/`. The Claude CLI `cwd` is always set to the temp directory. After each test, the sandbox is cleaned up.

The real repo is only read for two purposes:
1. Copying compliance files and conventions into the test sandbox (fixtures need these for lint checks)
2. Reading SKILL.md files to construct the CLI prompt

No test writes to, modifies, or executes within the real cookbook directory.

## Runner (lib/runner.ts)

Adapted from dev-team's runner.ts. Core flow:

1. Read SKILL.md from the skill directory
2. Strip YAML frontmatter (avoid CLI flag parsing issues)
3. Substitute variables:
   - `$ARGUMENTS` / `${ARGUMENTS}` -> test arguments string
   - `$CLAUDE_SKILL_DIR` / `${CLAUDE_SKILL_DIR}` -> skill directory path
4. Append execution instruction: "EXECUTE NOW with these arguments: ..."
5. Invoke: `claude -p <prompt> --output-format json --dangerously-skip-permissions --max-turns 30`
6. Parse JSON output, capture stdout/stderr
7. Return `{ output: string, exitCode: number, duration: number }`

### Configuration

```typescript
interface RunOptions {
  skill: string;           // skill directory name (e.g., "lint-artifact")
  args: string;            // $ARGUMENTS value
  cwd: string;             // working directory (temp cookbook)
  maxTurns?: number;       // default 30
  timeout?: number;        // default 600_000 ms
  env?: Record<string, string>;
}
```

## Fixtures (lib/fixtures.ts)

### createTestCookbook(name: string): string

Creates a temp directory with a minimal cookbook structure:

```
<tmp>/<name>/
├── principles/
│   └── simplicity.md           # copied from fixtures/valid-principle.md
├── guidelines/
│   └── testing/
│       └── test-pyramid.md     # copied from fixtures/valid-guideline.md
├── recipes/
│   └── infrastructure/
│       └── logging.md          # copied from fixtures/valid-recipe.md
├── compliance/
│   └── artifact-formatting/
│       ├── principle-formatting.md   # copied from real repo
│       ├── guideline-formatting.md   # copied from real repo
│       └── recipe-formatting.md      # copied from real repo
├── introduction/
│   ├── conventions.md          # copied from real repo
│   └── glossary.md             # copied from real repo
├── index.md                    # minimal index listing the 3 test artifacts
├── README.md                   # minimal README with correct counts
└── .claude/
    └── CLAUDE.md               # minimal CLAUDE.md with correct counts
```

### createTestWebsite(name: string): string

Creates a temp directory mimicking `cookbook-web/cookbook/` for update-website tests. Initially empty — tests verify files appear after sync.

### cleanup(dir: string): void

Removes temp directories.

### copyFixture(name: string, destDir: string, destPath: string): void

Copies a fixture file to a destination path within the test cookbook.

## Assertions (lib/assertions.ts)

```typescript
// File presence
function fileExists(dir: string, relativePath: string): void;
function fileNotExists(dir: string, relativePath: string): void;

// Content matching
function fileContains(dir: string, path: string, substring: string): void;
function fileMatches(dir: string, path: string, pattern: RegExp): void;
function fileNotContains(dir: string, path: string, substring: string): void;

// Frontmatter
function hasField(dir: string, path: string, field: string, value?: string): void;
function hasApproval(dir: string, path: string): void;  // approved-by is non-empty

// Output matching
function outputContains(output: string, substring: string): void;
function outputMatches(output: string, pattern: RegExp): void;

// Lint results
function lintPasses(output: string): void;   // "CLEAN" in output
function lintFails(output: string): void;    // "NOT CLEAN" in output
function hasFailure(output: string, checkId: string): void;
```

## Fixture Files

### fixtures/valid-principle.md

A principle that passes all lint checks: complete frontmatter (including approved-by/approved-date empty), H1 matching title, statement paragraph, actionable bullets, Change History.

### fixtures/valid-guideline.md

A guideline that passes all checks: complete frontmatter, summary after H1, structured guidance with RFC 2119 keywords, Change History.

### fixtures/valid-recipe.md

A minimal recipe that passes all checks: complete frontmatter, all required sections in correct order (Overview, Behavioral Requirements with kebab-case names and RFC keywords, Appearance N/A, States N/A, Accessibility N/A, Test Vectors, Edge Cases, Logging, Platform Notes, Design Decisions, Compliance, Change History). Infrastructure type to avoid needing real UI content.

### fixtures/bad-frontmatter.md

A file with: missing `id` field, wrong `type` value ("document" instead of "principle"), missing `approved-by`/`approved-date`, malformed `version` ("1.0").

### fixtures/bad-structure.md

A recipe with: no Overview section, no Behavioral Requirements, no Change History, a TODO placeholder in the body.

## Test Specifications

### lint-artifact.test.ts

| Test | Input | Expected |
|------|-------|----------|
| passes valid principle | valid-principle.md | output contains "CLEAN" |
| passes valid guideline | valid-guideline.md | output contains "CLEAN" |
| passes valid recipe | valid-recipe.md | output contains "CLEAN" |
| fails bad frontmatter | bad-frontmatter.md | output contains "NOT CLEAN", lists FM-02, FM-04, FM-06 |
| fails bad structure | bad-structure.md | output contains "NOT CLEAN", lists RF-01, RF-02, RF-12 |
| detects type from frontmatter | valid-principle.md | output contains "Type: principle" |
| reports --version | --version flag | output contains "lint-artifact v1.0.0" |

### approve-artifact.test.ts

| Test | Input | Expected |
|------|-------|----------|
| approves clean artifact | valid-principle.md (empty approved-by) | approved-by field set to "approve-artifact v1.0.0", approved-date set to today |
| refuses failing artifact | bad-frontmatter.md | output contains "NOT APPROVED", file unchanged |
| reports --version | --version flag | output contains "approve-artifact v1.0.0" |

### add-artifact.test.ts

| Test | Input | Expected |
|------|-------|----------|
| updates index | new valid-principle.md added to principles/ | index.md contains new entry |
| updates README counts | new principle added | README.md count incremented |
| approves before adding | new valid-principle.md | approved-by field is non-empty |
| refuses bad artifact | bad-frontmatter.md | output contains failure, index.md unchanged |

### create-artifact.test.ts

Requires `--test-mode` support in the skill (auto-approve AskUserQuestion).

| Test | Input | Expected |
|------|-------|----------|
| creates principle | --test-mode principle --title "Test Principle" | File created at principles/test-principle.md with valid frontmatter |
| creates guideline | --test-mode guideline --title "Test Guideline" | File created in guidelines/ with valid frontmatter |
| creates recipe | --test-mode recipe --title "Test Recipe" | File created in recipes/ with all required sections |

### update-website.test.ts

| Test | Input | Expected |
|------|-------|----------|
| syncs to website dir | test cookbook + empty website dir | website dir matches cookbook content |
| dry-run reports changes | --dry-run with differences | output lists changes, website dir unchanged |
| skips when no website | no website dir present | output contains "not found" |
| excludes .claude | cookbook with .claude/ dir | .claude/ not in website dir |

### repair-cookbook.test.ts

| Test | Input | Expected |
|------|-------|----------|
| detects broken reference | artifact with bad agentic-cookbook:// URI | output contains FAIL for cross-reference |
| detects missing index entry | artifact not in index.md | output contains FAIL for missing entry |
| dry-run mode | --dry-run | report printed, no files modified |

### install-cookbook-global.test.ts

| Test | Input | Expected |
|------|-------|----------|
| installs skill file | temp HOME dir | ~/.claude/skills/install-cookbook/SKILL.md exists |

## Test Mode Support

Skills that use AskUserQuestion interactively need `--test-mode` added to their SKILL.md:

**Affected skills:**
- create-artifact (type selection, title, location, summary, platforms, section content)
- repair-cookbook (fix approval prompts)

**Behavior:** When `$ARGUMENTS` contains `--test-mode`, all AskUserQuestion calls auto-approve to the first/default option. The skill prints `[TEST MODE]` at startup to confirm.

## NPM Scripts

```json
{
  "test": "vitest run",
  "test:unit": "vitest run --config vitest.config.ts",
  "test:e2e": "vitest run --config vitest.e2e.config.ts",
  "test:lint": "vitest run specs/lint-artifact.test.ts",
  "test:approve": "vitest run specs/approve-artifact.test.ts",
  "test:smoke": "vitest run specs/lint-artifact.test.ts specs/approve-artifact.test.ts"
}
```

## Verification

After implementation:
1. `cd .claude/tests && npm install && npm test` runs all tests
2. Each spec file runs independently
3. Temp directories in /tmp/ are cleaned up after each test
4. No test reads from or writes to the real cookbook — all work happens in temp copies
