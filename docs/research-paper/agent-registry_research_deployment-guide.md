# Deployment Guide

## Architecture

- **Client** (Cloudflare Worker `official-agent-registry`): Vite SPA + reverse proxy to backend
- **Server** (Railway): Hono API server + PostgreSQL
- **Domain**: officialagentregistry.com (DNS managed by Cloudflare)

## Deploy Client to Cloudflare

The client is a Cloudflare Worker that serves static assets and proxies `/api/*`, `/auth/*`, `/health` to the Railway backend.

**Automated**: Pushes to `main` that change `client/**` or `shared/**` trigger a GitHub Action (`.github/workflows/deploy-client.yml`).

**Manual CLI deploy**:

```bash
# From repo root
npm run build:client
cd client && npx wrangler deploy
```

This builds `shared` then `client`, and deploys to the `official-agent-registry` worker with custom domains `officialagentregistry.com` and `www.officialagentregistry.com`.

**Requirements**:
- `CLOUDFLARE_API_TOKEN` env var (or `wrangler login`)
- Worker name is set in `client/wrangler.jsonc`

## Deploy Server to Railway

The server auto-deploys when pushing to `main` (Railway watches the git repo).

**Manual CLI deploy**:

```bash
# Link to project (one-time setup)
railway link

# Deploy
railway up
```

**Key env vars on Railway** (update via `railway variables set KEY=VALUE`):

| Variable | Value |
|----------|-------|
| `CLIENT_URL` | `https://officialagentregistry.com` |
| `CORS_ORIGIN` | `https://officialagentregistry.com,http://localhost:5173` |
| `GITHUB_CALLBACK_URL` | `https://officialagentregistry.com/auth/github/callback` |
| `GITHUB_CLIENT_ID` | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App client secret |
| `SESSION_SECRET` | 32+ char secret for JWT signing |
| `DATABASE_URL` | PostgreSQL connection string (set by Railway) |

## GitHub OAuth App

Settings at: https://github.com/settings/developers

- **Homepage URL**: `https://officialagentregistry.com`
- **Authorization callback URL**: `https://officialagentregistry.com/auth/github/callback`
- **Client ID**: `Ov23licG7kkEQpIrqi3G`

## Version Bumping

Every deploy must bump the version:

1. Update `VERSION` file
2. Update `version` in `shared/package.json`, `client/package.json`, `server/package.json`

The client reads `VERSION` at build time via Vite's define.

## DNS (Cloudflare)

Zone ID: `7d54b9a57f7a7a7eb58e1d98803c71e1`

Custom domains are managed by `wrangler deploy` via the `routes` in `client/wrangler.jsonc`. Do not manually add A/AAAA records for the root or www — the worker creates them automatically.

## Troubleshooting

- **SSL 525 error**: Domain has DNS records pointing to a non-existent origin. Delete conflicting A/CNAME records and redeploy the worker.
- **Site not loading after changes**: Flush local DNS cache: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
- **GitHub OAuth redirect_uri mismatch**: Ensure `GITHUB_CALLBACK_URL` on Railway and the callback URL in the GitHub OAuth App both match exactly.
