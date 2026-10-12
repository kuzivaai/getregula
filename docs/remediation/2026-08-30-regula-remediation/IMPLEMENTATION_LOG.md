# Implementation log

## 30 August 2026, session start

- OBSERVED: root `/home/USER/getregula`, branch
  `feat/site-ux-redesign-2026-08-27`, HEAD
  `fbed8f3baf81f0c5f0860ebaf56a2845b632b547`.
- OBSERVED: 65 tracked modified files, 13 untracked files, no staged or
  deleted files.
- OBSERVED: push remains locally disabled through
  `no-push://history-reset-required`.
- OBSERVED: the complete dated audit package and consolidated document were
  read. Their engineering claims remain evidence leads until reproduced.
- OBSERVED: the roadmap supports the requested observation and
  evidence-preparation boundary.
- OBSERVED: ignored generated governance and model-card output contains legal
  tier and duty language. Those files are retained unchanged as evidence.
- Decision: begin with cross-surface product-boundary reproduction before
  cache, sharing, security and website changes.

## Phase 1 core generated-output boundary

- REPRODUCED: `regula report` generated a mandatory-obligations statement
  from one code match; the no-findings path generated a dominant absence
  verdict; the model-card generator emitted an EU AI Act risk classification.
- REPRODUCED: the existing determination guard and focused suite passed while
  those supported outputs remained unsafe. The original control was therefore
  insufficient for this defect class.
- OBSERVED: the internal predicate engine exposed `indications`, `obligations`
  and `outside_scope_candidate` through public adapters.
- Implemented `scripts/evidence_review.py` as the shared reviewable-evidence
  schema for code observations. It preserves source location, indicator,
  detector priority limitation, declared context, missing context,
  contradictions, candidate references, reviewer questions, review steps,
  limitations and an empty human decision.
- Implemented public declared-context schema version 2.0. Public adapters no
  longer expose internal legal-outcome fields or traces.
- Updated CLI text, REST, MCP, reports, PDF HTML, SARIF, evidence packs,
  questionnaire output, model-card and governance scaffolds, sales summaries
  and conformity evidence packs to use review language.
- Removed generated readiness percentages, conformity scores, inferred duties,
  legal tier, deadlines and pre-filled conformity decisions from the active
  conformity-pack path while preserving its article-organised file layout.
- Compatibility: the public decision object is intentionally schema-breaking.
  `result_type`, `rule_resolution`, `indications`, `obligations`,
  `outside_scope_basis` and `decision_trace` are replaced by the versioned
  review schema. This requires a major-version release decision outside this
  session.
- Remaining Phase 1 work: browser assessment, public guides, examples,
  structured data, locale output and wider semantic guard coverage remain open
  for the website phase.

## Phase 2 scan-cache correctness and durability

- REPRODUCED: with identical source bytes, a cache warmed under custom rules A
  served a stale prohibited observation under rules B. The reverse order hid
  the observation under rules A. The red run reported 19 passes and four
  intended failures, including the first policy collision.
- OBSERVED: the v7 key represented source content, relative path, full-path
  classifiers, scanner scope, AI-library context and ignore handling. It did
  not represent the effective custom rules, forced or exempt policy entries,
  or the effective confidence threshold.
- Implemented a deterministic effective-configuration digest. Mapping and set
  order are canonicalised; list order remains significant because configured
  rule priority can change the selected observation. The digest includes
  effective custom rules, force and exemption policy, effective minimum
  confidence, domain activation, parser mode and scanner feature semantics.
- Expanded the scanner implementation fingerprint to the modules that can
  change a cached per-file observation. Source bytes, file identity,
  path-derived classifiers, scan scope, ignore handling and AI-library context
  remain separate attributable key components.
- Bumped the cache schema from v7 to v8. Prior entries are not migrated because
  their effective configuration cannot be recovered and their correctness
  cannot be established.
- Added a versioned on-disk envelope, atomic replacement, platform-specific
  file locking, dirty-key merge semantics, a 10,000-entry default bound,
  visible corruption and persistence errors, and explicit
  `REGULA_DISABLE_CACHE` handling.
- REPRODUCED during adversarial review: merging an entire stale in-memory
  snapshot could revert a concurrent writer's update to an untouched key.
  Corrected this before phase closure by merging only keys changed by the
  current cache instance.
- Compatibility: the first scan after this change is deliberately cold. Cache
  contents are a private performance artefact, not a public data contract.
- Remaining limitation: Windows locking code is present but was not executed
  in this WSL2 session. Cross-process locking and merge behaviour were executed
  on Linux.

## Phase 3 assessment sharing evidence

- REPRODUCED: the existing version 3 encoder converted both a missing answer
  and an explicit `unsure` answer to `u`. The decoder padded every shorter
  payload with `u` and returned each padded position as an explicit `unsure`.
- OBSERVED: the three locale pages already contained compatible, unrelated
  redesign changes. Those changes were preserved. The share fix is centred in
  the previously clean shared adapter and flow files; locale pages received
  only their recovery copy.
- Implemented share schema version 4 as base64url-encoded JSON with an explicit
  state for every question. Supported codec states are `unanswered`, `yes`,
  `no`, `unsure`, `not_applicable` and `contradictory`. Missing state fields
  are malformed rather than padded.
- Added question-set, jurisdiction and decision-model provenance. Unknown
  answer identifiers, malformed payloads, mismatched jurisdictions, mismatched
  question sets and unsupported versions fail explicitly.
- Legacy versions remain decodable but are labelled `legacy_lossy`. The UI
  warns that older formats converted missing answers to explicit uncertainty.
- Contradictory shared evidence is preserved by the codec but is not sent to
  automatic evaluation. The UI shows a recovery message and creates no result.
- Added localised recovery copy for EN, DE and PT-BR. Fluent and legal-language
  review of the translated wording remains external.
- Browser rendering was BLOCKED: loopback socket creation returned
  `PermissionError`, and browser automation could not create its session file
  because that cache path is read-only. Production flow behaviour was instead
  exercised with a bounded DOM harness in the existing Node gate. Visual
  rendering remains unverified.

## Phase 4 security and privacy boundaries

- OBSERVED: the MCP server relied on a system-directory denylist. A client
  could request any other readable path, `regula_gap` had no workspace
  capability, and text input had no MCP-specific size limit.
- Implemented one explicit existing workspace root for each MCP server
  process. Path tools perform lexical containment before filesystem probes,
  resolved containment after symlink resolution, sensitive-path exclusion,
  file-count and total-byte preflight, and bounded request and text reads.
- MCP scans disable the configuration-file pass, and MCP gap assessment uses
  a sensitive-path-excluding walk. Local audit events record tool name,
  outcome, relative target or input length, and observation count, never the
  supplied source or text.
- OBSERVED: the REST server accepted a non-loopback host without any distinct
  acknowledgement despite having no authentication. It now accepts loopback
  by default and fails before server construction for any other bind unless
  `--unsafe-network` is supplied.
- OBSERVED: feedback opened a pre-filled external URL without showing its
  decoded fields or obtaining confirmation. It now minimises file paths,
  redacts common absolute paths from descriptions, shows the exact title,
  label and body, and opens a browser only after an interactive `yes`.
- OBSERVED: the weekly digest granted `contents: write`, sent issue bodies to
  a model, wrote model text to `TRIAGE.md`, then committed and pushed it.
  The workflow now has read-only contents permission and no persisted checkout
  credentials. Inputs are bounded and filtered, issue text is marked as
  untrusted data, output must match an exact known-issue schema, and the
  escaped draft is written only to the human-review job summary.
- Remaining limitations: Windows MCP path and lock behaviour is unexecuted;
  the REST server still has no authentication; no external workflow run or
  branch-setting inspection occurred; GitHub submission remains the user's
  action after feedback preview.

## Phase 5 website and public experience

- OBSERVED: the existing dirty tree contained a substantial light-theme
  redesign. Its layout and content intent were preserved. Remediation focused
  on semantic alignment, the primary journey, result integrity, generated-page
  drift, locale meaning and the shared trust shell.
- OBSERVED: public metadata, guides, examples and result paths used stronger
  compliance or determination wording than the implemented product boundary.
  Article 50 output did not carry the same role, context, condition and
  exception caveat as other decision paths.
- Implemented one homepage journey from bounded purpose, through a concrete
  observation example and explicit unknowns, to the currently supported
  pinned source evaluation path. Removed PyPI and moving-branch presentation
  from active installation guidance.
- Applied the review schema to the browser assessment. Article 5, Article 6,
  Annex III and Article 50 results expose observations, potentially relevant
  provisions, missing context, reviewer questions and blank human decisions.
- Implemented share schema version 4 and visible recovery for malformed,
  unsupported and lossy legacy links across EN, DE and PT-BR.
- REPRODUCED: five generated region pages had drifted from their sources.
  Updated the shared template and source records, then regenerated the pages.
  The site-integrity check now reports five byte-identical outputs and 1,613
  resolving internal links.
- Corrected demonstrated recurring PT-BR diacritic defects on six canonical
  pages. Added a narrow regression control. Fluent review remains external.
- REPRODUCED: current browser capture could not run. Local loopback binding
  returned `PermissionError`, and browser storage returned `EROFS`. No current
  screenshot, visual acceptance or human accessibility claim is made.

## Phase 6 evaluation-tooling readiness

- REPRODUCED: the two real rating packets did not share a usable canonical
  item identity, and agreement computation could not process the incomplete
  packet state safely.
- Added packet schema version 1.0 and canonical identifier scheme
  `corpus-project-file-line-v1`. Both utilities now consume that schema,
  preserve blinded fields and report missing overlap as incomplete.
- REPRODUCED: rater 1 has 50 labels, rater 2 has 0, and overlap is 0. No second
  rating or agreement result was manufactured.
- Representative detector validity remains BLOCKED on later independent human
  evaluation.

## Phase 7 release and reproducibility integrity

- OBSERVED: controlling CI lanes installed ranged test extras instead of the
  repository lock. Updated the Linux controlling lanes to pin `uv==0.11.0`
  and use `uv sync --locked --extra test`.
- Replaced moving-branch install examples with `v2.0.0` or an explicit
  `COMMIT_SHA`. The local tag resolves to the current HEAD. Remote tag state is
  UNVERIFIED because no network verification succeeded.
- REPRODUCED: the local release gate passes the required major-version check.
- REPRODUCED: the publication gate remains blocked on four controls and was
  not weakened.
- BLOCKED: `.git/index` is read-only. A normal and an approved escalated
  `git add` both failed with `Read-only file system`, leaving five
  session-created implementation files untracked. The full Git-based gate
  cannot be reported green until that environment boundary is removed.

## Challenge passes

- Staff engineering: narrowed shared abstractions to current callers; retained
  internal predicate logic; tested cache collision, stale-writer and
  corruption paths; recorded the public schema break.
- Product boundary: searched generated output, metadata, headings, badges,
  guides, locales and structured data; combined planted semantic controls with
  structured renderer assertions.
- Security and privacy: exercised hostile MCP paths, symlinks, sensitive names,
  input bounds, REST bind refusal, feedback cancellation and hostile model
  input. Native Windows and external GitHub settings remain unverified.
- Website and UX: tested source structure, locale links, assessment journeys,
  malformed sharing, generated integrity and responsive CSS assertions. Visual
  and human assistive-technology review remains blocked.
- Testing: retained red-first evidence, added negative controls that reach
  production adapters, and did not weaken the publication gate.
- Scope: deferred commercial validation, representative evaluation, legal
  approval, deployment, release and intrusive testing.
