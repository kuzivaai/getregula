"""AI-assisted hiring and employee management system.

Fixture for high-risk employment AI (Annex III, Category 4).
When scanned from tests/ directory, scores are deprioritised by -40 (INFO tier).
When copied outside tests/ (as test_exit_code_warn_tier does), scores WARN tier.
"""
import torch
from transformers import pipeline
from sklearn.ensemble import GradientBoostingClassifier

# Employment screening — Annex III, Category 4
candidate_screening_model = GradientBoostingClassifier()

def screen_cv_candidates(resumes):
    """Automated CV screening for hiring decisions."""
    classifier = pipeline("text-classification")
    scores = classifier([r["text"] for r in resumes])
    return [r for r, s in zip(resumes, scores) if s["score"] > 0.7]

def rank_job_applicants(applications):
    """Automated ranking of job applicants for hiring decisions."""
    classifier = pipeline("text-classification")
    scores = classifier([app["cover_letter"] for app in applications])
    return sorted(applications, key=lambda a: scores[applications.index(a)]["score"])

def evaluate_employee_performance(employee_data):
    """AI-driven employee performance evaluation for promotion decisions."""
    model = torch.load("performance_model.pt")
    return model(employee_data)
