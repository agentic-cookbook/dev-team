# security — Specialities

- [authentication](authentication.md) — OAuth 2.0/OIDC with PKCE for public clients, system browser for native apps, no 
- [authorization](authorization.md) — Deny by default, server-side enforcement only, least privilege scopes, RBAC, BOL
- [content-security-policy](content-security-policy.md) — default-src 'none' baseline, nonce-based script-src with strict-dynamic, never u
- [cors](cors.md) — Explicit origin allowlist (never reflect Origin), no wildcard with credentials, 
- [dependency-security](dependency-security.md) — Lockfiles committed, CI audit step (npm audit/pip-audit/Dependabot) failing on c
- [input-validation](input-validation.md) — All validation duplicated server-side, allowlists over denylists, validate-sanit
- [privacy-and-data-compliance](privacy-and-data-compliance.md) — 7 compliance checks — data-minimization, consent-before-collection, secure-data-
- [privacy](privacy.md) — Collect only what's needed, prefer on-device processing, opt-in consent for non-
- [secure-storage](secure-storage.md) — Platform secure storage for all tokens/credentials/sensitive data — Keychain (Sw
- [security-compliance](security-compliance.md) — 7 compliance checks — secure-authentication, server-side-authorization, secure-s
- [security-headers-checklist](security-headers-checklist.md) — All 7 required headers on every web response — Strict-Transport-Security, Conten
- [sensitive-data](sensitive-data.md) — Data minimization with explicit DTOs (not raw DB models), PII classification tie
- [token-handling](token-handling.md) — Access token lifetime 5-15min, no PII in JWT claims, refresh token rotation, pla
- [transport-security](transport-security.md) — TLS 1.2 minimum (prefer 1.3), disable TLS 1.0/1.1, HSTS with max-age=31536000 in
- [user-safety-compliance](user-safety-compliance.md) — 6 compliance checks — content-moderation, age-appropriate-content, abuse-prevent
