# Application Map Specification

Version: 1.0.0

The formal specification for the application map produced by the decomposition-synthesizer agent. This is the machine-referenceable contract for the primary output of the codebase-decomposition specialist pipeline.

## Purpose

The application map is an annotated, hierarchical decomposition of a codebase. It serves as the blueprint for a cookbook project: the tree becomes the component hierarchy, each node becomes a recipe, and the edges become dependency relationships.

## File Location

Written to `<output>/context/research/application-map.md` during the `create-recipe-from-code` workflow.

## Document Structure

The application map is a markdown document with YAML frontmatter followed by structured sections.

### Frontmatter

```yaml
---
id: <UUID v4>
title: "Application Map — <project-name>"
type: application-map
version: 1.0.0
created: <ISO 8601 date>
modified: <ISO 8601 date>
author: decomposition-synthesizer
repo: <absolute path to analyzed repo>
summary: "<one-line summary of what was analyzed>"
---
```

| Field | Required | Format | Description |
|-------|----------|--------|-------------|
| id | YES | UUID v4 | Unique identifier |
| title | YES | String | "Application Map — <name>" |
| type | YES | `application-map` | Document type discriminator |
| version | YES | Semver | Spec version this map conforms to |
| created | YES | ISO 8601 date | Creation timestamp |
| modified | YES | ISO 8601 date | Last modification timestamp |
| author | YES | String | Always `decomposition-synthesizer` |
| repo | YES | Absolute path | Root of the analyzed codebase |
| summary | YES | String | One-line description |

### Required Sections

Sections MUST appear in this order.

#### 1. Overview

```markdown
## Overview

- **Repo:** <absolute path>
- **Total source files:** <N>
- **Tree depth:** <N levels>
- **Total nodes:** <N>
- **Nodes with recipes:** <N>
- **Cross-cutting concerns:** <comma-separated list>
- **Recipe order:** bottom-up, <N> recipes
```

All fields required. Counts must be exact (derived from the tree, not estimated).

#### 2. File Index

```markdown
## File Index

| File | Node |
|------|------|
| <relative path from repo root> | <node name> |
| ... | ... |
```

Every source file in the repo MUST appear exactly once. No file may be unmapped. No file may appear in multiple nodes. Paths are relative to the repo root.

**Excluded files:** Build artifacts, generated code, vendored dependencies, and non-source files (images, assets, config) MAY be excluded. If excluded, list the exclusion patterns:

```markdown
### Excluded Patterns
- `build/`, `dist/`, `.build/`
- `Pods/`, `node_modules/`, `vendor/`
- `*.generated.swift`, `*.pb.go`
```

#### 3. Tree

```markdown
## Tree

<ASCII tree showing the full hierarchy with recipe markers>
```

Format:
```
App [R:25]
├── Core [R:24]
│   ├── Auth Service [R:15]
│   │   ├── Token Manager [R:1]
│   │   └── Session Store [R:2]
│   ├── Data Layer [R:20]
│   │   ├── Schema Manager [R:3]
│   │   └── Sync Engine [R:10]
│   └── Networking [R:14]
├── Features
│   ├── Chat [R:22]
│   │   ├── Message List [R:11]
│   │   ├── Composer [R:12]
│   │   └── Media Picker [R:13]
│   └── Settings [R:23]
│       ├── Account [R:16]
│       └── Preferences [R:17]
└── Infrastructure
    ├── Logging [R:4]
    └── Analytics [R:5]
```

- `[R:N]` — recipe order number. Present only on nodes with `recipe: true`.
- Nodes without `[R:N]` are structural grouping nodes (no recipe generated).
- Tree MUST include every node. No omissions.

#### 4. Nodes

One subsection per node, ordered by recipe order (nodes without recipes listed after all recipe nodes).

```markdown
## Nodes

### <Node Name>

- **Recipe:** yes | no
- **Recipe order:** <N> (omit if recipe: no)
- **Parent:** <parent node name> (omit for root)
- **Children:** <comma-separated child names> | leaf
- **Path:** <primary directory or file path, relative to repo root>
- **Files:**
  - `<relative path>`
  - `<relative path>`
  - ...

#### Annotations

- **Purpose:** <primary purpose classification>
- **Algorithmic complexity:** <complexity profile>
- **Dependencies (internal):** <list of node names>
- **Dependencies (external):** <libraries, OS frameworks, system services>
- **Runtime conditions:** <permissions, entitlements, env requirements>
- **App interactions:** <communication patterns with other nodes>
- **System interactions:** <OS-level interactions>
- **Lifecycle:** <init/teardown pattern>
- **Framework convention:** <pattern name or "none detected">
- **Cross-cutting concerns:** <concerns passing through this node>

#### Edges

- **depends-on:** [<node>, <node>, ...]
- **depended-on-by:** [<node>, <node>, ...]
- **interacts-with:** [<node> (<pattern>), ...]

#### Feature Flows

- **<Flow name>:** <Node1> → <Node2> → <Node3> → ...
- **<Flow name>:** <Node1> → <Node2> → ...
```

##### Node Field Rules

| Field | Required | Rule |
|-------|----------|------|
| Recipe | YES | `yes` or `no` |
| Recipe order | If recipe: yes | Positive integer, unique across all nodes |
| Parent | All except root | Must reference an existing node name |
| Children | YES | Comma-separated names or `leaf` |
| Path | YES | Relative to repo root |
| Files | YES | At least one file. Each file must appear in File Index. |
| Purpose | YES | From purpose-classification lens |
| Algorithmic complexity | NO | Omit if lens had no findings |
| Dependencies (internal) | NO | Omit if none. Each must reference an existing node. |
| Dependencies (external) | NO | Omit if none |
| Runtime conditions | NO | Omit if none |
| App interactions | NO | Omit if none |
| System interactions | NO | Omit if none |
| Lifecycle | NO | Omit if lens had no findings |
| Framework convention | NO | Omit if none detected |
| Cross-cutting concerns | NO | Omit if none pass through |
| depends-on | NO | Node names. Each must exist in the tree. |
| depended-on-by | NO | Node names. Inverse of depends-on (computed). |
| interacts-with | NO | Node name + interaction pattern in parens. |
| Feature flows | NO | Omit if no user-facing flows pass through. |

##### Annotation Rules

- Annotations MUST be derived from specialty-team findings. Do not invent annotations.
- If a lens had no findings for a node, omit that annotation entirely. Do not write "none" or "N/A".
- Dependencies (internal) MUST reference node names, not file paths.
- Dependencies (external) MUST name specific libraries/frameworks, not categories.

#### 5. Feature Flows

```markdown
## Feature Flows

### <Flow Name>
<Node1> → <Node2> → <Node3> → <Node4>

**Trigger:** <what initiates this flow>
**Data:** <what data moves through the flow>
**Nodes involved:** <comma-separated node names>
```

List all user-facing feature flows that span 3+ nodes. Each flow must reference only nodes that exist in the tree.

#### 6. Cross-Cutting Concerns

```markdown
## Cross-Cutting Concerns

### <Concern Name>
- **Type:** cross-cutting | shared-infrastructure
- **Nodes affected:** <comma-separated node names>
- **Dedicated code:** <node name if shared-infrastructure, "none" if pure cross-cutting>
- **Description:** <one sentence>
```

Every concern identified by the cross-cutting-detection lens MUST appear here. Classification:
- **cross-cutting**: No dedicated code node. Manifests as calls/patterns scattered across nodes (e.g., logging calls, retry logic).
- **shared-infrastructure**: Has its own code node in the tree. Other nodes depend on it (e.g., a logging framework, an auth service).

## Validation Rules

### Structural (S-series)

| ID | Rule | Severity |
|----|------|----------|
| S01 | Frontmatter has all required fields | FAIL |
| S02 | All required sections present in order: Overview, File Index, Tree, Nodes, Feature Flows, Cross-Cutting Concerns | FAIL |
| S03 | Every file in File Index maps to exactly one node | FAIL |
| S04 | Every node's Files list entries appear in File Index with matching node | FAIL |
| S05 | Every node (except root) has a Parent that exists in the tree | FAIL |
| S06 | Every Children reference points to an existing node | FAIL |
| S07 | Recipe order numbers are unique positive integers | FAIL |
| S08 | Recipe order is a valid topological sort (no node ordered before its dependencies) | FAIL |

### Content (C-series)

| ID | Rule | Severity |
|----|------|----------|
| C01 | No source file left unmapped in File Index | FAIL |
| C02 | depends-on edges reference existing nodes | FAIL |
| C03 | depended-on-by is the exact inverse of depends-on across all nodes | WARN |
| C04 | Feature flows reference only existing nodes | FAIL |
| C05 | Cross-cutting concerns reference only existing nodes | FAIL |
| C06 | Every node with recipe: yes has a Purpose annotation | WARN |
| C07 | Overview counts match actual tree contents | WARN |
| C08 | Tree ASCII visualization matches the Nodes section | WARN |

## Relationship to Cookbook Project

The application map drives cookbook project creation:

| Map concept | Cookbook project concept |
|-------------|----------------------|
| Tree hierarchy | Component tree in `cookbook-project.json` |
| Node with recipe: yes | Component with a `recipe` field |
| Node with recipe: no | Structural group node (no recipe) |
| Node files | Recipe's source file references |
| Node annotations | Recipe content (behavioral requirements, edge cases, etc.) |
| depends-on edges | Component `depends-on` array |
| Recipe order | Order in which recipe-writer processes nodes |
| Feature flows | Documented in recipes that participate |
| Cross-cutting concerns | Noted in each recipe's cross-cutting section |
