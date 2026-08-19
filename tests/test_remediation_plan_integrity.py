#!/usr/bin/env python3
"""A completion record must refer to a task that exists.

`regula plan --done BOGUS-ID` printed "Marked BOGUS-ID as completed." and
exited 0, having written `{"BOGUS-ID": {"status": "completed"}}` into
`.regula/plan-status.json`. Nothing checked the id.

The defect was wider than a missing id check. `cmd_plan` builds
`empty_decision("eu", "cli:plan")` unconditionally, so applicability never
resolves there and the command emits no task list at all. Every id was
therefore bogus, not just the malformed ones, and `--status` already declined
to interpret the very file `--done` was writing. In a tool whose `.regula/`
output is read as evidence, manufacturing a record with no referent is worse
than emitting nothing.

Two layers are pinned here, because either alone leaves the class open:
  - `mark_task_done` requires the id set of the plan the mark belongs to.
  - `cmd_plan --done` refuses, because it has no plan to mark against.

These use `tempfile` rather than pytest's `tmp_path` deliberately, so the
custom runner in `test_classification.py` executes them too. It skips any test
taking a pytest fixture.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import remediation_plan  # noqa: E402
from errors import UsageError  # noqa: E402


def _plan_with(ids):
    return {"tasks": [{"id": i} for i in ids]}


def test_mark_task_done_refuses_an_id_no_plan_contains():
    """The original defect, at the library boundary."""
    with tempfile.TemporaryDirectory() as d:
        try:
            remediation_plan.mark_task_done(
                d, "BOGUS-ID",
                remediation_plan.plan_task_ids(_plan_with(["TASK-001"])))
        except UsageError as e:
            assert "BOGUS-ID" in str(e), str(e)
            assert "TASK-001" in str(e), "the message must name what is valid"
        else:
            raise AssertionError(
                "mark_task_done accepted an id present in no plan, which is "
                "the defect: it writes a completion record with no referent")
        assert not (Path(d) / ".regula" / "plan-status.json").exists(), (
            "a refused mark must leave no file behind")
    print("  PASS  mark_task_done refuses an id no plan contains")


def test_mark_task_done_refuses_when_the_plan_is_empty():
    """An empty plan makes every id invalid, and the message must say so."""
    with tempfile.TemporaryDirectory() as d:
        try:
            remediation_plan.mark_task_done(d, "TASK-001", set())
        except UsageError as e:
            assert "no tasks" in str(e), str(e)
        else:
            raise AssertionError(
                "mark_task_done accepted an id against an empty plan")
    print("  PASS  mark_task_done refuses every id when the plan is empty")


def test_mark_task_done_still_marks_a_real_task():
    """Control in the other direction. The check must not refuse valid work."""
    with tempfile.TemporaryDirectory() as d:
        status = remediation_plan.mark_task_done(
            d, "TASK-002",
            remediation_plan.plan_task_ids(_plan_with(["TASK-001", "TASK-002"])))
        assert status["TASK-002"]["status"] == "completed", status
        written = json.loads(
            (Path(d) / ".regula" / "plan-status.json").read_text(encoding="utf-8"))
        assert written["TASK-002"]["status"] == "completed", written
        assert "completed_at" in written["TASK-002"], written
    print("  PASS  control: a real task id is still marked and persisted")


def test_plan_task_ids_matches_what_generate_plan_emits():
    """The helper must read the real shape, not an assumed one.

    If `generate_plan` renames its id field, a hand-written id set silently
    goes empty and every mark starts failing (or, worse, stops being checked).
    """
    findings = [
        {"file": "src/predict.py", "line": 23, "tier": "high_risk",
         "category": "employment", "description": "AI employment screening",
         "indicators": ["employment"], "articles": ["Article 9"]},
    ]
    gap = {"articles": {"9": {"title": "Risk Management", "score": 0,
                              "gaps": ["No risk assessment found"]}},
           "overall_score": 0}
    plan = remediation_plan.generate_plan(findings, gap, project_name="p")
    ids = remediation_plan.plan_task_ids(plan)
    assert ids, "generate_plan produced tasks but plan_task_ids saw none"
    assert len(ids) == len(plan["tasks"]), "ids must be unique per task"
    with tempfile.TemporaryDirectory() as d:
        for task_id in ids:
            remediation_plan.mark_task_done(d, task_id, ids)
    print(f"  PASS  all {len(ids)} generated ids are accepted by mark_task_done")


def test_cli_plan_done_refuses_and_writes_nothing():
    """End to end, because the library fix alone would not have caught this.

    The CLI could satisfy `mark_task_done` by passing an id set it invented,
    and while writing this test it briefly did exactly that. This runs the
    real command and checks the two things a user sees: the exit code, and
    whether a file appeared.
    """
    with tempfile.TemporaryDirectory() as d:
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.cli", "plan",
             "--project", d, "--done", "BOGUS-ID"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=180)
        assert proc.returncode == 2, (
            f"expected exit 2, got {proc.returncode}\n{proc.stdout}\n{proc.stderr}")
        assert "Marked" not in proc.stdout, (
            f"the command reported success it did not achieve: {proc.stdout!r}")
        assert not (Path(d) / ".regula" / "plan-status.json").exists(), (
            "a refused mark wrote a status file anyway")
    print("  PASS  regula plan --done refuses, exits 2, and writes nothing")


if __name__ == "__main__":
    for t in (test_mark_task_done_refuses_an_id_no_plan_contains,
              test_mark_task_done_refuses_when_the_plan_is_empty,
              test_mark_task_done_still_marks_a_real_task,
              test_plan_task_ids_matches_what_generate_plan_emits,
              test_cli_plan_done_refuses_and_writes_nothing):
        t()
