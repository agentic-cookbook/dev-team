# Recipe Section Authoring Guide

Brief guidance on what each of the 17 recipe sections should contain, common mistakes, and what makes a good vs bad entry.

## 1. Frontmatter

```yaml
---
version: 1.0.0            # Start at 1.0.0 for new recipes
status: draft              # New recipes start as draft
created: YYYY-MM-DD        # Today's date
last-updated: YYYY-MM-DD   # Same as created for new recipes
author: claude-code        # Or the user's name
copyright: YYYY Mike Fullerton
platforms: [...]           # Only list platforms this recipe targets
tags: [...]                # 2-5 freeform labels for discoverability
dependencies: []           # Other recipes this one depends on
---
```

**Common mistake**: Listing all platforms when the recipe only applies to desktop (e.g., window-frame-persistence is macOS only).

## 2. Overview

One paragraph: what it is, when to use it, why it exists.

**Good**: "A slim, animated bar that slides in at the bottom of a view to indicate a background operation is in progress."
**Bad**: "This is a component for showing things." (too vague)

## 3. Behavioral Requirements

The most important section. Every requirement gets:
- A unique kebab-case name describing the requirement
- An RFC 2119 keyword: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY
- A clear, testable assertion

**Good**: "progress-spinner: The bar MUST display an indeterminate progress spinner (platform-native)."
**Bad**: "looks-nice: The bar should look nice." (untestable, subjective)

**Guidelines**:
- MUST = required for conformance (breaking if missing)
- SHOULD = recommended, deviations need justification
- MAY = optional, implementation can choose
- Each requirement should be independently testable
- Group related requirements with subsection headers

## 4. Appearance

Concrete visual values — not descriptions.

**Good**: "Corner radius: 12pt, Padding: 12v × 24h, Font: system semibold 16pt"
**Bad**: "The button should be rounded and well-padded" (imprecise)

Include ASCII mockups for layouts:
```
┌──────────────────────────────────────┐
│ Sidebar      │ Content               │
│              │                       │
└──────────────┴───────────────────────┘
```

## 5. States

Table with every visual/behavioral state:

| State | Appearance change |
|-------|------------------|
| Default | — |
| Pressed | Background darkens 10% |
| Disabled | Opacity 0.5 |

**Common mistake**: Forgetting loading, error, and empty states.

## 6. Accessibility

Required items:
- Semantic role (button, heading, text field, etc.)
- Label requirements (what screen reader announces)
- Keyboard navigation (Tab, arrow keys, Return/Space)
- Minimum tap target (44×44pt iOS, 48×48dp Android)
- Dynamic Type / font scaling behavior

## 7. Conformance Test Vectors

Concrete input → expected output pairs, linked to requirement names:

| ID | Requirements | Input | Expected |
|----|-------------|-------|----------|
| comp-001 | tap-action | Tap button | Action fires |

**Good**: Specific, reproducible, linked to a requirement
**Bad**: "Test that it works" (not actionable)

## 8. Edge Cases

Boundary conditions the implementation must handle:
- Empty/nil data
- Extremely long text
- RTL languages
- Rapid repeated interaction
- Network unavailable (if applicable)
- Permission denied (if applicable)

## 9. Deep Linking

URL patterns per platform. Skip for recipes that aren't navigable views.

## 10. Localization

Table of string keys with default English values:

| String Key | Default (en) | Context |
|-----------|-------------|---------|
| `component.title` | "Settings" | Window title |

**Common mistake**: Forgetting to localize error messages and accessibility labels.

## 11. Accessibility Options

Which display options affect this component:

| Option | Behavior |
|--------|----------|
| Reduce Motion | Disable animations |
| Increase Contrast | Higher contrast colors |

Only list options that actually change behavior. Don't list every option if most are N/A.

## 12. Feature Flags

Flag keys that gate this component:

| Flag Key | Default | Description |
|----------|---------|-------------|
| `{{app_prefix}}.feature_name` | true | Enables this feature |

## 13. Analytics

Events tracked by this component:

| Event | Properties | When |
|-------|-----------|------|
| `component.viewed` | `{}` | On appear |

## 14. Privacy

- **Data collected**: What data, if any
- **Storage**: Where (on-device only, or transmitted?)
- **Transmission**: Does data leave the device?
- **Retention**: How long is it kept?

Most components collect no data — say so explicitly.

## 15. Logging

Subsystem: `{{bundle_id}}` | Category: `ComponentName`

| Event | Level | Message |
|-------|-------|---------|
| Appeared | debug | `ComponentName: appeared` |

**Rules**:
- Messages must be exact (LLM verifies by grepping log output)
- Use debug level for UI flow events
- Never log PII, even at debug level
- Include `{{placeholder}}` tokens for dynamic values

## 16. Platform Notes

Implementation guidance per platform. Be specific:

**Good**: "SwiftUI: Use `NavigationSplitView` with `.navigationSplitViewStyle(.balanced)`. Register shortcut via `Settings` scene."
**Bad**: "Use the platform's navigation." (not actionable)

Recommend native controls (see cookbook/principles/native-controls.md). Mention specific APIs, frameworks, and patterns.

## 17. Design Decisions

Record every subjective choice made during recipe creation:
- Icon choices
- Layout approach (sidebar vs tabs)
- Animation curves
- Default values that could go either way

Format: decision statement, then why, then "Approved by user" or "Pending approval".

## 18. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | YYYY-MM-DD | Initial recipe |

Update on every version bump with a brief description of what changed.
