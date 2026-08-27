# Regula public engineering open-items register

Date: 27 August 2026

This register contains product engineering and reusable evidence only. Private
operating records and personal context do not belong in this repository.

Status meanings:

- `OPEN`: no adequate implementation or current verification exists.
- `PARTIAL`: useful implementation exists, but a stated completion condition
  is unmet.
- `BLOCKED`: completion requires authenticated human access, a policy decision
  or representative human research.
- `CLOSED`: current evidence establishes the completion condition.

## Incident and distribution

| ID | First raised | Status | Current evidence and completion condition |
|---|---|---|---|
| R-001 | 27 August 2026 | BLOCKED | The custom domain returns GitHub Pages 404 while the Netlify production alias works. The reversible owner procedure is now specified in `docs/operations/WEBSITE_RECOVERY_RUNBOOK.md`. Complete when the owner applies verified project-specific DNS values and public browser smoke tests pass. |
| R-002 | 27 August 2026 | BLOCKED | PyPI exposes an active empty simple-index record but public endpoints do not establish account control. Complete when authenticated control and Trusted Publisher configuration are recorded. |
| R-003 | 27 August 2026 | OPEN | No public GitHub tag or release exists. A stale local `v2.0.0` tag points outside the current lineage. Complete when the stale tag is excluded and a fresh signed tag is created only by the approved release path. |
| R-004 | 27 August 2026 | BLOCKED | Public `main` is sanitised, but 66 GitHub pull-request head refs expose 2,444 commits outside it. The privacy scan found 486 unique rule/path combinations and 64 affected refs. Complete only after GitHub Support confirms disposition of the affected refs and caches; forks and external clones remain a separately stated limit. |
| R-005 | 27 August 2026 | BLOCKED | Product/package naming remains undecided. Website recovery may proceed, but immutable tag and package publication require a recorded decision. |
| R-006 | 26 August 2026 | PARTIAL | The local audit branch is ahead of remote `main` and has not had protected remote review. Complete after protected remote review and exact-commit CI. |

## Validity and detector behaviour

| ID | First raised | Status | Current evidence and completion condition |
|---|---|---|---|
| V-001 | 31 July 2026 | OPEN | The constructed commercial diagnostic recorded 0 of 40 for Regula against 40 of 40 for a transparent baseline. It is not external accuracy evidence. Complete through the preregistered project-held-out multi-annotator study. |
| V-002 | Before 25 August 2026 | OPEN | The historical precision record is single-reviewer and its corpus cannot be reconstructed. Its figure remains confined to the registered provenance surface; replacement requires independent reproducible evidence. |
| V-003 | 17 August 2026 | OPEN | The independent annotation protocol is designed but not executed. Complete with frozen inputs, at least three blinded raters, preserved disagreements, adjudication and confidence intervals. |
| V-004 | 27 August 2026 | OPEN | Default synthetic high-risk label fidelity moved from 10 of 30 to 4 of 30 because biometric and financial categories became opt-in. Complete when the precision and miss trade-off is measured on frozen positive and negative held-out data and a default-policy decision is recorded. |
| V-005 | 26 August 2026 | OPEN | The 27 August rerun reproduced 18/18 byte-repeatable variants and 11/13 preregistered diagnostic assertions on the 13-repository pinned external corpus. `private-gpt` and education-declared `proctoring-ai` remain adverse probes. This purposive diagnostic has no independent exhaustive ground truth, so detector validity across languages, domains, generated code, wrappers and indirection remains unknown. Complete only for predeclared populations actually evaluated. |
| V-006 | 26 August 2026 | OPEN | The heuristic priority score is not a correctness probability. Calibration claims require a representative calibration set and separate held-out evaluation. |

## UX and accessibility

| ID | First raised | Status | Current evidence and completion condition |
|---|---|---|---|
| U-001 | 26 August 2026 | OPEN | No representative moderated study establishes comprehension, confidence or task completion for the assessment and CLI journeys. Complete with recorded developer and governance-reviewer sessions. |
| U-002 | 26 August 2026 | PARTIAL | A fresh complete run covered 54 canonical pages at two viewports: 108 runs, zero detected violations, 71 incomplete colour-contrast results and 516 retained nodes. Real-browser checks also exercised the home questionnaire's successful and unanswered states at 390 × 844 and 1440 × 1000. Automation and agent-operated browser checks are not assistive-technology evidence. Complete after the manual WCAG 2.2 AA matrix and representative disabled-user testing. |
| U-003 | 26 August 2026 | OPEN | Non-English assessment pages have translated content but no fluent-user comprehension evidence. Complete with separate DE and PT-BR participant evidence or explicitly narrower support claims. |
| U-004 | 26 August 2026 | BLOCKED | EN, DE and PT-BR assessment pages duplicate scoring integration. Consolidating scoring before V-004 settles the default policy would increase the blast radius of an unvalidated rule change. Complete after the validity decision, when one generated decision model can produce all three and parity, keyboard and state-transition tests pass. |

## Engineering, security and regulatory maintenance

| ID | First raised | Status | Current evidence and completion condition |
|---|---|---|---|
| E-001 | 26 August 2026 | PARTIAL | Two-worker xdist roughly halved controlled full-suite time and CI is configured accordingly. Complete after exact-head remote CI confirms the updated critical path while the sequential audit stays green. |
| E-002 | 19 August 2026 | CLOSED | The 27 August locked all-extras audit found one advisory, `PYSEC-2026-3412`, in WeasyPrint 68.1 and no fixed release. Regula does not pass the affected `presentational_hints=True` option, retains an HTML fallback and suppresses nothing. Reopen if the dependency, advisory or call path changes. |
| E-003 | Before 27 August 2026 | OPEN | The [Commission's AI Act Service Desk](https://ai-act-service-desk.ec.europa.eu/en/guideline-explorer), retrieved 27 August 2026, still described its Article 6(5) classification guidance as a draft awaiting further consultation and adoption. `scripts/compliance_check.py` now records that verification date. Complete only when a primary Commission source confirms final adoption and all generated surfaces update together. |
| E-004 | 26 August 2026 | CLOSED | The premise that no pilot existed was false. `scripts/run_decision_mutations.py` mutates every fact comparison and every rule-to-obligation edge in the pure decision model. On 27 August it reconciled 136 mutants: 136 killed, 0 survived, 0 invalid and 0 timed out. Equivalent mutants were not assessed. This establishes assertion sensitivity for those two operators and this model only, not detector validity or legal correctness. |
| E-005 | 26 August 2026 | PARTIAL | The pinned external manifest is reproducible and includes large snapshots. The 27 August isolated-cache rerun observed 0.244 to 124.157 seconds per scan, while preserving explicit skipped-file counts. It did not measure warm-cache improvement, per-run peak memory or constrained-host behaviour. Complete only if a product decision needs those populations and declares a useful performance budget first. |
| E-006 | 27 August 2026 | OPEN | The historical register had 25 open, 27 partial and 32 legacy review-required machine-classified entries. Each requires current-tip evidence before it can be mapped to this register or closed. Absence from this public-safe register is not closure. |

## Historical reconciliation queue

The following identifiers were mechanically reported as open in the retired
register and require current-tip disposition: `N66`, `N71`, `N79`, `N80`,
`N81`, `N82`, `N83`, `N84`, `N85`, `N86`, `N87`, `N88`, `N98`, `N99`,
`N132`, `N143`, `N144`, `N150`, `N152`, `N157`, `N160`, `N161`, `N164`,
`N165`, `N166`.

The following were mechanically reported as partial: `N61`, `N62`, `N63`,
`N64`, `N69`, `N73`, `N78`, `N89`, `N90`, `N91`, `N92`, `N93`, `N94`,
`N95`, `N96`, `N97`, `N100`, `N101`, `N102`, `N103`, `N104`, `N105`,
`N106`, `N108`, `N139`, `N179`, `N180`.

Thirty-two legacy rows were classified `REVIEW_REQUIRED`. Their private prose
is not restored here. Reconciliation must use their identifiers and current
product evidence without copying private material back into the public tree.
