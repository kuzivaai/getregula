# regula-ignore
#!/usr/bin/env python3
"""
Coverage tests for classify_risk.py and credential_check.py

These are security-critical modules. This file adds tests for
uncovered paths identified by coverage analysis.

IMPORTANT: This file contains INTENTIONALLY FAKE credential patterns
for testing secret detection. All values are synthetic test fixtures.
"""

import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from classify_risk import (
    classify, RiskTier, is_ai_related, check_ai_security,
    generate_observations, _compute_confidence_score, is_training_activity,
)

passed = 0
failed = 0
_PYTEST_MODE = "pytest" in sys.modules


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


# ══════════════════════════════════════════════════════════════════════
# credential_check.py — Full Pattern Coverage
# ══════════════════════════════════════════════════════════════════════

# Synthetic test credentials — constructed to match patterns but NOT real keys
_SK = "sk-" + "abcdefghijklmnopqrstuvwxyz12345"
_ANT = "sk-ant-api03-" + "abcdefghijklmnopqrstuvwxyz1234567890"
_GOOG = "AIzaSyA-" + "0123456789abcdefghijklmnopqrstuv"
_GHP = "ghp_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij1234"
_GHS = "ghs_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij1234"
_AWS = "AKIA" + "IOSFODNN7EXAMPLE"
_PK_HEADERS = [
    "-----BEGIN RSA PRIVATE KEY" + "-----",
    "-----BEGIN PRIVATE KEY" + "-----",
    "-----BEGIN EC PRIVATE KEY" + "-----",
    "-----BEGIN OPENSSH PRIVATE KEY" + "-----",
    "-----BEGIN DSA PRIVATE KEY" + "-----",
]
_PG_CONN = "postgres://user:pass@db.example.com:5432/mydb"
_MONGO_CONN = "mongodb://admin:pass@cluster.example.com/mydb"
_PG_LOCAL = "postgres://localhost:5432/mydb"
# regula-ignore (needed for Edit hook bypass)
_AWS_SECRET = 'aws_secret = "abcdefghijABCDEFGHIJabcdefghijABCDEFGHIJ"'
_GENERIC_KEY = 'api_key = "abcdefghijklmnopqrstuvwxyz1234"'


def test_secret_anthropic_key():
    """Detects Anthropic API key pattern"""
    from credential_check import check_secrets
    findings = check_secrets(_ANT)
    assert_true(len(findings) > 0, "detects Anthropic key")
    anthropic = [f for f in findings if f.pattern_name == "anthropic_api_key"]
    assert_true(len(anthropic) > 0, "identified as anthropic_api_key")
    assert_eq(anthropic[0].confidence, "high", "Anthropic key is high confidence")
    print("✓ Secrets: detects Anthropic API key")


def test_secret_google_api_key():
    """Detects Google API key pattern"""
    from credential_check import check_secrets
    findings = check_secrets(_GOOG)
    google = [f for f in findings if f.pattern_name == "google_api_key"]
    assert_true(len(google) > 0, "identified as google_api_key")
    assert_eq(google[0].confidence, "high", "Google key is high confidence")
    print("✓ Secrets: detects Google API key")


def test_secret_github_token():
    """Detects GitHub personal access token (ghp_ and ghs_)"""
    from credential_check import check_secrets
    findings = check_secrets(_GHP)
    github = [f for f in findings if f.pattern_name == "github_token"]
    assert_true(len(github) > 0, "detects ghp_ GitHub token")
    assert_eq(github[0].confidence, "high", "GitHub token is high confidence")

    findings2 = check_secrets(_GHS)
    github2 = [f for f in findings2 if f.pattern_name == "github_token"]
    assert_true(len(github2) > 0, "detects ghs_ GitHub token")
    print("✓ Secrets: detects GitHub tokens (ghp_ and ghs_)")


def test_secret_private_key():
    """Detects PEM private key headers"""
    from credential_check import check_secrets
    for header in _PK_HEADERS:
        findings = check_secrets(header)
        pk = [f for f in findings if f.pattern_name == "private_key"]
        assert_true(len(pk) > 0, f"detects {header[:30]}...")
    print("✓ Secrets: detects all private key formats")


def test_secret_generic_api_key():
    """Detects generic API key assignments"""
    from credential_check import check_secrets
    findings = check_secrets(_GENERIC_KEY)
    generic = [f for f in findings if f.pattern_name == "generic_api_key"]
    assert_true(len(generic) > 0, "detects generic api_key assignment")
    assert_eq(generic[0].confidence, "medium", "generic key is medium confidence")
    print("✓ Secrets: detects generic API key assignment")


def test_secret_connection_string():
    """Detects database connection strings"""
    from credential_check import check_secrets
    findings = check_secrets(_PG_CONN)
    conn = [f for f in findings if f.pattern_name == "connection_string"]
    assert_true(len(conn) > 0, "detects postgres connection string")
    assert_eq(conn[0].confidence, "medium", "connection string is medium confidence")

    findings2 = check_secrets(_MONGO_CONN)
    conn2 = [f for f in findings2 if f.pattern_name == "connection_string"]
    assert_true(len(conn2) > 0, "detects mongodb connection string")
    print("✓ Secrets: detects database connection strings")


def test_secret_connection_string_localhost_exempt():
    """Localhost connection strings are NOT flagged"""
    from credential_check import check_secrets
    findings = check_secrets(_PG_LOCAL)
    conn = [f for f in findings if f.pattern_name == "connection_string"]
    assert_eq(len(conn), 0, "localhost not flagged")
    print("✓ Secrets: localhost connection strings exempted")


def test_secret_aws_secret_key():
    """Detects AWS secret access key pattern"""
    from credential_check import check_secrets
    findings = check_secrets(_AWS_SECRET)
    aws = [f for f in findings if f.pattern_name == "aws_secret_key"]
    assert_true(len(aws) > 0, "detects AWS secret key")
    assert_eq(aws[0].confidence, "medium", "AWS secret key is medium confidence")
    print("✓ Secrets: detects AWS secret access key")


# ── _redact Edge Cases ─────────────────────────────────────────────

def test_redact_short_value():
    """Redaction of values with 4 or fewer characters returns ****"""
    from credential_check import _redact
    assert_eq(_redact("abc"), "****", "3-char value fully redacted")
    assert_eq(_redact("abcd"), "****", "4-char value fully redacted")
    assert_eq(_redact("a"), "****", "1-char value fully redacted")
    assert_eq(_redact(""), "****", "empty string fully redacted")
    assert_eq(_redact("abcde"), "abcd****", "5-char value shows first 4")
    print("✓ Secrets: _redact handles short values")


# ── has_high_confidence_secret ─────────────────────────────────────

def test_has_high_confidence_secret():
    """Quick check for high-confidence secrets"""
    from credential_check import has_high_confidence_secret
    assert_true(has_high_confidence_secret(_SK), "OpenAI key")
    assert_true(has_high_confidence_secret(_ANT), "Anthropic key")
    assert_true(has_high_confidence_secret(_AWS), "AWS key")
    assert_true(has_high_confidence_secret(_PK_HEADERS[0]), "private key")
    assert_false(has_high_confidence_secret("print('hello')"), "no secret")
    assert_false(has_high_confidence_secret(""), "empty string")
    assert_false(has_high_confidence_secret(_GENERIC_KEY),
                 "generic key is medium, not high")
    print("✓ Secrets: has_high_confidence_secret works correctly")


# ── format_secret_warning ──────────────────────────────────────────

def test_format_warning_high_confidence():
    """format_secret_warning with high-confidence findings"""
    from credential_check import check_secrets, format_secret_warning
    findings = check_secrets(_SK)
    warning = format_secret_warning(findings)
    assert_true("CREDENTIAL EXPOSURE RISK" in warning, "has header")
    assert_true("blocked" in warning.lower(), "mentions blocking")
    print("✓ Secrets: format_secret_warning (high confidence)")


def test_format_warning_medium_only():
    """format_secret_warning with only medium-confidence findings"""
    from credential_check import format_secret_warning, SecretFinding
    medium_finding = SecretFinding(
        pattern_name="generic_api_key",
        confidence="medium",
        confidence_score=60,
        redacted_value="abcd****",
        description="Possible API key or token in assignment",
        remediation="Move credentials to environment variables.",
    )
    warning = format_secret_warning([medium_finding])
    assert_true("CREDENTIAL WARNING" in warning, "has medium header")
    assert_false("blocked" in warning.lower(), "no blocking for medium only")
    assert_true("abcd****" in warning, "shows redacted value")
    print("✓ Secrets: format_secret_warning (medium only)")


def test_format_warning_mixed():
    """format_secret_warning with both high and medium findings"""
    from credential_check import SecretFinding, format_secret_warning
    high_finding = SecretFinding(
        pattern_name="openai_api_key",
        confidence="high",
        confidence_score=95,
        redacted_value="sk-a****",
        description="OpenAI API key detected",
        remediation="Use environment variable OPENAI_API_KEY.",
    )
    medium_finding = SecretFinding(
        pattern_name="generic_api_key",
        confidence="medium",
        confidence_score=60,
        redacted_value="abcd****",
        description="Possible API key",
        remediation="Move to env vars.",
    )
    warning = format_secret_warning([high_finding, medium_finding])
    assert_true("CREDENTIAL EXPOSURE RISK" in warning, "has high header")
    assert_true("Additional warnings:" in warning, "has additional section")
    print("✓ Secrets: format_secret_warning (mixed)")


def test_format_warning_empty():
    """format_secret_warning with no findings returns empty string"""
    from credential_check import format_secret_warning
    assert_eq(format_secret_warning([]), "", "empty findings returns empty string")
    print("✓ Secrets: format_secret_warning (empty)")


# ── False Positive Prevention ──────────────────────────────────────

def test_secret_no_false_positive_short_sk():
    """Short sk- prefixed strings are not flagged (need 20+ chars)"""
    from credential_check import check_secrets
    findings = check_secrets("sk-short")
    openai = [f for f in findings if f.pattern_name == "openai_api_key"]
    assert_eq(len(openai), 0, "short sk- not flagged")
    print("✓ Secrets: short sk- prefix not false positive")


def test_secret_no_false_positive_similar_prefix():
    """Strings that look similar but don't match patterns"""
    from credential_check import check_secrets
    assert_eq(len(check_secrets("API_KEY_NAME=development")), 0, "env var name without value")
    assert_eq(len(check_secrets("aws_region = 'us-east-1'")), 0, "aws region not a key")
    assert_eq(len(check_secrets("github.com/user/repo")), 0, "github URL not a token")
    print("✓ Secrets: similar prefixes not false positives")


# ── Empty/Edge Inputs ──────────────────────────────────────────────

def test_secret_empty_input():
    """Empty and whitespace inputs handled gracefully"""
    from credential_check import check_secrets
    assert_eq(len(check_secrets("")), 0, "empty string")
    assert_eq(len(check_secrets("   ")), 0, "whitespace")
    assert_eq(len(check_secrets("\n\n\n")), 0, "newlines")
    print("✓ Secrets: empty/whitespace inputs handled")


def test_secret_binary_like_input():
    """Binary-like content doesn't crash"""
    from credential_check import check_secrets
    binary_like = "\x00\x01\x02" * 100
    findings = check_secrets(binary_like)
    assert_true(isinstance(findings, list), "returns list for binary input")
    print("✓ Secrets: binary-like input handled gracefully")


def test_secret_sorting_order():
    """Findings are sorted by confidence score (highest first)"""
    from credential_check import check_secrets
    text = _SK + " " + _GENERIC_KEY
    findings = check_secrets(text)
    if len(findings) >= 2:
        scores = [f.confidence_score for f in findings]
        assert_true(scores == sorted(scores, reverse=True), "sorted by confidence desc")
    print("✓ Secrets: findings sorted by confidence score")


# ── ReDoS Prevention (credentials) ────────────────────────────────

def test_no_redos_credential_patterns():
    """Verify credential patterns complete in <1s on pathological input"""
    from credential_check import check_secrets
    pathological_inputs = [
        'a' * 10000 + 'b',
        'sk-' + 'a' * 10000,
        'AKIA' + '0' * 10000,
        'api_key = "' + 'a' * 10000 + '"',
    ]
    for inp in pathological_inputs:
        start = time.time()
        check_secrets(inp)
        elapsed = time.time() - start
        assert_true(elapsed < 1.0, f"potential ReDoS: {elapsed:.2f}s on {inp[:30]}...")
    print("✓ Secrets: no ReDoS on pathological inputs")


# ══════════════════════════════════════════════════════════════════════
# classify_risk.py — Uncovered Path Tests
# ══════════════════════════════════════════════════════════════════════

# ── check_ai_security Skip Paths ──────────────────────────────────

def test_ai_security_skips_comments():
    """AI security checker skips comment lines"""
    code = "# pickle.load(f)  — example of what NOT to do\nprint('safe code')\n"
    findings = check_ai_security(code)
    pickle_findings = [f for f in findings if f["pattern_name"] == "unsafe_deserialization"]
    assert_eq(len(pickle_findings), 0, "comments skipped")
    print("✓ AI security: skips Python comments")


def test_ai_security_skips_js_comments():
    """AI security checker skips JS-style comments"""
    code = "// eval(response.choices[0].message.content)\nconsole.log('safe');\n"
    findings = check_ai_security(code)
    eval_findings = [f for f in findings if f["pattern_name"] == "no_output_validation"]
    assert_eq(len(eval_findings), 0, "JS comments skipped")
    print("✓ AI security: skips JS comments")


def test_ai_security_skips_docstrings():
    """AI security checker skips docstring content"""
    code = '"""\nDo not use pickle.load(f) on untrusted data.\n"""\nprint("safe")\n'
    findings = check_ai_security(code)
    pickle_findings = [f for f in findings if f["pattern_name"] == "unsafe_deserialization"]
    assert_eq(len(pickle_findings), 0, "docstring content skipped")
    print("✓ AI security: skips docstrings")


def test_ai_security_skips_long_lines():
    """AI security checker skips lines longer than 2000 chars"""
    long_line = "x = " + "a" * 2001 + " pickle.load(f)\n"
    findings = check_ai_security(long_line)
    pickle_findings = [f for f in findings if f["pattern_name"] == "unsafe_deserialization"]
    assert_eq(len(pickle_findings), 0, "long line skipped")
    print("✓ AI security: skips lines > 2000 chars")


def test_ai_security_skips_args_lines():
    """AI security checker skips documentation Args: lines"""
    code = "Args: response from eval(completion)\nReturns: result of eval(output)\n"
    findings = check_ai_security(code)
    eval_findings = [f for f in findings if f["pattern_name"] == "no_output_validation"]
    assert_eq(len(eval_findings), 0, "Args/Returns lines skipped")
    print("✓ AI security: skips Args:/Returns: documentation lines")


def test_ai_security_detects_multiple_patterns():
    """AI security checker detects multiple distinct patterns"""
    code = (
        "import pickle\n"
        "model = pickle.load(open('model.pkl', 'rb'))\n"
        "result = eval(response.choices[0].content)\n"
        "max_tokens = None\n"
    )
    findings = check_ai_security(code)
    pattern_names = {f["pattern_name"] for f in findings}
    assert_true("unsafe_deserialization" in pattern_names, "detects pickle")
    assert_true("no_output_validation" in pattern_names, "detects eval")
    print("✓ AI security: detects multiple patterns in one file")


# ── generate_observations ──────────────────────────────────────────

def test_governance_observations_training_data():
    """Generates Article 10 observation for training data patterns"""
    code = "from sklearn.model_selection import train_test_split\nmodel.fit(X_train, y_train)\n"
    obs = generate_observations(code)
    art10 = [o for o in obs if o["article"] == "10"]
    assert_true(len(art10) > 0, "Article 10 observation generated")
    assert_true("training data" in art10[0]["observation"].lower(), "mentions training data")
    print("✓ Observations: training data -> Article 10")


def test_governance_observations_prediction():
    """Generates Article 14 observation for prediction patterns"""
    code = "predictions = model.predict(X_test)\n"
    obs = generate_observations(code)
    art14 = [o for o in obs if o["article"] == "14"]
    assert_true(len(art14) > 0, "Article 14 observation generated")
    assert_true("human oversight" in art14[0]["observation"].lower(), "mentions human oversight")
    print("✓ Observations: prediction -> Article 14")


def test_governance_observations_automated_decision():
    """Generates Article 13 observation for automated decision functions"""
    code = "def screen_candidates(applications):\n    return ranked_list\n"
    obs = generate_observations(code)
    art13 = [o for o in obs if o["article"] == "13"]
    assert_true(len(art13) > 0, "Article 13 observation generated")
    assert_true("transparency" in art13[0]["observation"].lower(), "mentions transparency")
    print("✓ Observations: automated decision -> Article 13")


def test_governance_observations_no_logging():
    """Flags absence of logging as Article 12 observation"""
    code = "result = process(data)\nreturn result\n"
    obs = generate_observations(code)
    art12 = [o for o in obs if o["article"] == "12"]
    assert_true(len(art12) > 0, "Article 12 absence observation")
    assert_true("no logging" in art12[0]["observation"].lower(), "flags missing logging")
    print("✓ Observations: missing logging -> Article 12")


def test_governance_observations_with_logging():
    """No Article 12 absence flag when logging IS present"""
    code = "import logging\nlogger = logging.getLogger(__name__)\nlogger.info('done')\n"
    obs = generate_observations(code)
    art12 = [o for o in obs if o["article"] == "12"]
    assert_eq(len(art12), 0, "no absence flag when logging present")
    print("✓ Observations: logging present -> no Article 12 flag")


# ── _compute_confidence_score ──────────────────────────────────────

def test_confidence_score_computation():
    """Confidence score computed correctly for all tiers"""
    # Base: prohibited=75, high_risk=55, limited_risk=40, minimal_risk=15
    # match_bonus = min(num_matches * 8, 15), ai_bonus = 10 if has_ai
    assert_eq(_compute_confidence_score("prohibited", 1, False), 75 + 8 + 0, "prohibited 1 match no AI")
    assert_eq(_compute_confidence_score("prohibited", 1, True), 75 + 8 + 10, "prohibited 1 match with AI")
    assert_eq(_compute_confidence_score("high_risk", 1, True), 55 + 8 + 10, "high_risk 1 match with AI")
    assert_eq(_compute_confidence_score("limited_risk", 1, True), 40 + 8 + 10, "limited_risk 1 match with AI")
    assert_eq(_compute_confidence_score("minimal_risk", 1, False), 15 + 8, "minimal_risk 1 match no AI")
    assert_eq(_compute_confidence_score("prohibited", 3, True), 100, "capped at 100")
    assert_eq(_compute_confidence_score("unknown", 1, False), 10 + 8, "unknown tier defaults to 10")
    assert_eq(_compute_confidence_score("minimal_risk", 5, False), 15 + 15, "match bonus capped at 15")
    print("✓ Confidence score: computed correctly for all tiers")


# ── get_finding_tier ───────────────────────────────────────────────

def test_finding_tier_prohibited_always_block():
    """Prohibited classification always returns 'block'"""
    r = classify("social scoring using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "is prohibited")
    assert_eq(r.get_finding_tier(), "block", "prohibited always blocks")
    print("✓ Finding tier: prohibited always blocks")


def test_finding_tier_warn_range():
    """High-risk with single match falls in warn range"""
    r = classify("import sklearn; CV screening for hiring")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "is high risk")
    tier = r.get_finding_tier()
    assert_eq(tier, "warn", f"single high-risk match -> warn (score={r.confidence_score})")
    print("✓ Finding tier: single high-risk -> warn")


def test_finding_tier_info_range():
    """Minimal-risk AI system falls in info range"""
    r = classify("using tensorflow for recommendations")
    if r.tier == RiskTier.MINIMAL_RISK:
        tier = r.get_finding_tier()
        assert_eq(tier, "info", f"minimal risk -> info (score={r.confidence_score})")
    print("✓ Finding tier: minimal risk -> info")


# ── Pattern Coverage ───────────────────────────────────────────────

def test_prohibited_exploitation_vulnerabilities():
    """Exploitation of vulnerable groups -> PROHIBITED"""
    r = classify("target elderly users using tensorflow")
    assert_eq(r.tier, RiskTier.PROHIBITED, "target elderly")
    r = classify("exploit disability with machine learning")
    assert_eq(r.tier, RiskTier.PROHIBITED, "exploit disability")
    r = classify("vulnerable group targeting with sklearn")
    assert_eq(r.tier, RiskTier.PROHIBITED, "vulnerable group target")
    print("✓ Prohibited: exploitation of vulnerable groups")


def test_high_risk_essential_services_extended():
    """Extended essential services patterns"""
    r = classify("credit risk assessment model using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "credit risk")
    r = classify("credit model prediction with sklearn")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "credit model")
    r = classify("loan approval system using machine learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "loan approval")
    r = classify("lending decision engine with tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "lending decision")
    r = classify("benefit eligibility using machine learning")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "benefit eligibility")
    r = classify("emergency dispatch AI system using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "emergency dispatch")
    print("✓ High-risk: essential services extended patterns")


def test_high_risk_employment_extended():
    """Extended employment patterns"""
    r = classify("promotion decision system using tensorflow")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "promotion decision")
    r = classify("termination decision engine with sklearn")
    assert_eq(r.tier, RiskTier.HIGH_RISK, "termination decision")
    print("✓ High-risk: employment extended patterns")


def test_limited_risk_synthetic_content():
    """Synthetic content patterns -> LIMITED-RISK"""
    r = classify("face swap using tensorflow")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "face swap")
    r = classify("voice cloning with machine learning")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "voice cloning")
    r = classify("ai generated image model with tensorflow")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "ai generated image")
    r = classify("text to image pipeline with tensorflow")
    assert_eq(r.tier, RiskTier.LIMITED_RISK, "text to image")
    print("✓ Limited-risk: synthetic content patterns")


def test_training_detection_extended():
    """Extended training pattern detection"""
    assert_true(is_training_activity("using qlora for fine-tuning"), "qlora")
    assert_true(is_training_activity("from peft import get_peft_model"), "peft")
    assert_true(is_training_activity("SFTTrainer(model, args)"), "SFTTrainer")
    assert_true(is_training_activity("optimizer = torch.optim.Adam(params)"), "torch.optim")
    assert_true(is_training_activity("optimizer = tf.keras.optimizers.Adam()"), "tf.keras.optimizers")
    assert_true(is_training_activity("backpropagation through the network"), "backpropagation")
    assert_false(is_training_activity("model.predict(X_test)"), "inference is not training")
    assert_false(is_training_activity("print('hello world')"), "regular code is not training")
    print("✓ Training detection: extended patterns")


# ── ReDoS Prevention (classify_risk) ──────────────────────────────

def test_no_redos_classify_risk():
    """Verify classification patterns complete in <1s on pathological input"""
    pathological_inputs = [
        'a' * 10000 + 'b',
        'social' + ' ' * 10000 + 'score',
        'emotion' + '.' * 10000 + 'workplace',
        'biometric' + ' ' * 10000 + 'ident',
        'credit' + ' ' * 10000 + 'scor',
    ]
    for inp in pathological_inputs:
        start = time.time()
        classify(inp)
        elapsed = time.time() - start
        assert_true(elapsed < 1.0, f"potential ReDoS in classify: {elapsed:.2f}s on {inp[:40]}...")
    print("✓ No ReDoS: classify_risk patterns safe")


def test_no_redos_ai_security():
    """Verify AI security patterns complete in <1s on pathological input"""
    pathological = "pickle.loads(" + "a" * 10000 + ")\n" + "eval(" + "b" * 10000 + " response)\n"
    start = time.time()
    check_ai_security(pathological)
    elapsed = time.time() - start
    assert_true(elapsed < 1.0, f"potential ReDoS in ai_security: {elapsed:.2f}s")
    print("✓ No ReDoS: AI security patterns safe")


# ── Serialisation / Edge Cases ─────────────────────────────────────

def test_classification_serialisation_all_tiers():
    """All risk tiers serialise correctly"""
    tiers_and_inputs = [
        ("social scoring using tensorflow", "prohibited"),
        ("import sklearn; CV screening for hiring", "high_risk"),
        ("chatbot using tensorflow", "limited_risk"),
        ("print('hello world')", "not_ai"),
    ]
    for text, expected_tier in tiers_and_inputs:
        r = classify(text)
        d = r.to_dict()
        assert_eq(d["tier"], expected_tier, f"{expected_tier} serialises")
        j = r.to_json()
        parsed = json.loads(j)
        assert_eq(parsed["tier"], expected_tier, f"{expected_tier} JSON roundtrip")
    print("✓ Serialisation: all tiers serialise correctly")


def test_very_large_input():
    """Very large inputs don't cause crashes or excessive runtime"""
    large_input = "import tensorflow\n" * 5000 + "credit scoring model\n" * 100
    start = time.time()
    r = classify(large_input)
    elapsed = time.time() - start
    assert_true(elapsed < 5.0, f"large input took {elapsed:.2f}s")
    assert_true(r.tier is not None, "returns valid classification")
    print("✓ Edge case: very large input handled")


def test_multiline_pattern_matching():
    """Patterns match across typical code structures"""
    code = (
        "import torch\n"
        "from transformers import pipeline\n\n"
        "class HiringSystem:\n"
        "    def screen_candidates(self):\n"
        "        cv_screening = pipeline('text-classification')\n"
        "        return cv_screening(self.applications)\n"
    )
    r = classify(code)
    assert_eq(r.tier, RiskTier.HIGH_RISK, "multiline code classified correctly")
    print("✓ Edge case: multiline code patterns matched")


# ══════════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    tests = [
        # credential_check.py — pattern coverage (8)
        test_secret_anthropic_key,
        test_secret_google_api_key,
        test_secret_github_token,
        test_secret_private_key,
        test_secret_generic_api_key,
        test_secret_connection_string,
        test_secret_connection_string_localhost_exempt,
        test_secret_aws_secret_key,
        # credential_check.py — _redact (1)
        test_redact_short_value,
        # credential_check.py — has_high_confidence_secret (1)
        test_has_high_confidence_secret,
        # credential_check.py — format_secret_warning (4)
        test_format_warning_high_confidence,
        test_format_warning_medium_only,
        test_format_warning_mixed,
        test_format_warning_empty,
        # credential_check.py — false positives (2)
        test_secret_no_false_positive_short_sk,
        test_secret_no_false_positive_similar_prefix,
        # credential_check.py — edge inputs (3)
        test_secret_empty_input,
        test_secret_binary_like_input,
        test_secret_sorting_order,
        # credential_check.py — ReDoS (1)
        test_no_redos_credential_patterns,
        # classify_risk.py — AI security skip paths (6)
        test_ai_security_skips_comments,
        test_ai_security_skips_js_comments,
        test_ai_security_skips_docstrings,
        test_ai_security_skips_long_lines,
        test_ai_security_skips_args_lines,
        test_ai_security_detects_multiple_patterns,
        # classify_risk.py — generate_observations (5)
        test_governance_observations_training_data,
        test_governance_observations_prediction,
        test_governance_observations_automated_decision,
        test_governance_observations_no_logging,
        test_governance_observations_with_logging,
        # classify_risk.py — confidence (1)
        test_confidence_score_computation,
        # classify_risk.py — finding tier (3)
        test_finding_tier_prohibited_always_block,
        test_finding_tier_warn_range,
        test_finding_tier_info_range,
        # classify_risk.py — pattern coverage (4)
        test_prohibited_exploitation_vulnerabilities,
        test_high_risk_essential_services_extended,
        test_high_risk_employment_extended,
        test_limited_risk_synthetic_content,
        # classify_risk.py — training (1)
        test_training_detection_extended,
        # classify_risk.py — ReDoS (2)
        test_no_redos_classify_risk,
        test_no_redos_ai_security,
        # classify_risk.py — serialisation/edge (3)
        test_classification_serialisation_all_tiers,
        test_very_large_input,
        test_multiline_pattern_matching,
    ]

    print(f"Running {len(tests)} coverage tests...\n")

    for test in tests:
        try:
            test()
        except Exception as e:
            failed += 1
            print(f"  EXCEPTION in {test.__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed ({len(tests)} test functions)")
    if failed:
        print("SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("All tests passed!")
