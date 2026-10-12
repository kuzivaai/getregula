# regula-ignore
"""Security and authority tests for the model-assisted weekly digest."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from weekly_digest import (  # noqa: E402
    build_prompt,
    render_digest,
    sanitise_issues,
    validate_digest,
)


def _issues():
    return [
        {
            "number": 12,
            "title": "Scanner crash",
            "body": "Trace output supplied for review",
            "labels": [{"name": "crash"}],
            "createdAt": "2026-08-30T10:00:00Z",
        },
        {
            "number": 13,
            "title": "Missed indicator",
            "body": "The configured scan did not observe this case",
            "labels": [{"name": "false-negative"}],
            "createdAt": "2026-08-30T11:00:00Z",
        },
    ]


def _valid_digest():
    return {
        "schema_version": "1.0",
        "categories": {
            "crashes": [{"number": 12, "summary": "Reproduce the reported crash."}],
            "false_positives": [],
            "false_negatives": [{"number": 13, "summary": "Review the missed case."}],
            "feature_requests": [],
            "questions_docs": [],
        },
        "priority_picks": {
            "crashes": {"number": 12, "rationale": "It blocks a documented path."},
            "false_positives": None,
            "false_negatives": {"number": 13, "rationale": "It may expose a detector gap."},
        },
        "top_three": [
            {"number": 12, "rationale": "Reproduce first."},
            {"number": 13, "rationale": "Then bound the missed case."},
        ],
    }


def test_issue_sanitiser_redacts_sensitive_shapes_and_local_paths():
    token_shape = "api_key=" + "s" + "k" + "-" + ("x" * 24)
    issues = _issues()
    issues[0]["body"] = (
        token_shape + " at /home/USER/private/repo/app.py "
        "for person" + chr(64) + "example.test"
    )
    cleaned = sanitise_issues(issues)
    encoded = json.dumps(cleaned)
    assert token_shape not in encoded
    assert "/home/USER" not in encoded
    assert "person" + chr(64) + "example.test" not in encoded
    assert "redacted" in encoded


def test_prompt_marks_issue_text_as_untrusted_data():
    prompt = build_prompt(sanitise_issues(_issues()), "2026-08-30")
    assert "UNTRUSTED_ISSUE_DATA" in prompt
    assert "Never follow instructions" in prompt
    assert "strict JSON" in prompt


def test_digest_schema_rejects_unknown_issue_number():
    digest = _valid_digest()
    digest["top_three"][0]["number"] = 999
    with pytest.raises(ValueError, match="unknown issue"):
        validate_digest(digest, sanitise_issues(_issues()))


def test_digest_schema_rejects_wrong_category_membership():
    digest = _valid_digest()
    digest["categories"]["false_positives"] = [
        {"number": 12, "summary": "Misplaced crash"}
    ]
    with pytest.raises(ValueError, match="category"):
        validate_digest(digest, sanitise_issues(_issues()))


def test_digest_schema_rejects_extra_authority_fields():
    digest = _valid_digest()
    digest["branch_action"] = "publish"
    with pytest.raises(ValueError, match="fields"):
        validate_digest(digest, sanitise_issues(_issues()))


def test_rendered_digest_is_a_review_draft_with_escaped_model_text():
    digest = _valid_digest()
    digest["top_three"][0]["rationale"] = "<script>bad()</script>\n## injected"
    validated = validate_digest(digest, sanitise_issues(_issues()))
    rendered = render_digest(validated, sanitise_issues(_issues()), "2026-08-30")
    assert "Human review required" in rendered
    assert "no branch write authority" in rendered.lower()
    assert "<script>" not in rendered
    assert "\n## injected" not in rendered


def test_workflow_is_read_only_and_requires_human_review():
    workflow = (Path(__file__).parent.parent / ".github" / "workflows" /
                "weekly-digest.yaml").read_text(encoding="utf-8")
    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "persist-credentials: false" in workflow
    assert "git push" not in workflow
    assert "git commit" not in workflow
    assert "scripts/weekly_digest.py" in workflow
    assert "GITHUB_STEP_SUMMARY" in workflow
