# Principles

Core engineering principles that guide all cookbook decisions and implementations.

| File | Description |
|------|-------------|
| [meta-principle-optimize-for-change.md](meta-principle-optimize-for-change.md) | Every principle is a strategy for making future change cheaper and safer |
| [simplicity.md](simplicity.md) | Simple means no interleaving of concerns; optimize for simplicity over ease |
| [separation-of-concerns.md](separation-of-concerns.md) | A module should have one reason to change |
| [composition-over-inheritance.md](composition-over-inheritance.md) | Default to composing behaviors from small, focused pieces |
| [dependency-injection.md](dependency-injection.md) | A component should receive its dependencies from the outside |
| [explicit-over-implicit.md](explicit-over-implicit.md) | Hidden behavior, magic, and implicit coupling create bugs that take days to find |
| [fail-fast.md](fail-fast.md) | Invalid state should be detected and surfaced immediately at the point of origin |
| [idempotency.md](idempotency.md) | User actions and system operations should be safe to repeat without duplicate side effects |
| [immutability-by-default.md](immutability-by-default.md) | Default to immutable values; introduce mutability only when profiling demands it |
| [manage-complexity-through-boundaries.md](manage-complexity-through-boundaries.md) | Well-defined boundaries between subsystems let each side evolve independently |
| [design-for-deletion.md](design-for-deletion.md) | Every line of code is a maintenance liability; build disposable software |
| [native-controls.md](native-controls.md) | Always use the platform's built-in frameworks before custom implementations |
| [open-source-preference.md](open-source-preference.md) | When no native solution exists, research battle-tested open-source libraries first |
| [principle-of-least-astonishment.md](principle-of-least-astonishment.md) | APIs, UI, and system behavior should match what users and callers expect |
| [small-reversible-decisions.md](small-reversible-decisions.md) | If a decision is cheap to reverse, make it fast |
| [tight-feedback-loops.md](tight-feedback-loops.md) | The speed of your feedback loop is the speed of your learning |
| [make-it-work-make-it-right-make-it-fast.md](make-it-work-make-it-right-make-it-fast.md) | Separate correctness, design quality, and performance into sequential phases |
| [support-automation.md](support-automation.md) | Applications should expose their capabilities through automation interfaces |
| [yagni.md](yagni.md) | Build for today's known requirements, not speculative generality |
