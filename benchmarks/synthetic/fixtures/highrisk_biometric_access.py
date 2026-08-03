# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 1 — biometric identification.
Expected: high_risk."""

import numpy as np


class TurnstileIdentityGate:
    """Identifies staff at building entry from a face template."""

    def __init__(self, gallery):
        self.gallery = gallery

    def facial_recognition_match(self, probe_embedding):
        scores = [np.dot(probe_embedding, t) for t in self.gallery]
        best = int(np.argmax(scores))
        return best if scores[best] > 0.82 else None

    def admit(self, frame):
        subject = self.facial_recognition_match(embed(frame))
        return {"admit": subject is not None, "subject_id": subject}
