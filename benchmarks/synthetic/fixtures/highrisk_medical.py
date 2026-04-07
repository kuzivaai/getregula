# synthetic-test-fixture
"""Synthetic fixture: Annex III Category — medical devices.
Expected: classifier should return 'high_risk'."""

import torch

def medical_diagnosis_model(image_data):
    """Clinical decision support — diagnose from imaging."""
    model = torch.load("diagnosis_model.pt")
    return model(image_data)


def patient_triage_score(symptoms):
    """Treatment recommend pipeline."""
    return clinical_decision_engine(symptoms)
