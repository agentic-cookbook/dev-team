# Validation Checks

Complete checklist for validating cookbook integrity. Each check has an ID, description, verification method, and severity.

Severities:
- **FAIL**: Must be fixed. Broken content, missing required data, invalid references.
- **WARN**: Should be fixed. Style issues, missing optional content, potential problems.
- **PASS**: Check passed successfully.

---

## Category 1: Frontmatter Integrity

Applies to all content `.md` files (under `principles/`, `guidelines/`, `recipes/`, `workflows/`, `compliance/`, `reference/`, `introduction/`). Skip `_template.md` files.

| ID | Check | How to verify | Severity |
|----|-------|---------------|----------|
| F01 | All required fields present | Parse YAML frontmatter between `---` delimiters. Verify these fields exist: `id`, `title`, `domain`, `type`, `version`, `status`, `language`, `created`, `modified`, `author`, `copyright`, `license`, `summary`, `platforms`, `tags`, `depends-on`, `related`, `references`. Report each missing field. | FAIL |
| F02 | No empty required fields | Check that `id`, `title`, `domain`, `type`, `version`, `status`, `language`, `created`, `modified`, `author`, `copyright`, `license`, `summary` are non-empty strings (not `""`, not `null`, not `~`). List fields `platforms`, `tags`, `depends-on`, `related`, `references` may be empty arrays `[]`. | FAIL |
| F03 | ID is valid UUID | Check that the `id` field matches the UUID pattern: `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` (case-insensitive). | FAIL |
| F04 | No duplicate IDs | Collect all `id` values across every file. Report any duplicates with both file paths. | FAIL |
| F05 | Domain matches file path | Derive the expected domain from the file path: strip `.md` extension, prepend `agentic-cookbook://`. Compare with the `domain:` field. For index files, the domain should end with the directory name or `index`. Example: `principles/simplicity.md` should have domain `agentic-cookbook://principles/simplicity`. | FAIL |
| F06 | Type field is valid | Check that `type` is one of: `principle`, `guideline`, `recipe`, `workflow`, `reference`. | FAIL |
| F07 | Status field is valid | Check that `status` is one of: `draft`, `review`, `accepted`, `deprecated`. | FAIL |
| F08 | Version is valid semver | Check that `version` matches the pattern `X.Y.Z` where X, Y, Z are non-negative integers. Use regex: `^\d+\.\d+\.\d+$`. | FAIL |
| F09 | Dates are valid ISO 8601 | Check that `created` and `modified` match the pattern `YYYY-MM-DD`. Verify `modified` is >= `created`. | WARN |
| F10 | License is MIT | Check that `license` field is exactly `MIT`. | WARN |
| F11 | Language is valid BCP 47 | Check that `language` is a valid BCP 47 tag. For this cookbook, it should be `en`. | WARN |
| F12 | Summary length | Check that `summary` is between 10 and 200 characters. Too short suggests a placeholder; too long is unwieldy for tooltips. | WARN |
| F13 | Tags are lowercase kebab-case | Check that every item in `tags` matches `^[a-z0-9]+(-[a-z0-9]+)*$`. | WARN |
| F14 | Copyright year matches created year | Check that the year in `copyright` (e.g., `2026 Mike Fullerton`) matches the year in the `created` field. | WARN |
| F15 | Platforms values are valid | Check that every item in `platforms` is one of: `swift`, `kotlin`, `typescript`, `csharp`, `python`, `windows`, `macos`, `ios`, `web`. Empty list `[]` is valid (means universal). | WARN |

---

## Category 2: Content Structure

Applies to all content `.md` files (under `principles/`, `guidelines/`, `recipes/`, `workflows/`, `compliance/`, `reference/`, `introduction/`). Skip `_template.md` files.

| ID | Check | How to verify | Severity |
|----|-------|---------------|----------|
| C01 | H1 heading matches title | The first `# ` heading in the body (after frontmatter) should match the `title` field in frontmatter. Compare case-insensitively, stripping leading/trailing whitespace. | WARN |
| C02 | Change History section exists | Grep for `## Change History` in the file. Every non-template file must have this section. | FAIL |
| C03 | Change History table has rows | After `## Change History`, find a markdown table. It must have at least one data row (not just the header). The first row's version should match the frontmatter `version` or an earlier version. | WARN |
| C04 | Change History latest version matches frontmatter | The most recent version in the Change History table (last row) should match the frontmatter `version` field. | WARN |
| C05 | No empty sections | Find H2 sections (`## `) that have no content before the next heading or end of file. Sections with only whitespace count as empty. Skip `## Change History` (checked separately). | WARN |
| C06 | No TODO/FIXME placeholders | Grep for `TODO`, `FIXME`, `HACK`, `XXX`, `PLACEHOLDER` in the file body (case-insensitive). These suggest incomplete content. | WARN |
| C07 | Named requirements format | In files with a `## Requirements` section, check that requirements use the format `**<kebab-case-name>**: <description>`. Grep for `**` patterns and verify the name portion is kebab-case: `^[a-z0-9]+(-[a-z0-9]+)*$`. | WARN |
| C08 | No raw HTML | Grep for `<div`, `<span`, `<table`, `<br>`, `<img` tags. Cookbook content should be pure markdown. | WARN |
| C09 | Heading hierarchy | Check that headings follow proper hierarchy: no `### ` without a preceding `## `, no `#### ` without a preceding `### `. | WARN |
| C10 | No duplicate H2 sections | Check that no `## ` heading text appears more than once in the same file. | FAIL |

---

## Category 3: Cross-References

Applies to all content `.md` files.

| ID | Check | How to verify | Severity |
|----|-------|---------------|----------|
| X01 | Domain references resolve | Find all `agentic-cookbook://` references in file bodies and frontmatter (`depends-on`, `related`). For each, derive the expected file path: strip the `agentic-cookbook://` prefix, append `.md`. Verify the file exists. Also check for `index.md` in directories. Report broken references with the source file and target. | FAIL |
| X02 | Fragment references have targets | Find `#fragment` references (short-form within-document refs). For `#requirements/<name>`, verify that `**<name>**:` exists in the same file. For `#states/<name>`, verify a heading or bold text with that state name exists. | WARN |
| X03 | External URLs are well-formed | Find all URLs starting with `http://` or `https://` in file bodies and `references:` frontmatter. Verify they are syntactically valid (no spaces, no trailing punctuation absorbed). Do NOT check if they are reachable (no HTTP requests). | WARN |
| X04 | Depends-on references exist | For each item in the `depends-on` frontmatter list, verify it resolves to an existing file (same derivation as X01). | FAIL |
| X05 | Related references exist | For each item in the `related` frontmatter list, verify it resolves to an existing file (same derivation as X01). | WARN |
| X06 | No self-references | Check that a file's `depends-on` and `related` lists do not contain its own domain. | WARN |
| X07 | No circular depends-on | Build a dependency graph from all `depends-on` fields. Check for cycles. Report any cycles found with the full chain. | WARN |
| X08 | References field URLs are external | Check that items in the frontmatter `references:` list are external URLs (`http://` or `https://`), not internal domain references. Internal cross-refs belong in `depends-on` or `related`. | WARN |

---

## Category 4: Indexes and Documentation

| ID | Check | How to verify | Severity |
|----|-------|---------------|----------|
| I01 | All cookbook files in index.md | Read `index.md`. For every content `.md` file (excluding `index.md`, `introduction/conventions.md`, `_template.md`, and directory `index.md` files), verify it is referenced in `index.md` — either as a direct link `[text](relative/path.md)` or mentioned by filename. Glob all files, then grep the index for each. | FAIL |
| I02 | Index links resolve | Read `index.md`. For every markdown link `[text](path)`, verify the target file exists relative to the repo root. | FAIL |
| I03 | No stale index entries | For every link in `index.md` that points to a `.md` file, verify the target file still exists. Report dead links. | FAIL |
| I04 | CLAUDE.md is current | Read `CLAUDE.md` at the repo root. Verify it mentions all skill names listed under `skills/`. Verify the repository structure section is accurate by comparing against actual directories. | WARN |
| I05 | Directory index files exist | For each subdirectory under `cookbook/` that contains `.md` files (e.g., `cookbook/guidelines/testing/`), check if an `index.md` exists. Not required for leaf directories with a single file. | WARN |
| I06 | Contributing guide exists | Verify `appendix/contributing/AUTHORING.md` exists. | WARN |
| I07 | Conventions file exists | Verify `introduction/conventions.md` exists and has valid frontmatter. | FAIL |
| I08 | Rules directory matches tiers | Read `CLAUDE.md` and identify the listed tier rule files. Verify each exists under `rules/`. Report any rule file listed in CLAUDE.md but missing from `rules/`, or present in `rules/` but not mentioned in CLAUDE.md. | WARN |

---

## Category 5: Skills and Rules

| ID | Check | How to verify | Severity |
|----|-------|---------------|----------|
| S01 | All skills have SKILL.md | Glob `skills/*/`. For each skill directory, verify `SKILL.md` exists. | FAIL |
| S02 | Skill frontmatter has required fields | Read each `SKILL.md`. Verify YAML frontmatter contains at minimum: `name`, `description`. Check for `allowed-tools`, `context`, `argument-hint` as recommended fields. | FAIL for name/description, WARN for others |
| S03 | Skill name matches directory | The `name:` field in `SKILL.md` frontmatter should match the skill's directory name (the parent directory of SKILL.md). | WARN |
| S04 | Skill version field present | Check each `SKILL.md` has a `version:` field in frontmatter. Verify it is valid semver. | WARN |
| S05 | Skill references files exist | For each skill that uses `${CLAUDE_SKILL_DIR}/references/`, glob `references/*` in the skill directory. Grep the SKILL.md for any referenced filename and verify it exists. | FAIL |
| S06 | Skills listed in CLAUDE.md | Read `CLAUDE.md`. For each skill directory under `skills/`, verify the skill is mentioned in CLAUDE.md (by name or by the `/skill-name` command form). | WARN |
| S07 | Rule files have content | For each `.md` file under `rules/`, verify it is non-empty (more than just a title and blank lines). Check file size is > 100 bytes. | WARN |
| S08 | Rule files follow naming convention | Rule files under `rules/` should be UPPER-KEBAB-CASE with a `-RULE.md` suffix. Pattern: `^[A-Z0-9]+(-[A-Z0-9]+)*-RULE\.md$`. | WARN |
| S09 | No orphaned skill references | Grep `CLAUDE.md` and `cookbook/index.md` for `/skill-name` patterns. Verify each referenced skill actually exists under `skills/`. | WARN |
| S10 | Skill version matches internal version | If the SKILL.md body contains a version string like `v1.0.0` (in the version check block), verify it matches the frontmatter `version:` field. | FAIL |

---

## Category 6: File Placement

| ID | Check | How to verify | Severity |
|----|-------|---------------|----------|
| P01 | Principles in correct directory | All files under `principles/` should have `type: principle` in frontmatter. No principle files should exist outside this directory. Grep all files for `type: principle` and verify they are under `principles/`. | FAIL |
| P02 | Guidelines in correct directory | All files under `guidelines/` should have `type: guideline`. No guideline files outside this directory. | FAIL |
| P03 | Recipes in correct directory | All files under `recipes/` should have `type: recipe`. No recipe files outside this directory. | FAIL |
| P04 | Workflows in correct directory | All files under `workflows/` should have `type: workflow`. No workflow files outside this directory. | FAIL |
| P05 | References in correct directory | All files under `reference/` should have `type: reference`. Exception: `index.md` and `introduction/conventions.md` may be type `reference` at the top level. | WARN |
| P06 | No .md files at repo root (except index) | The only `.md` file directly at the repo root should be `index.md`. All content should be in subdirectories. | WARN |
| P07 | File names are kebab-case | All content `.md` filenames should match `^[a-z0-9]+(-[a-z0-9]+)*\.md$` or be `index.md` or `_template.md`. No spaces, no uppercase, no underscores (except `_template`). | WARN |
| P08 | No stale or temp files | Check for files matching: `*.bak`, `*.tmp`, `*.orig`, `*~`, `.DS_Store`, `Thumbs.db` under content directories and `rules/`. | WARN |
| P09 | Directory names are kebab-case | All content directory names should match `^[a-z0-9]+(-[a-z0-9]+)*$`. No spaces, no uppercase. | WARN |
| P10 | Template files are prefixed with underscore | Files intended as templates should be named `_template.md` or `_*.md`. Verify no template-like files exist without the underscore prefix (grep for `{{placeholder}}` patterns in non-template files). | WARN |

---

## Category 7: Consumer Installation

Applies only in consumer mode. The consuming project is the current working directory; the cookbook is at `../agentic-cookbook/`.

| ID | Check | How to verify | Severity |
|----|-------|---------------|----------|
| V01 | Cookbook directory exists | Verify `../agentic-cookbook/` exists and contains `index.md`. | FAIL |
| V02 | CLAUDE.md references cookbook | Read the consuming project's `CLAUDE.md`. Verify it contains a reference to `agentic-cookbook` — either a path like `../agentic-cookbook/` or a mention of the cookbook repo. | FAIL |
| V03 | Expected path is correct | If the consuming project's `CLAUDE.md` specifies an expected path for the cookbook (e.g., `../agentic-cookbook/`), verify that path resolves to the actual cookbook directory. | FAIL |
| V04 | Tier rule file installed | Check if any rule file from the cookbook's `rules/` directory is referenced or copied into the consuming project's `.claude/` configuration. Look for files matching `*-RULE.md` in the consumer's project or references to tier rules in `CLAUDE.md`. | WARN |
| V05 | Cookbook is on main branch | Run `git -C ../agentic-cookbook branch --show-current` and verify the result is `main`. A consuming project should reference the stable main branch. | WARN |
| V06 | Cookbook is clean | Run `git -C ../agentic-cookbook status --porcelain` and verify no uncommitted changes. Dirty cookbook may have untested content. | WARN |
| V07 | Skills accessible | For each skill listed in `../agentic-cookbook/skills/`, verify the `SKILL.md` is readable from the consumer's context. Test by reading one skill file. | WARN |
| V08 | Cookbook version consistency | Read the cookbook's `CLAUDE.md` and compare against any version pinning in the consumer's `CLAUDE.md`. If the consumer pins a cookbook version or commit, verify it matches what is checked out. | WARN |
