# regula-ignore
"""
Regula Quickstart — 60-second onboarding.

Creates a minimal policy, runs a first scan, and shows the user what to do next.
Non-interactive by default. Designed to get a developer from zero to first scan
in under a minute.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


_DEFAULT_POLICY = """\
version: "1.0"
organisation: "{org}"

frameworks:
  - eu_ai_act

thresholds:
  block_above: 80
  warn_above: 50

governance:
  ai_officer:
    name: ""
    contact: ""
"""


def run_quickstart(project_dir: str = ".", org: str = "My Organisation",
                   format_type: str = "text") -> dict:
    """Run quickstart onboarding flow.

    Steps:
        1. Check if policy already exists (skip creation if so)
        2. Create minimal policy file
        3. Run a scan of the project
        4. Show summary + next steps

    Returns:
        dict with keys: policy_created, policy_path, scan_results, next_steps
    """
    from report import scan_files

    project = Path(project_dir).resolve()
    project.mkdir(parents=True, exist_ok=True)
    start = time.time()

    # Step 1: Policy file
    policy_path = project / "regula-policy.yaml"
    policy_json = project / "regula-policy.json"
    policy_created = False

    if policy_path.exists() or policy_json.exists():
        existing = str(policy_path if policy_path.exists() else policy_json)
    else:
        policy_content = _DEFAULT_POLICY.format(org=org)
        policy_path.write_text(policy_content, encoding="utf-8")
        policy_created = True
        existing = str(policy_path)

    # Step 2: Run scan
    findings = scan_files(str(project))
    active = [f for f in findings if not f.get("suppressed")]

    # Categorise
    blocks = [f for f in active if f.get("tier") == "prohibited" or f.get("confidence_score", 0) >= 80]
    warns = [f for f in active if f not in blocks and f.get("confidence_score", 0) >= 50]
    infos = [f for f in active if f not in blocks and f not in warns]

    elapsed = time.time() - start

    # Step 3: Next steps
    next_steps = []
    if policy_created:
        next_steps.append("Edit regula-policy.yaml — set your organisation name and AI officer")
    next_steps.append("Run 'regula check .' for the full detailed scan (every finding, not just the top 3)")
    next_steps.append("Run 'regula doctor' to verify your setup")
    if blocks:
        next_steps.append(f"Review {len(blocks)} BLOCK finding(s) — these would fail CI")
    next_steps.append("Run 'regula install claude-code' to add pre-commit hooks")
    next_steps.append("Run 'regula gap --project .' for compliance gap analysis")
    next_steps.append("Run 'regula bias' to evaluate model stereotype bias (requires Ollama)")

    # Top findings preview — value-first onboarding (CLI UX best practice).
    # Quickstart used to report only counts ("1 BLOCK finding") and force the
    # user to run a second command to see what was found. Now it surfaces up
    # to the top 3 actionable findings inline so the user gets the core
    # benefit immediately.
    preview = []
    for f in (blocks + warns)[:3]:
        score = f.get("confidence_score", 0)
        # Derive the display tier directly — quickstart bypasses
        # findings_view.partition_findings, so _finding_tier is unset.
        if f.get("tier") == "prohibited" or score >= 80:
            tier_label = "block"
        elif score >= 50:
            tier_label = "warn"
        else:
            tier_label = "info"
        preview.append({
            "file": f.get("file", "?"),
            "tier": tier_label,
            "category": f.get("category", "Unknown"),
            "description": f.get("description", ""),
            "score": score,
        })

    result = {
        "policy_created": policy_created,
        "policy_path": existing,
        "scan_summary": {
            "total_findings": len(active),
            "block": len(blocks),
            "warn": len(warns),
            "info": len(infos),
            "files_scanned": len(set(f.get("file", "") for f in findings)),
        },
        "top_findings": preview,
        "elapsed_seconds": round(elapsed, 1),
        "next_steps": next_steps,
    }

    if format_type == "text":
        _print_text(result)

    return result


def _print_text(result: dict) -> None:
    """Print human-readable quickstart output."""
    print("\nRegula Quickstart\n")

    # Policy
    if result["policy_created"]:
        print(f"  Created: {result['policy_path']}")
    else:
        print(f"  Found existing policy: {result['policy_path']}")

    # Scan summary
    s = result["scan_summary"]
    print(f"\n  First scan complete ({result['elapsed_seconds']}s)")
    print(f"  {'Files scanned:':<20}{s['files_scanned']}")
    print(f"  {'BLOCK findings:':<20}{s['block']}")
    print(f"  {'WARN findings:':<20}{s['warn']}")
    print(f"  {'INFO findings:':<20}{s['info']}")

    # Show top 3 findings inline (value-first — user sees the actual issue
    # rather than just a count). Anything beyond 3 stays hidden behind
    # `regula check .` to avoid wall-of-text on a noisy first scan.
    top = result.get("top_findings", [])
    if top:
        print(f"\n  Top findings:")
        for f in top:
            tier_label = f.get("tier", "info").upper()
            score = f.get("score", 0)
            file_label = f.get("file", "?")
            cat = f.get("category", "")
            desc = f.get("description", "")
            print(f"    [{tier_label}] [{score:3d}] {file_label}")
            if cat:
                print(f"          {cat}")
            if desc and desc != cat:
                print(f"          {desc}")

    # Next steps
    print(f"\n  Next steps:")
    for i, step in enumerate(result["next_steps"], 1):
        print(f"    {i}. {step}")
    print()
