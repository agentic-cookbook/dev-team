# SEO Domain Redirect Strategy

Research on optimizing SEO when consolidating multiple domains to a primary domain.

## 301 Redirects (Permanent)

- Always use **301 redirects**, not 302. A 301 tells search engines to transfer link equity ("link juice") to the target domain.
- Redirect to the **equivalent page**, not just the homepage: `old-domain.com/about` → `primary.com/about`. This preserves page-level authority and avoids soft 404s.

## Canonical Domain Setup

- Pick one canonical primary domain and redirect all variants to it.
- Choose `www` vs non-`www` and stick with it.
- Use `https` (mandatory for modern SEO).
- Redirect all combinations: `http://www`, `http://non-www`, `https://www` or `https://non-www` → the canonical URL.
- Set `<link rel="canonical">` on the primary domain pointing to itself.

## Implementation Options

### Cloudflare (Recommended)

Add each secondary domain to Cloudflare, then use **Bulk Redirects** or **Page Rules** to 301 everything to the primary domain. No origin server needed for the secondary domains.

Example redirect rule pattern:

```
Source: *secondary-domain.com/*
Target: https://primary.com/${2}
Status: 301
```

### Server-Level

Handle redirects in a reverse proxy (nginx, Caddy) or Cloudflare Worker if traffic hits a server.

## Things to Avoid

- **No meta refresh or JS redirects** — search engines may not pass full equity.
- **No unrelated domain redirects** — redirecting domains with no topical relevance won't help and can look spammy.
- **No redirect chains** (A → B → C) — keep it to one hop.
- **Keep secondary domains registered** — if they lapse, the redirect chain breaks and someone else could squat them.

## Google Search Console

- Add all secondary domains as properties in Google Search Console.
- Use the **Change of Address** tool for any domains that previously had their own indexed content.

## GoDaddy Domain Management

- GoDaddy does **not** have an official CLI tool.
- They offer a REST API (`api.godaddy.com`) for managing domains and DNS records via API key.
- Unofficial community wrappers exist (e.g., `godaddy-dns` on npm) but are not officially supported.
- **Recommended approach:** Transfer DNS management (not domain registration) to Cloudflare by pointing GoDaddy nameservers to Cloudflare. Manage everything via `wrangler` or the Cloudflare dashboard.
