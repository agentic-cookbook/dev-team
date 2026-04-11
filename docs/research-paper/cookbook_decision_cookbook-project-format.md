---
id: b8e2d4f1-3a7c-4b9e-a1d5-6f2c8e9b3d4a
title: "Format: Cookbook Project Definition (.acproj)"
domain: agentic-cookbook://appendix/decisions/cookbook-project-format
type: reference
version: 1.0.0
status: draft
language: en
created: 2026-04-01
modified: 2026-04-01
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Self-contained, platform-agnostic project format (cookbook-project.json) that defines an app as a tree of components, resources, and context — the source of truth from which native code is generated per platform."
platforms:
  - all
tags:
  - infrastructure
  - project-format
  - generation
depends-on: []
related: []
references: []
---

# Cookbook Project Format

## Problem

The agentic-cookbook contains principles, guidelines, and recipes that describe how to build software — but there's no structured way to define a specific application project that uses the cookbook. Developers need a self-contained, shareable project definition format that:

- Captures what an app *is* (components, resources, context) in a platform-agnostic way
- Serves as the source of truth from which native code is generated per platform
- Supports a bidirectional workflow: generate code, iterate, port improvements back to the project definition
- Is consumable primarily by LLMs, with human-readable tooling coming later
- Enables contribution of improved recipes back to the cookbook

## Decision

### Core Concept

A **cookbook project** is a directory containing a `cookbook-project.json` manifest and supporting files (recipes, resources, context documents). It is analogous to an Xcode project but at a higher abstraction level — it defines *what* to build, not *how*. Generation tools produce native, best-of-class code for any target platform.

The manifest is the **single source of truth**. Files in the directory that aren't referenced in the manifest are ignored (no-ops). The manifest defines the complete project tree, dependencies, resources, and context.

### Identification

- **Filename:** `cookbook-project.json` — self-identifying from a directory listing, opens as JSON on every platform
- **Type field:** `"type": "cookbook-project"` inside the file — machine-validatable
- **Directory naming:** Cookbook project directories MUST use the suffix `-cookbook-project` (e.g., `my-app-cookbook-project/`). This distinguishes cookbook projects from other directories and makes the project type immediately recognizable.
- **Discovery:** Tools glob for `**/cookbook-project.json` to find projects

### Platform Philosophy

The project format is **platform-agnostic**. It does not target any single platform. The cookbook's position is that multi-platform (native code per platform, not cross-platform compromise code) is the way forward with agentic programming. The same project definition generates to Swift/SwiftUI on Apple, Kotlin on Android, C#/WinUI on Windows, etc.

### Hierarchical Manifest

The manifest uses a nested component tree that mirrors the app's logical architecture. Chosen over flat manifests (unwieldy at scale) and multi-file manifests (harder for LLMs to get the full picture).

### Cookbook Relationship

Recipes in a project start from cookbook recipes when available — forked, copied into the project, and customized. The project tracks provenance (`source` field) to enable contribution of improvements back to the cookbook.

## Schema

### Project Identity & Metadata

```json
{
  "type": "cookbook-project",
  "schema_version": "1.0.0",
  "name": "My Document Editor",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "0.1.0",
  "description": "A multi-platform document editor with rich text and collaboration",
  "author": "Mike Fullerton",
  "license": "MIT",
  "created": "2026-04-01",
  "modified": "2026-04-01",
  "platforms": ["ios", "macos", "windows"],
  "cookbook": {
    "repo": "path/or/url/to/agentic-cookbook",
    "version": "1.0.0"
  }
}
```

| Field | Required | Description |
|---|---|---|
| `type` | Yes | Always `"cookbook-project"` — identifies this as a cookbook project |
| `schema_version` | Yes | Version of the project format itself (semver). Separate from the project's version so tools know how to parse it |
| `name` | Yes | Human-readable project name |
| `id` | Yes | UUID — stable identity even if the directory is renamed |
| `version` | Yes | Project version (semver) |
| `description` | Yes | One-line description of the project |
| `author` | Yes | Primary author |
| `license` | Yes | SPDX license identifier |
| `created` | Yes | ISO 8601 date, immutable |
| `modified` | Yes | ISO 8601 date, updated on changes |
| `platforms` | Yes | Target platforms (e.g., `["ios", "macos", "windows"]`). Project-level default; components can override |
| `cookbook` | Yes | Reference to the cookbook this project was built against |
| `cookbook.repo` | Yes | Path or URL to the agentic-cookbook |
| `cookbook.version` | Yes | Cookbook version the project is based on |

### Component Tree

The `components` field defines the app's architecture as a nested tree. Each component is a named node:

```json
{
  "components": {
    "app": {
      "recipe": "app/app.md",
      "description": "Application entry point and lifecycle",
      "platforms": ["ios", "macos"],
      "depends-on": [],
      "source": {
        "domain": "agentic-cookbook://recipes/ui/apps/apple",
        "version": "1.0.0"
      },
      "components": {
        "document-window": {
          "recipe": "app/document-window/document-window.md",
          "description": "Main document editing window",
          "depends-on": ["app.document-model"],
          "components": {
            "toolbar": {
              "recipe": "app/document-window/toolbar/toolbar.md"
            },
            "editor": {
              "recipe": "app/document-window/editor/editor.md",
              "depends-on": ["app.document-model", "app.document-window.toolbar"]
            }
          }
        },
        "settings": {
          "recipe": "app/settings/settings.md",
          "description": "Application preferences"
        }
      }
    }
  }
}
```

| Field | Required | Description |
|---|---|---|
| *(key)* | — | Kebab-case component identifier (the key in the parent's `components` object) |
| `recipe` | No | Relative path to the markdown recipe spec. If absent, the component is an organizational grouping node |
| `description` | No | Short summary so the LLM can understand the tree without reading every recipe |
| `platforms` | No | Platform override. Inherits from parent component or project-level default if absent |
| `depends-on` | No | Array of dot-path component keys this component depends on. Gives tools a build order and the LLM an architecture overview |
| `source` | No | Cookbook provenance — only present on components forked from the cookbook |
| `source.domain` | Yes (if `source`) | The cookbook domain identifier of the source recipe |
| `source.version` | Yes (if `source`) | The cookbook recipe version that was forked |
| `resources` | No | Component-scoped resources (see Resources section) |
| `components` | No | Nested child components. Arbitrary depth |

**Rules:**
- A component without `recipe` is a valid grouping node
- Nesting depth is unlimited — mirrors how apps are structured (app > windows > views > subviews)
- `depends-on` references are dot-path component keys within the project (e.g., `"app.document-window.toolbar"`), not cookbook domain identifiers. This avoids ambiguity when the same key appears at different levels of the tree
- `source` enables diffing project recipe against the cookbook version for contribution back

### Resources

Resources are platform-agnostic definitions of assets and configs that generate to native formats. They exist at both project level and component level:

**Project-level resources** (shared across the app):

```json
{
  "resources": {
    "app-icon": {
      "type": "asset-catalog",
      "path": "resources/app-icon.json",
      "description": "Application icon set"
    },
    "app-config": {
      "type": "app-manifest",
      "path": "resources/app-config.json",
      "description": "Bundle ID, version, capabilities — generates to Info.plist, AndroidManifest, etc."
    },
    "strings": {
      "type": "localization",
      "path": "resources/strings.json",
      "description": "App-wide localized strings"
    }
  }
}
```

**Component-level resources** (scoped to a component):

```json
{
  "document-window": {
    "recipe": "app/document-window/document-window.md",
    "resources": {
      "icons": {
        "type": "asset-catalog",
        "path": "app/document-window/resources/icons.json",
        "description": "Toolbar and status icons"
      },
      "strings": {
        "type": "localization",
        "path": "app/document-window/resources/strings.json",
        "description": "UI strings, 3 languages"
      }
    }
  }
}
```

| Field | Required | Description |
|---|---|---|
| *(key)* | — | Kebab-case resource identifier |
| `type` | Yes | Resource category. Tells generation tools how to handle it |
| `path` | Yes | Relative path to the resource definition file (JSON) |
| `description` | No | What this resource contains |

**Initial resource types:**

| Type | Description | Example generation targets |
|---|---|---|
| `localization` | Translated UI strings | `.strings`/`.stringsdict` (Apple), `.xml` (Android), `.resx` (Windows) |
| `asset-catalog` | Images, icons, color sets | `.xcassets` (Apple), `drawable/` (Android), asset bundles (Windows) |
| `app-manifest` | App identity, capabilities, permissions | `Info.plist` (Apple), `AndroidManifest.xml`, `Package.appxmanifest` (Windows) |
| `sound` | Audio assets | Platform-native audio formats |
| `data` | Static data files (JSON, CSV, etc.) | Bundled as-is or transformed per platform |

Resource types are extensible — new types can be added as needs arise.

### Context

Project-wide supporting material — research, decisions, notes. Not generated to code, but provides background for the LLM:

```json
{
  "context": {
    "research": {
      "auth-evaluation": {
        "type": "research",
        "path": "context/research/auth-evaluation.md",
        "description": "Evaluated OAuth vs passkeys vs magic link — chose passkeys"
      }
    },
    "decisions": {
      "offline-first": {
        "type": "decision",
        "path": "context/decisions/offline-first.md",
        "description": "App will be offline-first with sync, not cloud-dependent"
      }
    },
    "notes": {
      "user-feedback-round-1": {
        "type": "note",
        "path": "context/notes/user-feedback-round-1.md",
        "description": "Notes from first round of user interviews"
      }
    }
  }
}
```

| Field | Required | Description |
|---|---|---|
| `context.research` | No | Supporting evidence, evaluations, comparisons |
| `context.decisions` | No | Authoritative architectural decisions |
| `context.notes` | No | Informational notes, interview transcripts, freeform material |

Each entry has:

| Field | Required | Description |
|---|---|---|
| *(key)* | — | Kebab-case identifier |
| `type` | Yes | `research`, `decision`, or `note` — signals to the LLM how to weigh the content |
| `path` | Yes | Relative path to the markdown file |
| `description` | No | Short summary |

**Integration with agentic-interview-team:** Interview transcripts and analyses flow naturally into `context/research/`. The interview team discovers requirements; the project captures them.

## Directory Layout

A typical project directory:

```
my-app-cookbook-project/
├── cookbook-project.json
├── app/
│   ├── app.md
│   ├── document-window/
│   │   ├── document-window.md
│   │   ├── resources/
│   │   │   ├── icons.json
│   │   │   └── strings.json
│   │   ├── toolbar/
│   │   │   └── toolbar.md
│   │   └── editor/
│   │       └── editor.md
│   └── settings/
│       └── settings.md
├── resources/
│   ├── app-icon.json
│   ├── app-config.json
│   └── strings.json
└── context/
    ├── research/
    │   └── auth-evaluation.md
    ├── decisions/
    │   └── offline-first.md
    └── notes/
        └── user-feedback-round-1.md
```

**Convention:** Directory structure mirrors the component tree, but the manifest is authoritative. Files not referenced in the manifest are ignored.

## Lifecycle

1. **Create** — User describes what they want to build (possibly via agentic-interview-team). A creation tool scaffolds the project directory and `cookbook-project.json`, pulling starter recipes from the cookbook where available.
2. **Refine** — User and LLM iterate on the project definition — adding components, customizing recipes, adding resources and context. The manifest is updated as the project evolves.
3. **Generate** — Generation tools read the manifest and recipes, producing native code for the target platform(s) (e.g., an Xcode project for iOS/macOS).
4. **Iterate** — User runs, tests, and refines the generated code. Improvements are ported back to the project recipes.
5. **Contribute** — Improvements to forked recipes can be contributed back to the cookbook via the existing contribution workflow. The `source` field enables diffing against the original.

## Future Tooling (Out of Scope for This Decision)

- **Project creation skill** — scaffolds a new project from user input
- **Component management skills** — add/remove/move components in the manifest
- **Generation pipeline** — reads manifest + recipes, produces platform-native projects
- **Sync tools** — port generated project changes back to project recipes
- **Validation** — schema validation of `cookbook-project.json`
- **Human-readable viewer** — renders the project in a browsable format
- **IDE integration** — the cookbook IDE being built with the cookbook itself

## Change History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-04-01 | Mike Fullerton | Initial design spec |
