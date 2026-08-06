"""Independent checks and mutation controls for the readiness pack."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

# Bare import, per .claude/rules/python-scripts.md. The package-qualified form
# `from scripts.validate_validation_readiness import ...` resolved on the
# author's machine ONLY because an editable install of regula-ai puts a path
# hook on sys.path mapping the name `scripts` to this working copy
# (`__editable___regula_ai_1_7_0_finder.MAPPING`). A clean checkout has no such
# mapping, so CI failed with `ModuleNotFoundError: No module named 'scripts'`
# on Python 3.10, 3.11, 3.12 and 3.13 the first time a pull request ever ran on
# this branch. That is the N1 class: provenance that exists only locally.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_validation_readiness import DEFAULT_PACK, validate  # noqa: E402


def _mutate(relative: str, old: str, new: str, expected: str) -> None:
    with tempfile.TemporaryDirectory(prefix="regula-readiness-mutation-") as tmp:
        pack = Path(tmp) / "pack"
        shutil.copytree(DEFAULT_PACK, pack)
        path = pack / relative
        text = path.read_text(encoding="utf-8")
        assert old in text, f"mutation source absent: {relative}: {old}"
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        errors = validate(pack, require_tracked=False)
        assert any(expected in error for error in errors), (expected, errors)


def test_validation_readiness_pack_passes() -> None:
    assert validate(DEFAULT_PACK, require_tracked=False) == []


def test_readiness_mutation_controls() -> None:
    mutations = (
        ("00-OWNER-DECISION-PACK.md", "VENTURE DECISION: STOP", "VENTURE DECISION: ", "missing status: VENTURE DECISION: STOP"),
        ("00-OWNER-DECISION-PACK.md", "PRODUCT PILOT: NOT APPROVED", "PRODUCT PILOT: APPROVED", "missing status: PRODUCT PILOT: NOT APPROVED"),
        ("00-OWNER-DECISION-PACK.md", "Unresolved facts", "Validated demand\n\n## Unresolved facts", "validated-demand claim"),
        ("06-ADVICE-PERMISSIONS-AND-COST-REGISTER.md", "| PERM-01 | Customer/supplier contact | NOT AUTHORISED", "| PERM-01 | Customer/supplier contact | AUTHORISED", "owner permission not disabled: PERM-01"),
        ("06-ADVICE-PERMISSIONS-AND-COST-REGISTER.md", "| COST-03 | Immigration advice | QUOTE_REQUIRED", "| COST-03 | Immigration advice | pending", "cost lacks evidence classification: COST-03"),
        ("templates/CONSENT.md", "this form", "this template is legally approved. this form", "legally-approved template claim"),
        ("04-MANUAL-BASELINE-PROTOCOL.md", "Regula output is hidden", "Regula output is visible", "04-MANUAL-BASELINE-PROTOCOL.md: missing control: manual-baseline blinding"),
        ("05-INDEPENDENT-TECHNICAL-LABELLING-PROTOCOL.md", "two independent qualified human raters", "one unblinded rater", "05-INDEPENDENT-TECHNICAL-LABELLING-PROTOCOL.md: missing control: independent rater requirement"),
        ("05-INDEPENDENT-TECHNICAL-LABELLING-PROTOCOL.md", "Adjudication is", "Resolution is", "05-INDEPENDENT-TECHNICAL-LABELLING-PROTOCOL.md: missing control: adjudication requirement"),
        ("05-INDEPENDENT-TECHNICAL-LABELLING-PROTOCOL.md", "`NOT_ASSESSABLE`", "`UNKNOWN_LABEL`", "05-INDEPENDENT-TECHNICAL-LABELLING-PROTOCOL.md: missing control: not-assessable label"),
        ("03-CONSENT-AND-DATA-HANDLING.md", "No real participant", "Jane Smith@example.com is a participant. No real participant", "possible real participant personal data"),
        ("01-TRUTH-AND-DEPENDENCIES.md", "Kuziva originated and built the initial Regula project.", "Collaborator originated and built the initial Regula project.", "01-TRUTH-AND-DEPENDENCIES.md: missing control: founder-history boundary"),
    )
    for mutation in mutations:
        _mutate(*mutation)

    with tempfile.TemporaryDirectory(prefix="regula-readiness-mutation-") as tmp:
        pack = Path(tmp) / "pack"
        shutil.copytree(DEFAULT_PACK, pack)
        (pack / "templates/ACCESS-LOG.md").unlink()
        assert any("missing required file: templates/ACCESS-LOG.md" in e for e in validate(pack, require_tracked=False))

        shutil.copy2(DEFAULT_PACK / "templates/ACCESS-LOG.md", pack / "templates/ACCESS-LOG.md")
        data = json.loads((pack / "readiness.json").read_text(encoding="utf-8"))
        data["venture_decision"] = "PROCEED"
        (pack / "readiness.json").write_text(json.dumps(data), encoding="utf-8")
        assert any("readiness.json disagreement: venture_decision" in e for e in validate(pack, require_tracked=False))
