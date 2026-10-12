# Regula remediation report, 30 August 2026

## Finding

PARTIALLY READY. The current working tree materially improves Regula's
product-boundary, cache, assessment-sharing, MCP, REST, feedback, model-workflow,
website-source, evaluation-tooling and locked-CI controls. Supported generated
outputs now distinguish detector observations, declared context, missing or
contradictory context and accountable human decisions. They do not complete a
legal applicability, tier, duty, compliance, conformity or non-applicability
decision from source code alone.

The repository is not production-ready. It does not pass the representative
evaluation entry gate. The website is ready for local source and code review
only, not bounded public evaluation. The publication gate remains blocked,
current browser and human accessibility checks did not run, the second rating
does not exist and the Git index is read-only.

## Scope and evidence basis

OBSERVED: repository root `/home/USER/getregula`, branch
`feat/site-ux-redesign-2026-08-27`, HEAD
`fbed8f3baf81f0c5f0860ebaf56a2845b632b547`. The dated audit and post-audit
assurance package under `docs/audit/project-intelligence-2026-08-30/` was read
as untrusted evidence and checked against the working tree before material
changes.

No commit, push, deployment, publication, registry operation, external GitHub
mutation, outreach, form submission or package release occurred.

## Starting and ending repository state

OBSERVED at start: 65 tracked modified files, 13 untracked files, no staged or
deleted files; tracked diff 65 files, 1,806 insertions and 778 deletions. Every
path and provenance classification is recorded in
`STARTING_STATE_MANIFEST.md`.

OBSERVED at ending capture: 150 tracked modified files, 33 untracked files, no
staged or deleted files; tracked diff 150 files, 5,613 insertions and 2,397
deletions. `ENDING_STATE_MANIFEST.md` contains the exact final status and path
list. The 65 tracked and 13 untracked starting entries remain present. No
pre-existing file was deleted, stashed, reset, attributed to a person or
silently cleaned.

BLOCKED: normal and approved escalated attempts to stage only the five new
implementation files both failed because `.git/index` is read-only. Those
files are:

- `benchmarks/rating_packet.py`
- `scripts/evidence_review.py`
- `scripts/weekly_digest.py`
- `tests/test_product_boundary_contract.py`
- `tests/test_weekly_digest.py`

Exact source, test, content, workflow and documentation paths are also mapped
to findings in `FINDING_DISPOSITION_REGISTER.csv`. Where remediation touched a
path already dirty at the start, the pre-existing intent was read and preserved
through a compatible incremental change. Because no clean checkpoint existed,
line-level authorship within those 65 paths is UNVERIFIED.

## Product-boundary remediation

REPRODUCED: HTML, PDF, model-card, governance, conformity, sales and
no-findings paths could emit legal-tier, mandatory-duty, readiness or absence
conclusions while the original phrase guard passed.

Implemented public review schema 2.0 and a shared code-observation record. The
active CLI, JSON, REST, MCP, SARIF, evidence-pack, Annex IV, governance,
model-card, PDF, sales, conformity and browser adapters now preserve:

- observation, source location, indicator and detector-priority limitation;
- declared, missing and contradictory context;
- potentially relevant source references and unresolved reviewer questions;
- source and model provenance where available;
- explicit limitations and suggested human review steps;
- `human_decision: null` until an accountable reviewer acts.

Article 5, Article 6, Annex III and Article 50 browser paths use the same
boundary. A configured scan that finds no indicator states only that no
indicator was found by that scan. Gap evidence remains visible under
`held_article_observations` and is not converted into duties.

Compatibility: public decision schema 2.0 intentionally removes the old
`result_type`, `rule_resolution`, `indications`, `obligations`,
`outside_scope_basis` and `decision_trace` contract. A later owner-controlled
major release must manage that break. Historical ignored generated artefacts
were preserved and were not rewritten as current evidence.

## Cache correctness and durability

REPRODUCED: warm custom-rules A then B and B then A could return the opposite
configuration's result. The v7 key omitted effective custom rules, force and
exemption policy and the effective confidence threshold.

Cache schema v8 uses a canonical effective-configuration digest covering
rules, policy, thresholds, domain activation, parser mode, scanner semantics,
source identity and path-sensitive inputs. List order remains significant where
priority changes behaviour; mappings and sets are canonicalised. Persistence
uses atomic replacement, platform locking, dirty-key merge, corruption
recovery, bounded growth and explicit disable behaviour. Old entries are
invalidated because their effective configuration cannot be reconstructed.

REPRODUCED during challenge: a full stale-snapshot merge could overwrite an
unrelated concurrent update. Dirty-key ownership corrected that race. Native
Windows locking remains UNVERIFIED.

## Assessment-sharing evidence

REPRODUCED: share version 3 encoded absent and explicitly unsure states
identically, then padded missing positions into answered states.

Version 4 preserves unanswered, yes, no, unsure, not-applicable and
contradictory states, plus question-set, jurisdiction and decision-model
provenance. Missing fields, unknown values, mismatched question sets,
jurisdiction mismatches, malformed payloads and unsupported versions fail
visibly. Legacy links remain decodable but are labelled `legacy_lossy`; the UI
does not pretend lost state was recovered.

## Security and privacy boundaries

MCP: REPRODUCED that a system-root denylist authorised unrelated readable
paths. Startup now requires one existing workspace root. Lexical and resolved
containment, symlink escape, sensitive-path, text-size, file-count and
total-work controls apply. Audit events record tool, outcome, relative target
or input length and observation count, never supplied source text.

REST: REPRODUCED that `0.0.0.0` was accepted with only a warning. Non-loopback
binds now fail before server construction unless `--unsafe-network` is
explicit. The server still has no authentication, and the override says so.

Feedback: REPRODUCED that an external URL opened before exact preview and
consent. The command now minimises paths, displays the exact title, label and
body, requires interactive `yes` and cancels without browser or network action.

Weekly digest: OBSERVED repository write permission and direct commit and push
of model output. The workflow is now read-only, does not persist checkout
credentials, bounds and filters untrusted issue data, validates a strict known-
issue schema and writes only an escaped human-review job summary. No live
workflow was triggered.

## Website and public experience

INFERRED from repository evidence: the primary user is a developer or
governance reviewer deciding whether Regula is suitable for a repository,
examining a truthful example, running a local bounded workflow and preparing
material for accountable review.

The homepage now follows one journey: bounded role, observable inputs, unknown
context, concrete reviewable output, local data boundary, pinned supported
source path and links to methods, limitations, security, privacy and the
repository. Moving-branch and PyPI installation presentation was removed from
active guidance. Metadata and social descriptions were included in the
semantic contract.

REPRODUCED: five generated region pages had drifted. Their shared template and
source records were corrected, and the outputs now match byte-for-byte.
Coverage pages use the shared shell. Demonstrated recurring PT-BR diacritic
defects were corrected, but fluent German and Brazilian Portuguese review is
still external.

BLOCKED: current approximately 360, 768 and 1440 CSS pixel screenshots and
human keyboard, screen-reader, zoom, reflow, contrast, target-size,
reduced-motion and print checks. Loopback socket creation returned
`PermissionError`; browser session storage returned `EROFS`. Historical
screenshots were preserved but not treated as current evidence. No WCAG 2.2 AA
claim is made. See `WEBSITE_BEFORE_AFTER_REVIEW.md`.

## Evaluation-tooling readiness

REPRODUCED: existing real rating packets did not provide a shared usable item
identity and incomplete agreement handling was unsafe. Both utilities now
consume packet schema 1.0 with canonical identifier
`corpus-project-file-line-v1`, preserve blinded fields and report missing
overlap as incomplete.

Current real state: rater 1 has 50 labels, rater 2 has 0 and overlap is 0. No
second rating, agreement figure or representative detector-validity result was
manufactured. The representative-evaluation entry gate is BLOCKED.

## Release and reproducibility integrity

Controlling Linux CI lanes now pin `uv==0.11.0` and use
`uv sync --locked --extra test`. Public source installation examples use
`v2.0.0` or require an explicit `COMMIT_SHA`. The local `v2.0.0` tag resolves
to HEAD; remote existence and immutability are UNVERIFIED.

The local release gate accepts the required major bump. The publication gate
correctly remains BLOCKED on durable-name evidence, a fresh reachable privacy
audit, historical pull-request remediation and confirmed PyPI control. It was
not weakened.

## Finding disposition

The controlling row-level record is `FINDING_DISPOSITION_REGISTER.csv`.

- BLOCKED: F-002 and F-011.
- DEFERRED without speculative implementation: F-008 and F-009.
- PARTIALLY FIXED: F-007 and F-024.
- FIXED IN TESTED OR SOURCE SCOPE: F-003, F-004, F-005, F-013, F-014,
  F-016 through F-023, F-025 through F-027, C-003 and PQA-001 through
  PQA-003.

Each fixed disposition is limited by its CSV evidence and limitation columns.
It does not imply legal approval, production security, representative validity,
accessibility conformance or release readiness.

## Verification evidence

Environment: Python 3.12.3, Node v24.3.0, local HEAD as recorded above.

Passing controlling or focused checks:

- `git diff --check`: exit 0.
- generator checks for gap demo, qualifier, `llms-full` and public-surface
  inventory: exit 0.
- count cascade: exit 0, 2,984 collected tests, 1,334 custom-runner functions,
  119 test files and 62 commands, with an explicit warning for the two
  untracked new tests.
- site integrity: exit 0, five generated pages identical, 1,613 internal links,
  claims and version checks pass.
- locale-link audit: exit 0, 108 links across 12 pages, 0 detected defects.
- determination controls: 25 planted prohibited examples detected, 18
  qualified examples allowed; tracked-tree scan 519 of 738 files, 0 findings.
- claim audit: 117 surfaces and 269 fact references checked, all published
  canonical numbers match. Declared carrier exclusions remain limitations.
- assessment JavaScript: 254 of 254 assertions pass.
- release gate: exit 0, required major and actual major.
- focused migrated-schema regression: 2 passed.
- CLI self-test: 6 of 6 passed.
- doctor with `REGULA_AUDIT_DIR=/tmp/regula-audit-final`: 9 passed, 3 info.

Mixed or blocked checks:

- custom runner: exit 1, 1,463 passed, 1 failed and 8 skipped. The only failure
  is the Git tracked-input control for the two untracked test modules.
- full pytest: exit 1, 2,935 passed, 38 skipped, 3 failed and 8 errors before
  the two stale schema assertions were migrated. The migrated assertions then
  passed in a focused two-test run. One failure remains the Git tracked-input
  control. Eight setup errors are local RFC 3161 mock-server tests blocked by
  `PermissionError` on loopback socket creation.
- default doctor: exit 1 because `/home/USER/.regula/audit` is not writable in
  this sandbox. The documented writable audit-directory override passes.
- publication gate: exit 1 with the four external conditions named above.
- browser capture: BLOCKED by loopback and browser-storage permissions.

The documented chained short gate therefore does not pass unconditionally.
No failure, warning or publication condition was suppressed to report green.
Raw command results and phase-level evidence are retained in
`VERIFICATION_LOG.md`.

## Independent challenge conclusions

Staff engineering: the shared representations are limited to current callers;
the predicate engine remains separate; cache omissions, ordering, corruption
and stale writers have negative controls. The largest compatibility risk is the
intentional public schema break.

Product boundary: structured output assertions, planted semantic controls and
metadata, guide, locale and generated-output scans now support the boundary.
Qualified external legal review remains required.

Security and privacy: positive workspace authority, bounds, bind refusal,
consent and removal of model publication authority are material reductions.
Native Windows, macOS, intrusive testing and external GitHub configuration are
unverified.

Website and UX: source hierarchy, result state, locale links, errors and
responsive contracts are tested. Visual hierarchy and assistive-technology
acceptance remain unverified because no current browser run succeeded.

Testing: production adapters, negative controls and generated artefacts are
exercised. The full suite's remaining red conditions are preserved. A clean
checkout cannot reproduce the new test count until the Git index is writable
and the new files are reviewed and staged.

Scope: representative research, commercial validation, legal approval,
deployment, release, public GitHub changes and speculative features remain out
of scope.

## Remaining uncertainty and owner actions

Legal: current EU source status was not reverified on the web in this session.
Qualified review of Article 2, Article 5, Article 6, Annex III, Article 50 and
all consequential boundary wording remains external.

Language and accessibility: fluent locale review, current visual review and
human accessibility testing remain external. No conformance claim is supported.

Security: native Windows and macOS path behaviour, external workflow settings,
branch protection and independent security assessment remain unverified. The
optional REST server remains unauthenticated.

Evaluation and commercial: representative validity, two independent ratings,
agreement, adjudication, product-market fit and willingness-to-pay remain
unverified or deferred.

Release: the owner must provide a writable Git index, review and stage only the
intended files, rerun all gates from that exact state, complete the browser and
external assurance work, and clear the publication gate before any release or
bounded public evaluation.

## Final decisions

- Representative-evaluation entry gate: NO, BLOCKED.
- Website status: ready for local source and code review only.
- Bounded public evaluation: NO.
- Production readiness: NO.
- Publication or release authorised by this session: NO.
