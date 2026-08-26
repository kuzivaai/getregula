# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 5(d) — emergency services triage.
Expected: high_risk."""


def emergency_dispatch_priority(call_transcript, caller_location):
    """Triages 999 calls and orders ambulance dispatch."""
    severity = _triage_model.predict(call_transcript)
    return {"priority": severity, "dispatch": severity >= 3}
