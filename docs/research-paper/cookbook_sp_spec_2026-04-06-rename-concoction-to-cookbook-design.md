# Rename Concoction to Project Cookbook

## Summary

Rename the "concoction" concept to "project cookbook" across the entire repo. Introduce a clear distinction between two kinds of cookbooks:

- **Top-level cookbook** — this repo (`agentic-cookbook/cookbook`), the source of principles, guidelines, ingredients, and recipes.
- **Project cookbook** — an assembly of recipes and ingredients into a complete application, plugin, or widget. Defined by a `cookbook.json` manifest in a directory with a `-cookbook` suffix. Replaces the former "concoction" concept.

## Motivation

"Concoction" is an awkward term that doesn't fit naturally with the cooking metaphor (ingredients, recipes). "Cookbook" is the natural top of that hierarchy and is more intuitive. The distinction between top-level and project cookbooks makes the relationship clear: the top-level cookbook provides the building blocks, and project cookbooks assemble them.

## Changes

### File renames (4 files/dirs)

| Current path | New path |
|---|---|
| `reference/concoction.schema.json` | `reference/cookbook.schema.json` |
| `reference/examples/my-document-editor-concoction/` | `reference/examples/my-document-editor-cookbook/` |
| `reference/examples/my-document-editor-concoction/concoction.json` | `reference/examples/my-document-editor-cookbook/cookbook.json` |
| `compliance/artifact-formatting/concoction-formatting.md` | `compliance/artifact-formatting/cookbook-formatting.md` |
| `appendix/decisions/ingredient-recipe-concoction-hierarchy.md` | `appendix/decisions/ingredient-recipe-cookbook-hierarchy.md` |

### Content updates (13 files)

Every occurrence of "concoction" is replaced with "cookbook" or "project cookbook" as appropriate. The `type` enum value in frontmatter changes from `concoction` to `cookbook`.

| File | Changes |
|---|---|
| `introduction/glossary.md` | Replace "Concoction" definition with "Project Cookbook". Update "Structural Element" definition. |
| `introduction/conventions.md` | Update type enum (`concoction` → `cookbook`). Update naming section (directory suffix `-concoction` → `-cookbook`). Update examples. |
| `README.md` | Replace all concoction references with project cookbook. |
| `.claude/CLAUDE.md` | Update artifact table and concoction reference. |
| `index.md` | Update concoction references. |
| `reference/cookbook.schema.json` (after rename) | Update internal descriptions and title. |
| `reference/examples/my-document-editor-cookbook/cookbook.json` (after rename) | Update if any internal references use "concoction". |
| `reference/examples/INDEX.md` | Update path and description references. |
| `compliance/artifact-formatting/cookbook-formatting.md` (after rename) | Replace all "concoction" with "cookbook" in content and frontmatter. |
| `compliance/artifact-formatting/INDEX.md` | Update filename reference and descriptions. |
| `compliance/INDEX.md` | Update reference. |
| `appendix/decisions/ingredient-recipe-cookbook-hierarchy.md` (after rename) | Update title, content, and domain. |
| `.claude/rules/artifact-formatting.md` | Update compliance file reference. |

### New concept: cookbook types

The glossary and conventions will document two cookbook types:

- **Top-level cookbook**: The source repository of principles, guidelines, ingredients, and recipes. This repo is a top-level cookbook.
- **Project cookbook**: An assembly of recipes and ingredients into a complete deliverable. Defined by a `cookbook.json` manifest. Directory suffix: `-cookbook`.

### Domain identifier changes

Any `agentic-cookbook://` domain paths that include "concoction" in the path update accordingly:
- `compliance/artifact-formatting/concoction-formatting` → `compliance/artifact-formatting/cookbook-formatting`
- `appendix/decisions/ingredient-recipe-concoction-hierarchy` → `appendix/decisions/ingredient-recipe-cookbook-hierarchy`

### Type enum

The frontmatter `type` field value changes from `concoction` to `cookbook` in:
- `introduction/conventions.md` (the type definition)
- `compliance/artifact-formatting/cookbook-formatting.md` (the formatting spec itself)
- Any artifact that currently has `type: concoction`

## Out of scope

- No changes to the artifact hierarchy (ingredient → recipe → cookbook remains the same structure)
- No changes to `cookbook.json` schema fields beyond renaming
- No changes to sibling projects (dev-team, cookbook-web) — those will be updated separately
