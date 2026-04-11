---
id: 4F351323-DB4C-4C7A-9972-AF89A6982E3F
title: "Ingredient / Recipe / Cookbook Artifact Hierarchy"
domain: agentic-cookbook://appendix/decisions/ingredient-recipe-cookbook-hierarchy
type: reference
version: 1.1.0
status: draft
language: en
created: 2026-04-05
modified: 2026-04-06
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Three-tier artifact hierarchy — ingredients (atomic specs), recipes (compositions), cookbooks (app assemblies) — replacing the flat recipe model and cookbook-project naming."
platforms: []
tags:
  - architecture
  - artifact-types
  - naming
depends-on:
  - agentic-cookbook://appendix/decisions/cookbook-project-format
related:
  - agentic-cookbook://introduction/conventions
  - agentic-cookbook://introduction/glossary
references: []
---

# Ingredient / Recipe / Cookbook Artifact Hierarchy

## Problem

The cookbook's artifact abstraction had two issues:

1. **"Recipe" conflated atoms and compositions.** All 27 recipes were atomic component specs (empty-state, file-tree-browser, settings-window). There was no way to define how multiple specs wire together into a coherent feature — that composition only existed implicitly in the cookbook-project manifest's component tree.

2. **"Cookbook-project" was overloaded.** The word "project" collides with IDE projects, GitHub projects, and general usage. Every conversation about cookbook projects required disambiguation.

## Decision

Introduce a three-tier hierarchy:

| Tier | Type | Format | Purpose |
|------|------|--------|---------|
| Atom | `ingredient` | Markdown (21 sections) | Individual component spec with behavioral requirements, appearance, states, configuration options, test vectors, and platform notes |
| Composition | `recipe` | Markdown (13 sections) | Combines configured ingredients into a coherent feature — defines integration requirements, layout, shared state, and integration test vectors |
| Assembly | `cookbook` | JSON manifest (`cookbook.json`) | Full app/plugin/widget definition — a hierarchical structure of structural elements with resources and context |

### Key design choices

**Ingredients declare configurable options.** Each ingredient has a `## Configuration` section listing the knobs it exposes (option name, type, default, description). Recipes specify configuration values when including an ingredient.

**Recipes are integration-focused.** A recipe does not repeat per-component detail (appearance, states, accessibility) — that lives in the ingredients. A recipe answers: how do these ingredients wire together? What state flows between them? What breaks at the integration boundaries?

**Cookbooks use "structure" not "components."** The manifest's top-level field is `"structure"` (a single object representing the thing being built), with `"structural-elements"` for children. Each node references a `"spec"` file (not `"recipe"`), since it could be based on either an ingredient or a recipe.

**Principles and guidelines are unchanged.** They sit alongside the ingredient/recipe/cookbook hierarchy as reference material, not part of the cooking metaphor.

## Alternatives Considered

### Minimal type extension

Add `ingredient` and `concoction` as types but keep one shared markdown format for both ingredients and recipes, differentiating only by the `type` field.

**Rejected because:** ingredients and recipes answer fundamentally different questions. A shared format would have many N/A sections in recipes and missing integration sections in ingredients. Purpose-built formats are clearer for both LLM and human consumers.

### Single format with conditional sections

One markdown format with conditional compliance checks: "applies when type is ingredient," "applies when type is recipe."

**Rejected because:** conditional compliance is harder to reason about and implement in tooling. Separate formats with separate compliance files are simpler.

## Schema Changes

The `cookbook-project.schema.json` is superseded by `cookbook.schema.json`. Key renames:

| Old | New |
|-----|-----|
| `"type": "cookbook-project"` | `"type": "cookbook"` |
| `"components"` (top-level dict) | `"structure"` (single object) |
| `"components"` (nested) | `"structural-elements"` |
| `"recipe"` (spec path) | `"spec"` |
| `$defs/component` | `$defs/structural-element` |
| `*-cookbook-project/` directory suffix | `*-cookbook/` |

## Scope

This decision defines the formats and schema only. Reclassification of the existing 27 recipes into ingredients and recipes is a separate future effort.

## Sibling Project Impact

### cookbook-web

Will need updates to recognize the three artifact tiers:
- New route structure for `/ingredients/`
- Updated navigation to show ingredients vs recipes
- Cookbook rendering (if the web app shows project definitions)

### dev-team

Skills referencing "recipe" need audit:
- `/plan-cookbook-recipe` — may need renaming or handling both types
- `/dev-team lint` — must recognize `type: ingredient`
- `/validate-cookbook` — must validate `ingredients/` directory and new frontmatter fields
- Artifact skills (`/lint-artifact`, `/approve-artifact`, `/create-artifact`) — must handle `type: ingredient`
- Agent descriptions that say "recipe" may need updating

These are documented here as future work items, not part of this decision's implementation scope.

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.1.0 | 2026-04-06 | Mike Fullerton | Rename concoction to cookbook throughout |
| 1.0.0 | 2026-04-05 | Mike Fullerton | Initial decision |
