# MCP Servers for Development

**Date:** 2026-03-29
**Context:** Catalog of MCP servers that enhance the development loop when used with Claude Code. Focuses on actively maintained servers useful for the plan/implement/verify cycle.

---

## How MCP Works with Claude Code

MCP (Model Context Protocol) is an open standard that lets Claude Code connect to external tools and data sources through a unified interface. Servers can be added at three scopes:

- **Local** (default) — private to the current project, stored in `.claude/`
- **Project** — committed to `.mcp.json` in the repo root, shared with team
- **User** — stored in `~/.claude.json`, available across all projects

### Adding a server

```bash
# CLI (stdio transport)
claude mcp add <name> --scope <scope> -- npx -y <package>

# CLI (HTTP/remote transport)
claude mcp add <name> --transport http <url>

# JSON (for .mcp.json or claude_desktop_config.json)
claude mcp add-json <name> '<json>'
```

### .mcp.json format

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@scope/package-name"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

Remote/OAuth servers use a different shape:

```json
{
  "mcpServers": {
    "server-name": {
      "type": "http",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

---

## Official / Reference Servers

These are maintained by the MCP steering group in the [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) repository. They demonstrate MCP features and SDK usage.

| Server | Description | Loop Phase | Runtime |
|--------|-------------|------------|---------|
| **Filesystem** | Secure file operations with configurable access controls | implement | Node.js |
| **Git** | Read, search, and manipulate Git repositories | plan, implement | Node.js |
| **Memory** | Knowledge graph-based persistent memory across sessions | plan | Node.js |
| **Fetch** | Web content fetching and conversion for efficient LLM usage | plan, implement | Node.js |
| **Sequential Thinking** | Dynamic and reflective problem-solving through thought sequences | plan | Node.js |
| **Time** | Time and timezone conversion capabilities | implement | Node.js |
| **Everything** | Reference/test server exercising all MCP features | n/a | Node.js |

**Note:** Twelve previously maintained reference servers (including Brave Search, GitHub, PostgreSQL, SQLite, Google Drive, Puppeteer) were archived in 2025 and moved to [servers-archived](https://github.com/modelcontextprotocol/servers-archived). Most have been superseded by vendor-maintained official servers.

### Filesystem

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    }
  }
}
```

```bash
claude mcp add filesystem -s user -- npx -y @modelcontextprotocol/server-filesystem ~/Documents ~/Projects
```

### Git

```json
{
  "mcpServers": {
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git"]
    }
  }
}
```

### Memory

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": "/path/to/memory.jsonl"
      }
    }
  }
}
```

### Fetch

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    }
  }
}
```

### Sequential Thinking

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## Development Environment

### Database Servers

| Server | Description | Databases | Loop Phase | Source |
|--------|-------------|-----------|------------|--------|
| **PostgreSQL** (archived ref) | Schema introspection and natural language queries | PostgreSQL | implement, verify | [servers-archived](https://github.com/modelcontextprotocol/servers-archived/tree/HEAD/src/postgres) |
| **Supabase** | Full backend access: database, auth, storage, edge functions | PostgreSQL (Supabase) | implement, verify | [supabase-community/supabase-mcp](https://github.com/supabase-community/supabase-mcp) |
| **Neon** | Serverless Postgres management and queries | PostgreSQL (Neon) | implement, verify | [neondatabase/mcp-server-neon](https://github.com/neondatabase/mcp-server-neon) |
| **DBHub** | Zero-dependency multi-database MCP server | PostgreSQL, MySQL, MariaDB, SQL Server, SQLite | implement, verify | [bytebase/dbhub](https://github.com/bytebase/dbhub) |
| **Postgres MCP Pro** | Configurable read/write access with performance analysis | PostgreSQL | implement, verify | [crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp) |
| **Redis** | Natural language interface for data management and search | Redis | implement | [redis/mcp-redis](https://github.com/redis/mcp-redis) |
| **Turso** | Built-in MCP server in Turso CLI for LibSQL databases | SQLite/LibSQL | implement | [tursodatabase/turso](https://github.com/tursodatabase/turso) |
| **Google Toolbox for Databases** | Managed MCP server for Cloud SQL, AlloyDB, Spanner | PostgreSQL, MySQL, SQL Server | implement, verify | [googleapis/genai-toolbox](https://github.com/googleapis/genai-toolbox) |
| **AnyDB** | Zero-config universal database connector | PostgreSQL, MySQL, SQLite, MongoDB, Redis | implement | [officialalexeev/anydb-mcp](https://github.com/officialalexeev/anydb-mcp) |

#### Supabase (remote OAuth -- recommended)

```bash
claude mcp add supabase --transport http https://mcp.supabase.com/mcp
```

Project-scoped: append `?project_ref=<your-ref>` to the URL.

#### Neon

```json
{
  "mcpServers": {
    "neon": {
      "command": "npx",
      "args": ["-y", "@neondatabase/mcp-server-neon"],
      "env": {
        "NEON_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### DBHub

```json
{
  "mcpServers": {
    "dbhub": {
      "command": "npx",
      "args": ["-y", "dbhub"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@host:5432/db"
      }
    }
  }
}
```

### Browser Automation & Testing

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Playwright** (Microsoft) | Browser automation via structured accessibility snapshots; cross-browser E2E testing | verify | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) |
| **Puppeteer** | Chrome/Chromium automation with anti-bot bypass and session persistence | verify | [anthropic servers-archived](https://github.com/modelcontextprotocol/servers-archived) |

#### Playwright

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

Requires Node.js 18+. Uses accessibility trees instead of screenshots -- fast, deterministic, and LLM-friendly.

### Documentation & Search

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Context7** | Fresh, version-specific library docs for 50+ frameworks | plan, implement | [upstash/context7](https://github.com/upstash/context7) |
| **Brave Search** | Web search via Brave Search API (2,000 free queries/month) | plan | [@brave/brave-search-mcp-server](https://www.npmjs.com/package/@brave/brave-search-mcp-server) |
| **Fetch** (reference) | General web content retrieval and markdown conversion | plan | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) |

#### Context7

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

Add `"CONTEXT7_API_KEY"` to `env` for higher rate limits (optional). Tools: `resolve-library-id`, `query-docs`. Supports Next.js, React, Tailwind, Supabase, and many more.

#### Brave Search

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@brave/brave-search-mcp-server"],
      "env": {
        "BRAVE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### API & HTTP Testing

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Apidog** | Bridge API specifications (OpenAPI/Swagger) into AI development workflows | plan, implement | [npm: apidog-mcp-server](https://www.npmjs.com/package/apidog-mcp-server) |
| **Postman** | API collection and environment access from Postman workspaces | plan, implement | [Postman MCP](https://www.postman.com/) |

#### Apidog

```json
{
  "mcpServers": {
    "apidog": {
      "command": "npx",
      "args": ["-y", "apidog-mcp-server@latest", "--oas=https://your-api.com/openapi.json"]
    }
  }
}
```

---

## Source Control & Project Management

### GitHub

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **GitHub** (official) | Repository operations, issues, PRs, code search, Actions | plan, implement, verify | [github/github-mcp-server](https://github.com/github/github-mcp-server) |

#### GitHub (HTTP -- recommended for Claude Code 2.1.1+)

```bash
claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'
```

#### GitHub (Docker -- local)

```bash
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_PAT -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

#### GitHub (binary -- no Docker)

```json
{
  "mcpServers": {
    "github": {
      "command": "github-mcp-server",
      "args": ["stdio"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-pat"
      }
    }
  }
}
```

Supports `--read-only` flag and `X-MCP-Readonly` header for safety.

### GitLab

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **GitLab** (official, beta) | Projects, issues, merge requests, pipelines, commits | plan, implement, verify | [GitLab MCP Docs](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/) |

#### GitLab (HTTP -- recommended)

```json
{
  "mcpServers": {
    "gitlab": {
      "type": "http",
      "url": "https://gitlab.example.com/api/v4/mcp"
    }
  }
}
```

Available to Premium and Ultimate customers. Requires GitLab 18.6+.

### Project Management

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Atlassian** (Jira + Confluence) | Issue management, documentation retrieval, ticket creation | plan, verify | [atlassian/atlassian-mcp-server](https://github.com/atlassian/atlassian-mcp-server) |
| **Linear** | Issues, cycles, project milestones, initiative tracking | plan, verify | [Remote MCP](https://mcp.linear.app/mcp) |
| **Notion** | Workspace search, page retrieval, database queries | plan | [makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server) |

#### Atlassian (Jira + Confluence -- remote OAuth)

```bash
claude mcp add atlassian --transport http https://mcp.atlassian.com/v1/mcp
```

Currently in beta. OAuth 2.1 authentication. Cloud customers only.

#### Linear (remote -- no local install needed)

```bash
claude mcp add linear --transport http https://mcp.linear.app/mcp
```

As of February 2026, supports initiatives, project milestones, and updates.

#### Notion

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "your-integration-token"
      }
    }
  }
}
```

Tools: `notion-search`, `retrieve_page`, `query_database`. Also available as a remote server.

---

## CI/CD & DevOps

### Infrastructure as Code

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Terraform** (HashiCorp) | Registry integration, workspace management, plan/apply | implement, verify | [hashicorp/terraform-mcp-server](https://github.com/hashicorp/terraform-mcp-server) |
| **Pulumi** | Registry queries, infrastructure provisioning via CLI | implement | [Pulumi MCP Blog](https://www.pulumi.com/blog/mcp-server-ai-assistants/) |

#### Terraform (Docker -- recommended)

```json
{
  "mcpServers": {
    "terraform": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "TFE_TOKEN",
        "hashicorp/terraform-mcp-server:0.4.0"
      ],
      "env": {
        "TFE_TOKEN": "your-terraform-token"
      }
    }
  }
}
```

Also available as a Go binary: `go install github.com/hashicorp/terraform-mcp-server/cmd/terraform-mcp-server@latest`. Supports both stdio and StreamableHTTP transports. Local use only (not designed for remote deployment).

### Container Orchestration

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Kubernetes** | Native K8s API interaction: pods, deployments, services, logs | implement, verify | [containers/kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server) |
| **kubectl MCP** | kubectl wrapper for pod diagnostics, rollouts, resource inspection | verify | [rohitg00/kubectl-mcp-server](https://github.com/rohitg00/kubectl-mcp-server) |
| **Argo CD** | GitOps workflow management for Kubernetes deployments | implement, verify | [argoproj-labs/mcp-for-argocd](https://github.com/argoproj-labs/mcp-for-argocd) |

#### Kubernetes

```json
{
  "mcpServers": {
    "kubernetes": {
      "command": "npx",
      "args": ["kubernetes-mcp-server@latest"]
    }
  }
}
```

Available as native binary (Go), npm package, Python package, and Docker image. Mount kubeconfig as read-only for security.

#### kubectl MCP

```bash
npx kubectl-mcp-server
# or
pip install kubectl-mcp-server
```

### GitOps & Deployment Platforms

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Cloudflare** | Manage Workers, KV, R2, and other Cloudflare resources | implement | Cloudflare |
| **Vercel** | Deployment management, project configuration, logs | implement, verify | [Vercel MCP Docs](https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel) |
| **Netlify** | Automated web deployment, serverless function management | implement | [Netlify MCP](https://www.pulsemcp.com/servers/dynamicendpoints-netlify) |

---

## Cloud Providers

### AWS

Amazon provides dozens of specialized MCP servers in the [awslabs/mcp](https://github.com/awslabs/mcp) repository.

| Server | Description | Loop Phase |
|--------|-------------|------------|
| **AWS MCP Server** (start here) | Secure, auditable AWS interactions with CloudTrail logging | implement, verify |
| **AWS Knowledge** | Latest AWS documentation, API references, architectural guidance | plan |
| **AWS Documentation** | Retrieve current AWS docs and API references | plan |
| **AWS IaC** | CloudFormation, CDK best practices, deployment troubleshooting | implement |
| **Amazon EKS** | Kubernetes cluster management on AWS | implement, verify |
| **Amazon ECS** | Container orchestration and deployment | implement |
| **AWS Serverless** | SAM CLI integration, serverless application lifecycle | implement |
| **AWS Lambda Tool** | Execute Lambda functions as AI tools | implement, verify |
| **AWS Support** | Create and manage support cases programmatically | verify |

All AWS servers support stdio transport.

### Google Cloud

Google provides managed MCP endpoints for many services. See [Supported Products](https://docs.cloud.google.com/mcp/supported-products) for the full list.

| Server | Description | Endpoint | Loop Phase |
|--------|-------------|----------|------------|
| **gcloud MCP** | Natural language interaction with gcloud CLI | [googleapis/gcloud-mcp](https://github.com/googleapis/gcloud-mcp) | implement |
| **BigQuery** | Query and manage BigQuery datasets | `bigquery.googleapis.com/mcp` | implement, verify |
| **Cloud Run** | Manage Cloud Run services | `run.googleapis.com/mcp` | implement |
| **Cloud SQL** | Manage Cloud SQL instances and databases | `sqladmin.googleapis.com/mcp` | implement, verify |
| **Cloud Logging** | Query and manage logs | `logging.googleapis.com/mcp` | verify |
| **Cloud Monitoring** | Query metrics and alerting | `monitoring.googleapis.com/mcp` | verify |
| **Compute Engine** | Manage VMs and infrastructure | `compute.googleapis.com/mcp` | implement |
| **GKE** | Manage Google Kubernetes Engine clusters | `container.googleapis.com/mcp` | implement, verify |
| **Firestore** | Document database operations | `firestore.googleapis.com/mcp` | implement |
| **Vertex AI** | ML model management and inference | `aiplatform.googleapis.com/mcp` | implement |
| **Spanner** | Globally distributed database operations | `spanner.googleapis.com/mcp` | implement |

Regional endpoints require replacing `REGION` in the URL (e.g., `alloydb.us-central1.rep.googleapis.com/mcp`). The gcloud MCP server is currently in preview.

#### gcloud MCP

```bash
npx -y @google-cloud/gcloud-mcp
```

### Microsoft Azure

Microsoft maintains MCP servers in the [microsoft/mcp](https://github.com/microsoft/mcp) repository.

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Azure MCP Server** | Unified access to Azure services | implement | [microsoft/mcp](https://github.com/microsoft/mcp) |
| **Azure DevOps** | Work items, repos, pipelines, boards | plan, implement, verify | [microsoft/azure-devops-mcp](https://github.com/microsoft/azure-devops-mcp) |

#### Azure DevOps (remote -- public preview)

```bash
claude mcp add azure-devops --transport http https://mcp.dev.azure.com
```

The Azure MCP Server is also integrated directly into Visual Studio 2026.

---

## Monitoring & Observability

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Sentry** | Production error tracking, stack traces, release correlation | verify | [getsentry/sentry-mcp](https://github.com/getsentry/sentry-mcp) |
| **Datadog** | Live observability data, metrics, dashboards, incident management | verify | [Datadog MCP Docs](https://docs.datadoghq.com/bits_ai/mcp_server/) |
| **Grafana** | Dashboard queries, data source access, alerting, incidents | verify | [grafana/mcp-grafana](https://github.com/grafana/mcp-grafana) |

### Sentry (remote OAuth -- recommended)

```bash
claude mcp add sentry --transport http https://mcp.sentry.dev/mcp
```

### Sentry (stdio -- local)

```json
{
  "mcpServers": {
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "your-auth-token",
        "SENTRY_ORG": "your-org-slug"
      }
    }
  }
}
```

### Grafana

```json
{
  "mcpServers": {
    "grafana": {
      "command": "npx",
      "args": ["-y", "@grafana/mcp-grafana"],
      "env": {
        "GRAFANA_URL": "https://your-grafana.example.com",
        "GRAFANA_SERVICE_ACCOUNT_TOKEN": "your-token"
      }
    }
  }
}
```

Supports `--disable-write` flag for read-only mode. 43+ tools across dashboards, alerts, incidents, and data sources.

### Datadog (remote)

```bash
claude mcp add datadog --transport http https://mcp.datadoghq.com/mcp
```

GA as of March 2026. Provides access to live telemetry, logs, traces, and metrics within established security and governance controls.

---

## Code Quality & Security

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Semgrep** | Multi-language SAST scanning for security vulnerabilities (30+ languages) | verify | [semgrep/mcp](https://github.com/semgrep/mcp) |
| **Snyk** | Dependency, code, container, and IaC vulnerability scanning | verify | [Snyk MCP Docs](https://docs.snyk.io/integrations/snyk-studio-agentic-integrations) |
| **ESLint MCP** | JavaScript/TypeScript linting with 600+ rules | verify | Community |

### Semgrep

The Semgrep plugin for Claude Code bundles the MCP server, hooks, and skills into a single install. It scans every file an agent generates using Semgrep Code, Supply Chain, and Secrets.

Tools: `security_check`, `semgrep_scan`, `semgrep_scan_with_custom_rule`, `get_abstract_syntax_tree`, `semgrep_findings`, `supported_languages`, `semgrep_rule_schema`.

### Snyk

```bash
npx -y snyk@latest mcp configure --tool=claude-cli
```

This single command downloads the latest Snyk CLI, configures the MCP server, and installs security scanning directives into Claude Code's global rules.

Tools: `snyk_sca_scan` (dependency vulnerabilities), `snyk_code_scan` (code security flaws), `snyk_iac_scan` (infrastructure as code), `snyk_container_scan` (container images), `snyk_sbom_scan` (SBOM analysis).

Requires Snyk CLI v1.1298.0+.

---

## Communication & Collaboration

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Slack** | Read channels, post messages, search threads | plan, verify | [@modelcontextprotocol/server-slack](https://www.npmjs.com/package/@modelcontextprotocol/server-slack) |
| **Twilio** | SMS, voice, and communication automation | implement | [Twilio MCP](https://www.twilio.com/en-us/blog/introducing-twilio-alpha-mcp-server) |

### Slack

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-token",
        "SLACK_TEAM_ID": "T00000000",
        "SLACK_CHANNEL_IDS": "C00000000,C11111111"
      }
    }
  }
}
```

---

## Design & Frontend

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Figma** | Direct access to layout data, component structures, design tokens | plan, implement | [Figma MCP Docs](https://developers.figma.com/docs/figma-mcp-server/) |

### Figma (remote -- no install)

```bash
claude mcp add figma --transport http https://mcp.figma.com/mcp
```

Also available as a desktop MCP server via the Figma app for selection-based prompting.

---

## Meta / Utility Servers

| Server | Description | Loop Phase | Source |
|--------|-------------|------------|--------|
| **Claude Code MCP** | Run Claude Code itself as a one-shot MCP server (agent-in-agent) | plan, implement, verify | [steipete/claude-code-mcp](https://github.com/steipete/claude-code-mcp) |
| **Zapier** | Connect to 7,000+ apps via Zapier automation | implement | Zapier |

---

## MCP Server Registries

These directories are where you can discover additional MCP servers beyond what is listed here.

| Registry | URL | Notes |
|----------|-----|-------|
| **Anthropic MCP Registry** | [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) | Official registry, integrated into Claude Code's `claude mcp add` flow |
| **Anthropic API Registry** | `api.anthropic.com/mcp-registry/v0/servers` | Programmatic API for server discovery |
| **PulseMCP** | [pulsemcp.com/servers](https://www.pulsemcp.com/servers) | 13,000+ servers, updated daily |
| **Smithery.ai** | [smithery.ai](https://smithery.ai) | Registry + management platform with built-in install infrastructure |
| **Glama.ai** | [glama.ai/mcp/servers](https://glama.ai/mcp/servers) | Comprehensive registry with hosting platform |
| **MCP Market** | [mcpmarket.com](https://mcpmarket.com) | Categorized directory with skills and tools |
| **Awesome MCP Servers** | [mcpservers.org](https://mcpservers.org) | Community-curated list |
| **Docker MCP Catalog** | [hub.docker.com/mcp](https://hub.docker.com/search?q=mcp) | Docker-packaged MCP servers |

---

## Recommended Starting Set

For a typical full-stack development workflow with Claude Code, these servers cover the core plan/implement/verify loop:

| Purpose | Server | Why |
|---------|--------|-----|
| Source control | **GitHub** | PR reviews, issue triage, cross-repo search |
| Documentation | **Context7** | Fresh library docs without leaving the editor |
| Database | **Supabase** or **DBHub** | Schema introspection, query assistance, migrations |
| Browser testing | **Playwright** | E2E verification via accessibility tree |
| Error tracking | **Sentry** | Production issue diagnosis with stack traces |
| Security | **Snyk** or **Semgrep** | Catch vulnerabilities before they ship |
| Project management | **Linear** or **Atlassian** | Ticket context during planning |
| Observability | **Grafana** or **Datadog** | Live metrics for verification |

---

## SDK Languages

MCP servers can be built using official SDKs in: **TypeScript, Python, Go, Rust, Java, Kotlin, C#, Ruby, PHP, and Swift**. Most servers in this catalog use TypeScript (Node.js) or Go.

---

## Sources

- [MCP Official Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Claude Code MCP Documentation](https://code.claude.com/docs/en/mcp)
- [modelcontextprotocol/servers (GitHub)](https://github.com/modelcontextprotocol/servers)
- [github/github-mcp-server (GitHub)](https://github.com/github/github-mcp-server)
- [Anthropic -- Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)
- [Anthropic -- Donating MCP and establishing the Agentic AI Foundation](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
- [awslabs/mcp (GitHub)](https://github.com/awslabs/mcp)
- [microsoft/mcp (GitHub)](https://github.com/microsoft/mcp)
- [google/mcp (GitHub)](https://github.com/google/mcp)
- [googleapis/gcloud-mcp (GitHub)](https://github.com/googleapis/gcloud-mcp)
- [Google Cloud MCP Supported Products](https://docs.cloud.google.com/mcp/supported-products)
- [hashicorp/terraform-mcp-server (GitHub)](https://github.com/hashicorp/terraform-mcp-server)
- [grafana/mcp-grafana (GitHub)](https://github.com/grafana/mcp-grafana)
- [Datadog MCP Server Docs](https://docs.datadoghq.com/bits_ai/mcp_server/)
- [Snyk Claude Code Guide](https://docs.snyk.io/integrations/snyk-studio-agentic-integrations/quickstart-guides-for-snyk-studio/claude-code-guide)
- [semgrep/mcp (GitHub)](https://github.com/semgrep/mcp)
- [Supabase MCP Docs](https://supabase.com/docs/guides/getting-started/mcp)
- [InfoWorld -- 10 MCP Servers for DevOps](https://www.infoworld.com/article/4096223/10-mcp-servers-for-devops.html)
- [Bannerbear -- 8 Best MCP Servers for Claude Code Developers](https://www.bannerbear.com/blog/8-best-mcp-servers-for-claude-code-developers-in-2026/)
- [PulseMCP Server Directory](https://www.pulsemcp.com/servers)
- [Smithery.ai](https://smithery.ai)
- [Glama.ai MCP Servers](https://glama.ai/mcp/servers)
