# Phase 2 — validation cards

Built 28 July 2026 from **primary-source retrieval**, not from the owner
sweep. The sweep at `getregula-internal/research-sweep-2026-07.md` is
treated as a **lead generator, not a source**: primary retrieval has
falsified it twice already (no agentic-AI category in Reg (EU) 2026/1744;
no 2 Aug 2030 date). No card cites it.

**Inheritance from `PHASE0_VERIFICATION.md`:** stated per card. Several
items were verified there on 27 Jul; where this pass re-retrieved and
agreed, the card says INHERITED-AND-RECONFIRMED. Where this pass found
something the earlier pass did not record, the card says NEW.

**Evidence tags** per PROGRAMME.md principle 1.

**Provenance of this pass, stated honestly.** Retrieval was performed by
two subagents with restricted inputs. Project rule: subagent output is not
verified by default. I independently re-fetched the two most load-bearing
corrections (items C4 and C2 below) against arXiv and both held. **The
remaining per-paper numbers carry the retrieval agents' evidence and are
tagged REPORTED-UNVERIFIED where I did not personally re-fetch them.** They
must not be published on any surface without a second check.

---

## PART A — the question these cards must answer

Three measured gaps, from Phase 0/1:

- **The five semantic FP classes** (`fp_taxonomy.json`): generative-model
  infra read as critical infrastructure (7), non-production paths (6),
  domain-word collision (4), compute-vs-human homonyms (4), modality
  confusion (3). **All 24 high-risk FPs are semantic, not lexical.**
  Consequence already measured: regex tightening cannot fix this class
  without destroying recall. **Any candidate whose lever is "better
  regexes" is presumptively weak and must argue its way in.**
- **F5:** 183 of 391 tier regexes (46.8%) are exercised by no test input.
- **F11:** precision corpus is Python-only; recall never measured.
  (Partly addressed 28 Jul: see the synthetic baseline, high-risk recall
  4/5 with one constructed miss.)

---

## PART B — FP-reduction / semantic-verification candidates

### B1. Tencent industrial study — arXiv:2601.18844
- **Citation:** Reducing False Positives in Static Bug Detection with LLMs:
  An Empirical Study in Industry. Du, Feng, Zou, Xu, Ma, Zhang, Liu, Peng, Lou.
- **Status: PEER-REVIEWED**, ICSE 2026 SEIP track. VERIFIED via the official
  ICSE 2026 site. **The arXiv page carries no venue at all** — anyone
  citing arXiv alone cannot establish this.
- **Numbers (REPORTED-UNVERIFIED, abstract-level):** 433 alarms (328 FP,
  105 TP); "94-98%" FP elimination; $0.0011-$0.12 and 2.1-109.5s per alarm;
  vs 10-20 minutes manual inspection.
- **Claim relied on:** hybrid static-plus-LLM triage removes most false
  alarms at cents-and-seconds cost on *real proprietary code*.
- **Applicability test (falsifiable):** run the adjudicator over the 24
  measured high-risk FPs and the synthetic positives. **Adopt only if it
  removes ≥50% of the 24 while losing 0 of 5 synthetic prohibited and ≤1
  of 5 high-risk.** Fails that → reject.
- **Domain shift:** the studied bug types are decidable from local program
  facts. **No EU AI Act determination is.** The 94-98% is a function of
  their 76% FP base rate and must not be carried across — that is the
  population-transfer error this project has a standing rule against.
- **Offline:** NO. Network per alarm. Optional extra only, per constraint 4.
- **Clonability:** (a) code. Defensive value only.
- **Rubric:** Detection efficacy, range **+0 to +6**, wide because the
  transfer is untested.
- **Verdict: ADOPT AS OPTIONAL TIER, gated on its own applicability test.**

### B2. MoCQ — arXiv:2504.16057
- **Citation:** Neuro-symbolic Static Analysis with LLM-generated
  Vulnerability Patterns. Li, Yao, Korich, Luo, Yu, Cao, Yang.
- **Status: PREPRINT, no venue found** (dblp returns zero hits for the
  title). REPORTED-UNVERIFIED.
- **Why it matters more than its status suggests:** it is the **only
  candidate whose architecture survives the offline constraint intact** —
  LLM at *authoring* time, deterministic execution at *scan* time.
- **Applicability test:** use an LLM offline to author *discriminative*
  rules separating Annex III "critical infrastructure" from model-serving
  infrastructure. **Adopt only if the generated rules cut the 7
  generative-infra FPs without losing synthetic recall.**
- **Honest mismatch, stated:** MoCQ solves a pattern-*authoring* problem.
  This project's measured conclusion is that pattern-level work cannot fix
  semantic FPs. Its runtime targets (Joern, CodeQL) violate stdlib-only.
  **The transferable idea is the offline-authoring split, not the system.**
- **Offline:** YES at scan time; NOT stdlib-only as published.
- **Rubric:** Detection efficacy **+0 to +3**.
- **Verdict: ADOPT THE PATTERN ONLY** (offline authoring), not the system.

### B3. AdaTaint — arXiv:2511.04023
- **Status: PREPRINT.** Single author, no institutional affiliation on the
  abs page, no venue, no code link, and **unrendered LaTeX escapes in the
  arXiv abstract metadata**, indicating an unproofread submission.
- **The one durable idea:** never let the LLM be the final authority; make
  it *propose* and validate the proposal against hard facts. For a
  regulatory product, where non-determinism is a far bigger problem than in
  a bug finder, that principle is the answer to the obvious objection.
- **Numbers: DO NOT CITE.** The -43.7% / +11.2% figures are abstract-level
  from a low-credibility preprint and were not read in the PDF.
- **Verdict: ADOPT AS A DESIGN PRINCIPLE. Cite no numbers.**

### B4. ZeroFalse — arXiv:2510.02534 · B5. QASecClaw — arXiv:2605.01885
- **Both PREPRINT** (dblp: CoRR only). REPORTED-UNVERIFIED.
- ZeroFalse's transferable claim: **per-CWE prompting beats generic
  prompting.** Maps onto the FP taxonomy, where each of the five classes
  needs a *different* disambiguation question. That is a design input.
- QASecClaw's numbers (F1 90.93 vs 78.39; FP 560→64; recall -3.1%) come
  from OWASP Benchmark v1.2, a synthetic Java suite with a mechanical
  oracle. **No such oracle exists for Annex III classification.**
- **Offline:** NO for both.
- **Verdict: ADOPT ZEROFALSE'S PER-PROVISION PROMPTING STRUCTURE.
  REJECT QASECCLAW'S NUMBERS as a forecast; the design is redundant with B1.**
- > **VALIDATOR FAIL on B4, accepted.** ZeroFalse was adopted with **no
  > falsifiable test and no domain-shift assessment** for the per-CWE to
  > per-provision mapping, in a pack whose own pass criterion requires
  > both. **Gate added:** build one per-provision prompt set and one
  > generic prompt set, run both over the 24 measured high-risk FPs, and
  > **adopt only if per-provision beats generic by ≥20% relative FP
  > reduction at equal recall on the synthetic set.** Fails that, or ties,
  > → reject. Also noted: B5's 560→64 baseline is **standalone Semgrep**,
  > not a strong SAST, which my draft omitted.

### B6. IRIS — arXiv:2405.17238
- **Status: PEER-REVIEWED**, ICLR 2025 (VERIFIED via iclr.cc). Not
  determinable from arXiv.
- **Verdict: REJECT.** Reason recorded per PROGRAMME.md: IRIS's headline is
  a **recall** result (CodeQL 27 → IRIS 55) with only ~5pp FDR improvement.
  This project's measured problem is the opposite — recall is adequate,
  precision is not. **None of the five FP classes is a dataflow error.**
  "Generative-model infra read as critical infrastructure" is a vocabulary
  collision, not an unreachable sink. Adopting it would add a CodeQL-scale
  dependency to solve a problem the tool does not have.

### **B-CROSS: the finding that matters most (RESTATED after validator FAIL)**

> **CORRECTED 28 Jul 2026.** The validator returned FAIL on this section
> for overstating the oracle claim, **and the overstatement ran in the
> conservative direction** — it made the literature look less applicable
> than it is. The original said all six operate where "a hard oracle
> exists". **That is true only of the synthetic benchmarks.** B1's labels
> came from Tencent's routine two-round human code review; C2's own thesis
> is that the label cannot be made without further context, with human
> experts reaching κ = 0.64; C4's reviewers reached κ = 0.453 and 0.424.
> **Those are human-adjudicated oracles with measurable, imperfect
> agreement — structurally the same situation as regulatory
> classification, not different from it.**
>
> Also corrected: B-CROSS listed **88.6%** among "every figure above". It
> appears nowhere above. It is QASecClaw's FP-reduction figure, equivalent
> to the 560→64 that *is* stated. A traceability break, not an invention.

**Restated claim.** The **synthetic** benchmarks (OWASP Benchmark v1.2,
Juliet, CASTLE) have mechanical oracles and **their precision figures
cannot transfer**. The **real-world** studies (B1 especially) do not have
mechanical oracles, and **B1 transfers better than this pack originally
credited.**

**What still holds unchanged:** no figure from any of them is a prediction
for a compliance corpus, and **no Phase 5 acceptance criterion may be
written in terms of one.**

What the literature supports: the **architecture** (cheap high-recall
matcher + semantic adjudicator whose output is grounded rather than
trusted) and the **triage economics** (cents and seconds vs 10-20 minutes).

What it does **not** support: **any specific precision number for a
compliance corpus.** Every figure above (88.6%, 94-98%, 43.7%) is a
population transfer, not a prediction. **No Phase 5 acceptance criterion
may be written in terms of them.**

**Five of six require a network call at scan time**, so they can only ever
be the optional, off-by-default extra. That is not a workaround; it is the
architecture constraint doing its job.

---

## PART C — corpus and benchmark methodology

### C1. arXiv:2403.18624, ICSE 2025 — the paper is NOT titled "PrimeVul"
> **FOURTH citation-identity defect, found by the validator in this
> document.** Actual title: **"Vulnerability Detection with Code Language
> Models: How Far Are We?"** (Ding et al.). **PrimeVul is the benchmark
> inside it**, not the paper. My draft headed this card "PrimeVul" while
> formally correcting exactly this error class at C4, and then wrote "the
> third citation-identity error found in this corpus" — which was
> incomplete by its own standard. Same defect at **B3** (AdaTaint; actual
> title "LLM-Driven Adaptive Source-Sink Identification and False Positive
> Mitigation for Static Analysis", Shiyin Lin), **B4** (ZeroFalse) and
> **B5** (QASecClaw), all recorded by system name with no title or authors.
- **Status: PEER-REVIEWED** (arXiv Comments states acceptance).
- **Requirements it sets (REPORTED-UNVERIFIED):** normalise (strip
  whitespace) then MD5 dedup, discarding self-identical pre/post pairs;
  **chronological split by commit date, 80/10/10 oldest→newest, with
  same-commit samples never split across sets**; three annotators with
  majority vote, senior expert leads discussion on disagreement.
- **Reports NO kappa.** Agreement handled procedurally.
- **Verdict: ADOPT dedup + chronological split.** These are the leakage
  controls and they are cheap.

### C2. Risse, Liu and Böhme — arXiv:2408.12986, ISSTA 2025
- **VERIFIED PERSONALLY 28 Jul 2026** by re-fetching the arXiv page.
  Title: "Top Score on the Wrong Exam: On Benchmarking in Machine Learning
  for Vulnerability Detection". **Three authors — Niklas Risse, Jing Liu,
  Marcel Böhme.** Comments: "Accepted at the 34th ACM SIGSOFT
  International Symposium on Software Testing and Analysis (ISSTA 2025)".
  **CORRECTION to the prior record, which omitted Jing Liu.**
- **Numbers (REPORTED-UNVERIFIED, from full text):** 300 functions, two
  independent labellers; step 1 agreement 82%, **Cohen κ = 0.64**; step 2
  agreement 98%, **Cohen κ = 0.96**; 15-minute per-function budget.
- **Verdict: ADOPT as the annotation-protocol model.** It is the closest
  thing in the set to a usable standard: two independent labellers, a
  reported statistic, discussion to resolve, written justification per
  label, documented expertise, public release of labels.

### C3. SecVulEval — arXiv:2505.19828
- **Status: PEER-REVIEWED but NOT from arXiv** (no Comments, no journal-ref).
  Crossref DOI 10.1145/3805760.3814932 → **AIware 2026**, pp. 388-396.
- **TWO CORRECTIONS:** venue is **AIware 2026, not 2025**; and the
  published title differs from the preprint title
  ("Context-Aware Benchmarking..." vs "Benchmarking LLMs for Real-World
  C/C++ Vulnerability Detection"). **Citing the arXiv title against the
  AIware DOI produces a mismatched citation.**
- **Adopt:** duplication rate as a mandatory reported dataset property.

### C4. arXiv:2507.21817 — **NOT called "BenchVul"**
- **VERIFIED PERSONALLY 28 Jul 2026.** Actual title: **"Out of
  Distribution, Out of Luck: How Well Can LLMs Trained on Vulnerability
  Datasets Detect Top 25 CWE Weaknesses?"** Comments: **"Accepted for
  publication at ICSE 2026"**. "BenchVul" does **not** appear in the title;
  it is one of three artefacts inside the paper.
- **CORRECTION to the prior record**, which carried it as a paper named
  BenchVul. This is the third citation-identity error found in this corpus.
- **Numbers (REPORTED-UNVERIFIED):** label inaccuracy 20-71% in prior
  datasets; TitanVul 38,548 functions from seven sources; **Cohen κ 0.453
  and 0.424, described by its own authors as moderate**.
- **Adopt:** AST-normalised dedup; removal of self-identical pairs;
  out-of-distribution evaluation rather than same-dataset splits.

### C5. CASTLE — arXiv:2503.09433, TASE 2025
- Peer-reviewed via Springer/Crossref (DOI 10.1007/978-3-031-98208-8_15);
  **no venue on the arXiv page**.
- 250 hand-authored micro-benchmarks, 25 CWEs, **10 per CWE split 6
  vulnerable / 4 non-vulnerable so false positives are measurable**.
- **Directly validates this project's synthetic fixture approach**, and
  says the quiet part: the corpus is capped at 250 *specifically* to keep
  manual verification feasible.
- **Adopt:** the balanced positive/negative split per category. Regula's
  synthetic set currently has 10 positives to 3 negatives; CASTLE's 6:4
  ratio would make FPs measurable, which they currently barely are.

### C6. Li et al. — FSE 2023, DOI 10.1145/3611643.3616262
- **Peer-reviewed**, ESEC/FSE '23, pp. 921-933.
- **The most uncomfortable and most useful item in the pack.** Seven SAST
  tools from 161 candidates detected **12.7%** of real-world vulnerabilities;
  **70.9% went undetected**; tools **overstated** their detection capability
  by 90.5% on the real dataset.
- **Why it matters here:** this is a *recall* measurement against ground
  truth, and it is the reason published precision figures and real recall
  diverge so violently in this field. **It is direct external evidence that
  Regula's unmeasured recall is likely to be the weak number, not its
  precision** — which is exactly the opposite of where the current public
  surfaces put their emphasis.
- **Verdict: ADOPT AS THE FRAMING FOR F11.** Cite it when publishing any
  recall figure.

### **C-CROSS: two findings that change the programme**

**1. The Fleiss κ ≥ 0.7 target is not what the literature does.**
PROGRAMME.md Phase 3 item 1 specifies "≥3 independent human annotators
with Fleiss' κ ≥ 0.7". MEASURED across these six papers: only **two report
any agreement statistic**, both use **Cohen's κ, not Fleiss**, and the
values are **0.64, 0.96, 0.453, 0.424**. **No paper in the set prescribes a
numeric threshold.** Two of the four reported values would fail a 0.7 bar,
in papers accepted at ISSTA 2025 and ICSE 2026.

> ### CORRECTED 28 July 2026 after RESEARCH VALIDATOR review. Read this, not the draft below it.
>
> The validator returned **FAIL** on this section and was right on every
> count. What it found, and what now stands:
>
> **1. A FALSIFIED CLAIM, now struck.** My draft asserted that "the ICSE
> 2026 paper ran its initial full pass with a single annotator and sampled
> for multi-reviewer validation afterwards", and used it to argue a
> cheaper path to credibility. **Neither ICSE 2026 paper in this pack did
> that.** C4's review used seven independent researchers each assigned a
> random sample, on top of an LLM multi-agent construction pipeline; B1's
> used two full rounds by different reviewers. **The claim was presented
> as established fact, was untagged, and does not survive contact with
> either source. It is struck entirely.** It came from a retrieval
> subagent and I published it without verifying it — the exact failure the
> standing rule about subagent output exists to prevent.
>
> **2. A miscount, and it ran against my own recommendation.** I wrote
> "two of the four reported values would fail a 0.7 bar". It is **three of
> four**: 0.64, 0.453 and 0.424. Only 0.96 clears it.
>
> **3. The 3-to-2 annotator reduction is NOT licensed by this
> measurement**, and is contradicted by **C1 in this same document**.
> PrimeVul (ICSE 2025) uses exactly three annotators with majority vote
> and a senior expert leading discussion. What the literature omits is a
> *kappa*, not the third annotator. My recommendation moved 3 → 2 on
> evidence that only addressed the threshold.
>
> **4. An unflagged population transfer, of the type I police elsewhere.**
> C4's κ = 0.453/0.424 measure agreement on a *validation audit of an
> LLM-constructed dataset*, with the authors themselves attributing the
> low values to the kappa paradox. Using them to set expectations for
> *primary human labelling* is a cross-population transfer. I catch this
> error in B1's 94-98% and committed it here.
>
> **WHAT NOW STANDS.** Dropping the **Fleiss κ ≥ 0.7 numeric threshold** is
> earned: no paper in the corpus sets one, and three of four observed
> values fall below it. Cohen rather than Fleiss follows mechanically from
> two raters. **A floor of κ ≥ 0.6 is restored**, the Landis and Koch
> "substantial" boundary this document already names as its interpretive
> frame. **Three annotators are retained on C1's precedent.** If that is
> later reduced, it must be recorded as a **resource decision, not a
> measured one.**
>
> Validator's summary judgement, recorded verbatim in substance: this was
> not a quiet bar-drop — it was declared, self-labelled a disposition, and
> open to Phase 7 overrule — but good faith is not sufficiency, and two of
> its three legs were unsupported with one falsified.

**~~Superseded draft, kept so the correction is visible:~~** *This is a
PROGRAMME.md principle 2 case. Recommendation was: retarget to two
independent labellers with Cohen's κ reported, no numeric floor.* **That
recommendation is withdrawn as stated and replaced by the corrected
position above.**

**2. None of the six is Python.** All are C/C++ or Java. **F11's
language-monoculture weakness cannot be closed by citing any of them.** It
can only be closed by rebuilding across languages. Any claim that the
corpus follows published standards must state that the standards were set
on other languages.

---

## PART D — what was NOT done

Stated rather than glossed, per "never present partial work as complete":

- **The RESEARCH VALIDATOR subagent has not been run** on these cards. That
  is a Phase 2 pass requirement (PROGRAMME.md principle 7). Until it runs,
  Phase 2 is **incomplete**, and these cards are inputs, not a validated set.
- **No PDFs were read** in the retrieval pass; the numbers tagged
  REPORTED-UNVERIFIED are abstract- and full-text-HTML-level only.
- **Regulatory items not re-verified this pass** (Reg (EU) 2026/1744,
  Korea, Colorado, prEN 18286, ISO/IEC 42005): these INHERIT
  `PHASE0_VERIFICATION.md` §C, which verified them against primaries on
  27 Jul. **prEN 18286 remains paywalled; clause-level alignment claims are
  forbidden until it is purchased.**
- **`/research-eval` was not run** on this pack.
