# Regula Self-Scan Results

**Date:** 16 April 2026
**Version:** 1.7.0
**Command:** `regula check .`
**Commit:** `d47bccd` (main)

This file is a transparency artefact — Regula run against its own
codebase. Reproduce any time with the command above. If the results
change materially between releases, this file is refreshed with the
new findings and an explanation of what changed.

---

## Summary

| Metric | Value |
|---|---|
| Files scanned | 97 |
| Prohibited findings | 0 |
| Credential findings | 0 |
| High-risk findings | 1 |
| Agent autonomy findings | 0 |
| Limited-risk findings | 1 |
| Suppressed findings | 35 |
| BLOCK tier | 0 |
| WARN tier | 1 |
| INFO tier | 1 |

---

## Findings

### High-risk indicators

| Tier | Score | File | Category | Detail |
|---|---|---|---|---|
| WARN | 68 | `examples/cv-screening-app/app.py` | Employment and workers management | Add human oversight before automated hiring/employment decisions |

**Assessment:** The only WARN-tier finding is in a deliberately
high-risk example fixture (`examples/cv-screening-app/`). The fixture
is designed to trigger this pattern so the repo can demonstrate
Regula's high-risk detection on a runnable project. It is not
production code.

### Limited-risk (Article 50)

| Tier | Score | File | Category |
|---|---|---|---|
| INFO | 45 | `examples/customer-chatbot/app.py:1` | Chatbots and conversational AI |

**Assessment:** Another intentional fixture — `examples/customer-chatbot/`
is the Article 50 transparency-obligation example.

### Suppressed findings

35 findings are suppressed via `# regula-ignore` comments. These cover:

- The detection engine itself (files that must contain the patterns
  they scan for — `scripts/classify_risk.py`, `scripts/credential_check.py`,
  `scripts/ai_code_governance.py`).
- Documentation-as-code that names Article 5 prohibited practices
  (`scripts/explain_articles.py` explains Article 5 vocabulary).
- Test helpers that construct synthetic credentials for hook testing
  (via char-code construction; see CLAUDE.md "Hook Awareness").

---

## Interpretation

Regula scanning its own codebase produces:

- **0 prohibited findings** — Regula does not implement any Article 5
  practice in production code.
- **0 credential exposures** — no hardcoded API keys or secrets.
- **0 BLOCK-tier findings** — nothing that would fail a CI gate.
- **1 WARN-tier finding** — the deliberate `cv-screening-app` example.
- **1 INFO-tier finding** — the deliberate `customer-chatbot` example.

Both active findings are **intentional test fixtures** included so
users can run `regula check examples/cv-screening-app` and
`regula check examples/customer-chatbot` and see representative
output for each risk tier.

The suppressed count (35) is dominated by the detection engine itself
— a Regula-style scanner necessarily contains the patterns it looks
for. Those sites use `# regula-ignore` so the engine does not flag its
own source.

---

## How to reproduce

```bash
git clone https://github.com/kuzivaai/getregula.git
cd getregula
regula check .
```

Output should match the counts above to within ±1 finding across
minor commits. The suppressed count shifts most often (as patterns
evolve); the BLOCK/WARN totals are the stable headline numbers.
