# Regula self-scan results

**Date:** 27 August 2026

**Version:** 2.0.0 source working tree

**Commands:** `python3 -m scripts.cli check . --no-facts`, `python3 -m scripts.cli check . --no-facts --domain employment`, and `python3 -m scripts.cli check --audit-suppressions`

This is a transparency check of Regula against its own production-scope tree. It tests the scanner’s reporting and self-reference behaviour; it is not an independent security assessment, a validity benchmark, or evidence that every tracked file was analysed.

## Default production-scope scan

| Metric | Observed value |
|---|---:|
| Decision | `insufficient_information` |
| Files scanned | 153 |
| Prohibited findings | 0 |
| Credential findings | 0 |
| Active high-risk findings | 0 |
| Agent-autonomy findings | 0 |
| Limited-risk findings | 0 |
| Domain-gated high-risk findings | 17 |
| Suppressed findings, including domain gating | 29 |
| BLOCK / WARN / INFO | 0 / 0 / 0 |
| Test files excluded from production scope | 137 |
| Code files under pruned directories | 1,008 across `.venv`, `benchmarks`, `examples`, and `scripts/demos` |

The correct reading is **no active detector findings in the selected production scope**. It is not “no AI”, “clean repository”, “minimal risk”, or “compliant”. The decision remains `insufficient_information` because `is_ai_system` and `jurisdiction_in_scope` were deliberately not declared.

## Employment-domain diagnostic

Activating `--domain employment` produced three active self-reference findings:

| File | Display tier | Why it matched |
|---|---|---|
| `scripts/cli.py` | BLOCK | The bundled demo launcher names the tracked CV-screening example. |
| `scripts/cli_analysis.py` | WARN | Questionnaire and analysis code contains employment-decision vocabulary. |
| `scripts/verify_installed_artefact.py` | WARN | Installed-artefact verification names and copies the employment fixture. |

These are scanner, questionnaire, and verification plumbing rather than an employment-decision product. They are retained as visible results because applying file-wide suppressions to broad production modules would hide unrelated future matches. This demonstrates a known limitation: domain activation can surface self-reference false positives and still needs file-level human review.

## Suppression audit

The dedicated audit found 11 `regula-ignore` directives, all with rationales and no warning or error status. A first run exposed three bare directives that only became relevant when the employment domain was active; they were corrected with narrow explanatory rationales before these results were recorded.

The displayed suppressed-finding count is larger than the directive count because one file-level directive can suppress several detector matches, and domain-gated findings are included in the displayed total.

## Coverage limits

- Default production scope excludes test files and named non-production directories. The CLI now discloses both populations even when other files were scanned.
- `.venv` dominates the pruned-file count and is third-party installed code, not repository source.
- Benchmarks and examples are validated separately by the test and evaluation suites; they are intentionally outside this self-scan population.
- The scan observes source patterns only. It cannot assess repository history, hosted infrastructure, real deployment behaviour, model performance, accessibility, or organisational controls.
- Zero active findings is not a false-positive, false-negative, security, or legal-validity measurement.

## Reproduce

From the exact source commit being reviewed:

```bash
python3 -m scripts.cli check . --no-facts
python3 -m scripts.cli check . --no-facts --domain employment
python3 -m scripts.cli check --audit-suppressions
```

Record `git rev-parse HEAD` with the output. Counts can change as production files and detector rules change; interpret any difference rather than copying the headline numbers forward.
