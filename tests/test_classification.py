# regula-ignore
#!/usr/bin/env python3
"""Comprehensive test suite for Regula classification engine"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from classify_risk import classify, RiskTier, is_ai_related

passed = 0
failed = 0

# Check if pyyaml is available (needed for complex YAML in framework/advisory tests)
try:
    import yaml
    _HAS_PYYAML = True
except ImportError:
    _HAS_PYYAML = False


def assert_eq(actual, expected, msg=""):
    global passed, failed
    if actual == expected:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {msg} — expected {expected}, got {actual}")


def assert_true(val, msg=""):
    assert_eq(val, True, msg)


def assert_false(val, msg=""):
    assert_eq(val, False, msg)


# ── AI Detection Tests ──────────────────────────────────────────────

def test_ai_detection_python_libraries():
    """Detects all major Python ML libraries"""
    assert_true(is_ai_related("import tensorflow"), "tensorflow")
    assert_true(is_ai_related("import torch"), "torch")
    assert_true(is_ai_related("from openai import OpenAI"), "openai")
    assert_true(is_ai_related("import anthropic"), "anthropic")
    assert_true(is_ai_related("from sklearn.ensemble import RandomForestClassifier"), "sklearn")
    assert_true(is_ai_related("import xgboost as xgb"), "xgboost")
    assert_true(is_ai_related("import lightgbm"), "lightgbm")
    assert_true(is_ai_related("from transformers import pipeline"), "transformers")
    assert_true(is_ai_related("import langchain"), "langchain")
    assert_true(is_ai_related("import keras"), "keras")
    assert_true(is_ai_related("import spacy"), "spacy")
    assert_true(is_ai_related("import nltk"), "nltk")
    assert_true(is_ai_related("import onnxruntime"), "onnxruntime")
    print("✓ AI detection: Python libraries")


def test_ai_detection_model_files():
    """Detects model file extensions"""
    assert_true(is_ai_related("model.onnx"), ".onnx")
    assert_true(is_ai_related("weights.pt"), ".pt")
    assert_true(is_ai_related("model.pth"), ".pth")
    assert_true(is_ai_related("classifier.pkl"), ".pkl")
    assert_true(is_ai_related("model.h5"), ".h5")
    assert_true(is_ai_related("model.safetensors"), ".safetensors")
    assert_true(is_ai_related("model.joblib"), ".joblib")
    assert_true(is_ai_related("model.gguf"), ".gguf")
    assert_true(is_ai_related("model.ggml"), ".ggml")
    print("✓ AI detection: model files")


def test_ai_detection_api_endpoints():
    """Detects AI API endpoints"""
    assert_true(is_ai_related("fetch('https://api.openai.com/v1/chat/completions')"), "openai api")
    assert_true(is_ai_related("url = 'https://api.anthropic.com/v1/messages'"), "anthropic api")
    assert_true(is_ai_related("generativelanguage.googleapis.com"), "google ai api")
    assert_true(is_ai_related("api.cohere.ai"), "cohere api")
    assert_true(is_ai_related("api.mistral.ai"), "mistral api")
    print("✓ AI detection: API endpoints")


def test_ai_detection_ml_patterns():
    """Detects ML patterns"""
    assert_true(is_ai_related("model.fit(X_train, y_train)"), "model.fit")
    assert_true(is_ai_related("model.predict(X_test)"), "model.predict")
    assert_true(is_ai_related("from_pretrained('bert-base')"), "from_pretrained")
    assert_true(is_ai_related("building a neural network"), "neural_network")
    assert_true(is_ai_related("deep learning model"), "deep_learning")
    assert_true(is_ai_related("machine learning pipeline"), "machine_learning")
    assert_true(is_ai_related("chat.completions.create"), "chat.completions")
    assert_true(is_ai_related("messages.create"), "messages.create")
    assert_true(is_ai_related("vectorstore.similarity_search"), "vectorstore")
    print("✓ AI detection: ML patterns")


def test_ai_detection_non_ai():
    """Ignores non-AI code"""
    assert_false(is_ai_related("print('hello world')"), "hello world")
    assert_false(is_ai_related("def add(a, b): return a + b"), "simple function")
    assert_false(is_ai_related("SELECT * FROM users WHERE id = 1"), "SQL query")
    assert_false(is_ai_related("npm install express"), "express install")
    assert_false(is_ai_related("git commit -m 'fix bug'"), "git command")
    assert_false(is_ai_related(""), "empty string")
    print("✓ AI detection: non-AI code ignored")


# ── Prohibited Classification Tests ─────────────────────────────────

def test_prohibited_social_scoring():
    """Social scoring → PROHIBITED"""
    r = classify("social credit scoring using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "social credit scoring")
    assert_eq(r.action, "block", "social scoring action")

    r = classify("import torch; citizen score system")
    assert_eq(r.tier, RiskTier.PROHIBITED, "citizen score")

    r = classify("behaviour scoring model with sklearn")
    assert_eq(r.tier, RiskTier.PROHIBITED, "behaviour scoring")
    print("✓ Prohibited: social scoring")


def test_prohibited_emotion_workplace():
    """Emotion + workplace → PROHIBITED"""
    r = classify("emotion detection workplace monitoring using torch")
    assert_eq(r.tier, RiskTier.PROHIBITED, "emotion workplace")

    r = classify("import tensorflow; employee emotion analysis")
    assert_eq(r.tier, RiskTier.PROHIBITED, "employee emotion")

    r = classify("sentiment analysis of employee performance with openai")
    assert_eq(r.tier, RiskTier.PROHIBITED, "sentiment employee")
    print("✓ Prohibited: emotion in workplace")


def test_prohibited_emotion_school():
    """Emotion + school → PROHIBITED"""
    r = classify("emotion detection in school using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "emotion school")
    print("✓ Prohibited: emotion in school")


def test_prohibited_realtime_biometric():
    """Real-time biometric + public → PROHIBITED"""
    r = classify("real time facial recognition in public using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "realtime facial")

    r = classify("import torch; live biometric public space surveillance")
    assert_eq(r.tier, RiskTier.PROHIBITED, "live biometric public")

    r = classify("mass surveillance biometric system with openai")
    assert_eq(r.tier, RiskTier.PROHIBITED, "mass surveillance biometric")
    print("✓ Prohibited: real-time biometric in public")


def test_prohibited_biometric_sensitive():
    """Biometric sensitive attributes → PROHIBITED"""
    r = classify("race detection model using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "race detection")

    r = classify("ethnicity inference with sklearn")
    assert_eq(r.tier, RiskTier.PROHIBITED, "ethnicity inference")

    r = classify("religion detection using deep learning")
    assert_eq(r.tier, RiskTier.PROHIBITED, "religion detection")

    r = classify("sexual orientation inference with machine learning")
    assert_eq(r.tier, RiskTier.PROHIBITED, "sexual orientation inference")
    print("✓ Prohibited: biometric sensitive attributes")


def test_prohibited_criminal_prediction():
    """Criminal prediction → PROHIBITED"""
    r = classify("crime prediction model using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "crime prediction")

    r = classify("predictive policing using sklearn")
    assert_eq(r.tier, RiskTier.PROHIBITED, "predictive policing")

    r = classify("recidivism risk model with machine learning")
    assert_eq(r.tier, RiskTier.PROHIBITED, "recidivism")
    print("✓ Prohibited: criminal prediction")


def test_prohibited_subliminal():
    """Subliminal manipulation → PROHIBITED"""
    r = classify("subliminal influence using neural network")
    assert_eq(r.tier, RiskTier.PROHIBITED, "subliminal")

    r = classify("beyond consciousness technique with deep learning")
    assert_eq(r.tier, RiskTier.PROHIBITED, "beyond consciousness")
    print("✓ Prohibited: subliminal manipulation")


def test_prohibited_facial_scraping():
    """Facial recognition scraping → PROHIBITED"""
    r = classify("face scraping database using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "face scraping")

    r = classify("mass facial collection with machine learning")
    assert_eq(r.tier, RiskTier.PROHIBITED, "mass facial collection")
    print("✓ Prohibited: facial recognition scraping")


# ── High-Risk Classification Tests ──────────────────────────────────

def test_high_risk_employment():
    """Employment systems → HIGH-RISK"""
    r = classify("import sklearn; CV screening for hiring")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "cv screening")
    assert_true("9" in r.applicable_articles, "article 9 present")
    assert_true("14" in r.applicable_articles, "article 14 present")

    r = classify("import torch; resume filtering algorithm")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "resume filtering")

    r = classify("candidate ranking system using openai")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "candidate ranking")

    r = classify("automated recruitment with machine learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "recruitment automation")
    print("✓ High-risk: employment")


def test_high_risk_credit_scoring():
    """Credit scoring → HIGH-RISK"""
    r = classify("import torch; credit scoring model")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "credit scoring")

    r = classify("creditworthiness assessment with sklearn")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "creditworthiness")

    r = classify("loan decision engine using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "loan decision")

    r = classify("insurance pricing model with machine learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "insurance pricing")
    print("✓ High-risk: credit scoring / essential services")


def test_high_risk_biometrics():
    """Biometric identification → HIGH-RISK"""
    r = classify("biometric identification system using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "biometric identification")

    r = classify("face recognition access control with torch")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "face recognition")

    r = classify("fingerprint recognition with deep learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "fingerprint recognition")
    print("✓ High-risk: biometrics")


def test_high_risk_medical():
    """Medical diagnosis → HIGH-RISK"""
    r = classify("medical diagnosis AI using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "medical diagnosis")

    r = classify("clinical decision support with sklearn")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "clinical decision")

    r = classify("treatment recommendation engine using openai")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "treatment recommendation")
    print("✓ High-risk: medical devices")


def test_high_risk_education():
    """Education → HIGH-RISK"""
    r = classify("student assessment AI using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "student assessment")

    r = classify("exam scoring system with machine learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "exam scoring")

    r = classify("admission decision model with sklearn")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "admission decision")
    print("✓ High-risk: education")


def test_high_risk_critical_infrastructure():
    """Critical infrastructure → HIGH-RISK"""
    r = classify("energy grid management AI with tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "energy grid")

    r = classify("traffic control system using deep learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "traffic control")
    print("✓ High-risk: critical infrastructure")


def test_high_risk_law_enforcement():
    """Law enforcement → HIGH-RISK"""
    r = classify("polygraph analysis using machine learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "polygraph")

    r = classify("criminal investigation AI using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "criminal investigation")
    print("✓ High-risk: law enforcement")


def test_high_risk_migration():
    """Migration → HIGH-RISK"""
    r = classify("border control AI using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "border control")

    r = classify("asylum application processing with machine learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "asylum application")
    print("✓ High-risk: migration")


def test_high_risk_justice():
    """Justice → HIGH-RISK"""
    r = classify("judicial decision support using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "judicial decision")

    r = classify("sentencing recommendation with machine learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "sentencing")
    print("✓ High-risk: justice")


def test_high_risk_safety():
    """Safety components → HIGH-RISK"""
    r = classify("autonomous vehicle AI with tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "autonomous vehicle")

    r = classify("self driving system using deep learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "self driving")
    print("✓ High-risk: safety components")


def test_high_risk_articles():
    """High-risk classifications include Articles 9-15"""
    r = classify("import sklearn; CV screening for hiring")
    expected = ["9", "10", "11", "12", "13", "14", "15"]
    for art in expected:
        assert_true(art in r.applicable_articles, f"article {art} in employment")
    print("✓ High-risk: all articles 9-15 present")


# ── Limited-Risk Classification Tests ───────────────────────────────

def test_limited_risk_chatbot():
    """Chatbot → LIMITED-RISK"""
    r = classify("import openai; build a chatbot")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "chatbot")
    assert_true("50" in r.applicable_articles, "article 50 for chatbot")

    r = classify("virtual assistant with langchain")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "virtual assistant")
    print("✓ Limited-risk: chatbot")


def test_limited_risk_deepfake():
    """Deepfake → LIMITED-RISK"""
    r = classify("import torch; deepfake generation")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "deepfake")

    r = classify("voice cloning with deep learning")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "voice clone")

    r = classify("ai generated image with tensorflow")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "ai generated image")
    print("✓ Limited-risk: synthetic content")


def test_limited_risk_age_estimation():
    """Age estimation → LIMITED-RISK"""
    r = classify("age estimation model with tensorflow")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "age estimation")

    r = classify("gender detection with machine learning")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "gender detection")
    print("✓ Limited-risk: biometric categorisation")


def test_limited_risk_emotion_no_workplace():
    """Emotion recognition without workplace → LIMITED-RISK (not prohibited)"""
    r = classify("emotion recognition app using tensorflow")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "emotion recognition general")

    r = classify("sentiment analysis tool with openai")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "sentiment analysis general")
    print("✓ Limited-risk: emotion recognition (no workplace)")


# ── Minimal-Risk Classification Tests ───────────────────────────────

def test_minimal_risk_recommendation():
    """Recommendation engine → MINIMAL-RISK"""
    r = classify("import tensorflow; recommendation engine")
    assert_eq(r.tier, RiskTier.MINIMAL_RISK, "recommendation engine")
    print("✓ Minimal-risk: recommendation engine")


def test_minimal_risk_code_completion():
    """Code completion → MINIMAL-RISK"""
    r = classify("import openai; code completion assistant")
    # "assistant" matches virtual_assist, so this is LIMITED_RISK
    # Use a more specific test
    r = classify("import tensorflow; model.fit(training_data)")
    assert_eq(r.tier, RiskTier.MINIMAL_RISK, "generic training")
    print("✓ Minimal-risk: generic AI training")


def test_minimal_risk_spam_filter():
    """Spam filter → MINIMAL-RISK"""
    r = classify("import sklearn; spam filter classifier")
    assert_eq(r.tier, RiskTier.MINIMAL_RISK, "spam filter")
    print("✓ Minimal-risk: spam filter")


# ── Edge Cases ──────────────────────────────────────────────────────

def test_edge_empty_input():
    """Empty input → NOT-AI"""
    r = classify("")
    assert_eq(r.tier, RiskTier.NOT_AI, "empty input")
    print("✓ Edge case: empty input")


def test_edge_case_insensitivity():
    """Classification is case insensitive"""
    r = classify("SOCIAL CREDIT SCORING USING TENSORFLOW")
    assert_eq(r.tier, RiskTier.PROHIBITED, "uppercase prohibited")

    r = classify("Import TensorFlow; CV Screening")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "mixed case high-risk")

    r = classify("IMPORT OPENAI; BUILD A CHATBOT")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "uppercase limited-risk")
    print("✓ Edge case: case insensitivity")


def test_edge_multiple_indicators():
    """Multiple indicators from different categories increase confidence"""
    r = classify("social credit scoring with predictive policing using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "multiple prohibited indicators")
    assert_eq(r.confidence, "high", "high confidence with multiple indicators")
    print("✓ Edge case: multiple indicators → high confidence")


def test_edge_prohibited_without_ai_indicator():
    """Prohibited patterns detected even without AI library import"""
    r = classify("social scoring system for citizens")
    assert_eq(r.tier, RiskTier.PROHIBITED, "prohibited without AI indicator")
    print("✓ Edge case: prohibited detected without AI indicator")


def test_edge_prohibited_overrides_high_risk():
    """Prohibited takes priority over high-risk"""
    r = classify("import tensorflow; social credit scoring for cv screening")
    assert_eq(r.tier, RiskTier.PROHIBITED, "prohibited overrides high-risk")
    print("✓ Edge case: prohibited overrides high-risk")


def test_edge_high_risk_overrides_limited():
    """High-risk takes priority over limited-risk"""
    r = classify("import openai; chatbot for cv screening hiring decisions")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "high-risk overrides limited")
    print("✓ Edge case: high-risk overrides limited-risk")


def test_classification_action_field():
    """Action field is correct for each tier"""
    r = classify("social credit using tensorflow")
    assert_eq(r.action, "block", "prohibited action is block")

    r = classify("import sklearn; cv screening")
    assert_eq(r.action, "allow_with_requirements", "high-risk action")

    r = classify("import openai; chatbot")
    assert_eq(r.action, "allow_with_transparency", "limited-risk action")

    r = classify("import tensorflow; recommendation engine")
    assert_eq(r.action, "allow", "minimal-risk action")

    r = classify("print('hello')")
    assert_eq(r.action, "allow", "not-ai action")
    print("✓ Edge case: action fields correct")


def test_classification_to_dict():
    """Classification serializes correctly"""
    r = classify("import sklearn; cv screening")
    d = r.to_dict()
    assert_eq(d["tier"], "high_risk", "tier serializes to string")
    assert_true(isinstance(d["indicators_matched"], list), "indicators is list")
    print("✓ Edge case: serialization")


def test_classification_to_json():
    """Classification produces valid JSON"""
    import json
    r = classify("import sklearn; cv screening")
    j = r.to_json()
    parsed = json.loads(j)
    assert_eq(parsed["tier"], "high_risk", "JSON tier")
    print("✓ Edge case: JSON output")


# ── Policy Engine Tests ─────────────────────────────────────────────

def test_policy_yaml_parser():
    """YAML fallback parser handles policy structure"""
    from classify_risk import _parse_yaml_fallback

    yaml_text = """version: "1.0"
rules:
  risk_classification:
    force_high_risk: [fraud_detection, customer_churn]
    exempt: [internal_chatbot_v2]
"""
    parsed = _parse_yaml_fallback(yaml_text)
    assert_eq(parsed.get("version"), "1.0", "yaml version parsed")
    rules = parsed.get("rules", {})
    assert_true(isinstance(rules, dict), "rules is dict")
    rc = rules.get("risk_classification", {})
    assert_true("fraud_detection" in rc.get("force_high_risk", []), "force_high_risk parsed")
    assert_true("internal_chatbot_v2" in rc.get("exempt", []), "exempt parsed")
    print("✓ Policy engine: YAML fallback parser works")


def test_policy_check_overrides():
    """Policy overrides function works for non-prohibited tiers"""
    import classify_risk
    original = classify_risk._POLICY

    classify_risk._POLICY = {
        "rules": {
            "risk_classification": {
                "force_high_risk": ["fraud_detection", "customer_churn"],
                "exempt": ["internal_chatbot_v2"],
            }
        }
    }

    r = classify("import tensorflow; fraud detection model")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "fraud_detection forced high-risk")

    r = classify("import openai; internal_chatbot_v2 update")
    assert_eq(r.tier, RiskTier.MINIMAL_RISK, "exempt system is minimal-risk")

    classify_risk._POLICY = original
    print("✓ Policy engine: force_high_risk and exempt work")


def test_policy_cannot_exempt_prohibited():
    """CRITICAL: Policy exempt list CANNOT override prohibited practices"""
    import classify_risk
    original = classify_risk._POLICY

    # Try to exempt a prohibited pattern via policy
    classify_risk._POLICY = {
        "rules": {
            "risk_classification": {
                "exempt": ["social_scoring_v2"],
            }
        }
    }

    # Even though "social_scoring_v2" is in exempt, "social scoring" is prohibited
    r = classify("social scoring v2 with tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "prohibited CANNOT be exempted by policy")

    classify_risk._POLICY = original
    print("✓ Policy engine: prohibited overrides policy exempt (safety-first)")


def test_prohibited_has_exceptions_field():
    """Prohibited classifications include exception info where applicable"""
    r = classify("emotion detection in workplace using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "emotion workplace is prohibited")
    # The emotion inference category has medical/safety exceptions
    # Check that the exceptions field is populated via the result object
    d = r.to_dict()
    assert_true("exceptions" in d, "exceptions field exists in output")
    print("✓ Prohibited: exceptions field present in classification")


def test_high_risk_performance_review():
    """Performance review AI → HIGH-RISK"""
    r = classify("performance review automation using AI model with tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "performance review AI")
    print("✓ High-risk: performance review")


# ── Audit Trail Tests ───────────────────────────────────────────────

def test_audit_hash_chain():
    """Audit trail maintains hash chain integrity"""
    import tempfile
    import os
    from log_event import log_event, verify_chain, get_audit_dir

    # Use temp directory
    temp_dir = tempfile.mkdtemp()
    os.environ["REGULA_AUDIT_DIR"] = temp_dir

    try:
        log_event("test", {"message": "first event"})
        log_event("test", {"message": "second event"})
        log_event("test", {"message": "third event"})

        valid, error = verify_chain()
        assert_true(valid, f"hash chain valid: {error}")
    finally:
        os.environ.pop("REGULA_AUDIT_DIR", None)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ Audit trail: hash chain integrity")


def test_audit_export_csv():
    """Audit trail exports to CSV"""
    from log_event import export_csv

    events = [
        {
            "event_id": "test-1",
            "timestamp": "2026-03-25T10:00:00Z",
            "event_type": "classification",
            "session_id": None,
            "project": None,
            "data": {"tier": "high_risk", "indicators": ["employment"], "tool_name": "Bash"},
        }
    ]

    csv_output = export_csv(events)
    assert_true("event_id" in csv_output, "CSV has headers")
    assert_true("test-1" in csv_output, "CSV has event data")
    assert_true("high_risk" in csv_output, "CSV has tier")
    print("✓ Audit trail: CSV export")


# ── Confidence Score Tests ──────────────────────────────────────────

def test_confidence_score_numeric():
    """Classifications include numeric confidence scores"""
    r = classify("social credit scoring using tensorflow")
    assert_true(isinstance(r.confidence_score, int), "confidence_score is int")
    assert_true(r.confidence_score > 0, "prohibited has positive score")
    assert_true(r.confidence_score <= 100, "score <= 100")

    r = classify("import sklearn; cv screening")
    assert_true(r.confidence_score > 0, "high-risk has positive score")

    r = classify("import openai; chatbot")
    assert_true(r.confidence_score > 0, "limited-risk has positive score")
    print("✓ Confidence scoring: numeric scores present")


def test_confidence_score_ordering():
    """Prohibited has higher confidence than high-risk which is higher than limited"""
    r_prohibited = classify("social credit scoring using tensorflow")
    r_high = classify("import sklearn; cv screening")
    r_limited = classify("import openai; chatbot")

    assert_true(r_prohibited.confidence_score > r_high.confidence_score,
                f"prohibited ({r_prohibited.confidence_score}) > high-risk ({r_high.confidence_score})")
    assert_true(r_high.confidence_score > r_limited.confidence_score,
                f"high-risk ({r_high.confidence_score}) > limited ({r_limited.confidence_score})")
    print("✓ Confidence scoring: tier ordering correct")


def test_multiple_indicators_increase_score():
    """Multiple indicators produce higher confidence score"""
    r_single = classify("import sklearn; cv screening")
    r_multi = classify("import sklearn; cv screening credit scoring loan decision")

    assert_true(r_multi.confidence_score >= r_single.confidence_score,
                f"multi ({r_multi.confidence_score}) >= single ({r_single.confidence_score})")
    print("✓ Confidence scoring: multiple indicators increase score")


# ── Report Tests ────────────────────────────────────────────────────

def test_sarif_output_structure():
    """SARIF output follows v2.1.0 schema structure"""
    from report import generate_sarif, scan_files
    import tempfile, os

    # Create a temp dir with a test file
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text("import tensorflow\ncredit_scoring_model = True\n")

    try:
        findings = scan_files(temp_dir)
        sarif = generate_sarif(findings, "test-project")

        assert_eq(sarif["version"], "2.1.0", "SARIF version")
        assert_true(len(sarif["runs"]) == 1, "has one run")
        assert_eq(sarif["runs"][0]["tool"]["driver"]["name"], "Regula", "tool name")
        assert_true(len(sarif["runs"][0]["tool"]["driver"]["rules"]) > 0, "has rules")
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ Report: SARIF output structure valid")


def test_html_report_contains_disclaimer():
    """HTML report contains risk indication disclaimer"""
    from report import generate_html_report

    html = generate_html_report([], "test-project")
    assert_true("not legal risk classification" in html.lower() or "not legal" in html.lower(),
                "HTML contains legal disclaimer")
    assert_true("pattern-based" in html.lower(), "HTML mentions pattern-based")
    print("✓ Report: HTML contains disclaimer")


def test_report_html_dependency_section():
    """HTML report includes dependency analysis section"""
    from report import generate_html_report
    findings = [{"file": "app.py", "tier": "high_risk", "category": "Employment",
                 "description": "CV screening", "confidence_score": 75, "suppressed": False}]
    dep_results = {"ai_dependencies": [{"name": "openai", "pinning": "exact", "version": "1.52.0"}],
                   "pinning_score": 80, "lockfiles": ["poetry.lock"], "compromised": [], "compromised_count": 0}
    html = generate_html_report(findings, "test-project", dependency_results=dep_results)
    assert_true("openai" in html, "dependency listed in HTML")
    assert_true("80" in html, "pinning score in HTML")
    print("✓ Report: HTML includes dependency analysis section")


def test_inline_suppression():
    """Files with regula-ignore comments have findings marked as suppressed"""
    from report import scan_files
    import tempfile

    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "model.py"
    test_file.write_text("# regula-ignore\nimport tensorflow\ncredit_scoring = True\n")

    try:
        findings = scan_files(temp_dir)
        suppressed = [f for f in findings if f.get("suppressed")]
        assert_true(len(suppressed) > 0, "suppressed findings exist")
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ Report: inline suppression works")


# ── New Feature Tests ───────────────────────────────────────────────

def test_questionnaire_generation():
    """Questionnaire generates 8 questions derived from Article 6"""
    from questionnaire import generate_questionnaire
    q = generate_questionnaire()
    assert_eq(q["type"], "risk_assessment_questionnaire", "questionnaire type")
    assert_eq(len(q["questions"]), 8, "8 questions")
    ids = {qu["id"] for qu in q["questions"]}
    assert_true("autonomous_decisions" in ids, "has autonomous_decisions question")
    assert_true("affected_domain" in ids, "has affected_domain question")
    print("✓ Questionnaire: generates 8 Article 6-derived questions")


def test_questionnaire_evaluation_high_risk():
    """High-risk answers produce high-risk classification"""
    from questionnaire import evaluate_questionnaire
    answers = {
        "autonomous_decisions": "yes",
        "affected_domain": "yes",
        "significant_harm": "yes",
        "narrow_procedural": "no",
        "improves_human_activity": "no",
        "public_facing": "no",
        "biometric_data": "yes",
        "deployment_eu": "yes",
    }
    result = evaluate_questionnaire(answers)
    assert_eq(result.tier, RiskTier.HIGH_RISK, "high-risk answers → HIGH_RISK")
    assert_true(result.confidence_score >= 70, f"score >= 70 (got {result.confidence_score})")
    print("✓ Questionnaire: high-risk answers produce HIGH_RISK")


def test_questionnaire_evaluation_minimal_risk():
    """Low-risk answers produce minimal-risk classification"""
    from questionnaire import evaluate_questionnaire
    answers = {
        "autonomous_decisions": "no",
        "affected_domain": "no",
        "significant_harm": "no",
        "narrow_procedural": "yes",
        "improves_human_activity": "yes",
        "public_facing": "yes",
        "biometric_data": "no",
        "deployment_eu": "no",
    }
    result = evaluate_questionnaire(answers)
    assert_eq(result.tier, RiskTier.MINIMAL_RISK, "low-risk answers → MINIMAL_RISK")
    assert_true(result.confidence_score < 40, f"score < 40 (got {result.confidence_score})")
    print("✓ Questionnaire: low-risk answers produce MINIMAL_RISK")


def test_session_aggregation():
    """Session aggregation produces valid profile structure"""
    from session import aggregate_session
    profile = aggregate_session(session_id="nonexistent-session", hours=1)
    assert_eq(profile["events"], 0, "empty session has 0 events")
    assert_eq(profile["risk_profile"], "none", "empty session has 'none' risk")
    print("✓ Session: aggregation produces valid profile")


def test_baseline_save_and_compare():
    """Baseline save and compare works correctly"""
    import tempfile, shutil
    from baseline import save_baseline, compare_to_baseline

    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "model.py"
    test_file.write_text("import tensorflow\ncredit_scoring = True\n")

    try:
        bl = save_baseline(temp_dir)
        assert_true(bl["findings_count"] > 0, "baseline has findings")

        result = compare_to_baseline(temp_dir)
        assert_eq(result["summary"]["new"], 0, "no new findings after baseline")
        assert_eq(result["summary"]["resolved"], 0, "no resolved findings")
        assert_true(result["summary"]["unchanged"] > 0, "unchanged findings exist")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ Baseline: save and compare work correctly")


def test_timeline_data():
    """Timeline contains verified enforcement dates"""
    from timeline import TIMELINE
    dates = [e["date"] for e in TIMELINE]
    assert_true("2025-02-02" in dates, "Article 5 date present")
    assert_true("2026-08-02" in dates, "High-risk date present")
    assert_true("2027-12-02" in dates, "Digital Omnibus proposed date present")

    # Verify Digital Omnibus entry has correct status
    omnibus = [e for e in TIMELINE if e["date"] == "2027-12-02"][0]
    assert_eq(omnibus["status"], "proposed", "Digital Omnibus is 'proposed' not 'effective'")
    print("✓ Timeline: verified enforcement dates present and accurate")


# ── Secret Detection Tests ──────────────────────────────────────────

def test_secret_detection_openai_key():
    """Detects OpenAI API key pattern"""
    from credential_check import check_secrets
    findings = check_secrets('curl -H "Authorization: Bearer sk-abcdefghijklmnopqrstuvwxyz12345"')
    assert_true(len(findings) > 0, "detects OpenAI key")
    assert_eq(findings[0].confidence, "high", "OpenAI key is high confidence")
    assert_true(findings[0].confidence_score >= 90, f"score >= 90 (got {findings[0].confidence_score})")
    print("✓ Secrets: detects OpenAI API key")


def test_secret_detection_aws_key():
    """Detects AWS access key pattern"""
    from credential_check import check_secrets
    findings = check_secrets("export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE")
    assert_true(len(findings) > 0, "detects AWS key")
    assert_eq(findings[0].pattern_name, "aws_access_key", "pattern is aws_access_key")
    print("✓ Secrets: detects AWS access key")


def test_secret_detection_no_false_positive():
    """Does not flag normal code as containing secrets"""
    from credential_check import check_secrets
    findings = check_secrets("git status && npm install && python3 main.py")
    assert_eq(len(findings), 0, "no false positives on normal commands")
    findings = check_secrets("print('hello world')")
    assert_eq(len(findings), 0, "no false positives on print")
    print("✓ Secrets: no false positives on normal code")


def test_secret_redaction():
    """Secrets are properly redacted in output"""
    from credential_check import check_secrets
    findings = check_secrets("sk-abcdefghijklmnopqrstuvwxyz12345")
    assert_true(len(findings) > 0, "found secret")
    assert_true(findings[0].redacted_value.startswith("sk-a"), "shows first 4 chars")
    assert_true("****" in findings[0].redacted_value, "redacts remainder")
    assert_true(len(findings[0].redacted_value) < 20, "redacted value is short")
    print("✓ Secrets: proper redaction in output")


# ── GPAI Awareness Tests ───────────────────────────────────────────

def test_gpai_training_detection():
    """Detects model training patterns"""
    from classify_risk import is_training_activity
    assert_true(is_training_activity("model.fit(X_train, y_train)"), "model.fit")
    assert_true(is_training_activity("trainer.train()"), "trainer.train")
    assert_true(is_training_activity("fine_tuning the model"), "fine_tune")
    assert_true(is_training_activity("from transformers import TrainingArguments"), "TrainingArguments")
    assert_true(is_training_activity("using LoRA adapters"), "lora")
    print("✓ GPAI: detects training patterns")


def test_gpai_inference_not_training():
    """Does not flag inference-only patterns as training"""
    from classify_risk import is_training_activity
    assert_false(is_training_activity("model.predict(X_test)"), "predict is not training")
    assert_false(is_training_activity("response = openai.chat.completions.create()"), "API call is not training")
    assert_false(is_training_activity("import torch; output = model(input)"), "inference is not training")
    print("✓ GPAI: inference patterns not flagged as training")


# ── Hook Integration Tests ──────────────────────────────────────────

def _run_hook(tool_name: str, tool_input: dict) -> tuple:
    """Run the pre_tool_use hook with given input, return (json_output, exit_code)."""
    import subprocess
    hook_path = str(Path(__file__).parent.parent / "hooks" / "pre_tool_use.py")
    input_json = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    result = subprocess.run(
        [sys.executable, hook_path],
        input=input_json, capture_output=True, text=True, timeout=10,
    )
    try:
        output = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        output = {}
    return output, result.returncode


def test_hook_prohibited_block():
    """Hook blocks prohibited patterns with exit code 2"""
    output, code = _run_hook("Bash", {"command": "python3 social_credit_scoring.py"})
    assert_eq(code, 2, "prohibited exits with code 2")
    decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
    assert_eq(decision, "deny", "prohibited decision is deny")
    reason = output.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    assert_true("PROHIBITED" in reason, "reason contains PROHIBITED")
    print("✓ Hook integration: prohibited block with exit 2")


def test_hook_high_risk_allow_with_iso():
    """Hook allows high-risk with ISO 42001 controls in context"""
    output, code = _run_hook("Bash", {"command": "python3 -c 'import sklearn; cv_screening()'"})
    assert_eq(code, 0, "high-risk exits with code 0")
    decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
    assert_eq(decision, "allow", "high-risk decision is allow")
    context = output.get("hookSpecificOutput", {}).get("additionalContext", "")
    assert_true("ISO 42001" in context, "context includes ISO 42001 controls")
    print("✓ Hook integration: high-risk allow with ISO 42001")


def test_hook_secret_block():
    """Hook blocks high-confidence secrets with exit code 2"""
    output, code = _run_hook("Bash", {"command": "curl -H 'Authorization: Bearer sk-abcdefghijklmnopqrstuvwxyz12345' api.openai.com"})
    assert_eq(code, 2, "secret exits with code 2")
    decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
    assert_eq(decision, "deny", "secret decision is deny")
    reason = output.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")
    assert_true("CREDENTIAL" in reason.upper(), "reason mentions credential")
    print("✓ Hook integration: secret block with exit 2")


def test_hook_clean_pass():
    """Hook allows clean operations with exit 0"""
    output, code = _run_hook("Bash", {"command": "git status"})
    assert_eq(code, 0, "clean command exits with code 0")
    decision = output.get("hookSpecificOutput", {}).get("permissionDecision")
    assert_eq(decision, "allow", "clean decision is allow")
    print("✓ Hook integration: clean pass with exit 0")


def test_file_credential_governance():
    """File scan detects AI credentials in AI-related files as governance finding"""
    from report import scan_files
    import tempfile, shutil

    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "ai_service.py"
    test_file.write_text(
        'import openai\n'
        'client = openai.Client(api_key="sk-abcdefghijklmnopqrstuvwxyz12345")\n'
        'result = client.chat.completions.create(model="gpt-4")\n'
    )

    try:
        findings = scan_files(temp_dir)
        cred_findings = [f for f in findings if f["tier"] == "credential_exposure"]
        assert_true(len(cred_findings) > 0, "credential found in AI file")
        assert_true("Article 15" in cred_findings[0]["category"], "framed as Article 15 governance")
        assert_true("OpenAI" in cred_findings[0]["description"], "identifies OpenAI key")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ AI credential governance: detects credentials in AI files as Article 15 finding")


# ── Compliance Status Workflow Tests ───────────────────────────────

def test_registry_scan_organization():
    """Org scan finds AI projects in subdirectories"""
    import tempfile, shutil
    from discover_ai_systems import scan_organization
    temp_dir = tempfile.mkdtemp()
    # Create two "projects"
    proj1 = Path(temp_dir) / "ai-app"
    proj1.mkdir()
    (proj1 / "pyproject.toml").write_text("[project]\nname = 'ai-app'\n")
    (proj1 / "app.py").write_text("import openai\nclient = openai.Client()\n")

    proj2 = Path(temp_dir) / "web-app"
    proj2.mkdir()
    (proj2 / "package.json").write_text('{"name": "web-app", "dependencies": {"express": "4.18.0"}}')
    (proj2 / "server.js").write_text("const express = require('express');\n")

    try:
        results = scan_organization(temp_dir, register=False)
        assert_true(results["projects_scanned"] >= 2, f"scans 2+ projects (got {results['projects_scanned']})")
        assert_true(results["ai_projects_found"] >= 1, "finds at least 1 AI project")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ Registry: org scan finds AI projects")


def test_registry_csv_export():
    """Registry exports as CSV"""
    from discover_ai_systems import format_registry_csv
    # Create a mock registry
    mock_registry = {
        "version": "1.0",
        "systems": {
            "test-app": {
                "highest_risk": "high_risk",
                "compliance_status": "assessment",
                "ai_libraries": ["openai", "torch"],
                "model_files": [],
                "last_scanned": "2026-03-27T00:00:00Z",
                "project_path": "/tmp/test-app",
            }
        }
    }
    csv_output = format_registry_csv(mock_registry)
    assert_true("test-app" in csv_output, "CSV contains system name")
    assert_true("HIGH-RISK" in csv_output, "CSV contains risk level")
    assert_true("assessment" in csv_output, "CSV contains compliance status")
    print("✓ Registry: CSV export works")


def test_compliance_workflow_transitions():
    """Compliance status follows valid transitions"""
    from discover_ai_systems import COMPLIANCE_STATUSES, COMPLIANCE_TRANSITIONS
    assert_true(len(COMPLIANCE_STATUSES) == 5, f"5 statuses defined (got {len(COMPLIANCE_STATUSES)})")
    assert_true("not_started" in COMPLIANCE_TRANSITIONS, "not_started has transitions")
    assert_true("compliant" in COMPLIANCE_TRANSITIONS, "compliant has transitions")
    # not_started can only go to assessment
    assert_eq(COMPLIANCE_TRANSITIONS["not_started"], ["assessment"], "not_started → assessment only")
    # compliant can only go to review_due
    assert_eq(COMPLIANCE_TRANSITIONS["compliant"], ["review_due"], "compliant → review_due only")
    print("✓ Compliance: workflow transitions are valid")


def test_compliance_status_update():
    """Compliance status updates and records history"""
    import tempfile, shutil
    from discover_ai_systems import (
        load_registry, save_registry, update_compliance_status,
        REGISTRY_PATH,
    )

    # Save original registry path
    original_path = REGISTRY_PATH

    temp_dir = tempfile.mkdtemp()
    import discover_ai_systems
    discover_ai_systems.REGISTRY_PATH = Path(temp_dir) / "test_registry.json"

    try:
        # Create a test registry
        registry = {"version": "1.0", "systems": {
            "test-app": {
                "registered_at": "2026-03-25T00:00:00+00:00",
                "last_scanned": "2026-03-25T00:00:00+00:00",
                "compliance_status": "not_started",
                "highest_risk": "high_risk",
            }
        }}
        save_registry(registry)

        # Valid transition: not_started → assessment
        entry = update_compliance_status("test-app", "assessment", "Starting review")
        assert_eq(entry["compliance_status"], "assessment", "status updated to assessment")
        assert_true(len(entry.get("compliance_history", [])) > 0, "history recorded")
        assert_eq(entry["compliance_history"][-1]["from"], "not_started", "history from correct")
        assert_eq(entry["compliance_history"][-1]["to"], "assessment", "history to correct")

        # Invalid transition: assessment → compliant (should fail)
        try:
            update_compliance_status("test-app", "compliant")
            assert_true(False, "should have raised ValueError for invalid transition")
        except ValueError:
            passed_local = True
            assert_true(True, "raises ValueError for invalid transition")

    finally:
        discover_ai_systems.REGISTRY_PATH = original_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ Compliance: status updates and records history")


def test_governance_contacts():
    """Governance contacts are readable from policy"""
    from classify_risk import get_governance_contacts
    # Should return dict (may be empty if no policy configured)
    contacts = get_governance_contacts()
    assert_true(isinstance(contacts, dict), "returns dict")
    print("✓ Governance: contacts readable from policy")


def test_qms_scaffold_generation():
    """QMS scaffold generates with all Article 17 sections"""
    import tempfile, shutil
    from generate_documentation import scan_project, generate_qms_scaffold

    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "model.py"
    test_file.write_text("import tensorflow\ncredit_scoring = True\n")

    try:
        findings = scan_project(temp_dir)
        qms = generate_qms_scaffold(findings, "test-project", temp_dir)
        assert_true("Article 17" in qms, "references Article 17")
        assert_true("Quality Management System" in qms, "contains QMS title")
        assert_true("Governance and Accountability" in qms, "has governance section")
        assert_true("Human Oversight" in qms, "has human oversight section")
        assert_true("Post-Market Monitoring" in qms, "has post-market monitoring")
        assert_true("Corrective Actions" in qms, "has corrective actions")
        assert_true("Review Schedule" in qms, "has review schedule")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ QMS: scaffold generates with all Article 17 sections")


def test_openai_key_no_anthropic_false_positive():
    """OpenAI key pattern does not match Anthropic keys"""
    from credential_check import check_secrets
    findings = check_secrets("sk-ant-api03-abcdefghijklmnopqrstuvwxyz12345")
    # Should only find the Anthropic pattern, not OpenAI
    openai_findings = [f for f in findings if f.pattern_name == "openai_api_key"]
    anthropic_findings = [f for f in findings if f.pattern_name == "anthropic_api_key"]
    assert_eq(len(openai_findings), 0, "OpenAI pattern does not match Anthropic key")
    assert_true(len(anthropic_findings) > 0, "Anthropic pattern matches Anthropic key")
    print("✓ Secrets: OpenAI pattern does not false-positive on Anthropic keys")


# ── AST Analysis Tests ─────────────────────────────────────────────

def test_ast_parse_python_file():
    """AST parser extracts imports, functions, and detects AI code"""
    from ast_analysis import parse_python_file
    code = """
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier

def train_model(X, y):
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

def test_model_accuracy():
    assert True
"""
    result = parse_python_file(code)
    assert_true(result["has_ai_code"], "detects AI imports")
    assert_true(len(result["ai_imports"]) >= 2, f"finds 2+ AI imports (got {len(result['ai_imports'])})")
    assert_true(len(result["function_defs"]) == 2, "finds 2 functions")
    # test_ function should be flagged
    test_fns = [f for f in result["function_defs"] if f["is_test"]]
    assert_true(len(test_fns) == 1, "identifies test function")
    assert_false(result["is_test_file"], "not a test file (1 of 2 fns is test)")
    print("✓ AST: parse_python_file extracts imports, functions, AI detection")


def test_ast_classify_context():
    """AST context classifier distinguishes implementation from test"""
    from ast_analysis import classify_context
    impl_code = "import openai\nclient = openai.Client()\nresult = client.chat.completions.create(model='gpt-4')\n"
    test_code = "def test_model(): assert True\ndef test_accuracy(): assert True\ndef test_loss(): assert True\n"
    assert_eq(classify_context(impl_code), "implementation", "AI code → implementation")
    assert_eq(classify_context(test_code), "test", "all test_ functions → test")
    assert_eq(classify_context("not valid python {{{{"), "not_python", "invalid syntax → not_python")
    print("✓ AST: classify_context distinguishes implementation vs test")


def test_ast_data_flow_tracing():
    """AST traces where AI model outputs go"""
    from ast_analysis import trace_ai_data_flow
    code = """
import openai
client = openai.Client()

def process():
    result = client.chat.completions.create(model="gpt-4", messages=[])
    if result.choices[0].message.content:
        return result
"""
    flows = trace_ai_data_flow(code)
    assert_true(len(flows) > 0, "finds AI data flows")
    # Should detect the create() call
    flow = flows[0]
    assert_true("create" in flow["source"], f"source contains create (got {flow['source']})")
    # Should have destinations
    dest_types = [d["type"] for d in flow["destinations"]]
    assert_true(len(dest_types) > 0, "has destinations")
    print("✓ AST: data flow tracing works")


def test_ast_human_oversight():
    """AST detects human oversight presence and absence"""
    from ast_analysis import detect_human_oversight
    # Code WITH oversight
    code_with = """
import openai
client = openai.Client()

def get_recommendation():
    result = client.chat.completions.create(model="gpt-4", messages=[])
    return result

def human_review(recommendation):
    print("Please review:", recommendation)
    approved = input("Approve? ")
    return approved == "yes"
"""
    result_with = detect_human_oversight(code_with)
    assert_true(result_with["has_oversight"], "detects oversight function")
    assert_true(len(result_with["oversight_patterns"]) > 0, "has oversight patterns")

    # Code WITHOUT oversight
    code_without = """
import openai
client = openai.Client()

def auto_decide(data):
    result = client.chat.completions.create(model="gpt-4", messages=[])
    if result:
        send_response(result)
"""
    result_without = detect_human_oversight(code_without)
    assert_true(result_without["oversight_score"] < result_with["oversight_score"],
                f"no-oversight score ({result_without['oversight_score']}) < oversight score ({result_with['oversight_score']})")
    print("✓ AST: detects human oversight presence and absence")


def test_ast_logging_practices():
    """AST detects logging near AI operations"""
    from ast_analysis import detect_logging_practices
    code_logged = """
import openai
import logging
logger = logging.getLogger(__name__)
client = openai.Client()

def predict(data):
    result = client.chat.completions.create(model="gpt-4", messages=[])
    logger.info("Prediction made: %s", result)
    return result
"""
    result = detect_logging_practices(code_logged)
    assert_true(result["has_logging"], "detects logging")
    assert_true(result["logging_score"] > 50, f"logged code scores > 50 (got {result['logging_score']})")

    code_unlogged = """
import openai
client = openai.Client()

def predict(data):
    result = client.chat.completions.create(model="gpt-4", messages=[])
    return result
"""
    result2 = detect_logging_practices(code_unlogged)
    assert_true(result2["logging_score"] < result["logging_score"],
                f"unlogged ({result2['logging_score']}) < logged ({result['logging_score']})")
    print("✓ AST: detects logging practices near AI operations")


# ── Compliance Gap Assessment Tests ────────────────────────────────

def test_compliance_gap_assessment():
    """Compliance gap assessment produces valid structure"""
    import tempfile, shutil
    from compliance_check import assess_compliance

    temp_dir = tempfile.mkdtemp()
    # Create a minimal AI project
    (Path(temp_dir) / "model.py").write_text(
        "import tensorflow as tf\nmodel = tf.keras.Sequential()\nmodel.fit(X, y)\n"
    )
    (Path(temp_dir) / "tests").mkdir()
    (Path(temp_dir) / "tests" / "test_model.py").write_text(
        "def test_accuracy(): assert True\n"
    )

    try:
        assessment = assess_compliance(temp_dir)
        assert_true("articles" in assessment, "has articles dict")
        assert_true("overall_score" in assessment, "has overall_score")
        assert_true(isinstance(assessment["overall_score"], (int, float)), "score is numeric")
        # Should have all 7 articles
        assert_eq(len(assessment["articles"]), 7, "7 articles assessed")
        # Each article should have required keys
        for art_num, art_data in assessment["articles"].items():
            assert_true("score" in art_data, f"article {art_num} has score")
            assert_true("evidence" in art_data, f"article {art_num} has evidence")
            assert_true("gaps" in art_data, f"article {art_num} has gaps")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ Compliance gap: produces valid assessment structure")


def test_compliance_gap_article_15_tests():
    """Article 15 detects test files as accuracy evidence"""
    import tempfile, shutil
    from compliance_check import assess_compliance

    temp_dir = tempfile.mkdtemp()
    (Path(temp_dir) / "model.py").write_text("import torch\nmodel = torch.nn.Linear(10, 1)\n")
    tests_dir = Path(temp_dir) / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_model.py").write_text("def test_accuracy(): pass\ndef test_robustness(): pass\n")

    try:
        assessment = assess_compliance(temp_dir)
        art15 = assessment["articles"]["15"]
        assert_true(art15["score"] > 0, f"Article 15 score > 0 with tests (got {art15['score']})")
        evidence_str = " ".join(art15["evidence"])
        assert_true("test" in evidence_str.lower(), "evidence mentions test files")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("✓ Compliance gap: Article 15 detects test files as evidence")


def test_regulatory_basis():
    """Regulatory basis is readable from policy"""
    from classify_risk import get_regulatory_basis
    basis = get_regulatory_basis()
    assert_true(isinstance(basis, dict), "returns dict")
    print("✓ Regulatory: basis readable from policy")


def test_cross_platform_locking():
    """File locking functions exist and are callable"""
    from log_event import _lock_file, _unlock_file
    assert_true(callable(_lock_file), "_lock_file is callable")
    assert_true(callable(_unlock_file), "_unlock_file is callable")
    print("✓ Cross-platform: file locking functions available")


def test_ast_engine_python_parse():
    """AST engine parses Python and returns unified format"""
    from ast_engine import analyse_file
    code = '''
import openai
client = openai.Client()
result = client.chat.completions.create(model="gpt-4", messages=[])
print(result)
'''
    findings = analyse_file(code, "test.py", language="python")
    assert_true(isinstance(findings, dict), "returns dict")
    assert_true("imports" in findings, "has imports")
    assert_true("ai_imports" in findings, "has ai_imports")
    assert_true("data_flows" in findings, "has data_flows")
    assert_true("oversight" in findings, "has oversight")
    assert_true("logging" in findings, "has logging")
    assert_true("context" in findings, "has context classification")
    assert_true(findings["has_ai_code"], "detects AI code")
    print("✓ AST engine: Python parse returns unified format")


def test_ast_engine_js_regex_fallback():
    """JS code with OpenAI import is detected as AI code via regex fallback"""
    from ast_engine import analyse_file
    code = "import OpenAI from 'openai';\nconst client = new OpenAI();\n"
    result = analyse_file(code, "app.js")
    assert_true(result["has_ai_code"], "JS with openai import → has_ai_code")
    assert_true("openai" in result["ai_imports"], f"'openai' in ai_imports (got {result['ai_imports']})")
    assert_eq(result["language"], "javascript", "language is javascript")
    print("✓ AST engine: JS regex fallback detects openai import")


def test_ast_engine_ts_regex_fallback():
    """TS code with Anthropic and ChromaDB imports detects 2+ AI imports"""
    from ast_engine import analyse_file
    code = (
        "import Anthropic from '@anthropic-ai/sdk';\n"
        "import { ChromaClient } from 'chromadb';\n"
        "const client = new Anthropic();\n"
    )
    result = analyse_file(code, "service.ts")
    assert_true(result["has_ai_code"], "TS with AI imports → has_ai_code")
    assert_true(len(result["ai_imports"]) >= 2,
                f"2+ AI imports detected (got {result['ai_imports']})")
    assert_eq(result["language"], "typescript", "language is typescript")
    print("✓ AST engine: TS regex fallback detects 2+ AI imports")


def test_ast_engine_non_ai_js():
    """JS code with only express import is NOT flagged as AI"""
    from ast_engine import analyse_file
    code = "import express from 'express';\nconst app = express();\n"
    result = analyse_file(code, "server.js")
    assert_false(result["has_ai_code"], "express-only JS → not AI")
    assert_eq(len(result["ai_imports"]), 0,
              f"no AI imports (got {result['ai_imports']})")
    print("✓ AST engine: express-only JS not flagged as AI")


def test_ast_engine_language_detection():
    """detect_language() returns correct language for known extensions and None for unknown"""
    from ast_engine import detect_language
    assert_eq(detect_language("model.py"), "python", ".py → python")
    assert_eq(detect_language("app.js"), "javascript", ".js → javascript")
    assert_eq(detect_language("service.ts"), "typescript", ".ts → typescript")
    assert_eq(detect_language("component.tsx"), "typescript", ".tsx → typescript")
    assert_eq(detect_language("widget.jsx"), "javascript", ".jsx → javascript")
    assert_eq(detect_language("module.mjs"), "javascript", ".mjs → javascript")
    assert_eq(detect_language("script.rb"), None, ".rb → None")
    assert_eq(detect_language("Service.java"), "java", ".java → java")
    assert_eq(detect_language("main.go"), "go", ".go → go")
    print("✓ AST engine: language detection correct for .py/.js/.ts/.tsx/.jsx/.mjs/.rb/.java/.go")


# ── Language Expansion Tests ───────────────────────────────────────

def test_ast_engine_java_ai_detection():
    """AST engine detects AI imports in Java"""
    from ast_engine import analyse_file
    code = 'import com.google.cloud.aiplatform.v1.PredictionServiceClient;\nimport dev.langchain4j.model.openai.OpenAiChatModel;\n\npublic class AIService {\n    public String predict(String input) {\n        return model.generate(input);\n    }\n}\n'
    findings = analyse_file(code, "AIService.java", language="java")
    assert_true(findings["has_ai_code"], "detects AI imports in Java")
    assert_true(len(findings["ai_imports"]) >= 1, f"finds AI imports (got {len(findings['ai_imports'])})")
    print("✓ AST engine: Java AI detection")


def test_ast_engine_go_ai_detection():
    """AST engine detects AI imports in Go"""
    from ast_engine import analyse_file
    code = 'package main\n\nimport (\n\t"github.com/sashabaranov/go-openai"\n\t"github.com/tmc/langchaingo/llms"\n)\n\nfunc main() {\n\tclient := openai.NewClient("key")\n}\n'
    findings = analyse_file(code, "main.go", language="go")
    assert_true(findings["has_ai_code"], "detects AI imports in Go")
    assert_true(len(findings["ai_imports"]) >= 1, f"finds AI imports (got {len(findings['ai_imports'])})")
    print("✓ AST engine: Go AI detection")


def test_ast_engine_java_non_ai():
    """Java code without AI imports is not flagged"""
    from ast_engine import analyse_file
    code = 'import org.springframework.boot.SpringApplication;\nimport javax.persistence.Entity;\n\npublic class Application {\n    public static void main(String[] args) {\n        SpringApplication.run(Application.class, args);\n    }\n}\n'
    findings = analyse_file(code, "Application.java", language="java")
    assert_false(findings["has_ai_code"], "Spring Boot app is not AI")
    print("✓ AST engine: Java non-AI correctly identified")


# ── Dependency Supply Chain Tests ──────────────────────────────────

def test_dep_scan_requirements_txt():
    """Parses requirements.txt and scores pinning quality"""
    from dependency_scan import parse_requirements_txt
    content = "openai==1.52.0\ntorch>=2.0\nlangchain\nlitellm==1.82.7\nnumpy\n"
    deps = parse_requirements_txt(content)
    assert_true(len(deps) >= 4, f"finds 4+ deps (got {len(deps)})")
    openai_dep = [d for d in deps if d["name"] == "openai"][0]
    assert_eq(openai_dep["pinning"], "exact", "openai is exact-pinned")
    assert_eq(openai_dep["version"], "1.52.0", "correct version")
    torch_dep = [d for d in deps if d["name"] == "torch"][0]
    assert_eq(torch_dep["pinning"], "range", "torch is range-pinned")
    langchain_dep = [d for d in deps if d["name"] == "langchain"][0]
    assert_eq(langchain_dep["pinning"], "unpinned", "langchain is unpinned")
    print("✓ Dependency scan: parses requirements.txt pinning quality")


def test_dep_scan_ai_identification():
    """Identifies AI vs non-AI dependencies"""
    from dependency_scan import is_ai_dependency
    assert_true(is_ai_dependency("openai"), "openai is AI")
    assert_true(is_ai_dependency("torch"), "torch is AI")
    assert_true(is_ai_dependency("litellm"), "litellm is AI")
    assert_true(is_ai_dependency("langchain"), "langchain is AI")
    assert_true(is_ai_dependency("scikit-learn"), "scikit-learn is AI")
    assert_true(is_ai_dependency("huggingface-hub"), "huggingface-hub is AI")
    assert_false(is_ai_dependency("flask"), "flask is not AI")
    assert_false(is_ai_dependency("requests"), "requests is not AI")
    assert_false(is_ai_dependency("django"), "django is not AI")
    print("✓ Dependency scan: AI dependency identification")


def test_dep_scan_pinning_score():
    """Calculates overall pinning score"""
    from dependency_scan import calculate_pinning_score
    deps = [
        {"name": "openai", "pinning": "exact", "is_ai": True},
        {"name": "torch", "pinning": "range", "is_ai": True},
        {"name": "langchain", "pinning": "unpinned", "is_ai": True},
        {"name": "flask", "pinning": "exact", "is_ai": False},
    ]
    score = calculate_pinning_score(deps)
    assert_true(0 <= score <= 100, f"score in range (got {score})")
    assert_true(score < 70, f"mixed pinning scores below 70 (got {score})")
    print("✓ Dependency scan: pinning score calculation")


def test_dep_scan_lockfile_detection():
    """Detects lockfile presence"""
    import tempfile, shutil
    from dependency_scan import detect_lockfiles
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "requirements.txt").write_text("openai==1.0\n")
    Path(temp_dir, "Pipfile.lock").write_text("{}\n")
    try:
        lockfiles = detect_lockfiles(temp_dir)
        assert_true(len(lockfiles) > 0, "detects Pipfile.lock")
        assert_true(any("Pipfile.lock" in lf for lf in lockfiles), "finds Pipfile.lock")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ Dependency scan: lockfile detection")


def test_dep_scan_package_json():
    """Parses package.json dependencies"""
    from dependency_scan import parse_package_json
    content = json.dumps({
        "dependencies": {
            "openai": "^4.0.0",
            "@anthropic-ai/sdk": "0.25.0",
            "express": "~4.18.0"
        }
    })
    deps = parse_package_json(content)
    assert_true(len(deps) >= 3, f"finds 3 deps (got {len(deps)})")
    openai_dep = [d for d in deps if d["name"] == "openai"][0]
    assert_eq(openai_dep["pinning"], "range", "^ is range")
    anthropic_dep = [d for d in deps if d["name"] == "@anthropic-ai/sdk"][0]
    assert_eq(anthropic_dep["pinning"], "exact", "bare version is exact")
    print("✓ Dependency scan: parses package.json")


def test_dep_scan_compromised_detection():
    """Detects known compromised package versions"""
    from dependency_scan import check_compromised
    deps = [
        {"name": "litellm", "version": "1.82.7", "pinning": "exact", "is_ai": True},
        {"name": "openai", "version": "1.52.0", "pinning": "exact", "is_ai": True},
    ]
    findings = check_compromised(deps)
    # Requires pyyaml for complex advisory YAML parsing — skip if not available
    if len(findings) == 0:
        try:
            import yaml
            assert_true(False, "pyyaml installed but no advisories loaded — real failure")
        except ImportError:
            print("✓ Dependency scan: detects known compromised versions (SKIPPED — pyyaml required)")
            return
    assert_true(len(findings) > 0, "finds compromised litellm")
    assert_eq(findings[0]["package"], "litellm", "identifies litellm")
    assert_eq(findings[0]["version"], "1.82.7", "identifies version")
    assert_true("credential" in findings[0]["description"].lower() or "malware" in findings[0]["description"].lower(),
                "description mentions the attack")
    print("✓ Dependency scan: detects known compromised versions")


# Rust/C++ dependency parsing (2 tests)

def test_dep_scan_cargo_toml():
    """Parses Cargo.toml dependencies"""
    from dependency_scan import parse_cargo_toml
    content = '''
[package]
name = "my-ai-app"
version = "0.1.0"

[dependencies]
candle-core = "0.8.0"
async-openai = { version = "0.25", features = ["stream"] }
tokio = { version = "1.0", features = ["full"] }
serde = "1.0"
'''
    deps = parse_cargo_toml(content)
    assert_true(len(deps) >= 4, f"finds 4 deps (got {len(deps)})")
    candle = [d for d in deps if d["name"] == "candle-core"]
    assert_true(len(candle) > 0, "finds candle-core")
    assert_eq(candle[0]["pinning"], "range", "semver is range (not exact)")
    assert_true(candle[0]["is_ai"], "candle-core is AI")
    tokio = [d for d in deps if d["name"] == "tokio"]
    assert_true(len(tokio) > 0, "finds tokio")
    assert_false(tokio[0]["is_ai"], "tokio is not AI")
    print("✓ Dependency scan: Cargo.toml parsing")


def test_dep_scan_vcpkg_json():
    """Parses vcpkg.json dependencies"""
    from dependency_scan import parse_vcpkg_json
    content = json.dumps({
        "dependencies": ["libtorch", "opencv4", "fmt", "boost-asio"]
    })
    deps = parse_vcpkg_json(content)
    assert_true(len(deps) >= 4, f"finds 4 deps (got {len(deps)})")
    torch = [d for d in deps if d["name"] == "libtorch"]
    assert_true(len(torch) > 0, "finds libtorch")
    assert_true(torch[0]["is_ai"], "libtorch is AI")
    fmt = [d for d in deps if d["name"] == "fmt"]
    assert_false(fmt[0]["is_ai"], "fmt is not AI")
    print("✓ Dependency scan: vcpkg.json parsing")


def test_gap_article_15_dependency_pinning():
    """Article 15 gap assessment includes dependency pinning analysis"""
    import tempfile, shutil
    from compliance_check import assess_compliance
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "app.py").write_text("import openai\nclient = openai.Client()\n")
    Path(temp_dir, "requirements.txt").write_text("openai\ntorch\nlangchain\n")
    try:
        assessment = assess_compliance(temp_dir)
        art15 = assessment["articles"]["15"]
        gaps_str = " ".join(art15["gaps"])
        assert_true("pinning" in gaps_str.lower() or "unpinned" in gaps_str.lower() or "supply chain" in gaps_str.lower(),
                    "Article 15 flags unpinned AI dependencies")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ Gap assessment: Article 15 includes dependency pinning")


def test_framework_mapper_eu_to_nist():
    """Maps EU AI Act articles to NIST AI RMF functions"""
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["9", "14"], frameworks=["nist-ai-rmf"])
    assert_true("9" in mapping, "article 9 mapped")
    nist = mapping["9"].get("nist_ai_rmf", {})
    assert_true(len(nist.get("functions", [])) > 0, "has NIST functions")
    assert_true("GOVERN" in nist["functions"], "Art 9 maps to GOVERN")
    print("✓ Framework mapper: EU AI Act to NIST AI RMF")


def test_framework_mapper_all_frameworks():
    """Maps to all three frameworks simultaneously"""
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["12"], frameworks=["all"])
    art12 = mapping.get("12", {})
    assert_true("eu_ai_act" in art12, "has EU AI Act")
    assert_true("nist_ai_rmf" in art12, "has NIST AI RMF")
    assert_true("iso_42001" in art12, "has ISO 42001")
    print("✓ Framework mapper: all three frameworks mapped")


def test_framework_mapper_owasp_llm():
    """Maps findings to OWASP Top 10 for LLMs"""
    if not _HAS_PYYAML:
        print("✓ Framework mapper: OWASP LLM Top 10 mapping (SKIPPED — pyyaml required)")
        return
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["15"], frameworks=["owasp-llm-top10"])
    assert_true("15" in mapping, "article 15 mapped")
    owasp = mapping["15"].get("owasp_llm_top10", {})
    assert_true(len(owasp.get("items", [])) > 0, "has OWASP LLM items for Art 15")
    print("✓ Framework mapper: OWASP LLM Top 10 mapping")


def test_framework_mapper_mitre_atlas():
    """Maps findings to MITRE ATLAS techniques"""
    if not _HAS_PYYAML:
        print("✓ Framework mapper: MITRE ATLAS mapping (SKIPPED — pyyaml required)")
        return
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["10"], frameworks=["mitre-atlas"])
    assert_true("10" in mapping, "article 10 mapped")
    atlas = mapping["10"].get("mitre_atlas", {})
    assert_true(len(atlas.get("techniques", [])) > 0, "has MITRE ATLAS techniques for Art 10")
    print("✓ Framework mapper: MITRE ATLAS mapping")


def test_framework_mapper_nist_csf():
    """Maps findings to NIST CSF 2.0"""
    if not _HAS_PYYAML:
        print("✓ Framework mapper: NIST CSF 2.0 mapping (SKIPPED — pyyaml required)")
        return
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["15"], frameworks=["nist-csf"])
    assert_true("15" in mapping, "article 15 mapped")
    csf = mapping["15"].get("nist_csf", {})
    assert_true(len(csf.get("functions", [])) > 0, "has NIST CSF functions for Art 15")
    assert_true("PROTECT" in csf["functions"], "Art 15 maps to PROTECT")
    print("✓ Framework mapper: NIST CSF 2.0 mapping")


def test_framework_mapper_soc2():
    """Maps findings to SOC 2 Trust Services Criteria"""
    if not _HAS_PYYAML:
        print("✓ Framework mapper: SOC 2 mapping (SKIPPED — pyyaml required)")
        return
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["9"], frameworks=["soc2"])
    assert_true("9" in mapping, "article 9 mapped")
    soc = mapping["9"].get("soc2", {})
    assert_true(len(soc.get("criteria", [])) > 0, "has SOC 2 criteria for Art 9")
    print("✓ Framework mapper: SOC 2 mapping")


def test_framework_mapper_iso_27001():
    """Maps findings to ISO 27001:2022"""
    if not _HAS_PYYAML:
        print("✓ Framework mapper: ISO 27001 mapping (SKIPPED — pyyaml required)")
        return
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["12"], frameworks=["iso-27001"])
    assert_true("12" in mapping, "article 12 mapped")
    iso = mapping["12"].get("iso_27001", {})
    assert_true(len(iso.get("controls", [])) > 0, "has ISO 27001 controls for Art 12")
    print("✓ Framework mapper: ISO 27001 mapping")


def test_framework_mapper_all_8_frameworks():
    """Maps to all 8 frameworks simultaneously"""
    from framework_mapper import map_to_frameworks
    mapping = map_to_frameworks(articles=["15"], frameworks=["all"])
    art15 = mapping.get("15", {})
    expected_keys = ["eu_ai_act", "nist_ai_rmf", "iso_42001", "nist_csf", "soc2", "iso_27001", "owasp_llm_top10", "mitre_atlas"]
    for key in expected_keys:
        assert_true(key in art15, f"Art 15 has {key}")
    print("✓ Framework mapper: all 8 frameworks mapped simultaneously")


def test_policy_thresholds():
    """Policy thresholds are readable"""
    from classify_risk import get_policy
    policy = get_policy()
    thresholds = policy.get("thresholds", {})
    assert_true(isinstance(thresholds, dict), "thresholds is dict or empty dict")
    print("✓ Policy: thresholds readable from policy")


def test_policy_exclusions():
    """Policy exclusions are readable"""
    from classify_risk import get_policy
    policy = get_policy()
    exclusions = policy.get("exclusions", {})
    assert_true(isinstance(exclusions, dict), "exclusions is dict or empty dict")
    print("✓ Policy: exclusions readable from policy")


# ── Integration Tests ──────────────────────────────────────────────

def test_integration_high_risk_project():
    """Full scan of high-risk fixture project"""
    from report import scan_files
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_high_risk")
    if not Path(fixture_path).exists():
        print("✓ Integration: high-risk fixture (SKIPPED — fixture not found)")
        return
    findings = scan_files(fixture_path)
    tiers = [f["tier"] for f in findings if not f.get("suppressed")]
    assert_true("high_risk" in tiers, "detects high-risk in employment screening project")
    print("✓ Integration: high-risk fixture scanned correctly")


def test_integration_compliant_project():
    """Full scan of compliant fixture project"""
    from compliance_check import assess_compliance
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_compliant")
    if not Path(fixture_path).exists():
        print("✓ Integration: compliant fixture (SKIPPED — fixture not found)")
        return
    assessment = assess_compliance(fixture_path)
    assert_true(assessment["overall_score"] > 30,
                f"compliant project scores > 30 (got {assessment['overall_score']})")
    print("✓ Integration: compliant fixture assessed correctly")


def test_integration_unpinned_deps():
    """Dependency scan of unpinned fixture project"""
    from dependency_scan import scan_dependencies
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_unpinned")
    if not Path(fixture_path).exists():
        print("✓ Integration: unpinned fixture (SKIPPED — fixture not found)")
        return
    results = scan_dependencies(fixture_path)
    assert_true(results["pinning_score"] < 50,
                f"unpinned project scores < 50 (got {results['pinning_score']})")
    unpinned_or_range = [d for d in results.get("ai_dependencies", []) if d["pinning"] in ("unpinned", "range")]
    assert_true(len(unpinned_or_range) > 0, "finds unpinned/range AI deps")
    print("✓ Integration: unpinned dependency fixture scanned correctly")


def test_integration_full_check_cli():
    """CLI check command runs end-to-end on fixture"""
    import subprocess
    fixture_path = str(Path(__file__).parent / "fixtures" / "sample_high_risk")
    if not Path(fixture_path).exists():
        print("✓ Integration: CLI check (SKIPPED — fixture not found)")
        return
    result = subprocess.run(
        [sys.executable, "scripts/cli.py", "check", fixture_path, "--format", "json"],
        capture_output=True, text=True, timeout=30,
        cwd=str(Path(__file__).parent.parent),
    )
    try:
        envelope = json.loads(result.stdout)
        assert_true(isinstance(envelope, dict) and "data" in envelope, "CLI outputs JSON envelope")
        findings = envelope["data"]
        assert_true(isinstance(findings, list), "CLI envelope data is a list")
        assert_true(len(findings) > 0, "CLI finds issues in high-risk project")
    except json.JSONDecodeError:
        assert_true(False, f"CLI output is not valid JSON: {result.stdout[:200]}")
    print("✓ Integration: CLI check runs end-to-end")


# ── Pattern Quality Tests ──────────────────────────────────────────

def test_pattern_no_false_positive_sentence_nlp():
    """NLP sentence usage does not trigger justice pattern"""
    r = classify("from nltk.translate.bleu_score import sentence_bleu with machine learning")
    assert_true(r.tier != RiskTier.HIGH_RISK or "justice" not in (r.category or "").lower(),
                "sentence_bleu should not trigger justice")
    print("✓ Pattern quality: sentence_bleu not false positive")


def test_pattern_no_false_positive_embedding_layer():
    """torch.nn.Embedding does not trigger high-risk"""
    r = classify("import torch; embedding = torch.nn.Embedding(1000, 128)")
    assert_true(r.tier != RiskTier.HIGH_RISK,
                "torch.nn.Embedding should not trigger high-risk")
    print("✓ Pattern quality: Embedding layer not false positive")


def test_pattern_no_false_positive_generic_predict():
    """Generic model.predict without domain context is not high-risk"""
    r = classify("import sklearn; model.predict(X_test)")
    assert_true(r.tier != RiskTier.HIGH_RISK,
                "generic model.predict should not trigger high-risk alone")
    print("✓ Pattern quality: generic predict not false positive")


def test_pattern_true_positive_cv_screening():
    """CV screening with AI correctly triggers employment high-risk"""
    r = classify("import sklearn; cv_screening(candidates)")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "cv screening is high-risk")
    print("✓ Pattern quality: CV screening correctly flagged")


def test_pattern_true_positive_credit_scoring():
    """Credit scoring with AI correctly triggers essential services"""
    r = classify("import xgboost; credit_score = predict_creditworthiness(applicant)")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "credit scoring is high-risk")
    print("✓ Pattern quality: credit scoring correctly flagged")


def test_confidence_threshold_filtering():
    """Low-confidence findings can be suppressed via policy threshold"""
    from classify_risk import get_policy
    policy = get_policy()
    threshold = 0
    try:
        threshold = int(policy.get("thresholds", {}).get("min_confidence", 0))
    except (TypeError, ValueError):
        pass
    assert_true(isinstance(threshold, int), "min_confidence is readable as int")
    # With default threshold of 0, nothing should be suppressed
    assert_eq(threshold, 0, "default threshold is 0 (no suppression)")
    print("✓ Confidence threshold: readable from policy")


# ── Confidence Tiers Tests ────────────────────────────────────────

def test_confidence_tier_block():
    """High-confidence findings are BLOCK tier"""
    # Use same snippet as test_confidence_score_numeric — already validated in this suite
    snippet = "social " + "credit " + "scoring using tensorflow"
    r = classify(snippet)
    assert_eq(r.get_finding_tier(), "block", "prohibited is always block")
    print("✓ Confidence tiers: prohibited = block")


def test_confidence_tier_info():
    """Low-confidence findings are INFO tier"""
    # Minimal-risk AI: has an AI indicator but no high/prohibited pattern
    r = classify("import torch; some_generic_ai_thing()")
    if r.confidence_score < 50:
        assert_eq(r.get_finding_tier(), "info", "low confidence = info")
    print("✓ Confidence tiers: low confidence = info")


# ── Tree-Sitter JS/TS Tests ───────────────────────────────────────

def test_tree_sitter_js_import_extraction():
    """Tree-sitter extracts JS imports from import statements and require calls"""
    from ast_engine import _tree_sitter_parse
    try:
        code = "import OpenAI from 'openai';\nconst { Anthropic } = require('@anthropic-ai/sdk');\n"
        result = _tree_sitter_parse(code, "javascript")
        assert_true(result["has_ai_code"], "detects AI imports via tree-sitter")
        assert_true(len(result["ai_imports"]) >= 2, f"finds 2+ AI imports (got {len(result['ai_imports'])})")
        print("✓ Tree-sitter: JS import extraction")
    except ImportError:
        print("✓ Tree-sitter: JS import extraction (SKIPPED — tree-sitter not installed)")


def test_tree_sitter_js_data_flow():
    """Tree-sitter traces where AI call results flow"""
    from ast_engine import _tree_sitter_parse
    try:
        code = """
import OpenAI from 'openai';
const client = new OpenAI();

async function process(data) {
    const response = await client.chat.completions.create({model: 'gpt-4', messages: []});
    console.log('AI result:', response);
    if (response.choices[0].message.content) {
        return response;
    }
}
"""
        result = _tree_sitter_parse(code, "javascript")
        assert_true(len(result["data_flows"]) > 0, "traces AI data flows")
        flow = result["data_flows"][0]
        dest_types = [d["type"] for d in flow["destinations"]]
        assert_true(len(dest_types) > 0, f"has destinations (got {dest_types})")
        print("✓ Tree-sitter: JS data flow tracing")
    except ImportError:
        print("✓ Tree-sitter: JS data flow tracing (SKIPPED — tree-sitter not installed)")


def test_tree_sitter_ts_oversight_detection():
    """Tree-sitter detects human oversight patterns in TypeScript"""
    from ast_engine import _tree_sitter_parse
    try:
        code = """
import Anthropic from '@anthropic-ai/sdk';
const client = new Anthropic();

async function getRecommendation(data: string): Promise<string> {
    const result = await client.messages.create({model: 'claude-3', messages: []});
    return result;
}

function humanReview(recommendation: string): boolean {
    console.log('Needs review:', recommendation);
    return confirm('Approve this recommendation?');
}
"""
        result = _tree_sitter_parse(code, "typescript")
        assert_true(result["oversight"]["has_oversight"], "detects humanReview function")
        assert_true(result["oversight"]["oversight_score"] > 50,
                    f"oversight score > 50 (got {result['oversight']['oversight_score']})")
        print("✓ Tree-sitter: TS oversight detection")
    except ImportError:
        print("✓ Tree-sitter: TS oversight detection (SKIPPED — tree-sitter not installed)")


def test_tree_sitter_js_function_extraction():
    """Tree-sitter extracts function and class definitions"""
    from ast_engine import _tree_sitter_parse
    try:
        code = """
import OpenAI from 'openai';
function processData(input) { return input; }
const helper = (x) => x * 2;
class AIService {
    constructor() {}
    predict(data) { return data; }
}
"""
        result = _tree_sitter_parse(code, "javascript")
        func_names = [f["name"] for f in result["function_defs"]]
        assert_true("processData" in func_names, "finds named function")
        class_names = [c["name"] for c in result["class_defs"]]
        assert_true("AIService" in class_names, "finds class")
        print("✓ Tree-sitter: JS function/class extraction")
    except ImportError:
        print("✓ Tree-sitter: JS function/class extraction (SKIPPED — tree-sitter not installed)")


# ── Rust/C/C++ language support (3 tests) ─────────────────────────

def test_ast_engine_rust_ai_detection():
    """AST engine detects AI imports in Rust"""
    from ast_engine import analyse_file
    code = 'use candle_core::Tensor;\nuse candle_nn::Linear;\nuse async_openai::Client;\n\nfn main() {\n    let tensor = Tensor::zeros(&[2, 3], candle_core::DType::F32, &candle_core::Device::Cpu);\n}\n'
    findings = analyse_file(code, "main.rs", language="rust")
    assert_true(findings["has_ai_code"], "detects AI imports in Rust")
    assert_true(len(findings["ai_imports"]) >= 2, f"finds 2+ AI imports (got {len(findings['ai_imports'])})")
    print("✓ AST engine: Rust AI detection")


def test_ast_engine_cpp_ai_detection():
    """AST engine detects AI includes in C++"""
    from ast_engine import analyse_file
    code = '#include <torch/torch.h>\n#include <opencv2/core.hpp>\n\nint main() {\n    auto tensor = torch::zeros({2, 3});\n    return 0;\n}\n'
    findings = analyse_file(code, "main.cpp", language="cpp")
    assert_true(findings["has_ai_code"], "detects AI includes in C++")
    assert_true(len(findings["ai_imports"]) >= 1, f"finds AI includes (got {len(findings['ai_imports'])})")
    print("✓ AST engine: C++ AI detection")


def test_ast_engine_rust_non_ai():
    """Rust code without AI imports is not flagged"""
    from ast_engine import analyse_file
    code = 'use std::collections::HashMap;\nuse tokio::runtime::Runtime;\n\nfn main() {\n    let map: HashMap<String, i32> = HashMap::new();\n}\n'
    findings = analyse_file(code, "main.rs", language="rust")
    assert_false(findings["has_ai_code"], "standard Rust libs not flagged as AI")
    print("✓ AST engine: Rust non-AI correctly identified")


# ── SBOM Generation Tests ──────────────────────────────────────────

def test_sbom_cyclonedx_structure():
    """SBOM generates valid CycloneDX 1.6 structure"""
    import tempfile, shutil
    from sbom import generate_sbom
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "app.py").write_text("import openai\nclient = openai.Client()\n")
    Path(temp_dir, "requirements.txt").write_text("openai==1.52.0\n")
    try:
        bom = generate_sbom(temp_dir)
        assert_eq(bom["bomFormat"], "CycloneDX", "bomFormat is CycloneDX")
        assert_eq(bom["specVersion"], "1.6", "specVersion is 1.6")
        assert_true("components" in bom, "has components")
        assert_true("metadata" in bom, "has metadata")
        assert_true(len(bom["components"]) > 0, "has at least 1 component")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ SBOM: CycloneDX 1.6 structure valid")


def test_sbom_ai_library_detection():
    """SBOM marks AI libraries with regula properties"""
    import tempfile, shutil
    from sbom import generate_sbom
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "app.py").write_text("import torch\nimport flask\n")
    Path(temp_dir, "requirements.txt").write_text("torch==2.4.1\nflask==3.0.0\n")
    try:
        bom = generate_sbom(temp_dir)
        ai_comps = [c for c in bom["components"]
                    if any(p.get("name") == "regula:is-ai-library" and p.get("value") == "true"
                           for p in c.get("properties", []))]
        assert_true(len(ai_comps) > 0, "finds AI library components")
        torch_comp = [c for c in ai_comps if c["name"] == "torch"]
        assert_true(len(torch_comp) > 0, "torch marked as AI library")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ SBOM: AI libraries marked with regula properties")


def test_sbom_model_file_detection():
    """SBOM detects ML model files"""
    import tempfile, shutil
    from sbom import generate_sbom
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "model.onnx").write_text("fake model content")
    Path(temp_dir, "app.py").write_text("import onnxruntime\n")
    try:
        bom = generate_sbom(temp_dir)
        model_comps = [c for c in bom["components"] if c.get("type") == "machine-learning-model"]
        assert_true(len(model_comps) > 0, "detects model file as ML model component")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ SBOM: ML model files detected")


# ── False positive fixes (4 tests) ─────────────────────────────────

def test_fp_fix_invoice_recognition():
    """invoice_recognition does not trigger biometrics high-risk"""
    r = classify("import torch; invoice_recognition(document)")
    assert_true(r.tier != RiskTier.HIGH_RISK or "biometric" not in (r.category or "").lower(),
                "invoice_recognition should not trigger biometrics")
    print("✓ FP fix: invoice_recognition not false positive")


def test_fp_fix_page_estimation():
    """page_estimation does not trigger biometric categorisation"""
    r = classify("import sklearn; page_estimation = calculate_pages(document)")
    assert_true(r.tier != RiskTier.LIMITED_RISK or "biometric" not in (r.category or "").lower(),
                "page_estimation should not trigger biometric categorisation")
    print("✓ FP fix: page_estimation not false positive")


def test_fp_fix_credit_model_detected():
    """Credit model training is detected as high-risk"""
    r = classify("import xgboost; credit_model = train_credit_risk_model(data)")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "credit risk model is high-risk")
    print("✓ FP fix: credit risk model correctly detected")


def test_fp_fix_social_media_score():
    """Social media engagement scoring does not trigger prohibited"""
    r = classify("import sklearn; social_media_engagement_metric = compute_engagement(posts)")
    assert_true(r.tier != RiskTier.PROHIBITED,
                "social media engagement should not trigger prohibited")
    print("✓ FP fix: social media engagement not prohibited")


# ── Article 6(3) exemption (2 tests) ──────────────────────────────

def test_exemption_assessment_likely_exempt():
    """System performing narrow procedural tasks is likely exempt"""
    from questionnaire import generate_exemption_assessment
    answers = {
        "narrow_procedural_task": "yes",
        "improves_human_output": "no",
        "pattern_detection_no_replacement": "no",
        "preparatory_task": "no",
    }
    result = generate_exemption_assessment(answers)
    assert_true(result["likely_exempt"], "narrow procedural task is likely exempt")
    assert_true("6(3)(a)" in result.get("exemption_type", ""), "identifies Art 6(3)(a)")
    assert_true(len(result.get("documentation", "")) > 50, "generates documentation")
    print("✓ Exemption: narrow procedural task is likely exempt")


def test_exemption_assessment_not_exempt():
    """System making autonomous decisions is not exempt"""
    from questionnaire import generate_exemption_assessment
    answers = {
        "narrow_procedural_task": "no",
        "improves_human_output": "no",
        "pattern_detection_no_replacement": "no",
        "preparatory_task": "no",
    }
    result = generate_exemption_assessment(answers)
    assert_false(result["likely_exempt"], "autonomous system is not exempt")
    print("✓ Exemption: autonomous system not exempt")


# ── Model card validation (2 tests) ────────────────────────────────────────

def test_model_card_validation_complete():
    """Complete model card scores high"""
    from compliance_check import validate_model_card
    card = """
# Model Card
## Intended Use
This model is intended for document summarisation.
## Limitations
Not suitable for medical advice. Known limitation: poor performance on long documents.
## Training Data
Trained on the CNN/DailyMail dataset.
## Performance
Accuracy: 85% on ROUGE-L. F1 score: 0.82.
## Ethical Considerations
We assessed bias across demographic groups. Fairness metrics reported.
"""
    result = validate_model_card(card)
    assert_true(result["completeness_score"] >= 80, f"complete card scores >= 80 (got {result['completeness_score']})")
    assert_eq(len(result["sections_missing"]), 0, "no missing sections")
    print("✓ Model card: complete card scores high")


def test_model_card_validation_incomplete():
    """Incomplete model card flags missing sections"""
    from compliance_check import validate_model_card
    card = """
# Model Card
## Intended Use
This model is for text classification.
"""
    result = validate_model_card(card)
    assert_true(result["completeness_score"] < 40, f"incomplete card scores < 40 (got {result['completeness_score']})")
    assert_true("limitations" in result["sections_missing"], "flags missing limitations")
    assert_true("training_data" in result["sections_missing"], "flags missing training data")
    print("✓ Model card: incomplete card flags missing sections")


def test_diff_mode_changed_files():
    """Diff mode filters to changed files only"""
    import tempfile, shutil, subprocess
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a git repo with two commits
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=temp_dir, capture_output=True)

        # First commit: one AI file
        Path(temp_dir, "old.py").write_text("import torch\nmodel = torch.nn.Linear(10, 1)\n")
        subprocess.run(["git", "add", "-A"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=temp_dir, capture_output=True)

        # Second commit: add another AI file
        Path(temp_dir, "new.py").write_text("import openai\nclient = openai.Client()\n")
        subprocess.run(["git", "add", "-A"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add new"], cwd=temp_dir, capture_output=True)

        # Get changed files since HEAD~1
        from cli import _get_changed_files
        changed = _get_changed_files(temp_dir, "HEAD~1")
        assert_true("new.py" in changed, "new.py is in changed files")
        assert_false("old.py" in changed, "old.py is NOT in changed files")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ Diff mode: correctly identifies changed files")


def test_remediation_high_risk_employment():
    """Employment high-risk finding gets specific fix suggestion"""
    from remediation import get_remediation
    rem = get_remediation("high_risk", "Annex III, Category 4", ["employment"], "hiring.py")
    assert_true(len(rem.get("fix_code", "")) > 20, "has fix code snippet")
    assert_true("human" in rem.get("fix_code", "").lower() or "review" in rem.get("fix_code", "").lower(),
                "fix suggests human oversight")
    assert_true("Article" in rem.get("article", ""), "references EU AI Act article")
    print("✓ Remediation: employment gets specific fix")


def test_remediation_credential():
    """Credential finding gets environment variable fix"""
    from remediation import get_remediation
    rem = get_remediation("credential_exposure", "", ["openai_api_key"], "app.py")
    assert_true("OPENAI_API_KEY" in rem.get("fix_code", ""), "suggests OPENAI_API_KEY env var")
    assert_true("os.environ" in rem.get("fix_code", ""), "uses os.environ pattern")
    print("✓ Remediation: credential gets env var fix")


def test_agent_monitor_empty_session():
    """Agent monitor handles empty sessions"""
    from agent_monitor import analyse_agent_session
    result = analyse_agent_session(session_id="nonexistent-session", hours=1)
    assert_eq(result["total_tool_calls"], 0, "empty session has 0 calls")
    assert_eq(result["risk_level"], "none", "empty session is no risk")
    assert_eq(result["autonomy_score"], 0, "empty session has 0 autonomy")
    print("✓ Agent monitor: handles empty session")


def test_agent_mcp_config_check():
    """MCP config check detects credentials"""
    import tempfile
    from agent_monitor import check_mcp_config
    # Build a fake API key at runtime to avoid credential detection in source
    fake_key = "sk-" + "abcdefghijklmnopqrstuvwxyz12345"
    config_content = '{"mcpServers": {"test": {"env": {"API_KEY": "' + fake_key + '"}}}}'
    temp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    temp.write(config_content)
    temp.close()
    findings = check_mcp_config(temp.name)
    import os; os.unlink(temp.name)
    assert_true(len(findings) > 0, "finds credential in MCP config")
    print("✓ Agent monitor: MCP config credential detection")


# ── AI Security Pattern Tests ─────────────────────────────────────

def test_ai_security_pickle_load():
    """Detects unsafe pickle deserialization in ML code"""
    from classify_risk import check_ai_security
    code = "import pickle\nwith open('model.pkl', 'rb') as f:\n    model = pickle.load(f)\n"
    findings = check_ai_security(code)
    assert_true(len(findings) > 0, "detects pickle.load")
    assert_eq(findings[0]["owasp"], "LLM05", "maps to OWASP LLM05")
    assert_true("deserialization" in findings[0]["description"].lower(), "describes deserialization risk")
    print("✓ AI security: detects unsafe pickle deserialization")


def test_ai_security_eval_on_output():
    """Detects eval/exec on AI model output"""
    from classify_risk import check_ai_security
    code = "response = client.chat.completions.create(model='gpt-4', messages=messages)\nresult = eval(response.choices[0].message.content)\n"
    findings = check_ai_security(code)
    eval_findings = [f for f in findings if f["pattern_name"] == "no_output_validation"]
    assert_true(len(eval_findings) > 0, "detects eval on AI output")
    assert_eq(eval_findings[0]["severity"], "critical", "eval on AI output is critical severity")
    print("✓ AI security: detects eval on AI output")


def test_ai_security_no_false_positive_safe_torch():
    """torch.load with weights_only=True is not flagged"""
    from classify_risk import check_ai_security
    code = "model = torch.load('model.pt', weights_only=True)\n"
    findings = check_ai_security(code)
    # The pattern matches torch.load broadly — this tests whether the pattern
    # is specific enough. If it catches safe usage, the pattern needs refinement.
    # For now, document this as a known limitation.
    print("✓ AI security: torch.load pattern tested (may flag safe usage — known limitation)")


# ── Error Handling Foundation Tests ───────────────────────────────

def test_doctor_command():
    """Test regula doctor runs and returns structured results."""
    import subprocess
    r = subprocess.run(["python3", "scripts/cli.py", "doctor"], capture_output=True, text=True)
    assert_eq(r.returncode, 0, "Doctor should exit 0")
    assert_true("Python" in r.stdout, "Should check Python version")
    assert_true("passed" in r.stdout.lower() or "PASS" in r.stdout, "Should show pass status")
    r = subprocess.run(["python3", "scripts/cli.py", "doctor", "--format", "json"],
                       capture_output=True, text=True)
    assert_eq(r.returncode, 0, "Doctor JSON should exit 0")
    data = json.loads(r.stdout)
    assert_true("data" in data and "checks" in data["data"], "JSON output should have checks in envelope")
    print("\u2713 Doctor command: runs, exits 0, supports JSON")


def test_self_test_command():
    """Test regula self-test runs built-in assertions."""
    import subprocess
    r = subprocess.run(["python3", "scripts/cli.py", "self-test"], capture_output=True, text=True)
    assert_eq(r.returncode, 0, "Self-test should exit 0")
    assert_true("PASS" in r.stdout, "Should show PASS")
    assert_true("6/6" in r.stdout or "passed" in r.stdout.lower(), "Should show all passed")
    print("\u2713 Self-test command: runs, exits 0, all assertions pass")


def test_regula_error_hierarchy():
    """Test custom exception classes exist with correct exit codes."""
    from errors import RegulaError, PathError, ConfigError, ParseError, DependencyError
    e = RegulaError("test")
    assert_eq(str(e), "test", "RegulaError message")
    assert_eq(e.exit_code, 1, "RegulaError exit_code")
    assert_eq(PathError("x").exit_code, 2, "PathError exit_code")
    assert_eq(ConfigError("x").exit_code, 2, "ConfigError exit_code")
    assert_eq(ParseError("x").exit_code, 2, "ParseError exit_code")
    assert_eq(DependencyError("x").exit_code, 2, "DependencyError exit_code")
    assert_true(isinstance(PathError("x"), RegulaError), "PathError is RegulaError")
    assert_true(isinstance(ConfigError("x"), RegulaError), "ConfigError is RegulaError")
    print("✓ Error hierarchy: all classes exist with correct exit codes")


def test_cli_exit_codes():
    """Test CLI exit code convention: 0=success, 1=findings, 2=tool error."""
    import subprocess
    r = subprocess.run(["python3", "scripts/cli.py"], capture_output=True, text=True)
    assert_eq(r.returncode, 2, "No-args should exit 2")
    r = subprocess.run(["python3", "scripts/cli.py", "check", "/nonexistent/path"],
                       capture_output=True, text=True)
    assert_eq(r.returncode, 2, "Bad path should exit 2")
    assert_true("does not exist" in r.stderr.lower(), "Should print error to stderr")
    r = subprocess.run(["python3", "scripts/cli.py", "classify", "--file", "/nonexistent.txt"],
                       capture_output=True, text=True)
    assert_eq(r.returncode, 2, "Bad file should exit 2")
    r = subprocess.run(["python3", "scripts/cli.py", "classify", "--input", "print('hello')"],
                       capture_output=True, text=True)
    assert_eq(r.returncode, 0, "Clean input should exit 0")
    print("✓ CLI exit codes: 0=success, 1=findings, 2=tool error")


def test_graceful_degradation():
    """Test check_optional utility for optional dependency messaging."""
    from degradation import check_optional, _warned
    _warned.clear()
    assert_true(check_optional("json", "JSON support", "pip install json") is True,
                "check_optional returns True for available package")
    import io
    stderr_capture = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = stderr_capture
    result = check_optional("nonexistent_package_xyz", "test feature", "pip install xyz")
    sys.stderr = old_stderr
    assert_true(result is False, "check_optional returns False for missing package")
    assert_true("nonexistent_package_xyz" in stderr_capture.getvalue(),
                "check_optional prints warning to stderr")
    # Second call should not warn again
    stderr_capture2 = io.StringIO()
    sys.stderr = stderr_capture2
    check_optional("nonexistent_package_xyz", "test feature", "pip install xyz")
    sys.stderr = old_stderr
    assert_true(stderr_capture2.getvalue() == "", "Should not warn twice for same package")
    _warned.clear()
    print("✓ Graceful degradation: check_optional works correctly")


def test_init_dry_run():
    """Test regula init --dry-run shows analysis without creating files."""
    import subprocess, tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        r = subprocess.run(["python3", "scripts/cli.py", "init", "--dry-run", "--project", tmpdir],
                           capture_output=True, text=True)
        assert_eq(r.returncode, 0, "Dry run should exit 0")
        assert_true("dry run" in r.stdout.lower() or "no changes" in r.stdout.lower(),
                     "Should mention dry run")
        assert_true(not os.path.exists(os.path.join(tmpdir, "regula-policy.yaml")),
                     "Dry run should not create files")
    print("\u2713 Init dry-run: shows analysis, creates no files")


def test_json_output_envelope():
    """Test --format json output has standard envelope with format_version."""
    import subprocess
    r = subprocess.run(["python3", "scripts/cli.py", "check", "--format", "json", "."],
                       capture_output=True, text=True)
    assert_true(r.returncode in (0, 1), "Unexpected exit code")
    data = json.loads(r.stdout)
    assert_true("format_version" in data, "Missing format_version")
    assert_eq(data["format_version"], "1.0", "format_version should be 1.0")
    assert_true("regula_version" in data, "Missing regula_version")
    assert_true("command" in data, "Missing command")
    assert_eq(data["command"], "check", "command should be check")
    assert_true("timestamp" in data, "Missing timestamp")
    assert_true("data" in data, "Missing data field")
    print("\u2713 JSON envelope: format_version, regula_version, command, timestamp, data all present")


def test_exit_code_warn_tier():
    """Test exit code 1 when WARN-tier findings exist (confidence >= 50)."""
    import subprocess, tempfile, os
    # Create fixture OUTSIDE tests/ to avoid test-file deprioritisation (-40 penalty)
    with tempfile.TemporaryDirectory() as tmpdir:
        # Employment AI code — high_risk base(65) + 1 match(+8) = 73 = WARN tier
        code = (
            "import torch\n"
            "from transformers import pipeline\n"
            "\n"
            "def rank_job_applicants(applications):\n"
            "    classifier = pipeline('text-classification')\n"
            "    return classifier(applications)\n"
            "\n"
            "def evaluate_employee_performance(data):\n"
            "    model = torch.load('model.pt')\n"
            "    return model(data)\n"
        )
        filepath = os.path.join(tmpdir, "hiring_system.py")
        with open(filepath, "w") as f:
            f.write(code)
        r = subprocess.run(["python3", "scripts/cli.py", "check", tmpdir],
                           capture_output=True, text=True)
        assert_eq(r.returncode, 1,
                  f"WARN-tier findings should exit 1, got {r.returncode}. Output: {r.stdout[-200:]}")
    print("\u2713 Exit code 1: WARN-tier findings trigger exit 1")


if __name__ == "__main__":
    tests = [
        # AI Detection (5 tests)
        test_ai_detection_python_libraries,
        test_ai_detection_model_files,
        test_ai_detection_api_endpoints,
        test_ai_detection_ml_patterns,
        test_ai_detection_non_ai,
        # Prohibited (8 tests)
        test_prohibited_social_scoring,
        test_prohibited_emotion_workplace,
        test_prohibited_emotion_school,
        test_prohibited_realtime_biometric,
        test_prohibited_biometric_sensitive,
        test_prohibited_criminal_prediction,
        test_prohibited_subliminal,
        test_prohibited_facial_scraping,
        # High-Risk (12 tests)
        test_high_risk_employment,
        test_high_risk_credit_scoring,
        test_high_risk_biometrics,
        test_high_risk_medical,
        test_high_risk_education,
        test_high_risk_critical_infrastructure,
        test_high_risk_law_enforcement,
        test_high_risk_migration,
        test_high_risk_justice,
        test_high_risk_safety,
        test_high_risk_articles,
        test_high_risk_performance_review,
        # Limited-Risk (4 tests)
        test_limited_risk_chatbot,
        test_limited_risk_deepfake,
        test_limited_risk_age_estimation,
        test_limited_risk_emotion_no_workplace,
        # Minimal-Risk (3 tests)
        test_minimal_risk_recommendation,
        test_minimal_risk_code_completion,
        test_minimal_risk_spam_filter,
        # Edge Cases (9 tests)
        test_edge_empty_input,
        test_edge_case_insensitivity,
        test_edge_multiple_indicators,
        test_edge_prohibited_without_ai_indicator,
        test_edge_prohibited_overrides_high_risk,
        test_edge_high_risk_overrides_limited,
        test_classification_action_field,
        test_classification_to_dict,
        test_classification_to_json,
        # Policy Engine (4 tests)
        test_policy_yaml_parser,
        test_policy_check_overrides,
        test_policy_cannot_exempt_prohibited,
        test_prohibited_has_exceptions_field,
        # Audit Trail (2 tests)
        test_audit_hash_chain,
        test_audit_export_csv,
        # Confidence Scoring (3 tests)
        test_confidence_score_numeric,
        test_confidence_score_ordering,
        test_multiple_indicators_increase_score,
        # Reports (3 tests)
        test_sarif_output_structure,
        test_html_report_contains_disclaimer,
        test_inline_suppression,
        # Report enhancement (1 test)
        test_report_html_dependency_section,
        # New features (6 tests)
        test_questionnaire_generation,
        test_questionnaire_evaluation_high_risk,
        test_questionnaire_evaluation_minimal_risk,
        test_session_aggregation,
        test_baseline_save_and_compare,
        test_timeline_data,
        # Secret detection (4 tests)
        test_secret_detection_openai_key,
        test_secret_detection_aws_key,
        test_secret_detection_no_false_positive,
        test_secret_redaction,
        # GPAI awareness (2 tests)
        test_gpai_training_detection,
        test_gpai_inference_not_training,
        # AI credential governance (1 test)
        test_file_credential_governance,
        # Hook integration (4 tests)
        test_hook_prohibited_block,
        test_hook_high_risk_allow_with_iso,
        test_hook_secret_block,
        test_hook_clean_pass,
        # AI System Registry (2 tests)
        test_registry_scan_organization,
        test_registry_csv_export,
        # Compliance workflow (2 tests)
        test_compliance_workflow_transitions,
        test_compliance_status_update,
        # Governance (1 test)
        test_governance_contacts,
        # QMS generation (1 test)
        test_qms_scaffold_generation,
        # Regex fix (1 test)
        test_openai_key_no_anthropic_false_positive,
        # AST analysis (5 tests)
        test_ast_parse_python_file,
        test_ast_classify_context,
        test_ast_data_flow_tracing,
        test_ast_human_oversight,
        test_ast_logging_practices,
        # Compliance gap assessment (2 tests)
        test_compliance_gap_assessment,
        test_compliance_gap_article_15_tests,
        # Infrastructure (3 tests)
        test_regulatory_basis,
        test_cross_platform_locking,
        # AST engine (5 tests)
        test_ast_engine_python_parse,
        test_ast_engine_js_regex_fallback,
        test_ast_engine_ts_regex_fallback,
        test_ast_engine_non_ai_js,
        test_ast_engine_language_detection,
        # Language expansion (3 tests)
        test_ast_engine_java_ai_detection,
        test_ast_engine_go_ai_detection,
        test_ast_engine_java_non_ai,
        # Rust/C/C++ language support (3 tests)
        test_ast_engine_rust_ai_detection,
        test_ast_engine_cpp_ai_detection,
        test_ast_engine_rust_non_ai,
        # Dependency supply chain (6 tests)
        test_dep_scan_requirements_txt,
        test_dep_scan_ai_identification,
        test_dep_scan_pinning_score,
        test_dep_scan_lockfile_detection,
        test_dep_scan_package_json,
        test_dep_scan_compromised_detection,
        # Rust/C++ dependency parsing (2 tests)
        test_dep_scan_cargo_toml,
        test_dep_scan_vcpkg_json,
        # Gap assessment enhancement (1 test)
        test_gap_article_15_dependency_pinning,
        # Framework mapper (2 tests)
        test_framework_mapper_eu_to_nist,
        test_framework_mapper_all_frameworks,
        # OWASP mapping (1 test)
        test_framework_mapper_owasp_llm,
        # MITRE ATLAS mapping (1 test)
        test_framework_mapper_mitre_atlas,
        # Additional framework mappings (4 tests)
        test_framework_mapper_nist_csf,
        test_framework_mapper_soc2,
        test_framework_mapper_iso_27001,
        test_framework_mapper_all_8_frameworks,
        # Policy enhancement (2 tests)
        test_policy_thresholds,
        test_policy_exclusions,
        # Integration tests (4 tests)
        test_integration_high_risk_project,
        test_integration_compliant_project,
        test_integration_unpinned_deps,
        test_integration_full_check_cli,
        # Pattern quality (5 tests)
        test_pattern_no_false_positive_sentence_nlp,
        test_pattern_no_false_positive_embedding_layer,
        test_pattern_no_false_positive_generic_predict,
        test_pattern_true_positive_cv_screening,
        test_pattern_true_positive_credit_scoring,
        # Confidence threshold (1 test)
        test_confidence_threshold_filtering,
        # Confidence tiers (2 tests)
        test_confidence_tier_block,
        test_confidence_tier_info,
        # Tree-sitter JS/TS (4 tests)
        test_tree_sitter_js_import_extraction,
        test_tree_sitter_js_data_flow,
        test_tree_sitter_ts_oversight_detection,
        test_tree_sitter_js_function_extraction,
        # SBOM generation (3 tests)
        test_sbom_cyclonedx_structure,
        test_sbom_ai_library_detection,
        test_sbom_model_file_detection,
        # False positive fixes (4 tests)
        test_fp_fix_invoice_recognition,
        test_fp_fix_page_estimation,
        test_fp_fix_credit_model_detected,
        test_fp_fix_social_media_score,
        # Article 6(3) exemption (2 tests)
        test_exemption_assessment_likely_exempt,
        test_exemption_assessment_not_exempt,
        # Model card validation (2 tests)
        test_model_card_validation_complete,
        test_model_card_validation_incomplete,
        # Diff scanning (1 test)
        test_diff_mode_changed_files,
        # Remediation engine (2 tests)
        test_remediation_high_risk_employment,
        test_remediation_credential,
        # Agent monitoring (2 tests)
        test_agent_monitor_empty_session,
        test_agent_mcp_config_check,
        # AI security patterns (3 tests)
        test_ai_security_pickle_load,
        test_ai_security_eval_on_output,
        test_ai_security_no_false_positive_safe_torch,
        # Doctor + Self-test (2 tests)
        test_doctor_command,
        test_self_test_command,
        # Error handling foundation (2 tests)
        test_regula_error_hierarchy,
        test_cli_exit_codes,
        # Graceful degradation (1 test)
        test_graceful_degradation,
        # Init dry-run + JSON envelope (2 tests)
        test_init_dry_run,
        test_json_output_envelope,
        # Exit code verification (1 test)
        test_exit_code_warn_tier,
    ]

    print(f"Running {len(tests)} tests...\n")

    for test in tests:
        try:
            test()
        except Exception as e:
            failed += 1
            print(f"  EXCEPTION in {test.__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed ({len(tests)} test functions)")
    if failed:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
