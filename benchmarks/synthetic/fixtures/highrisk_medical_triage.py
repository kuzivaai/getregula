# synthetic-test-fixture
"""Synthetic fixture: medical devices / health.
Expected: high_risk."""


def medical_diagnosis_support(radiograph):
    """Returns a diagnostic impression used in the patient record."""
    return _cnn.predict(radiograph)
