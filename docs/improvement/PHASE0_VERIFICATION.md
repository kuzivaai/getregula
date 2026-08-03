# Phase 0 Verification Report: Research Sweep 2026-07

> **RELOCATED AND PARTIALLY REDACTED, 28 July 2026.** This file was
> `.claude/phase0-verification-2026-07.md`, which was untracked and would
> not have survived a `git clean`. It is now tracked. **Section E
> ("Competitive-intelligence updates") has been removed** because this is
> a public repository and that section carries competitor pricing, star
> counts, and Regula's absence from a competitor's comparison page,
> gathered as positioning material. The repository's own `.gitignore`
> already treats competitor analysis as not-public. The removed section is
> held verbatim outside the repository at
> `getregula-internal/competitive-intelligence-2026-07.md`. One repo action
> item that was buried in it has been preserved in `OWNER_ACTIONS.md`
> rather than lost. **Nothing else in this document has been altered.**
> Competitor names elsewhere in this file are deliberately kept: the repo
> already names its comparison set publicly in
> `benchmarks/headtohead/PREREGISTRATION.md` and `adapters.py`.

Date: 27 July 2026. Evaluator: research-eval second pass, independent of the
sweep's author. Scope: every load-bearing claim in the owner-supplied research
sweep (held internally at `getregula-internal/research-sweep-2026-07.md`,
plus its full text) plus the sweep's claims
about Regula itself. Method: primary-source verification (arXiv abstracts,
EUR-Lex, publisher pages, GitHub, vendor pages), repo greps for self-claims,
and a deliberate falsification pass on the white-space premises.

VERDICT: **PASS WITH CORRECTIONS.** The programme's load-bearing premises
survive. The sweep as written must NOT be cited directly; cite only through
the corrections below. Quote fidelity failed on two items (see Issues 1-2).

## Score table (research-eval criteria)

| Criterion | Score (1-5) | Notes |
|---|---|---|
| Statistical Accuracy | 4 | Core numbers verified verbatim; several sub-numbers unverified (listed) |
| Quote Fidelity | 3 | Two quoted passages not confirmed verbatim at source (CodeRabbit, DAOnt) |
| Competitive Completeness | 4 | Dossier already covers ark-forge/Systima; ARQNXS newly surfaced (minor) |
| Policy/Regulatory Accuracy | 4 | Dates verified vs primaries; agentic-AI category CONTRADICTED by EUR-Lex text; SMC thresholds mislocated |
| Recency | 5 | prEN 18286 is fresher than the sweep states (now at Formal Vote) |
| Chronological & Self-Claim Accuracy | 4 | 33% figure needs N=6 caveat; "6 regex-only languages" is 5; SecVulEval venue is 2026 not 2025 |
| **Overall** | | **PASS with mandatory corrections** |

## A. Regula self-claims (verified against repo, 27 Jul)

| Claim | Verdict | Evidence |
|---|---|---|
| N=115 corpus, blind-labelled | VERIFIED | benchmarks/README.md; BLIND_LABELS.json (201 labels, 115 production-code); labels carry NO labeller attribution -> single-labeller premise stands |
| 33% high-risk precision | VERIFIED WITH MANDATORY CAVEAT | It is N=6; README calls it "statistically unmeasurable at this sample size"; overall precision 83.5% (N=115, v1.7.4). NEVER cite 33% without N=6. |
| SARIF output | VERIFIED | cli_scan.py, report.py |
| DPV-AIAct JSON-LD export | VERIFIED | scripts/dpv_export.py, cmd_dpv, evidence artifact 09-dpv-aiact.jsonld |
| "6 regex-only languages" | CORRECTED: **5** | TRUST.md/architecture.md: Python + JS/TS full AST; Java/Go/Rust/C/C++ regex-only. 8 languages total |
| 13 crosswalks | VERIFIED | framework_mapper._FRAMEWORK_KEYS = 13 keys |
| Delta-log content exists | VERIFIED | content/regulations/delta-log/: schema.json, feed.xml, index.json, 10 entries 2024-07-12 -> 2026-07-24 |
| Ed25519 / RFC 3161 / CycloneDX 1.7 ML-BOM | VERIFIED | signing.py, timestamp.py, sbom.py (specVersion "1.7") |
| AIR Blackbox ML-DSA-65 | VERIFIED-PER-DOSSIER | Dossier 27 Jul (itself research-eval'd); not re-verified against their repo this pass |

## B. Academic anchors

VERIFIED VERBATIM (safe to cite with the numbers given):
- **CASTLE** arXiv:2503.09433 — 13 SA tools, 10 LLMs, 2 FV tools, 250 micro-benchmarks, 25 CWEs, CASTLE Score. (TASE 2025 / Springer DOI not separately confirmed; arXiv confirmed.)
- **PrimeVul** arXiv:2403.18624, ICSE 2025 — dedup + chronological split; "a state-of-the-art 7B model scored 68.26% F1 on BigVul but only 3.09% F1 on PrimeVul". (oneFunc/nvdCheck names not in abstract; body-level detail.)
- **Risse/Liu/Böhme** arXiv:2408.12986, ISSTA 2025 — function-level labels need calling context; "9 in every 10 papers... function-level binary classification".
- **Li et al. FSE 2023** DOI 10.1145/3611643.3616262 — 7 tools from 161; 12.7% real-world detection; 70.9% undetected combined.
- **QASecClaw** arXiv:2605.01885 — F1 78.39%->90.93%, FP 560->64 (-88.6%), recall -3.1%, OWASP Benchmark v1.2, 2,740 Java cases, 11 CWEs, Mission Orchestrator. **Authors: Ameen, Ul Alam, Islam** (sweep's "Islam, A." is wrong first-author).
- **IRIS** arXiv:2405.17238 (Li, Dutta, Naik) — CWE-Bench-Java 120 vulns; CodeQL 27 vs IRIS+GPT-4 55. (ICLR 2025 not shown on arXiv page; plausible, unconfirmed.)
- **Tencent SEIP** ICSE 2026 SEIP, arXiv:2601.18844, DOI 10.1145/3786583.3786910 — 433 alarms (328 FP/105 TP); "hybrid... eliminate 94-98% of false positives with high recall". (Sub-numbers 0.93-0.94 acc, $0.0011-0.12/alarm, CoT-underperforms: UNVERIFIED at abstract level — read the paper before citing.)
- **GadgetHunter** FSE 2026 (PACMSE), Li/Zhang/Wang/Chen/Cao/Zhang/Liu — 197 previously unknown gadget chains; FN -32%, FP -12-85%. ("4 CVEs" unconfirmed.)
- **MoCQ** arXiv:2504.16057 — neuro-symbolic, 12 vuln types, 4 languages (C/C++, Java, PHP, JS); 46 new patterns, 25 unknown vulns.
- **AdaTaint** arXiv:2511.04023 — LLM source/sink + FP mitigation; -43.7% FP, +11.2% recall.
- **ZeroFalse** arXiv:2510.02534 — exists as described. (SARIF/CodeQL specifics not in abstract.)
- **DPV 2.0** arXiv:2404.13426, ISWC 2024, authors incl. Pandit/Esteves/Golpayegani — confirmed.
- **DPVCG issues #199 and #229** — BOTH OPEN. #199 "Adding concepts from the EU General-Purpose AI Code of Practice" (labels: eu-aiact, help-wanted, todo; milestone dpv v2.4). #229 "Update EU-AIAct extension with practical concepts" ("representing more of AIAct itself"). The open-door premise for upstream contribution is CONFIRMED.
- **AIRO** SEMANTiCS 2022, Golpayegani/Pandit/Lewis — confirmed (title says "ISO Risk Management Standards", based on ISO 31000 series).
- **KG mapping** arXiv:2408.11925 Hernandez/Golpayegani/Lewis — confirmed.
- **CLSR obligation-extraction** S2212473X25001026 — confirmed (GDPR + DSA + AI Act; LLM+KG). Repo github.com/thiagordp/obligation_extraction_for_compliance EXISTS (no description; link to paper unconfirmed from repo page).
- **CLSR semantic frameworks** S2212473X26000568 (Apr 2026) — confirmed; uses AIRO/VAIR, SHACL + N3 automated high-risk/prohibited rule-checking. STRATEGIC: adjacent prior art for any ontology-driven classifier claim; cite, do not claim novelty over it.
- **SUSVIBES** arXiv:2512.03262 (Zhao et al.) — "61% of the solutions from SWE-Agent with Claude 4 Sonnet are functionally correct, only 10.5% are secure"; hints don't fix. 200 tasks.
- **SecureVibeBench** ACL 2026 Main, aclanthology 2026.acl-long.1107, arXiv:2509.22097 — confirmed; 105 C/C++ tasks (OSS-Fuzz/ARVO); best agent only 23.8% correct+secure (useful extra figure).
- **Veracode 2025 GenAI Code Security Report** — 45% of samples failed security tests; Java worst at 72%; 80 tasks, 100+ LLMs; report July 2025 + Oct 2025 update + Spring 2026 update exists. (Sweep said "March 2026 update... ~55% flat": direction confirmed by the Spring 2026 update; exact figure unverified.)
- **Spracklen et al.** USENIX Security 2025, arXiv:2406.10279 — VERBATIM: "205,474 unique examples of hallucinated package names"; "at least 5.2% for commercial models and 21.7% for open-source models"; 576,000 code samples. **The 2.23M / 440,445 / 19.7% / 43% figures are secondary-reported, NOT verified against the paper (PDF 403s). Do not cite them until read.**
- **ISO/IEC 42005:2025** — published May 2025 (sources vary Apr-Jun). Confirmed real.
- **NIST IR 8596** Cyber AI Profile — preliminary draft 16 Dec 2025, 45-day comment to 30 Jan 2026. Confirmed.
- **NIST CAISI AI Agent Standards Initiative** — launched 17 Feb 2026, three pillars. Confirmed. (CI-profile concept note 7 Apr 2026: unverified detail.)
- **CycloneDX 1.7** — shipped March 2026; ECMA-424 2nd edition Dec 2025. Confirmed.
- **EO 14365** — "Ensuring a National Policy Framework for Artificial Intelligence", signed 11 Dec 2025; AI Litigation Task Force; Commerce 90-day review. Confirmed.
- **Almada et al.** IIC, DOI 10.1007/s40319-025-01672-8 — confirmed; first English study of its kind; copyright/TDM scope.

CORRECTED OR DOWNGRADED:
1. **CodeRabbit Dec 2025 (QUOTE FIDELITY FAIL).** Verified on the blog: 470 PRs (320 AI-co-authored / 150 human-only); 10.83 vs 6.45 issues per PR; "Security issues were up to 2.74x higher" (GENERAL security, not XSS-specific on the source page). The sweep's quoted "2.74x more cross-site scripting vulnerabilities, 1.91x more insecure direct object references, 1.88x more improper password handling" is NOT confirmed verbatim; 1.91x/1.88x appear nowhere on the source page. Cite: "up to 2.74x more security issues; ~1.7x more issues overall".
2. **DAOnt** arXiv:2604.16386 (QUOTE FIDELITY FAIL + MISCHARACTERISED). It is a formal ontology for the EU **Data Act** (Leyva-Sánchez et al.), not AI-Act change tracking; the quoted "focus predominantly on GDPR and AI Act requirements" is not in its abstract. Drop this citation from the delta-log rationale.
3. **BenchVul/TitanVul** arXiv:2507.21817 (MISREAD). Actual title: "Out of Distribution, Out of Luck..." (Li, Yikun et al., 19 authors). 20-71% label inaccuracy CONFIRMED. But "seven independent experienced researchers verify" is a misread of "aggregating seven public sources" (TitanVul, 38,548 functions). The ~50-samples-per-CWE detail unconfirmed.
4. **SecVulEval** — venue is **AIware 2026** Benchmark & Dataset Track (3rd ACM Conf. on AI-Powered Software), DOI 10.1145/3805760.3814932 confirmed; arXiv:2505.19828. Sweep said AIware 2025. Scope: C/C++, 25,440 functions / 5,867 CVEs confirmed; "145 CWEs" unconfirmed. Best agent F1 23.83% for vulnerable-statement detection.
5. **Kappa precedents (BOTH SHAKY).** arXiv:2511.16123 is a DIFFERENT paper (TVD key-aspect synthesis, Han et al.) — MISATTRIBUTED; no NVD/CWE kappa study found at that ID. arXiv:2604.04288 exists and matches topic (GitHub Security Advisories, Shifat et al.) but Cohen's kappa 0.76 / Gwet's AC1 0.95 NOT confirmed from the abstract. The multi-annotator design stands on PrimeVul + Risse + SecVulEval methodology; find proper IAA precedents during Phase 1 design.
6. **ComplianceNLP** arXiv:2604.23585 (MISCHARACTERISED). Real, but it is SEC/MiFID II/Basel III financial-regulation gap detection (Guo/Wu/Yiu, ACL 2026 Industry Track per page), not AI-Act. COLING 2025 reference unconfirmed. Weak relevance; drop from load-bearing set.
7. **LGGT+** arXiv:2603.28558 — exists (single author Adam Laabs; T-norm EU AI Act classification; T_G 84.5% accuracy). "TemporalKnowledgeNode"/"OntologyPatcher" component names NOT confirmed from abstract. Cite the t-norm result only.
8. **Korea survey** arXiv:2512.02046 (MISATTRIBUTED). It is "Global AI Governance Overview" (Kyrychenko/Mudryi/Chaklosh) and does NOT specifically cover Korea's Act. Drop as Korea support; the Korea sparsity claim stands on the absence-of-results searches instead.
9. **QASecClaw authorship** — Ameen, Ul Alam, Islam (not "Islam, A." as lead).

## C. Regulatory claims

| Claim | Verdict | Evidence |
|---|---|---|
| Reg (EU) 2026/1744, 8 Jul 2026, OJ 24 Jul, in force 27 Jul | **VERIFIED-PRIMARY** | EUR-Lex ELI eng page fetched 27 Jul (automated fetch of the actual text; recital 46 confirms third-day entry). Closes the handover Section 4a residual subject to owner eyeball. |
| Annex III deferral to 2 Dec 2027; Annex I to 2 Aug 2028 | VERIFIED-PRIMARY | Recital 40 quoted verbatim in fetch |
| New Art 5 prohibitions (nudification/CSAM) | VERIFIED-PRIMARY | New points (ba)/(bb) confirmed in text. The "2 Dec 2026" application date NOT confirmed from the excerpt. |
| Art 50(2) legacy marking from 2 Dec 2026 | CONSISTENT-UNCONFIRMED | Recital 38: four-month transitional period for providers on market before 2 Aug 2026 (2 Aug + 4 months = 2 Dec 2026). Article text not in excerpt. |
| SME/SMC lighter documentation | VERIFIED-PRIMARY | Amended Art 11(1); Art 3(14a) SME per Rec 2003/361/EC; Art 3(14b) SMC per Rec (EU) 2025/1099 point (2). **The "<750 employees / <EUR 150M" thresholds are NOT in the regulation** — they come from the SMC recommendation; never present them as AI-Act text. |
| **New agentic-AI category** | **CONTRADICTED (pending full-text)** | EUR-Lex fetch affirmatively found no agentic-AI definition or category. The one secondary claiming "AIH 0401" looks like SEO garbage. DO NOT add agentic-category copy to Regula from this sweep. Full-text human read before any reversal. |
| Public-authority systems by 2 Aug 2030 (Art 111(2)) | SUPPORTED-SECONDARY | Multiple secondaries (incl. lawandtechnology.eu); article not in fetched excerpt. Verify in full text before shipping copy. |
| Colorado SB 26-189 signed 14 May 2026, effective 1 Jan 2027 | VERIFIED | Polis signed 14 May 2026; repeals/replaces SB 24-205 (which was to take effect 30 Jun 2026); ADMT + "materially influence" standard; drops duty of care/RMP/impact assessments; notice + 30-day adverse-outcome explanation + human review |
| xAI v. Weiser stay | VERIFIED | Filed 9 Apr 2026 (D. Colo., 1:26-cv-01515 per Clearinghouse); DOJ moved to intervene 24 Apr; joint motion same day; **court granted 27 Apr 2026, suspending enforcement**. AG delaying enforcement (StateScoop); "standstill" (Privacy World). EO 14365 confirmed as the federal backdrop. SHIPPING FIX: Regula's Colorado copy must carry the stay + SB 26-189 transition. |
| Korea AI Basic Act in force 22 Jan 2026 | VERIFIED | First comprehensive framework; Enforcement Decree took effect same day; MSIT 99-task plan + 326 recommendations (2nd plenary Feb 2026); **penalties deferred one year (grace period)** — extra nuance Regula's Korea copy should carry; 10^26 FLOPs threshold |
| Brazil PL 2338 in Chamber since Mar 2025 | VERIFIED | Sent 17 Mar 2025; Special Commission (Canziani presiding, Ribeiro rapporteur); awaiting rapporteur's opinion; 12 public hearings May-Sep 2025; final vote expected 2026 |
| prEN 18286 at Enquiry/Formal Vote; Q4 2026; Oct 2025 acceleration | VERIFIED AND FRESHER | Public Enquiry CLOSED, comments reviewed, **now out for Formal Vote**; FprEN 18286 and "EN 18286:2026" designations exist in catalogues; CEN acceleration decision 23 Oct 2025 confirmed; 10 normative clauses, 5 informative annexes; compatible ISO 9001/13485/42001. OJEU-citation-confers-presumption point confirmed. |
| prEN 18228 (risk mgmt) / prEN 18283 (bias) | NOT CHECKED THIS PASS | Verify when aligning Annex IV packs |

## D. White-space premises (falsification pass, all survive)

1. **"EU AI Act code scanning" peer-reviewed literature: HOLDS.** Found tools (AIR Blackbox, Systima, ark-forge, SonnyLabs, Regula itself) and adjacent papers (GenAI-vs-human-experts compliance checking, Springer Discover AI Apr 2026 — document-level, not code scanning; arXiv:2604.04604 compliance architecture — preprint), but NO peer-reviewed study of static code scanning for AI-regulation compliance. The white space is real. Adjacent-prior-art caveat: cite the Springer paper and CLSR semantic-frameworks paper as related work, scoped as not-code-scanning.
2. **Korea English peer-reviewed technical-compliance scholarship: HOLDS.** Only law-firm/business grey literature surfaced. (The sweep's own supporting citation 2512.02046 was misattributed, but the premise stands on the searches.)
3. **Machine-readable AI-Act delta tracking: HOLDS, NARROWED.** Nothing publishes AI-Act deltas machine-readably. But adjacent: OSCAL-based AI compliance evidence (arXiv:2604.13767), Policy Cards (arXiv:2510.24383, crosswalks to NIST/ISO/EU AI Act), commercial reg-change platforms (Regology etc.). The delta-log publication must position against these and could offer an OSCAL mapping as a bridge.
4. **"No head-to-head has ever been run": HOLDS.** Nothing found; dossier line 179 agrees.

## E. Competitive-intelligence updates — REDACTED FROM THE TRACKED COPY

Three bullets removed on 28 July 2026 when this file moved into a public
repository. They recorded, as of fetches dated 27 July 2026: a competitor
comparison page and the tools it lists, a competitor's pricing, licence,
commit and star counts with a note that its remediation roadmap is stale
post-Omnibus, and the finding that Regula is absent from that comparison
page. All three were gathered as positioning material.

Held verbatim, unredacted, at
`getregula-internal/competitive-intelligence-2026-07.md`.

**Preserved from the removed section**, because it is a repo action item
and not competitive intelligence: a search-index snippet for
getregula.com seen on 27 Jul 2026 showed "398 risk patterns, 12
frameworks" against the canonical 419/13 in `data/site_facts.json`. The
live pages are correct (grep found no stale copies), so this is an
external index cache, **but it raised an untested question: does
`claim_auditor` sweep meta descriptions?** Carried into `OWNER_ACTIONS.md`
so the split does not lose it.

## F. Mandatory usage rules derived from this pass

1. Never cite the 33% figure without "(N=6; statistically unmeasurable at that sample size; overall 83.5%, N=115)".
2. Never quote the CodeRabbit XSS/IDOR/password multipliers; use "up to 2.74x more security issues; ~1.7x more issues overall (470 PRs)".
3. Never present "<750 employees / <EUR 150M" as AI-Act text; the SMC definition is by reference to Recommendation (EU) 2025/1099.
4. No agentic-AI-category copy anywhere in Regula until the full 2026/1744 text is human-read and it is found (currently contradicted).
5. Use Spracklen's verbatim-verified numbers only (205,474 unique; 5.2%/21.7%) until the paper is read for the totals.
6. Drop DAOnt, ComplianceNLP, and arXiv:2512.02046 from load-bearing citation lists; drop arXiv:2511.16123 entirely (wrong paper).
7. SecVulEval venue is AIware 2026; QASecClaw is Ameen et al.; BenchVul's "seven" is sources, not researchers.
8. "5 regex-only languages", not 6.
