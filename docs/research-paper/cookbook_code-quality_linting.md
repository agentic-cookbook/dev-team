---
id: 775da457-30c7-47de-b179-0fae8a8b779d
title: "Linting from day one"
domain: agentic-cookbook://guidelines/code-quality/linting
type: guideline
version: 1.0.0
status: accepted
language: en
created: 2026-03-27
modified: 2026-03-27
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "All projects MUST include linting configured from initial generation:"
platforms: 
  - csharp
  - kotlin
  - swift
  - typescript
  - web
tags: 
  - code-quality
  - linting
depends-on: []
related: []
references: 
  - https://eslint.org/
  - https://github.com/dotnet/roslynator
  - https://github.com/meziantou/Meziantou.Analyzer
  - https://github.com/realm/SwiftLint
  - https://github.com/swiftlang/swift-format
  - https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/style-rules/
  - https://pinterest.github.io/ktlint/
  - https://prettier.io/
  - https://stylelint.io/
approved-by: "approve-artifact v1.0.0"
approved-date: "2026-04-04"
---

# Linting from day one

All projects MUST include linting configured from initial generation:

| Platform | Linter | Formatter |
|----------|--------|-----------|
| Swift | SwiftLint | swift-format |
| Kotlin | ktlint | ktlint |
| TypeScript | ESLint | Prettier |
| C# / .NET | Roslyn Analyzers + .editorconfig | dotnet format |

Linter config MUST be committed. Linting MUST run as part of the build or pre-commit process. Formatting MUST be auto-fixable.

---

# Linting and Formatting

All projects MUST include linting configured from initial generation. Linter config MUST be committed. Linting MUST run as part of the build or pre-commit process. Formatting MUST be auto-fixable.

## Swift

1. [SwiftLint](https://github.com/realm/SwiftLint) with `.swiftlint.yml` at project root. Enable `strict` mode. Add as SPM plugin or Xcode build phase.
2. [swift-format](https://github.com/swiftlang/swift-format) for auto-formatting.

## Kotlin

Use [ktlint](https://pinterest.github.io/ktlint/) for both linting and formatting. Configure via `.editorconfig` at project root. Add as a Gradle plugin (`org.jlleitschuh.gradle.ktlint`).

## TypeScript

1. [ESLint](https://eslint.org/) with `eslint.config.js`. Use `eslint-config-prettier` to avoid conflicts with the formatter.
2. [Prettier](https://prettier.io/) with `.prettierrc` for auto-formatting.
3. [Stylelint](https://stylelint.io/) with `.stylelintrc.json` for CSS linting.
4. Add as `package.json` scripts and pre-commit hooks.

## C#

1. [`.editorconfig`](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/style-rules/) at repo root for all code style rules.
2. Enable Roslyn analyzers in `.csproj`:

```xml
<PropertyGroup>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  <AnalysisLevel>latest-recommended</AnalysisLevel>
</PropertyGroup>
```

3. Use `dotnet format` CLI for auto-fixing.
4. Supplement with [Roslynator](https://github.com/dotnet/roslynator) or [Meziantou.Analyzer](https://github.com/meziantou/Meziantou.Analyzer) for additional rules.

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-03-27 | Mike Fullerton | Initial creation |
