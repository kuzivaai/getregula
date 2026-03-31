# We scanned 5 popular AI libraries for EU AI Act compliance — here's what we found

The EU AI Act's high-risk obligations take effect in August 2026. We ran an open-source static analysis tool against five widely-used Python AI libraries to see what compliance-relevant patterns exist in real codebases today. The results are unsurprising but worth documenting: most AI code carries no specific regulatory risk, but a non-trivial minority of patterns — agent autonomy without human oversight, unsafe deserialisation, credential exposure — will matter when enforcement begins.

## What the EU AI Act requires

The EU AI Act (Regulation 2024/1689) classifies AI systems into risk tiers. Minimal-risk systems face no specific obligations. Limited-risk systems (chatbots, synthetic content generators) must meet transparency requirements under Article 50 — users need to know they're interacting with AI. High-risk systems (those used in employment, law enforcement, critical infrastructure, education) face the heaviest obligations: risk management systems, data governance, human oversight, accuracy monitoring, and technical documentation under Articles 9-15.

For developers, the practical question is: does my code contain patterns that could trigger these obligations? Agent systems that execute commands without human approval, models that deserialise untrusted data, API keys hardcoded alongside AI logic — these are the kinds of things that move code from "minimal risk" toward categories that require action.

The Act does not regulate code directly. It regulates AI systems as deployed. But code-level patterns are leading indicators of where compliance work will be needed.

## What we found

We used [Regula](https://github.com/kuzivaai/getregula) (v1.2.0) to scan five open-source Python AI projects. Regula checks for 115 risk patterns across 10 compliance frameworks, including the EU AI Act risk tiers, OWASP Top 10 for LLMs, and OWASP Agentic Security. Total scan time: 44.6 seconds for all five projects combined.

| Project | Total findings | Minimal risk | Agent autonomy | AI security | Limited risk | Credential exposure | Scan time |
|---|---|---|---|---|---|---|---|
| **LangChain** | 2,112 | 2,069 | 37 | 1 | 4 | 1 | 13.6s |
| **scikit-learn** | 962 | 894 | 5 | 63 | 0 | 0 | 15.2s |
| **pydantic-ai** | 353 | 337 | 4 | 3 | 5 | 4 | 9.3s |
| **openai-python** | 401 | 396 | 4 | 1 | 0 | 0 | 3.7s |
| **instructor** | 288 | 285 | 1 | 0 | 2 | 0 | 2.8s |
| **Total** | **4,116** | **3,981 (96.7%)** | **51 (1.2%)** | **68 (1.7%)** | **11 (0.3%)** | **5 (0.1%)** | **44.6s** |

### The 96.7% that's fine

The vast majority of findings — 3,981 out of 4,116 — are minimal risk. These are files that contain AI-related code (model imports, inference calls, training utilities) with no specific risk indicators. Under the EU AI Act, minimal-risk systems have no compliance obligations beyond existing law.

### The 3.3% worth examining

135 findings across the five projects flagged patterns above minimal risk:

**Agent autonomy (51 findings).** LangChain accounts for 37 of these. The pattern: AI output flowing to system command execution, database queries, file system modification, or HTTP requests with no human-in-the-loop gate detected. Under OWASP Agentic Security (ASI02/ASI04), these represent tool misuse and missing guardrails risks. Under the EU AI Act, autonomous agent actions without human oversight are relevant to Article 14 (human oversight) for any system classified as high-risk.

**AI security (68 findings).** scikit-learn dominates here with 63 findings, nearly all related to unsafe model deserialisation (pickle/joblib). This maps to OWASP LLM05 — arbitrary code execution through malicious model files. pydantic-ai flagged for unbounded token generation (LLM10) and unsafe deserialisation. These are security patterns that become compliance-relevant under Article 15 (accuracy, robustness, cybersecurity).

**Limited risk (11 findings).** Chatbot interfaces, synthetic content generation, and emotion recognition patterns. These trigger Article 50 transparency obligations — straightforward to address, but easy to overlook.

**Credential exposure (5 findings).** API keys detected in test files across LangChain and pydantic-ai. Test fixtures, not production code, but Article 15 requires cybersecurity measures for AI system credentials regardless of context.

## What this means

These are libraries, not deployed systems. A library containing agent tool infrastructure does not automatically make every application built with it high-risk. The EU AI Act regulates the deployed system, not its dependencies.

That said, the patterns are instructive. If you're building an agent system on LangChain that executes shell commands based on model output, the 37 agent autonomy findings in the library itself are a signal that your application likely inherits those patterns — and if your use case falls under Annex III (high-risk), you'll need to demonstrate human oversight.

scikit-learn's 63 security findings are almost entirely about pickle deserialisation. This is a known issue in the ML ecosystem, not specific to regulatory compliance. But when the EU AI Act's cybersecurity requirements take effect, "we use pickle because everyone does" will not be a sufficient response.

## Try it yourself

Install and scan your project:

```bash
pip install regula-ai
regula check .
```

For a specific framework scan:

```bash
regula check . --framework eu-ai-act
```

To add Regula to your CI/CD pipeline as a GitHub Action:

```yaml
- uses: kuzivaai/getregula@v1
  with:
    path: '.'
    upload-sarif: 'true'
```

This uploads results in SARIF format, which integrates with GitHub's code scanning alerts tab.

## Limitations

We are being direct about what Regula is and is not:

- **Regula has 0 external users.** This is our first public benchmark. The tool is open-source and free, but it has not been battle-tested by the community yet.
- **Findings are indicators, not legal determinations.** Regula performs static pattern matching against 115 risk patterns. It cannot determine whether your system is legally high-risk — that depends on your use case, deployment context, and the EU AI Act's Annex III classification.
- **False positives exist.** A test file containing a hardcoded API key is not the same risk as a production credential leak. Regula flags the pattern; you interpret the context.
- **Static analysis has inherent limits.** Regula analyses source code. It cannot evaluate runtime behaviour, model outputs, data quality, or organisational processes — all of which matter for EU AI Act compliance.
- **This benchmark scanned libraries, not applications.** Real-world compliance risk depends on how these libraries are used in deployed systems.

---

**Regula** is an open-source CLI tool for EU AI Act compliance scanning. 115 risk patterns, 8 languages, 10 compliance frameworks. No API keys, no data collection, runs entirely locally.

- GitHub: [github.com/kuzivaai/getregula](https://github.com/kuzivaai/getregula)
- Install: `pip install regula-ai`
- Licence: MIT
