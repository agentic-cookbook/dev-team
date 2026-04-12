# networking-api — Specialities

- [access-patterns-compliance](access-patterns-compliance.md) — 8 compliance checks — api-design-conventions, offline-behavior, retry-with-backo
- [api-design](api-design.md) — REST with consistent URL conventions (lowercase-hyphen, plural nouns, max 2 nest
- [caching](caching.md) — Server controls cache policy via headers; immutable versioned assets use `public
- [error-responses](error-responses.md) — RFC 9457 Problem Details format with `Content-Type: application/problem+json`; r
- [offline-and-connectivity](offline-and-connectivity.md) — Local-first with background sync for offline apps; three patterns in complexity 
- [pagination](pagination.md) — Cursor pagination preferred for most APIs — stable under concurrent mutations, c
- [principle-of-least-astonishment](principle-of-least-astonishment.md) — API and system behavior must match what callers expect; names must deliver exact
- [rate-limiting](rate-limiting.md) — Honor `Retry-After` header on 429 responses; if no `Retry-After`, use exponentia
- [real-time-communication](real-time-communication.md) — Start with SSE for server-push (built-in reconnection, standard HTTP, sufficient
- [retry-and-resilience](retry-and-resilience.md) — Exponential backoff with full jitter (`random(0, min(max_delay, base * 2^attempt
- [timeouts](timeouts.md) — Always set both connection timeout (10s) and read/response timeout (30s); total/
