# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 3 — education.
Expected: high_risk."""


def proctoring_flag_candidate(webcam_stream, exam_id):
    """Monitors a remote exam and flags suspected cheating for invalidation."""
    gaze = gaze_tracker(webcam_stream)
    return {"exam_id": exam_id, "cheating_probability": _clf.predict_proba(gaze)}
