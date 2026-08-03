# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 1 — biometric categorisation.
Expected: high_risk."""


def voice_recognition_enrol(caller_audio, customer_id):
    """Enrol a caller voiceprint for telephone banking identity checks."""
    return {"customer_id": customer_id, "voiceprint": _spectral(caller_audio)}


def verify_caller(caller_audio, stored_voiceprint):
    return _distance(_spectral(caller_audio), stored_voiceprint) < 0.15
