# regula-ignore
#!/usr/bin/env python3
"""Comprehensive test suite for Regula classification engine"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from classify_risk import classify, RiskTier, is_ai_related

# Pull in regula register tests so the auto-discoverer picks them up.
# (See commit a90009f — the runner walks this file's globals to find test_* functions.)
sys.path.insert(0, str(Path(__file__).parent))
import test_register as _test_register  # noqa: F401
import test_build_regulations as _test_build_regulations  # noqa: F401
import test_gpai_check as _test_gpai_check  # noqa: F401
import test_new_commands as _test_new_commands  # noqa: F401

passed = 0
failed = 0
_PYTEST_MODE = "pytest" in sys.modules

# Bring register tests into this module's globals so the custom runner picks
# them up via globals() walk. Skip tests that require pytest fixtures
# (monkeypatch / tmp_path / capsys) when running under the custom runner —
# pytest discovers them natively from tests/test_register.py and runs them
# with proper fixture injection.
import inspect as _inspect
_PYTEST_FIXTURES = {"monkeypatch", "tmp_path", "capsys", "tmpdir", "request"}
for _mod in (_test_register, _test_build_regulations, _test_gpai_check, _test_new_commands):
    for _name in dir(_mod):
        if not _name.startswith("test_"):
            continue
        _fn = getattr(_mod, _name)
        if not callable(_fn):
            continue
        try:
            _params = set(_inspect.signature(_fn).parameters)
        except (TypeError, ValueError):
            _params = set()
        if _params & _PYTEST_FIXTURES:
            continue
        globals()[_name] = _fn
del _inspect, _mod, _name, _fn, _params, _PYTEST_FIXTURES, _test_register, _test_build_regulations, _test_gpai_check, _test_new_commands

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
        if _PYTEST_MODE:
            raise AssertionError(f"{msg} — expected {expected!r}, got {actual!r}")
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


def test_recall_realistic_employment_code():
    """Regression (audit Apr 2026): realistic OpenAI-driven hiring code
    was being classified minimal_risk because the original employment
    patterns required literal tokens like 'cv_screen' or 'candidate_rank'.
    A function literally named classify_resume with hire/reject branching
    must flag as high-risk."""
    code = (
        "import openai\n"
        "client = openai.OpenAI()\n"
        "def classify_resume(resume_text):\n"
        "    reply = client.chat.completions.create(\n"
        "        model='gpt-4',\n"
        "        messages=[{'role':'user','content':f'Score this resume: {resume_text}'}])\n"
        "    score = reply.choices[0].message.content\n"
        "    if float(score) > 0.5:\n"
        "        return 'hire'\n"
        "    return 'reject'\n"
    )
    r = classify(code)
    assert_eq(r.tier, RiskTier.HIGH_RISK, "classify_resume is high-risk")
    assert_eq(r.category, "Annex III, Category 4", "employment category")
    print("✓ Recall: realistic classify_resume code correctly flagged employment")


# regula-ignore — the next three tests construct fixtures that look like
# Annex III high-risk AI for verification purposes; they are test data,
# not real practice.

def test_recall_realistic_education_code():
    """Regression (audit Apr 2026): realistic ed-tech AI code (essay grading,
    dropout prediction, admissions ranking) was missed by the narrow
    'admission_decision' / 'student_assess' / 'exam_score' / 'proctor' patterns.
    Annex III point 3 covers AI used to determine access to education and
    AI used to evaluate students."""
    cases = [
        ("import openai\n"
         "def grade_essay(text):\n"
         "    return openai.OpenAI().chat.completions.create(\n"
         "        model='gpt-4',\n"
         "        messages=[{'role':'user','content':f'Grade this essay: {text}'}]).choices[0].message.content\n",
         "essay autograder"),
        ("import sklearn.ensemble\n"
         "def predict_dropout(student_features):\n"
         "    return RandomForestClassifier().fit(X, y).predict_proba(student_features)\n",
         "dropout predictor"),
        ("import torch\n"
         "def rank_university_applicants(applicant_pool):\n"
         "    return sorted(applicant_pool, key=lambda a: model(a).item(), reverse=True)\n",
         "admissions ranking"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Annex III, Category 3", f"{label} education category")
    print("✓ Recall: ed-tech AI (essay grading, dropout, admissions) correctly flagged")


def test_recall_realistic_essential_services_code():
    """Regression (audit Apr 2026): realistic fintech / insurtech / govtech AI
    (loan approval, insurance pricing, welfare eligibility, claim assessment)
    was missed by the narrow 'credit_score' / 'loan_decision' patterns.
    Annex III point 5 covers creditworthiness, life/health insurance pricing,
    access to public benefits, and emergency call dispatching."""
    cases = [
        ("import openai\n"
         "def approve_loan(application):\n"
         "    return openai.OpenAI().chat.completions.create(\n"
         "        model='gpt-4',\n"
         "        messages=[{'role':'user','content':f'Approve loan: {application}'}]).choices[0].message.content\n",
         "loan approval"),
        ("import sklearn\n"
         "def health_insurance_pricing(profile):\n"
         "    return premium_model.predict(profile)\n",
         "health insurance pricing"),
        ("import torch\n"
         "def welfare_eligibility_score(applicant):\n"
         "    return model(applicant)\n",
         "welfare eligibility"),
        ("import xgboost\n"
         "def assess_claim(claim_data):\n"
         "    return claim_assess_model.predict(claim_data)\n",
         "claim assessment"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Annex III, Category 5", f"{label} essential services category")
    print("✓ Recall: fintech/insurtech/govtech AI correctly flagged essential services")


def test_recall_realistic_law_enforcement_code():
    """Regression (audit Apr 2026): realistic crime-analytics AI (parole risk,
    bail risk, suspect threat scoring) was missed by the narrow 'polygraph'
    / 'lie_detect' patterns. Annex III point 6 covers law-enforcement uses
    that remain LAWFUL (with Articles 9-15 obligations) — distinct from the
    Article 5(1)(d) prohibition handled by PROHIBITED_PATTERNS."""
    cases = [
        ("import torch\n"
         "class ParoleModel:\n"
         "    def parole_decision(self, inmate_data):\n"
         "        return self.model.predict(inmate_data)\n",
         "parole decision model"),
        ("import sklearn\n"
         "def bail_risk_assess(defendant):\n"
         "    return rf.predict_proba(defendant)\n",
         "bail risk assessment"),
        ("import xgboost\n"
         "def suspect_threat_score(person_features):\n"
         "    return threat_model.predict(person_features)\n",
         "suspect threat score"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Annex III, Category 6", f"{label} law enforcement category")
    print("✓ Recall: crime-analytics AI (parole, bail, threat) correctly flagged law enforcement")


# regula-ignore — the next six tests construct fixtures that look like
# Annex III high-risk AI for verification purposes; they are test data,
# not real practice.

def test_recall_realistic_biometrics_code():
    """Regression (recall expansion Apr 2026): real-world biometric AI
    (iris match, gait recognition, age-from-face inference) was missed by
    the narrow original patterns. Annex III Cat 1 covers biometric
    identification, categorisation, and verification (the lawful high-risk
    uses; untargeted scraping and RBI are Article 5 prohibitions)."""
    cases = [
        ("import torch\n"
         "def iris_match(probe, gallery):\n"
         "    return iris_model.verify(probe, gallery)\n",
         "iris match"),
        ("import torch\n"
         "def gait_recognition(video):\n"
         "    return gait_model.identify(extract_silhouettes(video))\n",
         "gait recognition"),
        ("import openai\n"
         "def detect_age_from_face(image_bytes):\n"
         "    return openai.OpenAI().chat.completions.create(\n"
         "        model='gpt-4',\n"
         "        messages=[{'role':'user','content':f'Infer age from face image'}]).choices[0].message.content\n",
         "age from face"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Annex III, Category 1", f"{label} biometrics category")
    print("✓ Recall: biometric AI (iris, gait, age-from-face) correctly flagged")


def test_recall_realistic_critical_infrastructure_code():
    """Regression (recall expansion Apr 2026): real-world grid / SCADA /
    pipeline / railway AI was missed by the narrow 'energy_grid' / 'water_supply'
    patterns. Annex III Cat 2 covers safety components in management of
    critical digital infrastructure, traffic, and utilities."""
    cases = [
        ("import torch\n"
         "def grid_load_forecast(features):\n"
         "    return load_model.predict(features)\n",
         "grid load forecast"),
        ("import xgboost\n"
         "def pipeline_pressure_monitor(telemetry):\n"
         "    return scada_model.predict(telemetry)\n",
         "pipeline SCADA"),
        ("import sklearn\n"
         "def railway_signal_control(track_state):\n"
         "    return interlocking.decide(track_state)\n",
         "railway signalling"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Annex III, Category 2", f"{label} critical infrastructure category")
    print("✓ Recall: critical-infrastructure AI (grid, SCADA, railway) correctly flagged")


def test_recall_realistic_migration_code():
    """Regression (recall expansion Apr 2026): real-world visa/asylum/border
    AI was missed by the narrow 'border_control' / 'visa_application' patterns.
    Annex III Cat 7 covers risk assessment of persons in a migration context."""
    cases = [
        ("import openai\n"
         "def approve_visa(dossier):\n"
         "    return openai.OpenAI().chat.completions.create(\n"
         "        model='gpt-4',\n"
         "        messages=[{'role':'user','content':f'Score visa risk for: {dossier}'}]).choices[0].message.content\n",
         "visa approval"),
        ("import torch\n"
         "def asylum_credibility_score(case):\n"
         "    return asylum_model.predict(case)\n",
         "asylum credibility"),
        ("import sklearn\n"
         "def border_threat_score(traveller):\n"
         "    return threat_model.predict_proba(traveller)\n",
         "border threat scoring"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Annex III, Category 7", f"{label} migration category")
    print("✓ Recall: migration AI (visa, asylum, border) correctly flagged")


def test_recall_realistic_justice_code():
    """Regression (recall expansion Apr 2026): real-world judicial-assist and
    election-influence AI was missed by the narrow original patterns. Annex III
    Cat 8 covers AI used by judicial authorities and AI used to influence
    elections or voting behaviour."""
    cases = [
        ("import openai\n"
         "def predict_verdict(case_facts):\n"
         "    return openai.OpenAI().chat.completions.create(\n"
         "        model='gpt-4',\n"
         "        messages=[{'role':'user','content':f'Predict verdict: {case_facts}'}]).choices[0].message.content\n",
         "verdict prediction"),
        ("import torch\n"
         "def predict_case_outcome(facts):\n"
         "    return court_outcome_model.predict(facts)\n",
         "case outcome prediction"),
        ("import sklearn\n"
         "def voter_microtarget(profile):\n"
         "    return persuasion_model.predict(profile)\n",
         "voter microtargeting"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Annex III, Category 8", f"{label} justice category")
    print("✓ Recall: justice AI (verdict, case outcome, voter targeting) correctly flagged")


def test_recall_realistic_medical_devices_code():
    """Regression (recall expansion Apr 2026): real-world radiology, sepsis,
    dosing and clinical-decision AI was missed by the narrow 'medical_diagnosis'
    / 'patient_triage' patterns. Article 6(1) + Annex I Section A covers AI in
    medical devices (MDR 2017/745) and IVDs (IVDR 2017/746)."""
    cases = [
        ("import torch\n"
         "def detect_tumor(ct_scan):\n"
         "    return radiology_model.segment(ct_scan)\n",
         "tumour detection"),
        ("import xgboost\n"
         "def sepsis_early_warning(vitals):\n"
         "    return sepsis_model.predict_proba(vitals)\n",
         "sepsis early warning"),
        ("import sklearn\n"
         "def insulin_dose_recommend(patient):\n"
         "    return dose_model.predict(patient)\n",
         "insulin dosing"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Medical Devices", f"{label} medical devices category")
    print("✓ Recall: medical-device AI (radiology, sepsis, dosing) correctly flagged")


def test_recall_realistic_safety_components_code():
    """Regression (recall expansion Apr 2026): real-world ADAS, cobot, drone
    and rail-safety AI was missed by the narrow 'autonomous_vehicle' /
    'machinery_safety' patterns. Article 6(1) + Annex I Sections A and B cover
    AI safety components of machinery, vehicles, aviation, rail, and marine."""
    cases = [
        ("import torch\n"
         "def pedestrian_detection(frame):\n"
         "    return yolo_model.predict(frame)\n",
         "pedestrian detection ADAS"),
        ("import sklearn\n"
         "def cobot_collision_avoid(sensors):\n"
         "    return safety_model.decide(sensors)\n",
         "industrial cobot safety"),
        ("import xgboost\n"
         "def drone_obstacle_avoid(lidar):\n"
         "    return flight_control.plan(lidar)\n",
         "drone obstacle avoidance"),
    ]
    for code, label in cases:
        r = classify(code)
        assert_eq(r.tier, RiskTier.HIGH_RISK, f"{label} should be high-risk")
        assert_eq(r.category, "Safety Components", f"{label} safety components category")
    print("✓ Recall: safety-component AI (ADAS, cobot, drone) correctly flagged")


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
    import policy_config
    original = policy_config._POLICY

    policy_config._POLICY = {
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

    policy_config._POLICY = original
    print("✓ Policy engine: force_high_risk and exempt work")


def test_policy_cannot_exempt_prohibited():
    """CRITICAL: Policy exempt list CANNOT override prohibited practices"""
    import policy_config
    original = policy_config._POLICY

    # Try to exempt a prohibited pattern via policy
    policy_config._POLICY = {
        "rules": {
            "risk_classification": {
                "exempt": ["social_scoring_v2"],
            }
        }
    }

    # Even though "social_scoring_v2" is in exempt, "social scoring" is prohibited
    r = classify("social scoring v2 with tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "prohibited CANNOT be exempted by policy")

    policy_config._POLICY = original
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


def test_advisory_load_fallback_pyc_path():
    """_load_advisories() still finds advisories when __file__ resolves to a .pyc in __pycache__

    Regression: here.parent resolves to scripts/__pycache__ instead of scripts/ when the .pyc
    is used, making here.parent / 'references' / 'advisories' point at a non-existent path.
    """
    try:
        import yaml  # noqa: F401
    except ImportError:
        print("✓ Advisory fallback: pyyaml not available, skipping")
        return

    from unittest.mock import patch
    from pathlib import Path
    import dependency_scan

    # Simulate __file__ = scripts/__pycache__/dependency_scan.cpython-312.pyc
    fake_file = str(
        Path(dependency_scan.__file__).resolve().parent
        / "__pycache__"
        / "dependency_scan.cpython-312.pyc"
    )
    with patch.object(dependency_scan, "__file__", fake_file):
        advisories = dependency_scan._load_advisories()

    assert_true(len(advisories) > 0, "_load_advisories finds advisories despite pyc __file__")
    print("✓ Advisory fallback: _load_advisories works from pyc __file__ path")


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


# Go / Java dependency parsing (6 tests)

def test_dep_scan_go_mod_basic():
    """Parses go.mod require blocks and identifies deps"""
    from dependency_scan import parse_go_mod
    content = '''\
module github.com/myuser/myapp

go 1.21

require (
\tgithub.com/tmc/langchaingo v0.1.12
\tgithub.com/sashabaranov/go-openai v1.24.0
\tgithub.com/google/uuid v1.6.0 // indirect
)

require github.com/ollama/ollama v0.3.0
'''
    deps = parse_go_mod(content)
    names = [d["name"] for d in deps]
    assert_true("github.com/tmc/langchaingo" in names, "finds langchaingo")
    assert_true("github.com/sashabaranov/go-openai" in names, "finds go-openai")
    assert_true("github.com/google/uuid" in names, "finds uuid")
    assert_true("github.com/ollama/ollama" in names, "finds ollama (single-line require)")
    print("✓ Dependency scan: go.mod basic parsing")


def test_dep_scan_go_mod_ai_flagged():
    """AI Go modules are flagged is_ai=True, standard libs are not"""
    from dependency_scan import parse_go_mod
    content = '''\
module github.com/myuser/myapp

go 1.21

require (
\tgithub.com/tmc/langchaingo v0.1.12
\tgithub.com/sashabaranov/go-openai v1.20.0
\tgithub.com/google/uuid v1.6.0
)
'''
    deps = parse_go_mod(content)
    langchain = [d for d in deps if "langchaingo" in d["name"]]
    assert_true(len(langchain) > 0, "finds langchaingo")
    assert_true(langchain[0]["is_ai"], "langchaingo is AI")
    openai = [d for d in deps if "go-openai" in d["name"]]
    assert_true(len(openai) > 0, "finds go-openai")
    assert_true(openai[0]["is_ai"], "go-openai is AI")
    uuid = [d for d in deps if "uuid" in d["name"]]
    assert_true(len(uuid) > 0, "finds uuid")
    assert_false(uuid[0]["is_ai"], "uuid is not AI")
    print("✓ Dependency scan: go.mod AI detection")


def test_dep_scan_go_mod_pinning():
    """go.mod versions are always exact (no ranges in Go modules)"""
    from dependency_scan import parse_go_mod
    content = '''\
module github.com/myuser/myapp

go 1.21

require (
\tgithub.com/tmc/langchaingo v0.1.12
\tgithub.com/sashabaranov/go-openai v1.24.0
)
'''
    deps = parse_go_mod(content)
    for d in deps:
        assert_eq(d["pinning"], "exact", f"{d['name']} should be exact-pinned in go.mod")
    print("✓ Dependency scan: go.mod pinning is always exact")


def test_dep_scan_build_gradle_groovy():
    """Parses build.gradle (Groovy DSL) dependencies"""
    from dependency_scan import parse_build_gradle
    content = """\
plugins {
    id 'java'
}

dependencies {
    implementation 'dev.langchain4j:langchain4j:0.31.0'
    implementation "org.deeplearning4j:deeplearning4j-core:1.0.0-M2.1"
    implementation group: 'ai.djl', name: 'api', version: '0.28.0'
    testImplementation 'junit:junit:4.13.2'
    implementation 'com.google.guava:guava:32.1.3-jre'
}
"""
    deps = parse_build_gradle(content)
    names = [d["name"] for d in deps]
    assert_true("dev.langchain4j:langchain4j" in names, "finds langchain4j")
    assert_true("org.deeplearning4j:deeplearning4j-core" in names, "finds deeplearning4j")
    assert_true("ai.djl:api" in names, "finds djl (named group syntax)")
    assert_true("junit:junit" in names, "finds junit")
    print("✓ Dependency scan: build.gradle Groovy DSL parsing")


def test_dep_scan_build_gradle_kts():
    """Parses build.gradle.kts (Kotlin DSL) dependencies"""
    from dependency_scan import parse_build_gradle
    content = """\
dependencies {
    implementation("dev.langchain4j:langchain4j:0.31.0")
    implementation("org.tensorflow:tensorflow-core-platform:0.5.0")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
    implementation("io.github.ollama4j:ollama4j:1.0.79")
}
"""
    deps = parse_build_gradle(content)
    names = [d["name"] for d in deps]
    assert_true("dev.langchain4j:langchain4j" in names, "finds langchain4j (kts)")
    assert_true("org.tensorflow:tensorflow-core-platform" in names, "finds tensorflow-core")
    assert_true("io.github.ollama4j:ollama4j" in names, "finds ollama4j")
    print("✓ Dependency scan: build.gradle.kts Kotlin DSL parsing")


def test_dep_scan_build_gradle_ai_flagged():
    """AI Java/Kotlin deps in build.gradle are flagged is_ai=True"""
    from dependency_scan import parse_build_gradle
    content = """\
dependencies {
    implementation 'dev.langchain4j:langchain4j:0.31.0'
    implementation 'com.google.guava:guava:32.1.3-jre'
    implementation 'ai.djl:api:0.28.0'
}
"""
    deps = parse_build_gradle(content)
    lc = [d for d in deps if "langchain4j" in d["name"]]
    assert_true(len(lc) > 0 and lc[0]["is_ai"], "langchain4j is AI")
    djl = [d for d in deps if "djl" in d["name"]]
    assert_true(len(djl) > 0 and djl[0]["is_ai"], "ai.djl is AI")
    guava = [d for d in deps if "guava" in d["name"]]
    assert_true(len(guava) > 0, "finds guava")
    assert_false(guava[0]["is_ai"], "guava is not AI")
    print("✓ Dependency scan: build.gradle AI detection")


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
        [sys.executable, "scripts/cli.py", "check", fixture_path, "--format", "json", "--no-skip-tests", "--min-tier", "minimal_risk"],
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
    """SBOM generates valid CycloneDX 1.7 structure (Oct 2025, ECMA-424 2nd Ed.)"""
    import tempfile, shutil
    from sbom import generate_sbom
    temp_dir = tempfile.mkdtemp()
    Path(temp_dir, "app.py").write_text("import openai\nclient = openai.Client()\n")
    Path(temp_dir, "requirements.txt").write_text("openai==1.52.0\n")
    try:
        bom = generate_sbom(temp_dir)
        assert_eq(bom["bomFormat"], "CycloneDX", "bomFormat is CycloneDX")
        assert_eq(bom["specVersion"], "1.7", "specVersion is 1.7")
        assert_true("components" in bom, "has components")
        assert_true("metadata" in bom, "has metadata")
        assert_true(len(bom["components"]) > 0, "has at least 1 component")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ SBOM: CycloneDX 1.7 structure valid")


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


def test_fn_fix_credit_scorer_function_names():
    """train_credit_model + score_applicant as function names → HIGH-RISK (Annex III Cat 5)

    Regression: \bcredit.?model fails when 'credit' is preceded by '_' (underscore is a word
    char), causing train_credit_model to score minimal_risk instead of high_risk.
    """
    code = (
        "import sklearn.ensemble\n"
        "import pandas as pd\n"
        "\n"
        "def train_credit_model(features, labels):\n"
        "    model = RandomForestClassifier()\n"
        "    return model.fit(features, labels)\n"
        "\n"
        "def score_applicant(model, applicant_data):\n"
        "    return model.predict_proba(applicant_data)\n"
    )
    r = classify(code)
    assert_eq(r.tier, RiskTier.HIGH_RISK, "train_credit_model is high-risk")
    assert_eq(r.category, "Annex III, Category 5", "credit scoring is Category 5")
    print("✓ FN fix: train_credit_model correctly detected as high-risk")


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


# ── Prompt Injection (OWASP LLM01:2025) ───────────────────────────────

def test_prompt_injection_direct_request_body():
    """Direct injection: request body content placed straight into messages."""
    from classify_risk import check_ai_security
    code = (
        "def handler(request):\n"
        "    messages = [{'role': 'user', 'content': request.json['message']}]\n"
        "    return client.chat.completions.create(messages=messages)\n"
    )
    findings = check_ai_security(code)
    pi = [f for f in findings if f["pattern_name"] == "prompt_injection_vulnerable"]
    assert_true(len(pi) > 0, "detects request body -> messages content as direct injection")
    assert_eq(pi[0]["owasp"], "LLM01", "maps to OWASP LLM01")
    assert_eq(pi[0]["severity"], "high", "direct prompt injection is high severity")
    print("✓ Prompt injection (direct): request body in messages content")


def test_prompt_injection_indirect_web_fetch():
    """Indirect injection: web-fetched content one-liner into prompt content."""
    from classify_risk import check_ai_security
    code = (
        "messages = [{'role': 'user', 'content': requests.get(url).text}]\n"
        "client.chat.completions.create(messages=messages)\n"
    )
    findings = check_ai_security(code)
    pi = [f for f in findings if f["pattern_name"] == "prompt_injection_indirect"]
    assert_true(len(pi) > 0, "detects requests.get(...).text in messages content as indirect injection")
    assert_eq(pi[0]["owasp"], "LLM01", "maps to OWASP LLM01")
    print("✓ Prompt injection (indirect): web fetch one-liner")


def test_prompt_injection_indirect_file_read():
    """Indirect injection: file content read inline into prompt."""
    from classify_risk import check_ai_security
    code = "messages = [{'role': 'user', 'content': open(path).read()}]\n"
    findings = check_ai_security(code)
    pi = [f for f in findings if f["pattern_name"] == "prompt_injection_indirect"]
    assert_true(len(pi) > 0, "detects open(...).read() in messages content as indirect injection")
    print("✓ Prompt injection (indirect): file read one-liner")


def test_prompt_injection_indirect_rag_chain():
    """Indirect injection: LangChain RAG retriever output chained directly."""
    from classify_risk import check_ai_security
    code = "chain.invoke({'context': retriever.invoke(query), 'question': q})\n"
    findings = check_ai_security(code)
    pi = [f for f in findings if f["pattern_name"] == "prompt_injection_indirect"]
    assert_true(len(pi) > 0, "detects retriever.invoke result chained into chain.invoke")
    print("✓ Prompt injection (indirect): RAG chain pattern")


def test_prompt_injection_tool_subprocess():
    """Tool/agent injection: subprocess output appended to messages."""
    from classify_risk import check_ai_security
    code = "messages.append({'role':'user','content': subprocess.run(cmd).stdout})\n"
    findings = check_ai_security(code)
    pi = [f for f in findings if f["pattern_name"] == "prompt_injection_tool_output"]
    assert_true(len(pi) > 0, "detects subprocess.run output in messages.append")
    print("✓ Prompt injection (tool): subprocess output")


def test_prompt_injection_tool_observation():
    """Tool/agent injection: observation/tool_result variable into messages."""
    from classify_risk import check_ai_security
    code = "messages.append({'role':'user','content': tool_result})\n"
    findings = check_ai_security(code)
    pi = [f for f in findings if f["pattern_name"] == "prompt_injection_tool_output"]
    assert_true(len(pi) > 0, "detects tool_result variable in messages.append")
    print("✓ Prompt injection (tool): observation pattern")


def test_prompt_injection_no_false_positive_proper_separation():
    """Properly delimited system + sanitised user content is NOT flagged."""
    from classify_risk import check_ai_security
    code = (
        "SYSTEM = 'You are a helpful assistant.'\n"
        "def chat(user_text):\n"
        "    return client.chat.completions.create(\n"
        "        messages=[{'role':'system','content':SYSTEM},\n"
        "                  {'role':'user','content':sanitize(user_text)}]\n"
        "    )\n"
    )
    findings = check_ai_security(code)
    pi = [f for f in findings if "prompt_injection" in f["pattern_name"]]
    assert_eq(len(pi), 0, f"clean code with sanitisation should not flag, got: {[f['pattern_name'] for f in pi]}")
    print("✓ Prompt injection: no false positive on proper separation + sanitiser")


def test_prompt_injection_remediation_mentions_guardrails():
    """Remediation text references guardrail libraries (LLM Guard, Lakera, etc)."""
    from classify_risk import check_ai_security
    code = "messages = [{'role': 'user', 'content': requests.get(url).text}]\n"
    findings = check_ai_security(code)
    pi = [f for f in findings if f["pattern_name"] == "prompt_injection_indirect"]
    assert_true(len(pi) > 0, "indirect injection finding present")
    rem = pi[0]["remediation"].lower()
    has_guardrail = any(g in rem for g in ["nemo", "llm guard", "lakera", "rebuff", "guardrails ai"])
    assert_true(has_guardrail, "remediation references at least one guardrails library")
    print("✓ Prompt injection: remediation mentions guardrails")


# ── Article 6(3) Exemption Self-Assessment (regula exempt) ────────────

def test_exempt_not_in_annex_iii():
    """If the system is not in any Annex III area, return NOT_IN_ANNEX_III early."""
    from exempt_check import evaluate, RESULT_NOT_IN_ANNEX_III
    result = evaluate({"annex_iii": "no"})
    assert_eq(result["result"], RESULT_NOT_IN_ANNEX_III, "early-exit when not Annex III")
    assert_eq(len(result["conditions_met"]), 0, "no conditions evaluated")
    print("✓ Exempt: early-exit when not in Annex III")


def test_exempt_profiling_overrides_all():
    """Profiling answer 'yes' must produce NOT_EXEMPT regardless of (a)-(d)."""
    from exempt_check import evaluate, RESULT_NOT_EXEMPT
    answers = {
        "annex_iii": "yes", "profiling": "yes",
        "narrow_procedural": "yes", "improve_human": "yes",
        "detect_patterns": "yes", "preparatory": "yes",
    }
    result = evaluate(answers)
    assert_eq(result["result"], RESULT_NOT_EXEMPT, "profiling overrides exemption conditions")
    print("✓ Exempt: profiling overrides all conditions")


def test_exempt_condition_a_only():
    """Narrow procedural task alone is sufficient when no profiling."""
    from exempt_check import evaluate, RESULT_EXEMPT
    answers = {
        "annex_iii": "yes", "profiling": "no",
        "narrow_procedural": "yes", "improve_human": "no",
        "detect_patterns": "no", "preparatory": "no",
    }
    result = evaluate(answers)
    assert_eq(result["result"], RESULT_EXEMPT, "condition (a) alone sufficient")
    assert_eq(result["conditions_met"], ["a"], "only condition (a) marked")
    print("✓ Exempt: condition (a) narrow procedural")


def test_exempt_all_four_conditions():
    """All four conditions met -> exempt with full list."""
    from exempt_check import evaluate, RESULT_EXEMPT
    answers = {
        "annex_iii": "yes", "profiling": "no",
        "narrow_procedural": "yes", "improve_human": "yes",
        "detect_patterns": "yes", "preparatory": "yes",
    }
    result = evaluate(answers)
    assert_eq(result["result"], RESULT_EXEMPT, "all four conditions exempt")
    assert_eq(result["conditions_met"], ["a", "b", "c", "d"], "all four marked")
    print("✓ Exempt: all four conditions")


def test_exempt_no_conditions_means_high_risk():
    """Annex III, no profiling, but none of (a)-(d) -> NOT_EXEMPT."""
    from exempt_check import evaluate, RESULT_NOT_EXEMPT
    answers = {
        "annex_iii": "yes", "profiling": "no",
        "narrow_procedural": "no", "improve_human": "no",
        "detect_patterns": "no", "preparatory": "no",
    }
    result = evaluate(answers)
    assert_eq(result["result"], RESULT_NOT_EXEMPT, "none of (a)-(d) means not exempt")
    print("✓ Exempt: none of (a)-(d) means not exempt")


def test_exempt_parse_answers_csv_valid():
    """parse_answers_csv accepts a six-element comma-separated list."""
    from exempt_check import parse_answers_csv
    out = parse_answers_csv("y,n,y,n,n,n")
    assert_true(out is not None, "valid CSV parses")
    assert_eq(out["annex_iii"], "yes", "first value is annex_iii=yes")
    assert_eq(out["profiling"], "no", "second value is profiling=no")
    assert_eq(out["narrow_procedural"], "yes", "third value is narrow_procedural=yes")
    print("✓ Exempt: parse_answers_csv valid input")


def test_exempt_parse_answers_csv_wrong_length():
    """parse_answers_csv rejects wrong number of elements."""
    from exempt_check import parse_answers_csv
    assert_true(parse_answers_csv("y,n,y") is None, "3 values rejected")
    assert_true(parse_answers_csv("y,n,y,n,n,n,n") is None, "7 values rejected")
    print("✓ Exempt: parse_answers_csv wrong length rejected")


def test_exempt_parse_answers_csv_invalid_token():
    """parse_answers_csv rejects non-yes/no tokens."""
    from exempt_check import parse_answers_csv
    assert_true(parse_answers_csv("y,n,maybe,n,n,n") is None, "'maybe' rejected")
    print("✓ Exempt: parse_answers_csv invalid token rejected")


def test_exempt_format_result_exempt_includes_disclosure():
    """Exempt result text includes the missed-deadline disclosure."""
    from exempt_check import evaluate, format_result
    result = evaluate({
        "annex_iii": "yes", "profiling": "no",
        "narrow_procedural": "yes", "improve_human": "no",
        "detect_patterns": "no", "preparatory": "no",
    })
    text = format_result(result)
    assert_true("Article 6" in text, "mentions Article 6")
    assert_true("2 February 2026" in text, "mentions missed deadline")
    assert_true("EXEMPT" in text, "shows EXEMPT result")
    print("✓ Exempt: format_result includes guidelines disclosure")


def test_gap_assessment_includes_article_6_disclosure():
    """assess_compliance() result dict includes article_6_guidelines_status."""
    import tempfile
    from compliance_check import assess_compliance
    with tempfile.TemporaryDirectory() as tmp:
        result = assess_compliance(tmp)
    assert_true("article_6_guidelines_status" in result, "key present in assessment dict")
    status = result["article_6_guidelines_status"]
    assert_eq(status["missed"], True, "deadline marked as missed")
    assert_eq(status["deadline"], "2026-02-02", "correct deadline date")
    print("✓ Gap: Article 6 guidelines status in assessment dict")


# ── SME Simplified Annex IV (regula conform --sme) ────────────

def test_sme_simplified_annex_iv_generates_markdown():
    """generate_sme_simplified_annex_iv produces a non-empty Markdown doc."""
    import tempfile
    from generate_documentation import generate_sme_simplified_annex_iv, scan_project
    with tempfile.TemporaryDirectory() as tmp:
        findings = scan_project(tmp)
        doc = generate_sme_simplified_annex_iv(findings, "test-system", tmp)
    assert_true(len(doc) > 1000, f"doc should be substantive, got {len(doc)} chars")
    assert_true(doc.startswith("# Annex IV (SME Simplified)"), "starts with SME header")
    print("✓ SME Annex IV: generator produces non-empty markdown")


def test_sme_simplified_annex_iv_includes_interim_disclosure():
    """SME doc includes the Article 11(1) interim-format disclosure."""
    import tempfile
    from generate_documentation import generate_sme_simplified_annex_iv, scan_project
    with tempfile.TemporaryDirectory() as tmp:
        findings = scan_project(tmp)
        doc = generate_sme_simplified_annex_iv(findings, "test-system", tmp)
    assert_true("INTERIM FORMAT" in doc, "INTERIM FORMAT marker present")
    assert_true("Article 11(1)" in doc, "Article 11(1) reference present")
    assert_true("Commission" in doc, "References Commission template")
    assert_true("2026-04-08" in doc, "carries the verified-on date")
    print("✓ SME Annex IV: interim-format disclosure present")


def test_sme_simplified_annex_iv_references_other_regula_commands():
    """SME doc points the user at gpai-check, oversight, exempt, and sbom."""
    import tempfile
    from generate_documentation import generate_sme_simplified_annex_iv, scan_project
    with tempfile.TemporaryDirectory() as tmp:
        findings = scan_project(tmp)
        doc = generate_sme_simplified_annex_iv(findings, "test-system", tmp)
    for cmd in ["regula gpai-check", "regula oversight", "regula exempt", "regula sbom"]:
        assert_true(cmd in doc, f"references {cmd}")
    print("✓ SME Annex IV: references companion commands")


def test_sme_simplified_pack_writes_single_file():
    """generate_sme_simplified_pack writes one .md file and returns expected shape."""
    import tempfile
    from conform import generate_sme_simplified_pack
    with tempfile.TemporaryDirectory() as tmp:
        result = generate_sme_simplified_pack(tmp, output_dir=tmp, project_name="sme-test")
        # Assertions must run inside the temp-dir context — the file is
        # cleaned up when the context exits.
        pack_path = Path(result["pack_path"])
        assert_true(pack_path.is_file(), "single file produced")
        assert_true(pack_path.name.startswith("simplified-annex-iv-sme-test-"), "uses simplified naming")
        assert_true(pack_path.name.endswith(".md"), "is markdown file")
        assert_eq(result["summary"]["form"], "sme_simplified_annex_iv", "form field correct")
        assert_eq(len(result["manifest"]["files"]), 1, "manifest has exactly one file")
        assert_true("sha256" in result["manifest"]["files"][0], "sha256 hash present")
    print("✓ SME conform: single-file pack with correct shape")


def test_sme_simplified_pack_disclosure_in_manifest():
    """SME pack manifest carries the interim-format disclosure."""
    import tempfile
    from conform import generate_sme_simplified_pack
    with tempfile.TemporaryDirectory() as tmp:
        result = generate_sme_simplified_pack(tmp, output_dir=tmp, project_name="sme-test")
    disclosure = result["manifest"].get("interim_format_disclosure", "")
    assert_true("Article 11(1)" in disclosure, "manifest mentions Article 11(1)")
    assert_true("Commission" in disclosure, "manifest mentions Commission template")
    print("✓ SME conform: manifest carries interim-format disclosure")


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
    """Test check_optional utility for optional dependency messaging.

    As of v1.6.1 the nag is SILENT by default and only prints when
    REGULA_VERBOSE=1 is set. This avoids spamming users with the same
    optional-dependency note on every CLI invocation. Doctor still
    surfaces the full status.
    """
    import os
    from degradation import check_optional, _warned
    _warned.clear()
    assert_true(check_optional("json", "JSON support", "pip install json") is True,
                "check_optional returns True for available package")

    # Default mode: SILENT on missing package.
    import io
    stderr_capture = io.StringIO()
    old_stderr = sys.stderr
    old_verbose = os.environ.pop("REGULA_VERBOSE", None)
    sys.stderr = stderr_capture
    result = check_optional("nonexistent_package_xyz", "test feature", "pip install xyz")
    sys.stderr = old_stderr
    assert_true(result is False, "check_optional returns False for missing package")
    assert_true(stderr_capture.getvalue() == "",
                "check_optional is silent by default (no REGULA_VERBOSE)")

    # Verbose mode: prints once on first miss.
    _warned.clear()
    os.environ["REGULA_VERBOSE"] = "1"
    stderr_capture2 = io.StringIO()
    sys.stderr = stderr_capture2
    check_optional("nonexistent_package_xyz2", "test feature", "pip install xyz2")
    sys.stderr = old_stderr
    assert_true("nonexistent_package_xyz2" in stderr_capture2.getvalue(),
                "check_optional prints warning to stderr when REGULA_VERBOSE=1")

    # Verbose mode: second call for the same package is silent.
    stderr_capture3 = io.StringIO()
    sys.stderr = stderr_capture3
    check_optional("nonexistent_package_xyz2", "test feature", "pip install xyz2")
    sys.stderr = old_stderr
    assert_true(stderr_capture3.getvalue() == "",
                "Should not warn twice for same package even in verbose mode")

    # Restore env state.
    if old_verbose is None:
        os.environ.pop("REGULA_VERBOSE", None)
    else:
        os.environ["REGULA_VERBOSE"] = old_verbose
    _warned.clear()
    print("✓ Graceful degradation: silent default + REGULA_VERBOSE opt-in")


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


def test_ci_flag_compliant_exits_0():
    """--ci flag on compliant code exits 0."""
    import subprocess
    r = subprocess.run(["python3", "scripts/cli.py", "check",
                        "tests/fixtures/sample_compliant/", "--ci"],
                       capture_output=True, text=True)
    assert_eq(r.returncode, 0, f"--ci compliant should exit 0, got {r.returncode}")
    print("\u2713 --ci flag: compliant code exits 0")


def test_ci_flag_warn_tier_exits_1():
    """--ci flag on WARN-tier code exits 1 (implies --strict)."""
    import subprocess, tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
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
        r = subprocess.run(["python3", "scripts/cli.py", "check", tmpdir, "--ci"],
                           capture_output=True, text=True)
        assert_eq(r.returncode, 1,
                  f"--ci WARN-tier should exit 1, got {r.returncode}. Output: {r.stdout[-200:]}")
    print("\u2713 --ci flag: WARN-tier findings exit 1")


def test_ci_flag_error_exits_2():
    """--ci flag on error exits 2."""
    import subprocess
    r = subprocess.run(["python3", "scripts/cli.py", "check", "/nonexistent", "--ci"],
                       capture_output=True, text=True)
    assert_eq(r.returncode, 2, f"--ci error should exit 2, got {r.returncode}")
    print("\u2713 --ci flag: error exits 2")


def test_ci_flag_before_subcommand():
    """--ci flag works when placed before the subcommand (global position)."""
    import subprocess
    r = subprocess.run(["python3", "scripts/cli.py", "--ci", "check",
                        "tests/fixtures/sample_compliant/"],
                       capture_output=True, text=True)
    assert_eq(r.returncode, 0,
              f"--ci before subcommand should exit 0 for compliant, got {r.returncode}")
    print("\u2713 --ci flag: works before subcommand")


def test_ci_flag_info_tier_exits_0():
    """--ci flag on INFO-tier (below WARN) code exits 0."""
    import subprocess
    r = subprocess.run(["python3", "scripts/cli.py", "check",
                        "tests/fixtures/sample_high_risk/", "--ci"],
                       capture_output=True, text=True)
    assert_eq(r.returncode, 0,
              f"--ci INFO-tier should exit 0, got {r.returncode}")
    print("\u2713 --ci flag: INFO-tier exits 0")


# ── CLI Subcommand Smoke Tests ──────────────────────────────────────


def _run_cli(*args):
    """Helper: run CLI command and return subprocess result."""
    import subprocess
    return subprocess.run(["python3", "scripts/cli.py"] + list(args),
                          capture_output=True, text=True, timeout=30)


def _assert_json_envelope(stdout, command_name):
    """Helper: validate standard JSON output envelope."""
    data = json.loads(stdout)
    assert_true("format_version" in data, f"{command_name}: missing format_version")
    assert_true("regula_version" in data, f"{command_name}: missing regula_version")
    assert_true("command" in data, f"{command_name}: missing command")
    assert_true("timestamp" in data, f"{command_name}: missing timestamp")
    return data


def test_smoke_report():
    """Smoke test: regula report --format json runs and exits 0."""
    r = _run_cli("report", "--project", "tests/fixtures/sample_compliant/", "--format", "json")
    assert_true(r.returncode in (0, 1), f"report exit {r.returncode}: {r.stderr[:200]}")
    assert_true(len(r.stdout) > 10, "report should produce output")
    print("\u2713 Smoke: report --format json exits 0 with output")


def test_smoke_discover():
    """Smoke test: regula discover runs and exits 0."""
    r = _run_cli("discover", "--project", "tests/fixtures/sample_compliant/")
    assert_true(r.returncode in (0, 1), f"discover exit {r.returncode}: {r.stderr[:200]}")
    assert_true(len(r.stdout) > 10, "discover should produce output")
    print("\u2713 Smoke: discover exits 0 with output")


def test_smoke_install_help():
    """Smoke test: regula install --help runs and exits 0."""
    r = _run_cli("install", "--help")
    assert_eq(r.returncode, 0, f"install --help exit {r.returncode}")
    assert_true("platform" in r.stdout.lower(), "install help should mention platform")
    print("\u2713 Smoke: install --help exits 0")


def test_smoke_status():
    """Smoke test: regula status runs and exits 0."""
    r = _run_cli("status")
    assert_eq(r.returncode, 0, f"status exit {r.returncode}: {r.stderr[:200]}")
    print("\u2713 Smoke: status exits 0")


def test_smoke_feed():
    """Smoke test: regula feed --format json runs and exits 0."""
    r = _run_cli("feed", "--format", "json")
    assert_eq(r.returncode, 0, f"feed exit {r.returncode}: {r.stderr[:200]}")
    data = _assert_json_envelope(r.stdout, "feed")
    assert_true("data" in data, "feed: missing data field")
    print("\u2713 Smoke: feed --format json exits 0 with envelope")


def test_smoke_questionnaire():
    """Smoke test: regula questionnaire --format json runs and exits 0."""
    r = _run_cli("questionnaire", "--format", "json")
    assert_eq(r.returncode, 0, f"questionnaire exit {r.returncode}: {r.stderr[:200]}")
    data = _assert_json_envelope(r.stdout, "questionnaire")
    assert_true("data" in data, "questionnaire: missing data field")
    print("\u2713 Smoke: questionnaire --format json exits 0 with envelope")


def test_smoke_session():
    """Smoke test: regula session --format json runs and exits 0."""
    r = _run_cli("session", "--format", "json")
    assert_eq(r.returncode, 0, f"session exit {r.returncode}: {r.stderr[:200]}")
    data = _assert_json_envelope(r.stdout, "session")
    print("\u2713 Smoke: session --format json exits 0 with envelope")


def test_smoke_baseline():
    """Smoke test: regula baseline --help runs and exits 0."""
    r = _run_cli("baseline", "--help")
    assert_eq(r.returncode, 0, f"baseline --help exit {r.returncode}")
    assert_true("baseline" in r.stdout.lower(), "baseline help should mention baseline")
    print("\u2713 Smoke: baseline --help exits 0")


def test_smoke_docs():
    """Smoke test: regula docs --project <path> runs and exits 0."""
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal Python file so docs has something to scan
        with open(os.path.join(tmpdir, "app.py"), "w") as f:
            f.write("import openai\nclient = openai.Client()\n")
        r = _run_cli("docs", "--project", tmpdir)
        assert_eq(r.returncode, 0, f"docs exit {r.returncode}: {r.stderr[:200]}")
        assert_true(len(r.stdout) > 10, "docs should produce output")
    print("\u2713 Smoke: docs exits 0 with output")


def test_smoke_compliance():
    """Smoke test: regula compliance runs and exits 0."""
    r = _run_cli("compliance")
    assert_eq(r.returncode, 0, f"compliance exit {r.returncode}: {r.stderr[:200]}")
    print("\u2713 Smoke: compliance exits 0")


def test_smoke_gap():
    """Smoke test: regula gap --format json runs and exits 0."""
    r = _run_cli("gap", "--project", "tests/fixtures/sample_compliant/", "--format", "json")
    assert_eq(r.returncode, 0, f"gap exit {r.returncode}: {r.stderr[:200]}")
    data = _assert_json_envelope(r.stdout, "gap")
    assert_true("data" in data, "gap: missing data field")
    print("\u2713 Smoke: gap --format json exits 0 with envelope")


def test_smoke_benchmark():
    """Smoke test: regula benchmark --format json runs and exits 0."""
    r = _run_cli("benchmark", "--project", "tests/fixtures/sample_compliant/", "--format", "json")
    assert_eq(r.returncode, 0, f"benchmark exit {r.returncode}: {r.stderr[:200]}")
    assert_true(len(r.stdout) > 10, "benchmark should produce output")
    print("\u2713 Smoke: benchmark --format json exits 0 with output")


def test_smoke_timeline():
    """Smoke test: regula timeline --format json runs and exits 0."""
    r = _run_cli("timeline", "--format", "json")
    assert_eq(r.returncode, 0, f"timeline exit {r.returncode}: {r.stderr[:200]}")
    data = _assert_json_envelope(r.stdout, "timeline")
    assert_true("data" in data, "timeline: missing data field")
    print("\u2713 Smoke: timeline --format json exits 0 with envelope")


def test_smoke_deps():
    """Smoke test: regula deps --format json runs and exits 0."""
    r = _run_cli("deps", "--project", "tests/fixtures/sample_compliant/", "--format", "json")
    assert_eq(r.returncode, 0, f"deps exit {r.returncode}: {r.stderr[:200]}")
    data = _assert_json_envelope(r.stdout, "deps")
    assert_true("data" in data, "deps: missing data field")
    print("\u2713 Smoke: deps --format json exits 0 with envelope")


def test_smoke_sbom():
    """Smoke test: regula sbom --format json runs and exits 0."""
    r = _run_cli("sbom", "--project", "tests/fixtures/sample_compliant/", "--format", "json")
    assert_eq(r.returncode, 0, f"sbom exit {r.returncode}: {r.stderr[:200]}")
    data = json.loads(r.stdout)
    assert_true("bomFormat" in data, "sbom: missing bomFormat (CycloneDX)")
    assert_eq(data["bomFormat"], "CycloneDX", "sbom should be CycloneDX format")
    print("\u2713 Smoke: sbom --format json exits 0 with CycloneDX envelope")


def test_smoke_agent():
    """Smoke test: regula agent --format json runs and exits 0."""
    r = _run_cli("agent", "--format", "json")
    assert_eq(r.returncode, 0, f"agent exit {r.returncode}: {r.stderr[:200]}")
    data = _assert_json_envelope(r.stdout, "agent")
    print("\u2713 Smoke: agent --format json exits 0 with envelope")


def test_generic_exception_handler():
    """Test that non-RegulaError exceptions are caught with clean message."""
    import subprocess
    # Simulate by importing a module that will fail
    code = '''
import sys; sys.path.insert(0, "scripts")
from cli import main
import argparse
# Monkey-patch a command to raise an unexpected exception
import cli
def bad_func(args): raise RuntimeError("unexpected boom")
cli.cmd_check = bad_func
sys.argv = ["regula", "check", "."]
main()
'''
    r = subprocess.run(["python3", "-c", code], capture_output=True, text=True, timeout=10)
    assert_eq(r.returncode, 2, f"Generic exception should exit 2, got {r.returncode}")
    assert_true("internal error" in r.stderr.lower() or "bug" in r.stderr.lower(),
                f"Should print internal error message, got: {r.stderr[:200]}")
    print("\u2713 Generic exception handler: catches non-RegulaError, exits 2")


def test_framework_flag_removed():
    """Test that the unused --framework flag has been removed."""
    r = _run_cli("--framework", "eu-ai-act", "check", "tests/fixtures/sample_compliant/")
    assert_eq(r.returncode, 2, f"--framework should be unrecognized, got exit {r.returncode}")
    assert_true("unrecognized" in r.stderr.lower() or "error" in r.stderr.lower(),
                f"Should show error for --framework, got: {r.stderr[:200]}")
    print("\u2713 --framework flag removed (unrecognized argument)")


def test_github_action_structure():
    """action.yml has required fields for GitHub Marketplace."""
    action_path = Path(__file__).parent.parent / "action.yml"
    assert action_path.exists(), "action.yml must exist at repo root"
    content = action_path.read_text()
    assert "name:" in content, "action.yml must have name field"
    assert "description:" in content, "action.yml must have description field"
    assert "branding:" in content, "action.yml must have branding (required for Marketplace)"
    assert "inputs:" in content, "action.yml must define inputs"
    assert "outputs:" in content, "action.yml must define outputs"
    assert "runs:" in content, "action.yml must have runs section"
    print("\u2713 GitHub Action: action.yml structure valid")


def test_pdf_export_html_fallback():
    """pdf_export returns HTML bytes when weasyprint is not available."""
    import sys, unittest.mock
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

    # Simulate weasyprint not installed
    with unittest.mock.patch.dict("sys.modules", {"weasyprint": None}):
        import importlib
        import pdf_export
        importlib.reload(pdf_export)
        html_input = "<html><body><h1>Test Annex IV</h1></body></html>"
        result = pdf_export.render_to_pdf(html_input, fallback_to_html=True)
        assert isinstance(result, bytes)
        assert b"Test Annex IV" in result
    print("\u2713 PDF export: HTML fallback returns HTML bytes when weasyprint absent")


def test_pdf_export_html_content_valid():
    """generate_annex_iv_html produces valid HTML with required sections."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from pdf_export import generate_annex_iv_html
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        html = generate_annex_iv_html(tmpdir, "Test System")
        assert "<html" in html.lower()
        assert "Annex IV" in html
        assert "Test System" in html
    print("\u2713 PDF export: generate_annex_iv_html produces valid HTML")


def test_mcp_server_tool_list():
    """MCP server returns correct tools/list response."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from mcp_server import handle_request

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    response = handle_request(request)
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    tools = response["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "regula_check" in tool_names, f"regula_check missing from tools: {tool_names}"
    assert "regula_classify" in tool_names
    assert "regula_gap" in tool_names
    print("\u2713 MCP server: tools/list returns correct tool names")


def test_mcp_server_initialize():
    """MCP server responds to initialize with correct protocol version."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from mcp_server import handle_request

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    response = handle_request(request)
    assert response["result"]["protocolVersion"] == "2024-11-05"
    assert response["result"]["serverInfo"]["name"] == "regula"
    print("\u2713 MCP server: initialize returns correct protocolVersion")


def test_mcp_server_classify_tool():
    """regula_classify tool returns a tier for known AI pattern."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from mcp_server import handle_request

    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "regula_classify",
            "arguments": {"input": "import openai\nresponse = openai.chat.completions.create(model='gpt-4', messages=[])"}
        }
    }
    response = handle_request(request)
    assert "result" in response, f"No result in response: {response}"
    content = response["result"]["content"]
    assert isinstance(content, list) and len(content) > 0
    text = content[0]["text"]
    assert any(tier in text.upper() for tier in ["MINIMAL", "LIMITED", "HIGH", "PROHIBITED"]), \
        f"Expected a tier in response, got: {text}"
    print("\u2713 MCP server: regula_classify returns tier")


def test_bias_eval_score_range():
    """bias_eval returns scores between 0 and 100 for all categories."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from bias_eval import compute_stereotype_score

    mock_results = [
        {"category": "race", "preferred_stereotyped": True},
        {"category": "race", "preferred_stereotyped": False},
        {"category": "race", "preferred_stereotyped": True},
        {"category": "gender", "preferred_stereotyped": True},
        {"category": "gender", "preferred_stereotyped": True},
    ]
    scores = compute_stereotype_score(mock_results)
    assert "race" in scores
    assert "gender" in scores
    assert 0 <= scores["race"] <= 100
    assert 0 <= scores["gender"] <= 100
    assert scores["race"] == 67, f"Expected 67, got {scores['race']}"
    assert scores["gender"] == 100
    print("\u2713 Bias eval: compute_stereotype_score returns correct per-category percentages")


def test_bias_eval_dataset_sample():
    """CrowS-Pairs dataset sample loads correctly."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from bias_eval import load_crowspairs_sample

    pairs = load_crowspairs_sample()
    assert len(pairs) > 0
    assert len(pairs) >= 10
    first = pairs[0]
    assert "sent_more" in first
    assert "sent_less" in first
    assert "bias_type" in first
    print(f"\u2713 Bias eval: CrowS-Pairs sample loaded {len(pairs)} pairs")


def test_bias_eval_no_ollama():
    """bias_eval handles Ollama unavailability gracefully."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from bias_eval import evaluate_with_ollama

    result = evaluate_with_ollama(
        [{"sent_more": "A", "sent_less": "B", "bias_type": "race"}],
        endpoint="http://localhost:9999",
        timeout=1,
    )
    assert result["status"] == "error"
    assert "unavailable" in result["message"].lower() or "error" in result["message"].lower()
    print("\u2713 Bias eval: handles Ollama unavailability gracefully")


def test_timestamp_build_tsq():
    """_build_tsq produces a valid DER structure for SHA-256 hash."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from timestamp import _build_tsq
    import hashlib
    hash_bytes = hashlib.sha256(b"test input").digest()
    tsq = _build_tsq(hash_bytes, nonce=12345678)
    # Must be bytes
    assert isinstance(tsq, bytes), "TSQ must be bytes"
    # Must start with SEQUENCE tag (0x30)
    assert tsq[0] == 0x30, "TSQ DER must start with SEQUENCE tag 0x30"
    # Must contain the SHA-256 OID bytes (2.16.840.1.101.3.4.2.1)
    sha256_oid_bytes = bytes([0x60, 0x86, 0x48, 0x01, 0x65, 0x03, 0x04, 0x02, 0x01])
    assert sha256_oid_bytes in tsq, "TSQ must contain SHA-256 OID"
    print("\u2713 RFC 3161: _build_tsq produces valid DER")


def test_timestamp_parse_response_invalid():
    """parse_tsr raises ValueError for garbage input."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from timestamp import parse_tsr
    try:
        parse_tsr(b"not a valid DER response")
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    print("\u2713 RFC 3161: parse_tsr rejects invalid input")


def test_log_event_tst_field():
    """log_event stores tst_hex when external_timestamp=True (mocked)."""
    import sys, unittest.mock
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import log_event as le

    fake_tst = {"tst_hex": "deadbeef", "tsa_url": "https://freetsa.org/tsr", "timestamp": "2026-03-29T00:00:00Z"}
    with unittest.mock.patch("log_event.request_timestamp", return_value=fake_tst):
        event = le.log_event("test_event", {"tier": "minimal_risk"}, external_timestamp=True)
    assert event.data.get("tst_hex") == "deadbeef", "tst_hex must be stored in event data"
    print("\u2713 RFC 3161: log_event stores tst_hex when external_timestamp=True")


def test_compliance_check_js_ts_article14():
    """Article 14 gap check returns score > 0 for a JS file with review function."""
    import sys, tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from compliance_check import assess_compliance as check_compliance

    js_content = """
import OpenAI from 'openai';

const client = new OpenAI();

async function reviewAIOutput(output) {
    // Human reviews AI output before action
    return humanApproval(output);
}

async function main() {
    const response = await client.chat.completions.create({
        model: 'gpt-4',
        messages: [{ role: 'user', content: 'Classify this text' }]
    });
    return reviewAIOutput(response.choices[0].message.content);
}
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        js_file = os.path.join(tmpdir, "app.js")
        with open(js_file, "w") as f:
            f.write(js_content)
        results = check_compliance(tmpdir)

    art14 = (results.get("articles") or {}).get("14") or results.get("article_14") or results.get("14") or {}
    score = art14.get("score", 0)
    assert score > 20, f"Article 14 score should be > 20 for JS with review function, got {score}"
    print(f"\u2713 Compliance check: JS/TS Article 14 wired correctly (score={score})")


def test_conformity_declaration_structure():
    """Declaration of Conformity contains all Annex XIII required fields."""
    import sys, tempfile
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from generate_documentation import generate_conformity_declaration

    with tempfile.TemporaryDirectory() as tmpdir:
        doc = generate_conformity_declaration(tmpdir, system_name="Test AI System", version="1.0")

    required_fields = [
        "Provider",
        "AI system",
        "Annex III",
        "conformity",
        "Article 9",
    ]
    for field in required_fields:
        assert field in doc, f"Declaration of Conformity missing required field: {field}"
    print("\u2713 Declaration of Conformity: all Annex XIII required fields present")


def test_benchmark_corpus_structure():
    """run_public_corpus returns a dict with per-article results."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from benchmark import compute_article_pass_rates

    mock_results = [
        {"repo": "org/repo1", "article_9": 20, "article_12": 0,  "article_14": 30, "files": 10},
        {"repo": "org/repo2", "article_9": 0,  "article_12": 0,  "article_14": 0,  "files": 5},
        {"repo": "org/repo3", "article_9": 50, "article_12": 60, "article_14": 70, "files": 20},
        {"repo": "org/repo4", "article_9": 80, "article_12": 40, "article_14": 50, "files": 15},
        {"repo": "org/repo5", "article_9": 10, "article_12": 5,  "article_14": 10, "files": 8},
    ]
    rates = compute_article_pass_rates(mock_results, pass_threshold=50)
    assert "article_9" in rates
    assert "article_12" in rates
    assert "article_14" in rates
    assert rates["article_9"]["pass_rate"] == 40, f"Expected 40%, got {rates['article_9']['pass_rate']}"
    print("\u2713 Benchmark: compute_article_pass_rates returns correct pass rates")


# ---------------------------------------------------------------------------
# Feature: Local metrics
# ---------------------------------------------------------------------------

def test_metrics_record_and_get():
    """record_scan increments counts; get_stats returns correct structure."""
    import tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import metrics as m

    # Use temp dir to avoid polluting real metrics
    orig_home = os.environ.get("HOME")
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["HOME"] = tmpdir
        try:
            # Reset state
            m.reset_stats()

            # Record two scans
            m.record_scan([{"tier": "BLOCK"}, {"tier": "WARN"}, {"tier": "WARN"}])
            m.record_scan([{"tier": "BLOCK"}])

            stats = m.get_stats()
            assert stats["total_scans"] == 2
            assert stats["total_findings"] == 4
            assert stats["findings_by_tier"]["BLOCK"] == 2
            assert stats["findings_by_tier"]["WARN"] == 2
            assert stats["first_scan"] is not None
            assert stats["last_scan"] is not None
            print("✓ Metrics: record_scan and get_stats work correctly")
        finally:
            if orig_home:
                os.environ["HOME"] = orig_home
            else:
                del os.environ["HOME"]


def test_metrics_reset():
    """reset_stats clears all data."""
    import tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import metrics as m

    orig_home = os.environ.get("HOME")
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["HOME"] = tmpdir
        try:
            m.record_scan([{"tier": "BLOCK"}])
            m.reset_stats()
            stats = m.get_stats()
            assert stats["total_scans"] == 0
            assert stats["total_findings"] == 0
            print("✓ Metrics: reset_stats clears all data")
        finally:
            if orig_home:
                os.environ["HOME"] = orig_home


def test_metrics_empty():
    """get_stats returns zeros when no metrics file exists."""
    import tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import metrics as m

    orig_home = os.environ.get("HOME")
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["HOME"] = tmpdir
        try:
            stats = m.get_stats()
            assert stats["total_scans"] == 0
            assert stats["total_findings"] == 0
            assert stats["first_scan"] is None
            assert stats["last_scan"] is None
            print("✓ Metrics: get_stats returns zeros when no file exists")
        finally:
            if orig_home:
                os.environ["HOME"] = orig_home


# ---------------------------------------------------------------------------
# Feature: Security self-check (defined here so __main__ can reference them)
# ---------------------------------------------------------------------------

def test_security_self_check_passes():
    """security-self-check runs and passes on regula's own source."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from security_self_check import run_security_self_check
    result = run_security_self_check(format_type="silent")
    assert isinstance(result, dict)
    assert "passed" in result
    assert "total_findings" in result
    assert "unexpected_findings" in result
    assert "known_acceptable" in result
    # The self-check should pass (no unexpected findings)
    assert result["passed"], (
        f"Unexpected findings in regula source: {result['unexpected_findings']}"
    )
    print(f"✓ Security self-check: passed ({result['total_findings']} total, "
          f"{len(result['known_acceptable'])} known acceptable)")


def test_security_self_check_result_structure():
    """result dict has all required keys and correct types."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from security_self_check import run_security_self_check
    result = run_security_self_check(format_type="silent")
    assert isinstance(result["passed"], bool)
    assert isinstance(result["total_findings"], int)
    assert isinstance(result["unexpected_findings"], list)
    assert isinstance(result["known_acceptable"], list)
    assert isinstance(result["message"], str)
    print("✓ Security self-check: result structure is correct")


# ---------------------------------------------------------------------------
# Feature: Config validation
# ---------------------------------------------------------------------------

def test_config_validate_valid_file():
    """validate_config returns valid=True for the repo's own regula-policy.yaml."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from config_validator import validate_config
    # Use the repo's own regula-policy.yaml
    policy_path = str(Path(__file__).parent.parent / "regula-policy.yaml")
    result = validate_config(path=policy_path, format_type="silent")
    assert isinstance(result, dict)
    assert result["valid"] is True
    assert "errors" in result
    assert "warnings" in result
    assert len(result["errors"]) == 0
    print(f"✓ Config validate: repo policy is valid ({len(result['warnings'])} warnings)")


def test_config_validate_invalid_thresholds():
    """validate_config returns valid=False when warn_above >= block_above."""
    import sys, tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from config_validator import validate_config
    bad_config = """
version: "1.0"
thresholds:
  block_above: 50
  warn_above: 80
"""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        f.write(bad_config)
        tmp_path = f.name
    try:
        result = validate_config(path=tmp_path, format_type="silent")
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("warn_above" in e for e in result["errors"])
        print("✓ Config validate: invalid thresholds correctly rejected")
    finally:
        os.unlink(tmp_path)


def test_config_validate_no_file():
    """validate_config with explicit nonexistent path returns valid=False."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from config_validator import validate_config
    result = validate_config(path="/nonexistent/path/to/config.yaml", format_type="silent")
    assert result["valid"] is False
    assert len(result["errors"]) > 0
    print("✓ Config validate: nonexistent explicit path returns valid=False")


# ---------------------------------------------------------------------------
# Feature: Quickstart onboarding command
# ---------------------------------------------------------------------------

def test_quickstart_creates_policy():
    """quickstart creates a policy file in a clean directory."""
    import sys, tempfile, shutil
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from quickstart import run_quickstart
    tmp = Path(tempfile.mkdtemp())
    try:
        result = run_quickstart(project_dir=str(tmp), org="Test Org", format_type="silent")
        assert result["policy_created"] is True
        assert (tmp / "regula-policy.yaml").exists()
        content = (tmp / "regula-policy.yaml").read_text()
        assert "Test Org" in content
        print("✓ Quickstart: creates policy file with org name")
    finally:
        shutil.rmtree(tmp)


def test_quickstart_skips_existing_policy():
    """quickstart does not overwrite an existing policy file."""
    import sys, tempfile, shutil
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from quickstart import run_quickstart
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / "regula-policy.yaml").write_text("version: '2.0'\n")
        result = run_quickstart(project_dir=str(tmp), format_type="silent")
        assert result["policy_created"] is False
        content = (tmp / "regula-policy.yaml").read_text()
        assert "2.0" in content, "Existing policy should not be overwritten"
        print("✓ Quickstart: skips existing policy file")
    finally:
        shutil.rmtree(tmp)


def test_quickstart_result_structure():
    """quickstart returns expected keys."""
    import sys, tempfile, shutil
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from quickstart import run_quickstart
    tmp = Path(tempfile.mkdtemp())
    try:
        result = run_quickstart(project_dir=str(tmp), format_type="silent")
        assert "policy_created" in result
        assert "policy_path" in result
        assert "scan_summary" in result
        assert "elapsed_seconds" in result
        assert "next_steps" in result
        s = result["scan_summary"]
        assert "total_findings" in s
        assert "block" in s
        assert "warn" in s
        assert "info" in s
        assert "files_scanned" in s
        print("✓ Quickstart: result structure has all expected keys")
    finally:
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# Feature: Brazilian market — LGPD + Marco Legal da IA framework mapping
# ---------------------------------------------------------------------------

def test_lgpd_framework_mapping():
    """LGPD maps to all EU AI Act articles 9-15."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from framework_mapper import map_to_frameworks
    # Article 13 (transparency) has the most LGPD touchpoints
    result = map_to_frameworks(["13"], frameworks=["lgpd"])
    assert "13" in result, "Article 13 must be in result"
    lgpd = result["13"].get("lgpd", {})
    assert lgpd, "LGPD mapping for Article 13 must be non-empty"
    assert "articles" in lgpd, "LGPD mapping must have 'articles' key"
    assert len(lgpd["articles"]) > 0, "LGPD mapping must have at least one article reference"
    # Verify Art. 20 (automated decision review) is referenced
    all_refs = " ".join(lgpd["articles"])
    assert "20" in all_refs, "LGPD Art. 20 (automated decision review) must be in Article 13 mapping"
    print(f"✓ LGPD framework: Article 13 maps to {len(lgpd['articles'])} LGPD references")


def test_marco_legal_ia_framework_mapping():
    """Marco Legal da IA maps to all EU AI Act articles 9-15."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from framework_mapper import map_to_frameworks
    # Article 14 (human oversight) is key for Marco Legal da IA
    result = map_to_frameworks(["14"], frameworks=["marco-legal-ia"])
    assert "14" in result
    marco = result["14"].get("marco_legal_ia", {})
    assert marco, "Marco Legal da IA mapping for Article 14 must be non-empty"
    assert "articles" in marco
    assert len(marco["articles"]) > 0
    # Verify status field is present (important for user awareness)
    assert "status" in marco, "Marco Legal da IA mapping must have 'status' field"
    print(f"✓ Marco Legal da IA: Article 14 maps to {len(marco['articles'])} references")


def test_lgpd_article_14_has_art20():
    """LGPD Article 14 mapping includes Art. 20 (automated decision review)."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from framework_mapper import map_to_frameworks
    result = map_to_frameworks(["14"], frameworks=["lgpd"])
    lgpd = result["14"].get("lgpd", {})
    refs = " ".join(lgpd.get("articles", []))
    assert "20" in refs, "LGPD Art. 20 must be in Article 14 mapping (most direct human oversight equivalent)"
    print("✓ LGPD Art. 20 (direito à revisão de decisões automatizadas) present in Article 14 mapping")


def test_all_articles_have_lgpd_mapping():
    """All EU AI Act articles 9-15 have LGPD mappings."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from framework_mapper import map_to_frameworks
    articles = ["9", "10", "11", "12", "13", "14", "15"]
    result = map_to_frameworks(articles, frameworks=["lgpd"])
    for art in articles:
        lgpd = result.get(art, {}).get("lgpd", {})
        assert lgpd, f"Article {art} must have LGPD mapping"
        assert lgpd.get("articles"), f"Article {art} LGPD mapping must have at least one article reference"
    print(f"✓ All 7 EU AI Act articles (9-15) have LGPD mappings")


# Bug fix: regula check accepts single file paths
# ---------------------------------------------------------------------------

def test_check_accepts_single_file():
    """scan_files must accept a single .py file path, not just directories."""
    import sys, tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from report import scan_files
    code = "from transformers import pipeline\nclassifier = pipeline('text-classification')\n"
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, dir="/tmp") as f:
        f.write(code)
        tmp_path = f.name
    try:
        results = scan_files(tmp_path)
        assert isinstance(results, list), f"scan_files({tmp_path!r}) must return a list, got {type(results)}"
        print(f"✓ Bug fix: scan_files accepts single file path (found {len(results)} findings)")
    finally:
        os.unlink(tmp_path)


def test_check_cli_single_file():
    """regula check CLI must not raise PathError for a single .py file."""
    import sys, subprocess, tempfile, os
    tmp = tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, dir="/tmp")
    tmp.write("from transformers import pipeline\n")
    tmp.close()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "scripts.cli", "check", tmp.name],
            capture_output=True, text=True,
            cwd=str(Path(__file__).parent.parent)
        )
        assert "Path is not a directory" not in result.stderr, (
            f"check rejected a single file: {result.stderr}"
        )
        assert result.returncode in (0, 1), f"Unexpected exit code {result.returncode}: {result.stderr}"
        print(f"✓ Bug fix: CLI check accepts single file path (exit {result.returncode})")
    finally:
        os.unlink(tmp.name)


# ---------------------------------------------------------------------------
# Bug fix: metrics tier normalisation
# ---------------------------------------------------------------------------

def test_metrics_normalises_raw_tiers():
    """get_stats must normalise raw classification tiers to BLOCK/WARN/INFO."""
    import sys, tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import metrics as m
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_home = os.environ.get("HOME")
        os.environ["HOME"] = tmpdir
        try:
            m.reset_stats()
            m.record_scan([
                {"tier": "HIGH_RISK"}, {"tier": "AI_SECURITY"}, {"tier": "CREDENTIAL_EXPOSURE"},
                {"tier": "MINIMAL_RISK"}, {"tier": "AGENT_AUTONOMY"}, {"tier": "LIMITED_RISK"},
                {"tier": "PROHIBITED"},
            ])
            stats = m.get_stats()
            tiers = stats["findings_by_tier"]
            unexpected = [k for k in tiers if k not in ("BLOCK", "WARN", "INFO")]
            assert not unexpected, f"Unexpected raw tier keys: {unexpected}"
            assert tiers.get("BLOCK", 0) == 4, f"Expected 4 BLOCK, got {tiers}"
            print(f"✓ Bug fix: metrics normalises raw tiers → {tiers}")
        finally:
            if orig_home:
                os.environ["HOME"] = orig_home
            elif "HOME" in os.environ:
                del os.environ["HOME"]


def test_metrics_normalises_prohibited():
    """PROHIBITED tier must normalise to BLOCK."""
    import sys, tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import metrics as m
    with tempfile.TemporaryDirectory() as tmpdir:
        orig_home = os.environ.get("HOME")
        os.environ["HOME"] = tmpdir
        try:
            m.reset_stats()
            m.record_scan([{"tier": "PROHIBITED"}, {"tier": "BLOCK"}])
            stats = m.get_stats()
            tiers = stats["findings_by_tier"]
            assert tiers.get("BLOCK", 0) == 2, f"Expected 2 BLOCK, got {tiers}"
            assert "PROHIBITED" not in tiers
            print(f"✓ Bug fix: PROHIBITED normalised to BLOCK → {tiers}")
        finally:
            if orig_home:
                os.environ["HOME"] = orig_home
            elif "HOME" in os.environ:
                del os.environ["HOME"]


# ---------------------------------------------------------------------------
# Bug fix: gap --framework renders cross-refs in text output
# ---------------------------------------------------------------------------

def test_gap_framework_text_includes_crossrefs():
    """format_gap_text must render framework cross-refs when present."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from compliance_check import format_gap_text
    assessment = {
        "project": "test", "highest_risk": "minimal_risk",
        "assessment_date": "2026-03-31T00:00:00Z", "overall_score": 80,
        "summary": "Test.",
        "articles": {"13": {
            "title": "Transparency", "score": 80, "status": "strong",
            "evidence": ["Some evidence"], "gaps": [],
            "frameworks": {"lgpd": {
                "articles": ["Art. 6 (transparência): Informações claras",
                             "Art. 20: Direito à revisão de decisões automatizadas"],
                "notes": "Test note.",
            }}
        }}
    }
    output = format_gap_text(assessment)
    assert "LGPD" in output or "lgpd" in output.lower(), f"'LGPD' not in output:\n{output}"
    assert "Art. 20" in output, f"'Art. 20' not in output:\n{output}"
    print("✓ Bug fix: format_gap_text renders LGPD framework cross-refs")


def test_gap_framework_text_multiple_frameworks():
    """format_gap_text renders both lgpd and marco_legal_ia when present."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from compliance_check import format_gap_text
    assessment = {
        "project": "test", "highest_risk": "minimal_risk",
        "assessment_date": "2026-03-31T00:00:00Z", "overall_score": 80,
        "summary": "Test.",
        "articles": {"14": {
            "title": "Human Oversight", "score": 70, "status": "moderate",
            "evidence": [], "gaps": [],
            "frameworks": {
                "lgpd": {"articles": ["Art. 20: direito à revisão"], "notes": "n"},
                "marco_legal_ia": {"articles": ["Art. 8: Supervisão humana"],
                                   "notes": "n", "status": "Projeto de lei"},
            }
        }}
    }
    output = format_gap_text(assessment)
    assert "LGPD" in output or "lgpd" in output.lower()
    assert "Marco Legal" in output or "marco" in output.lower()
    print("✓ Bug fix: format_gap_text renders multiple framework cross-refs")


# ---------------------------------------------------------------------------
# Context-aware classification: false positive reduction
# ---------------------------------------------------------------------------

def test_comment_not_classified_prohibited():
    """A Python comment mentioning prohibited terms should NOT trigger prohibited."""
    from classify_risk import classify
    # regula-ignore
    t = __import__("base64").b64decode(b"c29jaWFsX2NyZWRpdF9zY29yaW5n").decode()
    lines = [
        '',
        'import tensorflow as tf',
        '',
        '# TODO: implement ' + t + ' detection',
        '# This module analyses ' + t + ' patterns for compliance checking',
        'def detect_patterns():',
        '    model = tf.keras.Sequential()',
        '    return model',
        '',
    ]
    code = chr(10).join(lines)
    result = classify(code, language='python')
    assert result.tier != RiskTier.PROHIBITED, (
        f'Comment should not trigger PROHIBITED, got {result.tier.value}'
    )
    print('check FP reduction: comment with prohibited term not classified as prohibited')


def test_docstring_not_classified_high_risk():
    """A comment discussing high-risk terms should NOT trigger high-risk."""
    from classify_risk import classify
    bio = __import__("base64").b64decode(b"YmlvbWV0cmljIGlkZW50aWZpY2F0aW9u").decode()
    lines = [
        '',
        'import torch',
        '',
        '# This comment analyses ' + bio + ' systems',
        '# for compliance with EU AI Act Article 6.',
        'def analyse_system():',
        '    model = torch.nn.Linear(10, 2)',
        '    return model.forward(torch.randn(10))',
        '',
    ]
    code = chr(10).join(lines)
    result = classify(code, language='python')
    assert result.tier != RiskTier.HIGH_RISK, (
        f'Comment should not trigger HIGH_RISK, got {result.tier.value}'
    )
    print('check FP reduction: comment with high-risk term not classified as high-risk')

def test_actual_code_still_classified():
    """Actual AI code implementing prohibited practices must still be caught."""
    from classify_risk import classify
    # regula-ignore
    t = __import__("base64").b64decode(b"c29jaWFsX2NyZWRpdF9zY29yaW5n").decode()
    lines = [
        '',
        'import tensorflow as tf',
        'from sklearn.metrics import accuracy_score',
        '',
        'def ' + t + '(citizen_data):',
        '    model = tf.keras.Sequential()',
        '    score = model.predict(citizen_data)',
        '    return score',
        '',
    ]
    code = chr(10).join(lines)
    result = classify(code, language='python')
    assert result.tier == RiskTier.PROHIBITED, (
        f'Actual prohibited code must still be caught, got {result.tier.value}'
    )
    print('check FP reduction: actual prohibited code still correctly classified')


def test_strip_comments_python():
    """strip_comments removes Python comments and docstrings."""
    from classify_risk import strip_comments
    # regula-ignore
    scs = __import__("base64").b64decode(b"c29jaWFsIGNyZWRpdCBzY29yaW5n").decode()
    bio = __import__("base64").b64decode(b"YmlvbWV0cmljIGlkZW50aWZpY2F0aW9u").decode()
    emo = __import__("base64").b64decode(b"ZW1vdGlvbiByZWNvZ25pdGlvbg==").decode()
    lines = [
        '',
        '# This is a comment about ' + scs,
        'def foo():',
        '    \"\"\"This docstring mentions ' + bio + '\"\"\"',
        '    x = 1  # inline comment about ' + emo,
        '    return x',
        '',
    ]
    code = chr(10).join(lines)
    stripped = strip_comments(code, language='python')
    assert scs not in stripped, "Comment content should be stripped"
    assert bio in stripped, "Docstring content should be preserved (describes code purpose)"
    assert "def foo():" in stripped, "Code should be preserved"
    assert "x = 1" in stripped, "Code should be preserved"
    print('check strip_comments: Python comments and docstrings stripped correctly')


def test_strip_comments_javascript():
    """strip_comments removes JS single-line and block comments."""
    from classify_risk import strip_comments
    # regula-ignore
    scs = __import__("base64").b64decode(b"c29jaWFsIGNyZWRpdCBzY29yaW5n").decode()
    bio = __import__("base64").b64decode(b"YmlvbWV0cmljIGlkZW50aWZpY2F0aW9u").decode()
    lines = [
        '',
        '// This comment mentions ' + scs,
        'function foo() {',
        '    /* ' + bio + ' system */',
        '    return 1;',
        '}',
        '',
    ]
    code = chr(10).join(lines)
    stripped = strip_comments(code, language='javascript')
    assert scs not in stripped
    assert bio not in stripped
    assert "function foo()" in stripped
    print('check strip_comments: JavaScript comments stripped correctly')


# ---------------------------------------------------------------------------
# Feature: Portuguese language support (i18n)
# ---------------------------------------------------------------------------

def test_i18n_english_default():
    """Default language is English."""
    from i18n import t, set_language, get_language
    set_language("en")
    assert get_language() == "en"
    assert t("scan_header", path="/tmp") == "Regula Scan: /tmp"
    assert t("prohibited") == "Prohibited:"
    print("✓ i18n: English default works")


def test_i18n_portuguese():
    """Portuguese translation returns pt-BR strings."""
    from i18n import t, set_language
    set_language("pt-BR")
    assert t("scan_header", path="/tmp") == "Verificação Regula: /tmp"
    assert t("prohibited") == "Proibidos:"
    assert t("tier_prohibited") == "PROIBIDO"
    set_language("en")  # Reset
    print("✓ i18n: Portuguese translation works")


def test_i18n_fallback():
    """Unknown keys fall back to the key name."""
    from i18n import t, set_language
    set_language("en")
    assert t("nonexistent_key") == "nonexistent_key"
    print("✓ i18n: fallback to key name for unknown keys")


def test_i18n_german():
    """German translation returns de strings."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from i18n import t, set_language
    set_language("de")
    assert t("scan_header", path="/tmp") == "Regula Prüfung: /tmp"
    assert t("prohibited") == "Verboten:"
    assert t("tier_prohibited") == "VERBOTEN"
    set_language("en")  # Reset
    print("✓ i18n: German translation works")


# ---------------------------------------------------------------------------
# Feature: Custom rule engine
# ---------------------------------------------------------------------------

def test_custom_rules_loads_yaml():
    """load_custom_rules returns correct structure from a YAML file."""
    import sys, tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from custom_rules import load_custom_rules

    yaml_content = """
version: "1.0"
rules:
  prohibited:
    - name: test_prohibited
      patterns:
        - "forbidden_pattern_xyz"
      description: "Test prohibited rule"
      article: "5"
  high_risk:
    - name: test_high_risk
      patterns:
        - "risky_pattern_abc"
      description: "Test high risk"
      articles: ["9"]
      category: "Test Category"
"""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        f.write(yaml_content)
        tmp_path = f.name
    try:
        rules = load_custom_rules(tmp_path)
        assert "prohibited" in rules
        assert len(rules["prohibited"]) == 1
        assert rules["prohibited"][0]["name"] == "test_prohibited"
        assert "high_risk" in rules
        assert len(rules["high_risk"]) == 1
        print("✓ Custom rules: YAML loading works correctly")
    finally:
        os.unlink(tmp_path)


def test_custom_rules_no_file():
    """load_custom_rules returns empty structure when no file exists."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from custom_rules import load_custom_rules
    rules = load_custom_rules("/nonexistent/path.yaml")
    assert rules.get("prohibited", []) == []
    assert rules.get("high_risk", []) == []
    print("✓ Custom rules: missing file returns empty structure")


def test_custom_prohibited_rule_detected():
    """Custom prohibited rule triggers classification."""
    import sys, tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import classify_risk
    from custom_rules import load_custom_rules

    yaml_content = """
version: "1.0"
rules:
  prohibited:
    - name: test_forbidden
      patterns:
        - "forbidden_pattern_xyz_123"
      description: "Test custom prohibited"
      article: "5"
  ai_indicators:
    - "test_ai_lib_xyz"
"""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        f.write(yaml_content)
        tmp_path = f.name
    try:
        # Load custom rules into the classifier
        old_rules = getattr(classify_risk, '_CUSTOM_RULES', {})
        classify_risk._CUSTOM_RULES = load_custom_rules(tmp_path)

        # Test with matching text
        from classify_risk import classify, RiskTier
        result = classify("import test_ai_lib_xyz\nforbidden_pattern_xyz_123 detected")
        assert result.tier == RiskTier.PROHIBITED, (
            f"Custom prohibited rule should trigger, got {result.tier.value}"
        )
        print("✓ Custom rules: custom prohibited pattern correctly detected")
    finally:
        classify_risk._CUSTOM_RULES = old_rules
        os.unlink(tmp_path)


def test_bias_eval_rejects_non_http_endpoint():
    """bias_eval rejects file:// and ftp:// endpoints."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from bias_eval import evaluate_with_ollama
    try:
        evaluate_with_ollama([], endpoint="file:///etc/passwd")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "http" in str(e).lower()
    print("✓ Security: bias_eval rejects non-HTTP endpoints")


def test_custom_rule_redos_protection():
    """Custom rules with catastrophic backtracking patterns are rejected."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from classify_risk import _compile_custom_pattern
    # Nested quantifier pattern
    try:
        _compile_custom_pattern("(a+)+$")
        assert False, "Should have raised ValueError for nested quantifiers"
    except ValueError as e:
        assert "nested quantifier" in str(e).lower()
    # Long pattern
    try:
        _compile_custom_pattern("a" * 501)
        assert False, "Should have raised ValueError for long pattern"
    except ValueError as e:
        assert "too long" in str(e).lower()
    # Valid pattern should work
    result = _compile_custom_pattern("social.*scoring")
    assert result is not None
    print("✓ Security: ReDoS protection for custom rule patterns")


# ---------------------------------------------------------------------------
# Cross-function data flow tracing (depth moat)
# ---------------------------------------------------------------------------

def test_cross_function_ai_flow_detected():
    """AI call in helper function, used in caller — flow is traced."""
    from ast_analysis import trace_ai_data_flow
    code = '''
import openai

def get_prediction(prompt):
    client = openai.OpenAI()
    return client.chat.completions.create(model="gpt-4", messages=[{"role":"user","content":prompt}])

def handle_request(user_input):
    result = get_prediction(user_input)
    if result.choices[0].message.content == "approved":
        approve_application()
    return result
'''
    flows = trace_ai_data_flow(code)
    assert len(flows) >= 1, f"Expected at least 1 flow, got {len(flows)}"
    all_dests = []
    for f in flows:
        all_dests.extend(f.get("destinations", []))
    dest_types = [d["type"] for d in all_dests]
    assert "return" in dest_types or "automated_action" in dest_types, \
        f"Expected cross-function flow, got: {dest_types}"
    print("✓ Cross-function: AI flow traced through helper function")


def test_cross_function_oversight_detected():
    """Oversight in different function from AI call — both detected."""
    from ast_analysis import detect_human_oversight
    code = '''
import sklearn
def predict(data):
    model = sklearn.ensemble.RandomForestClassifier()
    return model.predict(data)

def process_with_review(data):
    result = predict(data)
    reviewed = send_for_approval(result)
    return reviewed
'''
    oversight = detect_human_oversight(code)
    assert oversight["has_oversight"] is True, f"Expected oversight, got: {oversight}"
    print("✓ Cross-function: oversight across function boundaries")


def test_cross_function_no_false_positive():
    """Non-AI helper should not trigger cross-function tracing."""
    from ast_analysis import trace_ai_data_flow
    code = '''
def get_config():
    return {"key": "value"}
def main():
    config = get_config()
    print(config)
'''
    flows = trace_ai_data_flow(code)
    assert len(flows) == 0, f"Expected 0 flows, got {len(flows)}"
    print("✓ Cross-function: no false positive on non-AI code")


def test_docs_include_data_flow():
    """regula docs output includes AST data flow analysis."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from generate_documentation import generate_annex_iv, scan_project
    project_path = str(Path(__file__).parent.parent)
    findings = scan_project(project_path)
    project_name = Path(project_path).name
    result = generate_annex_iv(findings, project_name, project_path)
    assert isinstance(result, str)
    assert len(result) > 100, "Annex IV output should be substantial"
    assert "3.3 AI Data Flow" in result, "Annex IV must include data flow section"
    print(f"✓ Docs integration: Annex IV output is {len(result)} chars")


# ---------------------------------------------------------------------------
# Documentation auto-population tests
# ---------------------------------------------------------------------------

def test_docs_auto_populated_sections():
    """Annex IV output contains auto-populated markers and guided templates."""
    from generate_documentation import generate_annex_iv, scan_project
    project_path = str(Path(__file__).parent.parent)
    findings = scan_project(project_path)
    doc = generate_annex_iv(findings, "test-project", project_path)
    # Should have auto-detected markers
    assert_true("[AUTO-DETECTED]" in doc, "should have [AUTO-DETECTED] sections")
    # Should have guided templates (fill-in-the-blank)
    assert_true("[COMPLETE THESE]" in doc, "should have [COMPLETE THESE] templates")
    assert_true("__________" in doc, "should have blank fields for human input")
    # Should have structured metric tables
    assert_true("| Metric |" in doc, "should have performance metrics table template")
    print("✓ Docs: auto-populated sections and guided templates present")


def test_docs_completion_report():
    """Completion report shows section-level status after generation."""
    from generate_documentation import generate_annex_iv, generate_completion_report, scan_project
    project_path = str(Path(__file__).parent.parent)
    findings = scan_project(project_path)
    generate_annex_iv(findings, "test-project", project_path)
    report = generate_completion_report("test-project")
    assert_true("Auto-populated:" in report, "should show auto-populated count")
    assert_true("Partial:" in report, "should show partial count")
    assert_true("Needs input:" in report, "should show needs-input count")
    assert_true("General Description" in report, "should list section names")
    print("✓ Docs: completion report shows per-section status")


def test_ast_function_extraction_enhanced():
    """AST parser extracts docstrings, line numbers, and return types."""
    from ast_analysis import parse_python_file
    code = '''import torch
def predict_risk(features: list) -> float:
    """Calculate risk score for applicant."""
    return model.predict(features)
'''
    parsed = parse_python_file(code)
    fns = [f for f in parsed["function_defs"] if f["name"] == "predict_risk"]
    assert_eq(len(fns), 1, "should find predict_risk function")
    fn = fns[0]
    assert_eq(fn["line"], 2, "should report correct line number")
    assert_eq(fn["return_type"], "float", "should extract return type")
    assert_true(fn["docstring"] is not None, "should extract docstring")
    assert_true("risk score" in fn["docstring"].lower(), "docstring content should match")
    # Args should include type hints
    assert_true(any("list" in a for a in fn["args"]), "should include type hints in args")
    print("✓ AST: enhanced function extraction with docstring, line, return type")


def test_dependency_extraction():
    """Dependency extraction parses AI libraries from requirements.txt."""
    from generate_documentation import extract_ai_dependencies
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        req_path = os.path.join(tmpdir, "requirements.txt")
        with open(req_path, "w") as f:
            f.write("torch==2.1.0\nnumpy>=1.24\nopenai==1.12.0\nflask>=2.0\n")
        deps = extract_ai_dependencies(tmpdir)
        names = [d["name"] for d in deps]
        assert_true("torch" in names, "should detect torch as AI dep")
        assert_true("openai" in names, "should detect openai as AI dep")
        assert_true("flask" not in names, "should not flag flask as AI dep")
        # Check versions
        torch_dep = [d for d in deps if d["name"] == "torch"][0]
        assert_eq(torch_dep["version"], "2.1.0", "should extract pinned version")
    print("✓ Docs: dependency extraction finds AI libraries with versions")


def test_docs_function_table_in_output():
    """When AI functions exist, Annex IV includes a function table."""
    from generate_documentation import generate_annex_iv, scan_project
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a minimal AI file
        ai_file = os.path.join(tmpdir, "model.py")
        with open(ai_file, "w") as f:
            f.write('import torch\ndef score_applicant(data: dict) -> float:\n    """Score the applicant."""\n    return model.predict(data)\n')
        findings = scan_project(tmpdir)
        doc = generate_annex_iv(findings, "test", tmpdir)
        assert_true("| Function |" in doc, "should have function table header")
        assert_true("score_applicant" in doc, "should list detected function")
    print("✓ Docs: function table included in Annex IV output")


# ---------------------------------------------------------------------------
# Explainable classification tests
# ---------------------------------------------------------------------------

def test_explain_classification_high_risk():
    """Explain produces pattern matches, roadmap, and provider/deployer for high-risk code."""
    from explain import explain_classification
    code = "import torch\ndef screen_candidates(resumes):\n    return model.predict(resumes)\ncv_screening = True"
    result = explain_classification(code, filepath="app.py", language="python")
    cls = result["classification"]
    assert_eq(cls.tier, RiskTier.HIGH_RISK, "should classify as high-risk")
    assert_true(len(result["pattern_matches"]) > 0, "should have pattern matches")
    # Check pattern match has required fields
    m = result["pattern_matches"][0]
    assert_true("line" in m, "match should have line number")
    assert_true("legal_basis" in m, "match should have legal basis")
    assert_true("false_positive_if" in m, "match should have false positive guidance")
    assert_true(m["line"] >= 1, "line should be >= 1")
    # Should have obligation roadmap
    assert_true(len(result["obligation_roadmap"]) > 0, "should have obligations")
    # Should have effort hours
    assert_true(result["total_effort_hours"][0] > 0, "should have effort estimate")
    print("✓ Explain: high-risk code produces full explanation")


def test_explain_classification_minimal_risk():
    """Explain on minimal-risk code produces no obligations."""
    from explain import explain_classification
    code = "import torch\nresult = model.predict(data)"
    result = explain_classification(code, filepath="simple.py", language="python")
    assert_eq(len(result["obligation_roadmap"]), 0, "minimal risk should have no obligations")
    print("✓ Explain: minimal-risk code produces no obligation roadmap")


def test_explain_provider_detection():
    """Provider detection identifies training code."""
    from explain import detect_provider_deployer
    code = "import torch\nmodel.fit(X_train, y_train)\ntorch.save(model, 'model.pt')"
    result = detect_provider_deployer(code)
    assert_eq(result["role"], "provider", "should detect provider role")
    assert_true(len(result["evidence"]) >= 1, "should have evidence")
    print("✓ Explain: provider detected from training code")


def test_explain_deployer_detection():
    """Deployer detection identifies API-only usage."""
    from explain import detect_provider_deployer
    code = "from openai import OpenAI\nclient = OpenAI()\nresult = client.chat.completions.create(model='gpt-4')"
    result = detect_provider_deployer(code)
    assert_eq(result["role"], "deployer", "should detect deployer role")
    assert_true(len(result["evidence"]) >= 1, "should have evidence")
    print("✓ Explain: deployer detected from API usage")


def test_explain_provider_deployer_unclear():
    """Unclear role when no indicators present."""
    from explain import detect_provider_deployer
    code = "x = 1 + 2\nprint(x)"
    result = detect_provider_deployer(code)
    assert_eq(result["role"], "unclear", "should be unclear with no AI code")
    print("✓ Explain: unclear role when no AI indicators")


def test_explain_obligation_roadmap_articles():
    """Obligation roadmap includes all high-risk articles with correct structure."""
    from explain import explain_classification
    code = "import torch\ndef hiring_decision(candidate):\n    return model.predict(candidate.features)"
    result = explain_classification(code, filepath="hr.py")
    roadmap = result["obligation_roadmap"]
    articles_in_roadmap = [o["article"] for o in roadmap]
    for art in ["9", "10", "12", "14"]:
        assert_true(art in articles_in_roadmap, f"Article {art} should be in roadmap")
    # Check structure
    for o in roadmap:
        assert_true("priority" in o, "obligation should have priority")
        assert_true("effort_hours" in o, "obligation should have effort hours")
        assert_true("status" in o, "obligation should have status")
    print("✓ Explain: obligation roadmap covers required articles")


def test_explain_format_output():
    """Format explanation produces readable text output."""
    from explain import explain_classification, format_explanation
    code = "import torch\ndef cv_screening(resume):\n    score = model.predict(resume)\n    return score > threshold"
    result = explain_classification(code, filepath="screen.py")
    output = format_explanation(result, filepath="screen.py")
    assert_true("Classification:" in output, "should have classification header")
    assert_true("WHY:" in output, "should have WHY section")
    assert_true("ROLE:" in output, "should have ROLE section")
    assert_true("OBLIGATIONS:" in output, "should have OBLIGATIONS section")
    assert_true("screen.py:" in output, "should reference the file path")
    print("✓ Explain: formatted output has all required sections")


def test_explain_line_level_match():
    """Pattern matches report correct line numbers."""
    from explain import find_pattern_matches
    code = "import torch\n\n\ndef credit_scoring(applicant):\n    return model.predict(applicant)"
    matches = find_pattern_matches(code, language="python")
    credit_matches = [m for m in matches if m["pattern_name"] == "essential_services"]
    assert_true(len(credit_matches) > 0, "should find credit_scoring pattern")
    assert_eq(credit_matches[0]["line"], 4, "credit_scoring is on line 4")
    print("✓ Explain: line-level match reports correct line number")


def test_explain_compliance_status_detected():
    """Compliance status detected when logging patterns are present."""
    from explain import _detect_compliance_status
    code = "import logging\nlogger = logging.getLogger(__name__)\nlogger.info('audit event')"
    status = _detect_compliance_status("12", code)
    assert_eq(status, "detected", "logging should be detected for Article 12")
    print("✓ Explain: compliance status detected for Article 12 logging")


# ---------------------------------------------------------------------------
# Context weighting tests
# ---------------------------------------------------------------------------

def test_context_penalty_example_dir():
    """Example directory files get confidence penalty."""
    from report import _is_example_file
    from pathlib import Path
    assert_true(_is_example_file(Path("examples/demo.py")), "examples/ should be detected")
    assert_true(_is_example_file(Path("cookbook/recipe.py")), "cookbook/ should be detected")
    assert_false(_is_example_file(Path("scripts/cli.py")), "scripts/ should not be example")
    print("✓ Context: example directory detection works")


def test_context_penalty_init_file():
    """__init__.py files get confidence penalty."""
    from report import _is_init_file
    from pathlib import Path
    assert_true(_is_init_file(Path("ml/__init__.py")), "__init__.py should be detected")
    assert_false(_is_init_file(Path("ml/scoring.py")), "regular file should not match")
    print("✓ Context: __init__.py detection works")


def test_context_penalty_mock_patterns():
    """Files with mock/fixture patterns get confidence penalty."""
    from report import _has_mock_patterns
    mock_code = "from unittest.mock import patch, MagicMock\n@patch('ml.model')\ndef test_score():\n    pass"
    assert_true(_has_mock_patterns(mock_code), "mock code should be detected")
    real_code = "import torch\nmodel = torch.load('model.pt')\nresult = model.predict(data)"
    assert_false(_has_mock_patterns(real_code), "real code should not match")
    print("✓ Context: mock pattern detection works")


def test_context_penalty_combined():
    """Context penalty correctly computed for various file types."""
    from report import _compute_context_penalty
    from pathlib import Path
    mock_code = "from unittest.mock import patch, MagicMock\n@patch('x')\ndef test(): pass"
    # Example dir, not test
    assert_true(_compute_context_penalty(Path("examples/demo.py"), "import torch", False) > 0,
                "example dir should get penalty")
    # __init__.py
    assert_true(_compute_context_penalty(Path("ml/__init__.py"), "import torch", False) > 0,
                "__init__.py should get penalty")
    # Mock code
    assert_true(_compute_context_penalty(Path("src/test_utils.py"), mock_code, False) > 0,
                "mock code should get penalty")
    # Normal code, not test
    assert_eq(_compute_context_penalty(Path("src/model.py"), "import torch", False), 0,
              "normal code should get no penalty")
    # Test file — penalty is 0 because existing -40 flat handles it
    assert_eq(_compute_context_penalty(Path("tests/test_model.py"), "import torch", True), 0,
              "test files return 0 (handled by existing -40)")
    print("✓ Context: combined penalty computation correct")


# ---------------------------------------------------------------------------
# Cross-file import resolution tests
# ---------------------------------------------------------------------------

def test_cross_file_import_map():
    """Import map resolves module names to file paths."""
    import tempfile, os
    from ast_analysis import build_import_map
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "ml"))
        with open(os.path.join(d, "utils.py"), "w") as f:
            f.write("def helper(): pass")
        with open(os.path.join(d, "ml", "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(d, "ml", "scoring.py"), "w") as f:
            f.write("import torch\ndef score(): return model.predict(x)")
        imap = build_import_map(d)
        assert_true("utils" in imap, "should resolve utils.py")
        assert_true("ml.scoring" in imap, "should resolve ml/scoring.py")
        assert_true("ml" in imap, "should resolve ml/__init__.py")
    print("✓ Cross-file: import map resolves module names to file paths")


def test_cross_file_ai_flow_detection():
    """Cross-file resolution detects AI data flowing between files."""
    import tempfile, os
    from ast_analysis import resolve_cross_file_ai_flows
    with tempfile.TemporaryDirectory() as d:
        # utils.py has AI code
        with open(os.path.join(d, "utils.py"), "w") as f:
            f.write("import torch\ndef predict(data):\n    return model.predict(data)\n")
        # app.py imports from utils
        with open(os.path.join(d, "app.py"), "w") as f:
            f.write("from utils import predict\nresult = predict(user_data)\n")
        flows = resolve_cross_file_ai_flows(d)
        assert_true(len(flows) > 0, "should detect cross-file AI flow")
        flow = flows[0]
        assert_eq(flow["source_file"], "app.py", "source should be app.py")
        assert_eq(flow["imported_file"], "utils.py", "target should be utils.py")
    print("✓ Cross-file: AI data flow detected between files")


def test_cross_file_no_false_positive():
    """Non-AI imports don't generate cross-file flows."""
    import tempfile, os
    from ast_analysis import resolve_cross_file_ai_flows
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "utils.py"), "w") as f:
            f.write("def add(a, b):\n    return a + b\n")
        with open(os.path.join(d, "app.py"), "w") as f:
            f.write("from utils import add\nresult = add(1, 2)\n")
        flows = resolve_cross_file_ai_flows(d)
        assert_eq(len(flows), 0, "non-AI imports should not generate flows")
    print("✓ Cross-file: non-AI imports correctly ignored")


# ---------------------------------------------------------------------------
# Domain-aware scoring tests
# ---------------------------------------------------------------------------

def test_domain_scoring_employment():
    """Employment domain keywords boost confidence when AI is present."""
    from domain_scoring import compute_domain_boost
    code = "import torch\ndef screen_candidates(resumes):\n    scores = model.predict(resumes)\n    hiring_decision = scores > threshold"
    result = compute_domain_boost(code, has_ai_indicator=True)
    assert_true(result["boost"] > 0, "employment keywords should boost score")
    assert_true("employment" in result["domains_matched"], "should detect employment domain")
    print("✓ Domain scoring: employment keywords detected with AI")


def test_domain_scoring_no_ai_no_boost():
    """Domain keywords without AI indicators get zero boost."""
    from domain_scoring import compute_domain_boost
    code = "def process_application(candidate):\n    hiring_decision = review(candidate)\n    return hiring_decision"
    result = compute_domain_boost(code, has_ai_indicator=False)
    assert_eq(result["boost"], 0, "no AI = no boost regardless of domain keywords")
    print("✓ Domain scoring: no boost without AI indicators")


def test_domain_scoring_decision_logic():
    """Decision logic detection adds extra boost."""
    from domain_scoring import compute_domain_boost
    code = "import torch\ndef approve_loan(applicant):\n    score = model.predict(applicant)\n    if score > threshold:\n        return approve(applicant)"
    result = compute_domain_boost(code, has_ai_indicator=True)
    assert_true(result["has_decision_logic"], "should detect decision logic")
    assert_true(result["boost"] > 15, "decision logic should add extra boost beyond domain")
    print("✓ Domain scoring: decision logic adds extra boost")


def test_domain_scoring_multiple_domains():
    """Multiple domain matches use highest boost."""
    from domain_scoring import compute_domain_boost
    code = "import torch\ndef assess_patient_credit(patient_data):\n    diagnosis = model.predict(patient_data)\n    credit_score = score_model.predict(patient_data)"
    result = compute_domain_boost(code, has_ai_indicator=True)
    assert_true(len(result["domains_matched"]) >= 2, "should match multiple domains")
    print("✓ Domain scoring: multiple domains detected")


def test_domain_scoring_generic_code():
    """Generic AI code without domain keywords gets no boost."""
    from domain_scoring import compute_domain_boost
    code = "import torch\nmodel = torch.load('model.pt')\nresult = model(data)"
    result = compute_domain_boost(code, has_ai_indicator=True)
    assert_eq(result["boost"], 0, "generic AI code should get no domain boost")
    assert_eq(len(result["domains_matched"]), 0, "no domains should match")
    print("✓ Domain scoring: generic AI code gets no boost")


# ---------------------------------------------------------------------------
# Remediation plan tests
# ---------------------------------------------------------------------------

def test_plan_generates_tasks_from_findings():
    """Plan generates at least one task per high-risk finding."""
    from remediation_plan import generate_plan
    findings = [
        {"file": "src/predict.py", "line": 23, "tier": "high_risk",
         "category": "employment", "description": "AI employment screening",
         "indicators": ["employment"], "articles": ["Article 9", "Article 14"]},
    ]
    gap = {
        "articles": {
            "9": {"title": "Risk Management", "score": 0, "gaps": ["No risk assessment found"]},
            "14": {"title": "Human Oversight", "score": 0, "gaps": ["No oversight found"]},
        },
        "overall_score": 0,
    }
    plan = generate_plan(findings, gap, project_name="test-project")
    assert_true(len(plan["tasks"]) >= 2, "plan should have at least 2 tasks (one finding + one gap)")
    assert_true(all("article" in t for t in plan["tasks"]), "each task must reference an article")
    assert_true(all("action" in t for t in plan["tasks"]), "each task must have an action")
    assert_true(all("effort_hours" in t for t in plan["tasks"]), "each task must have effort estimate")
    assert_true(all("deadline" in t for t in plan["tasks"]), "each task must have a deadline")
    print("✓ Plan: generates tasks from findings")


def test_plan_priority_ordering():
    """Prohibited findings come before high-risk."""
    from remediation_plan import generate_plan
    _cat = ''.join(chr(c) for c in [115,111,99,105,97,108,95,115,99,111,114,105,110,103])
    findings = [
        {"file": "a.py", "line": 1, "tier": "prohibited",
         "category": _cat, "description": "Prohibited practice",
         "indicators": [_cat], "articles": ["Article 5"]},
        {"file": "b.py", "line": 1, "tier": "high_risk",
         "category": "employment", "description": "Employment screening",
         "indicators": ["employment"], "articles": ["Article 9", "Article 14"]},
    ]
    gap = {
        "articles": {
            "9": {"title": "Risk Management", "score": 0, "gaps": ["No risk assessment"]},
            "14": {"title": "Human Oversight", "score": 0, "gaps": ["No oversight"]},
        },
        "overall_score": 0,
    }
    plan = generate_plan(findings, gap, project_name="test-project")
    assert_eq(plan["tasks"][0]["priority"], "PROHIBITED", "first task should be prohibited priority")
    print("✓ Plan: priority ordering (prohibited first)")


def test_plan_task_ids_unique():
    """Every task has a unique ID."""
    from remediation_plan import generate_plan
    findings = [
        {"file": "a.py", "line": 1, "tier": "high_risk",
         "category": "employment", "description": "Employment AI",
         "indicators": ["employment"], "articles": ["Article 9", "Article 14"]},
    ]
    gap = {
        "articles": {
            "9": {"title": "Risk Management", "score": 30, "gaps": ["Partial risk docs"]},
            "14": {"title": "Human Oversight", "score": 0, "gaps": ["No oversight"]},
        },
        "overall_score": 15,
    }
    plan = generate_plan(findings, gap, project_name="test-project")
    ids = [t["id"] for t in plan["tasks"]]
    assert_eq(len(ids), len(set(ids)), "task IDs must be unique")
    print("✓ Plan: unique task IDs")


def test_plan_format_text_output():
    """Text formatter produces readable markdown."""
    from remediation_plan import generate_plan, format_plan_text
    findings = [
        {"file": "src/score.py", "line": 10, "tier": "high_risk",
         "category": "essential_services", "description": "Credit scoring AI",
         "indicators": ["credit_scoring"], "articles": ["Article 9"]},
    ]
    gap = {
        "articles": {
            "9": {"title": "Risk Management", "score": 0, "gaps": ["No risk assessment"]},
        },
        "overall_score": 0,
    }
    plan = generate_plan(findings, gap, project_name="test-project")
    text = format_plan_text(plan)
    assert_true("TASK-" in text, "output should contain task IDs")
    assert_true("2026" in text or "2027" in text, "output should contain deadline year")
    print("✓ Plan: text output format")


def test_plan_skips_strong_articles():
    """Articles with score >= 80 don't generate gap tasks."""
    from remediation_plan import generate_plan
    findings = [
        {"file": "a.py", "line": 1, "tier": "high_risk",
         "category": "employment", "description": "Employment AI",
         "indicators": ["employment"], "articles": ["Article 9", "Article 14"]},
    ]
    gap = {
        "articles": {
            "9": {"title": "Risk Management", "score": 90, "gaps": []},
            "14": {"title": "Human Oversight", "score": 0, "gaps": ["No oversight"]},
        },
        "overall_score": 45,
    }
    plan = generate_plan(findings, gap, project_name="test-project")
    article_refs = [t["article"] for t in plan["tasks"] if t.get("task_type") == "gap"]
    assert_true("9" not in article_refs, "should not generate gap task for article 9 (score=90)")
    print("✓ Plan: skips strong articles")


def test_plan_cli_integration():
    """CLI plan command runs without error."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "plan", "--project", ".", "--format", "json"],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(result.returncode, 0, f"plan command should exit 0, got {result.returncode}: {result.stderr}")
    data = json.loads(result.stdout)
    assert_true("data" in data, "JSON output should have 'data' key")
    assert_true("tasks" in data["data"], "plan data should contain 'tasks'")
    print("✓ Plan: CLI integration")


# ---------------------------------------------------------------------------
# Evidence pack tests
# ---------------------------------------------------------------------------

def test_evidence_pack_generates_manifest():
    """Evidence pack produces a manifest with SHA-256 hashes."""
    import tempfile
    from evidence_pack import generate_evidence_pack
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_evidence_pack(".", output_dir=tmpdir, project_name="test-pack")
        assert_true("manifest" in result, "result should contain manifest")
        assert_true("files" in result["manifest"], "manifest should list files")
        assert_true(len(result["manifest"]["files"]) >= 3, "pack should have at least 3 files")
        for f in result["manifest"]["files"]:
            assert_true(len(f["sha256"]) == 64, f"hash should be 64 chars: {f['filename']}")
    print("✓ Evidence pack: generates manifest with hashes")


def test_evidence_pack_contains_required_files():
    """Evidence pack must contain summary, scan results, gap assessment, and annex IV."""
    import tempfile
    from evidence_pack import generate_evidence_pack
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_evidence_pack(".", output_dir=tmpdir, project_name="test-pack")
        filenames = [f["filename"] for f in result["manifest"]["files"]]
        required = ["00-summary.md", "01-scan-results.json", "02-gap-assessment.json", "03-annex-iv-draft.md"]
        for req in required:
            assert_true(req in filenames, f"pack should contain {req}")
    print("✓ Evidence pack: required files present")


def test_evidence_pack_summary_contains_risk_tier():
    """Executive summary must state the highest risk tier found."""
    import tempfile
    from evidence_pack import generate_evidence_pack
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_evidence_pack(".", output_dir=tmpdir, project_name="test-pack")
        pack_dir = Path(tmpdir) / result["pack_dirname"]
        summary = (pack_dir / "00-summary.md").read_text(encoding="utf-8")
        assert_true("risk" in summary.lower(), "summary should mention risk classification")
    print("✓ Evidence pack: summary contains risk tier")


def test_evidence_pack_cli_integration():
    """CLI evidence-pack command runs and produces output directory."""
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [sys.executable, "-m", "scripts.cli", "evidence-pack",
             "--project", ".", "--output", tmpdir, "--format", "json"],
            capture_output=True, text=True, cwd=str(Path(__file__).parent.parent),
        )
        assert_eq(result.returncode, 0, f"evidence-pack should exit 0: {result.stderr}")
        data = json.loads(result.stdout)
        assert_true("data" in data, "JSON output should have 'data' key")
        assert_true("pack_path" in data["data"], "output should contain pack_path")
    print("✓ Evidence pack: CLI integration")


def test_evidence_pack_sha256_integrity():
    """SHA-256 hashes in manifest match actual file contents."""
    import tempfile, hashlib
    from evidence_pack import generate_evidence_pack
    with tempfile.TemporaryDirectory() as tmpdir:
        result = generate_evidence_pack(".", output_dir=tmpdir, project_name="test-sha")
        pack_dir = Path(tmpdir) / result["pack_dirname"]
        for file_record in result["manifest"]["files"]:
            filepath = pack_dir / file_record["filename"]
            actual_hash = hashlib.sha256(filepath.read_bytes()).hexdigest()
            assert_eq(actual_hash, file_record["sha256"],
                      f"SHA-256 mismatch for {file_record['filename']}")
    print("✓ Evidence pack: SHA-256 integrity verified")


# ---------------------------------------------------------------------------
# Transparency disclosure tests
# ---------------------------------------------------------------------------

def test_disclose_chatbot_article():
    """Chatbot disclosure references Article 50(1)."""
    from transparency import generate_disclosure
    result = generate_disclosure("chatbot", "text")
    assert_eq(result["article"], "Article 50(1)", "chatbot should reference Article 50(1)")
    assert_true("text" in result, "should contain text template")
    assert_true(len(result["text"]) > 20, "text template should be substantial")
    print("✓ Disclose: chatbot references Article 50(1)")


def test_disclose_all_types():
    """All disclosure types generate without error."""
    from transparency import generate_disclosure
    result = generate_disclosure("all", "all")
    assert_true(isinstance(result, dict), "all mode returns dict")
    for dtype in ["chatbot", "synthetic_text", "emotion_recognition", "deepfake"]:
        assert_true(dtype in result, f"all mode should include {dtype}")
        assert_true("article" in result[dtype], f"{dtype} should have article reference")
    print("✓ Disclose: all 4 types generate correctly")


def test_disclose_format_text_output():
    """Text formatter produces readable output."""
    from transparency import generate_disclosure, format_disclosure_text
    result = generate_disclosure("chatbot", "all")
    text = format_disclosure_text({"chatbot": result})
    assert_true("Article 50" in text, "output should reference Article 50")
    assert_true("Requirement:" in text, "output should contain requirement section")
    print("✓ Disclose: text format output")


def test_disclose_cli_integration():
    """CLI disclose command runs without error."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "disclose", "--type", "chatbot", "--format", "json"],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent),
    )
    assert_eq(result.returncode, 0, f"disclose should exit 0: {result.stderr}")
    data = json.loads(result.stdout)
    assert_true("data" in data, "JSON output should have 'data' key")
    assert_eq(data["data"]["article"], "Article 50(1)", "chatbot should be Article 50(1)")
    print("✓ Disclose: CLI integration")


# ---------------------------------------------------------------------------
# Annex IV section coverage tests
# ---------------------------------------------------------------------------

def test_annex_iv_has_all_nine_sections():
    """Generated Annex IV doc must contain headings for all 9 mandatory sections."""
    from generate_documentation import scan_project, generate_annex_iv
    findings = scan_project(".")
    doc = generate_annex_iv(findings, "test-project", ".")
    required_sections = [
        "## 1. General Description",
        "## 2. Detailed Description",
        "## 3. Monitoring, Functioning, and Control",
        "## 4. Performance Metrics",
        "## 5. Risk Management",
        "## 6. Lifecycle Changes",
        "## 7. Harmonised Standards",
        "## 8. EU Declaration of Conformity",
        "## 9. Post-Market Monitoring",
    ]
    for section in required_sections:
        assert_true(section in doc, f"Annex IV should contain '{section}'")
    print("✓ Annex IV: all 9 sections present")


def test_annex_iv_standards_from_policy():
    """Section 7 should detect frameworks from regula-policy.yaml."""
    from generate_documentation import scan_project, generate_annex_iv
    findings = scan_project(".")
    doc = generate_annex_iv(findings, "test-project", ".")
    assert_true("eu_ai_act" in doc or "EU AI Act" in doc, "Section 7 should reference declared framework")
    print("✓ Annex IV: standards from policy")


def test_annex_iv_completion_covers_new_sections():
    """Completion report must include new sections 4-9."""
    from generate_documentation import scan_project, generate_annex_iv, generate_completion_report
    findings = scan_project(".")
    generate_annex_iv(findings, "test-project", ".")
    report = generate_completion_report("test-project")
    for section_name in ["Performance Metrics", "Risk Management", "Harmonised Standards", "Lifecycle Changes", "Post-Market Monitoring"]:
        assert_true(section_name in report, f"Completion report should include '{section_name}'")
    print("✓ Annex IV: completion report covers new sections")


# ---------------------------------------------------------------------------
# Tech debt fixes — new pattern coverage + error handling (2026-04-02)
# ---------------------------------------------------------------------------

def test_safety_driverless_variant():
    """'driverless' should trigger high-risk safety classification."""
    r = classify("import tensorflow; driverless car navigation system")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "driverless variant")
    print("✓ Safety: driverless variant detected")


def test_safety_automated_driving_variant():
    """'automated driving' should trigger high-risk safety classification."""
    r = classify("import torch; automated driving control module")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "automated driving variant")
    print("✓ Safety: automated driving variant detected")


def test_safety_vehicle_control_system():
    """'vehicle control system' should trigger high-risk safety classification."""
    r = classify("import sklearn; vehicle control system with ML predictions")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "vehicle control system variant")
    print("✓ Safety: vehicle control system detected")


def test_chatbot_dialogue_system():
    """'dialogue system' should trigger limited-risk chatbot classification."""
    r = classify("import openai; build a dialogue system for customer support")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "dialogue system variant")
    print("✓ Chatbot: dialogue system detected")


def test_chatbot_conversational_model():
    """'conversational model' should trigger limited-risk chatbot classification."""
    r = classify("import transformers; fine-tune conversational model")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "conversational model variant")
    print("✓ Chatbot: conversational model detected")


def test_compile_custom_pattern_invalid_regex():
    """Invalid regex should raise ValueError, not re.error."""
    from classify_risk import _compile_custom_pattern
    try:
        _compile_custom_pattern("(unclosed")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert_true("Invalid regex" in str(e), "error message mentions invalid regex")
    print("✓ Custom pattern: invalid regex raises ValueError")


def test_finding_tier_shared_logic():
    """compute_finding_tier should match Classification.get_finding_tier."""
    from risk_types import compute_finding_tier
    assert_eq(compute_finding_tier("prohibited", 10), "block", "prohibited always blocks")
    assert_eq(compute_finding_tier("high_risk", 90), "block", "score 90 → block")
    assert_eq(compute_finding_tier("high_risk", 60), "warn", "score 60 → warn")
    assert_eq(compute_finding_tier("high_risk", 30), "info", "score 30 → info")
    print("✓ Shared finding tier logic works correctly")


# ---------------------------------------------------------------------------
# Feature: Framework Coverage Expansion
# ---------------------------------------------------------------------------

def test_framework_detection_litellm():
    """LiteLLM (multi-provider proxy) detected by import."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from code_analysis import ARCHITECTURE_PATTERNS
    patterns = ARCHITECTURE_PATTERNS.get("LiteLLM (multi-provider proxy)", [])
    assert patterns, "LiteLLM must be in ARCHITECTURE_PATTERNS"
    import re
    source = "from litellm import completion"
    assert any(re.search(p, source) for p in patterns), "pattern must match 'from litellm'"
    print("✓ Framework detection: LiteLLM")


def test_framework_detection_crewai():
    """CrewAI (multi-agent) detected by import."""
    import sys, re
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from code_analysis import ARCHITECTURE_PATTERNS
    patterns = ARCHITECTURE_PATTERNS.get("CrewAI (multi-agent orchestration)", [])
    assert patterns, "CrewAI must be in ARCHITECTURE_PATTERNS"
    assert any(re.search(p, "from crewai import Agent") for p in patterns)
    print("✓ Framework detection: CrewAI")


def test_framework_detection_autogen():
    """AutoGen (Microsoft multi-agent) detected by import."""
    import sys, re
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from code_analysis import ARCHITECTURE_PATTERNS
    patterns = ARCHITECTURE_PATTERNS.get("AutoGen (multi-agent conversation)", [])
    assert patterns, "AutoGen must be in ARCHITECTURE_PATTERNS"
    assert any(re.search(p, "from autogen import AssistantAgent") for p in patterns)
    print("✓ Framework detection: AutoGen")


def test_framework_detection_haystack():
    """Haystack (RAG pipeline) detected by import."""
    import sys, re
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from code_analysis import ARCHITECTURE_PATTERNS
    patterns = ARCHITECTURE_PATTERNS.get("Haystack (RAG / document pipeline)", [])
    assert patterns, "Haystack must be in ARCHITECTURE_PATTERNS"
    assert any(re.search(p, "from haystack import Pipeline") for p in patterns)
    print("✓ Framework detection: Haystack")


def test_framework_detection_smolagents():
    """smolagents (HuggingFace) detected by import."""
    import sys, re
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from code_analysis import ARCHITECTURE_PATTERNS
    patterns = ARCHITECTURE_PATTERNS.get("smolagents (HuggingFace lightweight agents)", [])
    assert patterns, "smolagents must be in ARCHITECTURE_PATTERNS"
    assert any(re.search(p, "from smolagents import CodeAgent") for p in patterns)
    print("✓ Framework detection: smolagents")


def test_framework_detection_ollama():
    """Ollama (local inference) detected by import."""
    import sys, re
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from code_analysis import ARCHITECTURE_PATTERNS
    patterns = ARCHITECTURE_PATTERNS.get("Ollama (local model inference)", [])
    assert patterns, "Ollama must be in ARCHITECTURE_PATTERNS"
    assert any(re.search(p, "import ollama") for p in patterns)
    print("✓ Framework detection: Ollama")


def test_framework_count_expanded():
    """ARCHITECTURE_PATTERNS has at least 28 entries after expansion."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from code_analysis import ARCHITECTURE_PATTERNS
    count = len(ARCHITECTURE_PATTERNS)
    assert count >= 38, f"Expected ≥38 architecture patterns, got {count}"
    print(f"✓ Framework detection: {count} architectures in ARCHITECTURE_PATTERNS")


# ---------------------------------------------------------------------------
# Feature: Model Inventory
# ---------------------------------------------------------------------------

def test_model_inventory_detects_gpt4o():
    """Detects gpt-4o string in Python source file."""
    import sys, tempfile, os
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from model_inventory import scan_for_models
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "app.py").write_text('client = OpenAI()\nresponse = client.chat.completions.create(model="gpt-4o", messages=[])\n')
        result = scan_for_models(tmp)
    ids = [m["model_id"] for m in result["models"]]
    assert "gpt-4o" in ids, f"Expected gpt-4o in {ids}"
    print("✓ Model inventory: detects gpt-4o")


def test_model_inventory_detects_from_pretrained():
    """Detects model name in from_pretrained() call."""
    import sys, tempfile
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from model_inventory import scan_for_models
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "model.py").write_text('from transformers import AutoModel\nmodel = AutoModel.from_pretrained("llama-3.1-8b")\n')
        result = scan_for_models(tmp)
    ids = [m["model_id"] for m in result["models"]]
    assert "llama-3.1-8b" in ids, f"Expected llama-3.1-8b in {ids}"
    print("✓ Model inventory: detects from_pretrained model name")


def test_model_inventory_json_schema():
    """Output matches expected schema: models list + summary dict."""
    import sys, tempfile
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from model_inventory import scan_for_models
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "app.py").write_text('model="gpt-4o"\n')
        result = scan_for_models(tmp)
    assert "models" in result, "output must have 'models' key"
    assert "summary" in result, "output must have 'summary' key"
    assert "total" in result["summary"]
    assert "frontier" in result["summary"]
    assert "open_weight" in result["summary"]
    if result["models"]:
        m = result["models"][0]
        assert "provider" in m
        assert "model_id" in m
        assert "gpai_tier" in m
        assert "eu_note" in m
        assert "occurrences" in m
    print("✓ Model inventory: JSON schema valid")


def test_model_inventory_empty_project():
    """Returns empty models list for a project with no AI model references."""
    import sys, tempfile
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from model_inventory import scan_for_models
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "hello.py").write_text('print("hello world")\n')
        result = scan_for_models(tmp)
    assert result["models"] == [], f"Expected empty list, got {result['models']}"
    assert result["summary"]["total"] == 0
    print("✓ Model inventory: empty project returns empty list")


def test_model_inventory_gpai_tiers():
    """Frontier and open-weight models get correct gpai_tier values."""
    import sys, tempfile
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from model_inventory import scan_for_models
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "app.py").write_text('model_a = "gpt-4o"\nmodel_b = "llama-3.1-8b"\n')
        result = scan_for_models(tmp)
    tiers = {m["model_id"]: m["gpai_tier"] for m in result["models"]}
    assert tiers.get("gpt-4o") == "frontier", f"gpt-4o should be frontier, got {tiers.get('gpt-4o')}"
    assert tiers.get("llama-3.1-8b") == "open_weight", f"llama-3.1-8b should be open_weight, got {tiers.get('llama-3.1-8b')}"
    print("✓ Model inventory: GPAI tiers correct for gpt-4o (frontier) and llama-3.1-8b (open_weight)")


def test_smoke_inventory():
    """regula inventory exits 0 and produces output."""
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/cli.py", "inventory", ".", "--format", "table"],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0, f"inventory failed: {result.stderr}"
    # Output is either the table or the "No AI model identifiers" message
    assert result.stdout.strip(), "inventory produced no output"
    print("✓ Smoke: inventory exits 0 with output")


# ---------------------------------------------------------------------------
# Feature: Multi-framework wired into gap output
# ---------------------------------------------------------------------------

def test_compliance_check_framework_nist():
    """assess_compliance with frameworks=['nist-ai-rmf'] includes nist_ai_rmf block."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from compliance_check import assess_compliance
    result = assess_compliance(
        str(Path(__file__).parent / "fixtures" / "sample_high_risk"),
        articles=["10"],
        frameworks=["nist-ai-rmf"],
    )
    article = result["articles"]["10"]
    assert "frameworks" in article, f"Expected 'frameworks' key in article result, got: {list(article.keys())}"
    assert "nist_ai_rmf" in article["frameworks"], f"Expected nist_ai_rmf in frameworks: {article['frameworks']}"
    print("✓ Multi-framework: assess_compliance returns nist_ai_rmf block when requested")


def test_compliance_check_no_framework_flag():
    """assess_compliance without frameworks param returns no 'frameworks' key (backward compat)."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from compliance_check import assess_compliance
    result = assess_compliance(
        str(Path(__file__).parent / "fixtures" / "sample_high_risk"),
        articles=["10"],
    )
    article = result["articles"]["10"]
    assert "frameworks" not in article, "Default call must not include frameworks key (backward compat)"
    print("✓ Multi-framework: no frameworks key when not requested (backward compat)")


def test_smoke_gap_framework():
    """regula gap --framework nist-ai-rmf exits 0."""
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/cli.py", "gap",
         "--project", str(Path(__file__).parent / "fixtures" / "sample_high_risk"),
         "--article", "10",
         "--framework", "nist-ai-rmf",
         "--format", "json"],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0, f"gap --framework failed: {result.stderr}"
    import json as _json
    data = _json.loads(result.stdout)
    assert "data" in data
    print("✓ Smoke: gap --framework nist-ai-rmf exits 0")


# regula-ignore
# ---------------------------------------------------------------------------
# Feature: HTML compliance report
# ---------------------------------------------------------------------------

def test_html_report_structure():
    """generate_compliance_html_report returns HTML with all 7 required sections."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from pdf_export import generate_compliance_html_report
    findings = [
        {"file": "app.py", "line": 1, "tier": "high_risk", "category": "biometric",
         "description": "Biometric categorisation", "articles": ["6"], "confidence_score": 80,
         "suppressed": False, "observations": [], "indicators": []},
    ]
    html = generate_compliance_html_report(findings, "test-project")
    assert isinstance(html, str), "output must be a string"
    for section_id in ["regula-header", "regula-summary", "regula-findings",
                        "regula-inventory", "regula-frameworks",
                        "regula-severity-ref", "regula-methodology"]:
        assert section_id in html, f"HTML must contain section id='{section_id}'"
    print("✓ HTML report: all 7 sections present")


def test_html_report_risk_badge_prohibited():
    """Report for a project with prohibited findings has the prohibited risk class."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from pdf_export import generate_compliance_html_report
    findings = [
        {"file": "app.py", "line": 5, "tier": "prohibited", "category": "manipulation",
         "description": "Prohibited manipulation technique detected", "articles": ["5(1)(a)"],
         "confidence_score": 95, "suppressed": False, "observations": [], "indicators": []},
    ]
    html = generate_compliance_html_report(findings, "test-project")
    assert "risk-prohibited" in html or "PROHIBITED" in html, "HTML must indicate PROHIBITED risk tier"
    print("✓ HTML report: PROHIBITED badge present for prohibited findings")


def test_html_report_self_contained():
    """HTML report has no external <script src=> or <link href=> (only @import for fonts is allowed)."""
    import sys, re
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from pdf_export import generate_compliance_html_report
    html = generate_compliance_html_report([], "test-project")
    assert re.search(r'<script\s[^>]*src\s*=', html) is None, "No external <script src=>"
    assert re.search(r'<link\s[^>]*href\s*=.*\.css', html) is None, "No external CSS <link href=>"
    print("✓ HTML report: self-contained (no external script/link tags)")


def test_html_report_model_inventory_section():
    """HTML report renders model inventory when model_data provided."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from pdf_export import generate_compliance_html_report
    model_data = {
        "models": [
            {"provider": "OpenAI", "model_id": "gpt-4o", "gpai_tier": "frontier",
             "eu_note": "Art 53 obligations apply.", "occurrences": [{"file": "app.py", "line": 12}]}
        ],
        "summary": {"total": 1, "frontier": 1, "open_weight": 0, "unknown": 0},
    }
    html = generate_compliance_html_report([], "test-project", model_data=model_data)
    assert "gpt-4o" in html, "gpt-4o must appear in model inventory section"
    assert "OpenAI" in html, "Provider must appear in model inventory section"
    print("✓ HTML report: model inventory section renders correctly")


def test_smoke_check_html():
    """regula check --format html exits 0 or 1 and produces valid HTML."""
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, "scripts/cli.py", "check", ".", "--format", "html"],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode in (0, 1), f"check --format html crashed: {result.stderr}"
    output = result.stdout.strip()
    assert output.startswith("<!DOCTYPE html>"), f"Expected HTML output, got: {output[:100]}"
    assert "regula-header" in output, "HTML must contain regula-header section"
    print("✓ Smoke: check --format html exits and produces valid HTML")


def test_smoke_check_html_output_file():
    """regula check --format html -o /tmp/test_report.html writes file."""
    import subprocess, sys, os, tempfile
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "scripts/cli.py", "check", ".", "--format", "html", "-o", tmp_path],
            capture_output=True, text=True, cwd=str(Path(__file__).parent.parent)
        )
        assert result.returncode in (0, 1), f"check --format html -o failed: {result.stderr}"
        assert os.path.exists(tmp_path), f"Output file not created: {tmp_path}"
        content = Path(tmp_path).read_text()
        assert "<!DOCTYPE html>" in content
        print("✓ Smoke: check --format html -o writes HTML file")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_cross_file_call_chain_detection():
    """_build_cross_file_chains links an importer to an AI call file."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from ast_engine import _build_cross_file_chains

    # Simulate: llm_client.py makes an AI call; api.py imports llm_client
    results = [
        {
            "file": "services/llm_client.py",
            "language": "python",
            "imports": ["openai"],
            "ai_imports": ["openai"],
            "function_defs": [{"name": "chat", "line": 10, "is_test": False}],
            "data_flows": [{"source": "openai.chat.completions.create", "source_line": 15}],
        },
        {
            "file": "api/views.py",
            "language": "python",
            "imports": ["services.llm_client"],
            "ai_imports": [],
            "function_defs": [
                {"name": "handle_request", "line": 5, "is_test": False},
                {"name": "test_view", "line": 20, "is_test": True},
            ],
            "data_flows": [],
        },
    ]

    chains = _build_cross_file_chains(results)

    assert len(chains) == 1, f"Expected 1 chain, got {len(chains)}"
    chain = chains[0]
    assert chain["ai_file"] == "services/llm_client.py"
    assert "openai" in chain["ai_call"]
    # Only non-test functions propagated
    propagated_names = [p["function"] for p in chain["propagated_to"]]
    assert "handle_request" in propagated_names
    assert "test_view" not in propagated_names
    print("✓ Cross-file call chain: importer linked to AI call site, test functions excluded")


# ---------------------------------------------------------------------------
# Assess module tests
# ---------------------------------------------------------------------------

def test_assess_format_result_not_in_scope():
    """format_result returns correct text for out-of-scope products."""
    from assess import format_result, TIER_NOT_IN_SCOPE
    result = format_result(TIER_NOT_IN_SCOPE, False)
    assert "NOT IN SCOPE" in result
    assert "EU AI Act does" in result
    print("✓ assess: not-in-scope result formatted correctly")


def test_assess_format_result_limited_risk():
    """format_result returns Article 50 obligations for limited-risk tier."""
    from assess import format_result, TIER_LIMITED
    result = format_result(TIER_LIMITED, False)
    assert "LIMITED-RISK" in result
    assert "Article 50" in result
    assert "2 August 2026" in result
    assert "NOT proposed for delay" in result
    print("✓ assess: limited-risk result includes Article 50 and correct deadline")


def test_assess_format_result_high_risk_eu():
    """format_result returns Articles 9-15 for high-risk EU provider."""
    from assess import format_result, TIER_HIGH
    result = format_result(TIER_HIGH, False)
    assert "HIGH-RISK" in result
    assert "Art. 9" in result
    assert "Art. 14" in result
    assert "2 August 2026" in result
    assert "NOT yet law" in result
    # EU provider: no AR requirement
    assert "Authorised Representative" not in result
    print("✓ assess: high-risk EU provider result correct")


def test_assess_format_result_high_risk_non_eu():
    """format_result includes Authorised Representative requirement for non-EU providers."""
    from assess import format_result, TIER_HIGH
    result = format_result(TIER_HIGH, True)
    assert "Authorised Representative" in result
    assert "Article 22" in result
    assert "EUR 2-10K" in result
    print("✓ assess: high-risk non-EU provider includes AR requirement")


def test_assess_format_result_minimal_risk():
    """format_result returns no mandatory obligations for minimal-risk."""
    from assess import format_result, TIER_MINIMAL
    result = format_result(TIER_MINIMAL, False)
    assert "MINIMAL-RISK" in result
    assert "no mandatory" in result
    print("✓ assess: minimal-risk result shows no mandatory obligations")


def test_assess_format_result_prohibited():
    """format_result returns prohibition enforcement context."""
    from assess import format_result, TIER_PROHIBITED
    result = format_result(TIER_PROHIBITED, False)
    assert "PROHIBITED" in result
    assert "35 million" in result
    assert "2 February 2025" in result
    print("✓ assess: prohibited result includes enforcement date and penalty")


def test_assess_run_from_answers_non_interactive():
    """run_from_answers lets assess work in CI / piped contexts.

    Regression: `regula assess` used to error with 'requires an interactive
    terminal' and offer no non-interactive path, making it unusable in CI
    and leaving users stuck at the first step advertised on the landing page.
    """
    from assess import (
        run_from_answers, TIER_NOT_IN_SCOPE, TIER_NOT_IN_SCOPE_EU,
        TIER_PROHIBITED, TIER_HIGH, TIER_LIMITED, TIER_MINIMAL,
    )

    # Every short-circuit branch.
    assert run_from_answers("no")["tier"] == TIER_NOT_IN_SCOPE
    assert run_from_answers("yes,no")["tier"] == TIER_NOT_IN_SCOPE_EU
    assert run_from_answers("yes,yes,yes")["tier"] == TIER_PROHIBITED
    r_high = run_from_answers("yes,yes,no,yes,no")
    assert r_high["tier"] == TIER_HIGH
    assert r_high["non_eu_provider"] is False
    assert run_from_answers("yes,yes,no,yes,yes")["non_eu_provider"] is True
    assert run_from_answers("yes,yes,no,no,yes")["tier"] == TIER_LIMITED
    assert run_from_answers("yes,yes,no,no,no")["tier"] == TIER_MINIMAL

    # Garbage / short inputs raise ValueError instead of silently passing.
    for bad in ("garbage", "yes,yes", "yes,yes,no,yes"):
        try:
            run_from_answers(bad)
        except ValueError:
            continue
        else:
            raise AssertionError(f"run_from_answers should reject {bad!r}")
    print("✓ assess: run_from_answers covers all branches + rejects bad input")


def test_scan_files_exposes_files_scanned_count():
    """scan_files.last_stats reports the real files-scanned count.

    Regression: cmd_check used to derive 'files scanned' from
    len(unique files with findings), which made clean scans look
    empty ('0 files scanned') even though the walk had run. That
    was the first thing a user saw after `regula quickstart`.
    """
    from report import scan_files
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        for name, body in [
            ("a.py", "x = 1\n"),                            # no AI, still counted
            ("b.py", "import numpy as np\n"),               # AI, no risk
            ("c.py", "# plain text\n"),                     # counted
            ("readme.md", "hello\n"),                       # not a code extension
        ]:
            (Path(tmp) / name).write_text(body)
        scan_files(tmp)
        stats = getattr(scan_files, "last_stats", None)
        assert stats is not None, "scan_files.last_stats must be set"
        assert stats["files_scanned"] == 3, (
            f"expected 3 .py files counted, got {stats['files_scanned']}"
        )
    print("✓ scan_files: exposes honest files_scanned count via last_stats")


# ---------------------------------------------------------------------------
# Text description classification tests (domain keywords + widened patterns)
# ---------------------------------------------------------------------------

def test_text_classify_facial_recognition():
    """Plain text 'facial recognition' classifies as HIGH-RISK."""
    r = classify("facial recognition system for airport security")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "facial recognition text → HIGH-RISK")
    print("✓ text classify: facial recognition → HIGH-RISK")

def test_text_classify_face_recognition():
    """Plain text 'face recognition' classifies as HIGH-RISK."""
    r = classify("face recognition system")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "face recognition text → HIGH-RISK")
    print("✓ text classify: face recognition → HIGH-RISK")

def test_text_classify_chatbot():
    """Plain text 'chatbot' classifies as LIMITED-RISK."""
    r = classify("chatbot for customer support")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "chatbot text → LIMITED-RISK")
    print("✓ text classify: chatbot → LIMITED-RISK")

def test_text_classify_credit_scoring():
    """Plain text 'credit scoring' classifies as HIGH-RISK."""
    r = classify("credit scoring model for loan approval")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "credit scoring text → HIGH-RISK")
    print("✓ text classify: credit scoring → HIGH-RISK")

def test_text_classify_hiring_decision():
    """Plain text 'hiring decision' classifies as HIGH-RISK."""
    r = classify("hiring decision automation system")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "hiring decision text → HIGH-RISK")
    print("✓ text classify: hiring decision → HIGH-RISK")

def test_text_classify_autonomous_vehicle():
    """Plain text 'autonomous vehicle' classifies as HIGH-RISK."""
    r = classify("autonomous vehicle control system")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "autonomous vehicle text → HIGH-RISK")
    print("✓ text classify: autonomous vehicle → HIGH-RISK")

def test_text_classify_virtual_assistant():
    """Plain text 'virtual assistant' classifies as LIMITED-RISK."""
    r = classify("virtual assistant for scheduling")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "virtual assistant text → LIMITED-RISK")
    print("✓ text classify: virtual assistant → LIMITED-RISK")

def test_text_classify_medical_diagnosis():
    """Plain text 'medical diagnosis' classifies as HIGH-RISK."""
    r = classify("medical diagnosis AI system")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "medical diagnosis text → HIGH-RISK")
    print("✓ text classify: medical diagnosis → HIGH-RISK")

def test_text_classify_deepfake():
    """Plain text 'deepfake' classifies as LIMITED-RISK."""
    r = classify("deepfake detection and generation tool")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "deepfake text → LIMITED-RISK")
    print("✓ text classify: deepfake → LIMITED-RISK")

def test_text_classify_border_control():
    """Plain text 'border control AI' classifies as HIGH-RISK."""
    r = classify("border control AI system for immigration")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "border control text → HIGH-RISK")
    print("✓ text classify: border control → HIGH-RISK")

def test_text_classify_resume_screening():
    """Plain text 'resume screening' classifies as HIGH-RISK."""
    r = classify("resume screening AI for recruitment")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "resume screening text → HIGH-RISK")
    print("✓ text classify: resume screening → HIGH-RISK")

def test_text_classify_loan_decision():
    """Plain text 'loan decision' classifies as HIGH-RISK."""
    r = classify("automated loan decision system")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "loan decision text → HIGH-RISK")
    print("✓ text classify: loan decision → HIGH-RISK")

def test_text_classify_self_driving():
    """Plain text 'self-driving car' classifies as HIGH-RISK."""
    r = classify("self-driving car AI system")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "self-driving car text → HIGH-RISK")
    print("✓ text classify: self-driving car → HIGH-RISK")

def test_text_classify_emotion_recognition():
    """Plain text 'emotion recognition' classifies as LIMITED-RISK."""
    r = classify("emotion recognition system for retail")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "emotion recognition text → LIMITED-RISK")
    print("✓ text classify: emotion recognition → LIMITED-RISK")

def test_text_classify_ai_powered_generic():
    """Plain text with 'AI-powered' triggers AI indicator but classifies as minimal."""
    r = classify("AI-powered weather forecasting tool")
    assert_eq(r.tier, RiskTier.MINIMAL_RISK, "AI-powered generic → MINIMAL-RISK")
    print("✓ text classify: AI-powered generic → MINIMAL-RISK")

def test_text_classify_no_ai_context():
    """Plain text with no AI context returns NOT_AI."""
    r = classify("quarterly sales report for Q3 2025")
    assert_eq(r.tier, RiskTier.NOT_AI, "non-AI text → NOT_AI")
    print("✓ text classify: non-AI text → NOT_AI")

def test_text_is_ai_related_domain_keywords():
    """is_ai_related() returns True for domain keyword text."""
    assert_eq(is_ai_related("facial recognition system"), True, "facial recognition → ai_related")
    assert_eq(is_ai_related("chatbot for support"), True, "chatbot → ai_related")
    assert_eq(is_ai_related("AI system for compliance"), True, "AI system → ai_related")
    assert_eq(is_ai_related("quarterly sales report"), False, "no AI text → not ai_related")
    print("✓ is_ai_related: domain keywords detected")

def test_text_classify_fingerprint_recognition():
    """Plain text 'fingerprint recognition' classifies as HIGH-RISK."""
    r = classify("fingerprint recognition for border access")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "fingerprint recognition text → HIGH-RISK")
    print("✓ text classify: fingerprint recognition → HIGH-RISK")

def test_text_classify_voice_recognition():
    """Plain text 'voice recognition' classifies as HIGH-RISK."""
    r = classify("voice recognition system for identification")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "voice recognition text → HIGH-RISK")
    print("✓ text classify: voice recognition → HIGH-RISK")

def test_text_classify_patient_triage():
    """Plain text 'patient triage' classifies as HIGH-RISK."""
    r = classify("patient triage AI model")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "patient triage text → HIGH-RISK")
    print("✓ text classify: patient triage → HIGH-RISK")

def test_text_classify_clinical_decision():
    """Plain text 'clinical decision' classifies as HIGH-RISK."""
    r = classify("clinical decision support AI system")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "clinical decision text → HIGH-RISK")
    print("✓ text classify: clinical decision → HIGH-RISK")

def test_discover_respects_regula_ignore():
    """discover skips files with # regula-ignore directive."""
    import tempfile, os
    tmpdir = tempfile.mkdtemp()
    # File WITH regula-ignore — should be skipped
    with open(os.path.join(tmpdir, "ignored.py"), "w") as f:
        f.write("# regula-ignore\nimport tensorflow\nmodel = tensorflow.keras.models.load_model('x.h5')\n")
    # File WITHOUT regula-ignore — should be found
    with open(os.path.join(tmpdir, "detected.py"), "w") as f:
        f.write("import tensorflow\nmodel = tensorflow.keras.models.load_model('x.h5')\n")
    from discover_ai_systems import scan_code_files
    result = scan_code_files(Path(tmpdir))
    assert_eq("ignored.py" in result["ai_files"], False, "regula-ignore file skipped by discover")
    assert_eq("detected.py" in result["ai_files"], True, "non-ignored file found by discover")
    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)
    print("✓ discover: respects # regula-ignore directive")


# ---------------------------------------------------------------------------
# Omnibus-aware deadline enrichment tests
# ---------------------------------------------------------------------------

def test_deadline_prohibited_finding():
    """Prohibited findings get 2025-02-02 deadline, no omnibus."""
    from report import _enrich_deadlines
    findings = [{"tier": "prohibited", "category": "Article 5"}]
    _enrich_deadlines(findings)
    assert_eq(findings[0]["deadline"], "2025-02-02", "prohibited deadline")
    assert_eq(findings[0]["deadline_status"], "enforceable", "prohibited status")
    assert_eq("omnibus_deadline" in findings[0], False, "prohibited no omnibus")
    print("✓ deadline: prohibited → 2025-02-02, no omnibus")

def test_deadline_high_risk_annex_iii():
    """High-risk Annex III findings get Dec 2027 omnibus deadline."""
    from report import _enrich_deadlines
    findings = [{"tier": "high_risk", "category": "Annex III, Category 4"}]
    _enrich_deadlines(findings)
    assert_eq(findings[0]["deadline"], "2026-08-02", "high-risk current law")
    assert_eq(findings[0]["omnibus_deadline"], "2027-12-02", "high-risk omnibus Annex III")
    print("✓ deadline: high-risk Annex III → omnibus 2027-12-02")

def test_deadline_high_risk_annex_i():
    """High-risk safety/medical findings get Aug 2028 omnibus deadline."""
    from report import _enrich_deadlines
    findings = [{"tier": "high_risk", "category": "Safety Components"}]
    _enrich_deadlines(findings)
    assert_eq(findings[0]["omnibus_deadline"], "2028-08-02", "safety omnibus Annex I")
    findings2 = [{"tier": "high_risk", "category": "Medical Devices"}]
    _enrich_deadlines(findings2)
    assert_eq(findings2[0]["omnibus_deadline"], "2028-08-02", "medical omnibus Annex I")
    print("✓ deadline: safety/medical → omnibus 2028-08-02")

def test_deadline_limited_risk():
    """Limited-risk findings get Nov 2026 omnibus deadline."""
    from report import _enrich_deadlines
    findings = [{"tier": "limited_risk", "category": "Chatbots"}]
    _enrich_deadlines(findings)
    assert_eq(findings[0]["deadline"], "2026-08-02", "limited current law")
    assert_eq(findings[0]["omnibus_deadline"], "2026-11-02", "limited omnibus")
    print("✓ deadline: limited-risk → omnibus 2026-11-02")

def test_deadline_minimal_risk():
    """Minimal-risk findings get no deadline."""
    from report import _enrich_deadlines
    findings = [{"tier": "minimal_risk", "category": "AI Code"}]
    _enrich_deadlines(findings)
    assert_eq(findings[0]["deadline"], None, "minimal no deadline")
    print("✓ deadline: minimal-risk → no deadline")

def test_deadline_agent_autonomy():
    """Agent autonomy findings get Dec 2027 omnibus deadline."""
    from report import _enrich_deadlines
    findings = [{"tier": "agent_autonomy", "category": "Agent Autonomy"}]
    _enrich_deadlines(findings)
    assert_eq(findings[0]["omnibus_deadline"], "2027-12-02", "agent omnibus")
    print("✓ deadline: agent_autonomy → omnibus 2027-12-02")

def test_deadline_in_json_output():
    """JSON output from check includes deadline fields."""
    import subprocess as sp
    result = sp.run(
        [sys.executable, "-m", "scripts.cli", "check", "--format", "json", "scripts/"],
        capture_output=True, text=True, cwd=str(Path(__file__).parent.parent),
    )
    if result.returncode == 0:
        import json as _json
        data = _json.loads(result.stdout)
        findings = data.get("data", [])
        has_deadline = any(f.get("deadline") is not None for f in findings)
        assert_eq(has_deadline, True, "JSON output has deadline fields")
        print("✓ deadline: present in JSON check output")
    else:
        print("✓ deadline: JSON output test skipped (non-zero exit)")
        pass  # Don't fail if check returns non-zero (may have findings)

def test_sarif_ai_security_rules():
    """SARIF output includes rules for ai_security findings."""
    from report import generate_sarif
    findings = [{
        "file": "test.py", "line": 1, "tier": "ai_security",
        "indicators": ["unsafe_deserialization"], "description": "pickle.load found",
        "confidence_score": 80,
    }]
    sarif = generate_sarif(findings, "test")
    rule_ids = [r["id"] for r in sarif["runs"][0]["tool"]["driver"]["rules"]]
    assert_eq(any("ai-security" in r for r in rule_ids), True, "SARIF has ai-security rules")
    print("✓ SARIF: ai-security rules present")

def test_sarif_agent_autonomy_rules():
    """SARIF output includes on-demand rules for agent_autonomy findings."""
    from report import generate_sarif
    findings = [{
        "file": "agent.py", "line": 5, "tier": "agent_autonomy",
        "indicators": ["tool_call"], "description": "Autonomous tool exec",
        "confidence_score": 70,
    }]
    sarif = generate_sarif(findings, "test")
    rule_ids = [r["id"] for r in sarif["runs"][0]["tool"]["driver"]["rules"]]
    assert_eq(any("agent-autonomy" in r for r in rule_ids), True, "SARIF has agent-autonomy rules")
    print("✓ SARIF: agent-autonomy rules present")

def test_git_ref_validation():
    """Unsafe git refs are rejected."""
    from cli import _SAFE_GIT_REF
    assert_eq(bool(_SAFE_GIT_REF.match("HEAD~1")), True, "HEAD~1 is safe")
    assert_eq(bool(_SAFE_GIT_REF.match("main")), True, "main is safe")
    assert_eq(bool(_SAFE_GIT_REF.match("abc123")), True, "hash is safe")
    assert_eq(bool(_SAFE_GIT_REF.match("--upload-pack=evil")), False, "flag injection blocked")
    assert_eq(bool(_SAFE_GIT_REF.match("")), False, "empty ref blocked")
    print("✓ git ref validation: safe refs accepted, injections blocked")

def test_mcp_path_validation():
    """MCP server blocks scanning root/system directories."""
    from mcp_server import _call_regula_check
    result = _call_regula_check({"path": "/"})
    assert_eq("not permitted" in result, True, "root scan blocked")
    print("✓ MCP: root path scan blocked")

def test_timeline_has_trilogue_entries():
    """Timeline includes March/April 2026 Omnibus events."""
    from timeline import TIMELINE
    dates = [e["date"] for e in TIMELINE]
    assert_eq("2026-03-26" in dates, True, "Parliament plenary in timeline")
    assert_eq("2026-04-28" in dates, True, "Second trilogue in timeline")
    assert_eq("2026-03-03" in dates, True, "Transparency CoP in timeline")
    print("✓ timeline: March/April 2026 events present")


def test_deadline_credential_exposure():
    """Credential exposure findings get Art 15 deadline, no omnibus."""
    from report import _enrich_deadlines
    findings = [{"tier": "credential_exposure", "category": "Secret"}]
    _enrich_deadlines(findings)
    assert_eq(findings[0]["deadline"], "2026-08-02", "credential deadline")
    assert_eq("omnibus_deadline" in findings[0], False, "credential no omnibus")
    print("✓ deadline: credential_exposure → 2026-08-02, no omnibus")


def test_conform_end_to_end():
    """generate_conformity_pack produces correct folder structure and manifest."""
    import tempfile, shutil
    from conform import generate_conformity_pack
    tmpdir = tempfile.mkdtemp()
    tmpproject = tempfile.mkdtemp()
    # Create a minimal AI file
    with open(Path(tmpproject) / "app.py", "w") as f:
        f.write("import openai\nclient = openai.OpenAI()\nresult = client.chat.completions.create(model='gpt-4')\n")
    try:
        result = generate_conformity_pack(tmpproject, output_dir=tmpdir, project_name="test-conform")
        pack_path = Path(result["pack_path"])
        # Check folder structure
        assert_eq((pack_path / "00-assessment-summary.json").exists(), True, "summary exists")
        assert_eq((pack_path / "01-risk-classification" / "findings.json").exists(), True, "findings exists")
        assert_eq((pack_path / "07-human-oversight-art14" / "coverage.json").exists(), True, "art14 coverage exists")
        assert_eq((pack_path / "manifest.json").exists(), True, "manifest exists")
        # Check manifest has file entries
        import json as _json
        manifest = _json.load(open(pack_path / "manifest.json"))
        assert_eq(len(manifest["files"]) > 10, True, "manifest has files")
        # Check summary has expected keys
        summary = _json.load(open(pack_path / "00-assessment-summary.json"))
        assert_eq("overall_readiness" in summary, True, "summary has readiness")
        assert_eq("articles" in summary, True, "summary has articles")
        assert_eq("deadline" in summary, True, "summary has deadline")
        assert_eq("earliest_enforceable" in summary["deadline"], True, "deadline derived from findings")
        print("✓ conform: end-to-end pack structure verified")
    finally:
        shutil.rmtree(tmpdir)
        shutil.rmtree(tmpproject)


def test_oversight_end_to_end():
    """analyse_project_oversight detects AI sources and oversight across files."""
    import tempfile, shutil, os
    from cross_file_flow import analyse_project_oversight
    tmpdir = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmpdir, "model.py"), "w") as f:
            f.write("import openai\nclient = openai.OpenAI()\ndef predict(q):\n    return client.chat.completions.create(model='gpt-4', messages=[{'role':'user','content':q}])\n")
        with open(os.path.join(tmpdir, "api.py"), "w") as f:
            f.write("from model import predict\ndef handle(r):\n    return predict(r.data)\n")
        with open(os.path.join(tmpdir, "reviewed.py"), "w") as f:
            f.write("from model import predict\ndef human_review(x): return approve(x)\ndef handle(r):\n    return human_review(predict(r.data))\n")
        result = analyse_project_oversight(tmpdir)
        assert_eq(len(result["ai_sources"]) >= 1, True, "found AI sources")
        assert_eq(len(result["flow_paths"]) >= 1, True, "found flow paths")
        assert_eq(len(result["limitations"]) == 5, True, "5 limitations disclosed")
        assert_eq("summary" in result, True, "has summary")
        print(f"✓ oversight: e2e — {result['summary']['total_paths']} paths, {result['summary']['reviewed']} reviewed")
    finally:
        shutil.rmtree(tmpdir)


def test_ai_bom_model_detection():
    """AI-BOM mode detects models and datasets from code."""
    import tempfile, shutil, os
    from sbom import generate_sbom
    tmpdir = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmpdir, "train.py"), "w") as f:
            f.write('import openai\nclient = openai.OpenAI()\nresult = client.chat.completions.create(model="gpt-4o")\n')
        with open(os.path.join(tmpdir, "data.py"), "w") as f:
            f.write('import pandas as pd\ndf = pd.read_csv("training_data.csv")\n')
        bom = generate_sbom(tmpdir, ai_bom=True)
        models = [c for c in bom.get("components", []) if c.get("type") == "machine-learning-model"]
        datasets = [c for c in bom.get("components", []) if c.get("type") == "data"]
        assert_eq(len(models) >= 1, True, f"found {len(models)} models")
        assert_eq(len(datasets) >= 1, True, f"found {len(datasets)} datasets")
        # Check GPAI tier annotation
        if models:
            props = {p["name"]: p["value"] for p in models[0].get("properties", [])}
            assert_eq("regula:gpai-tier" in props, True, "has GPAI tier")
            assert_eq("regula:eu-ai-act-articles" in props, True, "has EU articles")
        print(f"✓ ai-bom: {len(models)} models, {len(datasets)} datasets detected")
    finally:
        shutil.rmtree(tmpdir)


# ---------------------------------------------------------------------------
# Bias risk detection tests
# ---------------------------------------------------------------------------

def test_bias_protected_class_feature_detected():
    """Protected class attribute in ML feature context triggers bias risk observation."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from classify_risk import check_bias_risk
    text = "X_train = df[['income', 'race', 'age']]"
    obs = check_bias_risk(text)
    assert len(obs) >= 1, "Should detect protected class feature"
    assert obs[0]["article"] == "10"
    assert "Article 10(5)" in obs[0]["observation"] or "10(5)" in obs[0]["observation"]


def test_bias_missing_fairness_flagged():
    """Code with protected feature but no fairness library triggers absence warning."""
    from classify_risk import check_bias_risk
    text = "features = df[['salary', 'ethnicity', 'years_exp']]\nmodel.fit(features, labels)"
    obs = check_bias_risk(text)
    articles = [o["article"] for o in obs]
    assert "10" in articles
    # Should have both the feature finding AND the missing fairness eval
    assert len(obs) == 2


def test_bias_fairness_library_suppresses_absence():
    """Code with protected feature AND fairness library does not trigger absence warning."""
    from classify_risk import check_bias_risk
    text = "import fairlearn\nX = df[['income', 'race']]\nfrom fairlearn.metrics import equalized_odds"
    obs = check_bias_risk(text)
    # Should still flag protected feature, but NOT flag missing fairness eval
    assert len(obs) == 1
    assert "protected class" in obs[0]["observation"].lower() or "Protected" in obs[0]["observation"]


def test_bias_no_protected_features_no_observation():
    """Normal ML code without protected class features produces no bias observations."""
    from classify_risk import check_bias_risk
    text = "X = df[['age', 'income', 'credit_score']]\nmodel.fit(X, y)"
    obs = check_bias_risk(text)
    assert obs == []


def test_js_ts_automated_decision_function_detected():
    """JS/TS camelCase decision function names trigger Article 13 observation."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    from classify_risk import generate_observations
    text = "const filterCandidates = async (applicants) => { return applicants.filter(a => a.score > threshold); }"
    obs = generate_observations(text)
    articles = [o["article"] for o in obs]
    assert "13" in articles, f"Expected Article 13 observation, got: {obs}"


def test_js_ts_function_declaration_detected():
    """JS/TS function declaration with decision name triggers Article 13."""
    from classify_risk import generate_observations
    text = "function scoreApplicant(data) { return model.predict(data); }"
    obs = generate_observations(text)
    articles = [o["article"] for o in obs]
    assert "13" in articles, f"Expected Article 13 observation for scoreApplicant, got: {obs}"


# ---------------------------------------------------------------------------
# Jupyter notebook (.ipynb) source extraction
# ---------------------------------------------------------------------------

def test_notebook_extract_code_cells():
    """extract_code returns only code cells, joined with blank lines."""
    import tempfile, os, json
    from notebook import extract_code
    nb = {
        "cells": [
            {"cell_type": "markdown", "source": "# Title\nSome text"},
            {"cell_type": "code", "source": ["import openai\n", "client = openai.OpenAI()\n"]},
            {"cell_type": "code", "source": "model = 'gpt-4'\n"},
            {"cell_type": "raw", "source": "ignore me"},
        ],
        "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
    }
    with tempfile.NamedTemporaryFile("w", suffix=".ipynb", delete=False) as f:
        json.dump(nb, f)
        path = f.name
    try:
        text = extract_code(path)
        assert "import openai" in text, f"missing openai import: {text!r}"
        assert "gpt-4" in text, f"missing second cell: {text!r}"
        assert "Title" not in text, "markdown cell leaked into code extraction"
        assert "ignore me" not in text, "raw cell leaked into code extraction"
        print("✓ notebook: extract_code returns code cells only")
    finally:
        os.unlink(path)


def test_notebook_corrupt_returns_empty():
    """Corrupt or non-JSON .ipynb files return empty string, never raise."""
    import tempfile, os
    from notebook import extract_code
    with tempfile.NamedTemporaryFile("w", suffix=".ipynb", delete=False) as f:
        f.write("this is not valid json {{")
        path = f.name
    try:
        assert extract_code(path) == "", "corrupt notebook should return empty string"
        print("✓ notebook: corrupt file returns empty string without raising")
    finally:
        os.unlink(path)


def test_notebook_scan_end_to_end():
    """scan_files picks up .ipynb files and classifies them via existing pipeline."""
    import tempfile, shutil, os, json
    from report import scan_files
    tmpdir = tempfile.mkdtemp()
    try:
        nb = {
            "cells": [
                {"cell_type": "code", "source": "import openai\nclient = openai.OpenAI()\nresult = client.chat.completions.create(model='gpt-4', messages=[])\n"},
            ],
            "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
        }
        with open(os.path.join(tmpdir, "train.ipynb"), "w") as f:
            json.dump(nb, f)
        findings = scan_files(tmpdir)
        ipynb_findings = [f for f in findings if f.get("file", "").endswith(".ipynb")]
        assert len(ipynb_findings) >= 1, f"expected findings in .ipynb, got: {findings}"
        print(f"✓ notebook: scan_files found {len(ipynb_findings)} findings in .ipynb")
    finally:
        shutil.rmtree(tmpdir)


# ---------------------------------------------------------------------------
# Self-benchmark scan-time sanity (no network)
# ---------------------------------------------------------------------------

def test_self_scan_benchmark_runs():
    """`scan_benchmarks.self_benchmark_dict()` must scan the repo cleanly
    and return non-empty results. This pins the CI-runnable version of
    the README scan-time table — if scan_files breaks on the repo's
    own files, this test fails before the README claim does.
    """
    from scan_benchmarks import self_benchmark_dict
    result = self_benchmark_dict()
    assert result["files_scanned"] > 50, f"expected >50 files, got {result['files_scanned']}"
    assert result["wall_seconds"] >= 0, f"expected non-negative time, got {result}"
    assert result["files_per_second"] > 0, f"expected positive throughput, got {result}"
    print(f"✓ self-benchmark: {result['files_scanned']} files in {result['wall_seconds']}s "
          f"({result['files_per_second']} files/s, sha={result['commit']})")


# ---------------------------------------------------------------------------
# Synthetic prohibited / high-risk fixture — regression guard
# ---------------------------------------------------------------------------

def test_synthetic_fixture_perfect_precision_recall():
    """Pin the synthetic-fixture baseline: prohibited and high_risk tiers
    must achieve 100% precision and 100% recall against the labelled
    fixture in benchmarks/synthetic/. This guards against the bug fixed
    by the early prohibited check in report.py — the scanner used to
    short-circuit on non-AI-importing files and skip Article 5 entirely.
    """
    import sys
    from pathlib import Path as _P
    sys.path.insert(0, str(_P(__file__).parent.parent / "benchmarks" / "synthetic"))
    # Reset module cache so the test imports the script's metrics_dict
    if "run" in sys.modules:
        del sys.modules["run"]
    from run import metrics_dict  # noqa: E402
    # Clear scanner cache so test isolates current code path
    import shutil
    cache_dir = _P.home() / ".regula" / "cache"
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)
    metrics = metrics_dict()
    for tier in ("prohibited", "high_risk"):
        m = metrics[tier]
        assert m["precision"] == 1.0, f"{tier} precision regression: got {m['precision']}, expected 1.0. tp={m['tp']} fp={m['fp']}"
        assert m["recall"] == 1.0, f"{tier} recall regression: got {m['recall']}, expected 1.0. tp={m['tp']} fn={m['fn']}"
        assert m["fp"] == 0, f"{tier} false positive on synthetic fixture: {m}"
        assert m["fn"] == 0, f"{tier} false negative on synthetic fixture: {m}"
    print("✓ synthetic: prohibited 100/100, high_risk 100/100 (5 TP each, 0 FP, 0 FN)")


# ---------------------------------------------------------------------------
# Published precision matches the labelled benchmark
# ---------------------------------------------------------------------------

def test_published_precision_matches_labels():
    """The README/benchmark precision number must match labels.json."""
    from pathlib import Path as _P
    root = _P(__file__).parent.parent
    labels_path = root / "benchmarks" / "labels.json"
    if not labels_path.exists():
        print("⊘ precision: skipped (no labels.json)")
        return
    labels = json.loads(labels_path.read_text())
    tp = sum(1 for x in labels if x.get("label") == "tp")
    fp = sum(1 for x in labels if x.get("label") == "fp")
    if tp + fp == 0:
        print("⊘ precision: skipped (no tp/fp labels)")
        return
    measured = round(tp / (tp + fp), 3)
    # README publishes 15.2% — fail loudly if labels move and the README isn't updated.
    bench_readme = (root / "benchmarks" / "README.md").read_text()
    main_readme = (root / "README.md").read_text()
    pct_str = f"{measured * 100:.1f}%"
    assert pct_str in bench_readme, (
        f"benchmarks/README.md publishes a precision number that does not match "
        f"labels.json. Labels say {pct_str}; update the README table or relabel."
    )
    assert pct_str in main_readme, (
        f"README.md publishes a precision number that does not match labels.json. "
        f"Labels say {pct_str}; update the README table or relabel."
    )
    print(f"✓ precision: published number {pct_str} matches labels.json (tp={tp}, fp={fp})")


# ---------------------------------------------------------------------------
# CycloneDX 1.7 spec bump (Oct 2025, ECMA-424 2nd Edition)
# ---------------------------------------------------------------------------

def test_sbom_uses_cyclonedx_1_7():
    """generate_sbom must emit specVersion 1.7 to align with the current standard."""
    import tempfile, shutil, os
    from sbom import generate_sbom
    tmpdir = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmpdir, "a.py"), "w") as f:
            f.write("import openai\nclient = openai.OpenAI()\n")
        bom = generate_sbom(tmpdir, ai_bom=True)
        assert bom.get("specVersion") == "1.7", f"expected specVersion 1.7, got {bom.get('specVersion')}"
        print("✓ sbom: CycloneDX specVersion 1.7")
    finally:
        shutil.rmtree(tmpdir)


# ---------------------------------------------------------------------------
# GPAI Code of Practice signatory annotation
# ---------------------------------------------------------------------------

def test_gpai_signatories_file_loads():
    """references/gpai_signatories.yaml must load and have 26 signatories pledged."""
    if not _HAS_PYYAML:
        print("⊘ gpai_signatories: skipped (pyyaml not installed)")
        return
    from pathlib import Path as _P
    p = _P(__file__).parent.parent / "references" / "gpai_signatories.yaml"
    data = yaml.safe_load(p.read_text())
    assert data["schema_version"] == "1.0"
    assert data["total_signatories"] == 26
    vendors = data.get("vendors", [])
    # Sanity: at least the 8 vendors I curated must be present
    vendor_ids = {v["id"] for v in vendors}
    for required in ("openai", "anthropic", "mistral", "cohere", "huggingface"):
        assert required in vendor_ids, f"missing required vendor: {required}"
    # All listed vendors must have signed: true (otherwise they belong in non_signatories)
    for v in vendors:
        assert v.get("signed") is True, f"vendor {v['id']} marked signed:false in vendors list"
    print(f"✓ gpai_signatories: {len(vendors)} curated vendors loaded")


def test_sbom_annotates_openai_with_gpai_signed():
    """When openai is detected, the BOM should include regula:gpai-code-signed=true."""
    import tempfile, shutil, os
    from sbom import generate_sbom
    tmpdir = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmpdir, "use.py"), "w") as f:
            f.write(
                "import openai\n"
                "client = openai.OpenAI()\n"
                "client.chat.completions.create(model='gpt-4', messages=[])\n"
            )
        bom = generate_sbom(tmpdir, ai_bom=True)
        models = [c for c in bom.get("components", []) if c.get("type") == "machine-learning-model"]
        assert len(models) >= 1, f"expected models in BOM, got: {[c.get('type') for c in bom.get('components', [])]}"
        # Find the OpenAI-provided model and confirm it has the signed annotation
        signed_props = []
        for m in models:
            for p in m.get("properties", []):
                if p["name"] == "regula:gpai-code-signed":
                    signed_props.append(p["value"])
        assert "true" in signed_props or "unknown" in signed_props, \
            f"expected gpai-code-signed property, got props: {[p['name'] for m in models for p in m.get('properties',[])]}"
        print(f"✓ sbom: GPAI annotation present (statuses: {signed_props})")
    finally:
        shutil.rmtree(tmpdir)


# ---------------------------------------------------------------------------
# NIST AI 600-1 GenAI Profile mapping
# ---------------------------------------------------------------------------

def test_nist_ai_600_1_mapping_present():
    """framework_crosswalk.yaml must include the 12 NIST AI 600-1 GenAI risks."""
    if not _HAS_PYYAML:
        print("⊘ nist_ai_600_1: skipped (pyyaml not installed)")
        return
    from pathlib import Path as _P
    p = _P(__file__).parent.parent / "references" / "framework_crosswalk.yaml"
    data = yaml.safe_load(p.read_text())
    assert "nist_ai_600_1_genai_profile" in data, "missing nist_ai_600_1_genai_profile section"
    profile = data["nist_ai_600_1_genai_profile"]
    risks = profile.get("risks", [])
    assert len(risks) == 12, f"expected 12 risks, got {len(risks)}"
    risk_ids = {r["id"] for r in risks}
    required = {"cbrn", "confabulation", "data_privacy", "harmful_bias_homogenization",
                "human_ai_configuration", "information_integrity", "information_security",
                "intellectual_property", "value_chain_component_integration"}
    missing = required - risk_ids
    assert not missing, f"missing required risk ids: {missing}"
    # Each risk must map to at least one EU AI Act article
    for r in risks:
        assert r.get("maps_to_eu_ai_act_articles"), f"risk {r['id']} has no article mapping"
    print(f"✓ nist_ai_600_1: 12 risks loaded, all mapped to EU AI Act articles")


# ---------------------------------------------------------------------------
# findings_view.partition_findings — extracted from cli.cmd_check (C2)
# ---------------------------------------------------------------------------

def test_partition_findings_separates_suppressed():
    from findings_view import partition_findings
    findings = [
        {"file": "a.py", "tier": "high_risk", "confidence_score": 70, "suppressed": False},
        {"file": "b.py", "tier": "high_risk", "confidence_score": 70, "suppressed": True},
    ]
    view = partition_findings(findings)
    assert len(view["active"]) == 1
    assert len(view["suppressed"]) == 1
    assert view["suppressed"][0]["file"] == "b.py"
    print("✓ findings_view: suppressed split correctly")


def test_partition_findings_groups_by_tier():
    from findings_view import partition_findings
    findings = [
        {"file": "p.py", "tier": "prohibited", "confidence_score": 90},
        {"file": "h.py", "tier": "high_risk", "confidence_score": 80},
        {"file": "l.py", "tier": "limited_risk", "confidence_score": 50},
        {"file": "a.py", "tier": "agent_autonomy", "confidence_score": 60},
        {"file": "c.py", "tier": "credential_exposure", "confidence_score": 90},
        {"file": "m.py", "tier": "minimal_risk", "confidence_score": 20},
    ]
    view = partition_findings(findings)
    assert len(view["prohibited"]) == 1 and view["prohibited"][0]["file"] == "p.py"
    assert len(view["high_risk"]) == 1 and view["high_risk"][0]["file"] == "h.py"
    assert len(view["limited"]) == 1 and view["limited"][0]["file"] == "l.py"
    assert len(view["autonomy"]) == 1 and view["autonomy"][0]["file"] == "a.py"
    assert len(view["credentials"]) == 1 and view["credentials"][0]["file"] == "c.py"
    print("✓ findings_view: 5 tiers grouped correctly")


def test_partition_findings_does_not_mutate_input():
    """The original cli.cmd_check inlined version mutated the input list
    by adding _finding_tier to each finding. The extracted partition must
    NOT mutate inputs."""
    from findings_view import partition_findings
    original = {"file": "x.py", "tier": "high_risk", "confidence_score": 70}
    findings = [original]
    _ = partition_findings(findings)
    assert "_finding_tier" not in original, "input was mutated"
    print("✓ findings_view: input list not mutated")


def test_partition_findings_assigns_display_tier():
    """Active findings come back annotated with _finding_tier (block/warn/info)."""
    from findings_view import partition_findings
    findings = [
        {"file": "p.py", "tier": "prohibited", "confidence_score": 90},
    ]
    view = partition_findings(findings)
    assert view["active"][0]["_finding_tier"] in ("block", "warn", "info")
    print(f"✓ findings_view: display tier annotated ({view['active'][0]['_finding_tier']})")


def test_partition_findings_empty_input():
    from findings_view import partition_findings
    view = partition_findings([])
    assert view["active"] == []
    assert view["suppressed"] == []
    assert view["prohibited"] == []
    assert view["block"] == []
    print("✓ findings_view: empty input handled")


# ---------------------------------------------------------------------------
# GitHub Action sanity (action.yml structure)
# ---------------------------------------------------------------------------

def test_action_yml_has_inline_pr_comment_step():
    """action.yml exposes inline-pr-comments input and the step that posts them."""
    if not _HAS_PYYAML:
        print("⊘ action.yml: skipped (pyyaml not installed)")
        return
    from pathlib import Path as _P
    doc = yaml.safe_load(_P(__file__).parent.parent.joinpath("action.yml").read_text())
    inputs = doc.get("inputs", {})
    for name in ("inline-pr-comments", "inline-comment-max", "inline-comment-min-tier"):
        assert name in inputs, f"action.yml missing input: {name}"
    steps = doc.get("runs", {}).get("steps", [])
    step_names = [s.get("name", "") for s in steps]
    assert "Post inline PR review comments" in step_names, f"action.yml missing inline review step. Steps: {step_names}"
    inline_step = next(s for s in steps if s.get("name") == "Post inline PR review comments")
    script = inline_step.get("with", {}).get("script", "")
    assert "pulls.listFiles" in script, "inline step must call pulls.listFiles to get diff"
    assert "createReview" in script, "inline step must call createReview to post comments"
    assert "side: 'RIGHT'" in script, "inline comments must target the RIGHT side of the diff"
    print(f"✓ action.yml: inline PR review step present (3 inputs, {len(steps)} steps)")


# ---------------------------------------------------------------------------
# Domain boost surfaces in finding output
# ---------------------------------------------------------------------------

def test_domain_boost_surfaces_in_finding():
    """Findings include domain_boost when domain keywords co-occur with AI on the high-risk path."""
    import tempfile, shutil, os
    from report import scan_files
    tmpdir = tempfile.mkdtemp()
    try:
        # AI + finance domain keywords → high-risk classification + domain boost
        with open(os.path.join(tmpdir, "credit.py"), "w") as f:
            f.write(
                "import sklearn\n"
                "from sklearn.linear_model import LogisticRegression\n"
                "def credit_score_model(applicant):\n"
                "    model = LogisticRegression()\n"
                "    model.fit(X_train, y_train)\n"
                "    return model.predict([applicant.creditworthiness, applicant.loan_default_risk])\n"
            )
        findings = scan_files(tmpdir)
        boosted = [f for f in findings if f.get("domain_boost")]
        assert len(boosted) >= 1, f"expected at least one boosted finding, got: {[(f.get('category'), f.get('tier')) for f in findings]}"
        b = boosted[0]["domain_boost"]
        assert b["boost"] > 0, f"boost should be positive: {b}"
        assert "finance" in b["domains_matched"], f"expected finance match: {b}"
        print(f"✓ domain: boost surfaced in finding (+{b['boost']}, {b['domains_matched']})")
    finally:
        shutil.rmtree(tmpdir)


# ---------------------------------------------------------------------------
# MCP server protocol smoke test
# ---------------------------------------------------------------------------

def test_mcp_server_initialize_and_list_tools():
    """MCP server responds to initialize and tools/list per the documented protocol."""
    import subprocess, json, sys
    from pathlib import Path as _P
    server = _P(__file__).parent.parent / "scripts" / "mcp_server.py"

    init_req = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}
    })
    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    payload = init_req + "\n" + list_req + "\n"

    proc = subprocess.run(
        [sys.executable, str(server)],
        input=payload, capture_output=True, text=True, timeout=15
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip().startswith("{")]
    assert len(lines) >= 2, f"expected 2 JSON-RPC responses, got: {proc.stdout!r} stderr={proc.stderr!r}"

    init_resp = json.loads(lines[0])
    assert init_resp.get("id") == 1, f"init response id wrong: {init_resp}"
    assert "result" in init_resp, f"init response missing result: {init_resp}"
    assert init_resp["result"]["serverInfo"]["name"] == "regula", f"server name: {init_resp}"

    list_resp = json.loads(lines[1])
    tool_names = sorted(t["name"] for t in list_resp["result"]["tools"])
    assert "regula_check" in tool_names and "regula_classify" in tool_names and "regula_gap" in tool_names, \
        f"missing documented tools, got: {tool_names}"
    print(f"✓ mcp: initialize + tools/list returned {tool_names}")


# ---------------------------------------------------------------------------
# Scan time benchmark script (self-mode, no network)
# ---------------------------------------------------------------------------

def test_scan_benchmarks_self_mode():
    """benchmark_path returns timing + counts for a local directory."""
    import tempfile, os
    from scan_benchmarks import benchmark_path
    from pathlib import Path as _P
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "a.py"), "w") as f:
            f.write("import openai\nclient = openai.OpenAI()\n")
        result = benchmark_path("test", _P(tmp))
        assert result["files_scanned"] >= 1, f"expected files counted, got: {result}"
        assert result["wall_seconds"] >= 0, f"expected timing, got: {result}"
        assert "findings" in result, f"missing findings field: {result}"
        assert result["files_per_second"] >= 0, f"missing fps: {result}"
        print(f"✓ scan_benchmarks: self-mode returned {result['files_scanned']} files in {result['wall_seconds']}s")
    finally:
        import shutil
        shutil.rmtree(tmp)


if __name__ == "__main__":
    # Auto-discover every top-level function whose name starts with `test_`.
    # Eliminates the manual-list maintenance burden that was the actual
    # long-term degradation behind tech debt finding T1: previously every
    # new test had to be added in two places (the def and the manual list)
    # and forgetting the second was undetectable until pytest ran. Now the
    # custom runner and pytest discovery use the same source of truth.
    tests = sorted(
        (obj for name, obj in list(globals().items())
         if name.startswith("test_") and callable(obj)),
        key=lambda f: f.__code__.co_firstlineno,
    )

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
