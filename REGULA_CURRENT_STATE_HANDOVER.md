# REGULA CURRENT-STATE HANDOVER

**Private review document. Do not publish or commit this handover without a separate privacy and scope decision.**

## EXECUTIVE STATE

**As of 23 September 2026, inspection started at 17:59:00 BST (UTC+01:00).** The examined repository is the Git top-level directory named **getregula**, referred to below as **R**. Its branch is **feat/site-ux-redesign-2026-08-27**, HEAD is **fbed8f3baf81f0c5f0860ebaf56a2845b632b547**, and it already had **157 modified tracked files and 85 untracked entries**, with no staged changes, before this task. This is a dirty historical checkout, not the newest isolated candidate. [E01]

Regula is a Python command-line tool, accompanied by a static website, for finding indications of AI use in code, recording deployment facts and assembling evidence for human review. Its proposed customer outcome is **one reviewable evidence file for one AI feature, before release or when a customer requests evidence**. It cannot establish legal compliance from code or file hashes. [E03, E06, E13]

The newest identified local candidate, **W2**, includes a browser draft, an installed CLI review workflow, explicit unknowns, evidence references, correction/recovery and change-triggered re-review. Existing records show bounded installed-workflow and browser checks. This session inspected the relevant implementations and matched all **793 inventory-listed files** to W2's retained inventory. It did not rerun those checks. W2 is based on **b58c622e966f1fdaef95c37e8cfc8181cd33139d**, with **118 staged changes and no new commit**. [E02, E11, E12]

**The three evidence-handling repairs exist in later local candidates, but the corresponding unsafe paths remain in R.** The current R working tree has no identified complete gate for its exact bytes. W2 also has **no verified complete four-part engineering gate**: its owner-gate destination is empty, and its retained preflight explicitly says no test ran. Earlier candidates have distinct failed full-pytest runs; their passing subsets must not be reassigned to W2. [E04, E07-E12]

Human comprehension, competent professional acceptance, buyer demand, delivery economics, native-language quality and present legal-source correctness remain unestablished. Deployment, merchant operation, payments and current public-service availability were not checked. [E13-E16]

**Next owner decision:** choose whether to advance the exact preserved W2 candidate through its existing source-pinned, permitted-runtime gate and subsequent review, before any integration or conditional commit. Do not reset R or treat older acceptance as acceptance of W2. This handover authorises no implementation, execution or release.

## Reading conventions and evidence locations

This document separates five evidence levels:

- **Observed in source:** implementation or local filesystem/Git state inspected in this session. This is not execution proof.
- **Recorded result:** an existing log or structured result was read. It reports an earlier execution, not a run performed for this handover.
- **Documented claim:** a README, plan, approval or summary says something which has not necessarily been demonstrated.
- **Inference:** a reasoned interpretation, explicitly qualified.
- **Unknown:** available evidence does not establish the answer.

Personal-machine path prefixes are deliberately omitted. The following aliases identify actual local locations inspected; they are not new directories or proposed locations.

| Alias | Location or record identifier |
| --- | --- |
| R | This repository root, getregula; Git identity above |
| D | The owner's Windows Downloads directory |
| C | D / Regula-Delivery-Continuation-2026-09-16-r01 |
| P | D / Regula-Transformation-Program-2026-08-31 |
| S1 records | C / successor-increment-2026-09-20 |
| S2 records | C / evidence-journey-increment-2026-09-21-02 |
| J3 records | C / reviewable-outcome-increment-2026-09-22-03 |
| W records | C / website-experience-increment-2026-09-22-04 |
| B records | W records / browser-verification-2026-09-23-r01 |
| S2, J3, W2 source | The separate successor, reviewable-outcome and website workspaces referenced by C / ACTIVE_CONTEXT.json and the respective inventories; these are not R |

The actual source locations and personal path prefixes remain in the owner's existing private records. A reviewer without those files can understand the conclusions here, but cannot independently reproduce their hashes from this document alone.

The selected inventory covered repository guidance, README and product pages, packaging metadata, CLI parsers/handlers, scanner entry points, decision models and adapters, regulation maps, evidence generation and verification, the newer review workflow, browser draft code, representative regression bodies, CI configuration, retained gate logs, package identities, programme/authority records, delivery and pricing decisions. It did not indiscriminately ingest earlier giant consolidations. [E01-E17]

## PRODUCT AND CUSTOMER JOURNEY

### Positioning and intended user

The current product direction is a bounded review response for one AI feature. The likely user is a technical product owner or engineer who must answer a governance, procurement or customer question; the recipient is a technical/governance reviewer. This interpretation is supported by the decision brief, review-response guide and implemented question/evidence registers. It is not validated segmentation or willingness-to-pay research. [E06, E13]

The wording supplied for this handover, “Before you release an AI feature, prepare the evidence your technical and governance reviewers will ask for”, appears in **D / CODEX-EXECUTION-PROMPT.md:11** as a previously proposed sentence, followed by “without uploading your source code”, using a comma. The exact punctuation variant in the current request was not found in the selected current product-source search. **D / DECISIONS-UX-AND-PRICES.md:17-27** discusses a shorter proposed hero and cautions against promising what reviewers will ask for or an unconditional no-upload claim. This is proposed positioning, not evidence that the sentence is a shipped promise.

R's README presents code scanning and review support. W2 adds a more concrete question-first browser experience. Both still need careful distinction between an observed code signal, an owner's declaration and a review conclusion. [E03, E06, E11]

### One AI-feature journey

The following describes **W2**, unless otherwise stated. R does not contain `scripts/review_record.py` or `site/prepare/index.html` and therefore does not prove this complete journey exists in the original checkout.

| Step | Actual implementation and user experience | Evidence and remaining limit |
| --- | --- | --- |
| Question | Browser starter captures the feature, review question, responsible owner and next action; regional context can seed a question. | W2: site/assets/review-starter.js:4-49; B browser observations. One bounded draft, not an unrestricted case-management system. |
| Evidence | Browser downloads a structured draft. The local `regula review` command accepts the record and an explicitly selected evidence directory, captures permitted files and produces a review response and manifest. | W2: scripts/cli.py:1296-1304; scripts/review_record.py:344-365,551-594. Browser draft itself does not upload or automatically discover evidence. |
| Uncertainty | Unknown, Investigating, Conflicting and Out of scope are explicit states. A blank answer remains null; unavailable evidence is not silently converted into proof. | W2: scripts/review_record.py:27-56,318-341; B/downloaded-draft-cli-r02/result.json. State preservation is recorded, not professional validation of an answer. |
| Reviewer | Record and response expose reviewer-related fields and human acceptance status. | W2: scripts/review_record.py:412-548. Software can store an attributed review; it does not authenticate professional competence or cause a review to occur. |
| Next action | Required ownership/next-action information is preserved in the draft and presented in the response. | Source and synthetic browser/CLI exercise. Completion of the real-world action is unverified. |
| Correction and recovery | Editing a question invalidates the stale preview. Saved drafts can be reopened. Malformed or richer unsupported imports are rejected rather than silently flattened. Clear/replacement operations have confirmation and preservation behaviour. | W2: site/assets/review-starter.js:53-85,138-179; B/BROWSER-RESULTS.md:55-71. No browser autosave is established. |
| Change and re-review | Previous records and captured evidence versions support comparison. Relevant changed evidence puts dependent review back into a pending state; clearing that state requires recorded review information rather than automatic success. | W2: scripts/review_record.py:300-315,412-487; tests/test_review_journey.py:90-141. Synthetic named reviewers in fixtures are not actual human acceptance. |

The latest recorded browser-download-to-installed-CLI exercise preserved the draft's **Investigating** state, **null answer**, **Not performed** human acceptance and input bytes. Provenance, review/bundle generation and folder/archive/sample verification each returned zero. These are recorded command observations, not five additional pytest cases. [E12]

### Nontechnical user versus reviewer

A nontechnical user sees a static starter, contextual questions, missing-input messages, an example and a downloadable draft. The browser does not deliver a hosted collaborative review service or a working purchase/fulfilment pipeline in this inspected journey.

A technical reviewer receives structured records, an HTML response, selected evidence, hashes and a verification route. The CLI requires an independently obtained trusted installation and understanding of the supplied evidence. The newer review-response guide documents bounded spreadsheet handling, retained uncertainty and review history. It does not turn hash consistency into correctness or legal approval. [E06-E07]

### Usability and value evidence

Recorded browser work on 23 September found and repaired three concrete problems: dark-footer text contrast, a starter wider than a 320-pixel screen and long hashes overflowing the generated response. The records contain screenshots, layout measurements and interaction observations. They do **not** establish that the website is objectively the best in its market. [E12]

The strongest recorded observations are:

- Nine homepage/product/starter measurements at 320, 390 and 1,440 pixels had no horizontal page overflow; five regional pages fitted at 320 pixels.
- Footer contrast measurements ranged from **5.7959 to 11.311** in the captured state.
- Empty submission, malformed import, cancelled clearing/replacement, explicit unknowns and saved-draft reopening received synthetic browser exercises.
- Escape returned focus from the menu. Main focus transfer after the skip link and full reverse keyboard containment were not established.

Screen readers, genuine 400% zoom, JavaScript-disabled operation, native-language comprehension and actual participant task performance remain unestablished. These are more consequential than a claim of visual polish. This handover did not launch a browser or independently inspect the saved screenshot pixels. [E12]

The delivery learner's informal response is documented as useful feedback from an involved person, not an independent buyer test or proof of professional competence. **J3 / OBSERVATION-ADDENDUM.md:9,33-53** leaves participant results, reviewer availability, competence, buyer benefit and purchase evidence unanswered. Existing learner materials and observation cards are prepared materials, not completed delivery. [E13-E14]

## CURRENT TECHNICAL INVENTORY

### Architecture and executable surfaces

| Component | What the inspected material establishes | Limits and best reference |
| --- | --- | --- |
| Language and packaging | Python package `regula-ai`; Python >=3.10; console entry `regula = scripts.cli:main`; inherited version `2.0.0`. Core declares no external runtime dependencies. | R: pyproject.toml:5-16,31-82,93-124; scripts/constants.py:16. Several different local wheels share the version; content hash is required for identity. |
| Imports and entry point | Large CLI dispatcher and separate handlers, with the repository's bare-import convention and stable JSON envelope. | R: AGENTS.md:20-24; scripts/cli.py. This was selective inspection, not a full audit of every dispatcher branch. |
| Optional packages | YAML, tree-sitter, PDF, signing/timestamp, telemetry, web API and test extras are declared separately. | R: pyproject.toml:31-82. Core-only installed exercises do not demonstrate all extras. No package was installed in this task. |
| CLI surface | Static parser inspection found 62 top-level declarations in R/S2 and 63 in J3/W2, which adds `review`. | This is a parser inventory, not 63 executed commands. Families include check/classify/assess, questionnaires, reports, governance, evidence-pack/verify, attest, dependency/SBOM/AIBOM tools, monitoring, agent/bias tools, feed/regwatch and diagnostics. |
| Scanning | Selected scan implementation handles directory/file discovery, decoding failures, notebook issues and incomplete coverage accounting. Python AST analysis and JS/TS optional parsing are documented; other language coverage is more heuristic. | R: scripts/report.py:655-794; docs/architecture.md:57-94. The whole detection corpus and real-world accuracy were not revalidated. |
| Size/coverage bounds | Source constants contain file-size and classification bounds. Oversized, unsupported or unreadable material can limit coverage. | R: scripts/constants.py:18-54; scripts/report.py:655-794. Zero findings does not prove absence of AI use or obligations. |
| Decision kernel | Typed facts include yes/no/unknown/not-applicable, provenance and time/jurisdiction context. Rules can report insufficient information and contradictory facts. | R: scripts/decision_kernel.py:28-92,199-253,375-408. This is deterministic decision support, not a legal opinion. |
| Public decision presentation | Adapters separate evidence/provenance from a human decision. Later adapters remove legacy fields and retain an unrecorded human decision. | R: scripts/decision_adapters.py:29-115; W2: scripts/decision_adapters.py:83-199. R and W2 adapters differ; they are not interchangeable evidence. |
| Jurisdiction/rule data | Decision-model keys include EU, Korea and Colorado; local regulation-map files exist for EU AI Act, South Korea and Colorado. | references/decision_model.v1.json; scripts/regulation_map.py:25-110. Data presence is not proof of exhaustive jurisdictional coverage. |
| Reports | CLI text/JSON reporting, generated evidence-pack instructions, structured review record, HTML response and optional bundle are implemented in relevant candidates. PDF is an optional extra. | R: scripts/cli_evidence.py; W2: scripts/review_record.py:490-594; pyproject.toml. New response is absent in R; optional PDF was not exercised here. |
| Review/workbook workflow | New review command validates records, captures evidence, exports a response and tracks relevant changes. Guide defines bounded XLSX reading rather than spreadsheet recalculation. | W2: scripts/review_record.py; docs/review-response-guide.md:39-111. Documented bounds include 200 records, 8 MiB input files and 32 MiB captured evidence. |
| Evidence verifier and bundle | Selected payloads can be checked against a manifest; later packaging enforces a flat membership contract and rejects unwanted file types. | See security section. R retains unsafe older paths. |
| Static website | R contains existing EN/DE/PT-BR pages and browser assessment; W2 adds starter, five regional experiences, field notes and a generated example. | W2: site/prepare, site/experiences, site/field-notes, site/examples/review. Static content is not a deployed operational backend. |
| Browser scanner | Repository documents a client-side port and 38 canonical synthetic fixtures, including 30 high-risk fixtures. | R: AGENTS.md, docs/ENGINEERING_ROADMAP.md. Fixture parity is not independently measured detection validity; not rerun here. |
| Local HTTP API | Optional Flask routes expose scan/review-related functions with workspace path constraints. Default binding is local; W2 checks resolved loopback addresses unless unsafe binding is explicitly selected. | R: scripts/api_server.py:52-70,121-159,253-279; W2: scripts/api_server.py:53-80,132-170. No production authentication assurance was established. |
| MCP | Stdio handlers expose selected check/classify/gap functions under a configured workspace boundary. | R: scripts/mcp_server.py:174-221,397-466; W2: corresponding workspace and handler sections. Results go to the invoking client; its subsequent data handling is outside this local code. |
| Agent/model-related features | Monitoring/agent analysis, bias evaluation and a digest integration exist as separate surfaces. No implemented System One model or autonomous end-to-end governance investigator was established. | scripts/monitor.py; scripts/bias_eval.py; digest tooling. Presence or naming of an agent feature does not prove autonomous investigation quality. |
| Platforms | Linux/WSL is represented by current candidate evidence. CI declares Ubuntu/Python version jobs; older native Windows checks exist for a different candidate. | .github/workflows/ci.yaml:13-55; docs/architecture.md:57-94; P/A5 results. Windows support for all new security behaviour remains unverified. |

The declared installation is a console package, and retained workflows used disposable installed environments outside their checkout. Actual private environment locations are in the result JSON files. Public package availability, the current release and registry state were **not queried**. A source-install instruction referencing mutable public main would not identify any of these retained candidates. [E03, E08-E12]

### Local operation and transmission boundaries

The inspected review-export, evidence hashing and bundle paths use local files. The W2 browser draft builds a local Blob download and reads selected files in the browser. A bounded recorded browser capture saw seven same-origin static GETs and no submission request during that exercise. This supports that particular journey, not a universal privacy claim. [E06, E12]

Other inspected surfaces can communicate:

- **Optional telemetry:** Sentry initialisation depends on configuration/consent and a DSN. Scrubbing and disabled local-variable capture are visible in source. Actual environment values and current consent configuration were deliberately not read. R: scripts/telemetry.py:29-51,131-158; W2: corresponding consent/suppression/initialisation sections.
- **Optional timestamping:** sends a hash imprint and nonce to a timestamp authority. This is not the same as transmitting the whole evidence file, but it is a network operation. scripts/timestamp.py:257-271.
- **Bias evaluation:** can send prompts to a configured model endpoint; default local endpoint does not constrain all configurations. Dataset retrieval can also use the network. scripts/bias_eval.py:92,151-163,295-321.
- **Feeds/regulatory updates:** remote retrieval is implemented. scripts/feed.py:152-170.
- **Digest tooling:** R's untracked scripts/weekly_digest.py:260-305 contains an Anthropic request over prepared issue content. It is not evidence that customer source is always transmitted, nor that the current user has configured it.
- **API/MCP:** a client can obtain results and relay them elsewhere. The local implementation cannot promise what an external caller or model client will do.

Consequently, **no-upload must be scoped to a defined workflow and configuration**. It cannot honestly describe every optional integration without further verification. No integration or network call was executed in this handover. [E05]

### Findings, facts, applicability and conclusions

Code findings are indicators produced by detection rules. Business declarations supply things code cannot reliably establish, such as intended purpose, deployment context, role and affected people. Applicability logic consumes such facts and rule data; an unknown or contradictory fact must remain visible. A compliance conclusion additionally requires correct legal interpretation, adequate evidence and authorised human judgement. The newer public adapter and review response explicitly preserve the unrecorded human decision. This distinction is central to avoiding false reassurance. [E04, E06]

## Chronological candidate ledger

“Current candidate” is ambiguous unless identified. **R is the requested current checkout. W2 is the latest separately preserved candidate found in the continuation records.** Neither has a verified complete gate for its currently examined bytes.

| Candidate | Date and identity | State and verification qualification |
| --- | --- | --- |
| R, historical original | HEAD fbed8f3baf81f0c5f0860ebaf56a2845b632b547, 27 August 2026; branch feat/site-ux-redesign-2026-08-27 | Currently dirty, 242 entries before this task. Older records call an original checkout frozen, but this session does not infer all today's bytes are the previously frozen set. |
| Pre-A2 checkpoint | b69c17a5ac3a8877cde317b95d50c6b9c4ca6fcb, 31 August 2026 | P records and retained logs identify an earlier engineering checkpoint and subsequent checks; not today's R or W2. |
| Accepted A2 baseline | b58c622e966f1fdaef95c37e8cfc8181cd33139d, 1 September 2026 | Programme records describe A2 acceptance and later A4 reconciliation. A5 has historical technical evidence, with publication/release adjudication still open. Not a final integrated version of later changes. |
| S1, initial local successor | Increment dated 20 September; results recorded 21 September. b58c622 plus 20 uncommitted files | Historical custom/pytest/installed results apply to its preserved source. Two subsequent documentation labels received scoped checks, not another full gate. |
| S2, evidence journey repair | REGULA-EVIDENCE-JOURNEY-2026-09-21-02; b58c622; branch local/evidence-file-successor-2026-09-16 | Three repairs integrated at file level into that successor, not R. Now 23 unstaged changes. All 765 inventory-listed files matched in this session. Owner run later failed at pytest with eight errors. |
| J3, question-to-review child | REGULA-REVIEWABLE-OUTCOME-2026-09-22-03; b58c622; branch local/reviewable-outcome-2026-09-22 | 50 staged changes, no new commit. All 776 inventory-listed files matched. Full gate stopped at pytest; conditional checkpoint commit not made. Parent preserved. |
| W1, website r01 | REGULA-WEBSITE-EXPERIENCE-2026-09-22-04; 22 September | Website child of the reviewable-outcome work; scoped/installed checks, no full gate. Its earlier “browser not performed” status is superseded for the bounded later browser exercise, not for human acceptance. |
| W2, website/browser r02 | Same website increment, updated 23 September; b58c622; branch local/website-experience-2026-09-22 | 118 staged changes; 793 inventory-listed files matched; 28 files changed relative to W1. Installed r03 wheel and browser evidence. Full gate not run in the inspected records; reserved r02 owner output is empty. |

The inventories are stronger identities than a shared version number or base commit. Hashes below are retained identifiers, with current source membership/hash comparisons performed for S2, J3 and W2. This task did not build, install or unpack those packages.

| Object | SHA-256 |
| --- | --- |
| S1 preserved source archive | 1e95472e026e317b8c51b3bb5fbd119be29dfc96ce99989719f2fb1f3a0e7db1 |
| S1 wheel | 6db1315828b4b3c431991f2031c62c7f50cc8b609998876a9781f2b9fdca70a8 |
| S2 candidate-final-files.json | 1e07e5a21c32fb8e004a27fe2a6f4c996fdbdc05e696033b794be2ae01c70c2d |
| S2 source archive | 3347b2033cce9b9e756893377b16f86c65467d2279fcbc5027c71d399ed978c2 |
| S2 wheel | 1119c8eb93a45116d3e8fe4703b46614c3559edd9c96ad60dffb56299e3f5acd |
| J3 candidate-source-inventory-r03.json | dce64b9506ecc96c735c6bd7e0b0f3e26861f79052952a76846b3b3184f00e25 |
| J3 wheel | d02879b1748f311ae13d46ec8b557fcbf4b46c1ed0c9575b10daeef53cfe0bd3 |
| W1 candidate-source-inventory-r01.json | 3d547243da5879fb01175c256912d4ed9717c0920e88ac041d8e7f4b31699482 |
| W2 candidate-source-inventory-r02.json | 9094aed9403e7a792fffacdb9cb7860a11dce1f5305de74df919b7f2f0b9f13e |
| W2 candidate-source-r02.tar.gz | 55a7f7b9ed040827853fe77908d462dd919d236baf41b81af94bde1dc975c3ee |
| W2 installed-r03/regula_ai-2.0.0-py3-none-any.whl | 76512fd3a849848871ba5c9d84da8b04e1b4314449f100a046ddd1120992dceb |

The same live successor location has advanced since S1. S1's preserved archive, not its former location's present content, identifies that historical candidate. [E02, E08-E12]

## EVIDENCE HANDLING AND SECURITY

### Current workflow and defect status

For the repaired candidates, a producer selects permitted local evidence, generates a manifest and optional ZIP, then gives a recipient instructions to use an independently trusted installed verifier. Verification establishes consistency of listed payloads against that manifest. Origin/authenticity needs a separate trust basis; truth and professional acceptability need substantive review.

| Finding | R, inspected current checkout | Later repaired source and existing execution evidence |
| --- | --- | --- |
| REVIEW-20260921-01, generated instructions | scripts/evidence_pack.py:485-498 emits a second Python hash example which prints MODIFIED without a failure exit and joins manifest-supplied paths without the repaired handler's constraints. | W2: scripts/evidence_pack.py:490-524 directs recipients to the maintained installed verifier, explains exits and scope, and does not invent a released package installation. S2 retained actual-product-path reproduction and old-wheel negative controls; later regression uses freshly generated README commands. |
| REVIEW-20260921-02, report overwrites input | R: scripts/cli_evidence.py:568-571 writes the requested report directly after verification; the inspected path has no equivalent input/output collision protection. | W2: scripts/cli_evidence.py:588-621 protects archive, selected manifest and listed evidence through resolved-path/same-file checks, stages a report in a temporary file, flushes/fsyncs and replaces safely. Recorded regressions cover text/JSON, direct and alias collisions, preservation and repeat verification. |
| REVIEW-20260921-03, unwanted bundle inputs | R: scripts/evidence_pack.py:577-588 copies entries satisfying is_file(), which follows links, and directly opens the output archive. An unlisted linked file can enter the ZIP through this path. | W2: scripts/evidence_pack.py:635-707 validates permitted flat members and manifest before packaging, rejects unexpected/link/non-regular inputs, checks listed hashes and atomically replaces the archive through a temporary output. Actual generation regressions inspect ZIP members and absence of synthetic outside-marker bytes. |

This session observed the source contrast; it did **not** rerun exploitation or manufacture new evidence. S2's retained reproduction distinguishes old installed-product behaviour from the earlier reviewer's function-level probes. The negative-control result was **three expected failures**, not three successful product checks. [E07, E09]

Representative regression bodies inspected include W2 `tests/test_evidence_bundle.py:245-291` for generated-output instructions, `294-356` for report protection, and `436-475` for product-path bundle membership. This is more substantial than trusting test names, but their historic pass status still comes from retained logs.

### Important boundaries and limitations

**Manifest scope.** Hash checks cover listed payloads. They do not prove that every ZIP member is covered, that the manifest is authentic, or that evidence is true. Generated verifier/instruction material is not automatically trusted because it arrived in the same untrusted archive. Later instructions make this distinction explicit. [E07]

**Untrusted paths and malformed manifests.** The newer verification path validates shape, algorithm/digest fields, path containment and read failures. ZIP input has bounded size/member handling. Bundle generation additionally enforces a flat pack, case-folded/reserved-name rules and explicit documented extras. Unlisted files, including an otherwise legitimate extra report, are not silently accepted into that bundle contract. R's partial safeguards must not be equated with these later controls. [E07]

**Links and special files.** Bundle policy rejects links/non-regular inputs before copying their contents; this includes internal links under the bounded ordinary-file policy. Report aliases use path resolution and file identity. A separate in-pack report location can be legitimate for verification when it is not protected evidence, while subsequently making that directory unsuitable for strict bundle membership. Platform-dependent alias/case tests are not proof of identical Windows behaviour. [E07, E09]

**Failure and atomicity.** Safe temporary-output replacement protects an existing report/archive against the tested failure paths. It is not a transaction over every generated file in an existing pack directory. S2's repair report retains the limitation that ordinary generated files may already have changed before a later unexpected-member rejection, while the prior ZIP remains preserved. [E09]

**Concurrency.** Stable input is still an assumption. No general cross-process locking or guarantee against a malicious concurrent file swap was established. Fixing a deterministic output collision does not establish universal race safety.

**Signing and timestamps.** Optional cryptographic dependencies and an out-of-band trusted key are separate from basic consistency. The signature path can be unverifiable without dependencies; strict modes reject rather than confer trust. The latest core-only installed exercise did not newly validate optional signing/timestamp extras. [E07, E12]

**Sensitive information.** A correctly hashed evidence pack may still contain material that should not be shared. Local operation does not provide redaction, permission-to-disclose or legal privilege. No real confidential outside files were needed for the retained synthetic marker tests. This handover did not inspect customer datasets or secrets.

**Evidence levels are distinct.** A function probe demonstrates a selected function under its shim; a handler test exercises a handler; an installed workflow adds package/provenance coverage; a complete gate adds the repository's required suite for an exact source. None supplies human/legal acceptance. [E08-E12]

## VALIDATION AND RELEASE-READINESS MATRIX

### Required engineering gate

The repository's four-stage command is established directly by **R / AGENTS.md:13-15**:

```bash
python3 tests/test_classification.py && python3 -m pytest tests/ -q && python3 -m scripts.cli self-test && python3 -m scripts.cli doctor
```

Later retained runners use the existing compatible Python 3.12.3 environment, scoped cache/audit paths and stop-on-failure sequencing. Gate runs use source code; separate installed exercises test a disposable installation without source PYTHONPATH. These must not be collapsed.

**No test, preflight, build, installation or gate was run for this handover.** The following are recorded results read from existing evidence. Counts are preserved as separate populations; rows and passing subtests must not be added together.

| Candidate/date and artefact | Command/check and environment | Recorded outcome | What it establishes, and current applicability |
| --- | --- | --- | --- |
| Older dirty-original record; C/ACTIVE_CONTEXT.json, preserved_test | `python3 -m pytest tests/test_product_boundary_contract.py tests/test_evidence_bundle.py tests/test_evidence_format_v1.py -q` | **30 passed in 5.09s**, scoped historical record | Summary associates it with dirty fbed8f3. No complete per-file identity was established for today's R. Not a full gate. |
| Pre-A2; P/A2/raw-logs/07-custom-runner.log, 08-complete-pytest.log, 09-complete-pytest-loopback-capable.log and 10-12 diagnostic logs | Custom runner; two pytest attempts; separate diagnostics | Custom **1,465 passed, 0 failed, 8 skipped**, **1,369 functions**. Pytest **2,979 passed, 45 skipped, 8 errors** in **561.24s**, and again **360.43s**. Separate self-test **6/6**; doctor **8 pass, 3 info, 1 warning**, later private doctor **9 pass, 3 info**. | Historical attempts, not current candidate. Separate successful diagnostics cannot repair failed chains. |
| Pre-A2 owner result, 1 September; P/A2/raw-logs/17-owner-wsl-complete-pytest-20260901-091706.log:56-57 | Owner WSL full pytest; programme binds preceding source checkpoint | **2,987 passed, 45 skipped in 287.88s**, exit **0** | A successful historical pytest result, not proof of W2 or one four-command chain assembled from unrelated attempts. |
| A5 historical Linux, 2 September; P/A5/owner-results/wsl-20260902-194716/pytest.stdout.log:44 | Owner WSL pytest on accepted older baseline per P | **2,987 passed, 45 skipped in 443.24s**, recorded exit **0** | Supports historical technical acceptance recorded by P. Does not verify later repairs or current dirty R. |
| A5 historical Windows, 4 September; P/A5/owner-results/windows-critical/run-20260904-143501/pytest.output.log:3 | Critical suite, Python 3.12.10, symlink-capable native environment | **97 passed in 7.56s**; result summary records no skips. Earlier **96 passed, 1 skipped** remained distinct. | Native evidence for older source only. P also reports **274/274** Edge checks; their raw browser execution was not independently examined here. |
| S1, 21 September; final-gate-result.json and final-*.stdout.log | Custom then full pytest, Python 3.12.3/WSL; diagnostics after chain failure | Custom **1,465 passed, 0 failed, 8 skipped**, **1,374 functions**, exit **0**. Pytest **2,984 passed, 45 skipped, 8 errors, 11 subtests passed in 163.93s**, exit **1**. | **Full gate did not pass.** Errors are recorded socket-fixture PermissionErrors. Self-test/doctor were separate successful diagnostics. Does not apply wholesale to S2/J3/W2. |
| S1, after two documentation-label changes; final-count-checks.json | Pytest published-count/cascade checks | **69 passed, 4 subtests passed in 14.28s** | Scoped result after changes, not another full gate. |
| S1 installed-result.json | Core-only disposable wheel, provenance and recipient checks | **8 installed-artefact checks**; valid directory/ZIP **0**, modified/missing **1**, malformed **2**; portable valid **0**, adverse traversal/malformed/link/special-file cases **1** | Bounded installed behaviour for S1 wheel. Does not eliminate the later generated-README/report/bundle defects or prove all optional commands. |
| S2, 21 September; regression-red-old-wheel.*, affected-*.json, repair-and-count-contracts.* | Old-wheel negative control; affected source tests; final repair/count contracts | Negative control **3 failed, 5 deselected in 0.93s**, expected defects. Interim **124 passed in 13.64s**, then **125 passed in 13.47s**. Final **123 passed, 4 subtests passed in 25.61s**. | Distinct scoped runs before/after adjustments; not additive. Final exact command is given below. |
| S2 bounded diagnostics/installation | Custom runner correction, independent self-test/doctor; installed-result.json | First custom **1,465 passed, 1 failed, 8 skipped**, then **1,465 passed, 0 failed, 8 skipped**, **1,383 functions**. Self-test **6/6**; doctor **9 pass, 3 info**. **8 artefact checks**, **5 recipient regression groups**; 14 report-identity operations are overlapping observations. | The import-contract failure was preserved and corrected. Core installed-path evidence supports S2 repairs, not a complete gate. |
| S2 owner run, 22 September; owner-full-gate/result.json, custom-runner.stdout, pytest.stdout:374 | Actual owner runner, source identity 1e07e5a..., same compatible interpreter | Custom **1,465 passed, 0 failed, 8 skipped**, **1,383 functions**, exit **0**. Pytest **2,993 passed, 45 skipped, 8 errors, 11 subtests passed in 190.70s**, exit **1**. Source unchanged. | **Actual failed full-gate attempt recovered.** Self-test and doctor not reached in that chain. Eight socket-fixture errors remain visible; no product pass inferred. |
| Later refused S2 invocation; J3/gate-reconciliation-2026-09-22-r01/result.json | Output-location preflight, no START stage for that invocation | Reserved output already occupied by retained earlier attempt. No new product test result. | Explains owner rejection without erasing the previous actual failure. Not a passing preflight, completed test or proof of a still-active process. |
| J3, 22 September; child-full-gate/result.json and stdout | Custom then full pytest, source identity dce64b95... | Custom **1,465 passed, 0 failed, 8 skipped**, **1,398 functions**, exit **0**. Pytest **3,008 passed, 45 skipped, 8 errors, 11 subtests passed in 261.80s**, exit **1**. Source unchanged. | **Full gate failed/stopped.** Separate self-test **6/6** and doctor **8 pass, 3 info, 1 warning** are diagnostics. Warning concerns mounted audit-directory permissions, not demonstrated client disclosure. |
| J3 installed-r02 evidence and wheel-to-r03-source.json | Disposable installation; artefact/recipient and synthetic workbook journey | **8 artefact checks**, **5 recipient groups**, synthetic complete CLI/workbook journey reported passed; **140 runtime members** matched r03 | Supports installed bounded workflow. No human acceptance. Earlier failed build/package attempts remain in TEST-SUMMARY.json. |
| W1, 22 September; TEST-SUMMARY.json, installed-r02/result.json | Website/review scoped suites, static links/locales, disposable install | Final source scope **36 passed in 3.28s**; prior affected scope **178 passed, 4 subtests passed in 21.84s**. Installed website scope **9 passed in 3.01s**, **8 artefact checks**. **2,020** internal links, zero dead; **182** locale links over **16** pages. | Source/installed scopes only. Full gate and browser work not completed at this stage. Later W2 supersedes changed bytes. |
| W2, 23 September; B/BROWSER-RESULTS.md:45-53; W/installed-r03 | Website scope, then final rebuilt installed website/review scope | Source **36 passed in 3.55s**, then **36 passed in 3.36s**, both before final response-wrap edit. Final installed **24 passed in 5.68s**; **8 artefact checks, 0 findings**. | Final installed exercise supports W2's bounded paths; the earlier 36-pass source result is not final-byte full verification. |
| W2, B/downloaded-draft-cli-r02/result.json and browser records | Actual synthetic downloaded draft through installed CLI; browser measurements | Provenance, review/bundle, folder verification, ZIP verification and public-sample verification: each **exit 0**. Nine page-layout and five regional measurements; **2,038** internal references, zero dead; locale **182/16**, zero cue failures; privacy scan **793 files, zero findings**. | Recorded synthetic/mechanical results, not additional pytest cases or legal/human acceptance. Tracker-source exemptions remain warnings. |
| W2, B/owner-preflight-r02.stdout; W/owner-website-full-gate-r02 | Source/interpreter/membership/output preflight | **PREFLIGHT PASS: exact candidate, expected interpreter and empty reserved output. No test executed.** Actual destination was accessible, ordinary and empty, including hidden entries, at inspection. | **No verified complete W2 gate.** No full custom-runner/pytest/self-test/doctor result for W2 is present there. |
| All current candidates | Release, CI, deployment, native Office, professional/human/buyer acceptance | **Not established for current source.** No new external observations obtained. | CI configuration, an approval, local staging or a preflight does not supply these results. |

The final S2 scoped command, from `repair-and-count-contracts.json`, was:

```text
python -m pytest tests/test_evidence_bundle.py tests/test_site_facts.py tests/test_collection_integrity.py tests/test_cascade_count.py tests/test_source_of_truth.py tests/test_published_count_manifest.py -q
```

Here `python` denotes the recorded existing virtual-environment interpreter, with personal prefix omitted. This is a transcription of a recorded command, not an instruction executed now.

### Failed attempts and unexecuted checks retained

J3's **TEST-SUMMARY.json** records adverse controls (**2 failed, 13 deselected**), a collection failure caused by a missing build backend in that environment, an initial wheel missing the new review module, and an initial custom-runner result of **1,465 passed, 5 failed, 8 skipped**. Later bounded repairs/checks are recorded; these earlier failures have not been deleted or relabelled as passes. Its **396 passed, 1 skipped, 4 subtests passed** scoped population predates final package/source adjustments and is not the final full gate.

W1 retains an initial wrong-interpreter installation preflight, negative controls (**2 failed, 6 deselected**), surface/membership/navigation failures (**3 failed, 79 passed**) and localisation failures (**2 failed, 176 passed, 4 subtests passed**) before corrected scoped results. These are not evidence of a passing release gate.

W2 browser limitations include a cached-CSS failed observation, a CSP-blocked diagnostic, a hidden-radio click timeout resolved through the visible label, an inconclusive listener inspection and incomplete transport-byte capture. They are documented rather than suppressed. No new optional signing/timestamp, complete native-platform or human acceptance was added. [E10-E12]

### Exact gate-reconciliation conclusion

S2's owner directory is **occupied by a real earlier failed run**, including RUN_STARTED.json, result.json, source-after.json and actual stage streams. Therefore the later owner command's no-START rejection was an output-preservation preflight stop, not a new product failure or a reason to erase the prior logs.

The separately reserved J3 and W2 owner destinations were empty when inspected. The latest W2 runner is `W / run-owner-website-full-gate-r02.py`, pinned to inventory **9094aed9...**, base **b58c622...**, its branch and expected interpreter. Its code preserves exclusive log creation, source checks and stop-on-failure sequencing. It was **read, not executed**, in this task. [E09-E12]

A proposed follow-up is to use that existing exact-source owner action in a permitted runtime after resource/source coordination. Do not rerun the occupied S2 destination, change expected hashes to accept drift, or assemble successful stages from different attempts. A current-source result.json, stage streams and source-after.json from one complete permitted run are the missing engineering acceptance artefacts.

## REGULATORY AND REPORTING CAPABILITIES

### Jurisdiction scope and source freshness

The inspected rule/decision data explicitly includes **EU, South Korea and Colorado**. W2's five regional website experiences are **EU in German, UK in English, Brazil in Portuguese, Singapore in English and Korea in English**. That is **five regional experiences, not five additional languages or five complete legal engines**. EN, DE and PT-BR are the observed principal content languages. [E04, E11-E12]

The decision-model file declares version **2026-08-26.1** and source retrieval date **2026-08-26**. It contains source references, but their present authority, amendments and interpretation were not legally reverified here. Adapters have fields for source dates/versions, including missing values; the availability of fields does not prove every finding has a fresh authoritative citation. The website SOURCE-REGISTER records retrieval limitations and partial access for some material. [E04, E11]

The review workflow accepts declared purpose, role and deployment facts because a repository scan cannot reliably infer them. Rule-map crosswalks and article references are aids to review, not a complete conformity assessment. This document deliberately states no newly verified regulatory deadline.

### Reports and false reassurance

The later HTML response improves readability by grouping questions, evidence, uncertainty and review status. The browser record supports repair of mobile hash wrapping. JSON records and manifests give technical recipients more explicit structure and traceability. However:

- Human interpretation of the report has not been observed in a completed independent task.
- Source-derived findings can be incomplete or heuristic.
- Unsupported files, truncated/limited scans, unreadable files and absent declarations can leave material unknown.
- Hash consistency says nothing about the accuracy, completeness or provenance of a claim unless separate evidence establishes those properties.
- A rule-model answer with correct software behaviour may still be legally wrong or incomplete.
- “Zero findings”, “no missing files” and a zero exit code each answer a different technical question; none is a compliance certificate.

A qualified review of legal-source freshness, claims and deployment facts remains necessary before a professional service or jurisdiction-specific promise is accepted. No new global legal review was performed. [E03-E07, E14-E16]

## COMMERCIAL, DELIVERY, AND GOVERNANCE STATUS

### Authority and integration

The owner-authorised source transitions are recorded with bounded scopes. Their existence does not authorise new work in this read-only handover.

- **REGULA-LOCAL-SUCCESSOR-2026-09-16-01:** later records preserve the owner's local-successor approval and the separate original/accepted baseline. There is no need to infer a fresh approval from a filename.
- **REGULA-EVIDENCE-JOURNEY-2026-09-21-02:** approval covers the three repairs, relevant source/tests/generated instructions/docs, synthetic verification, disposable builds/installation, file-level integration and private records. It expressly excludes commits, remote operations, publication/deployment, payments, messaging, client-data transfer and new paid consumption. Assigned writer status is not proof all other processes are idle.
- **REGULA-REVIEWABLE-OUTCOME-2026-09-22-03:** the recorded local checkpoint-commit permission is conditional on required verification and diff/privacy review. The retained J3 result says no commit because the full-gate condition was unmet. It does not permit remote push, deployment, payment, external model integration or A5 closure.
- Website continuation records identify the later local website work and preserve no-publication/commercial boundaries. They do not establish a new merchant or release approval.
- **This task:** read-only investigation plus this one new Markdown file. Historical execution instructions were treated as evidence, not run.

S2's repaired files are integrated into its local successor. J3's work is integrated into its child and staged. W2's work is staged in its isolated website candidate. Git identities read now corroborate no new checkpoint commit in those candidates. W2's result explicitly says it has not been integrated into the pinned earlier successor. R still differs materially. [E01-E02, E09-E12, E15]

No remote push, release, deployment, revenue, payment settlement or operating checkout/consultancy-enquiry path was independently observed. No external services were contacted. Local files and reports cannot settle those questions. A5 remains a separate unresolved programme gate.

### Prices and delivery economics

The retained decision brief provides **hypotheses**, not validated sales or permission to charge:

| Proposal | Recorded scope/status |
| --- | --- |
| £49 total one-off kit | Proposed entry product, not a demonstrated accepted market price |
| £1,450 net review | One AI system/feature, five questions, two stakeholder interviews and bounded technical peer review/handover; kit included |
| £395 net managed-review cycle | Later cost-informed pilot proposal, not an active monthly subscription |

The workbook/decision discussion's **£0.22** is **headroom above a chosen margin target**, not total contribution or profit. The decision brief's £49 model gives **£12.93 contribution after £15 acquisition cost, before fixed overhead**, whereas £29 produces **minus £2.84** under the same illustrative assumptions. Model assumptions include tax, payment fees, reserves, delivery/support time and labour cost. They were not revalidated against actual seller status or fulfilment here. [E13]

The original pricing r01 safety verification, learner copies and stored print-definition repairs are recorded as completed within their limited scopes. They were not recreated, recalculated or accepted as native Office results in this task. **34 private checks** and the bounded pricing safeguards are not engineering, buyer or professional acceptance. [E14]

Delivery needs actual skills assessment, supervised rehearsal, competent technical/professional review, honest scoping and measured effort. A collaborator's commercial-law qualification, if available, could be relevant to a defined engagement, but neither qualification nor a proposed partnership establishes specialist competence, insurer acceptance or permission to claim professional review. No such partner acceptance was established.

### Opportunity, defensibility and risk

**Inference:** a useful opportunity is reducing the effort to produce a small, traceable, reviewable answer from local evidence while keeping unknowns and changed evidence visible. The later implementation is more concrete than a generic compliance checklist.

**No demonstrated moat was established.** The selected materials do not prove exclusive data, protected IP, exceptional distribution, switching costs, validated detection superiority or repeat revenue. The existing code and accumulated engineering evidence are assets; they are not by themselves a durable competitive advantage. No market/competitor research was performed in this no-network task.

A future defensible service could depend on reliable delivery, qualified review, trusted distribution, evidence quality and repeatable measured outcomes. Those are hypotheses requiring validation, not existing capabilities or authorised roadmap commitments. Main risks are false legal reassurance, source/version confusion, incomplete platform verification, high support/review cost at low prices and marketing claims stronger than the evidence. [E03, E13-E16]

## GAP AND NEXT-DECISION REGISTER

The small set below is prioritised by consequence. These are proposed decisions or follow-ups, **not actions authorised by this handover**.

| Priority/type | Gap and supporting evidence | Consequence | Smallest next step; responsible actor; closing evidence |
| --- | --- | --- | --- |
| 1. Immediate source/release blocker | R still has unsafe evidence paths; S2/J3/W2 are distinct uncommitted candidates. [E01,E02,E07] | Reviewer or owner can test, ship or amend the wrong source. | Owner/controller selects the exact candidate to advance and preserves the others. Close with an explicit source/inventory identity and reviewed integration scope, not a reset or shared version string. |
| 2. Immediate verification blocker | W2 has preflight/scoped evidence but no full gate; earlier candidates stopped on eight socket errors. [E08-E12] | Conditional commit/release criteria remain unmet. | Owner uses the existing inspected W2 r02 action in a permitted, coordinated runtime. Preserve one complete chain, true exits, counts, environment and source stability. If blocked, retain the exact failure; do not disable controls. |
| 3. Professional/release claims | Current legal-source freshness, complete platform behaviour and publication/privacy adjudication are unsettled. [E04,E07,E12,E15] | Correct software can still mislead, fail on another platform or expose unsuitable material. | Appropriate engineering/platform reviewer and competent regulatory reviewer inspect the selected candidate's claims and boundaries; owner adjudicates A5 separately. Close with source-bound platform evidence and dated, scoped professional decisions. |
| 4. Customer-journey validation | Automated synthetic paths exist; no completed independent learner/reviewer task. Keyboard/zoom/screen-reader/native-language questions remain. [E06,E12,E14] | A technically exportable pack may be confusing, unusable or unacceptable to its recipient. | Use existing observation/learner task cards with consenting participants and a competent reviewer. Record completion, errors, unsupported conclusions, recovery, review acceptability and effort, including failures. Do not write participant answers. |
| 5. Commercial/delivery validation | Prices/costs are hypotheses; seller/tax/competence/fulfilment and buyer demand unverified. [E13-E15] | Charging could promise a service whose scope, margin or value is not established. | Owner and qualified advisers verify seller/tax/scope, then a bounded supervised pilot with actual cost and buyer evidence, under separate commercial authority. Close with real effort/cost, acceptance and willingness-to-pay evidence, not model headroom. |
| 6. Longer-term opportunity only | Agentic investigation, System One models, expanded jurisdictions and richer reports are not proven solutions to a measured bottleneck. [E04,E05,E13,E16] | Premature platform expansion increases complexity and external-data risk without demonstrated benefit. | After the core journey is validated, define one measurable bottleneck and a bounded experiment. External models/data/jurisdictions require explicit authority and professional boundaries. Compare accuracy, effort, comprehension and privacy against the existing workflow. |

The most important acceptance separation is: **component correctness → complete engineering gate → chosen-source integration → complete-task usability → professional acceptance → buyer value → commercial readiness**. Evidence for one does not substitute for the next.

## EVIDENCE LEDGER AND LIMITATIONS

### Compact evidence map

Ranges below identify selected passages actually inspected or the precise existing result objects. Candidate prefixes are essential: a path with the same name can have different contents in R and W2.

| ID | Material conclusions | Primary location or precise identifier |
| --- | --- | --- |
| E01 | R root/branch/HEAD/dirty state; task boundaries; gate definition | Read-only Git top-level, branch, HEAD, status and source/hash inventory captured at 17:59 BST; R/AGENTS.md:13-32; docs/ENGINEERING_ROADMAP.md:7-54 |
| E02 | Candidate separation, current source identities and staging | C/ACTIVE_CONTEXT.json: original_checkout, current_successor_increment, reviewable_outcome_increment, website_experience_increment; corresponding source Git status; S2/candidate-final-files.json; J3/candidate-source-inventory-r03.json; W/candidate-source-inventory-r02.json; per-file hash comparisons in this session |
| E03 | Product claims, installation and architecture | R/README.md:4,10,66-94; pyproject.toml:5-16,31-82,93-124; scripts/constants.py:16-54; docs/architecture.md:57-94; .github/workflows/ci.yaml:13-55 |
| E04 | Scanner limits, facts, decision logic and jurisdictions | R/scripts/report.py:655-794; scripts/decision_kernel.py:28-92,199-253,375-408; references/decision_model.v1.json:1-38 and jurisdiction objects; scripts/regulation_map.py:25-110; R/scripts/decision_adapters.py:29-115; W2/scripts/decision_adapters.py:83-199 |
| E05 | Network/data-flow qualifications | R/scripts/api_server.py:52-70,121-159,253-279; W2/scripts/api_server.py:53-80,132-170; R/scripts/mcp_server.py:174-221,397-466; scripts/telemetry.py:29-51,131-158; scripts/timestamp.py:257-271; scripts/bias_eval.py:92,151-163,295-321; scripts/feed.py:152-170; R/scripts/weekly_digest.py:260-305 |
| E06 | Question/evidence/review, recovery and change behaviour | W2/scripts/cli.py:1296-1304; scripts/review_record.py:27-80,300-365,412-594; site/assets/review-starter.js:4-85,138-179; docs/review-response-guide.md:39-111; tests/test_review_journey.py:90-141 |
| E07 | Three old defects and repaired source; security contract | R/scripts/evidence_pack.py:485-498,577-588; R/scripts/cli_evidence.py:510-543,568-571; W2/scripts/evidence_pack.py:92-113,490-524,635-707; W2/scripts/cli_evidence.py:218-414,508-621; W2/tests/test_evidence_bundle.py:245-356,436-475 |
| E08 | S1 historical results and package identity | S1/preservation.json; candidate-final-files.json; final-gate-result.json; final-custom-runner.stdout.log:599; final-pytest.stdout.log:374 and socket traces; final-count-checks.json and stdout:2; installed-result.json |
| E09 | S2 implementation/reproduction/scoped/installed/owner outcome | S2/REPAIR-RESULT.md:125-150; baseline-product-path-reproduction.json; regression-red-old-wheel.json; repair-and-count-contracts.json and stdout; installed-result.json; installed-report-identities.json; owner-full-gate/result.json, RUN_STARTED.json, source-after.json, custom-runner.stdout:629, pytest.stdout:374 |
| E10 | J3 source, gate failure, installation, conditional commit and reconciliation | J3/FINAL-RESULT.json:2-29; TEST-SUMMARY.json; child-full-gate/result.json and stdout; wheel-to-r03-source.json; gate-reconciliation-2026-09-22-r01/result.json; actual reserved owner-child-full-gate directory |
| E11 | W1/W2 preservation, scoped checks, regional surfaces | W/TEST-SUMMARY.json; WEBSITE-RESULTS.md; SOURCE-REGISTER.json; candidate-preservation-r01.json and r02.json; candidate-source-inventory-r01.json and r02.json; W2/site/experiences and site/field-notes; W2/data/supported_surface_manifest.json |
| E12 | Latest browser/installed/gate and integration status | B/BROWSER-RESULTS.md:3-90,123-145; B/BROWSER-RESULTS.json; B/downloaded-draft-cli-r02/result.json; W/installed-r03/result.json, website-record-workflow.stdout:2, artefact-guard.stdout; B/owner-preflight-r02.stdout; W/run-owner-website-full-gate-r02.py:16-22,36-59,64-97; actual empty owner-website-full-gate-r02 directory |
| E13 | Positioning, prices, assumptions and learner feedback status | D/CODEX-EXECUTION-PROMPT.md:11; D/DECISIONS-UX-AND-PRICES.md:9-27,40-59; D/Regula-Codex-Execution-2026-09-17.md:94; selected delivery-playbook context |
| E14 | Private delivery work versus human/native acceptance | C/ACTIVE_CONTEXT.json: independent_work and recorded checkpoints; J3/OBSERVATION-ADDENDUM.md:7-9,33-53; J3/OUTCOME-ACCEPTANCE.md and FINAL-RESULT.json acceptance fields |
| E15 | Bounded authority, A2/A5 history and no release inference | P/PROGRAM_STATE.json; P/A5/owner-actions/REGULA-EVIDENCE-JOURNEY-2026-09-21-02-APPROVAL.md; P/A5/owner-actions/REGULA-REVIEWABLE-OUTCOME-2026-09-22-03-APPROVAL.md; C/ACTIVE_CONTEXT.json authority fields; P/A2/raw-logs/17-owner-wsl-complete-pytest-20260901-091706.log:56-57; P/A5/owner-results/wsl-20260902-194716/pytest.stdout.log:44; P/A5/owner-results/windows-critical/run-20260904-143501/pytest.output.log:3 |
| E16 | Unknown moat, demand, legal correctness, market superiority | Explicit absence of qualifying evidence within the inspection boundaries; not a negative claim about all possible external evidence. No market, registry, legal-site or deployment query performed. |
| E17 | Repository preservation during this task | Initial in-memory inventory of 823 Git-visible entries, initial index SHA-256 65e3339fbc6567e7b6118ef8933c7fa003c82fe3a5c0ac147ceaed637ec3d70c, and final comparison described below |

### Reconciled conflicts and chronology

1. **Historical acceptance versus later failed gates.** A2/A5 contain genuine older results. S1, S2 and J3 have different source identities and different pytest totals. Both statements can be true. Neither proves W2 passed.
2. **S2 report versus later owner result.** The original repair report prepared an owner action; the later directory contains an actual failed run. That newer primary result supersedes “not yet run” for S2 only. The subsequently refused invocation added no test result.
3. **W1 browser absence versus W2 browser evidence.** The later bounded browser exercise supersedes the earlier no-browser status, but leaves human/professional acceptance open.
4. **“Frozen original” versus current dirty checkout.** Historical records mention a smaller original change count, while this session observed 242 entries. Timing and cause of all additional pre-existing changes are not resolved. This task preserved them.
5. **README versus deployment history.** R's README still says Pages is unavailable; the current HEAD commit subject refers to restoring GitHub Pages. Neither is a live-service observation. Present deployment availability is unknown.
6. **Counts and badges versus execution.** README/published collection totals are not passes. Different collectors, custom function counts, pytest counts, subtests and installed groups are distinct populations.
7. **Recent content versus legal authority.** Recently generated regional copy and a source register do not establish that all underlying law, amendments or interpretations are current.
8. **Product source versus private summaries.** Where a summary says repaired, source identity and the actual later implementation support that only for the identified successor. The older R handlers still contradict an unqualified “Regula is fixed” statement.

### I could not verify

- A complete current-source gate for R or W2.
- A current remote release, package registry state, production deployment or current public website behaviour.
- End-to-end merchant checkout, payment, fulfilment, consultancy enquiry receipt or revenue.
- Independent professional acceptance, participant comprehension, willingness to pay or measured buyer benefit.
- Current legal correctness or exhaustive jurisdictional scope.
- Latest-candidate Windows alias/case behaviour, optional signing/timestamp installation coverage, full accessibility or native-language quality.
- Independent off-device recovery; local archives and matching inventories are preservation evidence.
- Machine-wide process idleness or source exclusivity outside the visible coordination evidence.
- Every command, test body, integration, ignored file or historical document; this was selective inspection.
- Full provenance of every pre-existing dirty change in R, or whether unprovided external evidence would close any of the above.

### Search boundaries

No network calls, package installation, repository mutation, product execution, tests, preflights, build/release commands or new screenshots were performed. Existing logs, structured records and selected source bodies were read. Dates/counts above derive from those records and the current local clock; timestamps are not invented approval signatures.

Searches stayed within Regula source and its named local continuation/programme/delivery records. Credentials, environment-secret files, unrelated personal data and customer source were excluded. Large historical consolidations were used only as context leads when needed, not copied wholesale. Saved browser results were read, but no visual certification was inferred from screenshots merely being present.

The source inventory comparison covers Git-visible tracked and untracked entries. It does not hash ignored data or all Git internals. The pre-existing untracked nested directory at `output/candidate-remediation-2026-08-30/` was recorded as a directory rather than recursively fingerprinted; it was not changed. These boundaries limit the preservation claim.

### Task preservation and final read-back

At 18:28:21 BST on 23 September 2026, the read-only comparison found no modified or removed entries in the initial inventory. All 822 pre-existing regular-file hashes and the recorded nested-directory metadata were unchanged. HEAD, branch and the Git index hash were unchanged. Using the same full untracked-file status mode, the only added status entry was this document, bringing the count from 242 to 243.

This document was read back as a non-empty UTF-8 Markdown file with all requested sections. Screening of its contents found no expanded personal-machine paths, em/en dashes or matches for the credential patterns checked. That screening is bounded, not a guarantee about every possible confidential fact. Only this new handover was written; no existing source, tests, configuration, documentation, programme records, evidence or Git history was intentionally changed. The ignored-file and nested-directory limits stated above still apply.
