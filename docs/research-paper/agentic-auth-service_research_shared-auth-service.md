# Shared Auth Service Research

Date: 2026-04-06
Status: Deployed (v1)

## What It Is

A standalone RS256 JWT authentication service shared by all agentic projects. Every site in the ecosystem delegates auth to this single service rather than implementing its own user management.

- **Repo:** [agentic-cookbook/agentic-auth-service](https://github.com/agentic-cookbook/agentic-auth-service)
- **Local:** `~/projects/active/agentic-auth-service`
- **Deployed:** `https://backend-production-9b1f.up.railway.app`
- **Admin:** admin@myagenticprojects.com

## Why a Shared Service

When you have multiple sites (main + admin + dashboard) under one project, and multiple projects under one ecosystem, auth gets messy fast:

- **Per-site auth** means N user tables, N login flows, N password resets — users create separate accounts for each site
- **Shared database** couples unrelated services at the data layer and makes independent deploys impossible
- **Asymmetric JWT** solves it: one service holds the private key and issues tokens, every other site validates tokens locally with the public key — zero network calls to the auth service at request time

## Architecture

```
                         ┌──────────────────────┐
                         │   agentic-auth-service│
                         │   (Railway + Postgres)│
                         │                       │
     login/register ───▶ │  POST /api/auth/*     │ ──▶ issues JWT (RS256)
                         │  GET  /.well-known/    │ ──▶ serves public key
                         │        jwks.json       │
                         └──────────────────────┘
                                    │
                          public key distributed
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
        ┌──────────┐         ┌──────────┐         ┌──────────┐
        │  Site A   │         │  Site B   │         │  Site C   │
        │ (Worker)  │         │ (Worker)  │         │ (Worker)  │
        │           │         │           │         │           │
        │ validates │         │ validates │         │ validates │
        │ JWT locally│        │ JWT locally│        │ JWT locally│
        └──────────┘         └──────────┘         └──────────┘
```

### Key Design Decisions

**RS256 (asymmetric) over HS256 (symmetric):** With HS256, every service that validates tokens needs the shared secret — any compromised service can forge tokens for all others. RS256 means only the auth service has the private key; sites only need the public key, which is safe to distribute.

**Refresh token rotation:** Each `/api/auth/refresh` call revokes the old refresh token and issues a new one. If a refresh token is stolen and used, the legitimate user's next refresh fails — a detectable signal.

**Stateless validation:** Sites never call back to the auth service to validate a request. They fetch the public key once (from JWKS or a local `.pem` file) and verify JWTs locally. The auth service can go down without breaking authenticated sessions.

**JWKS endpoint:** `/.well-known/jwks.json` serves the public key in JWK format with a 1-hour cache header. Sites can auto-discover keys by `kid` (currently `auth-service-1`), which enables key rotation without redeploying every site.

## Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Node.js (Hono framework) |
| Database | PostgreSQL on Railway |
| ORM | Drizzle |
| JWT | `jose` library (RS256) |
| Passwords | `bcrypt` (min 12 chars) |
| Deploy | Railway (Dockerfile build) |
| Healthcheck | `GET /api/health` |

## API Surface

### Public routes (no auth required)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/auth/register` | Create account, returns access + refresh tokens |
| `POST` | `/api/auth/login` | Authenticate, returns access + refresh tokens |
| `POST` | `/api/auth/refresh` | Exchange refresh token for new pair (rotation) |
| `GET` | `/.well-known/jwks.json` | Public key in JWK format (cached 1h) |
| `GET` | `/api/health` | Health check (`{ status: "ok" }`) |

### Authenticated routes (Bearer token required)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/auth/logout` | Revoke refresh token |
| `GET` | `/api/auth/me` | Current user profile |

### Admin-only routes (admin role required)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/admin/users` | List all users |
| `PATCH` | `/api/admin/users/:id` | Update user role |
| `DELETE` | `/api/admin/users/:id` | Delete user (revokes all tokens) |

### Error format

All errors use RFC 7807 problem detail:
```json
{ "type": "about:blank", "title": "Unauthorized", "status": 401, "detail": "Invalid credentials" }
```

## Token Details

| Property | Access Token | Refresh Token |
|----------|-------------|---------------|
| Algorithm | RS256 | N/A (opaque) |
| Expiry | 4 hours | 30 days |
| Key ID | `auth-service-1` | — |
| Issuer | `agentic-auth-service` | — |
| Storage | In-memory (client) | SHA-256 hash in Postgres |
| Contains | `sub` (user ID), `email`, `role` | — |

## Database Schema

Two tables:

**users**
- `id` (UUID, PK)
- `email` (unique, not null)
- `password_hash` (bcrypt)
- `role` ("admin" \| "user", default "user")
- `created_at`, `updated_at`

**refresh_tokens**
- `id` (UUID, PK)
- `user_id` (FK → users, cascade delete)
- `token_hash` (SHA-256 of the opaque token)
- `expires_at`
- `created_at`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Postgres connection string |
| `JWT_PRIVATE_KEY` | Yes | PEM-encoded RS256 private key |
| `JWT_PUBLIC_KEY` | Yes | PEM-encoded RS256 public key |
| `PORT` | No | Server port (default: 3000) |
| `CORS_ORIGIN` | No | Allowed origins, comma-separated (default: `*`) |

## How Sites Integrate

A consuming site needs to:

1. **Get the public key** — either embed `.site/jwt-public.pem` at build time, or fetch from `/.well-known/jwks.json` at startup
2. **Verify tokens** — on each request, extract `Authorization: Bearer <token>`, verify with the public key, check `iss` is `agentic-auth-service`
3. **Extract claims** — `sub` is the user ID, `role` determines permissions

No SDK or library needed — any JWT library that supports RS256 works. The auth service is language-agnostic.

## Operational Notes

- **Seeding:** `npm run db:seed` creates the admin user (standalone script, only needs `DATABASE_URL`)
- **Migrations:** `npm run db:migrate` runs Drizzle migrations (standalone, only needs `DATABASE_URL`)
- **Local dev:** `npm run dev` starts with tsx watch
- **Key rotation:** Add a new key with a new `kid`, keep the old key in JWKS until all outstanding tokens expire (4h max)

## Open Questions / Future Work

- **Rate limiting:** No rate limiting on login/register yet — vulnerable to brute force
- **Email verification:** Registration doesn't verify email ownership
- **Password reset:** No forgot-password flow
- **Multi-factor auth:** Not implemented
- **Session management UI:** No way for users to see/revoke their active sessions
- **CORS lockdown:** Currently `*` in production — should be restricted to known site origins
- **Key rotation tooling:** Manual process today, could be automated via site-manager
