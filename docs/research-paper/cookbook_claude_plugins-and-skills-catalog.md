# Claude Code Plugins & Skills Catalog

**Date:** 2026-03-29
**Context:** Catalog of available Claude Code plugins and skills for development workflows.
**How plugins work:** Plugins extend Claude Code with skills, agents, hooks, and MCP servers. Install via `/plugin install <name>@claude-plugins-official` or add community marketplaces with `/plugin marketplace add <owner/repo>`.

---

## Official Plugins (claude-plugins-official)

The official Anthropic marketplace is automatically available in Claude Code. Browse with `/plugin` > Discover tab, or visit [claude.com/plugins](https://claude.com/plugins). Source: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official).

### Code Intelligence (LSP Plugins)

These plugins enable Claude Code's built-in Language Server Protocol support, giving Claude real-time type checking, diagnostics after every edit, jump-to-definition, find-references, and symbol navigation. Each requires the corresponding language server binary installed on your system.

| Plugin | Language | Binary Required | Install |
|--------|----------|-----------------|---------|
| `typescript-lsp` | TypeScript/JavaScript | `typescript-language-server` | `/plugin install typescript-lsp@claude-plugins-official` |
| `pyright-lsp` | Python | `pyright-langserver` | `/plugin install pyright-lsp@claude-plugins-official` |
| `rust-analyzer-lsp` | Rust | `rust-analyzer` | `/plugin install rust-analyzer-lsp@claude-plugins-official` |
| `gopls-lsp` | Go | `gopls` | `/plugin install gopls-lsp@claude-plugins-official` |
| `jdtls-lsp` | Java | `jdtls` | `/plugin install jdtls-lsp@claude-plugins-official` |
| `swift-lsp` | Swift | `sourcekit-lsp` | `/plugin install swift-lsp@claude-plugins-official` |
| `clangd-lsp` | C/C++ | `clangd` | `/plugin install clangd-lsp@claude-plugins-official` |
| `csharp-lsp` | C# | `csharp-ls` | `/plugin install csharp-lsp@claude-plugins-official` |
| `kotlin-lsp` | Kotlin | `kotlin-language-server` | `/plugin install kotlin-lsp@claude-plugins-official` |
| `php-lsp` | PHP | `intelephense` | `/plugin install php-lsp@claude-plugins-official` |
| `lua-lsp` | Lua | `lua-language-server` | `/plugin install lua-lsp@claude-plugins-official` |
| `ruby-lsp` | Ruby | `ruby-lsp` | `/plugin install ruby-lsp@claude-plugins-official` |
| `elixir-ls-lsp` | Elixir | `elixir-ls` | `/plugin install elixir-ls-lsp@claude-plugins-official` |

**Phase:** Implement, Verify. Free/open-source.

### Security & Code Quality

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `security-guidance` | Hook that intercepts file writes and scans for 8 vulnerability categories (injection, XSS, unsafe code evaluation, dangerous deserialization, shell command risks, etc.) before changes are applied. | Verify | `/plugin install security-guidance@claude-plugins-official` |
| `semgrep` | Real-time SAST scanning via Semgrep MCP server. Scans every file an agent generates for security vulnerabilities and guides Claude to write secure code. Bundles MCP server, hooks, and skills. | Verify | `/plugin install semgrep@claude-plugins-official` |
| `aikido` | SAST, secrets detection, and IaC misconfiguration scanning. Auto-identifies changed files, runs scans (up to 50 files), applies remediation, and re-scans up to 3 times until clean. | Verify | `/plugin install aikido@claude-plugins-official` |
| `coderabbit` | AI code review with 40+ static analyzers, AST parsing, security checks. Integrates project guidelines (CLAUDE.md) into reviews automatically. Use `/coderabbit:review`. | Verify | `/plugin install coderabbit@claude-plugins-official` |
| `autofix-bot` | Detects security vulnerabilities, code quality issues, and hardcoded secrets using 5,000+ static analyzers. Scans code and dependencies for CVEs. | Verify | `/plugin install autofix-bot@claude-plugins-official` |
| `optibot` | Catches production-breaking bugs, business logic issues, and security vulnerabilities. Analyzes local changes, compares branches, and reviews patch files with line-specific feedback. | Verify | `/plugin install optibot@claude-plugins-official` |
| `nightvision` | DAST and API discovery platform for finding exploitable vulnerabilities in web applications and APIs. | Verify | `/plugin install nightvision@claude-plugins-official` |
| `opsera-devsecops` | AI-powered architecture analysis, security scanning, compliance auditing, and SQL security. | Verify | `/plugin install opsera-devsecops@claude-plugins-official` |
| `sonatype-guide` | Dependency security intelligence. Evaluates open-source dependencies for known vulnerabilities. | Verify | `/plugin install sonatype-guide@claude-plugins-official` |

**Free/open-source** (security-guidance, semgrep scan is free tier). Aikido, CodeRabbit, Optibot, Autofix-bot, NightVision, Opsera, and Sonatype have free tiers or trials; premium features may require paid accounts.

### Code Review & Quality Workflows

| Plugin | What It Does | Phase | Installs | Install |
|--------|-------------|-------|----------|---------|
| `code-review` | Multi-agent PR code review with confidence-based filtering. Specialized agents analyze code quality, tests, error handling, and type design in parallel. Anthropic-verified. | Verify | 191,903 | `/plugin install code-review@claude-plugins-official` |
| `code-simplifier` | Code clarity agent that simplifies and refines recently modified code while preserving functionality and consistency. Anthropic-verified. | Implement | 159,908 | `/plugin install code-simplifier@claude-plugins-official` |
| `pr-review-toolkit` | Specialized pull request review agents across six domains. | Verify | -- | `/plugin install pr-review-toolkit@claude-plugins-official` |

### Development Workflow & Methodology

| Plugin | What It Does | Phase | Installs | Install |
|--------|-------------|-------|----------|---------|
| `superpowers` | Comprehensive skills framework: TDD (red-green-refactor), systematic debugging (4-phase), Socratic brainstorming, subagent-driven development with code review, skill authoring. By Jesse Vincent. | Plan, Implement, Verify | 294,839 | `/plugin install superpowers@claude-plugins-official` |
| `feature-dev` | Structured 7-phase feature development: discovery, codebase exploration (multiple explorer agents), clarifying questions, architecture design (multiple architect agents), implementation, quality review (3 reviewer agents), summary. Anthropic-verified. | Plan, Implement, Verify | 143,911 | `/plugin install feature-dev@claude-plugins-official` |
| `ralph-loop` | Interactive AI loops for iterative development. Claude works on tasks repeatedly, seeing prior work until completion. Enables autonomous multi-hour coding sessions with context reset between tasks. Anthropic-verified. | Implement | 120,629 | `/plugin install ralph-loop@claude-plugins-official` |
| `commit-commands` | Git workflow commands: commit, push, and PR creation with generated messages. | Implement | -- | `/plugin install commit-commands@claude-plugins-official` |
| `hookify` | Create custom hooks from natural language (e.g., "Warn me when I use dangerous commands"). Auto-generates rules from corrected behaviors. `/hookify:list` and `/hookify:configure` for management. | Implement, Verify | -- | `/plugin install hookify@claude-plugins-official` |
| `claude-code-setup` | Analyzes codebases and recommends Claude Code automations (hooks, rules, CLAUDE.md settings). | Plan | -- | `/plugin install claude-code-setup@claude-plugins-official` |
| `claude-md-management` | Maintains and improves CLAUDE.md files. Audits quality, captures learnings, keeps project memory current. | Plan | -- | `/plugin install claude-md-management@claude-plugins-official` |
| `remember` | Continuous memory across sessions. Extracts, summarizes, and compresses conversations into tiered daily logs. | Plan, Implement | -- | `/plugin install remember@claude-plugins-official` |

### Design & Frontend

| Plugin | What It Does | Phase | Installs | Install |
|--------|-------------|-------|----------|---------|
| `frontend-design` | Generates production-grade frontends with distinctive design. Avoids generic AI aesthetics with intentional typography, spacing, and color. Anthropic-verified. | Implement | 413,623 | `/plugin install frontend-design@claude-plugins-official` |
| `figma` | Reads Figma design files directly. Extracts frames, components, tokens, and layout data for design-to-code translation. | Plan, Implement | -- | `/plugin install figma@claude-plugins-official` |
| `playground` | Creates interactive HTML playgrounds with visual controls, live preview, and prompt output. | Implement | -- | `/plugin install playground@claude-plugins-official` |

### Plugin & Agent Development

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `plugin-dev` | Comprehensive toolkit for building Claude Code plugins. 7 specialized skills covering hooks, MCP integration, plugin structure, settings, commands, agents, and skill authoring. | Implement | `/plugin install plugin-dev@claude-plugins-official` |
| `agent-sdk-dev` | Tools for building applications with the Claude Agent SDK. Scaffolding, patterns, and best practices. | Implement | `/plugin install agent-sdk-dev@claude-plugins-official` |
| `mcp-server-dev` | Design and build MCP servers. Guides creation of high-quality servers for integrating external APIs. | Implement | `/plugin install mcp-server-dev@claude-plugins-official` |
| `skill-creator` | Create, improve, and test Claude Code skills. Includes eval/benchmark tooling. | Implement | `/plugin install skill-creator@claude-plugins-official` |
| `ai-firstify` | AI-first project auditor. Audits and re-engineers projects based on AI-first design principles. 1 skill + 9 reference docs. | Plan | `/plugin install ai-firstify@claude-plugins-official` |

### Source Control & Project Management

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `github` | Official GitHub MCP server. Create issues, manage PRs, review code, search repos, access GitHub API. | Plan, Implement, Verify | `/plugin install github@claude-plugins-official` |
| `gitlab` | GitLab DevOps platform integration. Pipeline management, merge requests, CI/CD. | Plan, Implement, Verify | `/plugin install gitlab@claude-plugins-official` |
| `linear` | Linear issue tracking integration. Pull tickets, update status, manage issues from Claude Code. | Plan, Implement | `/plugin install linear@claude-plugins-official` |
| `atlassian` | Jira and Confluence integration. Issue tracking and knowledge base access. | Plan, Implement | `/plugin install atlassian@claude-plugins-official` |
| `asana` | Asana project management integration. Task and project management. | Plan | `/plugin install asana@claude-plugins-official` |
| `notion` | Notion workspace integration. Access pages, databases, and knowledge bases. | Plan | `/plugin install notion@claude-plugins-official` |

### Testing & Browser Automation

| Plugin | What It Does | Phase | Installs | Install |
|--------|-------------|-------|----------|---------|
| `playwright` | Microsoft's browser automation MCP server. Claude controls Chrome to interact with web pages, take screenshots, fill forms, automate E2E testing. | Verify | 134,578 | `/plugin install playwright@claude-plugins-official` |
| `stagehand` | Browser automation with natural language commands. AI-powered act, extract, observe, and agent methods. By Browserbase. | Verify | -- | `/plugin install stagehand@claude-plugins-official` |
| `chrome-devtools-mcp` | Live Chrome browser control and DevTools inspection. Network requests, console errors, performance analysis on existing sessions. | Verify | -- | `/plugin install chrome-devtools-mcp@claude-plugins-official` |

### Code Search & Navigation

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `context7` | Upstash Context7 MCP server. Injects real, version-specific library documentation into Claude's context from source repos. Reduces hallucinations on rapidly evolving frameworks. | Plan, Implement | `/plugin install context7@claude-plugins-official` |
| `greptile` | AI-powered natural language codebase search. Query repositories to find code, understand dependencies, and explore architecture. Includes automated PR review comments. | Plan, Verify | `/plugin install greptile@claude-plugins-official` |
| `sourcegraph` | Search, navigate, and understand code across all repositories. Semantic search, regex search, commit/diff history, symbol navigation, reference tracing. | Plan | `/plugin install sourcegraph@claude-plugins-official` |
| `serena` | Semantic code analysis MCP server. Symbol-level retrieval and editing across 30+ languages. Find symbols, references, and make precision edits without reading entire files. | Plan, Implement | `/plugin install serena@claude-plugins-official` |

### Deployment & Infrastructure

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `deploy-on-aws` | 5-step AWS deployment: analyze codebase, recommend services, estimate costs, generate IaC (CDK/CloudFormation), deploy with confirmation. 3 MCP servers (awsknowledge, awspricing, awsiac). Open-sourced by AWS. | Implement | `/plugin install deploy-on-aws@claude-plugins-official` |
| `aws-serverless` | AWS serverless application development patterns and tooling. | Implement | `/plugin install aws-serverless@claude-plugins-official` |
| `migration-to-aws` | Cloud migration assessment and planning tools. | Plan | `/plugin install migration-to-aws@claude-plugins-official` |
| `vercel` | Vercel deployment platform integration. Deploy frontends and serverless functions. | Implement | `/plugin install vercel@claude-plugins-official` |
| `railway` | Railway app and database deployment. Container-based deployment. | Implement | `/plugin install railway@claude-plugins-official` |
| `firebase` | Google Firebase backend management. Firestore queries, cloud functions, auth, hosting. | Implement | `/plugin install firebase@claude-plugins-official` |
| `supabase` | Supabase backend services: database, auth, storage, real-time subscriptions, edge functions. | Implement | `/plugin install supabase@claude-plugins-official` |
| `terraform` | Terraform IaC automation. Code generation, module creation, provider development. | Implement | `/plugin install terraform@claude-plugins-official` |
| `netlify-skills` | Netlify platform: serverless functions, edge computing, managed databases, image optimization, forms. | Implement | `/plugin install netlify-skills@claude-plugins-official` |

### Database & Data

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `prisma` | Prisma ORM and PostgreSQL management. Migrations, SQL queries, data interaction. | Implement | `/plugin install prisma@claude-plugins-official` |
| `neon` | Neon PostgreSQL database management. Neon-specific skills and API access via MCP server. | Implement | `/plugin install neon@claude-plugins-official` |
| `planetscale` | PlanetScale MySQL database tools. MCP server + database skills. | Implement | `/plugin install planetscale@claude-plugins-official` |
| `cockroachdb` | CockroachDB cluster management. Requires connection env vars. | Implement | `/plugin install cockroachdb@claude-plugins-official` |
| `pinecone` | Pinecone vector database integration. Semantic search, index management, RAG workflows. | Implement | `/plugin install pinecone@claude-plugins-official` |

### Monitoring & Observability

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `sentry` | Sentry error monitoring. Access error reports, analyze stack traces, search issues, debug production errors. | Verify | `/plugin install sentry@claude-plugins-official` |
| `posthog` | PostHog product analytics. Query analytics, manage feature flags, run A/B tests, track errors, analyze LLM costs. 10+ commands, OAuth support. | Verify | `/plugin install posthog@claude-plugins-official` |
| `pagerduty` | PagerDuty risk scoring and incident correlation. Scores pre-commit diffs against historical incident data. | Verify | `/plugin install pagerduty@claude-plugins-official` |
| `firetiger` | Observability workflows and monitoring integration. | Verify | `/plugin install firetiger@claude-plugins-official` |

### Communication & Collaboration

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `slack` | Slack workspace search and messaging integration. | Plan | `/plugin install slack@claude-plugins-official` |
| `discord` | Discord messaging bridge with access control. | Plan | `/plugin install discord@claude-plugins-official` |
| `telegram` | Telegram messaging bridge. | Plan | `/plugin install telegram@claude-plugins-official` |
| `imessage` | iMessage messaging bridge (macOS only). | Plan | `/plugin install imessage@claude-plugins-official` |
| `intercom` | Intercom customer support integration. | Plan | `/plugin install intercom@claude-plugins-official` |

### API & Integration Tools

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `postman` | Full API lifecycle management. Sync collections, generate client code, discover APIs, run tests, create mocks, publish docs, audit security. | Plan, Implement, Verify | `/plugin install postman@claude-plugins-official` |
| `stripe` | Stripe payment integration. Payment flows, webhook verification, SDK patterns. | Implement | `/plugin install stripe@claude-plugins-official` |
| `zapier` | Connect to 8,000+ apps via Zapier automation. | Implement | `/plugin install zapier@claude-plugins-official` |

### Documentation & Content

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `mintlify` | Documentation site building and management. | Implement | `/plugin install mintlify@claude-plugins-official` |
| `microsoft-docs` | Microsoft Azure and .NET documentation lookup. | Plan | `/plugin install microsoft-docs@claude-plugins-official` |

### Web Scraping & Data Extraction

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `firecrawl` | Web scraping with JS rendering, anti-bot detection, proxy rotation. Converts content to markdown/JSON. | Plan, Implement | `/plugin install firecrawl@claude-plugins-official` |
| `brightdata-plugin` | Web scraping and data extraction from 40+ sites. | Plan | `/plugin install brightdata-plugin@claude-plugins-official` |
| `nimble` | Web data extraction toolkit. | Plan | `/plugin install nimble@claude-plugins-official` |

### AI/ML & Specialized

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `huggingface-skills` | Build and train ML models using Hugging Face. | Implement | `/plugin install huggingface-skills@claude-plugins-official` |
| `atomic-agents` | Atomic Agents framework development for agent-based systems. | Implement | `/plugin install atomic-agents@claude-plugins-official` |
| `goodmem` | GoodMem memory infrastructure for agents. | Implement | `/plugin install goodmem@claude-plugins-official` |
| `fiftyone` | Computer vision dataset building and management. | Implement | `/plugin install fiftyone@claude-plugins-official` |
| `helius` | Solana blockchain development tools. | Implement | `/plugin install helius@claude-plugins-official` |

### Output Styles & Learning

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `explanatory-output-style` | Educational insights about implementation choices. Claude explains the "why" behind code decisions. | Implement | `/plugin install explanatory-output-style@claude-plugins-official` |
| `learning-output-style` | Interactive learning mode for skill building. Turns coding sessions into tutorials. | Implement | `/plugin install learning-output-style@claude-plugins-official` |

### CMS & Website Builders

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `sanity-plugin` | Sanity headless CMS content management. | Implement | `/plugin install sanity-plugin@claude-plugins-official` |
| `wordpress.com` | WordPress site creation and editing. | Implement | `/plugin install wordpress.com@claude-plugins-official` |
| `wix` | Wix site and app development. | Implement | `/plugin install wix@claude-plugins-official` |
| `flint` | AI website builder. | Implement | `/plugin install flint@claude-plugins-official` |
| `cloudinary` | Asset management and media optimization. | Implement | `/plugin install cloudinary@claude-plugins-official` |

### Business & Misc

| Plugin | What It Does | Phase | Install |
|--------|-------------|-------|---------|
| `adspirer-ads-agent` | Cross-platform ad management (Google, Meta, TikTok). | Plan | `/plugin install adspirer-ads-agent@claude-plugins-official` |
| `circleback` | Meeting and email context integration. | Plan | `/plugin install circleback@claude-plugins-official` |
| `legalzoom` | Legal document review and guidance. | Plan | `/plugin install legalzoom@claude-plugins-official` |
| `zoominfo` | B2B contact and company search. | Plan | `/plugin install zoominfo@claude-plugins-official` |
| `postiz` | Social media automation (28+ platforms). | Plan | `/plugin install postiz@claude-plugins-official` |
| `searchfit-seo` | SEO audit and optimization. | Plan | `/plugin install searchfit-seo@claude-plugins-official` |
| `voila-api` | Shipment tracking and logistics. | Plan | `/plugin install voila-api@claude-plugins-official` |
| `rc/revenuecat` | In-app purchase backend management. | Implement | `/plugin install rc/revenuecat@claude-plugins-official` |
| `sumup` | SumUp payment terminal integration. | Implement | `/plugin install sumup@claude-plugins-official` |
| `atlan` | Data catalog and governance platform. | Plan | `/plugin install atlan@claude-plugins-official` |
| `astronomer-data-agents` | Apache Airflow/Astronomer DAG development. | Implement | `/plugin install astronomer-data-agents@claude-plugins-official` |
| `followrabbit` | GCP cost optimization. | Plan | `/plugin install followrabbit@claude-plugins-official` |
| `fakechat` | Localhost web chat testing. | Verify | `/plugin install fakechat@claude-plugins-official` |
| `product-tracking-skills` | Product analytics instrumentation. | Implement | `/plugin install product-tracking-skills@claude-plugins-official` |

---

## Knowledge Work Plugins (anthropics/knowledge-work-plugins)

Anthropic maintains a separate set of plugins for non-developer job functions. These work in both Claude Code and Cowork. Source: [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins).

**Install marketplace:** `/plugin marketplace add anthropics/knowledge-work-plugins`

| Plugin | What It Does | Key Connectors | Install |
|--------|-------------|----------------|---------|
| `productivity` | Tasks, calendars, daily workflows, personal context | Slack, Notion, Asana, Linear, Jira, Monday, ClickUp, Microsoft 365 | `/plugin install productivity@knowledge-work-plugins` |
| `sales` | Prospect research, call prep, pipeline review, outreach drafts, battlecards | Slack, HubSpot, Close, Clay, ZoomInfo, Notion, Fireflies, Microsoft 365 | `/plugin install sales@knowledge-work-plugins` |
| `customer-support` | Ticket triage, response drafting, escalation, knowledge base articles | Slack, Intercom, HubSpot, Guru, Jira, Notion, Microsoft 365 | `/plugin install customer-support@knowledge-work-plugins` |
| `product-management` | Specs, roadmaps, research synthesis, competitor tracking | Slack, Linear, Asana, Monday, ClickUp, Jira, Notion, Figma, Amplitude, Pendo | `/plugin install product-management@knowledge-work-plugins` |
| `marketing` | Content drafting, campaign planning, brand voice enforcement, performance reports | Slack, Canva, Figma, HubSpot, Amplitude, Notion, Ahrefs, Klaviyo | `/plugin install marketing@knowledge-work-plugins` |
| `legal` | Contract review, NDA triage, compliance risk assessment | Slack, Box, Egnyte, Jira, Microsoft 365 | `/plugin install legal@knowledge-work-plugins` |
| `finance` | Journal entries, account reconciliation, financial statements, variance analysis | Snowflake, Databricks, BigQuery, Slack, Microsoft 365 | `/plugin install finance@knowledge-work-plugins` |
| `data` | Dataset querying, SQL writing, analysis, dashboard building | Snowflake, Databricks, BigQuery, Definite, Hex, Amplitude, Jira | `/plugin install data@knowledge-work-plugins` |
| `enterprise-search` | Unified search across email, chat, docs, wikis | Slack, Notion, Guru, Jira, Asana, Microsoft 365 | `/plugin install enterprise-search@knowledge-work-plugins` |
| `bio-research` | Literature search, genomics, target prioritization | PubMed, BioRender, bioRxiv, ClinicalTrials.gov, ChEMBL, Benchling | `/plugin install bio-research@knowledge-work-plugins` |
| `cowork-plugin-management` | Create and customize plugins for your organization | -- | `/plugin install cowork-plugin-management@knowledge-work-plugins` |

All free/open-source (MIT license). Connectors may require paid accounts on the integrated services.

---

## Official Agent Skills (anthropics/skills)

Anthropic publishes agent skills as a separate repository for use in Claude.ai (paid plans), the API, and Claude Code. Source: [anthropics/skills](https://github.com/anthropics/skills).

### Document Skills

Source-available (proprietary license). Available to paid Claude plans.

| Skill | What It Does | Phase |
|-------|-------------|-------|
| `pdf` | Read, extract, fill forms, merge, split, rotate, watermark, convert PDF files. | Implement |
| `docx` | Create, read, edit Word documents with tracked changes and OOXML manipulation. | Implement |
| `pptx` | Create presentations from scratch or templates with HTML-to-PPTX conversion. | Implement |
| `xlsx` | Build financial models with formulas, formatting, charts. Read/edit spreadsheets. | Implement |

**Install (Claude Code):** `/plugin install document-skills@anthropic-agent-skills`

### Creative & Design Skills

| Skill | What It Does | Phase |
|-------|-------------|-------|
| `frontend-design` | Production-grade frontend interfaces with high design quality. | Implement |
| `canvas-design` | Visual art in PNG/PDF using design philosophy. Posters, artwork, static pieces. | Implement |
| `algorithmic-art` | Generative art using p5.js with seeded randomness and interactive parameters. | Implement |
| `theme-factory` | Style artifacts with 10+ preset themes (colors/fonts). Slides, docs, reports, pages. | Implement |
| `brand-guidelines` | Apply Anthropic's brand colors and typography to artifacts. | Implement |
| `slack-gif-creator` | Animated GIFs optimized for Slack with constraints and validation. | Implement |
| `web-artifacts-builder` | Multi-component HTML artifacts using React, Tailwind, shadcn/ui. | Implement |

### Development & Technical Skills

| Skill | What It Does | Phase |
|-------|-------------|-------|
| `claude-api` | Build apps with Claude API and Anthropic SDKs. Patterns and best practices. | Implement |
| `mcp-builder` | Guide for creating MCP servers (Python FastMCP or TypeScript). | Implement |
| `webapp-testing` | Interact with and test local web apps using Playwright. Screenshots, logs, debugging. | Verify |

### Communication Skills

| Skill | What It Does | Phase |
|-------|-------------|-------|
| `internal-comms` | Write internal communications (status reports, leadership updates). | Plan |
| `doc-coauthoring` | Structured workflow for co-authoring documentation, proposals, specs. | Plan, Implement |
| `skill-creator` | Create, modify, improve, and benchmark skills. Performance eval tooling. | Implement |

---

## Community Plugins & Marketplaces

### Build with Claude

A community-curated marketplace with 494+ extensions. Source: [davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude). Website: [buildwithclaude.com](https://buildwithclaude.com).

**Install marketplace:** `/plugin marketplace add davepoon/buildwithclaude`

Notable community plugins hosted here include `frontend-design-pro` and other enhanced versions of official plugins.

### Claude Code Demo Marketplace (anthropics/claude-code)

Example plugins from Anthropic showing what's possible. Source: [anthropics/claude-code/plugins](https://github.com/anthropics/claude-code/tree/main/plugins).

**Install marketplace:** `/plugin marketplace add anthropics/claude-code`

Includes reference implementations like `commit-commands`, `security-guidance`, and `example-plugin` for plugin developers.

### Community GitHub Security Scanner

[harish-garg/security-scanner-plugin](https://github.com/harish-garg/security-scanner-plugin) -- Scans code for vulnerabilities using GitHub's official advisory data. Free/open-source.

### Claude Office Skills

[tfriedel/claude-office-skills](https://github.com/tfriedel/claude-office-skills) -- Office document creation and editing (PPTX, DOCX, XLSX, PDF) with automation support. Community alternative to official document skills. Free/open-source.

### Claude Mem

[thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) -- Automatically captures everything Claude does during sessions, compresses it with AI, and injects relevant context into future sessions. Free/open-source.

---

## Community Skill Collections

### VoltAgent/awesome-agent-skills

1,060+ skills from official dev teams and community. Compatible with Claude Code, Codex, Gemini CLI, Cursor. Source: [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills).

**Notable official vendor skills included:**

| Vendor | Skills | Phase |
|--------|--------|-------|
| Google Labs | Gemini API, Vertex AI, Live API streaming, Workspace CLI (Drive, Sheets, Gmail, Calendar, Docs, Slides) | Implement |
| Vercel Labs | React patterns, Next.js optimization, caching strategies, deployment workflows, React Native performance | Implement |
| Cloudflare | Agent SDK, Durable Objects, MCP servers, performance auditing, Workers infrastructure | Implement |
| Stripe | Payment integration best practices, SDK upgrade guidance | Implement |
| Netlify | Serverless functions, edge computing, managed databases, image optimization, forms | Implement |
| Expo | React Native / Expo development patterns | Implement |
| Trail of Bits | Security analysis and audit patterns | Verify |
| Sentry | Error monitoring and debugging workflows | Verify |
| Hugging Face | ML model training and deployment | Implement |
| Better Auth | Auth implementation, 2FA, email/password, organizations | Implement |
| HashiCorp | Terraform code generation, modules, provider development | Implement |
| Tinybird | Data pipelines and SQL query guidelines | Implement |

Free/open-source.

### alirezarezvani/claude-skills

192+ skills covering engineering, marketing, product, compliance, and advisory. Compatible with Claude Code, Codex, Gemini CLI, Cursor. Source: [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills). Free/open-source.

### levnikolaevich/claude-code-skills

Plugin suite with bundled MCP servers for the full delivery lifecycle: Agile pipeline with multi-model AI review, project bootstrap, documentation generation, codebase audits, performance optimization. Includes hex-line (hash-verified editing), hex-graph (code knowledge graph), and hex-ssh (remote SSH) MCP servers. Source: [levnikolaevich/claude-code-skills](https://github.com/levnikolaevich/claude-code-skills). Free/open-source.

### daymade/claude-code-skills

Professional marketplace with production-ready skills and a built-in skill-reviewer tool for validation. Source: [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills). Free/open-source.

### sickn33/antigravity-awesome-skills

1,326+ skills with installer CLI, bundles, and workflows. Compatible with Claude Code, Cursor, Codex CLI, Gemini CLI, Antigravity. Source: [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills). Free/open-source.

### Awesome Lists (Curated Directories)

| Repository | Focus | Source |
|-----------|-------|--------|
| travisvn/awesome-claude-skills | Curated skills, resources, and tools | [GitHub](https://github.com/travisvn/awesome-claude-skills) |
| ComposioHQ/awesome-claude-skills | Skills, resources, customization tools | [GitHub](https://github.com/ComposioHQ/awesome-claude-skills) |
| hesreallyhim/awesome-claude-code | Skills, hooks, commands, agents, plugins | [GitHub](https://github.com/hesreallyhim/awesome-claude-code) |
| Chat2AnyLLM/awesome-claude-plugins | Marketplaces and plugins directory | [GitHub](https://github.com/Chat2AnyLLM/awesome-claude-plugins) |
| ccplugins/awesome-claude-code-plugins | Commands, subagents, MCP servers, hooks | [GitHub](https://github.com/ccplugins/awesome-claude-code-plugins) |

---

## Plugin Registries & Directories

| Registry | URL | Description |
|----------|-----|-------------|
| Official Anthropic | [claude.com/plugins](https://claude.com/plugins) | Authoritative directory, all official + partner plugins |
| claude-plugins.dev | [claude-plugins.dev](https://claude-plugins.dev/) | Community registry with CLI. 11,989 plugins, 63,065 skills |
| ClaudePluginHub | [claudepluginhub.com](https://www.claudepluginhub.com/) | Community directory with categorization and search |
| Build with Claude | [buildwithclaude.com](https://buildwithclaude.com/) | 494+ extensions with voting and comments |
| Claude Marketplaces | [claudemarketplaces.com](https://claudemarketplaces.com/) | Curated directory of plugins, skills, and MCP servers |
| dotclaude.com | [dotclaude.com/plugins](https://dotclaude.com/plugins) | Plugin documentation and reference |

---

## How to Submit Plugins

- **Official marketplace:** Submit via [claude.ai/settings/plugins/submit](https://claude.ai/settings/plugins/submit) or [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)
- **Own marketplace:** Create a GitHub repo with `.claude-plugin/marketplace.json` and share via `/plugin marketplace add <owner/repo>`
- **Community registries:** Follow submission guidelines on each registry's GitHub repo

---

## Sources

- [Claude Code Plugin Documentation](https://code.claude.com/docs/en/discover-plugins)
- [Official Plugin Marketplace](https://claude.com/plugins)
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- [anthropics/claude-code/plugins](https://github.com/anthropics/claude-code/tree/main/plugins)
- [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)
- [anthropics/skills](https://github.com/anthropics/skills)
- [Plugin Marketplace Guide](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugins Reference](https://code.claude.com/docs/en/plugins-reference)
- [Customize Claude Code with Plugins (Anthropic announcement)](https://www.anthropic.com/news/claude-code-plugins)
- [Pete Gypps: Complete Guide to 36 Official Plugins](https://www.petegypps.uk/blog/claude-code-official-plugin-marketplace-complete-guide-36-plugins-december-2025)
- [Firecrawl: Top 10 Claude Code Plugins 2026](https://www.firecrawl.dev/blog/best-claude-code-plugins)
- [Builder.io: Superpowers Plugin Deep Dive](https://www.builder.io/blog/claude-code-superpowers-plugin)
- [obra/superpowers](https://github.com/obra/superpowers)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [davepoon/buildwithclaude](https://github.com/davepoon/buildwithclaude)
- [claude-plugins.dev](https://claude-plugins.dev/)
- [claudepluginhub.com](https://www.claudepluginhub.com/)
- [claudemarketplaces.com](https://claudemarketplaces.com/)
- [buildwithclaude.com](https://buildwithclaude.com/)
- [AWS Deploy Plugin (open-sourced)](https://claude.com/plugins/deploy-on-aws)
- [Pinecone Plugin](https://www.pinecone.io/blog/pinecone-plugin-for-claude-code/)
- [Neon Plugin Docs](https://neon.com/docs/ai/ai-claude-code-plugin)
- [Semgrep Plugin](https://semgrep.dev/docs/mcp)
- [Aikido Plugin](https://help.aikido.dev/ai-and-dev-tools/aikido-mcp/anthropic-claude-code-mcp)
- [CodeRabbit Plugin](https://docs.coderabbit.ai/cli/claude-code-integration)
- [PostHog Plugin](https://github.com/PostHog/posthog-for-claude)
- [PlanetScale Plugin](https://github.com/planetscale/claude-plugin)
- [CockroachDB Plugin](https://github.com/cockroachdb/claude-plugin)
- [Supabase as Official Connector](https://supabase.com/blog/supabase-is-now-an-official-claude-connector)
