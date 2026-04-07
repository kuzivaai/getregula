# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 1 — biometric identification.
Expected: classifier should return 'high_risk'."""

import face_recognition

def biometric_identification_pipeline(image):
    """Run facial recognition against the watchlist."""
    encodings = face_recognition.face_encodings(image)
    return match_against_watchlist(encodings)


def fingerprint_recognition_check(scan_data):
    """Match fingerprint against database."""
    return fingerprint_recognition_match(scan_data)
