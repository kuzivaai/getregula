#!/usr/bin/env python3
"""Test suite for Regula classification engine"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from classify_risk import classify, RiskTier, is_ai_related


def test_ai_detection():
    assert is_ai_related("import tensorflow")
    assert is_ai_related("import torch")
    assert is_ai_related("from openai import OpenAI")
    assert not is_ai_related("print('hello')")
    print("✓ AI detection tests passed")


def test_prohibited():
    r = classify("social credit scoring using tensorflow")
    assert r.tier == RiskTier.PROHIBITED
    r = classify("emotion detection workplace monitoring using torch")
    assert r.tier == RiskTier.PROHIBITED
    print("✓ Prohibited classification tests passed")


def test_high_risk():
    r = classify("import sklearn; CV screening for hiring")
    assert r.tier == RiskTier.HIGH_RISK
    assert "9" in r.applicable_articles
    r = classify("import torch; credit scoring model")
    assert r.tier == RiskTier.HIGH_RISK
    print("✓ High-risk classification tests passed")


def test_limited_risk():
    r = classify("import openai; build a chatbot")
    assert r.tier == RiskTier.LIMITED_RISK
    r = classify("import torch; deepfake generation")
    assert r.tier == RiskTier.LIMITED_RISK
    print("✓ Limited-risk classification tests passed")


def test_minimal_risk():
    r = classify("import tensorflow; recommendation engine")
    assert r.tier == RiskTier.MINIMAL_RISK
    print("✓ Minimal-risk classification tests passed")


if __name__ == "__main__":
    test_ai_detection()
    test_prohibited()
    test_high_risk()
    test_limited_risk()
    test_minimal_risk()
    print("\n✅ All tests passed!")
