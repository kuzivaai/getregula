# Phase 0 — BASELINE

All figures MEASURED on branch `improvement/2026-08-programme` at commit
`d4180e3`, 27 July 2026, unless tagged otherwise. Phase 0 changes nothing;
every defect recorded here is fixed later, in plan order.

Evidence tags: **MEASURED** (command + output) / **VERIFIED** (source +
date) / **JUDGEMENT** / **REPORTED-UNVERIFIED**.

---

## 1. Test suite

| Metric | Value | Method |
|---|---|---|
| pytest | **2,849 passed, 0 failed, 0 skipped** | MEASURED `python3 -m pytest tests/ -q` |
| pytest duration | **896.15 s (14 min 56 s)** | MEASURED, same run |
| Custom runner | **1,386 passed, 0 failed, 0 skipped (963 test functions)** | MEASURED `python3 tests/test_classification.py` |
| Coverage | see §9 | MEASURED `pytest --cov=scripts` |

Rubric anchor said 2,821 tests. **MEASURED 2,849.** Principle 2 applies:
the anchor is corrected to 2,849 (the delta is the 28 tests added by the
27 Jul moat work committed at `d4180e3`).

## 2. Gate status (all green at baseline)

| Gate | Result | Method |
|---|---|---|
| `claim_auditor --verify-facts` | OK — 137 fact references across **16 files**, all match canonical | MEASURED |
| `site_integrity.py` | OK | MEASURED |
| `verify_seo.py` | passed, 4 pre-existing warnings (title lengths) | MEASURED |
| `cli self-test` | 6/6 passed, rc=0 | MEASURED |
| `cli doctor` | 8 passed, 4 info, rc=0 | MEASURED |
| `cli security-self-check` | rc=0 | MEASURED |
| ruff F821/F811 on `scripts/`, `tests/` | All checks passed | MEASURED |
| ruff F821 on `benchmarks/synthetic/fixtures/` | 21 findings — **intentional**: fixtures are deliberately non-runnable samples of risky code; pre-existing (commit `1f731a8`) | MEASURED |

## 3. Detection patterns (measured, not claimed)

`python3 -c "import site_facts; site_facts.count_patterns()"`:

| Bucket | Count |
|---|---|
| tier_groups | 57 |
| **tier_regexes (headline claim)** | **419** |
| ai_indicators | 212 |
| gpai_training | 17 |
| architecture | 38 |
| data_source | 10 |
| logging | 4 |
| oversight | 4 |
| credential | 18 |
| agentic_categories | 10 |
| grand_total | 722 |

## 4. Per-language mechanism — MATERIAL CORRECTION TO THE RUBRIC ANCHOR

Rubric anchor: "6/8 languages regex-only". **That is wrong in both
directions, because the mechanism depends on an optional extra.**

MEASURED from `scripts/ast_engine.py` and `pyproject.toml`:

| Language | Mechanism | Depends on |
|---|---|---|
| Python | Real AST (`ast_analysis.py`, stdlib `ast`) | nothing — always available |
| JavaScript | tree-sitter AST, **else regex fallback** | optional extra `regula-ai[ast]` |
| TypeScript | tree-sitter AST, **else regex fallback** | optional extra `regula-ai[ast]` |
| Java | regex only | — |
| Go | regex only | — |
| Rust | regex only | — |
| C | regex only | — |
| C++ | regex only | — |

- With the `[ast]` extra installed: **5/8 regex-only** (anchor says 6/8 — too pessimistic).
- On a **default `pip install regula-ai`: 7/8 regex-only** (anchor is far too optimistic; only Python gets AST).

MEASURED: a fresh venv install of the built wheel does **not** include
tree-sitter (`tree_sitter: ABSENT (default install confirmed)`).

**Anchor correction:** the honest statement is mechanism-dependent and must
always name the install path. See §11 for the resulting anchor adjustment.

Also MEASURED: `site_facts.count_languages()` returns a **hardcoded `8`**
with the comment "Fixed list". The 8-language claim is therefore not
derived from the code and would not fail if a language were removed —
a claim-auditor blind spot (§7).

## 5. CLI surface

**62 commands** — MEASURED via `regula --help-all` (62 command entries),
matching `site_facts.count_commands()` which greps `^def cmd_` across
`scripts/cli*.py`. The rubric's "62 CLI commands" is confirmed.

Note: `regula --help` does **not** list the commands (only global flags);
the list requires `--help-all`. Discoverability finding, not a defect.

## 6. Precision-benchmark provenance

Source artefacts: `benchmarks/results/random_corpus/METHODOLOGY.json`,
`PRECISION.json`, `BLIND_LABELS.json`, `benchmarks/LABELLING_CRITERIA.md`.

| Property | Value | Note |
|---|---|---|
| Corpus construction | GitHub search, pool 276 → **50 repos**, `random_seed: 42`, filters `stars:10..5000, pushed:>2024-04-01, size>50KB` | Reproducible; good |
| **Language coverage** | **Python only** — every seed query is `language:python+topic:...` | **The headline precision figure covers 1 of 8 supported languages.** 7 languages have NO precision measurement. |
| Labelled findings | 201 total, **115 production-code** (N=115) | |
| Labeller | **Single** — `BLIND_LABELS.json` entries carry no `labeller` field; `LABELLING_CRITERIA.md` records all 446 corpus entries attributed to one person | Single-labeller confirmed |
| Overall precision | **0.835** | |
| high_risk tier | tp=2, fp=4, **n=6**, precision 0.333 | The "33%" figure. N=6. |
| Other tiers | ai_security .854 (n=48), agent_autonomy .829 (n=41), limited_risk .875 (n=8), minimal_risk 1.0 (n=11), credential 1.0 (n=1) | |
| **Recall** | **Not measured at all** — no false-negative denominator exists in any artefact | Anchor's "recall unquantified" confirmed |
| Version attribution | **DISCREPANCY**: `PRECISION.json` says "Re-scanned with domain-gated Regula **v1.7.0**"; `README.md:246` says "measured on **v1.7.4**" | Claim-integrity defect; the claim auditor checks numbers, not version attributions |
| Currency | Last measured 2026-04-25 against a 1.7.x build; **never re-measured on 1.9.0** | |

## 7. Claim-auditor coverage — blind-spot census

| Surface class | Count | Number-drift verified? | Unsourced-claim swept? |
|---|---|---|---|
| Files in `--verify-facts` set | 16 | **Yes** | Yes |
| `site/**/*.html` | 56 | Only the 6 in the 16-set | **Yes** (via `site_integrity.check_claims`, which passes every site HTML) |
| `docs/**/*.md` | 58 | Only 4 in the 16-set | **No** — docs markdown is not swept by any gate |
| `README.md`, `SECURITY.md` | 2 | Yes | Yes |

**Finding:** number-drift protection covers 16 files; unsourced-claim
detection covers all site HTML but **no `docs/*.md` outside the 16-set**.
Two blind spots already known from the handover are confirmed present:
numbers separated from their unit by markup, and German/Portuguese
dot-format numerals (`2.849`). Both were hit during the 27 Jul count
cascade and required a manual sweep.

## 8. Performance — superlinear scaling MEASURED

| Target | Files | Wall time | Per file |
|---|---|---|---|
| `benchmarks/synthetic/fixtures` (default install) | 13 | **0.576 s** | 44 ms |
| this repo, `regula check . --format json` | 136 reported | **38.0 s / 40.9 s** (two runs) | ~280 ms |
| this repo, `report.scan_files('.')` direct | 222 scanned | **66.3 s** | 299 ms |

Per-file cost rises ~6.7x between the 13-file and 222-file targets. This
is superlinear and is the single largest UX risk for real-world repos
(a 1,000-file project would extrapolate to minutes). Cause not yet
diagnosed — Phase 1 investigation target. Note also the two scan entry
points report different file counts (136 vs 222) for the same directory;
scope/skip rules differ between them.

## 9. Coverage

MEASURED via `pytest --cov=scripts --cov-report=json`. **Run pending at
time of writing** (the instrumented suite runs materially slower than the
896 s uninstrumented baseline). Recorded in the follow-up checkpoint;
this row is deliberately left as an honest gap rather than estimated.

## 10. UX baseline — fresh venv, default install

Script: `scratchpad/ux_baseline.sh`. Wheel built from this tree
(`regula_ai-1.9.0-py3-none-any.whl`).

| Step | MEASURED |
|---|---|
| `pip install <wheel>` into fresh venv | **1.20 s** |
| First scan, 13-file sample | **0.576 s**, exit code 1 |
| Bare `regula` (no args) in that directory | **0.207 s**, exit code 1 |
| Total time-to-first-result from empty venv | **~1.8 s** plus venv creation |

Install speed is excellent and is a direct dividend of the stdlib-only
constraint.

### Friction points MEASURED

1. **HIGH — `doctor` prints install commands for the wrong PyPI package.**
   `regula doctor` emits `pip install regula[yaml]` and
   `pip install regula[ast]`. The distribution is named **`regula-ai`**
   (`pyproject.toml:6`). **`regula` is a real, unrelated package on
   PyPI** (VERIFIED 2026-07-27, `GET https://pypi.org/pypi/regula/json`
   → HTTP 200, "A lightweight, simplified wrapper around the Tkinter
   library", v0.1.2). Following Regula's own advice installs a stranger's
   package. **18 occurrences of the `regula[` form repo-wide**
   (`scripts/doctor.py`, `scripts/pdf_export.py`, `scripts/signing.py`,
   `scripts/conform.py`, `scripts/timestamp.py`, docs). Severity: high —
   user harm plus supply-chain flavour. Dimension: Trust & integrity.
2. **HIGH — silent AST-to-regex downgrade for JS/TS.** On a default
   install, scanning JavaScript/TypeScript falls back to regex with **no
   disclosure in the scan output** (MEASURED: grepping a JS scan for
   `tree.sitter|regex|degrad|fallback|AST` returns nothing).
   `regula doctor` does disclose it, but a user who never runs `doctor`
   is given regex-quality results while `docs/TRUST.md` states "Python
   and JS/TS have full AST + cross-file flow". Dimension: Detection
   efficacy + Trust.
3. **MEDIUM — `regula check` exits 1 when findings exist.** Correct for
   CI gating, but it terminates `set -e` shell scripts (it broke this
   baseline's own harness). Needs to be explicit in the quickstart.
4. **LOW — commands are invisible from `--help`.** `--help-all` is
   required to see the 62 commands.

## 11. Rubric anchor re-measurement (Principle 2)

| Dimension | Anchor as given | Measurement | Disposition |
|---|---|---|---|
| Detection efficacy | 42 — "33% high-risk precision; 83.5% on N=115 single-labeller; recall unquantified; 6/8 languages regex-only; no head-to-head" | 33% (n=6) ✓, 83.5% (N=115) ✓, single-labeller ✓, recall absent ✓, no head-to-head ✓. **But: 7/8 regex-only on a default install, not 6/8, and the 83.5% covers Python only** | **Lower to 38.** Two facts the anchor missed both cut against the tool: the default install has one AST language, and the precision figure generalises to none of the other seven. |
| Engineering craft | 90 — "2,821 tests" | **2,849 tests** MEASURED; suite green; install 1.2 s | **Hold at 90**, test count corrected to 2,849. Superlinear scan performance (§8) is a real defect but is offset by the suite, packaging and gate discipline. |
| Trust & integrity | 92 — "claim auditor fails CI on drift; published FP rates" | Both true. **But** number-drift verification covers 16 of ~116 surfaces, `docs/*.md` is unswept, a version attribution is internally contradictory (§6), and `doctor` misdirects users to a foreign package (§10.1) | **Lower to 84.** The apparatus is real and better than the segment norm; the coverage gap and the two integrity defects are not consistent with 92. |
| Regulatory currency | 85 | Omnibus flip test-gated ✓; Korea ✓; current Colorado statute + docket precision ✓; delta-log now verified-primary ✓ | **Hold at 85.** |
| Problem altitude | 40 | Not independently re-measurable in Phase 0 (depends on the AICDI mapping, reviewed in Phase 1) | Hold pending Phase 1. |
| Delivered-value | 8 | Not re-measured in Phase 0; unchanged artefacts | Hold at 8. |
| Durability | 30 | Bus factor 1 confirmed (single committer in `git log`) | Hold at 30. |

**Recomputed provisional aggregate:**
0.25(38) + 0.20(40) + 0.15(90) + 0.15(84) + 0.10(85) + 0.10(8) + 0.05(30)
= 9.5 + 8.0 + 13.5 + 12.6 + 8.5 + 0.8 + 1.5 = **54.4** (given: 57).

The baseline is **worse than the programme assumed**, by 2.6 points, and
the reasons are specific: the default-install detection mechanism, the
Python-only precision corpus, and two claim-integrity defects. Recording
this before any improvement work is the point of Phase 0.

## 12. Public-surface census

| Surface | Location | Editable here? |
|---|---|---|
| README | `README.md` | in-repo |
| Security policy | `SECURITY.md` | in-repo |
| Website | `site/**` (56 HTML incl. DE + PT-BR locales, 6 region pages) | in-repo source; **deployment is human-gated** |
| Docs | `docs/**` (58 markdown) | in-repo |
| PyPI description | `pyproject.toml:11` `description` + `readme = "README.md"` | in-repo text; **publishing is human-gated** |
| Pricing | `site/pricing.html` | in-repo; **live pricing change is human-gated** |
| GitHub repo metadata | topics, description, releases page | **external, human-gated** |
| PyPI project page | rendered from the above at publish time | **external, human-gated** |

Snapshot for diffing: the 16 claim-audited files are already
number-locked; the full HTML set is fingerprinted by
`scripts/site_integrity.py`. No separate snapshot artefact is needed —
`git diff` against `d4180e3` is the diff-ready baseline.
