# DIRECTIVE v3: verbatim record

Received from the owner 29 July 2026 and recorded here per its own section 0.

**This directive EXTENDS `PROGRAMME.md`. It does not replace it.** Where v3 and
PROGRAMME.md conflict, PROGRAMME.md's principles win and the conflict is logged
in the table below. That instruction is v3's own (section 0), so following it is
not a deviation.

**The body below is reproduced verbatim.** It is a contract document, held to
the same standard as PROGRAMME.md, whose header states "Do not edit the body".

> **Logged deviation, standing rule on em dashes.** HANDOVER.md section 11
> forbids em dashes in repo copy. The directive body contains them. The
> verbatim-record requirement wins for the same reason verbatim command output
> wins in `.claude/rules/measurement.md`: altering it would falsify the record.
> The em dashes below are the owner's, not this repo's prose, and nothing in
> this file outside the quoted body uses them.

---

## Conflict and extension log (required by section 0)

| # | v3 says | PROGRAMME.md says | Resolution |
|---|---|---|---|
| 1 | Section 5 inserts a new **Phase 1.7** (scaffolding refresh) before Phase 2 resumes | Phases run 0, 1, 2, 3, 4, 5, 6, 7, 8 in order | **Extension, not conflict.** Phase 2 is at loop 1 of 3 and unfinished; 1.7 is inserted, nothing is skipped. Loop caps and prior verdicts stand. |
| 2 | Section 7 adds repository, website and consultant-packaging scope | Phase 8 covers public-surface alignment only | **Extension.** v3 sequences execution after the Phase 4 gate, which is consistent with Principle 9 (stop-and-ask before public change). |
| 3 | Section 7a and 7b require OpenSSF Scorecard, Lighthouse CI, Playwright and axe-core | Principle 4: stdlib-only core, offline by default, no telemetry | **Not a conflict.** HANDOVER.md section 11 already records this as a **runtime-core** constraint, not a CI constraint. Logged because it reads as one. |
| 4 | Section 3 makes primary sources outrank research sweeps | Principle 1 (evidence tags) and Principle 7 (independence) | **Consistent, and strengthens both.** No conflict. |
| 5 | Section 2 permits tracked, shrinking, visible debt | Principle 3 (no metric gaming) | **Consistent.** The quarantine ratchet is shrink-only and itemised; silent debt remains forbidden. |
| 6 | Section 8 proposes a citable write-up on self-referential measurement error | Phase 7 deliverables | **Extension.** Search-first condition is stated in v3 itself and is retained. |
| 7 | Section 4 re-opens the agentic-AI item that STATE.md closed | Principle 2 (measured over embedded) | **v3 is correct and PROGRAMME.md agrees.** A measurement beat the embedded conclusion. Settled 29 Jul 2026; see STATE.md checkpoint. |

**No irreconcilable conflict was found.** Every divergence above is an extension
or a sequencing change, and none lowers a bar or discards a prior finding.

---

## Status of section 0 at the time of recording

Discharged in the session of 29 July 2026, before this file was written:

- PROGRAMME.md, STATE.md, HANDOVER.md and GATE-REVIEW.md read in full.
- `git status --porcelain` empty; `git log --oneline main..HEAD | wc -l` = **52**;
  `main` = `origin/main` = `6daacd2d`; branch absent from `git ls-remote`.
- **All eight gates re-measured personally, all green:** `pytest tests/ -q`
  **2416 passed rc=0** (22m16s); `tests/test_classification.py` **1386 passed,
  0 failed, 0 skipped** rc=0 (19m53s); `claim_auditor.py --verify-facts` rc=0;
  `site_integrity.py` rc=0; `cascade_count.py --check` rc=0 (canonical 2,416);
  `build_recall_artefact.py --check` rc=0; `build_gap_demo.py --check` rc=0;
  `check_selfref_sourcing.py --control-only` rc=0 with the control firing both ways.
- Three prose figures in HANDOVER.md were found not to reproduce and are
  recorded in the STATE.md checkpoint of the same date.

---

## DIRECTIVE BODY (verbatim)

REGULA PROGRAMME v3 — SCAFFOLDING REFRESH, EXTENDED SCOPE, UNCHANGED DISCIPLINE
0. SESSION PROTOCOL — execute before anything else

Read docs/improvement/PROGRAMME.md, then STATE.md (resume file), then HANDOVER.md. Re-measure before trusting prose: git status, git log --oneline main..HEAD | wc -l, and every gate in HANDOVER §9. Write this directive to docs/improvement/DIRECTIVE-v3.md and record in STATE.md that v3 extends PROGRAMME.md rather than replacing it. Where v3 and PROGRAMME.md conflict, PROGRAMME.md's principles win and the conflict is logged.

1. WHAT THIS IS NOT

This is not a restart. Phase 2 failed at loop 1/3; Phase 4 failed at loop 2/3. Those failures produced the programme's most valuable artefacts: 24 loop-1 objections, 18 loop-2 MAJORs with dispositions, the FP taxonomy, the recall decomposition (33/47/63/53% by path), the trace targets, the instrument-error record. Discarding any of it is forbidden. New research is absorbed into the existing gates; it does not reset them. If any instruction here reads as "start the research/plan/implement cycle over," interpret it as "extend the existing cycle with new inputs."

2. THREE RECONCILED CONSTRAINTS (owner-directed; these resolve real contradictions)
"No tech debt" means no new unlogged debt. The quarantine, the shrink-only ratchet and dated annotations are approved debt ledgers and remain. Debt that is tracked, shrinking and visible is compliant; debt that is silent is not.
"Nothing is deprioritised" means nothing is silently dropped. Every finding gets a written disposition and a home — fixed, ledgered, or explicitly deferred with a reason. Scope fences and loop caps remain; they are how the programme avoids drift, and they are not deprioritisation.
"Do not suppress anything" means suppression must be chosen and justified. This is the F30 finding stated as a rule: 61 claims invisible to the gate "for a reason nobody chose" is exactly the failure. Every suppression mechanism — allowlist, quarantine, citation-word sourcing, the 0.5 floor — needs an explicit, tested, documented rationale or it goes.
3. SOURCE HIERARCHY — binding, and the reason this directive exists

You will receive two research sweeps (27 July, 29 July) and a validation document. Research sweeps are lead generators. Primary sources are truth. Evidence of why: the 29 July sweep reintroduced the agentic-AI claim this programme had already killed by EUR-Lex retrieval, and downgraded Colorado from settled fact to "conflicting accounts." Drift runs both ways.
Rules: (a) no claim from any sweep enters a Regula artefact without primary-source verification, recorded with retrieval date; (b) the validation document supersedes the sweeps where they conflict; (c) every 2026 arXiv identifier must be verified to exist and its status (preprint vs peer-reviewed) confirmed at the source before citation — treat all as unverified until checked; (d) where the validation says "could not verify," that is a task, not a conclusion.

4. CORRECTION LAYER — apply before any new work

Verified corrections to be applied and recorded:

Colorado: SB 26-189 signed 14 May 2026, effective 1 Jan 2027, repeals and replaces SB 24-205. Two further 2026 statutes exist (HB 26-1263 Chatbot Safety Act; a health-care AI law), both effective 1 Jan 2027 — assess whether they belong in the crosswalk. Enforcement stayed (xAI v. Weiser, 27 Apr 2026); AG will not enforce either statute pending rulemaking. Verify each against the Colorado General Assembly primary text before publishing.
EN 18286: approved by CEN-CENELEC 12 July 2026, published as EN 18286:2026. Any Regula statement that it is "at formal vote" or "unpublished" is now false. The distinction that must be preserved everywhere: published ≠ OJ-cited; only Official Journal citation confers Article 40 presumption of conformity.
ISO/IEC 42005:2025 and 42006:2025: both published; 42005 is impact assessment, 42006 is certification-body requirements (some secondary sources conflate them — do not). Also published: 42007, 12792:2025, TS 6254, TR 20226. Investigate ISO/IEC TR 42106 (differentiated benchmarking of AI system quality characteristics, under publication 2026-04) — it bears directly on the benchmark work.
The 2 August 2030 date: real, but from Regulation (EU) 2024/1689 Article 111(2), not from the Omnibus. Recital 39 of 2026/1744 clarifies that grace period's scope without changing the date. Both the prior STATE.md finding and the sweep are correct under different framings; record it that way.
RE-OPEN the agentic-AI item. STATE.md closed it as "no agentic-AI category or definition exists; nothing may be added." Primary text contradicts the existence half: recital 43 establishes AIH horizontal technology codes; Article 1(16) amends Article 30(2) to reference Annex XIV; recital 45 empowers delegated acts amending Annex XIV. Task: fetch Annex XIV from EUR-Lex directly and record what AIH 0401 actually says — two careful secondaries disagree ("agentic AI" vs "emerging technologies"). Then decide whether the OWASP Agentic crosswalk gains a legitimate regulatory hook. Whatever you find: it is a nomenclature code, not a definition, and carries no obligations — say so wherever it appears.
5. NEW PHASE 1.7 — SCAFFOLDING AND GUARDRAIL REFRESH (runs before Phase 2 resumes)

The programme's rules were written days ago and have since been proven partly wrong by its own findings. Rebuild them against verified 2026 practice.

Audit current scaffolding: .claude/rules/ (git, measurement, tests, python-scripts, quality-standards, regulatory-content, site-html), .claude/commands/, .claude/skills/, subagent charters. For each: is it loaded, is it obeyed, has it prevented a real failure, and is there a recorded instance where it should have and didn't?
Apply the self-verification literature. Verify each citation first, then apply. The load-bearing claim across it — LLMs cannot reliably self-correct or self-assess, and self-assessment calibration degrades after seeing one's own output — is the theoretical account of every failure this programme has recorded: the 8-of-14 table, the false blog "discrepancy," the guard narrower than its own standard, the three pre-flagged closures that failed on merit. Encode the response structurally: independent critic subagents that never see their own prior justifications, and gates external to the thing being gated.
Context-compaction risk: research and record whether governance constraints survive compaction in this setup. If constraint-pinning or equivalent is verified practice, adopt it. This programme has crossed multiple context resets already and STATE.md is the only thing that carried.
Deliverable: revised rules committed and loaded, plus docs/improvement/SCAFFOLDING-AUDIT.md recording what changed, why, and which recorded failure each change would have caught. No rule ships without naming the failure it prevents.
6. THE EXISTING QUEUE — unchanged, runs next

Re-derivations of Trust and Detection at HEAD under one written rule (resolving BASELINE §11's 90-vs-88 self-contradiction) → the traces for the 8 unexplained recall misses and the 6-fixture scanner/classifier divergence, path-labelled → Phase 4 plan revision against §F and both loops' dispositions → loop 3 in a fresh session with the closure-verification brief. Loop 3 fails → escalate the irreducible list; do not spend it under context pressure.
F25 remains the most urgent live defect: the landing page's meta claim is falsely sourced right now by the word "Source" in a <title> tag, on a public surface. And the validation confirms F25 is larger than recorded — CITATION_WORDS also contains "see" and "ref". Scope it against the complete picture, not the partial one.
CI has never run on this branch. claim_auditor --diff-base is red on TRUST.md and MODEL_CARD.md and will fire on first push. Resolve before any merge is contemplated.

7. NEW SCOPE — sequenced after the Phase 4 gate, prepared before it

These are the transcript's genuine additions. Preparation (inventory, audit, plan) may run in parallel; execution waits for the gate, because publishing through a gate that is still being repaired is what Phase 1.5 exists to prevent.

7a. Repository. Full inventory before any deletion: every file classified needed / superseded / never-public. Purge only after the inventory is complete and reviewed — provenance and auditability must survive (this project's own evidence story depends on it, so git filter-repo-class operations need explicit owner approval). Structure to current conventions; governance files complete; SPDX headers; run OpenSSF Scorecard in CI and pursue the Best Practices passing badge — noting that silver/gold are structurally gated by single-maintainer status, which is a finding to record, not a failure to hide. Nothing competitive or personal enters the public repo; the getregula-internal/ boundary already established stands.

7b. Website. Playwright-based audit: crawl, journey testing, link and content integrity, @axe-core/playwright for WCAG 2.2, Lighthouse CI for Core Web Vitals. Record that only ~30% of WCAG criteria are machine-testable — automation supplements human judgement, never replaces it. Restructure documentation on Diátaxis to serve both audiences: tutorials and how-to for CLI implementers, reference and explanation for compliance and legal buyers.
GEO, evidence-based only. Verified: Google's guidance (15 May 2026, updated 15 June) says no special files are needed and Search ignores llms.txt; Ahrefs found 97% of llms.txt files get zero traffic. Regula already ships llms.txt and llms-full.txt — keep them as near-zero-cost maintenance for Claude, Perplexity and coding agents, never as a Google lever, and never as a substitute for content. The verified lever is what Google actually names: original data, first-hand experience, real case studies, server-rendered HTML (AI crawlers largely don't run JavaScript). Note the convergence: Regula's benchmark corpus, honest precision/recall figures and regulatory delta-log are simultaneously the moat and the GEO strategy. Build the artefact once, publish it well.

7c. Consultant packaging. This targets delivered-value evidence — the rubric's weakest dimension at 8/100 and the one no code work moves. Map Regula's existing evidence outputs (Annex IV packs, SHA-256 manifests, Ed25519 signing, RFC 3161 timestamping, Annex VIII packets) to what buyers purchase: system inventory and risk classification (Art. 6), data governance (Art. 10), technical documentation (Art. 11), record-keeping (Art. 12), transparency (Art. 13), human oversight (Art. 14). Deliverable is a packaged offer, not a claim of traction. Where market or rate data is unavailable, say so — do not estimate.

8. MOAT — build durable, not clever

Rank by what survives cheap replication: judgment-labelled data (c) > institutional credentials (e) > citable artefacts (d) > decaying-currency knowledge (b) > code (a). A competitor matched two differentiators in weeks; that is the empirical proof that features are the weakest tier. Priority order for this programme: the multi-annotator labelled corpus with proper agreement statistics and a Croissant + datasheet dataset record; the head-to-head benchmark nobody has yet run; the regulatory delta-log; standards participation. Verify every methodology citation before adopting it — including the agreement-statistic and dataset-documentation standards, which the validation could not confirm.
Genuinely sparse terrain, worth a short citable write-up: self-referential measurement error — an instrument whose corpus contains itself. This programme has already produced a documented live instance (the handover's §10 figures invalidated by its own rewrite, violating the rule the same document states). Search first for prior formal work; if it genuinely doesn't exist, that is a contribution.

9. OWNER ITEMS — prepare, never execute

Five decisions are blocking and go in the next review pack: the quarantine sensitivity-admissions mechanism; the F14 deviation on Articles 11 and 12; F25 and F30 scoping (F25 is larger than written — present the complete picture); F29's 387-vs-386 and whether the blog's 389 gets corrected; the DE/PT-BR provenance sentence.
Flag to the owner immediately, as a same-day item: prEN 18228 (AI Risk Management) and prEN 18282 (Cybersecurity Specifications for AI Systems) close public enquiry on 30 July 2026; prEN 18229-1 (Trustworthiness Framework, Logging) closes 20 August 2026. Public comment is the cheapest available route to standards participation without committee membership. Verify these windows against CEN-CENELEC directly before the owner acts.
Also standing: DPVCG post, raters 2 and 3, Zenodo/DOI and licence decision, BSI ART/1, GSC re-auth, private remote for getregula-internal/, and the 1.5b residuals.

10. STANDING DISCIPLINE

Evidence tags on every material claim. Measured-over-embedded, including over this directive. Loop caps of 3 with honest escalation. Independent subagent charters. Nothing on main. No public-surface change without owner approval. Comprehensiveness over speed — and where they genuinely conflict, say so rather than choosing silently. Record your own errors in place rather than deleting them; the record of what went wrong is why this programme's numbers can be trusted at all.
