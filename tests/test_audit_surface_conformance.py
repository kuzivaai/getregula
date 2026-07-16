# regula-ignore
"""Conformance guard: deliverable surfaces must never embed unscoped audit data.

Class rule (P1, 2026-07-16 — cross-client confidentiality): any module
that writes client-facing artefacts must obtain audit events exclusively
through log_event.collect_audit_trail (project-scoped). Raw
query_events() access is permitted only in the audit module itself and
in explicitly justified machine-local surfaces.

The guarded scope is discovered by WALKING scripts/ and hooks/ — never a
hardcoded list of known-offender files — so a new surface added tomorrow
is guarded the day it lands. (Guard style required by the class-fix
completeness rule: enumerate by walking, forbid the pattern family.)
"""

import re
from pathlib import Path

REPO = Path(__file__).parent.parent
SCRIPTS = REPO / "scripts"
HOOKS = REPO / "hooks"

# Modules allowed to call query_events(...) without a project_path= in
# the call text. Every entry must carry its justification.
QUERY_ALLOWLIST = {
    "log_event.py":      "owner module: defines the API and its own CLI (has --project)",
    "cli_admin.py":      "operator CLI over the machine store; exposes --project for scoping",
    "agent_monitor.py":  "machine-local monitoring output, never embedded in deliverables",
    "session.py":        "machine-local session summaries, never embedded in deliverables",
}


def _walk_py(*dirs):
    for d in dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.py")):
            yield p


def _call_sites(text: str, name: str):
    """Yield the ~200 chars following each `name(` CALL occurrence.

    Definition sites (`def name(...)`) are skipped — hooks define
    same-named no-op stubs in their ImportError fallbacks.
    """
    for m in re.finditer(re.escape(name) + r"\s*\(", text):
        prefix = text[max(0, m.start() - 10): m.start()]
        if re.search(r"\bdef\s+$", prefix):
            continue
        # Capture the full call by balancing parentheses (capped), so
        # multi-line calls are judged on their complete argument list.
        depth = 0
        end = m.end()
        for i in range(m.end() - 1, min(len(text), m.end() + 2000)):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        yield text[m.start(): end]


class TestQueryEventsScoping:
    def test_every_query_events_call_is_scoped_or_justified(self):
        offenders = []
        for path in _walk_py(SCRIPTS, HOOKS):
            text = path.read_text(encoding="utf-8")
            for site in _call_sites(text, "query_events"):
                if "project_path=" in site:
                    continue
                if path.name in QUERY_ALLOWLIST:
                    continue
                offenders.append(f"{path.name}: {site.splitlines()[0][:100]}")
        assert not offenders, (
            "Unscoped query_events() call outside the allowlist. Deliverable "
            "surfaces must use collect_audit_trail(project_path); machine-local "
            "surfaces need an allowlist entry WITH justification:\n  "
            + "\n  ".join(offenders)
        )

    def test_walk_is_not_vacuous(self):
        """The walk must actually see the audit API in use (pattern-rot guard)."""
        seen = sum(
            1 for p in _walk_py(SCRIPTS, HOOKS)
            if "query_events" in p.read_text(encoding="utf-8")
        )
        assert seen >= 3, "walking guard no longer sees query_events usage — pattern rotted"


class TestDeliverableWritersUseScopedCollector:
    """Any module that writes pack artefacts (detected by _write_and_record)
    must not touch the raw audit query/verify API at all."""

    def _pack_writers(self):
        writers = [
            p for p in _walk_py(SCRIPTS)
            if "_write_and_record" in p.read_text(encoding="utf-8")
        ]
        assert len(writers) >= 2, (
            "expected at least evidence_pack.py and conform.py to be discovered "
            "as pack writers — detection pattern rotted"
        )
        return writers

    def test_pack_writers_never_call_query_events(self):
        offenders = [
            p.name for p in self._pack_writers()
            if re.search(r"\bquery_events\s*\(", p.read_text(encoding="utf-8"))
        ]
        assert not offenders, (
            f"pack writers must use collect_audit_trail, not query_events: {offenders}"
        )

    def test_pack_writers_never_verify_chain_unscoped(self):
        offenders = []
        for p in self._pack_writers():
            for site in _call_sites(p.read_text(encoding="utf-8"), "verify_chain"):
                if "project_path=" not in site and "verify_chain_dir" not in site:
                    offenders.append(p.name)
        assert not offenders, (
            f"pack writers must not verify the machine-wide chain: {offenders}"
        )

    def test_audit_embedding_goes_through_collector(self):
        for p in self._pack_writers():
            text = p.read_text(encoding="utf-8")
            if "audit" in text.lower():
                assert "collect_audit_trail" in text, (
                    f"{p.name} references audit data but does not use "
                    "collect_audit_trail — scoped collection is mandatory"
                )


class TestProducersTagEvents:
    """Events written without project attribution land in the machine-wide
    store and are invisible to every project-scoped deliverable. Producers
    must pass project_path unless there is a documented reason not to."""

    LOG_ALLOWLIST = {
        "log_event.py": "owner module; its CLI exposes --project explicitly",
        "cli_admin.py": "operator CLI; --project optional by design (machine store is its job)",
        "session.py": (
            "session risk profile aggregates MACHINE-WIDE activity; writing "
            "it into a project chain would leak cross-project aggregates "
            "into that project's deliverables — it must stay machine-local"
        ),
    }

    def test_hooks_always_pass_project_path(self):
        offenders = []
        for path in _walk_py(HOOKS):
            text = path.read_text(encoding="utf-8")
            for site in _call_sites(text, "log_event"):
                if "project_path=" not in site:
                    offenders.append(f"{path.name}: {site.splitlines()[0][:80]}")
        assert not offenders, (
            "hook log_event() call without project_path= — events would land "
            "in the machine-wide store, unattributed:\n  " + "\n  ".join(offenders)
        )

    def test_script_producers_tag_or_are_justified(self):
        offenders = []
        for path in _walk_py(SCRIPTS):
            if path.name in self.LOG_ALLOWLIST:
                continue
            text = path.read_text(encoding="utf-8")
            for site in _call_sites(text, "log_event"):
                if "project_path=" not in site:
                    offenders.append(f"{path.name}: {site.splitlines()[0][:80]}")
        assert not offenders, (
            "script log_event() call without project_path= and without an "
            "allowlist justification:\n  " + "\n  ".join(offenders)
        )


class TestReadPathsDoNotCreateDirectories:
    """Reading a chain that does not exist must not create directories.
    Before this guard, every query/verify against a project with no
    chain left an empty projects/<slug>/ directory in the operator's
    REAL store (27 were found there on 2026-07-16)."""

    def test_query_and_verify_leave_no_trace(self, tmp_path, monkeypatch):
        import sys as _sys
        _sys.path.insert(0, str(SCRIPTS))
        root = tmp_path / "pristine-store"
        monkeypatch.setenv("REGULA_AUDIT_DIR", str(root))
        from log_event import query_events, verify_chain, collect_audit_trail
        ghost = tmp_path / "ghost_project"
        ghost.mkdir()
        assert query_events(project_path=str(ghost)) == []
        valid, _ = verify_chain(project_path=str(ghost))
        assert valid is True, "an absent chain is an empty valid chain"
        data = collect_audit_trail(str(ghost))
        assert data["event_count"] == 0
        assert not root.exists(), (
            "read-only audit access created directories in the store"
        )


class TestSecretRedaction:
    """Secret values must never be persisted to the audit trail — it is
    embedded in client-facing deliverables. The pre-tool hook only blocks
    HIGH-confidence findings; anything else executes and is logged, so
    the hooks must redact tool payloads before log_event.

    NOTE: fake keys below are synthetic test fixtures (AGENTS.md)."""

    def test_redact_secrets_replaces_known_pattern(self):
        import sys as _sys
        _sys.path.insert(0, str(SCRIPTS))
        from credential_check import redact_secrets
        fake_key = "sk-" + "a" * 30
        text = f"api_client = OpenAI(api_key='{fake_key}')"
        out = redact_secrets(text)
        assert fake_key not in out
        assert "[REDACTED:openai_api_key]" in out

    def test_redact_secrets_handles_empty_and_clean_text(self):
        import sys as _sys
        _sys.path.insert(0, str(SCRIPTS))
        from credential_check import redact_secrets
        assert redact_secrets("") == ""
        clean = "def add(a, b): return a + b"
        assert redact_secrets(clean) == clean

    def test_post_hook_never_persists_secret_values(self, tmp_path):
        import json
        import os
        import subprocess
        import sys as _sys
        if not (HOOKS / "post_tool_use.py").exists():
            import pytest
            pytest.skip("hooks/ not present (local dev file, not tracked in git)")
        audit_dir = tmp_path / "audit"
        proj = tmp_path / "redactproj"
        proj.mkdir()
        fake_key = "sk-" + "b" * 30
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": f"export OPENAI_API_KEY={fake_key}"},
            "tool_response": {"stdout": f"key was {fake_key}"},
            "session_id": "s-redact",
            "cwd": str(proj),
        }
        env = os.environ.copy()
        env["REGULA_AUDIT_DIR"] = str(audit_dir)
        env.pop("REGULA_PROJECT_DIR", None)
        r = subprocess.run(
            [_sys.executable, str(HOOKS / "post_tool_use.py")],
            input=json.dumps(payload), capture_output=True, text=True,
            env=env, timeout=30, cwd=str(tmp_path),
        )
        assert r.returncode == 0
        chain_files = list(audit_dir.rglob("audit_*.jsonl"))
        assert chain_files, "hook should have logged an event"
        logged = "\n".join(f.read_text(encoding="utf-8") for f in chain_files)
        assert fake_key not in logged, "raw secret value reached the audit trail"
        assert "[REDACTED:openai_api_key]" in logged
