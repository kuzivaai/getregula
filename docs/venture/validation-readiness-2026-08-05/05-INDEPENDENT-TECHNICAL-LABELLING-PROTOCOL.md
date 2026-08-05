# Independent technical-labelling and comparison protocol

STATUS: PREPARATION ONLY
EXTERNAL ACTION: DISABLED
VENTURE DECISION: STOP
PRODUCT PILOT: NOT APPROVED

Protocol status: `PREREGISTERED_NOT_EXECUTED`.

## Construct and population

Exact technical job: for an atomic claims-triage onboarding buyer requirement,
identify technically observable repository evidence that supports, contradicts or
cannot assess the supplier response, with a reproducible source pointer. It does
not classify legal risk or compliance.

Target population is permissioned repositories and associated technical
artefacts for small UK suppliers whose AI-assisted claims-triage systems reached
general-insurer production onboarding. This is a purposive exploratory population;
discovery must document the sampling frame, approach flow, exclusions and coverage
limits rather than claim representativeness. Mirrors, tutorials,
synthetic fixtures, Regula development examples and repositories seen during
detector development are excluded from the prospective holdout.

Unit: one frozen buyer-requirement × repository-evidence decision, clustered
within repository and transaction. Required labels are `PRESENT_SUPPORTED`,
`PRESENT_CONTRADICTORY`, `NOT_FOUND_IN_FROZEN_REVIEW_SCOPE`, `NOT_ASSESSABLE`, `ABSTAIN` and
`OUT_OF_SCOPE`, each with file/line or artefact pointer, rationale, confidence and
review time.

## Independence, freeze and leakage controls

- At least two independent qualified human raters, neither Codex, an LLM,
  subagent nor Kuziva counted as an independent pair.
- Raters disclose employment, financial, authorship and tool conflicts.
- Raters are blind to Regula and baseline output until initial labels are frozen.
- Development/calibration examples are separate from the prospective holdout.
- Regula commit, tree, configuration, runtime and transparent baseline are frozen
  before holdout labels are opened.
- Corpus manifest records licence, permission, provenance, hashes, inclusion and
  every failed or excluded run. Silent exclusion is prohibited.

## Training, disagreement and analysis

Raters train on non-study examples, independently label a calibration set, discuss
codebook ambiguity, then repeat on a new calibration set. No universal agreement
cut-off is asserted. Report raw agreement and an appropriate chance-corrected
measure with uncertainty only after label prevalence is known. Retain raw
disagreements. Adjudication is by a third qualified person or documented panel;
the adjudicated label never replaces raw labels.

Compare frozen Regula separately with (1) a deterministic transparent lexical
baseline and (2) the blinded manual workflow; do not combine them into one
comparator. Report per-method confusion fractions, precision, recall, abstention,
not-assessable rate, false-alert review time, evidence-pointer validity and failed
runs. Report repository-level distributions and language/category strata; do not
treat clustered units as independent. Use paired repository-level intervals or a
cluster-aware model only if data support it. Report null and adverse results.

Previous thresholds are not reused because the buyer construct, unit and
population differ from commercial_v1. Before outputs are opened, preregister a
minimum safety condition of no higher unsupported-evidence rate than baseline and
one primary benefit metric selected by a frozen rule tied to the discovery
workflow: choose time saved only where both methods complete the same units;
otherwise choose evidence-pointer validity. Record the selection before any
comparison output is opened. Without a defensible effect
size, the first study is exploratory and cannot prove external efficacy.

## Order

Owner/professional readiness, permissioned discovery, blinded manual baseline,
independent labelling and frozen comparison, then and only then an owner decision
on assisted delivery. Payment cannot substitute for accuracy; accuracy cannot
substitute for demand.
