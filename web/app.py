"""
Regula Assess — Web UI

A minimal Flask app that wraps the CLI `regula assess` questionnaire
for non-technical users. Stateless, no database, no auth.

Run:
    pip install flask
    python app.py
"""

import sys
from pathlib import Path

# Allow importing from scripts/ using the same bare-import convention
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from flask import Flask, render_template, request, session, redirect, url_for
from assess import (
    Q_USES_AI,
    Q_EU_USERS,
    Q_PROHIBITED,
    Q_HIGH_RISK,
    Q_TRANSPARENCY,
    Q_NON_EU,
    TIER_NOT_IN_SCOPE,
    TIER_NOT_IN_SCOPE_EU,
    TIER_PROHIBITED,
    TIER_HIGH,
    TIER_LIMITED,
    TIER_MINIMAL,
    format_result,
)

app = Flask(__name__)
app.secret_key = "regula-assess-web-session-key"

# Ordered question flow — mirrors run_interactive() in assess.py
QUESTIONS = [
    {"key": "uses_ai", "text": Q_USES_AI},
    {"key": "eu_users", "text": Q_EU_USERS},
    {"key": "prohibited", "text": Q_PROHIBITED},
    {"key": "high_risk_domain", "text": Q_HIGH_RISK},
    {"key": "transparency_trigger", "text": Q_TRANSPARENCY},
    {"key": "non_eu_provider", "text": Q_NON_EU},
]


def _determine_result(answers: dict) -> dict:
    """Replicate the short-circuit logic from assess.run_interactive()."""
    if answers.get("uses_ai") == "no":
        return {"tier": TIER_NOT_IN_SCOPE, "non_eu_provider": False}
    if answers.get("eu_users") == "no":
        return {"tier": TIER_NOT_IN_SCOPE_EU, "non_eu_provider": False}
    if answers.get("prohibited") == "yes":
        return {"tier": TIER_PROHIBITED, "non_eu_provider": False}
    if answers.get("high_risk_domain") == "yes":
        non_eu = answers.get("non_eu_provider") == "yes"
        return {"tier": TIER_HIGH, "non_eu_provider": non_eu}
    if answers.get("transparency_trigger") == "yes":
        return {"tier": TIER_LIMITED, "non_eu_provider": False}
    return {"tier": TIER_MINIMAL, "non_eu_provider": False}


def _next_question_key(answers: dict) -> str | None:
    """Return the key of the next question to ask, or None if done."""
    if "uses_ai" not in answers:
        return "uses_ai"
    if answers["uses_ai"] == "no":
        return None
    if "eu_users" not in answers:
        return "eu_users"
    if answers["eu_users"] == "no":
        return None
    if "prohibited" not in answers:
        return "prohibited"
    if answers["prohibited"] == "yes":
        return None
    if "high_risk_domain" not in answers:
        return "high_risk_domain"
    if answers["high_risk_domain"] == "yes":
        if "non_eu_provider" not in answers:
            return "non_eu_provider"
        return None
    if "transparency_trigger" not in answers:
        return "transparency_trigger"
    return None


def _question_number(answers: dict) -> int:
    """How many questions answered so far (for progress display)."""
    return len(answers)


def _get_question(key: str) -> dict:
    for q in QUESTIONS:
        if q["key"] == key:
            return q
    return QUESTIONS[0]


# Human-readable tier labels
TIER_LABELS = {
    TIER_NOT_IN_SCOPE: "Not in Scope",
    TIER_NOT_IN_SCOPE_EU: "Not Currently in Scope",
    TIER_MINIMAL: "Minimal Risk",
    TIER_LIMITED: "Limited Risk",
    TIER_HIGH: "High Risk",
    TIER_PROHIBITED: "Prohibited",
}

TIER_COLOURS = {
    TIER_NOT_IN_SCOPE: "#10b981",
    TIER_NOT_IN_SCOPE_EU: "#10b981",
    TIER_MINIMAL: "#10b981",
    TIER_LIMITED: "#f59e0b",
    TIER_HIGH: "#ef4444",
    TIER_PROHIBITED: "#ef4444",
}


@app.route("/")
def index():
    session.clear()
    return render_template("assess.html", page="intro")


@app.route("/start")
def start():
    session["answers"] = {}
    return redirect(url_for("question"))


@app.route("/question", methods=["GET", "POST"])
def question():
    answers = session.get("answers", {})

    if request.method == "POST":
        key = request.form.get("key")
        value = request.form.get("answer")
        if key and value in ("yes", "no"):
            answers[key] = value
            session["answers"] = answers

    next_key = _next_question_key(answers)
    if next_key is None:
        return redirect(url_for("result"))

    q = _get_question(next_key)
    total = 5  # max questions a user can see
    current = _question_number(answers) + 1

    return render_template(
        "assess.html",
        page="question",
        question=q,
        current=current,
        total=total,
    )


@app.route("/result")
def result():
    answers = session.get("answers", {})
    if not answers:
        return redirect(url_for("index"))

    res = _determine_result(answers)
    tier = res["tier"]
    non_eu = res["non_eu_provider"]
    result_text = format_result(tier, non_eu)

    return render_template(
        "assess.html",
        page="result",
        tier=tier,
        tier_label=TIER_LABELS.get(tier, tier),
        tier_colour=TIER_COLOURS.get(tier, "#3b82f6"),
        non_eu=non_eu,
        result_text=result_text,
        answers=answers,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
