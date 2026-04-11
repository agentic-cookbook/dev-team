---
id: 39931D07-F23F-4980-A055-6916E722A01F
title: "Guideline Formatting Compliance"
domain: agentic-cookbook://compliance/artifact-formatting/guideline-formatting
type: compliance
version: 1.0.0
status: draft
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Structural formatting checks for guideline artifacts — frontmatter, summary, structured guidance, RFC keywords, and change history."
platforms: []
tags:
  - compliance
  - artifact-formatting
  - guideline
depends-on:
  - agentic-cookbook://introduction/conventions
related:
  - agentic-cookbook://compliance/artifact-formatting/principle-formatting
  - agentic-cookbook://compliance/artifact-formatting/recipe-formatting
references: []
---

# Guideline Formatting Compliance

Guidelines are topic-oriented rules that apply during planning and implementation. They are more detailed than principles but less prescriptive than recipes — structured guidance with clear requirements.

## Applicability

This category applies to any file with `type: guideline` in its frontmatter. All files in `guidelines/` (and its subdirectories) MUST have this type.

## Checks

### gf-frontmatter-complete

All required YAML frontmatter fields MUST be present per `introduction/conventions.md`.

**Applies when:** always.

**Required fields:** id, title, domain, type, version, status, language, created, modified, author, copyright, license, summary, platforms, tags, depends-on, related, references.

**Guidelines:**
- [Conventions](agentic-cookbook://introduction/conventions)

---

### gf-type-field

The `type` field MUST be `guideline`.

**Applies when:** always.

---

### gf-title-heading

The first H1 heading MUST match the frontmatter `title` field exactly.

**Applies when:** always.

---

### gf-summary-statement

A summary statement MUST appear immediately after the H1 heading. This is the guideline's core message — typically 1-3 sentences that a reader can act on without reading further.

**Applies when:** always.

---

### gf-structured-guidance

The guideline MUST include structured guidance in the form of bullet points, tables, subsections, or a combination. Unstructured prose without actionable items is not sufficient.

**Applies when:** always.

---

### gf-rfc-keywords

Requirements within the guideline MUST use RFC 2119 keywords (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY) to indicate obligation levels. Keywords MUST be bold or uppercase when used normatively.

**Applies when:** the guideline contains requirements or rules (not purely informational content).

---

### gf-change-history

The file MUST end with a `## Change History` section containing a table with columns: Version, Date, Author, Summary.

**Applies when:** always.

**Guidelines:**
- [Conventions](agentic-cookbook://introduction/conventions)

---

### gf-compliance-section

The guideline MAY include a `## Compliance` section listing evaluated compliance checks and their status. This is recommended when the guideline is referenced by compliance checks in other categories.

**Applies when:** the guideline is referenced by one or more compliance check definitions.

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-04-04 | Mike Fullerton | Initial creation |
