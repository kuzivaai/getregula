# Clear-Case Clusters — Batch Confirmation Sheet

**Purpose:** These are findings the model considers clearly TP or FP.
The human rater confirms each cluster as a batch (with spot-checks),
rather than reviewing each finding individually.

**How to use:** Read the cluster description, spot-check 2-3 findings,
then confirm or reject the entire cluster. If you reject, move the
cluster to individual review.

---

# Targeted Corpus

## Cluster T-TP-1: Deepface Core Biometric Modules (22 findings)

**Proposed label: TP** — All are core modules of the deepface biometric
identification library. Each directly implements facial recognition,
verification, demography analysis, embedding generation, or model loading
for biometric models. Falls under Annex III Category 1.

**Spot-check guidance:** Pick any 3 files. Do they implement or directly
serve face recognition/verification? If yes, confirm the cluster.

| ID | File | Confidence |
|----|----- |------------|
| T-deepface-001 | `deepface/DeepFace.py` | — |
| T-deepface-002 | `deepface/api/src/app.py` | — |
| T-deepface-004 | `deepface/models/FacialRecognition.py` | — |
| T-deepface-005 | `deepface/models/demography/Age.py` | — |
| T-deepface-006 | `deepface/models/demography/Gender.py` | — |
| T-deepface-007 | `deepface/models/demography/Race.py` | — |
| T-deepface-008 | `deepface/models/facial_recognition/ArcFace.py` | — |
| T-deepface-009 | `deepface/models/facial_recognition/Buffalo_L.py` | — |
| T-deepface-010 | `deepface/models/facial_recognition/DeepID.py` | — |
| T-deepface-011 | `deepface/models/facial_recognition/Dlib.py` | — |
| T-deepface-012 | `deepface/models/facial_recognition/Facenet.py` | — |
| T-deepface-013 | `deepface/models/facial_recognition/FbDeepFace.py` | — |
| T-deepface-014 | `deepface/models/facial_recognition/GhostFaceNet.py` | — |
| T-deepface-015 | `deepface/models/facial_recognition/OpenFace.py` | — |
| T-deepface-016 | `deepface/models/facial_recognition/SFace.py` | — |
| T-deepface-017 | `deepface/models/facial_recognition/VGGFace.py` | — |
| T-deepface-023 | `deepface/modules/datastore.py` | — |
| T-deepface-024 | `deepface/modules/modeling.py` | — |
| T-deepface-025 | `deepface/modules/recognition.py` | — |
| T-deepface-026 | `deepface/modules/representation.py` | — |
| T-deepface-027 | `deepface/modules/streaming.py` | — |
| T-deepface-028 | `deepface/modules/verification.py` | — |

**Confirm cluster?** `____` (yes / no / move to individual review)

---
## Cluster T-TP-2: face_recognition Core (2 findings)

**Proposed label: TP** — Core API and CLI of the face_recognition library.
Directly performs face detection and identification. Annex III Category 1.

| ID | File |
|----|------|
| T-face_recognition-002 | `face_recognition/api.py` |
| T-face_recognition-003 | `face_recognition/face_detection_cli.py` |

**Confirm cluster?** `____`

---
## Cluster T-TP-3: Credit Scoring Models (4 findings)

**Proposed label: TP** — Jupyter notebooks and utility code implementing
PD/LGD/EAD credit risk models. Directly performs credit scoring decisions.
Annex III Category 5 (access to essential services).

| ID | File |
|----|------|
| T-Lending-Club-Credit-Scoring-001 | `notebooks/3_pd_modeling.ipynb` |
| T-Lending-Club-Credit-Scoring-002 | `notebooks/4_lgd_ead_modeling.ipynb` |
| T-Lending-Club-Credit-Scoring-003 | `notebooks/5_pd_model_monitoring.ipynb` |
| T-Lending-Club-Credit-Scoring-005 | `src/modelling_utils.py` |

**Confirm cluster?** `____`

---
## Cluster T-TP-4: Other Clear TPs (2 findings)

| ID | Repo | File | Category | Reasoning |
|----|------|------|----------|-----------|
| T-AI-Resume-Analyzer-001 | AI-Resume-Analyzer | `App/App.py` | Annex III, Category 4 | AI-powered resume analysis tool. Annex III Category 4 — empl |
| T-Face-Biometry-001 | Face-Biometry | `app.py` | Annex III, Category 1 | Application that uses face_recognition for biometric identif |

**Confirm cluster?** `____`

---
## Cluster T-FP-1: Packaging / Documentation Files (3 findings)

**Proposed label: FP** — setup.py and Sphinx conf.py files. These are
packaging and documentation infrastructure. They do not perform or enable
the regulated activity.

| ID | File | Reasoning |
|----|------|-----------|
| T-deepface-029 | `setup.py` | Packaging/distribution file. Does not perform or enable biom |
| T-face_recognition-001 | `docs/conf.py` | Sphinx documentation configuration file. Does not perform bi |
| T-Lending-Club-Credit-Scoring-004 | `setup.py` | Packaging file. Does not perform credit scoring. Standard in |

**Confirm cluster?** `____`

---

# Blind Subset

## Cluster B-FP-1: Test Files (10 findings)

**Proposed label: FP** — All are test files. Per LABELLING_CRITERIA
context rule 2: 'test code is generally FP unless the test itself
contains hardcoded credentials or demonstrates a genuinely risky pattern.'

| # | Tier | Project | File |
|---|------|---------|------|
| 1 | minimal_risk | langchain | `libs/standard-tests/tests/unit_tests/test_decorate` |
| 6 | agent_autonomy | app_crewai | `lib/crewai-tools/tests/rag/test_mdx_loader.py` |
| 12 | minimal_risk | scikit-learn | `sklearn/utils/tests/test_optimize.py` |
| 15 | agent_autonomy | app_aider | `tests/basic/test_linter.py` |
| 28 | minimal_risk | instructor | `tests/test_logging.py` |
| 34 | minimal_risk | instructor | `tests/test_message_processing.py` |
| 38 | minimal_risk | pydantic-ai | `tests/test_utils.py` |
| 43 | minimal_risk | pydantic-ai | `tests/test_tools.py` |
| 46 | agent_autonomy | app_crewai | `lib/crewai/tests/cli/tools/test_main.py` |
| 48 | minimal_risk | instructor | `tests/dsl/test_simple_type_fix.py` |

**Confirm cluster?** `____`

---
## Cluster B-FP-2: Type Definitions / Package Inits (6 findings)

**Proposed label: FP** — Type definition files, package __init__.py,
and parameter schema files. Structural infrastructure, not AI application logic.

| # | Project | File |
|---|---------|------|
| 8 | openai-python | `src/openai/types/beta/thread_create_and_run_params` |
| 20 | scikit-learn | `sklearn/datasets/__init__.py` |
| 25 | openai-python | `src/openai/types/evals/create_eval_completions_run` |
| 29 | langchain | `libs/langchain/langchain_classic/load/__init__.py` |
| 30 | openai-python | `src/openai/types/responses/response_input_image_pa` |
| 41 | openai-python | `src/openai/types/image.py` |

**Confirm cluster?** `____`

---
## Cluster B-FP-3: Utilities / Plumbing (4 findings)

**Proposed label: FP** — Utility modules, logging, graph path utilities,
runtime context plumbing. Infrastructure, not AI application logic.

| # | Project | File |
|---|---------|------|
| 2 | pydantic-ai | `pydantic_graph/pydantic_graph/beta/paths.py` |
| 33 | scikit-learn | `sklearn/experimental/enable_halving_search_cv.py` |
| 39 | openai-python | `src/openai/_utils/_logs.py` |
| 45 | pydantic-ai | `pydantic_ai_slim/pydantic_ai/_run_context.py` |

**Confirm cluster?** `____`

---
## Cluster B-FP-4: Other Clear FPs (2 findings)

| # | Tier | Project | File | Reasoning |
|---|------|---------|------|-----------|
| 7 | ai_security | langchain | `libs/partners/openai/tests/unit_tests/ch` | Temperature setting in a test file. Not a producti |
| 31 | high_risk | app_crewai | `lib/crewai-tools/src/crewai_tools/tools/` | Selenium web scraping tool in CrewAI toolkit. Matc |

**Confirm cluster?** `____`

---
## Cluster B-TP-1: Deepface Biometric Core (5 findings)

**Proposed label: TP** — Files from deepface and Frigate that directly
perform biometric identification or surveillance with person detection.

| # | Project | File | Category |
|---|---------|------|----------|
| 5 | app_frigate | `frigate/config/classification.py` | Annex III, Category 1 |
| 9 | app_deepface | `deepface/models/facial_recognition/VGGFace.py` | Annex III, Category 1 |
| 10 | app_deepface | `deepface/models/demography/Gender.py` | Annex III, Category 1 |
| 14 | app_deepface | `deepface/modules/verification.py` | Annex III, Category 1 |
| 23 | app_deepface | `deepface/modules/database/neo4j.py` | Annex III, Category 1 |
| 27 | app_deepface | `deepface/models/facial_recognition/FbDeepFace` | Annex III, Category 1 |
| 47 | app_frigate | `frigate/comms/embeddings_updater.py` | Annex III, Category 1 |

**Confirm cluster?** `____`

---
## Cluster B-TP-2: Genuine Security / Autonomy Findings (5 findings)

**Proposed label: TP** — Production code with genuine AI security risks
(unsafe deserialization, unvalidated AI output to commands) or agent autonomy
concerns (AI output → shell execution without gate).

| # | Tier | Project | File | Description |
|---|------|---------|------|-------------|
| 3 | ai_security | app_proctoring | `face_spoofing.py` | AI Security (LLM05) |
| 11 | agent_autonomy | app_aider | `aider/commands.py` | Agent Autonomy (OWASP Agentic ASI02 Tool Misuse /  |
| 18 | agent_autonomy | app_crewai | `lib/crewai-tools/src/crewai_tools/tools/` | Agent Autonomy (OWASP Agentic ASI02 Tool Misuse /  |
| 22 | agent_autonomy | app_crewai | `lib/crewai-tools/src/crewai_tools/tools/` | Agent Autonomy (OWASP Agentic ASI02 Tool Misuse /  |
| 36 | ai_security | app_monai | `monai/networks/nets/resnet.py` | AI Security (LLM05) |
| 49 | ai_security | app_crewai | `lib/crewai/src/crewai/utilities/file_han` | AI Security (LLM05) |

**Confirm cluster?** `____`

---
## Cluster B-TP-3: Eval / Report Logic (4 findings)

**Proposed label: TP** — Minimal-risk findings in code that contains
meaningful AI evaluation or reporting logic (not just infrastructure).

| # | Project | File |
|---|---------|------|
| 42 | pydantic-ai | `pydantic_evals/pydantic_evals/evaluators/report_ev` |

**Confirm cluster?** `____`
