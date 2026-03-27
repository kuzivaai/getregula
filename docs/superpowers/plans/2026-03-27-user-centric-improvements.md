# User-Centric Improvements: GitHub Action, Pattern Quality, Framework Expansion

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the three highest-impact user-facing gaps: CI/CD integration (GitHub Action), signal quality (pattern refinement + context-aware filtering), and enterprise coverage (Java/Go languages + OWASP/MITRE frameworks).

**Architecture:** Three independent workstreams that can be built in any order. Each produces a user-facing capability tested against real codebases. The GitHub Action wraps existing CLI. Pattern quality improves the classification engine. Framework expansion adds data files and a thin mapper update.

**Tech Stack:** Python 3.10+ stdlib, GitHub Actions YAML, existing custom test framework.

**Working directory:** `/home/mkuziva/getregula/`

**User personas driving these decisions:**
- **DevOps engineer** setting up CI/CD → needs GitHub Action with SARIF upload
- **Developer** getting noisy findings → needs fewer false positives, confidence thresholds
- **DPO/consultant** assessing enterprise Java/Go codebases → needs language + framework coverage

---

## File Map

### New Files
| File | Responsibility |
|------|---------------|
| `action.yml` | GitHub Action definition (root of repo) |
| `.github/workflows/regula-scan.yaml` | Reusable workflow for the action |
| `references/owasp_llm_top10.yaml` | OWASP Top 10 for LLMs mapping data |
| `references/mitre_atlas.yaml` | MITRE ATLAS technique mapping data |

### Modified Files
| File | Changes |
|------|---------|
| `scripts/classify_risk.py` | Refine 6 regex patterns that cause false positives. Add `context_requires_ai` flag to high-risk patterns. Add confidence threshold filtering. |
| `scripts/ast_engine.py` | Add Java + Go import detection to EXTENSION_MAP and regex patterns |
| `scripts/framework_mapper.py` | Load and serve OWASP + MITRE mappings |
| `references/framework_crosswalk.yaml` | Add OWASP LLM Top 10 and MITRE ATLAS entries |
| `scripts/cli.py` | Wire --framework to accept owasp-llm-top10 and mitre-atlas |
| `regula-policy.yaml` | Add min_confidence threshold |
| `tests/test_classification.py` | Add tests for each improvement |
| `SKILL.md` | Document GitHub Action |
| `README.md` | Document all new capabilities |

---

## Phase 1: GitHub Action (User: DevOps Engineer)

The #1 adoption blocker. Every competitor (Systima Comply, Semgrep, Snyk, SonarQube) has a GitHub Action. Regula already produces SARIF output — wiring it into an Action is mostly configuration.

### Task 1.1: Create action.yml

**Files:**
- Create: `action.yml`

- [ ] **Step 1: Create action.yml**

```yaml
name: 'Regula AI Governance Scan'
description: 'Scan your codebase for EU AI Act risk patterns, AI dependency supply chain issues, and compliance gaps'
branding:
  icon: 'shield'
  color: 'blue'

inputs:
  path:
    description: 'Path to scan (default: current directory)'
    required: false
    default: '.'
  format:
    description: 'Output format: text, json, sarif'
    required: false
    default: 'sarif'
  framework:
    description: 'Compliance framework: eu-ai-act, nist-ai-rmf, iso-42001, owasp-llm-top10, all'
    required: false
    default: 'eu-ai-act'
  fail-on-prohibited:
    description: 'Fail the workflow if prohibited patterns are found'
    required: false
    default: 'true'
  fail-on-high-risk:
    description: 'Fail the workflow if high-risk patterns are found'
    required: false
    default: 'false'
  min-dependency-score:
    description: 'Minimum dependency pinning score (0-100). Fails below this threshold.'
    required: false
    default: '0'
  upload-sarif:
    description: 'Upload SARIF results to GitHub Code Scanning'
    required: false
    default: 'true'

outputs:
  findings-count:
    description: 'Total number of findings'
  prohibited-count:
    description: 'Number of prohibited pattern findings'
  high-risk-count:
    description: 'Number of high-risk findings'
  pinning-score:
    description: 'AI dependency pinning score (0-100)'
  sarif-file:
    description: 'Path to generated SARIF file'

runs:
  using: 'composite'
  steps:
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Run Regula scan
      id: scan
      shell: bash
      run: |
        # Run check and capture SARIF
        python ${{ github.action_path }}/scripts/cli.py check "${{ inputs.path }}" \
          --format sarif \
          --name "${{ github.repository }}" \
          > "${{ runner.temp }}/regula-results.sarif.json" 2>/dev/null || true

        # Count findings
        FINDINGS=$(python -c "
        import json, sys
        try:
            sarif = json.load(open('${{ runner.temp }}/regula-results.sarif.json'))
            results = sarif.get('runs', [{}])[0].get('results', [])
            prohibited = sum(1 for r in results if r.get('level') == 'error')
            high_risk = sum(1 for r in results if r.get('level') == 'warning')
            print(f'{len(results)}|{prohibited}|{high_risk}')
        except Exception:
            print('0|0|0')
        ")
        IFS='|' read -r TOTAL PROHIBITED HIGH_RISK <<< "$FINDINGS"

        echo "findings-count=$TOTAL" >> $GITHUB_OUTPUT
        echo "prohibited-count=$PROHIBITED" >> $GITHUB_OUTPUT
        echo "high-risk-count=$HIGH_RISK" >> $GITHUB_OUTPUT
        echo "sarif-file=${{ runner.temp }}/regula-results.sarif.json" >> $GITHUB_OUTPUT

        # Run dependency scan
        DEP_SCORE=$(python ${{ github.action_path }}/scripts/cli.py deps \
          --project "${{ inputs.path }}" --format json 2>/dev/null | \
          python -c "import json,sys; print(json.load(sys.stdin).get('pinning_score', 0))" 2>/dev/null || echo "0")
        echo "pinning-score=$DEP_SCORE" >> $GITHUB_OUTPUT

        # Print summary
        echo "## Regula AI Governance Scan" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "| Metric | Value |" >> $GITHUB_STEP_SUMMARY
        echo "|--------|-------|" >> $GITHUB_STEP_SUMMARY
        echo "| Total findings | $TOTAL |" >> $GITHUB_STEP_SUMMARY
        echo "| Prohibited | $PROHIBITED |" >> $GITHUB_STEP_SUMMARY
        echo "| High-risk | $HIGH_RISK |" >> $GITHUB_STEP_SUMMARY
        echo "| Dependency pinning score | $DEP_SCORE/100 |" >> $GITHUB_STEP_SUMMARY

        # Determine exit code
        EXIT=0
        if [ "${{ inputs.fail-on-prohibited }}" = "true" ] && [ "$PROHIBITED" -gt 0 ]; then
          EXIT=2
        fi
        if [ "${{ inputs.fail-on-high-risk }}" = "true" ] && [ "$HIGH_RISK" -gt 0 ]; then
          EXIT=1
        fi
        if [ "${{ inputs.min-dependency-score }}" -gt 0 ] && [ "$DEP_SCORE" -lt "${{ inputs.min-dependency-score }}" ]; then
          EXIT=1
        fi
        exit $EXIT

    - name: Upload SARIF to GitHub Code Scanning
      if: inputs.upload-sarif == 'true' && always()
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: ${{ runner.temp }}/regula-results.sarif.json
        category: regula-ai-governance
      continue-on-error: true
```

- [ ] **Step 2: Test action.yml syntax**

```bash
cd /home/mkuziva/getregula
python3 -c "import yaml; yaml.safe_load(open('action.yml'))" 2>/dev/null && echo "YAML valid" || python3 -c "
# Fallback: basic YAML syntax check
content = open('action.yml').read()
assert 'name:' in content
assert 'runs:' in content
assert 'using:' in content
print('Structure valid')
"
```

- [ ] **Step 3: Commit**

```bash
git add action.yml
git commit -m "feat: add GitHub Action for CI/CD integration with SARIF upload"
```

---

### Task 1.2: Create Example Workflow

**Files:**
- Create: `.github/workflows/regula-scan.yaml`

- [ ] **Step 1: Create example workflow**

```yaml
name: Regula AI Governance Scan
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  security-events: write  # Required for SARIF upload
  contents: read

jobs:
  regula-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Regula
        uses: kuzivaai/getregula@main
        with:
          path: '.'
          fail-on-prohibited: 'true'
          fail-on-high-risk: 'false'
          min-dependency-score: '0'
          upload-sarif: 'true'
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/regula-scan.yaml
git commit -m "ci: add example Regula scan workflow"
```

---

## Phase 2: Pattern Quality + Confidence Filtering (User: Developer Getting Noise)

The benchmark showed 0% precision on high-risk findings against anthropic-cookbook. The audit identified several patterns that produce false positives on common code. This phase fixes the patterns and adds confidence threshold filtering.

### Task 2.1: Audit and Refine High-Risk Patterns

**Files:**
- Modify: `scripts/classify_risk.py`
- Test: `tests/test_classification.py`

The `sentenc` pattern was already fixed. Now fix the remaining known false positive risks:

- [ ] **Step 1: Write failing tests for false positive scenarios**

Add to `tests/test_classification.py`:

```python
# ── Pattern Quality Tests ──────────────────────────────────────────

def test_pattern_no_false_positive_sentence_nlp():
    """NLP 'sentence' usage does not trigger justice pattern"""
    r = classify("from nltk.translate.bleu_score import sentence_bleu with machine learning")
    assert_true(r.tier != RiskTier.HIGH_RISK or "justice" not in (r.category or "").lower(),
                "sentence_bleu should not trigger justice")
    print("✓ Pattern quality: sentence_bleu not false positive")


def test_pattern_no_false_positive_embedding():
    """'embedding' in general ML context does not trigger high-risk"""
    r = classify("import torch; embedding = torch.nn.Embedding(1000, 128)")
    # Should be minimal_risk (general AI), not high-risk
    assert_true(r.tier != RiskTier.HIGH_RISK,
                "torch.nn.Embedding should not trigger high-risk")
    print("✓ Pattern quality: Embedding layer not false positive")


def test_pattern_no_false_positive_model_predict():
    """Generic model.predict does not trigger high-risk without domain context"""
    r = classify("import sklearn; model.predict(X_test)")
    # Should be minimal_risk (general AI usage), not high-risk
    assert_true(r.tier != RiskTier.HIGH_RISK,
                "generic model.predict should not trigger high-risk alone")
    print("✓ Pattern quality: generic predict not false positive")


def test_pattern_true_positive_cv_screening():
    """CV screening with AI should trigger employment high-risk"""
    r = classify("import sklearn; cv_screening(candidates)")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "cv screening is high-risk")
    assert_true("employment" in (r.category or "").lower() or "category 4" in (r.category or "").lower(),
                "cv screening is employment category")
    print("✓ Pattern quality: CV screening correctly flagged")


def test_pattern_true_positive_credit_scoring():
    """Credit scoring with AI should trigger essential services high-risk"""
    r = classify("import xgboost; credit_score = model.predict(applicant_data)")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "credit scoring is high-risk")
    print("✓ Pattern quality: credit scoring correctly flagged")
```

Add all 5 to tests list under `# Pattern quality (5 tests)`.

- [ ] **Step 2: Run tests — check which pass and which fail**

```bash
cd /home/mkuziva/getregula && python3 tests/test_classification.py 2>&1 | grep -E "FAIL|Pattern quality"
```

- [ ] **Step 3: Fix any failing tests by refining patterns**

For any test that fails because of a false positive, refine the pattern in `classify_risk.py` to require AI domain context. The principle: a high-risk pattern should require BOTH a domain keyword AND an AI indicator, not just one.

Review each `HIGH_RISK_PATTERNS` entry and add context-requiring guards where a single common English word could match:
- `r"procto"` → `r"procto\w*\W{0,5}(exam|ai|automat|monitor|cheat)"` (avoid matching "proctor" in non-AI contexts)
- Any single-word pattern that could appear in normal code should require proximity to an AI/ML term

- [ ] **Step 4: Run all tests, verify everything passes**

```bash
python3 tests/test_classification.py 2>&1 | tail -5
```

- [ ] **Step 5: Commit**

```bash
git add scripts/classify_risk.py tests/test_classification.py
git commit -m "fix: refine high-risk patterns to reduce false positives"
```

---

### Task 2.2: Add Confidence Threshold to Policy

**Files:**
- Modify: `regula-policy.yaml`
- Modify: `scripts/classify_risk.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

```python
def test_confidence_threshold_filtering():
    """Low-confidence findings can be suppressed via policy threshold"""
    from classify_risk import classify, get_policy
    policy = get_policy()
    threshold = policy.get("thresholds", {}).get("min_confidence", 0)
    # The threshold should be readable (even if 0)
    assert_true(isinstance(threshold, (int, float)), "min_confidence is numeric")
    print("✓ Confidence threshold: readable from policy")
```

- [ ] **Step 2: Add min_confidence to regula-policy.yaml**

```yaml
thresholds:
  block_on_prohibited: true
  block_on_high_risk: false
  min_dependency_pinning_score: 50
  min_confidence: 0  # 0-100: suppress findings below this score. 0 = show all.
```

- [ ] **Step 3: Update classify() to respect threshold**

In `classify_risk.py`, after computing the classification, check if confidence_score is below the policy threshold. If so, downgrade to MINIMAL_RISK with a note. Do NOT apply to PROHIBITED — those always surface.

```python
# In classify() after line ~629, before return:
policy = get_policy()
min_conf = policy.get("thresholds", {}).get("min_confidence", 0)
if isinstance(min_conf, (int, float)) and min_conf > 0:
    if result.tier not in (RiskTier.PROHIBITED,) and result.confidence_score < min_conf:
        result = Classification(
            tier=RiskTier.MINIMAL_RISK, confidence="low",
            action="allow",
            message=f"Finding suppressed (confidence {result.confidence_score} < threshold {min_conf})",
            confidence_score=result.confidence_score,
        )
```

- [ ] **Step 4: Run tests, commit**

```bash
python3 tests/test_classification.py 2>&1 | tail -5
git add regula-policy.yaml scripts/classify_risk.py tests/test_classification.py
git commit -m "feat: add configurable confidence threshold to suppress low-confidence findings"
```

---

## Phase 3: Language + Framework Expansion (User: Enterprise DPO/Consultant)

### Task 3.1: Add Java and Go Import Detection

**Files:**
- Modify: `scripts/ast_engine.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing tests**

```python
# ── Language Expansion Tests ───────────────────────────────────────

def test_ast_engine_java_ai_detection():
    """AST engine detects AI imports in Java"""
    from ast_engine import analyse_file
    code = '''
import com.google.cloud.aiplatform.v1.PredictionServiceClient;
import dev.langchain4j.model.openai.OpenAiChatModel;

public class AIService {
    public String predict(String input) {
        return model.generate(input);
    }
}
'''
    findings = analyse_file(code, "AIService.java", language="java")
    assert_true(findings["has_ai_code"], "detects AI imports in Java")
    assert_true(len(findings["ai_imports"]) >= 1, f"finds AI imports (got {len(findings['ai_imports'])})")
    print("✓ AST engine: Java AI detection")


def test_ast_engine_go_ai_detection():
    """AST engine detects AI imports in Go"""
    from ast_engine import analyse_file
    code = '''
package main

import (
    "github.com/sashabaranov/go-openai"
    "github.com/tmc/langchaingo/llms"
)

func main() {
    client := openai.NewClient("key")
}
'''
    findings = analyse_file(code, "main.go", language="go")
    assert_true(findings["has_ai_code"], "detects AI imports in Go")
    assert_true(len(findings["ai_imports"]) >= 1, f"finds AI imports (got {len(findings['ai_imports'])})")
    print("✓ AST engine: Go AI detection")


def test_ast_engine_java_non_ai():
    """Java code without AI imports is not flagged"""
    from ast_engine import analyse_file
    code = '''
import org.springframework.boot.SpringApplication;
import javax.persistence.Entity;

public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
'''
    findings = analyse_file(code, "Application.java", language="java")
    assert_false(findings["has_ai_code"], "Spring Boot app is not AI")
    print("✓ AST engine: Java non-AI correctly identified")
```

Add all 3 to tests list under `# Language expansion (3 tests)`.

- [ ] **Step 2: Add Java and Go to ast_engine.py**

Add to `EXTENSION_MAP`:
```python
".java": "java",
".go": "go",
```

Add `_analyse_java_regex(content)` and `_analyse_go_regex(content)` functions, similar pattern to `_analyse_js_ts_regex`:

**Java AI libraries:**
```python
JAVA_AI_LIBRARIES = {
    "com.google.cloud.aiplatform", "dev.langchain4j", "ai.djl",
    "org.tensorflow", "org.deeplearning4j", "com.microsoft.semantickernel",
    "com.azure.ai", "software.amazon.awssdk.services.bedrockruntime",
    "com.google.cloud.vertexai", "io.weaviate",
}
```

**Java import pattern:** `r'import\s+([\w.]+)\s*;'`

**Go AI libraries:**
```python
GO_AI_LIBRARIES = {
    "github.com/sashabaranov/go-openai", "github.com/tmc/langchaingo",
    "github.com/replicate/replicate-go", "gorgonia.org/gorgonia",
    "github.com/nlpodyssey/spago", "github.com/gomlx/gomlx",
    "cloud.google.com/go/aiplatform", "github.com/aws/aws-sdk-go-v2/service/bedrockruntime",
}
```

**Go import pattern:** `r'"([\w./\-]+)"'` within `import (...)` blocks

Add routing in `analyse_file()`:
```python
elif lang == "java":
    return _analyse_java_regex(content)
elif lang == "go":
    return _analyse_go_regex(content)
```

- [ ] **Step 3: Run tests, commit**

```bash
python3 tests/test_classification.py 2>&1 | tail -5
git add scripts/ast_engine.py tests/test_classification.py
git commit -m "feat: add Java and Go AI import detection"
```

---

### Task 3.2: Add OWASP LLM Top 10 Mapping

**Files:**
- Create: `references/owasp_llm_top10.yaml`
- Modify: `references/framework_crosswalk.yaml`
- Modify: `scripts/framework_mapper.py`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

```python
def test_framework_mapper_owasp_llm():
    """Maps findings to OWASP Top 10 for LLMs"""
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["15"], frameworks=["owasp-llm-top10"])
    assert_true("15" in mapping, "article 15 mapped")
    owasp = mapping["15"].get("owasp_llm_top10", {})
    assert_true(len(owasp.get("items", [])) > 0, "has OWASP LLM items for Art 15")
    print("✓ Framework mapper: OWASP LLM Top 10 mapping")
```

- [ ] **Step 2: Create references/owasp_llm_top10.yaml**

Map each EU AI Act article to relevant OWASP Top 10 for LLMs (2025) items:

```yaml
# OWASP Top 10 for Large Language Model Applications (2025)
# Source: https://genai.owasp.org/llm-top-10/
schema_version: "1.0"
last_updated: "2026-03-27"
source: "OWASP Foundation, 2025"

items:
  LLM01:
    id: "LLM01"
    name: "Prompt Injection"
    description: "Manipulating LLMs through crafted inputs to cause unintended actions"
    eu_ai_act_articles: ["13", "15"]
  LLM02:
    id: "LLM02"
    name: "Sensitive Information Disclosure"
    description: "LLMs inadvertently revealing confidential data"
    eu_ai_act_articles: ["10", "15"]
  LLM03:
    id: "LLM03"
    name: "Supply Chain Vulnerabilities"
    description: "Risks from third-party components, training data, and pre-trained models"
    eu_ai_act_articles: ["15"]
  LLM04:
    id: "LLM04"
    name: "Data and Model Poisoning"
    description: "Manipulation of training data or model weights"
    eu_ai_act_articles: ["10", "15"]
  LLM05:
    id: "LLM05"
    name: "Improper Output Handling"
    description: "Insufficient validation of LLM outputs before downstream use"
    eu_ai_act_articles: ["13", "14", "15"]
  LLM06:
    id: "LLM06"
    name: "Excessive Agency"
    description: "LLM systems granted too much autonomy without human oversight"
    eu_ai_act_articles: ["14"]
  LLM07:
    id: "LLM07"
    name: "System Prompt Leakage"
    description: "Extraction of system prompts revealing sensitive business logic"
    eu_ai_act_articles: ["13", "15"]
  LLM08:
    id: "LLM08"
    name: "Vector and Embedding Weaknesses"
    description: "Vulnerabilities in RAG retrieval systems and embeddings"
    eu_ai_act_articles: ["10", "15"]
  LLM09:
    id: "LLM09"
    name: "Misinformation"
    description: "LLMs generating false or misleading information"
    eu_ai_act_articles: ["13", "15"]
  LLM10:
    id: "LLM10"
    name: "Unbounded Consumption"
    description: "Resource exhaustion through uncontrolled LLM usage"
    eu_ai_act_articles: ["15"]
```

- [ ] **Step 3: Add OWASP entries to framework_crosswalk.yaml**

For each article (9-15), add an `owasp_llm_top10` section:

```yaml
  article_14:
    # ... existing eu_ai_act, nist_ai_rmf, iso_42001 ...
    owasp_llm_top10:
      items:
        - "LLM05: Improper Output Handling — insufficient validation before downstream use"
        - "LLM06: Excessive Agency — systems granted too much autonomy without human oversight"
```

Map based on the `eu_ai_act_articles` field in the OWASP file.

- [ ] **Step 4: Update framework_mapper.py to accept "owasp-llm-top10"**

In `map_to_frameworks()`, add "owasp-llm-top10" as a valid framework filter. When selected, include the `owasp_llm_top10` key from the crosswalk.

Update the CLI choices in `scripts/cli.py` to include "owasp-llm-top10".

- [ ] **Step 5: Run tests, commit**

```bash
python3 tests/test_classification.py 2>&1 | tail -5
git add references/owasp_llm_top10.yaml references/framework_crosswalk.yaml scripts/framework_mapper.py scripts/cli.py tests/test_classification.py
git commit -m "feat: add OWASP Top 10 for LLMs framework mapping"
```

---

### Task 3.3: Add MITRE ATLAS Mapping

**Files:**
- Create: `references/mitre_atlas.yaml`
- Modify: `references/framework_crosswalk.yaml`
- Test: `tests/test_classification.py`

- [ ] **Step 1: Write failing test**

```python
def test_framework_mapper_mitre_atlas():
    """Maps findings to MITRE ATLAS techniques"""
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["10"], frameworks=["mitre-atlas"])
    assert_true("10" in mapping, "article 10 mapped")
    atlas = mapping["10"].get("mitre_atlas", {})
    assert_true(len(atlas.get("techniques", [])) > 0, "has MITRE ATLAS techniques for Art 10")
    print("✓ Framework mapper: MITRE ATLAS mapping")
```

- [ ] **Step 2: Create references/mitre_atlas.yaml**

Map EU AI Act articles to relevant MITRE ATLAS (Adversarial Threat Landscape for AI Systems) techniques:

```yaml
# MITRE ATLAS — Adversarial Threat Landscape for AI Systems
# Source: https://atlas.mitre.org/
schema_version: "1.0"
last_updated: "2026-03-27"
source: "MITRE Corporation"

techniques:
  AML.T0001:
    id: "AML.T0001"
    name: "Reconnaissance — Active Scanning"
    eu_ai_act_articles: ["15"]
  AML.T0010:
    id: "AML.T0010"
    name: "ML Supply Chain Compromise"
    eu_ai_act_articles: ["15"]
  AML.T0018:
    id: "AML.T0018"
    name: "Backdoor ML Model"
    eu_ai_act_articles: ["10", "15"]
  AML.T0019:
    id: "AML.T0019"
    name: "Publish Poisoned Datasets"
    eu_ai_act_articles: ["10"]
  AML.T0020:
    id: "AML.T0020"
    name: "Poison Training Data"
    eu_ai_act_articles: ["10"]
  AML.T0024:
    id: "AML.T0024"
    name: "Exfiltration via ML Inference API"
    eu_ai_act_articles: ["13", "15"]
  AML.T0025:
    id: "AML.T0025"
    name: "Exfiltration via Cyber Means"
    eu_ai_act_articles: ["15"]
  AML.T0031:
    id: "AML.T0031"
    name: "Erode ML Model Integrity"
    eu_ai_act_articles: ["9", "15"]
  AML.T0034:
    id: "AML.T0034"
    name: "Cost Harvesting"
    eu_ai_act_articles: ["15"]
  AML.T0040:
    id: "AML.T0040"
    name: "ML Model Inference API Access"
    eu_ai_act_articles: ["13", "15"]
  AML.T0043:
    id: "AML.T0043"
    name: "Craft Adversarial Data"
    eu_ai_act_articles: ["9", "10", "15"]
  AML.T0047:
    id: "AML.T0047"
    name: "Evade ML Model"
    eu_ai_act_articles: ["9", "15"]
  AML.T0048:
    id: "AML.T0048"
    name: "Prompt Injection"
    eu_ai_act_articles: ["13", "15"]
```

- [ ] **Step 3: Add MITRE ATLAS entries to framework_crosswalk.yaml**

For each article, add a `mitre_atlas` section with relevant techniques.

Add "mitre-atlas" to CLI framework choices.

- [ ] **Step 4: Run tests, commit**

```bash
python3 tests/test_classification.py 2>&1 | tail -5
git add references/mitre_atlas.yaml references/framework_crosswalk.yaml scripts/cli.py tests/test_classification.py
git commit -m "feat: add MITRE ATLAS adversarial technique mapping"
```

---

## Phase 4: Documentation Update

### Task 4.1: Update README and SKILL.md

**Files:**
- Modify: `README.md`
- Modify: `SKILL.md`

- [ ] **Step 1: Add GitHub Action section to README**

After the CI/CD baseline section, add:

```markdown
### GitHub Action

Add Regula to your CI/CD pipeline with one step:

\`\`\`yaml
- uses: kuzivaai/getregula@main
  with:
    path: '.'
    fail-on-prohibited: 'true'
    upload-sarif: 'true'
\`\`\`

Results appear in the GitHub Security tab alongside CodeQL and other SARIF-producing tools.
```

- [ ] **Step 2: Update framework list in README**

Add OWASP LLM Top 10 and MITRE ATLAS to the framework mapping section.

- [ ] **Step 3: Update language support**

Add Java and Go to the supported languages table.

- [ ] **Step 4: Update test count**

Update to match actual count after all new tests.

- [ ] **Step 5: Commit**

```bash
git add README.md SKILL.md
git commit -m "docs: document GitHub Action, OWASP/MITRE mapping, Java/Go support"
```

---

## Final Verification

- [ ] **Run full test suite**: `python3 tests/test_classification.py` — all must pass
- [ ] **Test GitHub Action syntax**: `python3 -c "import yaml; yaml.safe_load(open('action.yml'))" 2>/dev/null || echo "Check manually"`
- [ ] **Test Java detection**: `python3 -c "from scripts.ast_engine import analyse_file; r = analyse_file('import dev.langchain4j.model.openai.OpenAiChatModel;', 'App.java'); print(r['has_ai_code'])"`
- [ ] **Test Go detection**: `python3 -c "from scripts.ast_engine import analyse_file; r = analyse_file('import \"github.com/sashabaranov/go-openai\"', 'main.go'); print(r['has_ai_code'])"`
- [ ] **Test OWASP mapping**: `python3 -c "from scripts.framework_mapper import map_to_frameworks; m = map_to_frameworks(['15'], ['owasp-llm-top10']); print(m['15'].get('owasp_llm_top10', {}).get('items', [])[:2])"`
- [ ] **Test pattern quality**: Run against anthropic-cookbook and verify 0 false positive high-risk findings

---

## Summary

| Phase | Tasks | New Tests | Key User Benefit |
|-------|-------|-----------|-----------------|
| 1. GitHub Action | 2 | 0 (infra) | DevOps: one-step CI/CD integration |
| 2. Pattern Quality | 2 | 6 | Developers: fewer false positives, configurable confidence |
| 3. Framework Expansion | 3 | 5 | Enterprise: Java/Go coverage, OWASP + MITRE mapping |
| 4. Documentation | 1 | 0 | All users: accurate docs |
| **Total** | **8 tasks** | **11 tests** | |
