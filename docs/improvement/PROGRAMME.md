# REGULA IMPROVEMENT PROGRAMME v2 — EVIDENCE-GATED, RESUMABLE, INDEPENDENTLY SCORED

> Verbatim record of the commissioning prompt, written at programme start
> per the SESSION PROTOCOL. Do not edit the body: it is the contract this
> programme is executed against. Progress lives in STATE.md.

## SESSION PROTOCOL (execute before anything else, every session)

Check for docs/improvement/STATE.md. If it exists: read it, read docs/improvement/PROGRAMME.md, and resume from the recorded position. Do NOT restart completed phases.

If it does not exist (first session): write this entire prompt verbatim to docs/improvement/PROGRAMME.md; create docs/improvement/STATE.md; create branch improvement/2026-08-programme from main. All work happens on this branch.

Checkpoint STATE.md after every phase and every ~20 significant actions: done / in progress / next / open questions / escalations. Checkpoint before context runs low so a fresh session resumes losslessly.

Read CLAUDE.md, list .claude/commands/ and .claude/skills/, and use every relevant project skill and command throughout.

## MISSION

Execute a full-cycle improvement programme: exhaustive code review → validated research acquisition → strategy synthesis → adversarially reviewed implementation plan → implementation → pre/post benchmarked verification → independent re-scoring → public-surface alignment. Comprehensiveness, thoroughness and accuracy take absolute priority over speed. Never present partial work as complete.

## BINDING PRINCIPLES

1. Evidence tags on every material claim: VERIFIED (source + date) / MEASURED (command + output) / REPORTED-UNVERIFIED / JUDGEMENT / MACHINE-LABELLED. "Insufficient data" is always acceptable; guessing is not.
2. Measured-over-embedded. If any measurement contradicts a number embedded in this programme — including the rubric anchors below — the measurement wins. Record the discrepancy in BASELINE.md and adjust the anchor with a note.
3. No metric gaming. The rubric is an instrument, not a Goodhart target. No tests written to trivially pass; no benchmark parameters chosen post hoc; every new public number gets a claim-auditor rule so drift protection extends to it.
4. Architecture constraints stand unless overturned by written ADR: stdlib-only core, offline by default, no telemetry. Optional networked features ship as extras, off by default, degrade gracefully when absent, and carry their own ADR.
5. Licence hygiene. Before adapting any code from a research artefact or repository, verify licence compatibility with the Apache-2.0/EUPL-1.2 + Detection Rule License structure. Record provenance per adapted snippet. Incompatible → reimplement from the paper's description only.
6. Git safety. Never commit to main. No force-pushes, no history rewrites. Conventional commits, one logical change each, full test suite green per commit.
7. Independence via subagents. Three charters run as fresh subagents with only their defined inputs: RESEARCH VALIDATOR (Phase 2), HOSTILE REVIEWER (Phase 4), INDEPENDENT SCORER (Phase 7). The implementing agent may not overrule a subagent verdict without a written disposition recorded in STATE.md.
8. Loop caps. Every validate/review cycle is capped at 3 iterations. Still failing → STOP, write an escalation note, continue non-dependent work, surface the escalation at the next human gate. Never silently lower a bar to pass.
9. Stop-and-ask gates (the only human interruptions): merging to main; changing any public-facing claim; anything requiring credentials, payment, accounts, or external submission; deleting user-facing functionality.
10. Drift checks, not deadlines. No rushing — but at every checkpoint answer in STATE.md: "is the current activity still the highest-value path to the rubric?" If no, log it and correct course.
11. Delivered-value may never be fabricated. No invented or simulated interviews, testimonials, users, stars, or adoption, under any framing. That dimension moves only on artefacts that verifiably exist.

## SCORING RUBRIC (source of truth; anchors provisional until Phase 0 re-measurement)

| Dimension | Weight | Anchor | Basis as given |
|---|---|---|---|
| Detection efficacy | 25% | 42 | 33% high-risk-tier precision; 83.5% overall on N=115 single-labeller; recall unquantified; 6/8 languages regex-only; no head-to-head ever run |
| Problem altitude | 20% | 40 | addresses 1 of ~20 governance gaps fully per own AICDI mapping; static-only |
| Engineering craft | 15% | 90 | 2,821 tests; stdlib-only; ships daily without breakage |
| Trust & integrity apparatus | 15% | 92 | claim auditor fails CI on drift; published FP rates |
| Regulatory currency & scope | 10% | 85 | Omnibus propagated in 3 days test-gated; Korea; current Colorado statute |
| Delivered-value evidence | 10% | 8 | 4 stars, 0 forks, 0 interviews, 0 revenue, 1 listing |
| Durability | 5% | 30 | bus factor 1; competitor parity in weeks |

Aggregate 57. Honest ceiling: autonomous in-repo work cannot exceed roughly 70–72, because delivered-value and parts of altitude/durability are human-gated (annotators, interviews, adoption, committee seats, publication acceptance). Obligations: (a) reach the ceiling with verified evidence; (b) make every human-gated point as cheap as possible to earn; (c) output the HUMAN-GATED LEDGER (Phase 7). Claiming 85 from code alone would be a lie — do not.

## PHASE 0 — BASELINE (measure everything; change nothing)

Full test suite (count, duration, failures MEASURED). Claim auditor status. Pattern counts by language and mechanism (AST vs regex). Inventory of all 62 CLI commands. Coverage report. Precision-benchmark provenance: corpus location, N, labelling method. Performance timings on a sample scan. UX baseline: fresh venv → install → first successful scan; record time-to-first-result and every point of friction. Public-surface census: locate every public claim (README, in-repo website source, PyPI description, pricing page); classify each surface in-repo (editable here) vs external (human-gated); snapshot all claims diff-ready. Write docs/improvement/BASELINE.md. Apply Principle 2 to the rubric anchors.

## PHASE 1 — EXHAUSTIVE CODE REVIEW (learn everything; change nothing)

Read the entire codebase — every module, command, pattern definition, test. Produce docs/improvement/CODE_REVIEW.md:

- Architecture map of the actual call graph (scan → detect → classify → crosswalk → evidence output).
- Detection layer: per-language mechanism audit; regex quality (anchoring, FP-prone constructs, patterns no test exercises); AST depth for Python/JS-TS.
- Classification layer: trace ≥10 real high-risk false positives from the existing corpus to their causal patterns; commit a categorised FP taxonomy as structured data (docs/improvement/fp_taxonomy.json) — this feeds Phase 3 annotation guidelines.
- Crosswalks: storage format, completeness against the 13 cited frameworks, staleness risk.
- Evidence outputs validated against their specs: Annex IV/VIII, manifests, Ed25519 + RFC 3161 chain, CycloneDX 1.7 ML-BOM schema, DPV-AIAct JSON-LD (vocabulary URLs must resolve).
- Test-suite audit: real coverage vs tautological tests; the claim auditor's blind spots.
- Corpus audit: N=115 composition, duplication, representativeness, labelling notes.
- Security pass: injection surfaces in report generation, path handling, subprocess use.
- Repo hygiene: dead code, packaging, CI, docs-vs-behaviour accuracy, licence headers.
- Every finding: severity + rubric dimension. Exhaustive inspection precedes any proposed fix — standing project rule.

## PHASE 2 — RESEARCH ACQUISITION + VALIDATION (cap: 3 loops)

Seed corpus: the 27 Jul 2026 research sweep in docs/research/ if present (absent → state so and request it): QASecClaw arXiv:2605.01885; ZeroFalse arXiv:2510.02534; Tencent ICSE 2026 SEIP FP-reduction study (note: chain-of-thought underperformed); IRIS arXiv:2405.17238; MoCQ arXiv:2504.16057; GadgetHunter FSE 2026; CASTLE TASE 2025; PrimeVul ICSE 2025; Risse et al. ISSTA 2025; SecVulEval; BenchVul; DPV 2.0 ISWC 2024 + EU-AIAct extension; AIRO; obligation-extraction CLSR 2025; LGGT+ arXiv:2603.28558; prEN 18286; ISO/IEC 42005:2025; Reg (EU) 2026/1744; Korea AI Basic Act (in force 22 Jan 2026); Colorado SB 26-189 incl. the xAI v. Weiser enforcement stay. Then search for anything newer or missed.

Per candidate, a validation card: full citation; publication status checked against the primary source (peer-reviewed / preprint / standard / grey — never trust a secondary mention); the specific claim Regula would rely on; falsifiable applicability test in Regula's context (stdlib-only? offline? solo maintainer? domain shift from vulnerability to compliance detection?); expected rubric movement (range); effort; clonability class (a code / b currency / c labelled data / d citable artefact / e credential).

RESEARCH VALIDATOR subagent: fresh context; inputs = the cards only; verifies citation existence and status, attacks each applicability argument, verdicts per card. Run /research-eval on the pack — if the command doesn't exist, say so explicitly and apply this identical checklist manually. Pass = zero unverifiable citations relied upon; every adoption has a falsifiable applicability argument; every rejection has a recorded reason; domain-shift risk assessed per item.

## PHASE 3 — STRATEGY SYNTHESIS (measurement instruments first)

Using validated items only. Items 1–2 are mandatory first movers because they instrument everything else:

1. Corpus rebuild protocol to PrimeVul discipline: dedup, temporal split, documented annotation guidelines derived from the Phase 1 FP taxonomy, protocol targeting ≥3 independent human annotators with Fleiss' κ ≥ 0.7. You may machine-pre-label with a documented ensemble — always tagged MACHINE-LABELLED, never presented as human labels. Build the annotation harness and recruit-ready pack; the human pass is a ledger item.
2. Pre-registered head-to-head benchmark vs AIR Blackbox and Systima Comply: commit the full protocol (metrics incl. CASTLE-style FP-penalising score, corpus, tool versions, invocation parameters, scoring script) BEFORE running anything. Then run PRE-implementation. It runs again, unchanged, in Phase 6. Publish whatever it shows — including if Regula loses.
3. Precision stack: optional SARIF-mediated LLM verification tier over flagged findings (QASecClaw/ZeroFalse pattern; Tencent cost evidence; no chain-of-thought). Extras-installed, off by default, graceful absence, ADR.
4. Currency stack: machine-readable regulatory delta-log, first entry 2024/1689 → 2026/1744, expressed against DPV-AIAct; versioned, DOI-ready, CI-tested vocabulary resolution; DPVCG upstream contribution prepared, not submitted.
5. Altitude within static scope: ISO/IEC 42005-aligned impact-assessment module; OWASP-Agentic statically-detectable checks; explicit documentation of what stays out of scope (runtime) and why.
6. Novel-combination assessment: do 3+4 combine into a temporally aware classifier — findings carry the regulation version assessed against; evidence packs record delta-log version; re-scan diffs distinguish "law changed" from "code changed"? Verify honestly whether anything in the segment does this before using the word novel.
7. Strategy doc: every element → dimension → movement range (assumptions stated) → clonability class → projected aggregate with arithmetic. Projection above ~72 is a signal to re-check the arithmetic.

## PHASE 4 — IMPLEMENTATION PLAN + HOSTILE REVIEW (cap: 3 loops)

Ordered plan; per item: measurable acceptance criteria, tests-to-add-first, rollback path, claim-auditor impact, docs impact, licence-provenance note where research code is adapted.

HOSTILE REVIEWER subagent: fresh context; inputs = plan + CODE_REVIEW + BASELINE only. Attacks: feasibility under stdlib-only; over-engineering relative to near-zero users; claim-integrity risk; test-gaming risk; licence risk; time-sink risk. Every attack gets a written disposition (accepted → plan changed / rejected → reason). Zero unresolved major objections = pass.

STOP-AND-ASK GATE: present plan summary, projected movement, escalations. Wait for approval.

## PHASE 5 — IMPLEMENTATION

Plan order. Per item: tests first where feasible; implement; suite green; claim auditor green; STATE.md updated; conventional commit. Done = acceptance criteria MEASURED. Honest failure → BLOCKED with evidence; continue; never fake completion or silently descope. Take the time each item genuinely needs.

## PHASE 6 — VERIFICATION

Re-run the pre-registered benchmark POST-implementation, parameters untouched; any deviation requires written justification. Suite + coverage + performance vs baseline. Precision re-measured with the provenance rule: published precision claims may only rest on human-labelled data; machine-labelled figures are always inline-tagged MACHINE-LABELLED wherever cited. Re-validate every evidence output against schema/spec. Anti-gaming audit: list any new test asserting trivialities and any benchmark or corpus decision that could favour Regula, each with justification. /research-eval fidelity pass: did implementation stay faithful to the validated research? Public-claim regression sweep: every number on every in-repo surface traces to a test or measured artefact. Re-measure time-to-first-result.

## PHASE 7 — INDEPENDENT RE-SCORE + HUMAN-GATED LEDGER

INDEPENDENT SCORER subagent: fresh context; inputs = rubric + evidence artefacts only (BASELINE, CODE_REVIEW, benchmark reports, verification outputs) — not the implementation narrative. Produces docs/improvement/SCORE_DELTA.md: old → new per dimension, every change anchored, aggregate arithmetic shown, sensitivity note. Main agent may annotate, not alter, absent a written disposition.

HUMAN-GATED LEDGER (ledger.yaml + prose): the explicit remaining path to 85. Per item — action (e.g. 3 human annotators for the κ-scored corpus pass; 10 recorded user interviews; first consulting engagement; dataset-paper submission with named venue and deadline; DPVCG submission; BSI ART/1 application), expected dimension movement, dependencies, and confirmation that preparation reduces the human effort to ≤1 day.

## PHASE 8 — PUBLIC-SURFACE ALIGNMENT (in-repo surfaces only)

Update README, in-repo website source, docs, PyPI description text, repo structure to the verified state: user-first ordering (what it does → 60-second start → honest limits); improved time-to-first-result reflected in the quickstart; every number claim-auditor-backed with provenance tags; benchmark/comparison page drafted from Phase 6; changelog entry. External executions (PyPI publish, site deploy, submissions) go on the ledger as prepared human tasks. STOP-AND-ASK GATE before merge to main.

## FINAL DELIVERABLE

FINAL_REPORT.md: what was done; measured before/after; score delta with arithmetic; regressions and negative results — anything that got worse or failed, stated plainly; blocked items; escalations; the ledger; and the three most important things now known about this codebase that were not known at Phase 0. The honesty of this report outranks the flattery of the result.
