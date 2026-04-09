---
id: 00000000-0000-0000-0000-000000000002
title: "Test Guideline"
domain: agentic-cookbook://guidelines/testing/test-guideline
type: guideline
version: 1.0.0
status: accepted
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "A test guideline used by the skill test harness to verify lint and approve behavior."
platforms: []
tags:
  - test
depends-on: []
related: []
references: []
approved-by: ""
approved-date: ""
---

# Test Guideline

Every change MUST have tests. Every bug fix MUST include a regression test.

- Unit tests MUST cover all business logic
- Integration tests SHOULD verify component boundaries
- E2E tests MAY be used for critical user journeys only

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-04-04 | Mike Fullerton | Initial creation |
