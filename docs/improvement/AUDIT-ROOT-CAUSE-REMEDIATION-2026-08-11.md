# Regula audit, root cause analysis, and remediation architecture

**Date:** 2026-08-11

**Scope:** Phases 0 to 2 only

**Measurement commit:** `136cdbfc60d8bf4d2bec12d8a95456a74e1a5957`

**Measurement tree:** `958548d019b029c96f55c53fb912e5fdcbd32d89`
**Branch:** `fix/regulatory-currency-2026-08-06`

This record distinguishes three classes of statement:

- **Demonstrated:** the implementation was read or a command was run. The consolidated handover contains the command and verbatim output.
- **Asserted:** a record, comment, test name, or external document says this, but this session did not independently establish it.
- **Interpreted:** an inference. Its assumptions and falsifier are stated.

Unless an external source or later documentation commit is explicitly named, every repository figure and code observation in this record was measured at the commit and tree above. The evidence appendix in the consolidated handover is part of this record. Evidence identifiers below name the verbatim appendix blocks.

## Scope controls and records read

**Demonstrated.** Before investigation, the session read these files from start to finish:

1. `AGENTS.md`.
2. `.handover.md`, the repository's most recent root handover.
3. `docs/improvement/LEDGER.md`, 1,227 lines and 212,073 bytes before this session's additions.
4. `docs/MODEL_CARD.md`, 175 lines.
5. `docs/improvement/VERDICT-RECORD-2026-08-06.md`, 137 lines and the most recent verdict record selected by the filename predicate.
6. `docs/improvement/HANDOVER-CLAIM-SCOPE-2026-08-05-195731.md`, 1,098 lines and the most recent dated repository handover selected by the filename predicate.
7. `/mnt/c/Users/USER/Downloads/Regula_Deep_Dive_Review_2026-08-11.docx`, extracted without modification to text, 675 lines, 9,058 words, and 68,326 bytes.
8. `/home/USER/.codex/skills/playwright/SKILL.md`, because this audit used a real browser.

The extracted 11 August review was treated as **Asserted** and only as a lead generator. None of its findings was promoted to Demonstrated without an independent source read, command, or browser reproduction.

**Asserted, controlling owner decision.** `docs/improvement/VERDICT-RECORD-2026-08-06.md` records `PRODUCT_BUILD: STOP`, `VENTURE_DECISION: STOP`, `STAGE_A_PACK: HOLD`, `EXTERNAL_CONTACT: NOT_AUTHORISED`, `REAL_DATA_COLLECTION: DISABLED`, `H1: ABANDONED`, `H2: NOT_CREATED`, `WTP: UNVALIDATED`, and `PILOT: NOT_APPROVED`. This session did not alter those fields, publish, deploy, release, contact anyone, spend, or collect real data.

## Executive finding

**Interpreted, supported by the demonstrated paths below.** Regula does not currently have one legal-decision system with several adapters. It has several decision systems with incompatible input contracts and a shared vocabulary. They conflate absence of evidence, explicit negative evidence, and unresolved facts; use heuristic scores as confidence; and attach articles or duties through tier defaults or additive thresholds instead of satisfied legal predicates. The assurance layer mostly verifies internal consistency with current artefacts. It can therefore certify unsafe current behaviour.

The immediate consequence is larger than a wrong screen. An all-unknown browser EU assessment produces a high-risk result, Articles 9 to 15, fixed readiness percentages, implementation-hour ranges, and a JSON file that the page invites the user to share with compliance, development, and legal teams. The exported document retains every answer as `unknown`. This is a demonstrated downstream regulatory artefact path.

The honest remediation is a redesign of the decision contract and its epistemic model. Adjusting the questionnaire's weights would leave the same generator active in the scanner, gap assessment, API, MCP, browser jurisdictions, and editor adapter.

## Phase 0a: state and verification

### Repository state

**Demonstrated.** Evidence `00-state` reports:

```text
CAPTURED_RC=0
HEAD 136cdbfc60d8bf4d2bec12d8a95456a74e1a5957
tree 958548d019b029c96f55c53fb912e5fdcbd32d89
branch fix/regulatory-currency-2026-08-06
origin/main a14a1879743bdd9be02a8080a0b662e97eaf4d48
origin/main...HEAD 0 6
latest tag v1.9.0
tag...HEAD 0 201
```

The porcelain status block was empty. The branch was six commits ahead of `origin/main` and 201 commits ahead of `v1.9.0`, with no commits behind either comparison point.

### Mandated verification chain

Each command wrote output to a file that was deleted before the run. Its exit code was captured from `$?` in a separate file.

| Command | Captured result | What that result establishes |
|---|---:|---|
| `python3 tests/test_classification.py` | 0; 1,390 passed, 0 failed, 0 skipped; 1,098 runner functions | The custom runner selected and passed those registered functions. It does not establish the pytest suite or semantic correctness. |
| `python3 -m pytest tests/ -q` in the sandbox | 1; 2,720 passed, 1 failed, 8 errors | The collected cases other than the reported failure/errors passed in this run. Eight errors were localhost socket permission errors, not assertion failures. |
| `python3 -m pytest tests/test_manifest_timestamp.py -q` outside the sandbox | 0; 23 passed in 6.70s | The timestamp test module passes when its localhost mock server can bind. |
| isolated published-count test | 1; 1 failed in 0.34s | The count-literal failure reproduces independently on the unchanged tree. |
| `python3 -m scripts.cli self-test` | 0; 6/6 | Six built-in smoke checks passed. |
| `python3 -m scripts.cli doctor` in the sandbox | 1 | The audit directory was not writable under sandbox policy. |
| the same doctor command outside the sandbox | 0; 8 passed, 4 info | The doctor failure was environmental under this execution policy. |

**Demonstrated new contradiction.** The isolated pytest failure identifies `docs/improvement/LEDGER.md` because N78 includes the bare current count in prose while N78 declares the alphanumeric count-collision class closed. The count gate is therefore both catching a real current invariant violation and disproving its own closure record. This was not in the 11 August review.

### Fast gates and named gates

All gate results below are from the measurement commit and tree.

| Gate | RC | Demonstrated invariant actually enforced | Specific demonstrated or constructed counterexample it misses |
|---|---:|---|---|
| `scripts.claim_verify --facts` | 0 | Typed numeric fact references agree with the current fact registry for 148 references in 17 files. | A page can cite the right fact identifier while its prose falsely calls a stale 13-item benchmark current. Semantic support is not checked. |
| site integrity | 0 | Generated regional pages match, 1,173 enumerated references resolve, configured source markers exist, and guarded version strings agree. | The current all-unknown assessment produces a definitive high-risk export and the gate still passes. |
| cascade count | 0 | The canonical collected-test figure appears on 11 manifest-listed surfaces in the expected rendering. | PyPI still publishes a different test badge and is outside this repository cascade. The gate also passed before the full suite exposed the bare count in the ledger. |
| recall artefact | 0 | Recomputing against the same sanctioned fixtures and labels reproduces the committed recall artefact. | Incorrect or unrepresentative labels can reproduce perfectly. Reproducibility is not external validity. |
| gap demo | 0 | The committed gap-demo output matches a fresh run on its fixture. | A constructed TensorFlow hiring project produced `highest_risk: not_ai` while the gap engine still emitted Articles 9 to 17. Deterministic reproduction does not validate applicability. |
| self-reference control | 0 | A page cannot satisfy a sourcing requirement solely by citing itself, and the positive sourced fixture passes. | A real external URL that does not support the accompanying sentence still satisfies URL presence and source-class checks. |
| merge blocker | 0 outside sandbox | No finding in its computed `introduced` set also appeared in its computed `published` set. | Existing public false claims and current unsafe questionnaire behaviour are not newly introduced/published intersections and pass. |
| claim delivery auditor | 0 | 530 enumerated delivery-surface claim records across 96 files carry an accepted source marker. | It does not determine whether the source entails the claim. The stale benchmark and broad Article 50 prose remain. |
| release gate | 0 | Changelog sections and the delta from its configured previous version require a minor bump, and `1.9.0` is a minor bump from `1.7.10`. | It does not reject 201 post-tag commits that retain the already published `1.9.0` identity, and it does not inspect a built wheel. |

**Interpreted.** None of these gates is perfect. Each is intentionally or accidentally scoped to a mechanical predicate. The counterexamples show that their names must not be interpreted as legal accuracy, efficacy, release reproducibility, or safe user behaviour.

## Phase 0b: decision paths traced from code

The path enumeration predicate selected direct calls to `evaluate_questionnaire`, `classify`, `scan_files`, `assess_compliance`, and the artefact generators; all CLI `set_defaults` bindings; all REST route branches; all MCP tool definitions; both VS Code command registrations; and all browser decision-function definitions. Evidence `12-path-enumeration` itemises 57 direct Python calls, 64 CLI bindings, 7 REST routes, 3 MCP tools, 2 editor commands, and 7 browser decision functions, with each total reconciled to its itemisation.

### CLI questionnaire

Path: argparse binding in `scripts/cli.py` -> `scripts/cli_analysis.py::cmd_questionnaire` -> JSON load -> `scripts/questionnaire.py::evaluate_questionnaire` -> `QuestionnaireResult` -> text or the standard CLI JSON envelope.

- **Validation:** JSON syntax and file I/O are caught. The decoded root type, known question identifiers, completeness, and answer values are not validated by the CLI path.
- **Unknown:** missing known keys use `.get(question_id, "unsure")`. Unknown keys are ignored. An explicit `unsure` is assigned a numeric weight. A list or string reaches `.get` and becomes an internal error.
- **Confidence:** the evaluator returns the literal label `high` for every outcome. `confidence_score` is the final additive score, not an estimate of correctness.
- **Obligations:** score thresholds select a tier. High-risk attaches Articles 9 to 15. Limited-risk attaches Article 50. Attachment does not require a named legal predicate to be true.

The direct probe demonstrated that `{}`, all eight `unsure` answers, and an unknown-only key all yield `limited_risk`, `high`, score 56, and Article 50. An invalid known value also produced a result through the direct function and CLI. A partial API-valid map with only `deployment_eu: no` yields limited risk, high confidence, score 49, and Article 50.

### CLI `classify`

Path: CLI binding -> `scripts/cli_scan.py::cmd_classify` -> `scripts/classify_risk.py::classify` -> prohibited patterns -> policy override -> AI-related predicate -> high/limited patterns -> minimal fallback -> `Classification` -> CLI output.

- **Validation:** file/input selection is validated by argparse-level control. The classifier accepts any string, including an empty string when called by another adapter.
- **Unknown:** there is no unknown state. No pattern evidence maps to `not_ai` with action `allow` and confidence `high`.
- **Confidence:** `_compute_confidence_score` is a tier base plus match-count bonus plus AI-context bonus. The categorical confidence labels are branch constants or match-count labels. No representative calibration set or conditional error estimate is consulted.
- **Articles:** prohibited patterns attach their configured Article 5 reference; high-risk patterns union their configured article lists; limited risk attaches Article 50 unconditionally when that tier matches. No applicability evidence object is required.

The direct empty-string probe returned `not_ai`, `allow`, `high`, confidence score 0. This demonstrates a category mismatch between the confidence label and its numeric field.

### CLI `check`

Path: CLI binding -> `scripts/cli_scan.py::cmd_check` -> `_validate_path` -> `scripts/report.py::scan_files` -> safe filesystem walk -> per-file `classify` plus credential/security/autonomy detectors -> context/domain adjustments -> findings -> text, JSON, SARIF, HTML, or manifest paths.

- **Validation:** the path, safe-read conditions, supported extensions, size/symlink constraints, ignore directives, scope, and selected CLI values are checked at several layers. A partial scan is represented through `scan_files.last_stats`, not in each finding.
- **Unknown:** no classification unknown exists. Eligible unreadable or undecodable files are tracked as skips, but a readable file with insufficient contextual evidence becomes no finding, `not_ai`, or minimal risk.
- **Confidence:** finding confidence is recomputed from a tier base, number of indicators, domain boosts, and fixed penalties/caps for test files, examples, infrastructure paths, string context, and self-scans. It is a prioritisation score, not calibrated correctness probability.
- **Articles:** the classifier's pattern-configured article list is copied into each finding. SARIF rendering consumes the finding configuration and includes Article 50 language for limited-risk rules.

On the constructed 153-byte TensorFlow hiring file, `regula check --format json` returned an empty findings array and RC 0. This does not establish that all hiring systems are missed; it demonstrates this concrete input and the limited evidence discovery of this path.

### CLI `gap`

Path: CLI binding -> `scripts/cli_compliance.py::cmd_gap` -> path validation -> `scripts/compliance_check.py::assess_compliance` -> project walk -> `_determine_highest_risk` -> all requested article checkers -> arithmetic mean -> output.

- **Validation:** project must be a directory. Requested article values not present in `ARTICLE_CHECKERS` are silently omitted. The API limits article types but does not validate membership.
- **Unknown:** evidence absent for an article is converted to a low score and gaps. There is no not-applicable or insufficient-information state.
- **Confidence:** the reported percentages are evidence-presence scores from checkers and an unweighted mean. They are not called classifier confidence, but the UI/status labels use them as strength/readiness.
- **Obligations:** by default all Articles 9 to 15 and 17 are checked regardless of the `highest_risk` result. Regulation-overlap duties attach only when highest risk is high or prohibited, but the EU article gap set is unconditional.

The same constructed file yielded `highest_risk: not_ai`, overall score 2, and gap entries for Articles 9 to 17. That is an applicability contradiction, not merely low recall.

### REST API

Path: `scripts/api_server.py` route -> `_read_json_body` -> handler-specific accessors -> the same Python questionnaire, classifier, scanner, or gap function -> `_build_envelope` on success.

- **Validation:** content type, content length, body presence, maximum nesting, and JSON syntax are checked. `_read_json_body` returns any JSON root while declaring `dict`. Handlers call `.get` before validating the root. Array and string roots therefore raise `AttributeError`, close the connection, and print a traceback instead of returning an API error. Path and selected field validation varies by handler.
- **Unknown:** questionnaire empty maps are rejected, but partial maps and unknown question identifiers are accepted. This differs from the CLI while reaching the same evaluator. The other three engines have the unknown behaviour described above.
- **Confidence and articles:** inherited from the called core implementation.
- **Envelope:** successful v1 decisions use the standard envelope. `_send_error` uses `{error,status}` and health uses a third shape. This is an intentional current test expectation, not a uniform contract.

The API probe demonstrated HTTP 200 and a definitive limited/high/Article 50 result for a partial answer map and for an unknown-only question map. Invalid values received HTTP 400. Array/string roots caused `RemoteDisconnected` plus server tracebacks.

### Browser assessment

Path: `site/assess/{index,de,pt-br}.html` form or decoded share URL -> `calculateResults` -> one of `calculateResultsEU`, `calculateResultsKR`, or `calculateResultsCO` -> rendered result -> `exportJSON`, print/PDF, clipboard, or share URL.

- **Validation:** each question radio group can represent `yes`, `no`, or `unknown`. `decodeAnswers` pads missing encoded characters and maps invalid characters to unknown. There is no versioned schema or rejection path.
- **Unknown:** unknown contributes fixed points. It is not an abstention state. EU, Korea, and Colorado use separate additive functions. The three locale files contain copied scoring implementations.
- **Confidence:** displayed scores are additive heuristics. The UI labels them precise scoring and derives readiness percentages and effort ranges in EU output.
- **Obligations:** EU score/tier branches attach Articles 9 to 15 or Article 50. Korea and Colorado attach branch-specific cards or recommended actions. Unknown inputs can select definitive branches.

Real-browser controls demonstrated:

- All-unknown EU: high risk, score 91, Articles 9 to 15, readiness percentages, fixed hour ranges, and a 2,127-byte JSON export containing every answer as `unknown`.
- All-unknown Korea: `General AI system`, score 72, and a next step that says Article 31 requires transparency notices.
- All-unknown Colorado: `Not covered ADMT`, score 78. The pre-measurement prediction of positive obligations was wrong; the broader predicted epistemic failure landed as a definitive negative determination under total uncertainty.
- At 320 by 800 CSS pixels, the homepage has a 15,476-pixel scroll height and no horizontal overflow in that measurement.
- Opening the mobile menu and pressing Escape leaves the menu button expanded and the dialog present.

String-normalised comparisons showed the EU, Korea, and Colorado scoring functions are currently byte-identical across the three locales after translated strings are normalised. That falsifies current behavioural locale drift for those functions, while confirming three copied implementations. `exportJSON` differs: PT-BR adds a `locale` field that EN and DE omit.

### Browser scanner

Path: code pasted or uploaded -> `runScan` in each locale page -> `site/assess/scanner.js::scanCode` -> `classifyCode`, security checks, and observations -> rendered findings.

- **Validation:** browser file/input limits and filename-based language detection are adapter controls. The scanner is a static JavaScript port of the Python patterns.
- **Unknown:** absent pattern evidence becomes `not_ai` or minimal risk, not unresolved.
- **Confidence:** `_confScore` mirrors the classifier's fixed bases and match-count/context bonuses. `not_ai` has confidence label high and score 0.
- **Articles:** copied from the first prohibited pattern, the union of high-risk pattern articles, or Article 50 for any limited-risk match.

The scanner decision engine is distinct from the browser questionnaire and from Python `report.scan_files`. It shares patterns and some formulas, not one runtime or one enforced contract.

### MCP tools

Paths:

- `regula_check` -> `_validate_scan_path` -> Python `scan_files` -> plain text.
- `regula_classify` -> required non-empty `input` check -> Python `classify` -> plain text.
- `regula_gap` -> `_validate_scan_path` -> Python `assess_compliance` -> plain text.

The MCP tool declarations provide JSON-schema-like input shapes, but `handle_request` takes the `arguments` map and does not execute a schema validator. Missing values receive local defaults. Decision confidence and articles are inherited from the Python engines. Errors can be returned as successful tool text beginning `Error:` rather than JSON-RPC tool errors. No unknown decision state is added.

### VS Code extension

Paths: `regula.scanFile` or `regula.scanWorkspace` -> `execFile` of `regula check --format json` -> `extractFindings` -> diagnostics and findings tree.

- **Validation:** TypeScript locally types a finding, but no runtime schema validation occurs. `extractFindings` returns an empty array for valid JSON with an unexpected envelope shape.
- **Unknown:** there is no stale, incomplete, or indeterminate diagnostic state.
- **Confidence and articles:** copied from CLI findings and used for display/severity.
- **Failure behaviour:** a single-file parse failure after non-zero CLI exit deletes that file's diagnostics. A valid but unexpected response clears to zero findings. Workspace processing clears all old diagnostics after any successfully parsed unexpected shape.

This is a new material finding absent from the prior review: API/CLI schema drift can present as a clean editor scan and erase prior warning state. Runtime execution of the extension was not completed because its own test command does not type-check, so the failure path is Demonstrated from implementation, not from an extension-host experiment.

## Phase 0c: downstream artefact propagation

### Questionnaire path

**Demonstrated.** The Python questionnaire result has three direct evaluator callers: the CLI questionnaire command, the REST questionnaire endpoint, and the module's standalone main path. The direct-call predicate found no Python path from `evaluate_questionnaire` into evidence packs, Annex IV, conformity packs, reports, SARIF, or DPV exports.

**Demonstrated.** The browser questionnaire has its own downstream path. Its result directly feeds DOM output, printing/PDF, clipboard/share links, and `exportJSON`. The all-unknown EU export is a regulatory-looking artefact with tier, score, articles, deadline/readiness/effort fields, and raw unknown answers. The page invites sharing with compliance, development, and legal teams. Therefore unresolved input can reach a handable regulatory artefact.

### Scanner and gap path

**Demonstrated.** Python `scan_files` directly feeds:

- evidence-pack scan output and risk decisions;
- conformity-pack findings;
- DPV export;
- general reports and SARIF;
- documentation generation through the related `scan_project`/`classify` path.

`assess_compliance` feeds evidence and conformity packs. Documentation generation produces Annex IV and conformity-declaration scaffolds. Annex IV and DPV contain human-review or risk-indication qualifications, but those qualifications do not repair a wrong underlying finding or unconditional article check. A result can therefore propagate into a package explicitly named an evidence pack or conformity pack. The exact source slices are in evidence `43-artifact-source`.

**Interpreted.** The browser all-unknown export is the highest-consequence demonstrated live path because it requires no repository scan or malformed input and preserves evidence of total uncertainty while still presenting definitive duties. The evidence/conformity pack path may be as consequential, but this session did not construct a third-party handoff experiment for every generator. That remains open.

## Phase 0d: the suite as an artefact

At the measurement commit/tree, pytest selected 2,729 cases in the full run. The Python AST predicate found 2,701 `test_*` functions across 106 Python test files; parameterisation and non-Python tests explain why function and case counts are different. The custom runner selected 1,098 functions.

The audit did not label every mock-based test defective. It used reproducible predicates and then described exactly what each predicate proves.

### Exit asserted while output is discarded

The AST predicate selected a test when it destructured or stored command output, asserted only the exit/result code, and never read the output variables in an assertion. It enumerated 13 tests and reconciled 13 items. They are itemised verbatim in evidence `21-test-smell-enumeration`.

These tests can prove command completion for their fixture. They cannot detect semantically wrong output. Three use empty projects or an empty directory: governance empty project, model-card empty project, and the generic empty-directory scan.

### Decision output guaranteed by a fixture

The refined AST predicate selected an API test when it replaced `classify`, `scan_files`, `assess_compliance`, or `evaluate_questionnaire` with `MagicMock(return_value=...)` and asserted HTTP status or response body. It enumerated 16 tests and reconciled 16 items. These are adapter tests. Their decision-output assertions are independent of the real engine and would pass if the underlying classifier or evaluator regressed while the adapter remained unchanged.

The related broad predicate found 53 tests with an assertion and a local patched return value or lambda. That broader set includes legitimate failure injection, filesystem isolation, and protocol tests, so it is recorded as a manual-review candidate set rather than misreported as 53 defective tests.

### Scans nothing

The exact API predicate selected four tests where `scan_files` is replaced by `MagicMock(return_value=[])`. A fifth set of three exit-only cases uses actual empty project fixtures. The four API items are enumerated in evidence `23-refined-test-predicates`; the three command items are named above. Some tests occur in more than one category.

### Known defect encoded as expected behaviour

The exact source predicate selected four expectations:

1. `all_unsure_cautious_default` requires all-unknown answers to yield limited risk, high confidence, and a positive score.
2. `missing_answers_default_to_unsure` requires an empty map to produce a positive score and tier.
3. `test_health_response_is_not_enveloped` requires the health response's contract divergence.
4. `test_mobile_menu_uses_non_modal_dialog_on_all_pages` requires `show()` and forbids `showModal()` but asserts neither Escape closure nor focus restoration.

The first two would reject a fail-closed epistemic repair unless changed to assert the new invariant. The third preserves a deliberately divergent contract. The fourth certifies the code shape implicated in the observed keyboard defect.

### Reconciled fraction

The union of the exact Python predicates is 32 distinct pytest test functions: 13 exit/output-discarded, 16 fixture-guaranteed response tests, two Python known-defect expectations, and one additional empty-scan API test not already in those sets. At commit `136cdbfc`, tree `958548d0`, that proxy set is `32 / 2,729 = 1.173%` of pytest cases if each function contributes one selected case. Two JavaScript known-defect assertions sit outside the pytest denominator. This is a lower-bound proxy, not an assertion that the other 98.827% prove correct behaviour. Parameterisation means a function-to-case fraction is approximate; a case-exact collection map was not built, so claiming a more exact fraction would fabricate precision.

## Phase 0e: gate conclusion

The counterexample table in Phase 0a is the requested gate audit. Every gate admits a concrete missed condition. None is blind to everything: each catches its named syntactic or consistency invariant. None establishes the product-level property suggested by words such as integrity, delivery, recall, or release. The suite itself demonstrates the risk: all six fast gates returned zero while full pytest independently failed on the current clean tree.

## Phase 0f: findings absent from the 11 August review

The prior review contained 18 numbered findings. Independent reproduction found support for 17 and reproduced the remaining pytest failure at a different exact current manifestation. The following material findings were absent or materially incomplete there:

1. **Downstream unknown export:** all-unknown EU answers reach a 2,127-byte shareable JSON artefact containing high-risk status and Articles 9 to 15.
2. **Jurisdictional epistemic failures:** all-unknown Korea produces Article 31 action language; all-unknown Colorado produces a definitive not-covered result.
3. **Gap applicability contradiction:** a project classified `not_ai` still receives Articles 9 to 17 gap obligations.
4. **Classifier confidence contradiction:** empty input maps to `not_ai`, `allow`, categorical high confidence, and numeric confidence 0.
5. **CLI/API contract split:** CLI accepts empty, partial, unknown-key, and invalid questionnaire maps differently from REST, while both call the same evaluator.
6. **Editor false-clean failure:** unexpected valid JSON becomes no findings, and some parse failures delete diagnostics.
7. **Locale export-schema drift:** PT-BR exports a locale field that EN and DE omit even though scoring functions currently match after string normalisation.
8. **Closure-record recurrence:** N78's own explanation reintroduces the count literal that its closure says is guarded, and full pytest fails on it.
9. **Gate simultaneity:** all six fast gates pass while the full suite fails and the browser unknown-export defect remains live.
10. **MCP error semantics:** validation and execution errors can be returned as successful text content rather than tool errors.

The itemisation has 10 entries and the total is 10. These findings were generated by predicates, probes, or source paths, not by subtracting memories of two documents.

## Reconciliation of the 11 August review

At the measurement commit/tree:

| Prior item | Independent status |
|---|---|
| R01 questionnaire scoring/confidence | Reproduced by direct evaluator and CLI/API probes. |
| R02 stale 100% benchmark page | Reproduced in the page source against the current model-card withdrawal. |
| R03 browser unknown scoring | Reproduced in a real browser in three jurisdictions. |
| R04 API root/envelope failures | Reproduced with array/string roots and source inspection. |
| R05 release identity divergence | Reproduced: 201 commits after tag; PyPI still serves 1.9.0 uploaded 2026-07-27. |
| R06 release workflow omits full suite | Reproduced from workflow call graph. |
| R07 VS Code validation gap | Reproduced: compile RC 0, test/type-check RC 2 on missing suite/test globals; no extension workflow found. |
| R08 Article 50 breadth | Reproduced in current site source. |
| R09 mobile navigation | Reproduced by Escape key control. |
| R10 claim gates are structural | Reproduced and extended with explicit counterexamples. |
| R11 pytest failure | Reproduced as one current failure; eight sandbox errors disappear outside sandbox. Exact prior failing test must not be assumed identical without its evidence. |
| R12 coverage evidence | Reproduced: stale local `.coverage`; no CI coverage path found. |
| R13 post-tag change volume | Reproduced by git-log predicate, 201 subjects itemised. |
| R14 locale logic duplication | Reproduced; current scoring functions match after normalisation, so present behavioural drift was not reproduced. |
| R15 dependency advisories | Reproduced outside the network sandbox: 7 advisories, 3 low, 1 moderate, 3 high. Production-only audit returned zero. |
| R16 homepage length | Reproduced at 320 by 800; 15,476 CSS pixels high, no horizontal overflow in that viewport. |
| R17 Brazil wording | Reproduced in source. |
| R18 package scope excludes web/tests | Reproduced in `pyproject.toml`; intent remains undocumented. |

This table does not make the prior record ground truth. It records this session's independent comparison.

## Phase 1: root cause generators

Predictions were written to `11-predictions-before-measurement.md` before the corresponding probes and comparisons. Wrong predictions are retained.

### Generator G1: no epistemic decision contract

**Terminal cause.** Input facts are not represented as facts with state and provenance. Unknown, missing, not detected, not applicable, and no are converted into weights or fallthrough branches. A tier then acts as a proxy for legal applicability, and a heuristic score acts as confidence.

**Pre-measurement predictions:** all-unknown Korea would attach obligations; all-unknown Colorado would attach obligations; omitted answers would equal unsure; no evidence would still receive positive/categorical confidence; contradictory sources would be averaged rather than represented.

**Results:**

- Korea positive-duty prediction: hit.
- Colorado positive-duty prediction: miss. It returned definitive not-covered instead, which supports the broader generator but falsifies the specific directional prediction.
- Omitted-equals-unsure prediction: hit in evaluator and URL decoder.
- Confidence-without-evidence prediction: hit in questionnaire and classifier.
- Contradiction-averaging prediction: not testable as written because the flat key/value schema cannot represent two sourced values for one fact. That inability is itself an epistemic contract defect, but it is not counted as a hit.

Strict hit rate: 3/5, or 60%. One miss and one untestable prediction are kept in the denominator.

**Accounts for:** questionnaire unknown results, browser EU/Korea/Colorado results, scanner/classifier false certainty, unconditional gap articles, misleading readiness/confidence, and downstream artefacts.

**Generator fix closes more than instance fix:** a score adjustment changes one boundary. A typed epistemic state and obligation predicate prevents every adapter from converting unresolved evidence into a legal conclusion.

### Generator G2: copied engines without one executable conformance contract

**Terminal cause.** Decision logic and output shaping are duplicated across Python, a JavaScript scanner, three large locale pages, API rendering, MCP text, and the editor. Shared names are treated as equivalence without a machine-enforced behavioural contract.

**Pre-measurement predictions:** locale scorer drift; locale export/schema drift; Python/browser differential behaviour.

**Results:**

- Current locale scorer drift: miss after string normalisation; the functions match.
- Locale export/schema drift: hit; PT-BR alone exports `locale`.
- Python/browser differential behaviour: hit; questionnaire count, validation, and scoring differ, and scanner/report paths are distinct.

Strict hit rate: 2/3, or 66.667%.

**Accounts for:** contract divergence, repeated fixes, locale maintenance risk, browser/Python questionnaire differences, MCP/editor adaptation differences, and release-surface drift.

**Generator fix closes more than instance fix:** one declarative decision model, one schema, and cross-runtime conformance vectors make future branch or locale drift detectable instead of relying on copied edits.

### Generator G3: validation occurs after dispatch rather than at every boundary

**Terminal cause.** Adapters assume decoded shapes, coerce booleans, ignore unknown identifiers, or turn parse failures into empty success. Type annotations and tool declarations are treated as validators when no validator runs.

**Pre-measurement predictions:** non-object API roots fail outside the standard envelope; CLI roots differ; browser share codes silently pad; an editor schema change becomes a clean result.

**Results:** all four predictions hit. Strict hit rate: 4/4, or 100%.

**Accounts for:** API disconnects, CLI internal errors, partial/unknown questionnaire acceptance, browser silent padding, MCP successful error text, and editor false-clean diagnostics.

**Generator fix closes more than instance fix:** a contract-first boundary validates every caller before domain execution and forces one typed failure state. Adding an `isinstance` check to one REST handler would leave every other adapter exposed.

### Generator G4: assurance checks artefact agreement more often than outcome validity

**Terminal cause.** Tests and gates are selected around stable rendering, fixture-controlled outputs, counts, source markers, and current snapshots. Few invariants state what must never happen under uncertainty, applicability failure, or adapter drift.

**Pre-measurement predictions:** exit-only tests; tests whose fixtures determine decision output; vacuous/empty scans; gates that pass semantic counterexamples; known defects encoded as expectations.

**Results:** all five prediction classes were found by the stated predicates. Strict hit rate: 5/5, or 100%.

**Accounts for:** all fast gates passing alongside unsafe output, all-unknown behaviour protected by tests, mock-heavy adapter assurance, and the distinction between reproducibility and validity being lost in names.

**Generator fix closes more than instance fix:** property, mutation, differential, and semantic scenario tests establish behaviour-level invariants. Adding another snapshot would only preserve the next implementation.

### Generator G5: supported product surface exceeds validated evidence

**Terminal cause.** Sixty-plus CLI commands, REST, MCP, an editor, three locale assessment pages, and generated evidence/conformity artefacts are presented under one product identity while efficacy evidence is narrow, weak, or explicitly negative.

**Pre-measurement predictions:** at least one adapter outside CI; published identity drift; a downstream artefact lacks enough epistemic context to support its presentation.

**Results:** all three predictions hit: the VS Code extension has no located workflow and its tests do not type-check; PyPI remains 1.9.0 while the tree is 201 commits beyond the tag; the all-unknown browser export makes definitive claims. Strict hit rate: 3/3, or 100%.

**Accounts for:** release identity ambiguity, unverified extension behaviour, unsupported breadth, handable artefact risk, and the gap between 0/40 constructed evidence discovery and product surface.

**Generator fix closes more than instance fix:** explicit capability tiers and fail-closed withdrawal of unvalidated surfaces stop unsupported claims from reappearing as new adapters or artefacts.

### Ranking

1. **G1, no epistemic decision contract:** highest consequence. It directly generates wrong legal-looking outputs and artefacts.
2. **G4, assurance targets agreement rather than validity:** makes G1 and G2 look safe and permits recurrence.
3. **G3, boundary validation is not fail-closed:** turns malformed or drifted data into crashes or false-clean output.
4. **G2, copied engines lack conformance:** multiplies every correction and makes recurrence likely.
5. **G5, surface exceeds evidence:** expands exposure and verification cost, though it does not alone determine a wrong result.

### Single binding constraint

**Interpreted.** The binding constraint is the absence of a canonical, executable contract for what a regulatory output means and what evidence must exist before that output may be emitted. Assumptions: a product-level invariant must be shared by every entry point, and assurance cannot compensate for an undefined target. This is not merely the most numerous cause. Left in place, duplicated engines, stronger schemas, and more tests can still faithfully reproduce the wrong meaning. It would be falsified if an existing executable contract were found that distinguishes unknown/no/not-applicable, defines obligation preconditions, and is enforced at every traced entry point. The path enumeration found none.

## Dynamic-premise results

1. **Questionnaire-only premise: falsified.** The same epistemic generator appears in classifier, scanner, gap, Korea, Colorado, API, MCP, and editor behaviour.
2. **Three implementations of one logic premise: falsified.** CLI and REST reuse several Python cores; browser questionnaire, browser scanner, Python scanner, and gap engine are distinct; locale logic is copied.
3. **Eighteen separable findings premise: falsified.** Five generators explain the demonstrated instances.
4. **Repair rather than redesign premise: falsified.** A threshold repair cannot introduce fact states, provenance, applicability predicates, contract validation, or cross-runtime conformance.

## Phase 2a: primary-source research

All sources below were retrieved on 2026-08-11. A source establishes only the proposition stated here.

### Selective prediction and abstention

Geifman and El-Yaniv, *SelectiveNet: A Deep Neural Network with an Integrated Reject Option*, PMLR 97 (2019), defines a selective model as a prediction function paired with a selection function that can abstain and evaluates selective risk at a target coverage. It supports reporting coverage and risk-coverage trade-offs rather than forcing an answer for every input. Source: <https://proceedings.mlr.press/v97/geifman19a.html>.

**Design implication, interpreted:** Regula should return `insufficient_information` with unresolved predicates when the required facts are absent. Coverage of determinate outputs and error among those outputs are separate measures.

### Calibration

Guo, Pleiss, Sun, and Weinberger, *On Calibration of Modern Neural Networks*, PMLR 70 (2017), defines calibration as agreement between stated confidence and empirical correctness frequency and evaluates calibration on labelled data. Source: <https://proceedings.mlr.press/v70/guo17a.html>.

**Design implication, interpreted:** Regula's tier bases, match bonuses, and questionnaire sums are not calibrated confidence. Until representative labelled outcomes exist, the numeric field should be removed from decision meaning and replaced with evidence completeness and rule-resolution state.

### Rule and predicate systems

The Object Management Group's Decision Model and Notation standard describes precise decision requirements and decision logic, including decision tables intended for unambiguous execution and validation. Source: <https://www.omg.org/dmn/index.htm>.

**Design implication, interpreted:** legal applicability should be represented as named predicates and decision tables/DAGs with traceable inputs, not an additive score whose compensating weights can override a necessary condition. Full DMN adoption is not required; the project can implement a smaller stdlib-only declarative table.

### Unknown distinct from no

JSON Schema's 2020-12 specification is the current published JSON Schema dialect listed by the project, and its `null` reference states that null is a value distinct from absence. Sources: <https://json-schema.org/specification> and <https://json-schema.org/understanding-json-schema/reference/null>.

**Design implication, interpreted:** the Regula domain contract should use an explicit enum such as `yes`, `no`, `unknown`, and `not_applicable`, require all decision-critical fact identifiers, and separately represent omitted/invalid input at the adapter boundary.

### Contract-first APIs

The official latest OpenAPI page retrieved during this session identifies OpenAPI Specification version 3.2.0 and defines a language-agnostic interface description for HTTP APIs. Source: <https://spec.openapis.org/oas/latest.html>. OpenAPI 3.1 explicitly aligns schema handling with JSON Schema 2020-12; 3.2.0 is the current latest page, so a new design should target 3.2.0 unless tooling compatibility requires a documented 3.1.x choice.

**Design implication, interpreted:** define request, success, problem, and export schemas first; validate runtime instances; generate or check adapters against them; and reject non-object roots before handler dispatch.

### Property and mutation testing

Hypothesis describes property-based testing over generated examples with automatic simplification of failing cases. Source: <https://github.com/HypothesisWorks/hypothesis/>. Jia and Harman's 2011 survey describes mutation testing as seeding systematic faults to assess whether tests distinguish them. Source: <https://www0.cs.ucl.ac.uk/staff/M.Harman/mutation_testing_repository/JiaHarman11.pdf>.

**Design implication, interpreted:** generate fact-state combinations and mutate every applicability/obligation edge. A test suite should fail when `unknown` becomes `no`, a necessary predicate is removed, an article edge changes, or an adapter returns an unvalidated shape. Hypothesis would be a test-only dependency and therefore needs an explicit project ruling because the core is stdlib-only.

### Static-analysis efficacy reporting

NIST SAMATE's Static Analysis Tool Exposition materials describe evaluating which weaknesses tools find and analysing false positives, while warning that exposition results do not support broad tool ranking. Source: <https://samate.nist.gov/SATE.html>.

No single current primary standard was found that mandates one universal metric set combining static-analysis efficacy, abstention quality, and user false-alert burden. Searches covered NIST SAMATE/SATE and SARIF. Therefore the following is **reasoned, not evidenced as a normative convention**: report labelled-corpus recall and precision by class, false alerts per thousand scanned lines/files, no-finding audit rate, determinate coverage, selective risk among determinate outputs, and skipped/unreadable input rates. It would be overturned by an applicable normative metric standard for this tool class.

### SARIF

OASIS SARIF 2.1.0 defines the interoperable static-analysis result format, including result kind/level, suppressions, baseline state, fingerprints, locations, and rule metadata. Source: <https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html>.

**Design implication, interpreted:** keep SARIF for located static findings, validate emitted documents against the SARIF schema, use result kinds/levels and baseline metadata accurately, and do not use SARIF as a carrier for unsupported legal determinations. SARIF defines interchange, not efficacy.

### Accessibility

WCAG 2.2 is a W3C Recommendation and includes keyboard operability, focus order, focus visibility, reflow, and name/role/value requirements relevant to the observed navigation. Source: <https://www.w3.org/TR/WCAG22/>. The WAI-ARIA Authoring Practices disclosure navigation example specifies that Escape closes the navigation and returns focus to the controlling button, and cautions that support must be tested with assistive technologies. Source: <https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/>.

**Design implication, demonstrated against source and browser:** implement Escape closure and focus restoration, then test keyboard, zoom/reflow, reduced motion, and representative screen-reader combinations. Automated checks cannot close the human usability item.

### Semantic versioning and provenance

Semantic Versioning 2.0.0 requires released contents not to be modified and defines patch and minor increments relative to a declared public API. Source: <https://semver.org/>. SLSA provenance 1.2 describes verifiable information about where, when, and how an artefact was produced and its relationship to source. Source: <https://slsa.dev/spec/v1.2/provenance>.

**Design implication, interpreted:** a release gate must build the wheel/sdist from the release commit, verify version identity and contents, run the full release test chain against those artefacts, and emit signed or hosted provenance appropriate to the chosen SLSA level. A changelog-only bump check is insufficient.

### AI Act standards status

The British Standards Institution announced publication of BS EN 18286:2026 on 2026-07-24 as an AI quality-management-system framework. Source: <https://www.bsigroup.com/en-GB/insights-and-media/media-centre/press-releases/2026/july/en-18286-provides-a-framework-for-ai-quality-management-under-the-eu-ai-act/>.

The European Commission's AI Act standardisation page, updated 2026-08-03, explains that after standards are delivered the Commission assesses them and, if suitable, cites them in the Official Journal. Source: <https://digital-strategy.ec.europa.eu/en/policies/ai-act-standardisation>. The Commission AI Act Service Desk states for Article 40 that only references published in the Official Journal confer presumption of conformity. Source: <https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-40>.

Exact EUR-Lex searches for `EN 18286` and `18286:2026` produced no relevant citation result on 2026-08-11; unrelated cosmetics records appeared. Therefore EN 18286 publication is verified, but OJ citation is **unverified and no relevant citation was found**, not asserted impossible or definitively absent.

The BSI/CEN project page for `prEN 18229-1` records a draft enquiry with comment period 2026-05-28 to 2026-07-21 and estimated publication 2027-06-15. Source: <https://standardsdevelopment.bsigroup.com/projects/2024-03324>. Other national standards-body pages showed later national comment deadlines, so the session does not claim one universal national enquiry close date. On 2026-08-11 it remained a draft, not a published EN, and no OJ citation was verified.

**Design implication:** do not state that publication alone provides presumption of conformity. Keep a dated standards-status registry with separate fields for draft, national adoption/publication, Commission assessment, and OJ citation.

## Phase 2b: remediation architecture at the generators

### R1. Canonical epistemic decision kernel for G1

**Change.** Define a versioned domain model whose decision-critical inputs are facts with `yes`, `no`, `unknown`, or `not_applicable`, provenance, jurisdiction, and timestamp. Implement applicability as named predicates and a traceable decision DAG/table. Output a tagged union: `indication`, `insufficient_information`, or `outside_scope_candidate`. Every obligation must cite the satisfied predicate path and specific provision. Unresolved necessary predicates produce a review list, not a duty.

Remove unconditional numeric confidence. Report `evidence_completeness`, `rule_resolution`, matched evidence, unresolved predicates, and detector-priority score separately. Numeric probability may return only after representative calibration data establishes its interpretation.

**Why root fix.** It changes what every result means. It prevents compensating weights and fallthrough from turning unknown into yes or no.

**Invariant.** No tier, outside-scope result, article duty, readiness percentage, or effort estimate may be emitted unless all required predicates for that claim are resolved and their evidence path is present. Unknown never increases determinacy.

**Fail-before/pass-after tests.** All-unknown and empty inputs currently emit limited/high or high-risk decisions. A property test generates fact maps and asserts that replacing a resolved fact with unknown cannot create a more determinate outcome or a new obligation. Mutating any necessary predicate or article edge must be killed.

**Cost.** High. It changes the domain model, browser engine, adapters, exports, copy, and fixtures. It needs legal review of the predicate tables.

**Risk.** False abstention and excessive loss of useful indications if predicates are too strict. Mitigate by distinguishing safe evidence-location output from legal determination.

**Falsifier.** If representative labelled evaluations show additive scoring has lower selective risk at the same coverage and can provide traceable necessary predicates, the predicate model should be reconsidered. Current evidence does not show that.

### R2. Contract-first boundaries for G3

**Change.** Publish versioned JSON Schemas and OpenAPI 3.2.0 for facts, decision outputs, problem details, browser exports, and REST routes. Set explicit root types, required fields, known identifiers, bounded strings/arrays, and `additionalProperties` policy. Validate before handler dispatch. Map one typed domain error to CLI, REST, MCP, browser, and editor presentations. MCP execution failures must be tool errors, not successful error prose. The editor must preserve prior diagnostics as stale and show a visible scan-error state on invalid output.

**Why root fix.** It establishes the same boundary property for every adapter rather than adding handler-specific guards.

**Invariant.** No unvalidated value reaches a decision function, and no invalid/missing output can be rendered as clean, complete, or successful.

**Fail-before/pass-after tests.** Array/string API roots currently disconnect; unknown questionnaire IDs pass; unexpected editor envelopes become empty. Contract tests send each invalid root/field across every adapter and require the defined error union while preserving prior editor state.

**Cost.** Medium to high. Stdlib JSON Schema validation would require either a small generated validator, a test/build dependency, or carefully limited handwritten validation. The rigorous choice is machine-verified schema with a build/test dependency; this costs dependency governance.

**Risk.** Breaking currently tolerated clients. That is a necessary breaking correction and requires an explicit versioned migration, not silent coercion.

**Falsifier.** If runtime schemas cannot express the domain invariants or generated validators diverge from the schema, the mechanism is insufficient and must be replaced.

**Protected-module ruling.** Wiring CLI error/result behaviour may require changes in the protected `scripts/cli.py` monolith. The evidence supports proposing that change, but project instructions require explicit approval before refactoring it. Prefer thin dispatch wiring and leave the monolith structure intact where possible.

### R3. One declarative model plus cross-runtime conformance for G2

**Change.** Store jurisdiction rules, fact definitions, obligation edges, and output schema in one versioned, language-neutral declarative source. Generate or load Python and browser tables from it. Keep translated strings in locale dictionaries only. Create a sanctioned corpus of conformance vectors covering every branch and invalid/unknown state; run it against Python, browser, REST, MCP, and editor adapters.

**Why root fix.** It makes shared semantics executable and makes duplicated runtime implementations accountable to the same contract.

**Invariant.** Given the same model version and normalised facts, every runtime returns the same semantic result and schema; locale changes affect presentation strings only.

**Fail-before/pass-after tests.** Current Python/browser questionnaire vectors differ and locale export schemas differ. Differential tests fail before and pass after. Change one generated article edge and require every runtime conformance test to fail until regenerated.

**Cost.** High initial migration and generator maintenance; lower recurring correction cost.

**Risk.** A defect in the canonical model propagates everywhere. Mitigate with independent semantic tests, source citations per rule, mutation testing, and human legal review.

**Falsifier.** If jurisdictions cannot be represented without opaque procedural code, retain a shared fact/output contract and per-jurisdiction engines, but preserve differential boundary tests. That is the reversible fallback.

### R4. Semantic assurance for G4

**Change.** Add property tests, mutation tests, real-engine contract tests, and high-consequence semantic gates. Separate adapter fixture tests from decision tests in naming and reporting. Add controls for all unknown, conflicting evidence, not applicable, partial scan, invalid schema, locale differential, and stale editor state. Gate documentation claims against outcome evidence, not URL presence alone.

**Why root fix.** It changes the assurance target from reproduction of current artefacts to violation detection.

**Invariant.** Every legal predicate and obligation edge is covered by a fail-before semantic test; a seeded mutation of any such edge is detected; no gate name claims a property outside its predicate.

**Fail-before/pass-after tests.** The current all-unknown tests pass unsafe output and the six fast gates pass it. Reverse the expectations, add semantic scenarios, and require mutation score by decision edge rather than an undifferentiated percentage.

**Cost.** Medium to high, especially mutation runtime and representative oracle design.

**Risk.** Generated tests can encode the same wrong oracle. Mitigate by deriving legal predicates from cited primary text and keeping independent adversarial examples.

**Falsifier.** If mutations survive only because they are semantically equivalent, improve mutation operators and report equivalents rather than suppressing them.

### R5. Capability containment for G5

**Change.** Define three product tiers: verified evidence locator, experimental decision aid, and withdrawn/disabled. Keep local static pattern location only where measured behaviour supports it and label it evidence discovery, not classification. Disable or visibly withdraw definitive questionnaire decisions/exports, readiness percentages, effort estimates, and editor clean-state claims until R1 to R4 pass. Evidence/conformity packs must become scaffolds that carry provenance and unresolved facts, or be withheld. REST/MCP/editor surfaces remain disabled unless they pass the same contract corpus.

**Why root fix.** It aligns what users can do and infer with evidence the project can carry, rather than adding disclaimers to unsupported breadth.

**Invariant.** No enabled surface can emit a claim or artefact stronger than its validation evidence. Disabled paths look and behave disabled, with an honest explanation and no actionable-looking dead controls.

**Fail-before/pass-after tests.** The current browser exports a definitive all-unknown result and the editor can clear diagnostics on schema failure. Containment tests require an explicit unavailable/insufficient state across all traced adapters and forbid exports of unresolved determinations.

**Cost.** Reduced apparent product surface and possible user disappointment. This is cheaper and safer than maintaining unsupported capability.

**Risk.** Over-withdrawal may hide useful low-stakes evidence location. Preserve that smaller function with precise copy and measured limitations.

**Falsifier.** Representative validation demonstrating acceptable class-specific recall, false-alert burden, selective risk, and user comprehension would justify re-enabling a surface.

## Phase 2c: sequence by consequence

### Contain live harm now

1. **Fail closed on unresolved questionnaire facts across CLI, REST, and all browser locales.** Disable definitive results and all exports/share/PDF paths until the canonical insufficient-information response exists. Repository-verifiable with cross-adapter tests. This is the proposed Phase 3 item for the next authorised scope.
2. **Prevent false-clean editor state.** Invalid or unexpected CLI output must retain prior diagnostics as stale and display a scan failure. Repository-verifiable, but extension-host UX still needs manual testing.
3. **Remove or disable unconditional readiness, effort, and obligation presentation.** Repository-verifiable for presence and decision paths; legal appropriateness requires external review.

### Must precede any future release

1. R1 fact-state and predicate model, dependent on legal rule review.
2. R2 versioned schemas and boundary validation, dependent on R1 output types.
3. R3 generated/shared decision tables and differential vectors, dependent on R1 and R2.
4. R4 property/mutation/semantic gates, built alongside R1 to R3 and required before re-enabling.
5. Correct the stale benchmark, Article 50 breadth, Brazil future-tense certainty, and every public claim contradicted by the model card. Repository copy can be checked; regulatory entailment needs primary-source review.
6. Put the VS Code extension under an actual compile/test workflow and repair its test configuration. Repository-verifiable.
7. Build release artefacts from a clean tagged commit, test installed artefacts, reconcile all version surfaces, and emit provenance. Repository-verifiable except trust in external hosting/signing infrastructure.
8. Validate SARIF against the official schema and keep legal conclusions out of unsupported result fields. Repository-verifiable.
9. Fix the mobile disclosure navigation for Escape, focus restoration, keyboard order, and visible state. Mechanical behaviour is repository-verifiable; representative assistive-technology usability is not.

### Later validation programme, not closeable by repository engineering

1. Independently label a representative corpus by jurisdiction and task; report class-specific recall/precision and false-alert burden.
2. Measure abstention coverage and selective risk.
3. Conduct representative developer/compliance user studies for comprehension, task completion, trust, and error recovery.
4. Conduct screen-reader, zoom/reflow, keyboard, touch-target, and reduced-motion studies across representative platforms.
5. Obtain legal review of predicate tables and obligation mappings.
6. Monitor Commission assessment and Official Journal citation separately for EN 18286 and the EN 18229 series.
7. Validate whether any decision confidence can be calibrated; otherwise keep it absent.

## Phase 3 status

Phase 3 was not reached. Phases 0 to 2 required the available session, and the demonstrated containment item changes every questionnaire surface. Executing only the easiest browser or CLI instance would violate the requirement to fix the class across all traced entry points. No product code, public surface, test expectation, gate allowlist, suppression, skip, pin, stub, or TODO was introduced.

The next scope should explicitly authorise the first containment item above and the necessary protected CLI wiring, with fail-before controls preserved and pass-after controls run across CLI, REST, EN, DE, and PT-BR.

## Residual uncertainty and falsifiers

- No representative corpus was labelled in this session. Static-analysis efficacy beyond the existing sanctioned fixtures remains unverified.
- No human, screen-reader, or representative user study was performed. Browser automation proves mechanics, not usability or comprehension.
- No third party received an artefact. Handability is demonstrated by export and page copy; actual downstream reliance is unmeasured.
- Current scoring functions match across locales after string normalisation, but that does not prove semantic translation equivalence.
- The exact prior R11 failing test cannot be identified from memory; only the current failure is verified here.
- EN 18286 publication is verified. OJ citation was not found and remains unverified, not declared definitively absent.
- The proposed rule model requires legal validation. Engineering can enforce a wrong predicate perfectly.

## Standing verdicts after this work

Unchanged: `PRODUCT_BUILD: STOP`; `VENTURE_DECISION: STOP`; `STAGE_A_PACK: HOLD`; `EXTERNAL_CONTACT: NOT_AUTHORISED`; `REAL_DATA_COLLECTION: DISABLED`; `H1: ABANDONED`; `H2: NOT_CREATED`; `WTP: UNVALIDATED`; `PILOT: NOT_APPROVED`.
