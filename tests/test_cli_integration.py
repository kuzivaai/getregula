"""CLI integration tests — exercise top commands via subprocess."""
import os
import subprocess
import sys
import tempfile

import pytest


def run_cli(*args, env_overrides=None):
    """Run regula CLI and return (returncode, stdout, stderr)."""
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli"] + list(args),
        capture_output=True, text=True, timeout=60,
        cwd=str(__import__("pathlib").Path(__file__).resolve().parents[1]),
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def test_check_sample_high_risk():
    rc, out, err = run_cli("check", "tests/fixtures/sample_high_risk")
    assert rc == 0
    assert "high" in out.lower() or "findings" in out.lower() or "risk" in out.lower()


def test_assess_auto():
    rc, out, err = run_cli("assess", "--answers", "yes,yes,no,yes,no")
    assert rc == 0
    assert "high" in out.lower() or "risk" in out.lower()


def test_plan():
    rc, out, err = run_cli("plan", "--project", "tests/fixtures/sample_high_risk")
    assert rc == 0


def test_gap():
    rc, out, err = run_cli("gap", "--project", "tests/fixtures/sample_high_risk")
    assert rc == 0
    assert "Art" in out or "article" in out.lower()


def test_self_test():
    rc, out, err = run_cli("self-test")
    assert rc == 0
    assert "passed" in out.lower() or "pass" in out.lower()


def test_doctor():
    rc, out, err = run_cli("doctor")
    assert rc == 0
    assert "passed" in out.lower() or "pass" in out.lower()


def test_sbom():
    rc, out, err = run_cli("sbom")
    assert rc == 0


def test_handoff_garak(tmp_path):
    """regula handoff garak — write to tmp --output so we do not mutate
    the committed fixture directory. `regula handoff` defaults to
    writing inside the project dir; tests must override."""
    out = tmp_path / "garak.regula.yaml"
    rc, stdout, stderr = run_cli(
        "handoff", "garak", "tests/fixtures/sample_high_risk",
        "--output", str(out),
    )
    assert rc == 0
    assert out.exists()


def test_regwatch():
    rc, out, err = run_cli("regwatch")
    assert rc == 0


def test_inventory():
    rc, out, err = run_cli("inventory", "tests/fixtures/sample_high_risk")
    assert rc == 0


def test_governance(tmp_path):
    out = tmp_path / "AI_GOVERNANCE.md"
    rc, stdout, stderr = run_cli("governance", "--project", "tests/fixtures/sample_high_risk", "--output", str(out))
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "AI Governance" in content or "governance" in content.lower()
    assert "scaffold" in content.lower() or "TO BE COMPLETED" in content


def test_model_card(tmp_path):
    out = tmp_path / "MODEL_CARD.md"
    rc, stdout, stderr = run_cli("model-card", "--project", "tests/fixtures/sample_high_risk", "--output", str(out))
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "Model Card" in content or "model" in content.lower()


def test_governance_empty_project(tmp_path):
    out = tmp_path / "AI_GOVERNANCE.md"
    empty = tmp_path / "empty_proj"
    empty.mkdir()
    rc, stdout, stderr = run_cli("governance", "--project", str(empty), "--output", str(out))
    assert rc == 0
    assert out.exists()  # should produce valid scaffold even for empty project


def test_model_card_empty_project(tmp_path):
    out = tmp_path / "MODEL_CARD.md"
    empty = tmp_path / "empty_proj"
    empty.mkdir()
    rc, stdout, stderr = run_cli("model-card", "--project", str(empty), "--output", str(out))
    assert rc == 0
    assert out.exists()


def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmp:
        rc, out, err = run_cli("check", tmp)
        assert rc == 0  # should not crash on empty dir


def test_github_annotations_emitted_under_github_actions():
    """With GITHUB_ACTIONS=true and --ci, each finding gets a workflow command.

    This lets CI surface findings as inline PR annotations without needing
    SARIF/CodeQL setup. Uses the real high-risk cv-screening-app fixture so
    the test is grounded in the actual Regula output — no fabricated messages.
    """
    rc, stdout, stderr = run_cli(
        "check", "--ci", "examples/cv-screening-app",
        env_overrides={"GITHUB_ACTIONS": "true"},
    )
    # CI mode exits 1 on WARN or BLOCK findings.
    assert rc == 1, f"expected rc=1 (WARN in CI mode), got {rc}\nstderr={stderr}"
    # Exactly one high-risk WARN finding expected for cv-screening-app.
    warning_lines = [ln for ln in stdout.splitlines() if ln.startswith("::warning")]
    assert len(warning_lines) == 1, f"expected 1 ::warning, got {len(warning_lines)}\nstdout={stdout}"
    ann = warning_lines[0]
    # Path must resolve to the file inside the scanned project, not just `app.py`.
    assert "file=examples/cv-screening-app/app.py" in ann, ann
    assert ",line=" in ann, ann
    # Message content must match what the scanner actually produced.
    assert "Employment" in ann, ann


def test_github_annotations_suppressed_without_github_actions():
    """Without GITHUB_ACTIONS=true, --ci mode does NOT emit workflow commands.

    Local runs should stay quiet so a developer running `regula check --ci`
    at their terminal isn't spammed with ::warning lines.
    """
    rc, stdout, stderr = run_cli(
        "check", "--ci", "examples/cv-screening-app",
        env_overrides={"GITHUB_ACTIONS": ""},
    )
    assert rc == 1
    assert not any(
        ln.startswith("::warning") or ln.startswith("::error") or ln.startswith("::notice")
        for ln in stdout.splitlines()
    ), f"expected zero workflow commands, got stdout={stdout}"


def test_github_annotations_suppressed_without_ci_flag():
    """GITHUB_ACTIONS=true without --ci should not emit annotations either.

    Annotations are a CI-mode-only feature — the `regula check` default is
    reserved for the human-readable report.
    """
    rc, stdout, stderr = run_cli(
        "check", "examples/cv-screening-app",
        env_overrides={"GITHUB_ACTIONS": "true"},
    )
    # No --ci means WARN does not fail the run.
    assert rc == 0
    assert not any(
        ln.startswith("::warning") or ln.startswith("::error") or ln.startswith("::notice")
        for ln in stdout.splitlines()
    ), f"expected zero workflow commands, got stdout={stdout}"


def test_examples_customer_chatbot_prints_limited_risk_row():
    """The LIMITED-RISK section must show the finding row, not just the header.

    Regression for the bug where `regula check examples/customer-chatbot`
    printed the `LIMITED-RISK:` header with no row beneath — the renderer
    was silently skipping INFO-tier limited-risk findings unless --verbose
    was set, while still emitting the section header. Every other per-tier
    section (prohibited, credentials, high_risk, autonomy) prints its
    rows unconditionally; limited-risk was the odd one out.

    After the fix, the section header is followed by a row in the same
    format used for credential/autonomy findings:
        [tier] [score] file:line — message
    """
    import re
    rc, stdout, stderr = run_cli("check", "examples/customer-chatbot")
    assert rc == 0, f"expected rc=0, got {rc}\nstderr={stderr}"
    assert "LIMITED-RISK" in stdout, f"missing LIMITED-RISK header:\n{stdout}"
    row_pattern = re.compile(
        r"^\s+\[(INFO|WARN|BLOCK)\]\s+\[\s*\d+\]\s+\S+:\d+\s+—\s+.+$",
        re.MULTILINE,
    )
    after_header = stdout.split("LIMITED-RISK", 1)[1]
    rows = row_pattern.findall(after_header)
    assert rows, (
        f"LIMITED-RISK header printed with no finding row underneath:\n{stdout}"
    )


def test_examples_code_completion_tool_scans_one_file():
    """examples/code-completion-tool must scan exactly 1 file and produce
    a genuinely clean result (zero findings of any tier).

    Regression for the bug where `regula check examples/code-completion-tool`
    reported `Files scanned: 0 (test files excluded — use --no-skip-tests
    to include)`. Two compounding causes:

      * an older release missing the scan_files.last_stats telemetry
        attribute, so the CLI fell back to len(unique files with findings)
        which is 0 for a genuinely clean scan;
      * the "test files excluded" suffix fired on any total_files==0 +
        skip_tests_active combination, regardless of whether test files
        were actually skipped — misleadingly blaming the heuristic when
        the real cause was the missing telemetry.

    After the fix, last_stats carries files_scanned + tests_skipped, and
    the suffix only appears when tests_skipped > 0.
    """
    import re
    rc, stdout, stderr = run_cli("check", "examples/code-completion-tool")
    assert rc == 0, f"expected rc=0, got {rc}\nstderr={stderr}"
    m = re.search(r"Files scanned:\s+(\d+)", stdout)
    assert m, f"no Files scanned line in output:\n{stdout}"
    assert m.group(1) == "1", (
        f"expected 1 file scanned, got {m.group(1)}\n{stdout}"
    )
    # Must NOT claim test files were excluded.
    assert "test files excluded" not in stdout and "test file(s) excluded" not in stdout, (
        f"unexpected 'test files excluded' claim on a fixture with no test files:\n{stdout}"
    )
    # Genuinely clean: zero findings across every tier.
    for tier_label in (
        "Prohibited", "High-risk", "Limited-risk",
        "BLOCK tier", "WARN tier", "INFO tier",
    ):
        mt = re.search(rf"{tier_label}:\s+(\d+)", stdout)
        assert mt, f"missing '{tier_label}' line in:\n{stdout}"
        assert mt.group(1) == "0", (
            f"{tier_label} expected 0, got {mt.group(1)}\n{stdout}"
        )


def test_generator_commands_do_not_mutate_tracked_files(tmp_path):
    """Running the two generator commands that historically polluted the
    repo tree (`regula docs` and `regula handoff`) must not leave any
    modified files behind when given an explicit --output tmpdir.

    Regression for the bug where both commands defaulted to writing
    inside the current working directory / project directory, so test
    runs repeatedly mutated committed artifacts (timestamp diffs on
    docs/sample_high_risk_annex_iv.md and tests/fixtures/.../garak.regula.yaml).
    """
    import pathlib
    repo = pathlib.Path(__file__).resolve().parents[1]

    # Snapshot tracked-file state.
    def porcelain():
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo), capture_output=True, text=True, timeout=15,
        )
        return r.stdout

    before = porcelain()

    # regula docs — explicit tmp output.
    docs_out = tmp_path / "docs_out"
    rc1, _, err1 = run_cli(
        "docs", "--project", "tests/fixtures/sample_high_risk",
        "--output", str(docs_out),
    )
    assert rc1 == 0, f"docs failed: {err1[:200]}"

    # regula handoff garak — explicit tmp output.
    handoff_out = tmp_path / "garak.regula.yaml"
    rc2, _, err2 = run_cli(
        "handoff", "garak", "tests/fixtures/sample_high_risk",
        "--output", str(handoff_out),
    )
    assert rc2 == 0, f"handoff failed: {err2[:200]}"

    after = porcelain()
    assert after == before, (
        f"generator commands mutated tracked files in the repo tree.\n"
        f"before:\n{before}\n"
        f"after:\n{after}"
    )
