"""Deployment-contract tests for the GitHub Pages workflow."""

from __future__ import annotations

import re
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO / ".github" / "workflows"
PAGES_WORKFLOW = WORKFLOWS / "pages.yml"


def _pages_workflow() -> str:
    return PAGES_WORKFLOW.read_text(encoding="utf-8")


def test_pages_workflow_is_the_only_pages_deployer():
    deployers = sorted(
        path.name
        for path in WORKFLOWS.iterdir()
        if path.is_file()
        and "actions/deploy-pages@" in path.read_text(encoding="utf-8")
    )
    assert deployers == ["pages.yml"]


def test_pages_workflow_waits_for_successful_main_push_ci():
    workflow = _pages_workflow()
    required_fragments = (
        "workflow_run:",
        'workflows: ["CI"]',
        "types: [completed]",
        "branches: [main]",
        "github.event.workflow_run.conclusion == 'success'",
        "github.event.workflow_run.event == 'push'",
        "github.event.workflow_run.head_branch == 'main'",
        "github.event.workflow_run.head_sha",
        "github.ref == 'refs/heads/main'",
    )
    for fragment in required_fragments:
        assert fragment in workflow


def test_pages_workflow_has_a_pinned_build_to_deploy_chain():
    workflow = _pages_workflow()
    for action in (
        "actions/checkout",
        "actions/configure-pages",
        "actions/upload-pages-artifact",
        "actions/deploy-pages",
    ):
        assert re.search(
            rf"uses:\s*{re.escape(action)}@[0-9a-f]{{40}}(?:\s|$)", workflow
        )
    assert "needs: build" in workflow
    assert "group: pages" in workflow
    assert "cancel-in-progress: false" in workflow
    assert re.search(
        r"path:\s*['\"]?\.?/?site['\"]?\s*$", workflow, re.MULTILINE
    )


def test_pages_custom_domain_source_matches_public_canonical_domain():
    cname = REPO / "site" / "CNAME"
    assert cname.read_text(encoding="utf-8") == "getregula.com\n"
