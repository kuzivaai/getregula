# Blind Subset — Human Labelling Workbench

**Total findings:** 50

**Distribution:** minimal_risk 22, high_risk 12, agent_autonomy 9, ai_security 5, credential_exposure 1, limited_risk 1

**Instructions:** Copy `rater2_blind_subset.json` to `rater1_blind_subset.json`. For each finding, set `label` to `tp` or `fp`. Add `notes`. Do NOT consult `labels.json` — this must be independent.

**Tier-specific decision shortcut:**
- `minimal_risk` (22 entries): TP if the file contains meaningful AI/ML application logic. FP if it is pure infrastructure (config, routing, type definitions) that happens to be in an AI project.
- `high_risk` (12 entries): TP if the code performs/enables an Annex III activity. FP if the pattern matched but the code serves a different purpose.
- `agent_autonomy` (9 entries): TP if AI output flows to system commands/HTTP/file writes without a human gate. FP if the command execution is user-initiated or hardcoded.
- `ai_security` (5 entries): TP if genuine security risk (unsafe deserialization, unvalidated output, etc.). FP if test fixtures or secure patterns.
- `credential_exposure` (1 entry): TP if real credential. FP if test placeholder.
- `limited_risk` (1 entry): TP if synthetic content generation. FP if structured data output.

---

## Entry 1 / 50

- **Project:** langchain
- **File:** `libs/standard-tests/tests/unit_tests/test_decorated_tool.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 2 / 50

- **Project:** pydantic-ai
- **File:** `pydantic_graph/pydantic_graph/beta/paths.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 3 / 50

- **Project:** app_proctoring
- **File:** `face_spoofing.py`
- **Line:** 29
- **Tier:** ai_security
- **Category:** AI Security (LLM05)
- **Description:** Unsafe model deserialization — arbitrary code execution risk
- **Confidence:** 80
- **Indicators:** unsafe_deserialization

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 4 / 50

- **Project:** app_rasa
- **File:** `tests/conftest.py`
- **Line:** 524
- **Tier:** credential_exposure
- **Category:** AI Credential Governance (Article 15)
- **Description:** Private key detected in AI system code. Article 15 requires cybersecurity measures for high-risk systems. Fix: Never inc
- **Confidence:** 58
- **Indicators:** private_key
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 5 / 50

- **Project:** app_frigate
- **File:** `frigate/config/classification.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Description:** Biometric identification and categorisation
- **Confidence:** 88
- **Indicators:** biometrics

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 6 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/tests/rag/test_mdx_loader.py`
- **Line:** 24
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** AI output may flow to File system modification — no human gate detected
- **Confidence:** 30
- **Indicators:** File system modification
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 7 / 50

- **Project:** langchain
- **File:** `libs/partners/openai/tests/unit_tests/chat_models/test_responses_stream.py`
- **Line:** 62
- **Tier:** ai_security
- **Description:** High temperature setting — increased hallucination risk in production
- **Confidence:** 10
- **Indicators:** missing_temperature_control
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 8 / 50

- **Project:** openai-python
- **File:** `src/openai/types/beta/thread_create_and_run_params.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** NOTE: This may be a type definition or package init — check if it contains functional logic.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 9 / 50

- **Project:** app_deepface
- **File:** `deepface/models/facial_recognition/VGGFace.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Description:** Biometric identification and categorisation
- **Confidence:** n/a

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 10 / 50

- **Project:** app_deepface
- **File:** `deepface/models/demography/Gender.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Description:** Biometric identification and categorisation
- **Confidence:** n/a

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 11 / 50

- **Project:** app_aider
- **File:** `aider/commands.py`
- **Line:** 974
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** AI output may flow to System command execution — no human gate detected
- **Confidence:** 70
- **Indicators:** System command execution

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 12 / 50

- **Project:** scikit-learn
- **File:** `sklearn/utils/tests/test_optimize.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 13 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/src/crewai_tools/tools/oxylabs_google_search_scraper_tool/oxylabs_google_search_scraper_tool.py`
- **Line:** 132
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** Agent tool infrastructure: System command execution — human gate pattern detected nearby
- **Confidence:** 35
- **Indicators:** System command execution

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 14 / 50

- **Project:** app_deepface
- **File:** `deepface/modules/verification.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Description:** Biometric identification and categorisation
- **Confidence:** n/a

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 15 / 50

- **Project:** app_aider
- **File:** `tests/basic/test_linter.py`
- **Line:** 62
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** AI output may flow to System command execution — no human gate detected
- **Confidence:** 30
- **Indicators:** System command execution
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 16 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/src/crewai_tools/tools/singlestore_search_tool/singlestore_search_tool.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Description:** Biometric identification and categorisation
- **Confidence:** 35
- **Indicators:** biometrics

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 17 / 50

- **Project:** app_crewai
- **File:** `lib/crewai/src/crewai/utilities/evaluators/crew_evaluator_handler.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 4(b)
- **Description:** Worker monitoring and task allocation
- **Confidence:** 23
- **Indicators:** high_risk__worker_management

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 18 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/src/crewai_tools/tools/patronus_eval_tool/patronus_predefined_criteria_eval_tool.py`
- **Line:** 95
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** AI output may flow to HTTP mutation request — no human gate detected
- **Confidence:** 70
- **Indicators:** HTTP mutation request

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 19 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/src/crewai_tools/aws/bedrock/agents/invoke_agent_tool.py`
- **Line:** 172
- **Tier:** ai_security
- **Category:** AI Security (LLM02)
- **Description:** PII or sensitive data flows into or out of LLM without redaction — information disclosure risk
- **Confidence:** 80
- **Indicators:** sensitive_info_disclosure

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 20 / 50

- **Project:** scikit-learn
- **File:** `sklearn/datasets/__init__.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** NOTE: This may be a type definition or package init — check if it contains functional logic.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 21 / 50

- **Project:** app_crewai
- **File:** `lib/crewai/tests/utilities/evaluators/test_crew_evaluator_handler.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 4(b)
- **Description:** Worker monitoring and task allocation
- **Confidence:** 5
- **Indicators:** high_risk__worker_management
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 22 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/src/crewai_tools/tools/patronus_eval_tool/patronus_eval_tool.py`
- **Line:** 146
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** AI output may flow to HTTP mutation request — no human gate detected
- **Confidence:** 70
- **Indicators:** HTTP mutation request

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 23 / 50

- **Project:** app_deepface
- **File:** `deepface/modules/database/neo4j.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Description:** Biometric identification and categorisation
- **Confidence:** n/a

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 24 / 50

- **Project:** scikit-learn
- **File:** `sklearn/datasets/_covtype.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 25 / 50

- **Project:** openai-python
- **File:** `src/openai/types/evals/create_eval_completions_run_data_source_param.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** NOTE: This may be a type definition or package init — check if it contains functional logic.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 26 / 50

- **Project:** instructor
- **File:** `instructor/providers/gemini/utils.py`
- **Line:** 1
- **Tier:** limited_risk
- **Description:** Synthetic content generation
- **Confidence:** 53
- **Indicators:** synthetic_content

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 27 / 50

- **Project:** app_deepface
- **File:** `deepface/models/facial_recognition/FbDeepFace.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Description:** Biometric identification and categorisation
- **Confidence:** n/a

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 28 / 50

- **Project:** instructor
- **File:** `tests/test_logging.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 29 / 50

- **Project:** langchain
- **File:** `libs/langchain/langchain_classic/load/__init__.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** NOTE: This may be a type definition or package init — check if it contains functional logic.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 30 / 50

- **Project:** openai-python
- **File:** `src/openai/types/responses/response_input_image_param.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** NOTE: This may be a type definition or package init — check if it contains functional logic.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 31 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/src/crewai_tools/tools/selenium_scraping_tool/selenium_scraping_tool.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Safety Components
- **Description:** Safety components under Union harmonisation legislation
- **Confidence:** 23
- **Indicators:** safety_components

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 32 / 50

- **Project:** instructor
- **File:** `examples/logfire-fastapi/server.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** NOTE: This is example/demo code. Label based on what it does, not where it lives.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 33 / 50

- **Project:** scikit-learn
- **File:** `sklearn/experimental/enable_halving_search_cv.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 34 / 50

- **Project:** instructor
- **File:** `tests/test_message_processing.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 35 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/src/crewai_tools/tools/selenium_scraping_tool/selenium_scraping_tool.py`
- **Line:** 90
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** Agent tool infrastructure: System command execution — human gate pattern detected nearby
- **Confidence:** 35
- **Indicators:** System command execution

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 36 / 50

- **Project:** app_monai
- **File:** `monai/networks/nets/resnet.py`
- **Line:** 668
- **Tier:** ai_security
- **Category:** AI Security (LLM05)
- **Description:** Unsafe model deserialization — arbitrary code execution risk
- **Confidence:** 80
- **Indicators:** unsafe_deserialization

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 37 / 50

- **Project:** app_monai
- **File:** `monai/networks/utils.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 6
- **Description:** Law enforcement
- **Confidence:** 60
- **Indicators:** law_enforcement

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 38 / 50

- **Project:** pydantic-ai
- **File:** `tests/test_utils.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 39 / 50

- **Project:** openai-python
- **File:** `src/openai/_utils/_logs.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 40 / 50

- **Project:** pydantic-ai
- **File:** `pydantic_ai_slim/pydantic_ai/providers/litellm.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 41 / 50

- **Project:** openai-python
- **File:** `src/openai/types/image.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** NOTE: This may be a type definition or package init — check if it contains functional logic.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 42 / 50

- **Project:** pydantic-ai
- **File:** `pydantic_evals/pydantic_evals/evaluators/report_evaluator.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 43 / 50

- **Project:** pydantic-ai
- **File:** `tests/test_tools.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 44 / 50

- **Project:** app_crewai
- **File:** `lib/crewai-tools/src/crewai_tools/tools/weaviate_tool/vector_search.py`
- **Line:** 99
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** AI output may flow to System command execution — human gate pattern detected nearby
- **Confidence:** 45
- **Indicators:** System command execution

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 45 / 50

- **Project:** pydantic-ai
- **File:** `pydantic_ai_slim/pydantic_ai/_run_context.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 46 / 50

- **Project:** app_crewai
- **File:** `lib/crewai/tests/cli/tools/test_main.py`
- **Line:** 393
- **Tier:** agent_autonomy
- **Category:** Agent Autonomy (OWASP Agentic ASI02 Tool Misuse / ASI04 Missing Guardrails)
- **Description:** Agent tool infrastructure: System command execution — no human gate detected
- **Confidence:** 20
- **Indicators:** System command execution
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 47 / 50

- **Project:** app_frigate
- **File:** `frigate/comms/embeddings_updater.py`
- **Line:** 1
- **Tier:** high_risk
- **Category:** Annex III, Category 1
- **Description:** Biometric identification and categorisation
- **Confidence:** 73
- **Indicators:** biometrics

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 48 / 50

- **Project:** instructor
- **File:** `tests/dsl/test_simple_type_fix.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** ATTENTION: This is a test file.

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 49 / 50

- **Project:** app_crewai
- **File:** `lib/crewai/src/crewai/utilities/file_handler.py`
- **Line:** 180
- **Tier:** ai_security
- **Category:** AI Security (LLM05)
- **Description:** Unsafe model deserialization — arbitrary code execution risk
- **Confidence:** 80
- **Indicators:** unsafe_deserialization

**Your label:** `____` (tp / fp)
**Your notes:** 

---

## Entry 50 / 50

- **Project:** pydantic-ai
- **File:** `examples/pydantic_ai_examples/data_analyst.py`
- **Line:** 1
- **Tier:** minimal_risk
- **Description:** AI-related code with no specific risk indicators
- **Confidence:** 20
- **Workbench hint:** NOTE: This is example/demo code. Label based on what it does, not where it lives.

**Your label:** `____` (tp / fp)
**Your notes:** 

---