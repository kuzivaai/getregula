# Disagreement Dossier — Model vs Regula

**Provenance:** Model pre-label (Claude Opus 4.6, 15 June 2026). NOT a rater of record.
**Purpose:** Surfaces cases where the model disagrees with Regula's classification or flags ambiguity, so the human rater can adjudicate efficiently.
**Use:** Read each brief, decide tp/fp, record in the official label file. The model's call is a hypothesis, not a label.

**Total cases in this dossier:** 6 targeted + 14 blind subset = 20

---

# Part 1: Targeted Corpus Disagreements (6 cases)

## T-deepface-003

**File:** `deepface/commons/weight_utils.py`
**Repo:** deepface
**Category:** Annex III, Category 1

**Regula says:** high_risk — Annex III, Category 1 (biometric identification and categorisation)
**Model says:** FP

**Model reasoning:** BORDERLINE: Generic utility for downloading model weights / managing folders. While it serves the biometric system, the code itself is domain-agnostic (could be in any ML project). The file does not perform or specifically enable biometric identification — it downloads files. Leaning FP.

**Strongest argument for TP:** The file exists solely to serve deepface. Without it, the biometric system cannot load models. It is purpose-built infrastructure FOR biometric identification.

**Strongest argument for FP:** The code is a generic file-download utility. It downloads zip/bz2 files from URLs. Nothing in the code is biometric-specific. The same utility could serve any ML project.

**Single settling fact:** Read the function signatures. If every function is called exclusively by biometric modules (recognition, verification), it enables biometric identification. If the utility is also used by non-biometric modules (say, a generic ML loader), it's generic infrastructure.

**Your call:** `____` (tp / fp)

---

## T-deepface-018

**File:** `deepface/modules/database/milvus.py`
**Repo:** deepface
**Category:** Annex III, Category 1

**Regula says:** high_risk — Annex III, Category 1 (biometric identification and categorisation)
**Model says:** TP

**Model reasoning:** BORDERLINE: Database adapter for storing/querying biometric embeddings. Does not perform identification itself, but is purpose-built infrastructure that enables biometric identification at scale. Leaning TP because these modules exist solely to serve the biometric system — they are not general-purpose. A regulator would likely consider the embedding storage layer part of the biometric system.

**Strongest argument for TP:** This milvus adapter stores and queries biometric embeddings (face vectors). It is not a generic database client — it has deepface-specific schema, embedding dimensions, and search logic. A regulator reviewing the biometric system's data pipeline would include the embedding storage layer.

**Strongest argument for FP:** The adapter is a database connector. It stores vectors. Whether those vectors represent faces or product recommendations is determined by the caller, not by this file. The code itself contains no biometric logic.

**Single settling fact:** Check the import chain. If this module imports from `deepface.modules.modeling` or `deepface.models.FacialRecognition` (biometric-specific modules), it is coupled to the biometric system. If it only imports generic libraries (numpy, the database client), it is reusable plumbing.

**Your call:** `____` (tp / fp)

---

## T-deepface-019

**File:** `deepface/modules/database/neo4j.py`
**Repo:** deepface
**Category:** Annex III, Category 1

**Regula says:** high_risk — Annex III, Category 1 (biometric identification and categorisation)
**Model says:** TP

**Model reasoning:** BORDERLINE: Database adapter for storing/querying biometric embeddings. Does not perform identification itself, but is purpose-built infrastructure that enables biometric identification at scale. Leaning TP because these modules exist solely to serve the biometric system — they are not general-purpose. A regulator would likely consider the embedding storage layer part of the biometric system.

**Strongest argument for TP:** This neo4j adapter stores and queries biometric embeddings (face vectors). It is not a generic database client — it has deepface-specific schema, embedding dimensions, and search logic. A regulator reviewing the biometric system's data pipeline would include the embedding storage layer.

**Strongest argument for FP:** The adapter is a database connector. It stores vectors. Whether those vectors represent faces or product recommendations is determined by the caller, not by this file. The code itself contains no biometric logic.

**Single settling fact:** Check the import chain. If this module imports from `deepface.modules.modeling` or `deepface.models.FacialRecognition` (biometric-specific modules), it is coupled to the biometric system. If it only imports generic libraries (numpy, the database client), it is reusable plumbing.

**Your call:** `____` (tp / fp)

---

## T-deepface-020

**File:** `deepface/modules/database/pgvector.py`
**Repo:** deepface
**Category:** Annex III, Category 1

**Regula says:** high_risk — Annex III, Category 1 (biometric identification and categorisation)
**Model says:** TP

**Model reasoning:** BORDERLINE: Database adapter for storing/querying biometric embeddings. Does not perform identification itself, but is purpose-built infrastructure that enables biometric identification at scale. Leaning TP because these modules exist solely to serve the biometric system — they are not general-purpose. A regulator would likely consider the embedding storage layer part of the biometric system.

**Strongest argument for TP:** This pgvector adapter stores and queries biometric embeddings (face vectors). It is not a generic database client — it has deepface-specific schema, embedding dimensions, and search logic. A regulator reviewing the biometric system's data pipeline would include the embedding storage layer.

**Strongest argument for FP:** The adapter is a database connector. It stores vectors. Whether those vectors represent faces or product recommendations is determined by the caller, not by this file. The code itself contains no biometric logic.

**Single settling fact:** Check the import chain. If this module imports from `deepface.modules.modeling` or `deepface.models.FacialRecognition` (biometric-specific modules), it is coupled to the biometric system. If it only imports generic libraries (numpy, the database client), it is reusable plumbing.

**Your call:** `____` (tp / fp)

---

## T-deepface-021

**File:** `deepface/modules/database/pinecone.py`
**Repo:** deepface
**Category:** Annex III, Category 1

**Regula says:** high_risk — Annex III, Category 1 (biometric identification and categorisation)
**Model says:** TP

**Model reasoning:** BORDERLINE: Database adapter for storing/querying biometric embeddings. Does not perform identification itself, but is purpose-built infrastructure that enables biometric identification at scale. Leaning TP because these modules exist solely to serve the biometric system — they are not general-purpose. A regulator would likely consider the embedding storage layer part of the biometric system.

**Strongest argument for TP:** This pinecone adapter stores and queries biometric embeddings (face vectors). It is not a generic database client — it has deepface-specific schema, embedding dimensions, and search logic. A regulator reviewing the biometric system's data pipeline would include the embedding storage layer.

**Strongest argument for FP:** The adapter is a database connector. It stores vectors. Whether those vectors represent faces or product recommendations is determined by the caller, not by this file. The code itself contains no biometric logic.

**Single settling fact:** Check the import chain. If this module imports from `deepface.modules.modeling` or `deepface.models.FacialRecognition` (biometric-specific modules), it is coupled to the biometric system. If it only imports generic libraries (numpy, the database client), it is reusable plumbing.

**Your call:** `____` (tp / fp)

---

## T-deepface-022

**File:** `deepface/modules/database/weaviate.py`
**Repo:** deepface
**Category:** Annex III, Category 1

**Regula says:** high_risk — Annex III, Category 1 (biometric identification and categorisation)
**Model says:** TP

**Model reasoning:** BORDERLINE: Database adapter for storing/querying biometric embeddings. Does not perform identification itself, but is purpose-built infrastructure that enables biometric identification at scale. Leaning TP because these modules exist solely to serve the biometric system — they are not general-purpose. A regulator would likely consider the embedding storage layer part of the biometric system.

**Strongest argument for TP:** This weaviate adapter stores and queries biometric embeddings (face vectors). It is not a generic database client — it has deepface-specific schema, embedding dimensions, and search logic. A regulator reviewing the biometric system's data pipeline would include the embedding storage layer.

**Strongest argument for FP:** The adapter is a database connector. It stores vectors. Whether those vectors represent faces or product recommendations is determined by the caller, not by this file. The code itself contains no biometric logic.

**Single settling fact:** Check the import chain. If this module imports from `deepface.modules.modeling` or `deepface.models.FacialRecognition` (biometric-specific modules), it is coupled to the biometric system. If it only imports generic libraries (numpy, the database client), it is reusable plumbing.

**Your call:** `____` (tp / fp)

---

# Part 2: Blind Subset Disagreements (14 cases)

## Blind #4

**Project:** app_rasa
**File:** `tests/conftest.py`
**Tier:** credential_exposure
**Category:** AI Credential Governance (Article 15)

**Regula says:** credential_exposure — AI Credential Governance (Article 15)
**Model says:** FP

**Model reasoning:** BORDERLINE: Credential pattern in test conftest.py. Per LABELLING_CRITERIA: test code with credentials could be real secrets committed to tests, or test fixtures. Human must check whether this is a real private key or a test placeholder.

**Strongest argument for TP:** Test files sometimes contain real credentials committed by accident. A private key in conftest.py could be a genuine secret exposure, not a placeholder.

**Strongest argument for FP:** Test conftest files routinely contain fixture keys for mocking. Rasa is a well-maintained project; real secrets in tests would have been caught.

**Single settling fact:** Read the actual key value at line 524. If it starts with a realistic prefix (e.g. a PEM header) and is not obviously fake (`sk-test-xxx`), it may be real. Check git blame — if the key has been there since project inception, it's likely a fixture.

**Your call:** `____` (tp / fp)

---

## Blind #13

**Project:** app_crewai
**File:** `lib/crewai-tools/src/crewai_tools/tools/oxylabs_google_search_scraper_tool/oxylabs_google_search_scraper_tool.py`
**Tier:** agent_autonomy
**Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)

**Regula says:** agent_autonomy — Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
**Model says:** FP

**Model reasoning:** BORDERLINE: Regula detected a human gate pattern nearby, which suggests the autonomy concern is mitigated. But 'nearby' is approximate. Leaning FP given the gate detection, but human should verify the gate is actually in the execution path.

**Strongest argument for TP:** The tool executes HTTP requests based on AI-generated search queries. Even with a gate 'nearby,' the gate may not be in the actual execution path for this specific function.

**Strongest argument for FP:** Regula itself detected a human gate pattern nearby. If the gate wraps the tool invocation in the CrewAI agent loop, autonomy is mitigated.

**Single settling fact:** Is the 'human gate' in the call chain between the AI agent's output and this tool's `run()` method? Or is it elsewhere in the file?

**Your call:** `____` (tp / fp)

---

## Blind #16

**Project:** app_crewai
**File:** `lib/crewai-tools/src/crewai_tools/tools/singlestore_search_tool/singlestore_search_tool.py`
**Tier:** high_risk
**Category:** Annex III, Category 1

**Regula says:** high_risk — Annex III, Category 1
**Model says:** FP

**Model reasoning:** BORDERLINE: SingleStore search tool in CrewAI. Matched biometrics pattern but this is a generic vector search tool, not a biometric system. Low confidence (35). Leaning FP.

**Strongest argument for TP:** The tool might process biometric embeddings stored in SingleStore. Vector search is a common pattern for face matching.

**Strongest argument for FP:** SingleStore search tool is generic vector search — it searches any embeddings (product, text, image). The biometrics pattern triggered on vocabulary, not on actual biometric data processing. Confidence is low (35).

**Single settling fact:** Does the tool's schema or documentation mention biometric data, face embeddings, or identification? If not, it's generic vector search falsely flagged by keyword match.

**Your call:** `____` (tp / fp)

---

## Blind #17

**Project:** app_crewai
**File:** `lib/crewai/src/crewai/utilities/evaluators/crew_evaluator_handler.py`
**Tier:** high_risk
**Category:** Annex III, Category 4(b)

**Regula says:** high_risk — Annex III, Category 4(b)
**Model says:** FP

**Model reasoning:** BORDERLINE: CrewAI's 'crew evaluator handler' matched worker_management pattern, but CrewAI manages AI agents, not human workers. The 'crew' and 'task allocation' vocabulary triggered the pattern, but the system allocates tasks to software agents, not to employees. Leaning FP — a regulator would distinguish AI-agent orchestration from human-worker management.

**Strongest argument for TP:** The class literally evaluates and allocates tasks to 'crews' (teams). The vocabulary maps directly to worker management.

**Strongest argument for FP:** CrewAI 'crews' are AI agent teams, not human workers. Annex III Category 4 covers 'employment, workers management and access to self-employment' — meaning human workers. Managing software agents is not worker management under the Act.

**Single settling fact:** Does this code affect any natural person's employment, task allocation, or working conditions? If it only orchestrates AI agents (software), it's not Category 4.

**Your call:** `____` (tp / fp)

---

## Blind #19

**Project:** app_crewai
**File:** `lib/crewai-tools/src/crewai_tools/aws/bedrock/agents/invoke_agent_tool.py`
**Tier:** ai_security
**Category:** AI Security (LLM02)

**Regula says:** ai_security — AI Security (LLM02)
**Model says:** TP

**Model reasoning:** BORDERLINE: Sensitive data flow through AI agent. Depends on what data actually flows. High confidence (80) suggests the pattern is strong. Human should verify.

**Strongest argument for TP:** The tool invokes AWS Bedrock agents and passes data through. If any of that data includes PII or sensitive information, it flows to an external LLM without redaction — genuine LLM02 risk.

**Strongest argument for FP:** The tool is a generic Bedrock invocation wrapper. Whether sensitive data flows through it depends on how it's called, not on the tool itself.

**Single settling fact:** Does the `invoke_agent_tool.py` code pass user-provided content directly to the Bedrock API without any filtering? If yes, TP. If it only passes structured parameters, the risk is lower.

**Your call:** `____` (tp / fp)

---

## Blind #21

**Project:** app_crewai
**File:** `lib/crewai/tests/utilities/evaluators/test_crew_evaluator_handler.py`
**Tier:** high_risk
**Category:** Annex III, Category 4(b)

**Regula says:** high_risk — Annex III, Category 4(b)
**Model says:** FP

**Model reasoning:** BORDERLINE: CrewAI's 'crew evaluator handler' matched worker_management pattern, but CrewAI manages AI agents, not human workers. The 'crew' and 'task allocation' vocabulary triggered the pattern, but the system allocates tasks to software agents, not to employees. Leaning FP — a regulator would distinguish AI-agent orchestration from human-worker management.

**Strongest argument for TP:** The class literally evaluates and allocates tasks to 'crews' (teams). The vocabulary maps directly to worker management.

**Strongest argument for FP:** CrewAI 'crews' are AI agent teams, not human workers. Annex III Category 4 covers 'employment, workers management and access to self-employment' — meaning human workers. Managing software agents is not worker management under the Act.

**Single settling fact:** Does this code affect any natural person's employment, task allocation, or working conditions? If it only orchestrates AI agents (software), it's not Category 4.

**Your call:** `____` (tp / fp)

---

## Blind #24

**Project:** scikit-learn
**File:** `sklearn/datasets/_covtype.py`
**Tier:** minimal_risk

**Regula says:** minimal_risk — 
**Model says:** FP

**Model reasoning:** BORDERLINE: Dataset loader in scikit-learn. It loads data, which is a step in ML pipelines, but the file itself is a data-fetching utility, not inference/training logic.

**Strongest argument for TP:** Dataset loaders are part of ML pipelines. Loading data IS a step in AI/ML inference and training.

**Strongest argument for FP:** This is a data-fetching utility (downloads the Covertype dataset). It does not perform inference, training, or prediction. Per LABELLING_CRITERIA: 'code imports an AI library but only uses utility functions' is FP.

**Single settling fact:** Does this file contain any model fitting, prediction, or feature engineering? If it only fetches and caches a dataset, it's infrastructure.

**Your call:** `____` (tp / fp)

---

## Blind #26

**Project:** instructor
**File:** `instructor/providers/gemini/utils.py`
**Tier:** limited_risk

**Regula says:** limited_risk — 
**Model says:** TP

**Model reasoning:** BORDERLINE: Synthetic content generation detected. Depends on whether the output could be mistaken for human-created content. Provider utility code for Gemini — it connects to a model that generates content. Whether the specific integration constitutes limited-risk depends on the application using it. Human should decide.

**Strongest argument for TP:** Instructor + Gemini generates structured text outputs. If those outputs could be mistaken for human-written content, Article 50 transparency applies.

**Strongest argument for FP:** This is a provider utility file — it configures the Gemini client. The file itself doesn't generate content; it sets up the connection. The application using it determines whether synthetic content is produced.

**Single settling fact:** Does this file contain any content-generation call (e.g. `generate_content`, `chat.completions`)? Or is it purely client configuration?

**Your call:** `____` (tp / fp)

---

## Blind #32

**Project:** instructor
**File:** `examples/logfire-fastapi/server.py`
**Tier:** minimal_risk

**Regula says:** minimal_risk — 
**Model says:** TP

**Model reasoning:** BORDERLINE: Example/demo code. Per LABELLING_CRITERIA context rule 1: label based on what the code does. If it demonstrates real AI usage, it's TP. Human should check.

**Strongest argument for TP:** Example code that demonstrates real AI usage teaches users to build AI applications. Per LABELLING_CRITERIA context rule 1: 'label based on what the code does.'

**Strongest argument for FP:** It's an example server demonstrating observability (Logfire), not AI inference. If it only logs/traces and doesn't call an LLM itself, it's infrastructure.

**Single settling fact:** Does `server.py` make any LLM API call or model inference call? If yes, TP (it's a working AI application). If it only demonstrates logging setup, FP.

**Your call:** `____` (tp / fp)

---

## Blind #35

**Project:** app_crewai
**File:** `lib/crewai-tools/src/crewai_tools/tools/selenium_scraping_tool/selenium_scraping_tool.py`
**Tier:** agent_autonomy
**Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)

**Regula says:** agent_autonomy — Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
**Model says:** FP

**Model reasoning:** BORDERLINE: Regula detected a human gate pattern nearby, which suggests the autonomy concern is mitigated. But 'nearby' is approximate. Leaning FP given the gate detection, but human should verify the gate is actually in the execution path.

**Strongest argument for TP:** The selenium tool executes browser automation commands. If these flow from AI output, it's autonomous web interaction.

**Strongest argument for FP:** Regula detected a human gate nearby. Selenium scraping in CrewAI is typically wrapped in the agent execution loop which can have human-in-the-loop controls.

**Single settling fact:** Same as #13 — is the gate in the call chain?

**Your call:** `____` (tp / fp)

---

## Blind #37

**Project:** app_monai
**File:** `monai/networks/utils.py`
**Tier:** high_risk
**Category:** Annex III, Category 6

**Regula says:** high_risk — Annex III, Category 6
**Model says:** FP

**Model reasoning:** BORDERLINE: MONAI is a medical imaging framework. Flagged as law_enforcement (Category 6) likely due to domain keyword matching. MONAI's primary domain is healthcare, not law enforcement. However, healthcare IS an Annex III domain (Category 5 — access to essential services). The category assignment may be wrong even if the tier is right. Leaning FP for the stated category (law enforcement), but the file may be TP under a different category (healthcare). Human should adjudicate.

**Strongest argument for TP (different category):** MONAI IS medical imaging. Healthcare IS Annex III (Category 5 — access to essential services, or arguably Category 3 — education if used in medical training). The system may be high_risk, just miscategorised.

**Strongest argument for FP (stated category):** MONAI is flagged as 'law enforcement' (Category 6). It is categorically not law enforcement — it is medical imaging. The category is wrong. Even if the tier might be right under a different category, the STATED finding is incorrect.

**Single settling fact:** The question for labelling is: 'Does this code perform or enable the behaviour described in the finding's category?' The described category is law enforcement. MONAI does not perform law enforcement. FP for the stated finding, regardless of whether a different finding might be TP.

**Your call:** `____` (tp / fp)

---

## Blind #40

**Project:** pydantic-ai
**File:** `pydantic_ai_slim/pydantic_ai/providers/litellm.py`
**Tier:** minimal_risk

**Regula says:** minimal_risk — 
**Model says:** TP

**Model reasoning:** BORDERLINE: LLM provider integration. Contains connection logic to AI services. Arguably AI-related infrastructure. Human should decide if 'connecting to an LLM' counts as 'meaningful AI application logic.'

**Strongest argument for TP:** LiteLLM provider integration connects to AI models. This is functional AI-related code — it enables LLM inference.

**Strongest argument for FP:** It's a provider adapter (client configuration). It doesn't make decisions or generate content itself — it provides the transport layer.

**Single settling fact:** For minimal_risk, the test is 'does this file contain meaningful AI application logic?' Provider configuration that sets up model access is arguably 'meaningful AI logic' — it's the code that makes the AI system work. But pure client config (API key handling, endpoint URLs) is infrastructure. Check what the file actually does beyond configuration.

**Your call:** `____` (tp / fp)

---

## Blind #44

**Project:** app_crewai
**File:** `lib/crewai-tools/src/crewai_tools/tools/weaviate_tool/vector_search.py`
**Tier:** agent_autonomy
**Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)

**Regula says:** agent_autonomy — Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
**Model says:** FP

**Model reasoning:** BORDERLINE: Regula detected a human gate pattern nearby, which suggests the autonomy concern is mitigated. But 'nearby' is approximate. Leaning FP given the gate detection, but human should verify the gate is actually in the execution path.

**Strongest argument for TP:** The Weaviate vector search tool executes queries that could flow from AI agent decisions.

**Strongest argument for FP:** Gate pattern detected. And the Weaviate tool is a read operation (search), not a write/mutation — lower autonomy risk than HTTP mutations or system commands.

**Single settling fact:** Is the Weaviate query a read-only search, or does it modify data?

**Your call:** `____` (tp / fp)

---

## Blind #50

**Project:** pydantic-ai
**File:** `examples/pydantic_ai_examples/data_analyst.py`
**Tier:** minimal_risk

**Regula says:** minimal_risk — 
**Model says:** TP

**Model reasoning:** BORDERLINE: Example/demo code. Per LABELLING_CRITERIA context rule 1: label based on what the code does. If it demonstrates real AI usage, it's TP. Human should check.

**Strongest argument for TP:** This is example code that demonstrates a working AI data analyst. Per context rule 1: label based on what it does. If it makes LLM calls and processes data, it's meaningful AI application logic.

**Strongest argument for FP:** It's in `examples/` and may be a minimal demo, not production code. Minimal_risk only requires the code to be 'meaningful AI application logic' — a working example qualifies if it actually calls an LLM.

**Single settling fact:** Does the file call an LLM (e.g. pydantic-ai Agent, model.run())? If yes, TP — it's a working AI application. If it only defines schemas, FP.

**Your call:** `____` (tp / fp)

---
