---
name: Claude subscription billing constraint
description: User is on $200 Claude Max subscription; cannot use per-token API billing. Affects all LLM tooling choices.
type: user
originSessionId: 1529e1c6-c334-497e-83d0-d341413f38f4
---
User is on the $200/month Claude Max subscription. They cannot afford per-token API billing.

**Implication for tooling:** Anything that requires per-token Anthropic API billing is off the table as a default. Specifically:
- The Claude Agent SDK (`claude_agent_sdk` Python package) — rejected as the default dispatcher for the conductor architecture because it requires API keys.
- `claude -p` subprocess dispatch uses the Max subscription and is the sanctioned path.

**Secondary concern:** User has been hitting weekly usage limits on Max. They are interested in mixing in open-source LLMs for specific tasks (via a future `LocalDispatcher`) and in per-agent model tier selection (`high-reasoning` / `balanced` / `fast-cheap`) to stretch the subscription further.

When suggesting LLM-powered tools, libraries, or architectures: default to subscription-compatible mechanisms; flag per-token billing as a cost to the user.
