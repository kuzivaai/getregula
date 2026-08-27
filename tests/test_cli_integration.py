"""CLI integration tests — exercise top commands via subprocess."""
import json
import os
import subprocess
import sys
import tempfile



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


import contextlib


@contextlib.contextmanager
def _domain_gated_project():
    """A copy of the cv-screening example's app.py WITHOUT a policy file.

    The example itself declares `system.domain: employment` in its
    regula-policy.yaml (16 Jul 2026), so scanning it directly ACTIVATES
    the employment patterns. The domain-gating UX tests need the
    UNDECLARED state — employment vocabulary present, no domain declared
    — so they materialise a policy-less copy instead of depending on the
    documentation example's configuration.

    Uses tempfile rather than pytest's tmp_path: tmp_path's directory
    names contain the test name ("test_…"), which Regula's path
    screening treats as test provenance and skips entirely."""
    from pathlib import Path
    src = Path(__file__).resolve().parents[1] / "examples" / "cv-screening-app" / "app.py"
    with tempfile.TemporaryDirectory(prefix="gated-cv-app-") as td:
        proj = Path(td) / "hiring-service"
        proj.mkdir()
        (proj / "app.py").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        yield str(proj)


def test_check_sample_high_risk():
    rc, out, err = run_cli("check", "tests/fixtures/sample_high_risk")
    assert rc == 0
    assert "high" in out.lower() or "findings" in out.lower() or "risk" in out.lower()


def test_assess_auto():
    rc, out, err = run_cli("assess", "--answers", "yes,yes,no,yes,no")
    assert rc == 0
    assert "high" in out.lower() or "risk" in out.lower()


def test_assess_json_uses_standard_envelope():
    """`assess --format json` must emit the standard envelope, not a bare
    object. Regression for the July 2026 UX-audit Critical: assess was the
    one JSON surface that bypassed the envelope contract, so machine
    consumers got a different schema than every other command."""
    rc, out, err = run_cli("assess", "--answers", "yes,yes,no,yes,no", "--format", "json")
    assert rc == 0, f"assess failed: {err[:200]}"
    payload = json.loads(out)
    assert set(payload) == {
        "format_version", "regula_version", "command",
        "timestamp", "exit_code", "data",
    }, f"envelope keys wrong: {sorted(payload)}"
    assert payload["command"] == "assess"
    assert payload["exit_code"] == 0
    assert payload["data"]["tier"] == "high_risk"
    assert payload["data"]["answers"]["uses_ai"] == "yes"


def test_assess_json_prohibited_exit_code_in_envelope():
    """Envelope exit_code must match the process exit code on the
    prohibited path (both are 1)."""
    rc, out, err = run_cli("assess", "--answers", "yes,yes,yes", "--format", "json")
    assert rc == 1, f"expected rc=1 for prohibited tier, got {rc}: {err[:200]}"
    payload = json.loads(out)
    assert payload["exit_code"] == 1
    assert payload["data"]["tier"] == "prohibited"


def test_check_json_exit_code_in_envelope_matches_process_exit_code():
    """Same class of bug as test_assess_json_prohibited_exit_code_in_envelope
    above, found independently in `check` (not just `assess`): --format
    json's envelope previously hardcoded exit_code=0 unconditionally,
    while the real process exit code correctly reflected block-tier
    findings. A single JSON response could assert two contradictory
    outcomes (exit_code=0 in the body, process exit 1) depending on which
    signal a consumer checked. Verified end-to-end via subprocess so both
    signals are compared exactly as a real caller would observe them."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        (proj / "prohibited.py").write_text(
            "def social_credit_score(citizen):\n"
            "    return compute_social_score(citizen.behavior_history)\n"
        )
        rc, out, err = run_cli("check", str(proj), "--format", "json")
        assert rc == 1, f"expected rc=1 for a prohibited finding, got {rc}: {err[:200]}"
        payload = json.loads(out)
        assert payload["exit_code"] == 1, (
            "envelope exit_code must match the process exit code (both 1); "
            f"got envelope exit_code={payload['exit_code']} with process rc={rc}"
        )


def test_check_json_exit_code_zero_on_clean_scan():
    """False-positive/regression check: a clean scan must report exit_code=0
    in both the process exit code and the envelope, unaffected by the fix
    above."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        (proj / "clean.py").write_text("x = 1\n")
        rc, out, err = run_cli("check", str(proj), "--format", "json")
        assert rc == 0, f"expected rc=0 for a clean scan, got {rc}: {err[:200]}"
        payload = json.loads(out)
        assert payload["exit_code"] == 0


def test_check_html_exit_code_reflects_warn_tier_under_strict():
    """The --format html branch had its OWN narrower version of the same
    bug: it computed `sys.exit(1 if block_findings else 0)` locally,
    ignoring warn-tier findings even when --ci/--strict was set — unlike
    every other format (text/json/sarif), which correctly exit 1 for a
    warn-tier finding under --ci. Verifies html now matches."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        # A limited_risk (warn-tier) finding: a chatbot/conversational AI
        # pattern, not a block-tier prohibited/high-risk one.
        (proj / "warn.py").write_text(
            "import openai\n"
            "chatbot_response = openai.ChatCompletion.create(messages=msgs)\n"
            "print(chatbot_response)\n"
        )
        rc_no_ci, _, _ = run_cli("check", str(proj), "--format", "html")
        assert rc_no_ci == 0, "a warn-tier finding alone (no --ci) must not fail"

        rc_ci, _, err = run_cli("check", str(proj), "--format", "html", "--ci")
        assert rc_ci == 1, (
            "a warn-tier finding under --ci must fail closed for html, "
            f"matching text/json/sarif; got rc={rc_ci}: {err[:200]}"
        )


def test_classify_json_exit_code_matches_process_exit_code():
    """DEF-008 class, found in `classify` (not just `check`/`assess`):
    `classify --format json` previously RETURNED before reaching its own
    sys.exit(), so a prohibited classification reported exit_code=0 in the
    envelope AND process exit 0 in json mode, while text mode correctly
    exited 1 for the identical input."""
    rc_text, _, _ = run_cli(
        "classify", "--input", "social credit scoring system for citizens"
    )
    assert rc_text == 1, f"expected text mode rc=1, got {rc_text}"

    rc_json, out_json, err = run_cli(
        "classify", "--input", "social credit scoring system for citizens",
        "--format", "json",
    )
    assert rc_json == 1, f"expected json mode rc=1 (matching text), got {rc_json}: {err[:200]}"
    payload = json.loads(out_json)
    assert payload["exit_code"] == 1, (
        f"envelope exit_code must match process exit code; got {payload['exit_code']}"
    )
    data = payload["data"]
    assert data["detector_observation"]["detector_class"] == "prohibited"
    assert "tier" not in data["detector_observation"]
    assert data["decision"]["result_type"] == "insufficient_information"
    assert data["decision"]["rule_resolution"] == "unresolved"


def test_classify_json_exit_code_zero_on_benign_input():
    """False-positive/regression check for the classify fix above."""
    rc, out, err = run_cli(
        "classify", "--input", "a simple calculator function",
        "--format", "json",
    )
    assert rc == 0, f"expected rc=0 for benign input, got {rc}: {err[:200]}"
    payload = json.loads(out)
    assert payload["exit_code"] == 0


def test_check_explain_keeps_detector_detail_separate_from_decision():
    """Explain mode must not restore copied obligations or effort estimates."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        (_Path(d) / "screen.py").write_text(
            "from sklearn.linear_model import LogisticRegression\n"
            "def credit_score_decision(applicant):\n"
            "    return model.predict(applicant)\n",
            encoding="utf-8",
        )
        rc, out, err = run_cli(
            "check", d, "--explain", "--format", "json", "--no-skip-tests",
            "--domain", "finance"
        )
    assert rc in (0, 1), err[:200]
    data = json.loads(out)["data"]
    assert data["decision"]["result_type"] == "insufficient_information"
    assert data["detector_explanations"], "fixture must exercise explain output"
    for finding in data["detector_findings"]:
        assert "deadline" not in finding
        assert "deadline_note" not in finding
        assert "observations" not in finding
        for context in finding.get("detector_context", []):
            assert "requires" not in context["detector_observation"].lower()
    for explanation in data["detector_explanations"]:
        assert "obligation_roadmap" not in explanation
        assert "total_effort_hours" not in explanation
        assert "classification" not in explanation
        assert "classification_observation" in explanation


def test_plan_and_roadmap_withhold_claims_when_facts_are_absent():
    """The public planning adapters enforce the no-unresolved-claim invariant."""
    for command, output_key in (("plan", "plan"), ("roadmap", "roadmap")):
        rc, out, err = run_cli(command, "--project", ".", "--format", "json")
        assert rc == 0, f"{command} failed: {err[:200]}"
        data = json.loads(out)["data"]
        assert data[output_key] is None
        assert data["decision"]["result_type"] == "insufficient_information"
        assert data["decision"]["unresolved_predicates"]


def test_gap_strict_json_exit_code_matches_process_exit_code():
    """DEF-008 class, found in `gap`: json_output("gap", ...) previously
    always hardcoded envelope exit_code=0, contradicting the real process
    exit code under --strict with a low overall_score."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        (proj / "empty.py").write_text("x = 1\n")

        rc, out, err = run_cli(
            "gap", "--project", str(proj), "--strict", "--format", "json"
        )
        assert rc == 1, f"expected rc=1 for a low-score project under --strict, got {rc}: {err[:200]}"
        payload = json.loads(out)
        assert payload["exit_code"] == 1, (
            f"envelope exit_code must match process exit code; got {payload['exit_code']}"
        )


def test_gap_low_score_without_strict_exit_code_zero():
    """False-positive/regression check: the same low-scoring project
    WITHOUT --strict must report exit_code=0 in both signals."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        (proj / "empty.py").write_text("x = 1\n")

        rc, out, err = run_cli("gap", "--project", str(proj), "--format", "json")
        assert rc == 0, f"expected rc=0 without --strict, got {rc}: {err[:200]}"
        payload = json.loads(out)
        assert payload["exit_code"] == 0


def test_gpai_check_strict_json_exit_code_matches_process_exit_code():
    """DEF-008 class, found in `gpai-check`: json_output("gpai-check", ...)
    previously always hardcoded envelope exit_code=0, contradicting the
    real process exit code under --strict with a FAIL in the summary."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        (proj / "empty.py").write_text("x = 1\n")

        rc, out, err = run_cli(
            "gpai-check", str(proj), "--strict", "--format", "json"
        )
        assert rc == 1, f"expected rc=1 (FAIL present) under --strict, got {rc}: {err[:200]}"
        payload = json.loads(out)
        assert payload["exit_code"] == 1, (
            f"envelope exit_code must match process exit code; got {payload['exit_code']}"
        )
        assert payload["data"]["summary"]["FAIL"] > 0


def test_guardrails_strict_json_exit_code_matches_process_exit_code():
    """DEF-008 class, found in `guardrails`: json_output("guardrails", ...)
    previously always hardcoded envelope exit_code=0, contradicting the
    real process exit code under --strict/--ci with a low overall_score."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        (proj / "empty.py").write_text("x = 1\n")

        rc, out, err = run_cli(
            "guardrails", str(proj), "--strict", "--format", "json"
        )
        assert rc == 1, f"expected rc=1 (low score) under --strict, got {rc}: {err[:200]}"
        payload = json.loads(out)
        assert payload["exit_code"] == 1, (
            f"envelope exit_code must match process exit code; got {payload['exit_code']}"
        )


def test_deps_strict_json_exit_code_matches_process_exit_code():
    """DEF-008 class, found in `deps`: json_output("deps", ...) previously
    always hardcoded envelope exit_code=0, contradicting the real process
    exit code when compromised deps are found (unconditionally) or under
    --strict with a low pinning_score. Uses the existing
    tests/fixtures/sample_unpinned fixture, which is already known to
    produce a low pinning_score."""
    rc, out, err = run_cli(
        "deps", "tests/fixtures/sample_unpinned", "--strict", "--format", "json"
    )
    assert rc == 1, f"expected rc=1 (low pinning_score) under --strict, got {rc}: {err[:200]}"
    payload = json.loads(out)
    assert payload["exit_code"] == 1, (
        f"envelope exit_code must match process exit code; got {payload['exit_code']}"
    )
    assert payload["data"]["pinning_score"] < 50


def test_owasp_agentic_strict_json_exit_code_matches_process_exit_code():
    """DEF-008 class, found in `owasp-agentic`: json_output("owasp-agentic",
    ...) previously always hardcoded envelope exit_code=0, contradicting the
    real process exit code under --strict/--ci with an at_risk finding."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        # ASI01 vuln pattern (agent goal hijack): user_input concatenated
        # directly into a system prompt, with no matching control pattern.
        (proj / "agent.py").write_text("system_prompt = base + user_input\n")

        rc, out, err = run_cli(
            "owasp-agentic", str(proj), "--strict", "--format", "json"
        )
        assert rc == 1, f"expected rc=1 (at_risk finding) under --strict, got {rc}: {err[:200]}"
        payload = json.loads(out)
        assert payload["exit_code"] == 1, (
            f"envelope exit_code must match process exit code; got {payload['exit_code']}"
        )
        at_risk = [r for r in payload["data"]["risks"] if r["status"] == "at_risk"]
        assert at_risk, "expected at least one at_risk finding"


def test_ai_codegen_strict_json_exit_code_matches_process_exit_code():
    """DEF-008 class, found in `ai-codegen`: json_output("ai-codegen", ...)
    previously always hardcoded envelope exit_code=0, contradicting the
    real process exit code under --strict/--ci when transparency_compliant
    is False (naturally the case for a project with no AI-disclosure
    markers at all, such as an empty project)."""
    import tempfile
    from pathlib import Path as _Path
    with tempfile.TemporaryDirectory() as d:
        proj = _Path(d) / "proj"
        proj.mkdir()
        (proj / "empty.py").write_text("x = 1\n")

        rc, out, err = run_cli(
            "ai-codegen", str(proj), "--strict", "--format", "json"
        )
        assert rc == 1, f"expected rc=1 under --strict, got {rc}: {err[:200]}"
        payload = json.loads(out)
        assert payload["exit_code"] == 1, (
            f"envelope exit_code must match process exit code; got {payload['exit_code']}"
        )


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


def test_sbom(tmp_path):
    """SBOM smoke test proves a real dependency reaches CycloneDX output."""
    (tmp_path / "requirements.txt").write_text("requests==2.32.0\n")
    rc, out, err = run_cli("sbom", "--project", str(tmp_path))
    assert rc == 0
    bom = json.loads(out)
    assert bom["bomFormat"] == "CycloneDX"
    assert bom["specVersion"] == "1.7"
    assert any(
        component.get("name") == "requests"
        and component.get("version") == "2.32.0"
        for component in bom["components"]
    )


def test_dpv():
    """regula dpv — emits valid DPV-AIAct JSON-LD with the honest disclaimer."""
    import json as _json
    rc, out, err = run_cli("dpv", "--project", "tests/fixtures/sample_high_risk",
                           "-n", "SampleHR")
    assert rc == 0
    doc = _json.loads(out)
    assert doc["@context"]["eu-aiact"] == "https://w3id.org/dpv/legal/eu/aiact#"
    scan = doc["@graph"][0]
    assert scan["type"] == "regula:ScanResult"
    assert "Community Group" in _json.dumps(scan)


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
    """regwatch exit codes: 0=up-to-date, 1=stale (valid warning), 2=error.
    Both 0 and 1 are correct behaviour — 1 means unreviewed regulatory
    changes exist, which is the intended purpose of the command."""
    rc, out, err = run_cli("regwatch")
    assert rc != 2, f"regwatch error (exit 2): {out}{err}"
    assert "regwatch" in out.lower() or "ruleset" in out.lower()


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

    Uses a tempdir with a real AI finding to avoid path-dependent scope issues
    (examples/ is in SKIP_DIRS; tests/ has test provenance).
    """
    with tempfile.TemporaryDirectory() as tmp:
        app = os.path.join(tmp, "app.py")
        with open(app, "w") as f:
            f.write("import openai\nimport langchain\n"
                    "from langchain.chat_models import ChatOpenAI\n"
                    "chatbot = ChatOpenAI(model='gpt-4')\n"
                    "response = chatbot.predict('hello user')\n")
        rc, stdout, stderr = run_cli(
            "check", "--ci", tmp,
            env_overrides={"GITHUB_ACTIONS": "true"},
        )
    assert rc == 1, f"expected rc=1 (WARN in CI mode), got {rc}\nstderr={stderr}"
    warning_lines = [ln for ln in stdout.splitlines() if ln.startswith("::warning")]
    assert len(warning_lines) >= 1, f"expected >=1 ::warning, got {len(warning_lines)}\nstdout={stdout}"
    ann = warning_lines[0]
    assert "file=" in ann, ann
    assert ",line=" in ann, ann


def test_github_annotations_suppressed_without_github_actions():
    """Without GITHUB_ACTIONS=true, --ci mode does NOT emit workflow commands."""
    with tempfile.TemporaryDirectory() as tmp:
        app = os.path.join(tmp, "app.py")
        with open(app, "w") as f:
            f.write("import openai\nimport langchain\n"
                    "from langchain.chat_models import ChatOpenAI\n"
                    "chatbot = ChatOpenAI(model='gpt-4')\n"
                    "response = chatbot.predict('hello user')\n")
        rc, stdout, stderr = run_cli(
            "check", "--ci", tmp,
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
    rc, stdout, stderr = run_cli("check", "--scope", "all", "examples/customer-chatbot")
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


def test_nonempty_scan_discloses_excluded_test_files():
    """A successful production scan must still disclose skipped test files."""
    from pathlib import Path

    with tempfile.TemporaryDirectory(prefix="coverage-service-") as td:
        project = Path(td)
        (project / "app.py").write_text("value = 1\n", encoding="utf-8")
        (project / "test_helper.py").write_text("value = 2\n", encoding="utf-8")
        rc, stdout, stderr = run_cli("check", str(project))

    assert rc == 0, f"expected rc=0, got {rc}\nstderr={stderr}"
    assert "Files scanned:      1" in stdout, stdout
    assert "INFO: 1 test file(s) were not scanned" in stdout, stdout
    assert "Use --no-skip-tests to include them." in stdout, stdout


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

    # Snapshot tracked-file state. Parallel workers deliberately create
    # short-lived untracked fixtures under the repository root, so including
    # untracked paths here makes this assertion race with unrelated tests.
    def tracked_porcelain():
        r = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=str(repo), capture_output=True, text=True, timeout=15,
            check=True,
        )
        return r.stdout

    before = tracked_porcelain()

    # Regression for the xdist race: another worker's repository-local,
    # untracked fixture must not look like a tracked-file mutation.
    with tempfile.TemporaryDirectory(dir=str(repo)):
        assert tracked_porcelain() == before

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

    after = tracked_porcelain()
    assert after == before, (
        f"generator commands mutated tracked files in the repo tree.\n"
        f"before:\n{before}\n"
        f"after:\n{after}"
    )


def test_docs_default_output_goes_to_project_not_cwd(tmp_path):
    """`regula docs <project>` with NO --output must write into
    <project>/docs/, never <cwd>/docs/.

    Regression for the sentinel bug: the argparse default "docs" was
    resolved against the CWD, so every default-output invocation from the
    repo root (including test runs) dropped <cwd>/docs/tmp*_annex_iv.md
    junk into this repo — 56 such files accumulated before the July 2026
    audit caught it. git-status snapshots alone missed it because the
    junk was untracked and earlier tests always passed explicit --output.
    """
    import pathlib
    repo = pathlib.Path(__file__).resolve().parents[1]

    project = tmp_path / "proj"
    project.mkdir()
    (project / "app.py").write_text("import openai\n", encoding="utf-8")

    junk = repo / "docs" / f"{project.name}_annex_iv.md"
    assert not junk.exists()

    rc, _, err = run_cli("docs", str(project))
    assert rc == 0, f"docs failed: {err[:200]}"

    assert not junk.exists(), (
        f"default-output docs run polluted the repo: {junk} — the 'docs' "
        "sentinel must resolve against the project, not the CWD"
    )
    expected = project / "docs" / f"{project.name}_annex_iv.md"
    assert expected.exists(), f"output not written to project docs/: {expected}"


def test_demo_verdict_shows_high_risk():
    """Demo must show HIGH-RISK for the bundled hiring system, not NO AI DETECTED.

    Regression test for the domain-gating + scope-filtering bug where the demo's
    cv-screening-app was suppressed to 'NO AI DETECTED' because: (1) employment
    patterns are domain-gated and the demo didn't declare --domain, and (2) the
    examples/ directory was excluded by --scope production. Fixed by setting
    args.domain='employment' and args.scope='all' in cmd_demo.
    """
    rc, out, err = run_cli("demo")
    assert "HIGH-RISK" in out, (
        f"Demo should show HIGH-RISK verdict but got:\n{out[:500]}"
    )
    assert "NO AI DETECTED" not in out, (
        f"Demo must not show NO AI DETECTED:\n{out[:500]}"
    )


def test_domain_gating_hint_shown_for_suppressed_findings():
    """When domain-gated findings are suppressed, the INFO hint must appear.

    Regression test for a cache-path bug where domain_gated_count was not
    incremented for cached findings, hiding the hint from subsequent scans.
    """
    with _domain_gated_project() as proj:
        rc, out, err = run_cli("check", proj, "--scope", "all")
    assert "domain gating" in out.lower() or "domain gating" in err.lower(), (
        f"Expected domain gating hint in output:\nstdout: {out[:300]}\nstderr: {err[:300]}"
    )


def test_demo_data_in_sync():
    """Bundled demo data must be byte-identical to the source example.

    scripts/demos/cv_screening_app.py is a copy of examples/cv-screening-app/app.py.
    If either is updated, the other must match — this test catches drift.
    """
    repo = __import__("pathlib").Path(__file__).resolve().parents[1]
    source = repo / "examples" / "cv-screening-app" / "app.py"
    bundled = repo / "scripts" / "demos" / "cv_screening_app.py"
    assert source.exists(), f"Source not found: {source}"
    assert bundled.exists(), f"Bundled not found: {bundled}"
    assert source.read_bytes() == bundled.read_bytes(), (
        "examples/cv-screening-app/app.py and scripts/demos/cv_screening_app.py "
        "have diverged — update the copy to match the source"
    )


def test_suppressed_counter_matches_domain_gated_hint():
    """Suppressed: N in the stats block must equal the domain-gated count in the INFO hint."""
    with _domain_gated_project() as proj:
        rc, out, err = run_cli("check", proj, "--scope", "all")
    import re
    suppressed_m = re.search(r"Suppressed:\s+(\d+)", out)
    hint_m = re.search(r"(\d+) high-risk finding\(s\) suppressed by domain gating", out)
    assert suppressed_m, f"Suppressed line not found in output:\n{out[:400]}"
    assert hint_m, f"Domain gating hint not found in output:\n{out[:400]}"
    assert suppressed_m.group(1) == hint_m.group(1), (
        f"Suppressed counter ({suppressed_m.group(1)}) != hint count ({hint_m.group(1)})"
    )


def test_no_ai_detected_acknowledges_domain_gated():
    """When domain-gated findings exist, the verdict line must not say 'No AI components'."""
    with _domain_gated_project() as proj:
        rc, out, err = run_cli("check", proj, "--scope", "all")
    assert "No AI components" not in out, (
        f"Verdict should acknowledge domain-gated findings:\n{out[:400]}"
    )
    assert "suppressed by domain gating" in out, (
        f"Verdict should mention domain gating:\n{out[:400]}"
    )


def test_demo_banner_matches_scanned_path():
    """Demo banner path must match the directory actually scanned."""
    rc, out, err = run_cli("demo")
    # The banner says "scanning <dirname>" and the scan header says "Regula Scan: <path>"
    import re
    banner_m = re.search(r"Regula Demo .+ scanning (\S+)", out)
    assert banner_m, f"Demo banner not found in output:\n{out[:300]}"
    banner_name = banner_m.group(1)
    scan_m = re.search(r"Regula Scan: (.+)", out)
    assert scan_m, f"Scan header not found in output:\n{out[:300]}"
    scanned_path = scan_m.group(1).strip()
    assert scanned_path.endswith(banner_name), (
        f"Banner says '{banner_name}' but scan path is '{scanned_path}'"
    )


def test_demo_file_count_excludes_init():
    """Demo file count should not include the empty __init__.py package marker."""
    rc, out, err = run_cli("demo")
    import re
    m = re.search(r"Files scanned:\s+(\d+)", out)
    assert m, f"Files scanned line not found:\n{out[:300]}"
    count = int(m.group(1))
    assert count == 1, (
        f"Demo should scan 1 file (cv_screening_app.py), got {count}"
    )


def test_every_project_subcommand_accepts_positional_path():
    """Every subcommand that takes --project must also accept the natural
    positional form (`regula <cmd> .`) — published docs and site copy
    teach it, and six commands taught this way exited 2 until 8 Jul 2026;
    six MORE (conform, oversight, discover, guardrails, sbom, report)
    until 10 Jul 2026. This locks the whole class.

    `install`, `baseline`, and `audit` are exempt: they already have a
    different positional argument (audit: verify/export/query), and
    adding a second optional positional would make parses ambiguous.
    """
    import argparse
    from pathlib import Path as _P

    sys.path.insert(0, str(_P(__file__).resolve().parents[1] / "scripts"))
    import cli as cli_mod

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    cli_mod._build_subparsers(sub)

    exempt = {"install", "baseline", "audit"}
    checked = 0
    for name, sp in sub.choices.items():
        option_strings = {s for a in sp._actions for s in a.option_strings}
        if "--project" not in option_strings or name in exempt:
            continue
        try:
            args = parser.parse_args([name, "/tmp/some-project"])
        except SystemExit:
            raise AssertionError(
                f"`regula {name} <path>` exits 2 — the positional path "
                f"argument is missing from the {name!r} subparser"
            )
        # And the generic hook in main() maps it onto --project:
        assert getattr(args, "project_path_positional", None) == "/tmp/some-project", name
        checked += 1
    assert checked >= 25, f"only {checked} subcommands checked — glob regression?"


def test_report_domain_flag_activates_gated_findings():
    """`regula report` on a domain-gated project yields zero findings
    without --domain and real findings with it (10 Jul 2026 audit: the
    flag didn't exist, so domain-gated projects silently reported
    nothing). Uses a policy-less copy of the cv-screening example
    (employment vocabulary, no domain declared)."""
    with _domain_gated_project() as proj:
        rc, out, _ = run_cli("report", proj, "-f", "json")
        assert rc == 0
        gated = json.loads(out)["data"]
        rc, out, _ = run_cli("report", proj, "-f", "json",
                             "--domain", "employment")
    assert rc == 0
    activated = json.loads(out)["data"]
    assert len(activated) > len(gated), (
        f"--domain employment should surface gated findings: "
        f"{len(gated)} without vs {len(activated)} with"
    )
