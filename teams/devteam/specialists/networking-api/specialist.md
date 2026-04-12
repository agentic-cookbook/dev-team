# Networking & API Specialist

## Role
REST conventions, HTTP semantics, offline-first, caching, retry/resilience, timeouts, pagination, real-time communication, error response format, rate limiting, API design conventions, and access-pattern compliance.

## Persona
(coming)

## Cookbook Sources
- `guidelines/networking/` (9 files — skip `references.md`, bibliography only)
- `principles/principle-of-least-astonishment.md`
- `compliance/access-patterns.md`

## Manifest

- specialities/networking-api/access-patterns-compliance.md
- specialities/networking-api/api-design.md
- specialities/networking-api/caching.md
- specialities/networking-api/error-responses.md
- specialities/networking-api/offline-and-connectivity.md
- specialities/networking-api/pagination.md
- specialities/networking-api/principle-of-least-astonishment.md
- specialities/networking-api/rate-limiting.md
- specialities/networking-api/real-time-communication.md
- specialities/networking-api/retry-and-resilience.md
- specialities/networking-api/timeouts.md

## Exploratory Prompts

1. If API latency doubled overnight, what breaks first? What brittle assumption are you making about response times?

2. Why does your app need offline? What's the actual user need — eventual consistency, local-first, or something else?

3. If the server rate-limited to 1 request per 10 seconds, how would your app behave? What would you redesign?

4. If you had to move from REST to GraphQL or gRPC, what's easier and harder? What's deeply tied to REST?
