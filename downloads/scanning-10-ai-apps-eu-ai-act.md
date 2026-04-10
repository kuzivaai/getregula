# I scanned 10 open-source AI apps for EU AI Act compliance. Here's what I found.

The EU AI Act's high-risk obligations take effect in August 2026 — though the [Omnibus simplification proposal](https://digital-strategy.ec.europa.eu/en/library/proposal-regulation-amending-ai-act) (February 2026) may push certain deadlines to December 2027 if adopted. Either way, the regulation is law. It applies to AI systems deployed in or affecting the EU market.

I wanted to know: what does compliance actually look like in real codebases? Not in theory documents. Not in consultancy slide decks. In the code that developers are shipping right now.

So I ran [Regula](https://github.com/kuzivaai/getregula), an open-source static analysis tool for AI Act compliance, against 10 popular open-source AI projects. Combined, these projects have over 218,000 GitHub stars and represent the kinds of tools developers are building with today — coding agents, research assistants, chatbot platforms, LLM gateways.

## The projects

| Project | Stars | What it does | Source files | Findings |
|---|---|---|---|---|
| [Aider](https://github.com/Aider-AI/aider) | 43,117 | AI pair programming in the terminal | 165 | 13 |
| [Claude Engineer](https://github.com/Doriandarko/claude-engineer) | 11,162 | Claude-powered coding agent | 22 | 5 |
| [Open Computer Use](https://github.com/e2b-dev/open-computer-use) | 1,960 | AI desktop automation via sandboxed VMs | 13 | 0 |
| [gptme](https://github.com/gptme/gptme) | 4,266 | Terminal AI agent with local tool access | 645 | 87 |
| [Local Deep Research](https://github.com/LearningCircuit/local-deep-research) | 4,290 | Deep research agent (arXiv, PubMed, web) | 2,448 | 29 |
| [Khoj](https://github.com/khoj-ai/khoj) | 33,983 | Self-hosted AI second brain | 293 | 19 |
| [LiteLLM](https://github.com/BerriAI/litellm) | 42,823 | Unified proxy for 100+ LLM APIs | 4,081 | 210 |
| [LangBot](https://github.com/langbot-app/LangBot) | 15,786 | Bot platform for Discord/Slack/Telegram | 488 | 30 |
| [Kirara AI](https://github.com/lss233/kirara-ai) | 18,676 | Multi-modal chatbot for WeChat/QQ/Telegram | 288 | 24 |
| [ChatGPT-on-WeChat](https://github.com/zhayujie/chatgpt-on-wechat) | 42,946 | AI chatbot for WeChat/Feishu/DingTalk | 216 | 136 |
| **Total** | **218,009** | | **8,659** | **553** |

Scan time for all 10 projects: under 3 seconds combined.

## What Regula checks for

Regula scans source code for patterns that map to specific EU AI Act obligations, OWASP Top 10 for LLMs, and OWASP Agentic Security risks. It classifies findings into tiers: minimal risk (no obligations), limited risk (transparency required), high risk (full compliance regime), prohibited, and cross-cutting categories like agent autonomy and credential exposure.

It does not assess whether a system *is* high-risk — that depends on deployment context, not code alone. What it does is flag code-level patterns that become compliance-relevant if the system is deployed in a regulated context.

## What I found

553 findings across 8,659 source files. The breakdown:

| Category | Findings | % | What it means |
|---|---|---|---|
| Agent autonomy | 313 | 56.6% | AI output flowing to system commands, file writes, or HTTP requests without detected human oversight gates |
| Limited risk | 154 | 27.8% | Chatbot interfaces, synthetic content generation — Article 50 transparency obligations apply |
| AI security | 41 | 7.4% | Unsafe deserialisation, unbounded token generation — maps to OWASP LLM05/LLM10 and Article 15 |
| High risk | 27 | 4.9% | Patterns associated with employment, biometric, or critical infrastructure use cases |
| Credential exposure | 14 | 2.5% | API keys detected in source files — Article 15 cybersecurity relevance |
| Prohibited | 4 | 0.7% | Patterns matching prohibited practices under Article 5 (requires deployment context to confirm) |

### The dominant pattern: agent autonomy (56.6%)

More than half of all findings are agent autonomy patterns — AI output flowing directly to system command execution, file system modification, database queries, or HTTP requests. This is the defining characteristic of the current wave of AI tooling. Developers are building agents that act, not just chat.

Three projects account for most of these: ChatGPT-on-WeChat (127), gptme (84), and LiteLLM (34). The pattern is consistent: LLM output is passed to `subprocess`, `os.system`, file write operations, or HTTP clients without a human confirmation step in the code path.

Under the EU AI Act, this matters if the system is classified as high-risk (Article 14 requires human oversight mechanisms). Under OWASP Agentic Security, it maps to ASI02 (Tool Misuse) and ASI04 (Missing Guardrails) regardless of risk classification.

Some projects handle this well. Aider, for example, has human confirmation prompts before executing commands — Regula detected the gate pattern and adjusted its confidence score accordingly. Open Computer Use runs everything inside sandboxed VMs, which is a different form of containment that Regula doesn't currently evaluate as a mitigating control (noted for future improvement).

### Limited risk is straightforward (27.8%)

154 findings relate to chatbot interfaces and synthetic content generation. Under Article 50, these systems must disclose to users that they are interacting with AI or viewing AI-generated content. This is the easiest obligation to meet — a disclosure notice in the UI. Most of these projects already do this implicitly (the user knows they're talking to an AI), but the Act requires explicit disclosure.

LiteLLM accounts for 130 of these — expected for a proxy that routes to 100+ LLM providers, many of which generate text presented to end users.

### AI security: the unsexy but important one (7.4%)

41 findings for unsafe model deserialisation (pickle/joblib loading without integrity checks), unbounded token generation, and similar patterns. These map to OWASP LLM05 (insecure output handling) and LLM10 (unbounded consumption), and become compliance-relevant under Article 15's cybersecurity requirements.

Local Deep Research had 20 of these — primarily related to model loading from external sources without hash verification.

### High risk and prohibited: context-dependent (5.6% combined)

27 high-risk and 4 prohibited findings. These are patterns that *could* indicate use in high-risk contexts (employment decisions, biometric processing, critical infrastructure) or prohibited practices (social scoring, real-time biometric identification). Whether they actually trigger these classifications depends entirely on deployment context, not the code itself.

LiteLLM had 16 high-risk and all 4 prohibited findings. As a universal LLM proxy, it can be used in virtually any context — so these findings reflect the breadth of its potential deployment, not inherent risk in the code.

## What this means for developers building with AI

**Most AI code carries no specific regulatory risk.** 553 findings across 8,659 files means 93.6% of source files had no compliance-relevant patterns. The EU AI Act's minimal-risk category — which carries zero mandatory obligations — covers the vast majority of AI code.

**Agent autonomy is the pattern to watch.** If you're building agents that execute actions based on LLM output, you should be thinking about human oversight mechanisms now. Not because of regulatory panic — because it's good engineering. An agent that can execute arbitrary system commands based on LLM output is a security risk regardless of what the EU AI Act says.

**Transparency obligations are easy to meet.** If your application presents AI-generated content to users or operates as a chatbot, Article 50 requires disclosure. This is a UI change, not an architecture change.

**The Omnibus may simplify things further.** The European Commission's February 2026 simplification proposal would narrow the scope of high-risk classification and raise SME exemption thresholds. As of writing, it's a proposal under legislative review — not enacted. The original August 2026 timeline remains the legal baseline.

## How to run this yourself

```bash
pip install regula-ai
regula check /path/to/your/project
```

Regula is open-source, has zero dependencies, and runs entirely locally. No data leaves your machine. It takes under a second for most projects.

The 330 risk patterns it checks against are documented in the repository. If you disagree with a classification, you can suppress individual findings with inline comments or contribute pattern improvements upstream.

---

*Scans were run using Regula v1.6.1 against shallow clones of each project's default branch on 10 April 2026. Star counts are as of the same date. Findings reflect code-level patterns, not deployed system risk classifications — the EU AI Act regulates systems as deployed, not code in isolation.*

*The EU AI Act enforcement timeline is subject to change. The Omnibus simplification proposal (February 2026) is under legislative review and has not been enacted. All deadline references in this article reflect current law unless otherwise noted.*
