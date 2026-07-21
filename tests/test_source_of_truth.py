#!/usr/bin/env python3
"""Source-of-truth enforcement tests.

The July 2026 audit found eight independently-drifted copies of SKIP_DIRS
across scripts/, and five modules doing bare sibling imports without the
mandatory sys.path.insert self-protection. Both defect classes are
structural: they pass every functional test right up until the copies
disagree. These tests make the drift itself a test failure.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

# Module names that scripts/ files can bare-import as siblings.
_SIBLING_MODULES = {p.stem for p in SCRIPTS_DIR.glob("*.py")} - {"__init__"}

# `demos/` helper scripts are standalone examples, not package modules.
_EXEMPT_FILES: set = set()


def test_no_local_skip_dir_literals():
    """Every skip-directory set must come from constants.SKIP_DIRS.

    A local literal (`skip_dirs = {...}` / `_SKIP_DIRS = {...}`) is exactly
    how six copies drifted apart: the canonical set's false-positive tuning
    (examples/, demos/, benchmarks/, .github/) silently did not propagate
    to `regula sbom`, cross-file flow analysis, or generated Article-11
    documentation.
    """
    offenders = []
    pattern = re.compile(r"^\s*_?(?:DATASET_)?(?:skip_dirs|SKIP_DIRS)\s*=\s*\{", re.M)
    for f in sorted(SCRIPTS_DIR.glob("*.py")):
        if f.name == "constants.py":
            continue
        for m in pattern.finditer(f.read_text(encoding="utf-8")):
            # An aliased import (`= SKIP_DIRS`) is fine; a set literal is not.
            offenders.append(f"{f.name}: {m.group(0).strip()}")
    assert not offenders, (
        "Local skip-dir set literals found — import constants.SKIP_DIRS "
        f"(union local extras explicitly) instead: {offenders}"
    )


def test_sibling_importers_have_path_insert():
    """Any scripts/ module that bare-imports a sibling must self-protect
    with sys.path.insert (any form), per .claude/rules/python-scripts.md.

    Without it, the module only imports when every caller happens to have
    seeded sys.path first — `import classify_risk` from a clean interpreter
    failed until July 2026.
    """
    import_re = re.compile(
        r"^\s*(?:from\s+(\w+)\s+import|import\s+(\w+)(?:\s|$|,))", re.M
    )
    offenders = []
    for f in sorted(SCRIPTS_DIR.glob("*.py")):
        if f.name in ("__init__.py",) or f.name in _EXEMPT_FILES:
            continue
        text = f.read_text(encoding="utf-8")
        imports_sibling = any(
            (m.group(1) or m.group(2)) in _SIBLING_MODULES - {f.stem}
            for m in import_re.finditer(text)
        )
        if imports_sibling and "sys.path.insert" not in text:
            offenders.append(f.name)
    assert not offenders, (
        "Modules bare-import siblings without sys.path.insert "
        f"self-protection: {offenders}"
    )


def test_envelope_single_source_of_truth():
    """cli.py and api_server.py must build the JSON envelope via
    envelope.build_envelope — identical keys, identical format_version.
    Two byte-for-byte copies shipped once, making the 'never change the
    envelope format' rule unenforceable."""
    from envelope import build_envelope
    import cli
    import api_server

    a = cli._build_envelope("x", {"k": 1}, 0)
    b = api_server._build_envelope("x", {"k": 1}, 0)
    c = build_envelope("x", {"k": 1}, 0)
    for env in (a, b, c):
        env.pop("timestamp")
    assert a == b == c, f"envelope drift: cli={a} api={b} shared={c}"

    # No independent envelope dict literals outside envelope.py.
    for fname in ("cli.py", "api_server.py"):
        text = (SCRIPTS_DIR / fname).read_text(encoding="utf-8")
        assert '"format_version"' not in text, (
            f"{fname} builds its own envelope literal — use envelope.build_envelope"
        )


if __name__ == "__main__":
    test_no_local_skip_dir_literals()
    print("PASS: no local skip-dir literals outside constants.py")
    test_sibling_importers_have_path_insert()
    print("PASS: all sibling-importing modules self-insert sys.path")
    test_envelope_single_source_of_truth()
    print("PASS: JSON envelope has a single source of truth")


def test_omnibus_flip_propagates_to_all_consumers():
    """Setting OMNIBUS_OJ_DATE in omnibus.py must flip the deadline copy in
    every consumer — remediation_plan, evidence_pack (via exec summary
    helper), exec_summary, assess, timeline, roadmap. Before July 2026 the
    prose was hand-copied across six files; the Council approval had to be
    edited into each one and two were missed."""
    import importlib
    import omnibus

    saved = (omnibus.OMNIBUS_OJ_DATE, omnibus.OMNIBUS_ENACTED,
             omnibus.OMNIBUS_STATUS, omnibus.BINDING_NOTE)
    try:
        omnibus.OMNIBUS_OJ_DATE = "2026-07-20"
        omnibus.OMNIBUS_ENACTED = True
        omnibus.OMNIBUS_STATUS = f"Published in OJ {omnibus.OMNIBUS_OJ_DATE}; in force"
        omnibus.BINDING_NOTE = f"In force since OJ publication ({omnibus.OMNIBUS_OJ_DATE})."

        outputs = {}
        for mod_name in ("remediation_plan", "exec_summary", "assess", "timeline", "roadmap"):
            importlib.reload(importlib.import_module(mod_name))
            outputs[mod_name] = ""
        import remediation_plan
        import exec_summary
        import assess
        import timeline
        outputs["remediation_plan"] = remediation_plan.DEADLINE_HIGH_RISK
        outputs["exec_summary"] = exec_summary.TIER_DESCRIPTIONS["high_risk"]
        outputs["assess"] = "\n".join(assess._omnibus_deadline_lines())
        outputs["timeline"] = timeline._OMNIBUS_NOTE_STATUS + " " + json.dumps(timeline.TIMELINE)
        outputs["roadmap"] = ""  # roadmap builds its note per-call below
        from omnibus import status_parenthetical
        outputs["roadmap"] = status_parenthetical()

        for name, text in outputs.items():
            low = text.lower()
            assert "pending oj publication" not in low, f"{name} did not flip: ...{text[-120:]}"
            assert "pending formal adoption" not in low, f"{name} kept stale copy"
            assert "in force" in low, f"{name} missing enacted wording: ...{text[-120:]}"
    finally:
        (omnibus.OMNIBUS_OJ_DATE, omnibus.OMNIBUS_ENACTED,
         omnibus.OMNIBUS_STATUS, omnibus.BINDING_NOTE) = saved
        for mod_name in ("remediation_plan", "exec_summary", "assess", "timeline", "roadmap", "report"):
            import importlib as _il
            _il.reload(_il.import_module(mod_name))


def test_no_stale_omnibus_literal_anywhere():
    """'PENDING FORMAL ADOPTION' is the copy that went stale on 29 June
    2026 — it must never reappear as a hardcoded literal."""
    offenders = []
    for f in sorted(SCRIPTS_DIR.glob("*.py")):
        if "PENDING FORMAL ADOPTION" in f.read_text(encoding="utf-8"):
            offenders.append(f.name)
    assert not offenders, f"stale Omnibus copy hardcoded in: {offenders}"


def test_site_schema_softwareversion_matches_cli_version():
    """Every schema.org softwareVersion on the site must equal
    constants.VERSION. The 6 July 2026 release bumped about.html but
    missed index.html, regions/uae.html, and both locale pages — they
    served 1.7.3 until 9 July. Mutation-tested: planting 1.0.0 in any
    site page fails this test."""
    from constants import VERSION
    site_dir = Path(__file__).parent.parent / "site"
    pattern = re.compile(r'"softwareVersion":\s*"([^"]+)"')
    offenders = []
    seen = 0
    for page in sorted(site_dir.rglob("*.html")):
        for m in pattern.finditer(page.read_text(encoding="utf-8", errors="replace")):
            seen += 1
            if m.group(1) != VERSION:
                offenders.append(f"{page.relative_to(site_dir)}: {m.group(1)}")
    assert seen >= 5, f"expected >=5 softwareVersion declarations, found {seen}"
    assert not offenders, (
        f"schema.org softwareVersion drifted from constants.VERSION "
        f"({VERSION}): {offenders}"
    )


def test_current_version_declared_consistently_everywhere():
    """Every file that declares Regula's CURRENT version must equal
    constants.VERSION. The v1.7.5 release (16 Jul 2026) shipped with six
    stale 1.7.4 declarations — CITATION.cff (version + title),
    mcp-server.json, site/llms.txt, references/annex_iv_template.md and
    the MODEL_CARD header — because only pyproject/constants/badges/
    schema.org were enforced. Historical references ("measured on
    v1.7.4", demo recordings, spec examples) are deliberately NOT
    checked: they are provenance, not current-version claims."""
    from constants import VERSION
    root = Path(__file__).parent.parent

    # (file, regex with one capture group for the declared version)
    # pyproject must NOT declare a literal version: it is dynamic, read
    # from scripts/constants.py at build time (R1 single-sourcing).
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'dynamic = ["version"]' in pyproject, (
        "pyproject.toml must declare version as dynamic (single-sourced "
        "from scripts/constants.py)"
    )
    assert not re.search(r'^version\s*=\s*"', pyproject, re.M), (
        "pyproject.toml must not carry a literal [project] version — "
        "scripts/constants.py is the single source"
    )

    semver = r"([0-9]+(?:\.[0-9]+)*)"
    declarations = [
        ("CITATION.cff", r'^version:\s*"([^"]+)"'),
        ("CITATION.cff", rf'compliance scanner for code \(v{semver}\)'),
        ("mcp-server.json", r'"version":\s*"([^"]+)"'),
        ("site/llms.txt", rf'^- Version:\s*{semver}'),
        ("references/annex_iv_template.md", rf'_For use with Regula v{semver}_'),
        ("docs/MODEL_CARD.md", rf'^\| Version \| {semver}'),
        ("docs/MODEL_CARD.md", rf'This model card describes Regula v{semver}'),
    ]
    offenders = []
    for rel_path, pattern in declarations:
        text = (root / rel_path).read_text(encoding="utf-8")
        m = re.search(pattern, text, re.M)
        assert m, f"{rel_path}: current-version declaration not found ({pattern})"
        if m.group(1) != VERSION:
            offenders.append(f"{rel_path}: declares {m.group(1)}")
    assert not offenders, (
        f"current-version declarations drifted from constants.VERSION "
        f"({VERSION}): {offenders}"
    )


def test_pack_writers_pin_lf_newlines():
    """Every write_text in the evidence/conformity pack writers must pass
    newline="\\n". The recorded SHA-256 hashes are computed on the LF
    content string; without the pin, write_text translates \\n to
    os.linesep on Windows and `regula verify` reports every pack file
    MODIFIED (10 Jul 2026 audit finding)."""
    import re
    for script in ("evidence_pack.py", "conform.py"):
        src = (SCRIPTS_DIR / script).read_text(encoding="utf-8")
        offenders = []
        for m in re.finditer(r"write_text\(([^)]*)\)", src):
            if "newline=" not in m.group(1):
                line = src[:m.start()].count("\n") + 1
                offenders.append(f"scripts/{script}:{line}")
        assert not offenders, (
            f"write_text without newline pin (breaks pack hashes on "
            f"Windows): {offenders}"
        )
