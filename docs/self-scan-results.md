# Regula Self-Scan Results

**Date:** 17 July 2026 (first refreshed 16 July; re-run after the
suppression-rationale fixes landed)
**Version:** 1.7.5 (installed from PyPI)
**Command:** `regula check .` and `regula check . --domain employment`
**Commit:** main, 17 July 2026 (16 Jul scan basis was `497905b`)

This file is a transparency artefact — Regula run against its own
codebase. Reproduce any time with the commands above. If the results
change materially between releases, this file is refreshed with the
new findings and an explanation of what changed.

---

## Summary — default scan (`regula check .`)

| Metric | Value |
|---|---|
| Files scanned | 129 |
| Prohibited findings | 0 |
| Credential findings | 0 |
| High-risk findings (active) | 0 |
| High-risk findings (domain-gated, inactive) | 5 |
| Agent autonomy findings | 0 |
| Limited-risk findings | 0 |
| Suppressed findings (`# regula-ignore`) | 27 |
| BLOCK tier | 0 |
| WARN tier | 0 |
| INFO tier | 0 |

Verdict: **NO AI DETECTED**. When this file was first refreshed on
16 July the scan also warned that 19 suppressions carried no rationale
comment; all 27 now carry one (fixed 17 July 2026 — verify with
`regula check --audit-suppressions`, which reports zero
"NO RATIONALE" rows).

## Summary — employment domain activated (`--domain employment`)

| Metric | Value |
|---|---|
| High-risk findings (active) | 1 |
| BLOCK tier | 1 |

| Tier | Score | File | Category | Assessment |
|---|---|---|---|---|
| BLOCK | — | `scripts/cli.py:764` | Employment and workers management | `cmd_demo` — the `regula demo` launcher refers to the bundled `cv-screening-app` example by name. Engine/demo plumbing, not an employment AI system: the same "a scanner contains its own patterns' vocabulary" class as the `# regula-ignore` sites. Left visible rather than suppressed because a file-wide ignore on the CLI module would be far too broad. |

---

## What changed since the 16 April 2026 scan (v1.7.0)

The April scan reported 1 active WARN (`examples/cv-screening-app/`)
and 1 active INFO (`examples/customer-chatbot/`) — see this file's own
history at commit `a75d688` (16 April 2026). Both are gone from
the default scan, for two deliberate reasons — not because detection
weakened:

1. **Domain gating shipped** (the April–July precision work,
   15.2% → 85.9% measured precision). High-risk patterns in the
   employment, essential-services, worker-management, and justice
   domains no longer fire unless the project declares that domain
   (`--domain` or `system.domain` in `regula-policy.yaml`). The
   default self-scan therefore reports these as "5 high-risk
   finding(s) suppressed by domain gating" instead of active findings.
   Activating the domain shows detection still works (table above).
2. **`examples/`, `demos/`, and `benchmarks/` joined the canonical
   skip set** (`constants.SKIP_DIRS`) during false-positive tuning, so
   the deliberate fixtures no longer appear in the repo scan at all.
   To see them, scan them directly:
   `regula check examples/cv-screening-app --domain employment`.

Suppression count moved 35 → 27 over the same period (pattern and
skip-set evolution).

---

## Interpretation

- **0 prohibited findings** — Regula does not implement any Article 5
  practice in production code.
- **0 credential exposures** — no hardcoded API keys or secrets.
- **0 BLOCK-tier findings on the default scan** — nothing that would
  fail a CI gate.
- The single domain-activated BLOCK finding is the demo launcher's
  reference to the bundled high-risk example (see assessment above).
- The suppressed count (27) is dominated by the detection engine
  itself — a scanner necessarily contains the patterns it looks for.
  Every suppression carries a same-line rationale
  (`# regula-ignore — <reason>`), auditable with
  `regula check --audit-suppressions`.

---

## How to reproduce

```bash
pipx install regula-ai   # 1.7.5 or newer
git clone https://github.com/kuzivaai/getregula.git
cd getregula
regula check .
regula check . --domain employment
regula check --audit-suppressions
```

Counts drift slightly across minor commits (the suppressed count moves
most often). The stable headline numbers are the prohibited /
credential / BLOCK-tier zeros on the default scan.
