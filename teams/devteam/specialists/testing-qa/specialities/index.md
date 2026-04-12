# testing-qa — Specialities

- [flaky-test-prevention](flaky-test-prevention.md) — No shared mutable state between tests, no execution-order dependencies, no real 
- [mutation-testing](mutation-testing.md) — Run mutation testing before claiming tests are complete; platform tools: mutmut 
- [post-generation-verification](post-generation-verification.md) — Every generated artifact must pass 6 steps — build (all platforms), test (full s
- [properties-of-good-tests](properties-of-good-tests.md) — Tests should be isolated, composable, deterministic, fast, writable, readable, b
- [property-based-testing](property-based-testing.md) — Use for parsers, serializers, data transformers, encoders/decoders, validators —
- [security-testing](security-testing.md) — Run SAST (Semgrep all languages, Bandit for Python, CodeQL for deep analysis), d
- [test-data](test-data.md) — Construct test data per test; avoid large shared fixture files; use builder patt
- [test-doubles](test-doubles.md) — Use Martin Fowler's taxonomy (Dummy/Stub/Spy/Mock/Fake); prefer fakes over mocks
- [test-pyramid](test-pyramid.md) — 80% unit / 15% integration / 5% E2E; unit tests are fast and isolated; integrati
- [testing](testing.md) — Every change needs tests, every bug fix needs a regression test; prioritize unit
- [the-testing-workflow](the-testing-workflow.md) — Complete closed-loop workflow — write implementation, write unit tests (with pro
- [unit-test-patterns](unit-test-patterns.md) — AAA structure (Arrange/Act/Assert), one assertion concept per test, no logic in 
