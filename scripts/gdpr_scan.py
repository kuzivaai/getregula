#!/usr/bin/env python3
# regula-ignore
"""GDPR code pattern scanner with dual-compliance hotspot detection."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from gdpr_patterns import GDPR_PATTERNS, DUAL_COMPLIANCE_HOTSPOTS, GDPR_LIFECYCLE_PHASES
from constants import CODE_EXTENSIONS, SKIP_DIRS
from report import classify_provenance, _is_open_question


def scan_gdpr(project_path: str, scope: str = "all") -> dict:
    """Scan project for GDPR-relevant code patterns.

    Returns dict with findings, hotspots, and summary.
    """
    project = Path(project_path).resolve()
    findings = []
    hotspot_files = {}  # file -> list of hotspot categories

    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            filepath = Path(root) / filename
            if filepath.suffix not in CODE_EXTENSIONS:
                continue

            provenance = classify_provenance(filepath)
            if scope == "production" and provenance != "production":
                continue

            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
            except (PermissionError, OSError):
                continue

            rel_path = str(filepath.relative_to(project))

            for pattern, category, articles, description, confidence_label in GDPR_PATTERNS:
                matches = pattern.finditer(content)
                for match in matches:
                    line_num = content[:match.start()].count("\n") + 1
                    conf_score = {"high": 75, "medium": 55, "low": 35}.get(confidence_label, 50)

                    # Check for dual-compliance hotspot
                    hotspot = DUAL_COMPLIANCE_HOTSPOTS.get(category)

                    finding = {
                        "file": rel_path,
                        "line": line_num,
                        "category": category,
                        "description": description,
                        "gdpr_articles": articles,
                        "confidence_score": conf_score,
                        "confidence_label": confidence_label,
                        "provenance": provenance,
                        "lifecycle_phases": GDPR_LIFECYCLE_PHASES.get(category, ["develop"]),
                        "matched_text": match.group()[:80],
                        "regulation": "gdpr",
                    }

                    if hotspot:
                        finding["dual_compliance"] = True
                        finding["ai_act_articles"] = hotspot["ai_act"]
                        finding["hotspot_description"] = hotspot["description"]
                        # Track hotspot files
                        hotspot_files.setdefault(rel_path, []).append(category)
                    else:
                        finding["dual_compliance"] = False

                    finding["open_question"] = _is_open_question(finding)
                    findings.append(finding)
                    break  # One finding per pattern per file

    # Build summary
    hotspot_count = len(hotspot_files)
    article_counts = {}
    for f in findings:
        for art in f["gdpr_articles"]:
            article_counts[art] = article_counts.get(art, 0) + 1

    return {
        "findings": findings,
        "summary": {
            "total_findings": len(findings),
            "dual_compliance_hotspot_files": hotspot_count,
            "dual_compliance_findings": len([f for f in findings if f.get("dual_compliance")]),
            "hotspot_files": list(hotspot_files.keys()),
            "articles_triggered": article_counts,
            "high_confidence": len([f for f in findings if f["confidence_label"] == "high"]),
            "medium_confidence": len([f for f in findings if f["confidence_label"] == "medium"]),
            "low_confidence": len([f for f in findings if f["confidence_label"] == "low"]),
        },
    }
