# regula-ignore
"""Tests for project-scoped audit trails and chain continuity.

Covers the P1 confidentiality fix (evidence packs embedding the
machine-global audit trail) and the month-boundary hash-chain defect
(every new monthly file was seeded with the genesis hash while
verify_chain required cross-file continuity, so chain_valid was
structurally false on any store spanning two or more months).

Contract under test:
- log_event(project_path=...) writes to a per-project chain under
  <audit_root>/projects/<slug>/ — never interleaved with other projects.
- New monthly files continue the chain from the previous month's last
  hash (rotation continuity), for both the audit trail and the runtime
  monitor.
- verify_chain tolerates a genesis seed at a FILE boundary as a
  reported "legacy restart" (the pre-fix writer's actual behaviour),
  but still fails on tampering and on non-genesis mismatches.
- collect_audit_trail() is the single scoped-collection helper used by
  every deliverable surface (evidence pack, conformity pack, reports).
- Deliverables never contain events from other projects or from the
  machine-global store.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
HOOKS_DIR = Path(__file__).parent.parent / "hooks"
sys.path.insert(0, str(SCRIPTS_DIR))

from log_event import (  # noqa: E402
    collect_audit_trail,
    compute_hash,
    get_audit_dir,
    get_audit_file,
    log_event,
    project_slug,
    query_events,
    verify_chain,
    verify_chain_dir,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_chain(file_path: Path, n: int, start_prev: str = "0" * 64,
                 event_type: str = "test_event", day_offset: int = 0) -> str:
    """Write a hand-built valid hash chain to file_path, return last hash."""
    prev = start_prev
    lines = []
    for i in range(n):
        e = {
            "event_id": f"crafted-{file_path.stem}-{i}",
            "timestamp": f"2026-06-{day_offset + i + 1:02d}T00:00:00+00:00",
            "event_type": event_type,
            "session_id": None,
            "project": None,
            "data": {"i": i},
            "previous_hash": prev,
        }
        e["current_hash"] = compute_hash(e, prev)
        lines.append(json.dumps(e, sort_keys=True))
        prev = e["current_hash"]
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return prev


@pytest.fixture()
def audit_root(tmp_path, monkeypatch):
    root = tmp_path / "audit-root"
    monkeypatch.setenv("REGULA_AUDIT_DIR", str(root))
    monkeypatch.delenv("REGULA_PROJECT_DIR", raising=False)
    monkeypatch.delenv("REGULA_PROJECT", raising=False)
    return root


# ---------------------------------------------------------------------------
# Slug and directory derivation
# ---------------------------------------------------------------------------

class TestProjectSlug:
    def test_deterministic(self, tmp_path):
        p = tmp_path / "client_proj"
        p.mkdir()
        assert project_slug(str(p)) == project_slug(str(p))

    def test_distinct_paths_distinct_slugs(self, tmp_path):
        a = tmp_path / "proj"
        b = tmp_path / "sub" / "proj"
        a.mkdir()
        b.mkdir(parents=True)
        assert project_slug(str(a)) != project_slug(str(b))

    def test_sanitises_name(self, tmp_path):
        p = tmp_path / "we ird$name"
        p.mkdir()
        slug = project_slug(str(p))
        assert "/" not in slug and " " not in slug and "$" not in slug

    def test_project_dir_under_root(self, audit_root, tmp_path):
        p = tmp_path / "projA"
        p.mkdir()
        d = get_audit_dir(project_path=str(p))
        assert str(d).startswith(str(audit_root))
        assert d.parent.name == "projects"


# ---------------------------------------------------------------------------
# Write-time scoping
# ---------------------------------------------------------------------------

class TestWriteScoping:
    def test_global_default_unchanged(self, audit_root):
        log_event("test_event", {"k": 1})
        root_files = list(audit_root.glob("audit_*.jsonl"))
        assert len(root_files) == 1
        assert not (audit_root / "projects").exists()

    def test_project_path_writes_to_project_chain(self, audit_root, tmp_path):
        proj = tmp_path / "projA"
        proj.mkdir()
        log_event("test_event", {"k": 1}, project_path=str(proj))
        assert list(get_audit_dir(str(proj)).glob("audit_*.jsonl"))
        assert not list(audit_root.glob("audit_*.jsonl"))

    def test_project_name_autofilled(self, audit_root, tmp_path):
        proj = tmp_path / "projA"
        proj.mkdir()
        ev = log_event("test_event", {"k": 1}, project_path=str(proj))
        assert ev.project == "projA"

    def test_explicit_project_name_wins(self, audit_root, tmp_path):
        proj = tmp_path / "projA"
        proj.mkdir()
        ev = log_event("test_event", {"k": 1}, project="Custom",
                       project_path=str(proj))
        assert ev.project == "Custom"

    def test_env_project_dir_fallback(self, audit_root, tmp_path, monkeypatch):
        proj = tmp_path / "envproj"
        proj.mkdir()
        monkeypatch.setenv("REGULA_PROJECT_DIR", str(proj))
        log_event("test_event", {"k": 1})
        assert list(get_audit_dir(str(proj)).glob("audit_*.jsonl"))
        assert not list(audit_root.glob("audit_*.jsonl"))

    def test_projects_segregated(self, audit_root, tmp_path):
        a = tmp_path / "projA"
        b = tmp_path / "projB"
        a.mkdir()
        b.mkdir()
        log_event("test_event", {"who": "A"}, project_path=str(a))
        log_event("test_event", {"who": "B"}, project_path=str(b))
        a_events = query_events(project_path=str(a))
        b_events = query_events(project_path=str(b))
        assert [e["data"]["who"] for e in a_events] == ["A"]
        assert [e["data"]["who"] for e in b_events] == ["B"]


# ---------------------------------------------------------------------------
# Rotation continuity (the chain_valid:false root cause)
# ---------------------------------------------------------------------------

class TestRotationContinuity:
    def test_new_month_seeds_from_previous_file_global(self, audit_root):
        audit_root.mkdir(parents=True, exist_ok=True)
        last = _write_chain(audit_root / "audit_2026-06.jsonl", 3)
        ev = log_event("test_event", {"k": 1})
        assert ev.previous_hash == last

    def test_new_month_seeds_from_previous_file_project(self, audit_root, tmp_path):
        proj = tmp_path / "projA"
        proj.mkdir()
        pdir = get_audit_dir(str(proj))
        last = _write_chain(pdir / "audit_2026-06.jsonl", 2)
        ev = log_event("test_event", {"k": 1}, project_path=str(proj))
        assert ev.previous_hash == last

    def test_continuous_chain_verifies_clean(self, audit_root):
        audit_root.mkdir(parents=True, exist_ok=True)
        last = _write_chain(audit_root / "audit_2026-05.jsonl", 2)
        _write_chain(audit_root / "audit_2026-06.jsonl", 2, start_prev=last)
        valid, msg = verify_chain()
        assert valid is True
        assert msg is None


# ---------------------------------------------------------------------------
# Verification semantics
# ---------------------------------------------------------------------------

class TestVerifySemantics:
    def test_legacy_genesis_restart_tolerated_with_note(self, audit_root):
        audit_root.mkdir(parents=True, exist_ok=True)
        _write_chain(audit_root / "audit_2026-05.jsonl", 2)
        _write_chain(audit_root / "audit_2026-06.jsonl", 2)  # genesis seed
        valid, msg = verify_chain()
        assert valid is True
        assert msg is not None and "restart" in msg.lower()

    def test_nongenesis_mismatch_fails(self, audit_root):
        audit_root.mkdir(parents=True, exist_ok=True)
        _write_chain(audit_root / "audit_2026-05.jsonl", 2)
        _write_chain(audit_root / "audit_2026-06.jsonl", 2,
                     start_prev="deadbeef" * 8)
        valid, msg = verify_chain()
        assert valid is False

    def test_tamper_within_file_fails(self, audit_root):
        audit_root.mkdir(parents=True, exist_ok=True)
        f = audit_root / "audit_2026-06.jsonl"
        _write_chain(f, 3)
        lines = f.read_text().splitlines()
        e = json.loads(lines[1])
        e["data"]["i"] = 999
        lines[1] = json.dumps(e, sort_keys=True)
        f.write_text("\n".join(lines) + "\n")
        valid, msg = verify_chain()
        assert valid is False

    def test_genesis_restart_mid_file_fails(self, audit_root):
        """A genesis previous_hash is only forgiven at a FILE boundary."""
        audit_root.mkdir(parents=True, exist_ok=True)
        f = audit_root / "audit_2026-06.jsonl"
        _write_chain(f, 2)
        # append a fresh genesis-seeded chain to the SAME file
        extra = f.read_text()
        tmp = audit_root / "tmp.jsonl"
        _write_chain(tmp, 1)
        f.write_text(extra + tmp.read_text())
        tmp.unlink()
        valid, msg = verify_chain()
        assert valid is False

    def test_project_scope_verifies_only_that_chain(self, audit_root, tmp_path):
        a = tmp_path / "projA"
        b = tmp_path / "projB"
        a.mkdir()
        b.mkdir()
        log_event("test_event", {"k": 1}, project_path=str(a))
        # corrupt B's chain
        log_event("test_event", {"k": 1}, project_path=str(b))
        bfile = next(get_audit_dir(str(b)).glob("audit_*.jsonl"))
        e = json.loads(bfile.read_text().strip())
        e["data"]["k"] = 42
        bfile.write_text(json.dumps(e, sort_keys=True) + "\n")
        valid_a, _ = verify_chain(project_path=str(a))
        valid_b, _ = verify_chain(project_path=str(b))
        assert valid_a is True
        assert valid_b is False

    def test_machine_verify_covers_project_chains(self, audit_root, tmp_path):
        a = tmp_path / "projA"
        a.mkdir()
        log_event("test_event", {"k": 1}, project_path=str(a))
        afile = next(get_audit_dir(str(a)).glob("audit_*.jsonl"))
        e = json.loads(afile.read_text().strip())
        e["data"]["k"] = 42
        afile.write_text(json.dumps(e, sort_keys=True) + "\n")
        valid, msg = verify_chain()
        assert valid is False

    def test_verify_chain_dir_reusable(self, tmp_path):
        d = tmp_path / "chains"
        d.mkdir()
        last = _write_chain(d / "monitor_2026-05.jsonl", 2)
        _write_chain(d / "monitor_2026-06.jsonl", 2, start_prev=last)
        valid, msg = verify_chain_dir(d, "monitor_*.jsonl")
        assert valid is True


# ---------------------------------------------------------------------------
# Query scoping
# ---------------------------------------------------------------------------

class TestQueryScoping:
    def test_machine_scope_aggregates_all_chains(self, audit_root, tmp_path):
        a = tmp_path / "projA"
        a.mkdir()
        log_event("test_event", {"who": "global"})
        log_event("test_event", {"who": "A"}, project_path=str(a))
        events = query_events()
        whos = {e["data"]["who"] for e in events}
        assert whos == {"global", "A"}

    def test_project_scope_excludes_global(self, audit_root, tmp_path):
        a = tmp_path / "projA"
        a.mkdir()
        log_event("test_event", {"who": "global"})
        log_event("test_event", {"who": "A"}, project_path=str(a))
        events = query_events(project_path=str(a))
        assert [e["data"]["who"] for e in events] == ["A"]

    def test_project_scope_empty_when_no_chain(self, audit_root, tmp_path):
        a = tmp_path / "projA"
        a.mkdir()
        log_event("test_event", {"who": "global"})
        assert query_events(project_path=str(a)) == []


# ---------------------------------------------------------------------------
# collect_audit_trail — the single helper for deliverable surfaces
# ---------------------------------------------------------------------------

class TestCollectAuditTrail:
    def test_scope_fields_present(self, audit_root, tmp_path):
        proj = tmp_path / "client_proj"
        proj.mkdir()
        log_event("classification", {"tier": "high_risk"},
                  project_path=str(proj))
        data = collect_audit_trail(str(proj))
        assert data["scope"] == "project"
        assert data["project"] == "client_proj"
        assert data["project_slug"] == project_slug(str(proj))
        assert data["chain_valid"] is True
        assert data["event_count"] == 1
        assert data["limit_reached"] is False
        assert "scope_note" in data
        assert len(data["events"]) == 1

    def test_never_contains_foreign_events(self, audit_root, tmp_path):
        other = tmp_path / "other_client"
        other.mkdir()
        proj = tmp_path / "client_proj"
        proj.mkdir()
        log_event("tool_use", {"marker": "GLOBAL_SENSITIVE"})
        log_event("tool_use", {"marker": "OTHER_CLIENT_SENSITIVE"},
                  project_path=str(other))
        log_event("classification", {"marker": "own"},
                  project_path=str(proj))
        blob = json.dumps(collect_audit_trail(str(proj)))
        assert "GLOBAL_SENSITIVE" not in blob
        assert "OTHER_CLIENT_SENSITIVE" not in blob
        assert "own" in blob

    def test_empty_project_chain_is_honest(self, audit_root, tmp_path):
        proj = tmp_path / "client_proj"
        proj.mkdir()
        log_event("tool_use", {"marker": "GLOBAL_SENSITIVE"})
        data = collect_audit_trail(str(proj))
        assert data["event_count"] == 0
        assert data["events"] == []
        assert "GLOBAL_SENSITIVE" not in json.dumps(data)

    def test_limit_reached_flag(self, audit_root, tmp_path):
        proj = tmp_path / "client_proj"
        proj.mkdir()
        for i in range(5):
            log_event("test_event", {"i": i}, project_path=str(proj))
        data = collect_audit_trail(str(proj), limit=3)
        assert data["limit_reached"] is True
        assert data["event_count"] == 3
        # embedded events are the verifiable chain PREFIX (oldest first)
        assert [e["data"]["i"] for e in data["events"]] == [0, 1, 2]


# ---------------------------------------------------------------------------
# Deliverable surfaces (the P1 regression tests)
# ---------------------------------------------------------------------------

def _make_fixture_project(tmp_path: Path) -> Path:
    proj = tmp_path / "client_proj"
    proj.mkdir()
    (proj / "app.py").write_text(
        "import sklearn\n"
        "def score(candidate):\n"
        "    return candidate\n",
        encoding="utf-8",
    )
    return proj


def _seed_cross_project_events(tmp_path: Path, proj: Path):
    other = tmp_path / "other_client"
    other.mkdir(exist_ok=True)
    log_event("tool_use", {"marker": "GLOBAL_SENSITIVE_MARKER"})
    log_event("tool_use", {"marker": "OTHER_CLIENT_MARKER"},
              project_path=str(other))
    log_event("classification", {"marker": "OWN_PROJECT_MARKER"},
              project_path=str(proj))


class TestEvidencePackScoped:
    def test_pack_audit_trail_is_project_scoped(self, audit_root, tmp_path):
        from evidence_pack import generate_evidence_pack
        proj = _make_fixture_project(tmp_path)
        _seed_cross_project_events(tmp_path, proj)
        out = tmp_path / "out"
        result = generate_evidence_pack(str(proj), output_dir=str(out))
        audit_path = Path(result["pack_path"]) / "05-audit-trail.json"
        assert audit_path.exists()
        blob = audit_path.read_text(encoding="utf-8")
        audit = json.loads(blob)
        assert audit["scope"] == "project"
        assert "GLOBAL_SENSITIVE_MARKER" not in blob
        assert "OTHER_CLIENT_MARKER" not in blob
        assert "OWN_PROJECT_MARKER" in blob
        assert audit["chain_valid"] is True

    def test_pack_with_no_project_events_leaks_nothing(self, audit_root, tmp_path):
        from evidence_pack import generate_evidence_pack
        proj = _make_fixture_project(tmp_path)
        log_event("tool_use", {"marker": "GLOBAL_SENSITIVE_MARKER"})
        out = tmp_path / "out"
        result = generate_evidence_pack(str(proj), output_dir=str(out))
        blob = (Path(result["pack_path"]) / "05-audit-trail.json").read_text()
        assert "GLOBAL_SENSITIVE_MARKER" not in blob
        audit = json.loads(blob)
        # pack generation itself may log scoped events, but never foreign ones
        for ev in audit["events"]:
            assert "GLOBAL_SENSITIVE_MARKER" not in json.dumps(ev)


class TestConformPackScoped:
    def test_conform_audit_trail_is_project_scoped(self, audit_root, tmp_path):
        from conform import generate_conformity_pack
        proj = _make_fixture_project(tmp_path)
        _seed_cross_project_events(tmp_path, proj)
        out = tmp_path / "conform-out"
        generate_conformity_pack(str(proj), output_dir=str(out))
        hits = list(out.rglob("audit-trail.json"))
        assert hits, "conformity pack should contain audit-trail.json"
        blob = hits[0].read_text(encoding="utf-8")
        assert "GLOBAL_SENSITIVE_MARKER" not in blob
        assert "OTHER_CLIENT_MARKER" not in blob
        audit = json.loads(blob)
        assert audit["scope"] == "project"


class TestReportScoped:
    def test_html_report_include_audit_is_project_scoped(self, audit_root, tmp_path):
        proj = _make_fixture_project(tmp_path)
        _seed_cross_project_events(tmp_path, proj)
        out_file = tmp_path / "report.html"
        env = os.environ.copy()
        env["REGULA_AUDIT_DIR"] = str(audit_root)
        env.pop("REGULA_PROJECT_DIR", None)
        r = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "report.py"),
             "--project", str(proj), "--include-audit",
             "--format", "html", "--output", str(out_file)],
            capture_output=True, text=True, env=env, timeout=120,
        )
        assert r.returncode == 0, r.stderr
        html = out_file.read_text(encoding="utf-8")
        assert "GLOBAL_SENSITIVE_MARKER" not in html
        assert "OTHER_CLIENT_MARKER" not in html


# ---------------------------------------------------------------------------
# Hooks pass project identity from cwd
# ---------------------------------------------------------------------------

def _skip_if_no_hooks():
    if not (HOOKS_DIR / "pre_tool_use.py").exists():
        pytest.skip("hooks/ not present (local dev file, not tracked in git)")


class TestHookScoping:
    def _run_hook(self, hook_name, payload, audit_dir, cwd):
        env = os.environ.copy()
        env["REGULA_AUDIT_DIR"] = str(audit_dir)
        env.pop("REGULA_PROJECT_DIR", None)
        env["PYTHONPATH"] = str(SCRIPTS_DIR)
        return subprocess.run(
            [sys.executable, str(HOOKS_DIR / f"{hook_name}.py")],
            input=json.dumps(payload), capture_output=True, text=True,
            env=env, timeout=30, cwd=str(cwd),
        )

    def test_post_hook_scopes_by_input_cwd(self, tmp_path):
        _skip_if_no_hooks()
        audit_dir = tmp_path / "audit"
        proj = tmp_path / "hookproj"
        proj.mkdir()
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "x.py", "content": "print(1)"},
            "session_id": "s1",
            "cwd": str(proj),
        }
        r = self._run_hook("post_tool_use", payload, audit_dir, tmp_path)
        assert r.returncode == 0
        scoped = list((audit_dir / "projects").rglob("audit_*.jsonl"))
        assert scoped, "hook event should land in a project chain"
        event = json.loads(scoped[0].read_text().strip().splitlines()[-1])
        assert event["project"] == "hookproj"
        assert not list(audit_dir.glob("audit_*.jsonl")), \
            "no machine-global write when cwd known"

    def test_post_hook_falls_back_to_process_cwd(self, tmp_path):
        _skip_if_no_hooks()
        audit_dir = tmp_path / "audit"
        proj = tmp_path / "cwdproj"
        proj.mkdir()
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "x.py", "content": "print(1)"},
            "session_id": "s1",
        }
        r = self._run_hook("post_tool_use", payload, audit_dir, proj)
        assert r.returncode == 0
        scoped = list((audit_dir / "projects").rglob("audit_*.jsonl"))
        assert scoped
        event = json.loads(scoped[0].read_text().strip().splitlines()[-1])
        assert event["project"] == "cwdproj"


# ---------------------------------------------------------------------------
# Runtime monitor: same rotation-continuity class
# ---------------------------------------------------------------------------

class TestMonitorRotation:
    def test_monitor_new_month_seeds_from_previous_file(self, tmp_path):
        from monitor import MonitorSession

        mdir = tmp_path / "monitor"
        sysdir = mdir / "rot-test"
        last = _write_chain(sysdir / "monitor_2026-06.jsonl", 2)

        class FakeResponse:
            __module__ = "openai.types.chat"
            model = "gpt-4"

            class usage:
                prompt_tokens = 10
                completion_tokens = 5
                input_tokens = None
                output_tokens = None

        session = MonitorSession(system_id="rot-test", monitor_dir=str(mdir))
        with session.trace() as t:
            t.record(FakeResponse())
        current = [f for f in sysdir.glob("monitor_*.jsonl")
                   if f.name != "monitor_2026-06.jsonl"]
        assert current, "a new monthly file should exist"
        first = json.loads(current[0].read_text().strip().splitlines()[0])
        assert first["previous_hash"] == last

    def test_monitor_verify_tolerates_legacy_restart(self, tmp_path):
        from cli_monitor import verify_monitor_chain

        mdir = tmp_path / "monitor"
        sysdir = mdir / "legacy-test"
        _write_chain(sysdir / "monitor_2026-05.jsonl", 2)
        _write_chain(sysdir / "monitor_2026-06.jsonl", 2)  # genesis restart
        valid, msg = verify_monitor_chain("legacy-test", str(mdir))
        assert valid is True
        assert "restart" in (msg or "").lower()
