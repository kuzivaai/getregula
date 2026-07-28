# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 3 — education.
Expected: high_risk."""


def student_assessment_grade(essay_text, rubric):
    """Assigns the final grade of record for a submitted essay."""
    return _grader.grade(essay_text, rubric)
