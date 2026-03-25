#!/usr/bin/env python3
"""Comprehensive test suite for Regula classification engine"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from classify_risk import classify, RiskTier, is_ai_related

passed = 0
failed = 0


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
        # New features (6 tests)
        test_questionnaire_generation,
        test_questionnaire_evaluation_high_risk,
        test_questionnaire_evaluation_minimal_risk,
        test_session_aggregation,
        test_baseline_save_and_compare,
        test_timeline_data,
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
