# Regula Quickstart for AI Builders

You built an AI-powered app. Maybe with Claude, ChatGPT, Cursor, Lovable, or Bolt. It works. Now what?

If your app is used by anyone in the EU — or you plan to sell it there — the **EU AI Act** applies to you. Violations carry fines up to **EUR 35 million or 7% of global turnover**. The rules for high-risk AI systems take effect **2 August 2026**.

Regula tells you where you stand in 10 seconds.

---

## Step 1: Find Out Your Risk Tier

```bash
pipx install regula-ai
regula check .
```

Regula scans your code and tells you which **risk tier** your AI system falls into:

| Tier | What It Means | Example |
|------|---------------|---------|
| **PROHIBITED** | Banned in the EU. Stop. | Social credit scoring, subliminal manipulation |
| **HIGH-RISK** | Heavy compliance required (Articles 9-15) | CV screening, credit scoring, medical diagnosis |
| **LIMITED-RISK** | Must disclose AI to users (Article 50) | Chatbots, deepfakes, emotion recognition |
| **MINIMAL-RISK** | No mandatory requirements | Spam filters, recommendation engines |

If you built a chatbot — that's limited-risk. If it screens job applications — that's high-risk. If it scores people's social behaviour — that's prohibited.

**Regula detects this from your code patterns.** It doesn't need you to fill in a questionnaire.

---

## Step 2: Understand Why

```bash
regula check --explain .
```

This tells you in plain English:
- Which risk tier and why
- Which EU AI Act articles apply to your system
- What each article actually requires
- Whether you're the **provider** (built it) or **deployer** (using someone else's model)

---

## Step 3: Check What's Missing

```bash
regula gap .
```

If you're high-risk, Articles 9-15 apply. This command scores you on each one:

| Article | Requirement | What Regula Checks |
|---------|-------------|-------------------|
| Art. 9 | Risk management system | Error handling, risk documentation |
| Art. 10 | Data governance | Training data documentation, bias checks |
| Art. 11 | Technical documentation | Whether docs exist and cover required areas |
| Art. 12 | Record-keeping (logging) | Whether your AI calls are logged |
| Art. 13 | Transparency to deployers | Whether capabilities/limitations are documented |
| Art. 14 | Human oversight | Whether humans can review/override AI outputs |
| Art. 15 | Accuracy and cybersecurity | Input validation, dependency security, testing |

You can also check against other frameworks:
```bash
regula gap . --framework cra            # EU Cyber Resilience Act
regula gap . --framework nist-ai-rmf    # NIST AI Risk Management
regula gap . --framework iso-42001      # ISO/IEC 42001
```

---

## Step 4: Generate Documentation

```bash
regula docs .
```

The EU AI Act requires technical documentation (Annex IV). This generates a skeleton with everything Regula can auto-detect — AI libraries, model references, function signatures, risk classification. You fill in the rest.

---

## Step 5: Get a Fix Plan

```bash
regula plan .
```

Returns a prioritised list of tasks: what to fix first, estimated effort, which article each task addresses. Start with the highest-priority items.

---

## Step 6: Package Evidence

```bash
regula evidence-pack .
```

Bundles your scan results, gap assessment, documentation, and audit trail into a .zip file. Hand this to your compliance officer, lawyer, or auditor.

---

## Common Scenarios

### "I built a chatbot with the OpenAI API"
- Risk tier: **LIMITED-RISK** (Article 50)
- What you need: Tell users they're talking to AI. That's it.
- Run: `regula check .` to confirm, `regula disclose .` for disclosure text

### "I built a CV screening tool for recruiters"
- Risk tier: **HIGH-RISK** (Annex III, Category 4 — Employment)
- What you need: Full Articles 9-15 compliance, conformity assessment
- Run: `regula check .` → `regula gap .` → `regula plan .` → `regula docs .`

### "I built a recommendation engine for an online shop"
- Risk tier: **MINIMAL-RISK**
- What you need: Nothing mandatory. Optional: transparency is good practice.
- Run: `regula check .` to confirm you're in the clear

### "I fine-tuned an open-source model"
- Risk tier: Depends on use case + whether you're distributing the model
- GPAI obligations may apply if training compute exceeds thresholds
- Run: `regula check .` — Regula detects training patterns and flags GPAI obligations

---

## What Regula Does Not Do

- **Does not catch general security bugs** (XSS, SQL injection). Use Bandit, Semgrep, or Snyk for that.
- **Does not assess code quality or architecture.** It checks regulatory risk patterns, not whether your code is well-structured.
- **Does not check EU Cyber Resilience Act obligations** beyond the overlap with AI Act Article 15. Use `regula gap . --framework cra` to see where CRA and AI Act intersect, but CRA-specific requirements (SBOM, 5-year update obligation, 24-hour vulnerability reporting) are not fully covered.
- **Does not make you compliant.** It tells you where you stand. Compliance requires human judgement, legal review, and organisational measures that no tool can automate.

Findings are indicators for human review, not legal determinations.

---

## Install

```bash
pipx install regula-ai    # PyPI
regula check .           # scan current directory
regula self-test         # verify installation
regula doctor            # check dependencies
```

Zero dependencies for core features. Optional: `pyyaml` for config, `tree-sitter` for JS/TS AST analysis.
