# Regula commercial_v1 preregistration

Status: frozen before any `commercial_v1` tool execution. Session date:
2026-07-31 Europe/London. Product detection rules, classifiers, gates,
thresholds, and public positioning are frozen at commit
`94efa9e6ad9173fb888822543c247195078b0220`.

This evaluates whether one narrow Regula capability merits a bounded pilot.
It is not an EU AI Act compliance certification and is not designed to make
Regula look favourable. Failed installs, non-zero exits, timeouts, missing
repositories, and underpowered strata remain results.

## Evidence boundary and candidate jobs

Candidate A asks whether a buyer can use Regula for local AI inventory and a
reproducible evidence scaffold. A positive fact is an observable imported AI
library or service; comments, quoted examples, and near-name modules are
negative controls. A tool prediction requires a source-linked finding carrying
the case filename, integer line and non-empty indicator list. Ungrounded global
metadata is rejected. Real-repository inventory labels are not inferred by a
model.

Candidate B asks whether Regula can identify code-observable Article 50
implementation evidence. The unit is rendered affirmative disclosure or
machine-readable marking evidence. Corpus truth is limited to that observable
feature, not legal sufficiency. Tool output predicts the feature only when a
source-linked `limited_risk` finding identifies the case. The naive baseline
uses a stdlib HTML parser to exclude comments, scripts, styles and templates
and recognise visible affirmative text or an `ai-generated` meta marker.
Comments, dormant templates, developer notes, irrelevant attributes, and
negated text are negatives. A miss means
only that implementation evidence was not observed in the reviewed artefact.
It is never scored as a legal violation.

Candidate C asks whether declared intended purpose and deployment context can
support high-risk review. It cannot exceed `MODEL_PROVISIONAL` in this session:
two independent human raters and adjudication are unavailable. No code-only
result may clear Candidate C.

## Corpus and leakage controls

Layer 1 is 160 truth-by-construction decisions in `corpus.json`: 40 positive
and 40 negative decisions for each of A and B. Python and HTML are separate
language strata. Transformations are frozen before execution. Expected labels
are held in `labels.json`; `run.py` does not open that file. Labels are opened
only by `score.py` after every frozen run finishes.

Layer 2 is a disclosed purposive convenience frame of 12 public repositories
listed in `manifest.json`, pinned to commits obtained from `git ls-remote` on
2026-07-31. It is not random or confirmatory. The set includes Python and
TypeScript, AI and non-AI software, and small and materially larger projects.
Four previously benchmarked repositories are disclosed as exclusions rather
than silently removed. Repository identity, commit and licence are factual
metadata. Capability labels require blinded human review; without it, this
layer can support installation, runtime, alert-burden and evidence-reproduction
observations but not precision, recall, or external accuracy support. No
candidate can become `CLAIM_READY` from this convenience frame.

Layer 3 is a blinded scenario-pack requirement covering intended purpose,
roles, affected people, deployment context, consequence, oversight, code
evidence, decision rules, two independent labels and adjudication. It remains
unexecuted and `MODEL_PROVISIONAL` until independent humans supply those
fields.

No existing Regula development fixture is a headline holdout. No expected
holdout label may be exposed to a scanner command. After execution, internal
inspection may classify failures but may not tune product rules or corpus.

## Prospective sample size and power

The commercial gates concern lower confidence bounds, not convenient point
estimates. For 40/40 successes, a two-sided Wilson 95% lower bound is about
0.912, so a perfect applicable stratum can clear a 0.90 lower-bound policy.
With 39/40, the lower bound is about 0.871 and does not clear it. Forty actual
positives and forty negatives per synthetic candidate therefore make the gate
falsifiable while exceeding the 30-decision minimum.

This calculation does not grant independent trials or external validity. The
160 decisions repeat only three positive and five negative transformation
families per job. Transformation family, not generated file, is the inferential
unit; family-level results are diagnostic and cannot independently clear a
claim gate. Repository decisions are clustered. Twelve purposively chosen
clusters are exploratory and no repository-level accuracy labels exist, so
comparative inference is `INSUFFICIENT`. Forty predicted and actual positives
remain the minimum for descriptive Wilson intervals, which are reported with
an explicit correlated-case caveat rather than used as confirmatory coverage.

## Tools and comparator fairness

`tools.lock.json` freezes the latest official-registry Regula release found
(1.7.4), local HEAD, a transparent naive baseline, two registry-resolved
competitors, and one unresolved CLI lead. Each install uses a fresh external
virtual environment. The documented default runs first. At most one frozen
best-reasonable configuration may follow. A comparator that cannot install or
produce valid output is operationally unavailable and is not replaced.

Candidate A naive baseline matches ten explicit AI package/service names only
in active Python import statements. Candidate B naive baseline matches five
exact affirmative phrases in rendered markup and excludes five transparent
near-miss forms. These are intentionally inspectable, not optimised after
results.

Every synthetic CLI invocation has a 120-second limit and every repository
invocation a 900-second limit, retained stdout, stderr, command, working
directory, version, configuration, start/finish time, exit status, timeout,
input hash, output hashes and duration. In-process naive timing and cold CLI
timing are reported separately and never used for superiority. The available
`resource` high-water mark is cumulative child RSS, not per-invocation peak;
memory is therefore `NOT_MEASURED` for comparative purposes. Network behaviour
uses an attempted namespace denial plus a Python socket-construction denial.
The latter cannot see non-Python syscalls and cannot prove zero calls. Source
inspection alone cannot prove zero network calls.

## Execution sequence

1. Verify all frozen hashes, that Git actually succeeds, every repository
   input is tracked and not ignored, every listed input exists, and recursive
   discovery agrees with the manifest in both directions.
2. Acquire each pinned public repository into the external artefact directory;
   verify HEAD, source hash and licence. Missing acquisition is an error.
3. `install_tools.py` creates fresh environments for every registry-resolved
   package and retains installs; the unresolved Complior identity remains an
   availability result, not a product execution failure.
4. `run.py` executes naive and local-HEAD synthetic cells. Public Regula and
   competitor schemas are not coerced into synthetic accuracy decisions
   without a source-event adapter. `operations.py` nevertheless reaches and
   executes every installed documented default, and the one frozen configured
   compliance-agent path, on all 12 repositories. This is an availability and
   operations audit, not an accuracy comparison.
5. Repeat deterministic paths from a fresh output directory without output or
   fixture reuse. Compare normalised output hashes.
6. Only after both runs end, open `labels.json`, score, and classify failures.

`run.py` refuses an existing output directory. `verify.py` independently uses
`git ls-files`, checks HEAD against the manifest, and rejects missing,
untracked, ignored, changed, duplicate, extra or omitted inputs/results. It
retains adverse records but refuses to mark them successful. `normalise.py`
removes declared timing and harness-path fields and canonicalises case/Python
paths while retaining semantic configuration. `score.py` requires exact unique
enumeration, reports language/transform strata, retains fractions and Wilson
intervals, and hard-codes headline eligibility false until the external gate
engine evaluates every conjunct.

## Metrics and analysis

Where logically valid, report TP, FP, FN, TN, precision, recall, F1, MCC,
Wilson 95% intervals, false alerts per repository and per 1,000 relevant lines,
misses per repository, category/language breakdown, default/configured paths,
execution-path disagreement, install success, time to first valid result,
runtime, peak memory, determinism, observed network behaviour, evidence-pack
completeness, clean-checkout reproduction, manifest/signature verification and
exit-code usability.

Paired binary decisions may use exact McNemar diagnostically, but repeated
transformation families make item-level inference non-confirmatory. A future
confirmatory repository study must define an external population and adequate
independent repository clusters before using a paired repository bootstrap.
Report effect sizes and uncertainty, not p-values alone. Do not pool away a
weak job, language, transformation or category. No pseudo-probabilities or
calibration analysis are permitted unless a tool emits real confidence scores.
Sensitivity analysis reports false-positive to false-negative cost ratios of
1:1, 2:1, 1:2, 5:1 and 1:5; no single ratio is buyer truth.

## Preregistered gates

Candidate A is `CLAIM_READY` only if Wilson lower bounds are at least 0.90 for
both precision and recall, real repositories support the result, clean evidence
reproduction passes, no material hidden-network contradiction exists, and a
meaningful advantage over the naive baseline or executable competitor is
demonstrated. In this session, “real repositories support” requires independent
labels on at least 30 repositories sampled from a prospectively enumerated
buyer-relevant population. That condition is known unavailable, so A cannot
become `CLAIM_READY`; synthetic results can support only `PILOT` or `FAILED`.

Candidate B is `CLAIM_READY` only if the precision lower bound is at least
0.90 and recall lower bound at least 0.80, evidence observations are separated
from legal compliance, source absence never becomes a definitive violation,
and advantage over exact markup matching or an executable competitor is
demonstrated. “Meaningful advantage” means a paired difference whose 95%
interval excludes zero and whose absolute recall or precision improvement is
at least 0.05 without degrading the other metric by more than 0.02, or a
documented operational capability absent from the baseline with no accuracy
regression. No source-linked competitor adapter exists at freeze, so B also
cannot become `CLAIM_READY` in this session.

Candidate C requires two independent human raters, adjudication, context
inputs, raw disagreements and an appropriate agreement statistic, plus Wilson
lower bounds of 0.80 precision and 0.70 recall and no un-escalated definitive
legal error. Without those humans its ceiling is `MODEL_PROVISIONAL`.

All candidates additionally require two clean identical normalised runs,
verified evidence manifests, complete accounting, visible failures, a working
public-release first-use journey, no contradicted active high-consequence claim,
and no concealed category/language. A “material hidden-network contradiction”
means an observed socket attempt on a command actively described as offline or
zero-network. Public-claim integrity fails if any active unqualified legal
classification, universal reproducibility, or zero-network claim is
contradicted. A point estimate that passes while its
interval fails is `PILOT`, never `CLAIM_READY`.

Verdict fields and decision rules are exactly those in the session directive:
technical evidence, comparative advantage, public-claim integrity, regulatory
currency, operational readiness, demand evidence and overall decision are
reported separately. Research cannot raise demand above `UNVALIDATED`.

## Known preregistration limitations

- Layer 1 is generated from a small set of repeated transformation families;
  it tests metamorphic consistency, not independent Bernoulli performance.
- Real-repository precision and recall cannot be scored without independent
  labels. Twelve repository clusters are weak for uncertainty estimation.
- No human raters are available for Candidate C.
- Comparator schemas may not map cleanly to the same unit. A non-equivalent
  output is reported operationally, not coerced into an accuracy result.
- The current public PyPI description is stale relative to local HEAD and
  contains high-consequence claims; the claim audit may itself block every
  capability regardless of synthetic accuracy.
- Demand remains unvalidated without interviews, representative buyer data,
  design-partner commitments or payment.

These limitations cannot be changed after benchmark output is visible.
