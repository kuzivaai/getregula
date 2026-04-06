#!/usr/bin/env python3
# regula-ignore
"""
Regula Remediation Plan Generator

Takes scan findings and compliance gap data and produces a prioritised,
article-by-article action plan with concrete tasks, effort estimates,
and legal deadlines.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from remediation import CATEGORY_REMEDIATIONS


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TIER_PRIORITY = {
    "prohibited": 0,
    "high_risk": 1,
    "limited_risk": 2,
    "minimal_risk": 3,
}

PRIORITY_LABELS = {
    "prohibited": "PROHIBITED",
    "high_risk": "HIGH",
    "limited_risk": "MEDIUM",
    "minimal_risk": "LOW",
}

# Rough effort estimates per article (hours range).
# These are heuristic ranges for a typical SME project — no authoritative
# source exists. Presented to users with ~ prefix to signal imprecision.
ARTICLE_EFFORT = {
    "5": (2, 8),      # Remove prohibited functionality
    "9": (40, 60),     # Risk management system
    "10": (24, 40),    # Data governance
    "11": (16, 32),    # Technical documentation (Regula helps here)
    "12": (8, 16),     # Record-keeping / logging
    "13": (8, 16),     # Transparency
    "14": (16, 24),    # Human oversight
    "15": (16, 32),    # Accuracy, robustness, cybersecurity
}

DEADLINE_HIGH_RISK = "2 August 2026"
DEADLINE_OMNIBUS = "2 December 2027 (if Digital Omnibus enacted)"


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------

def generate_plan(
    findings: list,
    gap_assessment: dict,
    project_name: str = "project",
) -> dict:
    """Generate a prioritised remediation plan.

    Args:
        findings: List of finding dicts from report.scan_files().
        gap_assessment: Dict from compliance_check.assess_compliance().
        project_name: Human-readable project name.

    Returns:
        Plan dict with metadata and ordered task list.
    """
    tasks = []
    task_counter = 1

    # --- Phase 1: Tasks from prohibited/high-risk findings ---
    finding_tasks = _tasks_from_findings(findings, task_counter)
    tasks.extend(finding_tasks)
    task_counter += len(finding_tasks)

    # --- Phase 2: Tasks from compliance gaps ---
    articles = gap_assessment.get("articles", {})
    gap_tasks = _tasks_from_gaps(articles, task_counter)
    tasks.extend(gap_tasks)
    task_counter += len(gap_tasks)

    # --- Sort by priority, then effort ---
    tasks.sort(key=lambda t: (
        TIER_PRIORITY.get(t.get("_sort_tier", "minimal_risk"), 99),
        t.get("effort_hours", (0, 0))[0],
    ))

    # Re-assign sequential IDs after sort
    for i, task in enumerate(tasks, 1):
        task["id"] = f"TASK-{i:03d}"
        task.pop("_sort_tier", None)

    return {
        "project": project_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tasks": len(tasks),
        "tasks": tasks,
    }


def _tasks_from_findings(findings: list, start_id: int) -> list:
    """Create tasks for each unique finding that needs action."""
    tasks = []
    seen_categories = set()

    for finding in findings:
        tier = finding.get("tier", "minimal_risk")
        if tier not in ("prohibited", "high_risk"):
            continue

        category = finding.get("category", "unknown")
        if category in seen_categories:
            continue
        seen_categories.add(category)

        remediation = CATEGORY_REMEDIATIONS.get(category, {})
        summary = remediation.get("summary", f"Address {category} finding")
        explanation = remediation.get("explanation", "")

        articles = finding.get("articles", [])
        article_nums = []
        for a in articles:
            num = a.replace("Article ", "").strip()
            if num.isdigit():
                article_nums.append(num)

        task = {
            "id": f"TASK-{start_id + len(tasks):03d}",
            "priority": PRIORITY_LABELS.get(tier, "LOW"),
            "task_type": "finding",
            "article": ", ".join(article_nums) if article_nums else "—",
            "title": summary,
            "action": explanation or summary,
            "files": [f"{finding.get('file', '?')}:{finding.get('line', '?')}"],
            "effort_hours": ARTICLE_EFFORT.get(
                article_nums[0] if article_nums else "9", (8, 16)
            ),
            "deadline": finding.get("deadline_note") or DEADLINE_HIGH_RISK,
            "status": "not_started",
            "_sort_tier": tier,
        }
        tasks.append(task)

    return tasks


def _tasks_from_gaps(articles: dict, start_id: int) -> list:
    """Create tasks for each compliance gap (articles scoring < 80)."""
    tasks = []

    for article_num, data in articles.items():
        score = data.get("score", 0)
        if score >= 80:  # Strong evidence — no task needed
            continue

        gaps = data.get("gaps", [])
        if not gaps:
            continue

        title = data.get("title", f"Article {article_num}")
        effort = ARTICLE_EFFORT.get(article_num, (8, 16))

        # Scale effort down if partial progress exists
        if score >= 50:
            effort = (effort[0] // 2, effort[1] // 2)
        elif score >= 30:
            effort = (int(effort[0] * 0.7), int(effort[1] * 0.7))

        action_lines = [f"Address compliance gaps for Article {article_num} ({title}):"]
        for gap in gaps:
            action_lines.append(f"  - {gap}")

        task = {
            "id": f"TASK-{start_id + len(tasks):03d}",
            "priority": "HIGH",
            "task_type": "gap",
            "article": article_num,
            "title": f"Article {article_num} — {title}",
            "action": "\n".join(action_lines),
            "files": [],
            "effort_hours": effort,
            "deadline": DEADLINE_HIGH_RISK,
            "status": "not_started",
            "_sort_tier": "high_risk",
        }
        tasks.append(task)

    return tasks


# ---------------------------------------------------------------------------
# Status tracking
# ---------------------------------------------------------------------------

PLAN_STATUS_FILE = ".regula/plan-status.json"


def load_plan_status(project_path: str) -> dict:
    """Load saved plan status from .regula/plan-status.json."""
    status_path = Path(project_path) / PLAN_STATUS_FILE
    if not status_path.exists():
        return {}
    try:
        return json.loads(status_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_plan_status(project_path: str, status: dict) -> None:
    """Save plan status to .regula/plan-status.json."""
    status_path = Path(project_path) / PLAN_STATUS_FILE
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(
        json.dumps(status, indent=2, default=str), encoding="utf-8"
    )


def mark_task_done(project_path: str, task_id: str) -> dict:
    """Mark a task as completed in the status file."""
    status = load_plan_status(project_path)
    status[task_id] = {
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    save_plan_status(project_path, status)
    return status


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_plan_text(plan: dict) -> str:
    """Format plan as human-readable markdown."""
    lines = []
    lines.append(f"# Remediation Plan — {plan['project']}")
    lines.append(f"Generated: {plan['generated_at']}")
    lines.append(f"Tasks: {plan['total_tasks']}")
    lines.append("")

    current_priority = None
    for task in plan["tasks"]:
        if task["priority"] != current_priority:
            current_priority = task["priority"]
            lines.append(f"## Priority: {current_priority}")
            lines.append("")

        effort = task["effort_hours"]
        effort_str = f"~{effort[0]}-{effort[1]}h" if isinstance(effort, (list, tuple)) else f"~{effort}h"

        lines.append(f"{task['id']} [{task['priority']}] {task['title']}")
        lines.append(f"  Article: {task['article']}")
        if task.get("files"):
            lines.append(f"  Files: {', '.join(task['files'])}")
        lines.append(f"  Action: {task['action'].split(chr(10))[0]}")
        if "\n" in task.get("action", ""):
            for extra_line in task["action"].split("\n")[1:]:
                lines.append(f"          {extra_line}")
        lines.append(f"  Effort: {effort_str}")
        lines.append(f"  Deadline: {task['deadline']}")
        lines.append(f"  Status: [ ] {task['status'].replace('_', ' ').title()}")
        lines.append("")

    total_low = sum(t["effort_hours"][0] for t in plan["tasks"] if isinstance(t["effort_hours"], (list, tuple)))
    total_high = sum(t["effort_hours"][1] for t in plan["tasks"] if isinstance(t["effort_hours"], (list, tuple)))
    if total_low or total_high:
        lines.append("---")
        lines.append(f"Total estimated effort: ~{total_low}-{total_high} hours")
        lines.append(f"Deadline: {DEADLINE_HIGH_RISK}")

    return "\n".join(lines)


def format_plan_status(plan: dict, status: dict) -> str:
    """Format plan with completion status overlay."""
    completed = sum(1 for t in plan["tasks"] if status.get(t["id"], {}).get("status") == "completed")
    total = plan["total_tasks"]
    pct = int(completed / total * 100) if total > 0 else 0

    lines = [
        f"Remediation Plan Status — {plan['project']}",
        f"Progress: {completed}/{total} tasks ({pct}%)",
        "",
    ]

    for task in plan["tasks"]:
        task_status = status.get(task["id"], {})
        is_done = task_status.get("status") == "completed"
        mark = "[x]" if is_done else "[ ]"
        done_at = f" (completed {task_status['completed_at'][:10]})" if is_done else ""
        lines.append(f"  {mark} {task['id']} [{task['priority']}] {task['title']}{done_at}")

    return "\n".join(lines)
