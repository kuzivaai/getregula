"""H6: Regression test for compromised-package text-format output.

The text formatter in dependency_scan.format_dep_text was refactored to
use the correct dict keys (package/version/advisory_id/description/severity)
instead of the old never-populated keys (name/detail). This test ensures
the refactored formatter produces the expected header and advisory lines
for crafted compromised-package results.

Kept in a dedicated test file per project convention.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from dependency_scan import format_dep_text  # noqa: E402


def _make_scan_result(compromised: list[dict]) -> dict:
    """Build a minimal scan-result dict suitable for format_dep_text."""
    return {
        "project": "/tmp/test-project",
        "scan_date": "2026-04-16T12:00:00Z",
        "pinning_score": 80,
        "all_dependencies": [
            {"name": "torch", "version": "2.1.0", "pinning": "exact", "is_ai": True},
            {"name": "evil-pkg", "version": "1.0.0", "pinning": "exact", "is_ai": False},
        ],
        "ai_dependencies": [
            {"name": "torch", "version": "2.1.0", "pinning": "exact", "is_ai": True},
        ],
        "lockfiles": [],
        "compromised": compromised,
        "compromised_count": len(compromised),
        "summary": "GOOD: Dependencies are well-pinned.",
    }


# ── Tests ─────────────────────────────────────────────────────────


def test_compromised_section_header_present():
    """The COMPROMISED PACKAGES header appears with the correct count."""
    result = _make_scan_result([
        {
            "package": "evil-pkg",
            "version": "1.0.0",
            "advisory_id": "REGULA-2026-001",
            "description": "Known malware injecting credential-stealing code",
            "remediation": "Remove immediately",
            "severity": "critical",
        },
    ])
    text = format_dep_text(result)
    assert "COMPROMISED PACKAGES (1):" in text


def test_compromised_package_name_and_version_in_output():
    """Each compromised entry shows package@version."""
    result = _make_scan_result([
        {
            "package": "evil-pkg",
            "version": "1.0.0",
            "advisory_id": "REGULA-2026-001",
            "description": "Known malware",
            "remediation": "",
            "severity": "critical",
        },
    ])
    text = format_dep_text(result)
    assert "evil-pkg@1.0.0" in text


def test_compromised_severity_shown():
    """The severity tag appears in square brackets."""
    result = _make_scan_result([
        {
            "package": "evil-pkg",
            "version": "1.0.0",
            "advisory_id": "REGULA-2026-001",
            "description": "Known malware",
            "remediation": "",
            "severity": "critical",
        },
    ])
    text = format_dep_text(result)
    assert "[critical]" in text


def test_compromised_description_shown():
    """The advisory description text appears on the same line."""
    desc = "Backdoor discovered in build pipeline"
    result = _make_scan_result([
        {
            "package": "evil-pkg",
            "version": "1.0.0",
            "advisory_id": "REGULA-2026-002",
            "description": desc,
            "remediation": "",
            "severity": "high",
        },
    ])
    text = format_dep_text(result)
    assert desc in text


def test_compromised_advisory_id_shown():
    """The advisory ID appears on a follow-up indented line."""
    result = _make_scan_result([
        {
            "package": "evil-pkg",
            "version": "1.0.0",
            "advisory_id": "REGULA-2026-001",
            "description": "Known malware",
            "remediation": "",
            "severity": "critical",
        },
    ])
    text = format_dep_text(result)
    assert "advisory: REGULA-2026-001" in text


def test_compromised_multiple_packages():
    """Multiple compromised packages each get their own entry."""
    result = _make_scan_result([
        {
            "package": "evil-pkg",
            "version": "1.0.0",
            "advisory_id": "REGULA-2026-001",
            "description": "Known malware",
            "remediation": "",
            "severity": "critical",
        },
        {
            "package": "shady-lib",
            "version": "0.3.2",
            "advisory_id": "REGULA-2026-003",
            "description": "Exfiltrates environment variables",
            "remediation": "Upgrade to 0.3.3",
            "severity": "high",
        },
    ])
    text = format_dep_text(result)
    assert "COMPROMISED PACKAGES (2):" in text
    assert "evil-pkg@1.0.0" in text
    assert "shady-lib@0.3.2" in text
    assert "[critical]" in text
    assert "[high]" in text
    assert "advisory: REGULA-2026-001" in text
    assert "advisory: REGULA-2026-003" in text


def test_no_compromised_section_when_empty():
    """When no packages are compromised, the section is absent."""
    result = _make_scan_result([])
    text = format_dep_text(result)
    assert "COMPROMISED" not in text


def test_compromised_without_version():
    """A compromised entry with no version omits the @version suffix."""
    result = _make_scan_result([
        {
            "package": "evil-pkg",
            "version": "",
            "advisory_id": "REGULA-2026-001",
            "description": "Known malware",
            "remediation": "",
            "severity": "critical",
        },
    ])
    text = format_dep_text(result)
    # Should show just the package name without @
    lines = text.splitlines()
    compromised_lines = [ln for ln in lines if "evil-pkg" in ln and "advisory" not in ln]
    assert len(compromised_lines) >= 1
    # Should NOT have "evil-pkg@" with empty version
    assert "evil-pkg@" not in text


def test_compromised_format_line_structure():
    """Verify the exact line format: '  pkg@ver [severity]: description'."""
    result = _make_scan_result([
        {
            "package": "evil-pkg",
            "version": "1.0.0",
            "advisory_id": "REGULA-2026-001",
            "description": "Known malware",
            "remediation": "",
            "severity": "critical",
        },
    ])
    text = format_dep_text(result)
    lines = text.splitlines()
    # Find the line with the package entry (not the advisory line)
    pkg_lines = [ln for ln in lines if "evil-pkg@1.0.0" in ln]
    assert len(pkg_lines) == 1
    line = pkg_lines[0]
    # Should match: "  evil-pkg@1.0.0 [critical]: Known malware"
    assert line.strip() == "evil-pkg@1.0.0 [critical]: Known malware"
