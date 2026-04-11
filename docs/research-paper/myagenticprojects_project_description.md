# MyAgenticProjects

A full-stack SaaS platform with auth, feature flags, messaging, and feedback — deployed across Railway and Cloudflare.

## Purpose

MyAgenticProjects is a production SaaS application bootstrapped from site-manager v1.3.0. It provides a multi-site monorepo architecture with a Hono backend API, PostgreSQL database, and three React+TypeScript frontends. All services are deployed and live. Functions as both a working product and a reference architecture for the Cloudflare + Railway stack.

## Key Features

- Hono backend API with PostgreSQL and Drizzle ORM
- Three React SPA frontends (main site, admin, dashboard)
- GitHub/Google OAuth + email/password authentication with JWT
- Feature flags, messaging, and feedback systems
- Shared TypeScript + Zod schemas across apps
- npm workspaces monorepo

## Tech Stack

- **Backend:** Hono 4.7.0, Node.js 22, TypeScript 5.7, PostgreSQL 16, Drizzle ORM
- **Auth:** JWT (jose), bcrypt, GitHub/Google OAuth
- **Frontend:** React 19, TanStack Router/Query, Tailwind CSS 4, Vite
- **Deployment:** Railway (backend via Docker), Cloudflare Workers (3 frontends via GitHub Actions)
- **Database:** PostgreSQL 16 (Railway) + D1 SQLite (dashboard)
- **Domain:** myagenticprojects.com

## Status

Recently completed / stable — all services deployed and live.

## Related Projects

- [Agentic Auth Service](../../agentic-auth-service/docs/project/description.md) — shared auth microservice
- [Learn True Facts](../../learntruefacts/docs/project/description.md) — similar stack, in planning
