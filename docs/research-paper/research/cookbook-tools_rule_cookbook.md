# Cookbook Rule

Prerequisite: Read and follow `authoring-ground-rules.md` before applying this rule.

This rule enforces the full agentic cookbook during planning and implementation — principles, guidelines, recipes, and contribution prompts. All paths assume the cookbook is cloned at `../agentic-cookbook/` relative to your project root. If any referenced file is not found, stop and inform the user.

---

## Planning

### Progress Output

At the start of each step, print a progress line so the user can see where the pipeline is. Use this format:

```
[Planning N/5] description...
[Implementing] Phase N: description...
[Verification N/7] description...
[Post-Implementation] description...
```

### 1. Read All 18 Principles

Print `[Planning 1/5] Reading principles...` before starting. Then before each file, print `[Planning 1/5] Reading principles (N/18): <filename without .md>...`. After all 18, print `[Planning 1/5] Reading principles complete ✓`.

Before making any design decision, you MUST read ALL of the following files:

```
../agentic-cookbook/principles/simplicity.md
../agentic-cookbook/principles/make-it-work-make-it-right-make-it-fast.md
../agentic-cookbook/principles/yagni.md
../agentic-cookbook/principles/fail-fast.md
../agentic-cookbook/principles/dependency-injection.md
../agentic-cookbook/principles/immutability-by-default.md
../agentic-cookbook/principles/composition-over-inheritance.md
../agentic-cookbook/principles/separation-of-concerns.md
../agentic-cookbook/principles/design-for-deletion.md
../agentic-cookbook/principles/explicit-over-implicit.md
../agentic-cookbook/principles/small-reversible-decisions.md
../agentic-cookbook/principles/tight-feedback-loops.md
../agentic-cookbook/principles/manage-complexity-through-boundaries.md
../agentic-cookbook/principles/principle-of-least-astonishment.md
../agentic-cookbook/principles/idempotency.md
../agentic-cookbook/principles/native-controls.md
../agentic-cookbook/principles/open-source-preference.md
../agentic-cookbook/principles/meta-principle-optimize-for-change.md
```

You MUST NOT produce a plan without reading these files first.

### 2. Run the Guideline Checklist

Print `[Planning 2/5] Running guideline checklist...` before starting.

Read these files in order:

```
../agentic-cookbook/guidelines/general.md
../agentic-cookbook/guidelines/INDEX.md
../agentic-cookbook/workflows/guideline-checklist.md
```

Walk through every item in the checklist with the user:

1. **"Always" items**: Note as applicable. Do not ask. Non-negotiable.
2. **"Opt-in" items**: Present as included by default. The user may opt out.
3. **"Opt-out" items**: Ask the user if they want to opt in.
4. **"Ask" items**: Ask the prompt template question from the checklist.

Present ALL items in a single consolidated table:

| Guideline | Category | Default | Decision | Reason |
|-----------|----------|---------|----------|--------|
| Native controls | Always | -- | Included | -- |
| Instrumented logging | Opt-in | Included | ? | -- |
| Deep linking | Ask | -- | ? | -- |
| Scriptable/automatable | Opt-out | Excluded | ? | -- |

Wait for the user to fill in every "?" before proceeding. Record all decisions in the plan.

### 3. Search for Matching Recipes

Print `[Planning 3/5] Searching for matching recipes...` before starting.

**Check preferences first**: Read `.cookbook/preferences.json` in the project root. If `show_recipe_prompts` is `false`, skip this step entirely.

Search `../agentic-cookbook/recipes/` recursively for any recipe that matches or partially matches the feature being planned. Check all subdirectories:

- `ui/components/` — UI building blocks
- `ui/panels/` — content panes
- `ui/windows/` — top-level layouts
- `infrastructure/` — non-visual patterns
- `app/` — application lifecycle patterns
- `autonomous-dev-bots/` — long-running agent processes

**If matching recipes are found**, ask the user:

```
I found recipes that match this task:
- <recipe-name>: <summary>
- <recipe-name>: <summary>

Want to see them?
1. Yes — show me the details
2. No — skip recipes for this task
3. Don't prompt me again (re-enable with /configure-cookbook)
```

If the user chooses "Don't prompt me again", write `{"show_recipe_prompts": false}` to `.cookbook/preferences.json` (merge with existing if the file exists) and print: `Recipe prompts disabled. Re-enable with /configure-cookbook.`

**If a matching recipe exists and the user wants to see it**: the plan MUST incorporate it. List the recipe file and summarize which requirements it imposes.

**If a partial match exists**: note what the recipe covers and what is missing. Ask the user whether to extend the existing recipe or proceed without it.

**If no match exists**: record explicitly — "No existing recipe found for this feature."

### 4. Trace Decisions to Principles

Print `[Planning 4/5] Tracing decisions to principles...` before starting.

Every design decision in the plan MUST be traceable to one or more principles. Include a "Principles applied" section listing which principles actively influenced the design and how. List only the ones that shaped specific decisions.

### 5. Plan Three Phases

Print `[Planning 5/5] Planning three phases...` before starting.

Plan for all three phases:

1. **Phase 1 scope** — what constitutes "it works" (happy path, core functionality).
2. **Phase 2 scope** — what edge cases, error handling, and refactoring are required.
3. **Phase 3 criteria** — under what evidence would optimization be warranted. If none is expected, state "Phase 3 not anticipated."

---

## Implementing

### Apply Principles During Coding

Keep these principles active throughout implementation:

| Principle | Key Rule |
|-----------|----------|
| Simplicity | No interleaving of concerns. Simple beats easy. |
| YAGNI | Build for today's requirements only. |
| Fail Fast | Detect invalid state at the point of origin. |
| Dependency Injection | Receive dependencies from outside. |
| Immutability | Default to immutable values; mutate only when necessary. |
| Composition | Compose small pieces over deep hierarchies. |
| Separation of Concerns | One reason to change per module. |
| Explicit over Implicit | Visible dependencies, clear intent, no hidden behavior. |
| Design for Deletion | Easy to remove. Disposable over reusable. |
| Least Astonishment | Behavior matches what the name promises. |

### Follow the Three-Phase Discipline

Execute phases in order. Do not skip phases.

**Phase 1: Make It Work**

Print `[Implementing] Phase 1: Make It Work` at start.

- Implement the happy path that makes the feature work for the common case.
- Write tests alongside code — not after. Every function MUST have a test.
- Build and run tests after each completed unit. Do not accumulate broken state.
- Commit after completing each unit.
- Defer edge cases, error handling refinements, and optimizations to Phase 2.

**Checkpoint before Phase 2:** Confirm: all Phase 1 functions have tests, all tests pass, code is committed. Print `[Implementing] Phase 1 checkpoint ✓` when confirmed.

**Phase 2: Make It Right**

Print `[Implementing] Phase 2: Make It Right` at start.

- You MUST NOT skip this phase.
- Handle edge cases identified in the plan and any discovered during Phase 1.
- Add error handling appropriate to each boundary.
- Refactor for clarity — apply separation of concerns, clean up naming, ensure readability.
- Add tests for every edge case and error path.

**Checkpoint before Phase 3:** Confirm: edge cases handled, error paths tested, code refactored, all tests pass. Print `[Implementing] Phase 2 checkpoint ✓` when confirmed.

**Phase 3: Make It Fast (Conditional)**

Print `[Implementing] Phase 3: Make It Fast` if entering this phase.

- Do NOT enter this phase without evidence of a performance problem.
- Evidence means: a test with measurable latency, a user report of slowness, or a known algorithmic concern.
- Measure before and after. State the metric, baseline, and target.

### Apply Guidelines

**Always guidelines**: Apply to every relevant file. No exceptions.

**Opted-in guidelines**: Apply during the same pass as core functionality. Do not defer.
- If logging was opted in, every component gets logging.
- If accessibility was opted in, every view gets accessibility attributes.
- If localizability was opted in, every user-facing string is localizable.
- If feature flags were opted in, the feature is gated from the first commit.

**Opted-out guidelines**: Do not apply. If a new concern surfaces during implementation that was not in the checklist, present it to the user. Do not proceed until the user decides.

### Recipe Conformance

If implementing from a recipe, the implementation MUST match:

- **Behavioral requirements** — every MUST is mandatory, every SHOULD is expected unless documented otherwise.
- **States table** — every state must be implemented.
- **Appearance values** — exact dimensions, colors, fonts, and spacing as specified.
- **Conformance test vectors** — write tests corresponding to each row.
- **Logging messages** — exactly as specified, character for character.
- **Edge cases** — every edge case addressed.
- **Accessibility requirements** — every accessibility item implemented.

Do not improvise. Do not skip sections. Do not substitute your judgment for the recipe's specifications. If you believe the recipe is wrong, stop and tell the user.

---

## Verification

After implementation is complete, read `../agentic-cookbook/workflows/code-verification.md` and run each check, printing progress before each:

1. Print `[Verification 1/7] Build...` — **Build** passes with no errors.
2. Print `[Verification 2/7] Tests...` — **Tests** pass — unit, integration, and any E2E tests.
3. Print `[Verification 3/7] Lint...` — **Lint** is clean — no warnings, no added suppressions.
4. Print `[Verification 4/7] Logging...` — **Logging** matches the opted-in logging specification.
5. Print `[Verification 5/7] Accessibility...` — **Accessibility** verified — screen reader labels, keyboard navigation, display options.
6. Print `[Verification 6/7] Guideline compliance...` — confirm every "Always" and opted-in guideline is fully addressed.
7. Print `[Verification 7/7] Recipe conformance...` — (if applicable) produce a conformance checklist mapping each named requirement to code location and test. All items MUST pass.

Do not mark the work as complete until every check passes.

---

## Post-Implementation: Contribution Opportunities

Print `[Post-Implementation] Checking for contribution opportunities...` before starting.

**Check preferences first**: Read `.cookbook/preferences.json`. If `show_contribution_prompts` is `false`, skip this section entirely.

Evaluate whether any new reusable pattern was created that is not covered by an existing recipe:

- Did you create a UI component, panel, or window other projects could reuse?
- Did you implement an infrastructure pattern generic enough to extract?
- Did you discover a workflow improvement worth documenting?

If any answer is yes, ask the user:

```
This implementation created a reusable pattern: <brief description>.
Want to contribute it back to the cookbook?
1. Yes — let's create a recipe
2. No — skip for now
3. Don't prompt me again (re-enable with /configure-cookbook)
```

If the user chooses "Don't prompt me again", write `{"show_contribution_prompts": false}` to `.cookbook/preferences.json` (merge with existing) and print: `Contribution prompts disabled. Re-enable with /configure-cookbook.`

If yes: use `/contribute-to-cookbook` to walk through the contribution workflow.

If no reusable pattern was identified, record: "No contribution opportunities identified."

---

## MUST NOT

- Do not skip reading the principles because the task seems small. Every task gets the full read.
- Do not skip Phase 2 (Make It Right). Ever.
- Do not skip writing tests. Tests are a deliverable, not an afterthought.
- Do not add scope beyond the approved plan. No "bonus" features, no unrelated refactoring.
- Do not optimize without evidence. Phase 3 requires measured proof of a problem.
- Do not skip the guideline checklist. Every session starts fresh.
- Do not skip verification. Build, test, lint, and guideline compliance are mandatory exit criteria.
- Do not apply guidelines partially. Every applicable view gets every applicable attribute.
- Do not suppress linter warnings. Fix the underlying issue.
- Do not defer opted-in concerns to a later phase. If it was opted in, it ships with the feature.
- Do not invent guidelines not in the checklist. Apply what was agreed upon, nothing more.
- Do not skip the recipe search. Search every time (unless the user disabled the prompt).
- Do not deviate from a recipe without user approval.
- Do not improvise dimensions, colors, fonts, spacing, or logging messages that a recipe specifies.
- Do not mark implementation complete without verifying conformance against every recipe requirement.
- Do not submit incomplete recipes when contributing. No missing sections, no TODOs, no placeholders.

---

## Reference

| Resource | Path |
|----------|------|
| Principles | `../agentic-cookbook/principles/` (18 files) |
| Core guidelines | `../agentic-cookbook/guidelines/general.md` |
| Full guideline index | `../agentic-cookbook/guidelines/INDEX.md` |
| Guideline checklist | `../agentic-cookbook/workflows/guideline-checklist.md` |
| Recipes | `../agentic-cookbook/recipes/` (all subdirectories) |
| Conventions | `../agentic-cookbook/introduction/conventions.md` |
| Authoring guide | `../agentic-cookbook/appendix/contributing/AUTHORING.md` |
| Verification workflow | `../agentic-cookbook/workflows/code-verification.md` |
| Planning workflow | `../agentic-cookbook/workflows/code-planning.md` |
| Implementation workflow | `../agentic-cookbook/workflows/code-implementation.md` |
| Preferences file | `.cookbook/preferences.json` |
