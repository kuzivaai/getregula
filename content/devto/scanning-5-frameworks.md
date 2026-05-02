---
title: "We scanned 5 AI frameworks for EU AI Act compliance. Here's what 389 patterns found."
published: false
description: "469 findings across PyTorch, HuggingFace Transformers, LangChain, LlamaIndex, and CrewAI. The framework you pick shapes your compliance surface before you write a line of code."
tags: euaiact, ai, opensource, python
canonical_url: https://getregula.com/blog/blog-scanning-5-frameworks.html
cover_image: https://getregula.com/assets/og-image.png
---

Your compliance surface doesn't start with the code you write. It starts with the framework you import. We ran [Regula](https://github.com/kuzivaai/getregula) against the source code of PyTorch, HuggingFace Transformers, LangChain, LlamaIndex, and CrewAI -- five frameworks that collectively power most of what gets called "AI" in production today.

## Why scan frameworks, not apps?

Our [previous post](https://getregula.com/blog/blog-scanning-10-ai-apps.html) scanned 10 open-source AI applications and found 553 findings. That told us what developers are building. This post asks a different question: what does the foundation layer look like?

Frameworks don't make deployment decisions. They don't decide whether a chatbot runs in a hospital or a toy shop. But they establish patterns that propagate into every application built on top of them. A model-loading library that uses `pickle` deserialization carries a cybersecurity surface (Article 15) into every project that imports it. An agent framework that pipes LLM output to `subprocess.run` carries a human oversight surface (Article 14) into every agent built with it.

So we scanned them.

## The frameworks

| Framework | Stars | What it does | Source files | Findings |
|---|---|---|---|---|
| [HuggingFace Transformers](https://github.com/huggingface/transformers) | 159,867 | Pre-trained model library (NLP, vision, audio) | 4,255 | 175 |
| [LlamaIndex](https://github.com/run-llama/llama_index) | 48,882 | Data framework for LLM applications | 4,594 | 163 |
| [PyTorch](https://github.com/pytorch/pytorch) | 99,411 | Deep learning framework | 7,010 | -- |
| [CrewAI](https://github.com/crewAIInc/crewAI) | 49,778 | Multi-agent orchestration framework | 1,104 | 78 |
| [LangChain](https://github.com/langchain-ai/langchain) | 134,779 | LLM application framework | 2,463 | 53 |
| **Total (4 scanned)** | **492,717** | | **19,426** | **469** |

Scanned with [Regula v1.7.0](https://github.com/kuzivaai/getregula) (389 risk patterns across EU AI Act, OWASP LLM Top 10, and OWASP Agentic Security). Under 4 seconds per framework. PyTorch scan was still running at time of publication due to the size of its codebase (7,010 source files); results will be added when available.

## What we found

| Category | Findings | % | What it means |
|---|---|---|---|
| AI security | 251 | 53.5% | Unsafe deserialization, sensitive data in prompts, unbounded generation -- maps to OWASP LLM Top 10 and Article 15 |
| Agent autonomy | 102 | 21.7% | LLM output flowing to system commands, file writes, HTTP calls without human oversight gates |
| Limited risk | 57 | 12.2% | Chatbot interfaces, synthetic content generation -- Article 50 transparency obligations |
| High risk | 42 | 9.0% | Patterns associated with employment, biometric, education, or safety-critical contexts |
| Credential exposure | 17 | 3.6% | API keys or tokens detected in source -- Article 15 cybersecurity relevance |
| Prohibited | 0 | 0% | No prohibited practice patterns found in any framework |

Compare this to the [application-level scan](https://getregula.com/blog/blog-scanning-10-ai-apps.html): when we scanned 10 AI apps, agent autonomy was the top category at 56.6%. In frameworks, AI security dominates at 53.5%. That makes sense. Frameworks handle the plumbing (model loading, data serialization, API wiring). Applications make the deployment decisions.

Zero prohibited findings. Frameworks don't implement social scoring or subliminal manipulation. If you're worried about Article 5, look at what you're building with the framework, not the framework itself.

## Each framework carries a different compliance profile

We didn't expect the differences to be this stark.

### HuggingFace Transformers: cybersecurity surface (65% AI security)

113 of [175 findings](https://github.com/kuzivaai/getregula/tree/main/benchmarks/results/framework_scan_2026_04) are AI security patterns. Transformers loads, saves, and converts models across dozens of formats. That means deserialization code paths and model weight handling, which trigger Article 15's cybersecurity requirements if the system qualifies as high-risk.

It also had 28 high-risk findings, the highest count of any framework. Transformers is used in computer vision, speech recognition, and NLP classification, all of which can land in Annex III high-risk categories depending on how they're deployed.

If you're building on Transformers, your main compliance concern is cybersecurity: verifying model integrity, securing the deserialization pipeline, documenting provenance.

### CrewAI: human oversight surface (72% agent autonomy)

56 of [78 findings](https://github.com/kuzivaai/getregula/tree/main/benchmarks/results/framework_scan_2026_04) are agent autonomy patterns. CrewAI's entire purpose is to let AI agents take actions, and the scan reflects that: LLM output flowing to tool execution, task delegation between agents, autonomous decision loops.

If you deploy a CrewAI-based system in a high-risk context, Article 14 requires that humans can effectively oversee it. Confirmation gates, audit trails, the ability to interrupt agent decisions.

CrewAI provides some of these primitives (human input steps, callbacks). The scan can't tell whether your specific pipeline actually uses them. That's on you.

### LlamaIndex: mixed surface with credential exposure

[163 findings](https://github.com/kuzivaai/getregula/tree/main/benchmarks/results/framework_scan_2026_04), the highest count. 98 are AI security, mostly from its data connectors and document processing pipelines. LlamaIndex connects to dozens of external data sources (databases, APIs, file systems, cloud storage), and each connection point is an attack surface.

The 16 credential exposure findings are the interesting ones. LlamaIndex's integration layer handles API keys for vector databases, LLM providers, and data sources. Some of these appear in example code and test fixtures. Developers copy-paste examples. If the example has something that looks like a real API key, it ends up in production.

28 agent autonomy findings come from its query engine and agent capabilities, which route user queries to retrieval and generation pipelines.

### LangChain: relatively clean for its size

53 findings across 2,463 source files. Surprisingly low for a project with 134K stars. LangChain's monorepo splits functionality into small packages (`langchain-core`, `langchain-community`, etc.), so patterns don't concentrate in one place.

Top indicators: sensitive information disclosure (18) and system command execution (9). The agent patterns exist (LangChain has tool-calling and agent execution) but they're spread across packages rather than concentrated in a single orchestration layer.

## What this means for teams choosing frameworks

Your compliance surface is partly inherited. Choosing CrewAI for your agent pipeline means inheriting a human oversight obligation. Choosing Transformers for model serving means inheriting a cybersecurity obligation. These aren't bad things. They're the baseline engineering requirements for that type of work. But you should know about them before you start building.

The framework-level story is AI security, not agent autonomy. When we scanned applications, agent autonomy dominated. When we scanned frameworks, AI security dominated. Frameworks create the security surface. Applications create the oversight surface. Different conversations, different teams.

Article 5 is an application-layer concern. No framework ships social scoring or subliminal manipulation. If you're evaluating prohibited-practice risk, you're evaluating what you build, not what you build with.

One thing we didn't expect: credential exposure in example code. LlamaIndex's 16 credential findings are mostly in examples and templates. Developers copy-paste examples. Framework maintainers should treat example code with the same security discipline as library code.

## Why 389 patterns matter

Some scanning tools run 39 checks. Regula runs 389 patterns across 52 risk categories, covering the EU AI Act (Articles 5, 9-15, 50, 51-55), OWASP LLM Top 10, OWASP Agentic Security, and 18 credential patterns. The difference shows up most in the AI security category, where deserialization risks and prompt injection surfaces need specific regex matchers to avoid false positives.

At 39 checks, a model-loading framework looks clean. At 389, you can see the cybersecurity surface that Article 15 actually cares about.

## Run this yourself

```bash
pip install regula-ai
git clone --depth 1 https://github.com/langchain-ai/langchain.git
regula check langchain
```

Regula is open-source, zero-dependency, and runs locally. No data leaves your machine. The full scan JSON for each framework in this post is available in the [repository](https://github.com/kuzivaai/getregula/tree/main/benchmarks/results/framework_scan_2026_04) for independent verification.

*Scans were run using Regula v1.7.0 against shallow clones of each framework's default branch on 25 April 2026. Star counts are as of the same date. Source file counts include Python, JavaScript, TypeScript, C/C++, and Jupyter notebooks. Findings reflect code-level patterns, not deployed system risk classifications -- the EU AI Act regulates systems as deployed, not code in isolation.*

*PyTorch results pending at time of publication due to scan duration on a 7,010-file codebase. Totals will be updated when available.*

*The EU AI Act enforcement timeline is subject to change. The [Omnibus simplification proposal](https://digital-strategy.ec.europa.eu/en/library/proposal-regulation-amending-ai-act) (February 2026) may push certain Annex III deadlines from August 2026 to December 2027 if adopted. It has not been enacted. All deadline references in this article reflect current law unless otherwise noted.*

---

*Originally published at [getregula.com](https://getregula.com/blog/blog-scanning-5-frameworks.html)*
