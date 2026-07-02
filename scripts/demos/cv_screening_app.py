"""Minimal CV-screening reference app for Regula.

This example intentionally triggers an EU AI Act Annex III (Category 4,
Employment) classification when scanned with `regula check`. It exists so
that new Regula users have a runnable fixture to demonstrate high-risk
detection on their own machine — not as production code.

What it does
------------
Loads a small in-memory dataset of job applications, trains a logistic
regression on toy features, and ranks candidates by predicted score.
No network calls, no persistence, no real PII.

Why it is high-risk under the EU AI Act
---------------------------------------
Annex III (4)(a) lists "AI systems intended to be used for recruitment
or selection of natural persons, in particular to place targeted job
advertisements, to analyse and filter job applications, and to evaluate
candidates" as high-risk use cases. If this code were deployed for real
hiring, Articles 9–15 would apply (risk management, data governance,
documentation, logging, transparency, human oversight, accuracy).

See: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689
"""
from __future__ import annotations

from dataclasses import dataclass

from sklearn.linear_model import LogisticRegression


@dataclass
class JobApplicant:
    years_experience: float
    relevant_skills: int
    education_level: int


def train_cv_screening_model(
    applicants: list[JobApplicant], outcomes: list[int]
) -> LogisticRegression:
    """Train a toy model that screens resumes by predicted hire outcome."""
    features = [
        [a.years_experience, a.relevant_skills, a.education_level]
        for a in applicants
    ]
    model = LogisticRegression(max_iter=200)
    model.fit(features, outcomes)
    return model


def rank_candidates(
    model: LogisticRegression, applicants: list[JobApplicant]
) -> list[tuple[JobApplicant, float]]:
    """Score and rank job candidates by predicted probability of hire."""
    features = [
        [a.years_experience, a.relevant_skills, a.education_level]
        for a in applicants
    ]
    probabilities = model.predict_proba(features)[:, 1]
    scored = list(zip(applicants, probabilities))
    return sorted(scored, key=lambda pair: pair[1], reverse=True)


if __name__ == "__main__":
    training_applicants = [
        JobApplicant(years_experience=1.0, relevant_skills=2, education_level=1),
        JobApplicant(years_experience=5.0, relevant_skills=7, education_level=2),
        JobApplicant(years_experience=8.0, relevant_skills=9, education_level=3),
        JobApplicant(years_experience=2.0, relevant_skills=3, education_level=2),
    ]
    training_outcomes = [0, 1, 1, 0]

    screening_model = train_cv_screening_model(training_applicants, training_outcomes)

    new_applicants = [
        JobApplicant(years_experience=3.0, relevant_skills=5, education_level=2),
        JobApplicant(years_experience=6.0, relevant_skills=8, education_level=3),
    ]
    ranked = rank_candidates(screening_model, new_applicants)
    for applicant, score in ranked:
        print(f"score={score:.3f}  {applicant}")
