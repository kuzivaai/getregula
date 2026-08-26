# Evidence review and engineering basis — 25 August 2026

## Scope and method

This review asks how Regula can become more accurate, repeatable, scalable and
useful without overstating what static code evidence can establish. Research
was performed on 25 August 2026. Searches prioritised enacted law, regulator and
standards-body material, peer-reviewed software-engineering and measurement
research, then current official documentation and repository metadata for
candidate tools. August 2026 preprints were included only as emerging evidence
and are labelled accordingly.

This is a structured engineering review, not a complete systematic literature
review. Repository stars and recent activity are ecosystem observations, not
evidence of correctness, suitability or scientific validity. “Current” below
means observed on 25 August 2026; it does not guarantee that no newer or
unindexed source existed.

## Source appraisal

| Source | Status on 25 August 2026 | What it supports | Important limit |
|---|---|---|---|
| [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32026R1744) | Enacted EU law; OJ 24 July 2026, in force 27 July | Amendments to the AI Act, including high-risk dates and the Article 50(2) transition | Must be read with the consolidated AI Act; not every AI Act duty moved |
| [Consolidated Regulation (EU) 2024/1689](https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:02024R1689-20260727) | Official consolidated text dated 27 July 2026 | Operative article wording after the Omnibus amendment | Consolidation is a reading aid; the OJ acts remain authoritative |
| [Commission Article 50 guidelines](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems) | Official Commission guidance, 20 July 2026 | Scope and practical interpretation of Article 50 transparency duties | Guidance is not legislation and does not replace case-specific legal analysis |
| [Article 50 Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content) | Final voluntary code, 10 June 2026 | Candidate practices for marking and labelling AI-generated content | Voluntary support instrument; not proof of conformity by itself |
| [NIST TEVV-Athlon, NIST AI 200-2](https://doi.org/10.6028/NIST.AI.200-2.ipd) | Initial public draft, announced 7 August 2026; comments open to 6 October | Structured, adaptable, context-specific TEVV design | Draft, not a final standard and not validation of Regula |
| [NIST AI RMF Playbook — Measure](https://airc.nist.gov/airmf-resources/playbook/measure/) | Official voluntary guidance; living resource | Documented test sets and methods, independent assessors, representative users/data and disaggregated evaluation | Not a checklist or a product certification |
| [PrimeVul](https://doi.org/10.1109/ICSE55347.2025.00038) | Peer-reviewed ICSE 2025 paper | Label quality, de-duplication, chronological splitting and realistic metrics; demonstrates severe benchmark inflation | Vulnerability detection is analogous, not identical, to regulatory-indicator detection |
| [Top Score on the Wrong Exam](https://doi.org/10.1145/3728887) | Peer-reviewed ISSTA 2025 paper | Function-level binary labels often lack enough program context | Security-vulnerability construct; Regula needs its own construct-validity study |
| [Zapf et al. on nominal inter-rater reliability](https://doi.org/10.1186/s12874-016-0200-9) | Peer-reviewed simulation and case study | Krippendorff alpha and bootstrap intervals when ratings may be missing | Assumes the chosen label construct itself is valid |
| [Conformal Risk Control](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html) | Peer-reviewed ICLR 2024 paper | Distribution-free control of expected monotone loss under stated exchangeability/calibration conditions | Does not make heuristic scores calibrated; conditions must be tested on representative data |
| [VICBench](https://arxiv.org/abs/2608.12246) | Preprint submitted 12 August 2026 | Emerging exact-version, multi-language and independently checked benchmark practice | Not peer reviewed; human-plus-agent annotation is not the same as independent human ground truth |
| [SARIF 2.1.0 plus Errata 01](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) | OASIS standard plus approved errata | Stable interchange for tool/rule metadata, locations, runs and results | A valid SARIF document can still contain invalid or misleading findings |
| [GitHub SARIF support](https://docs.github.com/en/code-security/reference/code-scanning/sarif-files/sarif-support) | Current platform documentation | Supported SARIF subset, stable alert identity and upload/truncation constraints | GitHub consumption constraints are narrower than the full OASIS standard |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | W3C Recommendation | Keyboard operation, focus, reflow, names/states, target size and other testable accessibility requirements | Automated conformance checks do not establish usability with representative people |
| [SLSA 1.2](https://slsa.dev/spec/v1.2/) | Approved industry specification, current version | Source/build provenance, consistent builds and verifiable artifact lineage | Provenance protects lineage/integrity, not detector accuracy |
| [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) | Current official docs; [MIT repository](https://github.com/tree-sitter/tree-sitter) active on 25 August | Robust concrete syntax trees and incremental parsing across languages | Adding its Python binding or grammars would violate Regula's zero-dependency core unless isolated as optional tooling |
| [Semgrep OSS](https://semgrep.dev/docs/writing-rules/glossary) | Current official docs; [LGPL repository](https://github.com/semgrep/semgrep) active on 25 August | Syntax-aware matching, constant propagation and intraprocedural taint concepts | OSS and proprietary engines have different interfile capabilities; it is a baseline/integration candidate, not a drop-in core dependency |
| [CodeQL data flow](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/) | Current official docs; [MIT queries repository](https://github.com/github/codeql) active on 25 August | AST, control-flow and local/global data-flow modelling; explicit source/sink/barrier semantics | Database construction and global flow have language, build and resource costs; CLI licensing/distribution differs from the query repository |
| [Joern code property graph](https://docs.joern.io/code-property-graph/) | Current official docs; [Apache-2.0 repository](https://github.com/joernio/joern) active on 25 August | Combining syntax, control and data-flow representations in a cross-language graph | JVM/tooling footprint conflicts with a small stdlib-only core; suitable for research baselines or an optional adapter |
| [BenchProctor](https://github.com/TheAuditorTool/BenchProctor) | Apache-2.0 repository; 7 stars and active in July 2026 when observed | Candidate examples for SARIF-oriented benchmark orchestration | Very limited adoption and no peer-reviewed validity evidence found; do not inherit claims or scores uncritically |

For scale only, GitHub API observations on 25 August 2026 showed approximately
26,752 stars for Tree-sitter, 16,396 for Semgrep, 10,009 for the CodeQL queries
repository and 3,448 for Joern. These counts are volatile and are not a ranking
of technical quality.

## Findings and decisions

### 1. The legal source model is now materially different from the 2024 schedule

Regulation (EU) 2026/1744 sets 2 December 2027 for Chapter III Sections
1–3 obligations concerning Article 6(2)/Annex III systems, and 2 August 2028
for Article 6(1)/Annex I systems. Article 50 transparency obligations applied
from 2 August 2026. Amended Article 111(4) gives providers of relevant systems
placed on the market before that date until 2 December 2026 for Article 50(2).
Every Regula deadline surface must retain this Omnibus caveat and cite the
specific provision; a generic “the AI Act was delayed” statement is false.

The decision model already records the enacted Omnibus source and these dates.
The remaining engineering rule is to test all generated locales and machine
outputs against that source rather than repeat dates manually.

### 2. Current accuracy figures are development evidence, not ground truth

The existing labelled corpus was produced by one maintainer and the synthetic
fixtures were written for known rules. They are useful for regression and
hypothesis generation. They cannot establish independent real-world precision,
recall, calibration or legal correctness.

The strongest next step is not a larger uncurated corpus. It is a versioned,
licence-compatible, project-held-out corpus with exact commits, negatives,
pre-split de-duplication, independent blinded human ratings, preserved
disagreements and sufficient code/project context. `not_assessable` must be an
allowed outcome because forcing absent deployment context into TP or FP makes
the label look more certain than the evidence.

Implementation consequence: `benchmarks/MULTI_ANNOTATOR_PROTOCOL.md` now
defines this protocol. `benchmarks/annotation_stats.py` now uses nominal
Krippendorff alpha with a deterministic item-bootstrap interval and incomplete
ratings; it retains Fleiss kappa only as a complete-case view. Universal
“publishable above X” agreement bands were removed.

### 3. Use a staged hybrid detector, not one universal regex engine

The mature tool ecosystems converge on layered representations:

1. cheap lexical candidate generation;
2. syntax-aware confirmation and extraction;
3. local flow where a rule has explicit sources, sinks and barriers;
4. bounded interprocedural or cross-file flow for predeclared high-value rules;
5. explicit fallback/abstention when the language, parse or context is
   unsupported.

Regula already has a Python AST path, JavaScript/TypeScript analysis helpers,
cross-file flow and content-hash caching. The near-term task is to attach a
machine-readable `analysis_mode` and `context_status` to each finding and then
measure every rule/language stratum separately. Regex remains a candidate
signal; it must not be described as equivalent to an AST or data-flow result.

Tree-sitter is the strongest candidate for an optional multi-language parsing
adapter because of its robust, incremental concrete syntax trees. It should not
be added to the packaged core while the zero-dependency constraint stands.
Semgrep, CodeQL and Joern should first be reproducible external baselines and
sources of query-design concepts, with scope/licence/resource differences
reported, rather than copied wholesale.

### 4. Priority scores are not probabilities

Regula's 0–100 value is a heuristic detector-priority score. It is not a 70%
chance that a finding is correct. Renaming or documentation cannot calibrate
it. Calibration requires a representative, independent calibration set and a
held-out evaluation; subgroup shift and time drift must be measured.

Conformal risk control is promising only after those prerequisites exist. A
future selective policy should publish coverage and selective error, including
the composition and error rate of abstained items. Until then, missing facts
should yield an explicit review requirement or abstention, never a confident
legal result.

### 5. Repetition requires provenance at three different layers

- **Finding provenance:** stable rule ID/version, source location, parser/fallback
  mode, configuration digest, limitations and original evidence.
- **Evaluation provenance:** corpus/split/codebook digests, exact commits,
  random seed, exclusions, environment, completion status and integer confusion
  counts before derived metrics.
- **Build provenance:** artifact digest and verifiable builder/source lineage.

SARIF is the correct interchange for findings, but Regula-specific evaluation
and completion metadata must remain machine-readable alongside it. SLSA
provenance complements this; neither proves detector validity.

### 6. Product validity includes comprehension and accessibility

The critical user task is deciding what code evidence needs human review, not
maximising alarming findings. The interface must expose uncertainty, skipped
files, unsupported context and next actions without making an unavailable path
look actionable. WCAG 2.2 AA checks, keyboard/focus/reflow tests, desktop/mobile
browser exercises and screen-reader names/states are release evidence.
Representative user testing is still required to establish comprehension and
confidence; automated tests and screenshots cannot do that.

## Evidence-led implementation order

1. **Public-repository boundary:** keep the current tree free of personal and
   internal operating material; scan it automatically; then perform a separately
   reviewed all-ref history rewrite and credential-response process.
2. **Evaluation foundation:** freeze a machine-readable protocol and corpus
   manifest; capture exact commits/licences/dates; de-duplicate before a
   project-held-out chronological split; obtain independent blinded labels.
3. **Finding provenance:** add analysis mode, context sufficiency, rule version
   and limitation fields without breaking the stable JSON envelope or SARIF.
4. **Measured language-aware rules:** migrate high-cost false-positive clusters
   to syntax/local-flow confirmation one rule family at a time and publish
   per-stratum deltas with intervals.
5. **Abstention/calibration:** introduce only after an independent calibration
   corpus exists; report coverage and selective error rather than a bare score.
6. **Scale and UX:** benchmark cold/warm cache, bounded memory and monorepository
   completion; validate the primary and failure tasks at representative desktop
   and mobile sizes, then conduct representative human testing.

## Explicit non-decisions

- No new runtime dependency is added to the packaged stdlib-only core by this
  review.
- No external repository is endorsed based on popularity.
- No preprint is treated as settled peer-reviewed evidence.
- No current Regula performance figure is promoted to independent real-world
  accuracy.
- No static code result is promoted to legal classification, conformity or
  compliance.
