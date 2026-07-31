# commercial_v1 preregistration red-team disposition

Review date: 2026-07-31. Reviewer received only the protocol, manifest,
comparator lock, research questions, harness/scoring/verification code and
selection files. It did not receive labels, results, detector tables, author
reasoning or a preferred verdict. No benchmark result existed.

The repository writer reproduced each material finding by reading the named
control and tracing its call path. All eight HIGH and all six MEDIUM findings
were accepted. All cheap LOW controls in the same integrity class were also
accepted. No finding was dismissed silently.

| Severity | Reproduced finding | Disposition before freeze |
|---|---|---|
| HIGH | Public Regula, competitors and repositories were listed but unreachable from `run.py`. | Added `install_tools.py`, `operations.py` and `acquire.py`. Accuracy adapters remain deliberately absent for non-equivalent competitor schemas, so competitor output is operations-only and cannot support superiority. |
| HIGH | Candidate B used any nested `limited_risk` tier and a raw-substring pseudo-renderer. | Regula adapter now requires a source-linked case finding; naive baseline uses `HTMLParser` visible text/meta events. Construct is explicitly an observable feature, not legal sufficiency. |
| HIGH | Candidate A accepted any global non-empty inventory-like list. | Adapter now requires filename, integer line and indicator evidence from the case file. |
| HIGH | Verification discovery was tautological and result validation unused. | Independent tracked discovery uses `git ls-files`; HEAD, hashes and exact sets are checked. Adverse result records are retained but fail success eligibility. |
| HIGH | Fresh output paths guaranteed different normalised hashes. | Harness paths and timing fields are removed and Python/case paths canonicalised; regression control uses distinct roots. |
| HIGH | Repository selection was purposive while described as deterministic sampling. | It is now explicitly a purposive convenience census, not random or confirmatory. Prior-benchmark exclusions remain visible. Claim-ready support is impossible from it. |
| HIGH | Scoring pooled jobs and set headline eligibility from completeness alone. | Language/transform strata are emitted. A separate conjunctive gate engine evaluates thresholds and external gates; synthetic score files hard-code headline eligibility false. |
| HIGH | Duplicate/extra result records could retain eligibility. | Exact unique ID equality is required; duplicate negative control added; candidate membership comes from label metadata. |
| MEDIUM | Forty correlated variants were treated as independent Bernoulli trials. | Transformation family is the inferential unit; Wilson intervals are descriptive and cannot make the synthetic layer confirmatory. |
| MEDIUM | Timing and comparator availability conditions were unequal. | In-process and cold-process timings cannot support superiority. Identity resolution, install availability and accuracy are separate. |
| MEDIUM | Baseline did not implement rendered evidence. | DOM-visible-text/meta extraction added, with hidden-element and negation controls. |
| MEDIUM | “Article 50 implementation” overstated legal ground truth. | Labels cover observable disclosure/marking features only; legal mapping remains review-required. |
| MEDIUM | Commercial predicates were subjective. | Protocol now gives numeric comparative thresholds, a 30-independently-labelled-repository condition, and exact network/public-claim blockers. These conditions are known unmet and therefore falsify claim-ready status rather than being relaxed. |
| MEDIUM | Memory/network promises exceeded instrumentation. | Comparative memory is `NOT_MEASURED`; cumulative RSS is labelled. Socket denial is implemented with explicit non-Python limitation; namespace failure is retained. |
| LOW | Critical inputs were outside hash binding. | Manifest now enumerates every tracked `commercial_v1` input except itself and `freeze.json`; `freeze.json` binds manifest, protocol, labels and tool lock externally. |
| LOW | Seeded ordering could be reverted without changing membership. | Pseudo-random selection was removed; lexical set equality is checked. |
| LOW | Tests did not prove discovery, duplicates, null parsing or path invariance. | Focused controls cover missing Git, ignored/untracked inputs, bidirectional enumeration, hashes, duplicates, adverse records, path invariance and conjunctive gates. Further mutation testing remains a limitation. |
| LOW | Rejecting failures could erase them. | Failure records remain in raw evidence and block eligibility; authenticity/completeness validation is separate from success. |

The corrections intentionally make a favourable verdict harder. In particular,
the absence of independent repository labels and equivalent competitor accuracy
adapters means Candidates A and B cannot become `CLAIM_READY` in this session,
regardless of synthetic point estimates.
