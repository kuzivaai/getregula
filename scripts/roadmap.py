# regula-ignore
"""Compliance roadmap generator — deadline-aware, week-by-week action plan.

Uses the Action Priority Matrix methodology (PMI/MindTools):
priority_score = criticality × (1 / effort)
Quick wins scheduled first.

Effort estimates are heuristic ranges for a typical SME project.
No authoritative per-article effort benchmarks exist.
"""

import math
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from remediation_plan import ARTICLE_EFFORT, DEADLINE_HIGH_RISK


# ---------------------------------------------------------------------------
# Per-article fix guidance — maps each article to the regula command that
# generates the relevant remediation scaffold.
# ---------------------------------------------------------------------------

ARTICLE_FIX_GUIDANCE = {
    "5": {
        "command": "regula fix --project .",
        "description": "Remove prohibited AI functionality identified in scan",
    },
    "9": {
        "command": "regula docs --project . --qms",
        "description": "Generate risk management system scaffold (QMS template)",
    },
    "10": {
        "command": "regula docs --project .",
        "description": "Generate data governance documentation scaffold",
    },
    "11": {
        "command": "regula docs --project .",
        "description": "Generate Annex IV technical documentation draft",
    },
    "12": {
        "command": "regula fix --project .",
        "description": "Generate logging and audit trail implementation scaffold",
    },
    "13": {
        "command": "regula disclose --project .",
        "description": "Generate Article 50 transparency disclosure",
    },
    "14": {
        "command": "regula oversight --project .",
        "description": "Analyse human oversight patterns and generate recommendations",
    },
    "15": {
        "command": "regula fix --project .",
        "description": "Generate robustness and cybersecurity fix scaffolds",
    },
}


# Phase definitions (validated against ISO 42001 implementation methodology)
ROADMAP_PHASES = [
    {"name": "Quick Wins", "description": "Transparency disclosures, AI disclosure in README, low-effort documentation"},
    {"name": "Documentation", "description": "Risk management, data governance, model cards, technical documentation"},
    {"name": "Technical Implementation", "description": "Human oversight gates, logging, monitoring, robustness measures"},
    {"name": "Validation & Conformity", "description": "Testing, conformity assessment preparation, final review"},
]

# Criticality scores per article (higher = more critical to address first)
ARTICLE_CRITICALITY = {
    "5": 10,   # Prohibited — must remove immediately
    "13": 8,   # Transparency — quick win, low effort
    "12": 7,   # Record-keeping — foundational for audit
    "9": 6,    # Risk management — central requirement
    "10": 5,   # Data governance
    "14": 5,   # Human oversight
    "11": 4,   # Technical documentation
    "15": 4,   # Accuracy/robustness/cybersecurity
}


def generate_roadmap(
    gap_assessment: dict,
    target_date: str = DEADLINE_HIGH_RISK,
    project_name: str = "project",
) -> dict:
    """Generate a week-by-week compliance roadmap.

    Args:
        gap_assessment: Dict from compliance_check.assess_compliance().
        target_date: Deadline string (default: "2 August 2026").
        project_name: Human-readable project name.

    Returns:
        Roadmap dict with phases, weekly tasks, and metadata.
    """
    now = datetime.now(timezone.utc)

    # Parse target date
    try:
        deadline = datetime.strptime(target_date.strip(), "%d %B %Y").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            deadline = datetime.strptime(target_date.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            deadline = datetime(2026, 8, 2, tzinfo=timezone.utc)

    weeks_remaining = max(1, math.ceil((deadline - now).days / 7))

    # Build task list from gaps
    tasks = []
    articles = gap_assessment.get("articles", {})
    for art_num, art_data in articles.items():
        score = art_data.get("score", 100)
        if score >= 90:
            continue  # Already compliant enough

        effort_range = ARTICLE_EFFORT.get(art_num, (16, 32))
        avg_effort = (effort_range[0] + effort_range[1]) / 2
        criticality = ARTICLE_CRITICALITY.get(art_num, 3)

        # Action Priority Matrix: criticality × (1 / effort)
        priority_score = criticality * (1.0 / max(avg_effort, 1))

        # Phase assignment. Only Articles 5, 9-15 are expected from
        # assess_compliance(). Any other article defaults to Validation.
        if avg_effort <= 16:
            phase_idx = 0  # Quick wins
        elif art_num in ("9", "10", "11"):
            phase_idx = 1  # Documentation
        elif art_num in ("14", "15"):
            phase_idx = 2  # Technical implementation
        else:
            phase_idx = 3  # Validation

        # Generate specific action items from gaps
        gaps = art_data.get("gaps", [])
        action = gaps[0] if gaps else f"Address Article {art_num} compliance gap (score: {score}/100)"

        tasks.append({
            "article": art_num,
            "article_name": art_data.get("name", art_data.get("title", f"Article {art_num}")),
            "action": action,
            "effort_hours": effort_range,
            "effort_days": (effort_range[0] // 8, max(1, effort_range[1] // 8)),
            "priority_score": round(priority_score, 3),
            "phase": phase_idx,
            "current_score": score,
            "criticality": criticality,
        })

    # Sort by priority score (highest first)
    tasks.sort(key=lambda t: -t["priority_score"])

    # Assign to weeks based on phase and priority
    weekly_plan = []
    phase_week_ranges = _distribute_weeks(weeks_remaining, len(ROADMAP_PHASES))

    for phase_idx, phase in enumerate(ROADMAP_PHASES):
        phase_tasks = [t for t in tasks if t["phase"] == phase_idx]
        start_week, end_week = phase_week_ranges[phase_idx]

        for i, task in enumerate(phase_tasks):
            week = min(start_week + i, end_week)
            guidance = ARTICLE_FIX_GUIDANCE.get(task["article"], {})
            item = {
                "week": week,
                "phase": phase["name"],
                "article": task["article"],
                "article_name": task["article_name"],
                "action": task["action"],
                "effort_days": task["effort_days"],
                "priority": "critical" if task["criticality"] >= 8 else "high" if task["criticality"] >= 5 else "medium",
                "current_score": task["current_score"],
                "next_command": guidance.get("command", "regula check --project ."),
                "fix_description": guidance.get("description", f"Run regula check to review Article {task['article']} findings"),
            }
            weekly_plan.append(item)

    weekly_plan.sort(key=lambda w: w["week"])

    # Omnibus caveat
    omnibus_note = (
        "Note: The EU Digital Omnibus (not yet law) proposes extending "
        "Annex III high-risk deadlines to 2 December 2027. The roadmap "
        "uses the current legal baseline. Use --target-date to adjust."
    )

    return {
        "project": project_name,
        "generated_at": now.isoformat(),
        "target_date": deadline.strftime("%d %B %Y"),
        "weeks_remaining": weeks_remaining,
        "total_tasks": len(tasks),
        "omnibus_caveat": omnibus_note,
        "phases": [
            {
                "name": phase["name"],
                "description": phase["description"],
                "weeks": f"{phase_week_ranges[i][0]}-{phase_week_ranges[i][1]}",
                "task_count": len([t for t in tasks if t["phase"] == i]),
            }
            for i, phase in enumerate(ROADMAP_PHASES)
        ],
        "weekly_plan": weekly_plan,
        "methodology": "Action Priority Matrix (criticality x 1/effort)",
        "effort_disclaimer": "Effort estimates are heuristic ranges for a typical SME project. No authoritative per-article benchmarks exist.",
    }


def _distribute_weeks(total_weeks: int, num_phases: int) -> list:
    """Distribute weeks across phases proportionally."""
    # Phase weights: Quick wins 15%, Documentation 35%, Technical 35%, Validation 15%
    weights = [0.15, 0.35, 0.35, 0.15]
    ranges = []
    start = 1
    for i, w in enumerate(weights[:num_phases]):
        end = start + max(1, int(total_weeks * w)) - 1
        if i == num_phases - 1:
            end = total_weeks  # Last phase gets remaining weeks
        end = min(end, total_weeks)
        start = min(start, total_weeks)
        end = max(start, end)  # Never let start > end
        ranges.append((start, end))
        start = end + 1
    return ranges


def format_roadmap_text(roadmap: dict, actionable: bool = True) -> str:
    """Format roadmap as human-readable text.

    Args:
        roadmap: Roadmap dict from generate_roadmap().
        actionable: If True (default), show next_command after each task.
    """
    lines = []
    lines.append(f"\n  Compliance Roadmap — {roadmap['project']}")
    lines.append(f"  Target: {roadmap['target_date']} ({roadmap['weeks_remaining']} weeks remaining)")
    lines.append(f"  Tasks: {roadmap['total_tasks']}")
    lines.append("")

    # Phase overview
    lines.append("  Phases:")
    for phase in roadmap["phases"]:
        if phase["task_count"] > 0:
            lines.append(f"    {phase['name']} (weeks {phase['weeks']}): {phase['task_count']} task(s)")
            lines.append(f"      {phase['description']}")
    lines.append("")

    # Weekly plan
    lines.append("  Week-by-week plan:")
    current_phase = ""
    for item in roadmap["weekly_plan"]:
        if item["phase"] != current_phase:
            current_phase = item["phase"]
            lines.append(f"\n  -- {current_phase} --")
        effort = f"~{item['effort_days'][0]}-{item['effort_days'][1]}d"
        lines.append(f"    Week {item['week']:>2d}  [{item['priority']:>8s}]  Art. {item['article']:>2s}  {effort:>8s}  {item['action']}")
        if actionable and item.get("next_command"):
            lines.append(f"              \u2192 {item['next_command']}")
    lines.append("")

    # Omnibus caveat
    lines.append(f"  {roadmap['omnibus_caveat']}")
    lines.append(f"  Methodology: {roadmap['methodology']}")
    lines.append(f"  {roadmap['effort_disclaimer']}")
    lines.append("")
    return "\n".join(lines)
