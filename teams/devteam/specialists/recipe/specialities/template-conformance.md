---
name: template-conformance
description: Validates YAML frontmatter fields, section order, correct types, and semver version in recipe files.
artifact: guidelines/recipe-quality/template-conformance.md
version: 1.0.0
---

## Worker Focus
Ensure valid YAML frontmatter with all required fields (id, title, domain, type, version, status, language, created, modified, author, summary, platforms). Confirm all template sections are present in correct order. Verify correct types: arrays for platforms/tags, semver for version.

## Verify
All frontmatter fields present and correctly typed; all template sections present in order; version is valid semver; no extra top-level sections.
