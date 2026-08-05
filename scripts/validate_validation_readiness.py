#!/usr/bin/env python3
"""Validate the preparation-only validation-readiness decision pack."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACK = REPO_ROOT / "docs" / "venture" / "validation-readiness-2026-08-05"

REQUIRED_FILES = (
    "00-OWNER-DECISION-PACK.md",
    "01-TRUTH-AND-DEPENDENCIES.md",
    "02-DISCOVERY-PROTOCOL.md",
    "03-CONSENT-AND-DATA-HANDLING.md",
    "04-MANUAL-BASELINE-PROTOCOL.md",
    "05-INDEPENDENT-TECHNICAL-LABELLING-PROTOCOL.md",
    "06-ADVICE-PERMISSIONS-AND-COST-REGISTER.md",
    "07-GO-HOLD-STOP-GATE.md",
    "SOURCES.md",
    "readiness.json",
    "templates/PARTICIPANT-INFORMATION.md",
    "templates/CONSENT.md",
    "templates/CONFIDENTIALITY.md",
    "templates/RECORDING-CONSENT.md",
    "templates/DOCUMENT-AND-REPOSITORY-PERMISSION.md",
    "templates/DATA-REUSE-PERMISSION.md",
    "templates/WITHDRAWAL-AND-DELETION.md",
    "templates/DATA-RECEIPT-REGISTER.md",
    "templates/ACCESS-LOG.md",
    "templates/INCIDENT-ESCALATION.md",
    "templates/DESTRUCTION-CONFIRMATION.md",
    "templates/RECRUITMENT-SPECIFICATION.md",
    "templates/ANNOTATION-CODEBOOK.md",
    "templates/RATER-QUALIFICATION-AND-CONFLICT.md",
    "templates/DISAGREEMENT-AND-ADJUDICATION.md",
    "templates/CORPUS-MANIFEST.json",
    "templates/DEVIATION-REGISTER.md",
    "templates/CONTRIBUTION-EVIDENCE.md",
)

STATUS_LINES = (
    "STATUS: PREPARATION ONLY",
    "EXTERNAL ACTION: DISABLED",
    "VENTURE DECISION: STOP",
    "PRODUCT PILOT: NOT APPROVED",
)

HYPOTHESIS = (
    "A small UK AI supplier is responding to a UK general insurer’s "
    "production-onboarding evidence request for an AI-assisted claims-triage system."
)

FORBIDDEN_CLAIMS = (
    (re.compile(r"\bvalidated demand\b", re.I), "validated-demand claim"),
    (re.compile(r"\b(?:viability|scalability)\s*:\s*demonstrated\b", re.I), "demonstrated venture claim"),
    (re.compile(r"\b(?:endorsement|eligibility)\s+(?:is\s+)?(?:likely|established|demonstrated|approved)\b", re.I), "endorsement or eligibility claim"),
    (re.compile(r"\bownership (?:was|has been) transferred\b", re.I), "ownership-transfer claim"),
    (re.compile(r"\bPhuluso (?:originated|built|created) (?:the initial )?(?:Regula|software|project)\b", re.I), "false founder-history claim"),
    (re.compile(r"\blawful basis\s*:\s*(?!OWNER_INPUT_REQUIRED|ADVISER_INPUT_REQUIRED|UNRESOLVED)", re.I), "settled lawful-basis claim"),
    (re.compile(r"\b(?:template|form)s?\s+(?:is\s+)?legally approved\b", re.I), "legally-approved template claim"),
)


def _tracked(repo_root: Path, path: Path) -> bool:
    """Check tracked status without trusting readiness.json."""
    import subprocess

    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.relative_to(repo_root))],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def validate(pack: Path, *, require_tracked: bool = True) -> list[str]:
    errors: list[str] = []
    repo_root = REPO_ROOT
    documents: dict[str, str] = {}

    for relative in REQUIRED_FILES:
        path = pack / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"empty required file: {relative}")
        if require_tracked and pack.is_relative_to(repo_root) and not _tracked(repo_root, path):
            errors.append(f"untracked required file: {relative}")
        if path.suffix == ".md":
            documents[relative] = path.read_text(encoding="utf-8")

    markdown = "\n".join(documents.values())
    for relative, text in documents.items():
        for status in STATUS_LINES:
            if status not in text:
                errors.append(f"{relative}: missing status: {status}")

    if HYPOTHESIS not in markdown:
        errors.append("exact discovery hypothesis missing")
    if "DISCOVERY HYPOTHESIS STATUS: UNVERIFIED" not in markdown:
        errors.append("discovery hypothesis is not marked unverified")

    for pattern, label in FORBIDDEN_CLAIMS:
        if pattern.search(markdown):
            errors.append(f"forbidden {label}")

    required_controls = {
        r"Kuziva originated and built the initial Regula project\.": "founder-history boundary",
        r"PROPOSED_FUTURE_ROLE": "prospective-role classification",
        r"REAL DATA COLLECTION: DISABLED": "real-data disablement",
        r"LEGAL REVIEW: REQUIRED": "legal review marker",
        r"DATA-PROTECTION REVIEW: REQUIRED": "data-protection review marker",
        r"Regula output is hidden": "manual-baseline blinding",
        r"two independent qualified human raters": "independent rater requirement",
        r"blind to Regula and baseline output": "technical-label blinding",
        r"raw\s+disagreements": "raw disagreement retention",
        r"adjudication": "adjudication requirement",
        r"NOT_ASSESSABLE": "not-assessable label",
        r"ABSTAIN": "abstention label",
    }
    for pattern, label in required_controls.items():
        if not re.search(pattern, markdown, re.I):
            errors.append(f"missing control: {label}")

    permissions = documents.get("06-ADVICE-PERMISSIONS-AND-COST-REGISTER.md", "")
    for line in permissions.splitlines():
        if line.startswith("| PERM-") and "NOT AUTHORISED" not in line:
            errors.append(f"owner permission not disabled: {line.split('|')[1].strip()}")
        if line.startswith("| COST-") and not any(
            marker in line
            for marker in ("OFFICIAL_FEE", "PUBLIC_LIST_PRICE", "NON_BINDING_ESTIMATE", "QUOTE_REQUIRED", "UNKNOWN")
        ):
            errors.append(f"cost lacks evidence classification: {line.split('|')[1].strip()}")

    data_doc = documents.get("03-CONSENT-AND-DATA-HANDLING.md", "")
    if re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", data_doc):
        errors.append("possible real participant personal data")

    readiness_path = pack / "readiness.json"
    if readiness_path.is_file():
        try:
            readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            errors.append(f"invalid readiness.json: {exc}")
        else:
            expected = {
                "venture_decision": "STOP",
                "product_pilot_status": "NOT_APPROVED",
                "external_action": "NOT_AUTHORISED",
                "real_data_collection": "DISABLED",
                "discovery_hypothesis_status": "PREREGISTERED_NOT_EXECUTED",
            }
            for key, value in expected.items():
                if readiness.get(key) != value:
                    errors.append(f"readiness.json disagreement: {key}")
            owner_doc = documents.get("00-OWNER-DECISION-PACK.md", "")
            recommendation = readiness.get("owner_recommendation", "")
            if f"OWNER_RECOMMENDATION: {recommendation}" not in owner_doc:
                errors.append("readiness.json disagreement: owner_recommendation")

    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--allow-untracked", action="store_true")
    args = parser.parse_args(argv)
    errors = validate(args.pack.resolve(), require_tracked=not args.allow_untracked)
    if errors:
        print(f"validation-readiness pack: FAIL ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"validation-readiness pack: PASS ({len(REQUIRED_FILES)} required files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
