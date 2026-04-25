#!/usr/bin/env python3
"""Benchmark Regula against real OSS AI projects.

Two corpora:
  - LIBRARY_PROJECTS: AI libraries/frameworks (existing baseline)
  - APP_PROJECTS: Real-world AI applications across EU AI Act risk categories

Usage:
    python3 benchmarks/run_benchmark.py                # scan all
    python3 benchmarks/run_benchmark.py --corpus lib    # libraries only
    python3 benchmarks/run_benchmark.py --corpus app    # applications only
"""
import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# ── Library corpus (AI frameworks/SDKs) ─────────────────────────────
LIBRARY_PROJECTS = [
    {"name": "instructor", "repo": "https://github.com/jxnl/instructor.git"},
    {"name": "pydantic-ai", "repo": "https://github.com/pydantic/pydantic-ai.git"},
    {"name": "langchain", "repo": "https://github.com/langchain-ai/langchain.git"},
    {"name": "scikit-learn", "repo": "https://github.com/scikit-learn/scikit-learn.git"},
    {"name": "openai-python", "repo": "https://github.com/openai/openai-python.git"},
]

# ── Application corpus (real-world AI apps by EU AI Act risk category) ──
APP_PROJECTS = [
    # Existing app scans
    {"name": "app_aider", "repo": "https://github.com/Aider-AI/aider.git",
     "category": "Agent Autonomy — AI coding assistant"},
    {"name": "app_crewai", "repo": "https://github.com/crewAIInc/crewAI.git",
     "category": "Agent Autonomy — multi-agent framework"},
    {"name": "app_openadapt", "repo": "https://github.com/OpenAdaptAI/OpenAdapt.git",
     "category": "Agent Autonomy — RPA/process automation"},
    {"name": "app_privategpt", "repo": "https://github.com/zylon-ai/private-gpt.git",
     "category": "Limited Risk — RAG/document QA"},
    {"name": "app_quivr", "repo": "https://github.com/QuivrHQ/quivr.git",
     "category": "Limited Risk — knowledge management"},
    # Hiring/HR — Annex III 6(a)
    {"name": "app_resume_matcher", "repo": "https://github.com/srbhr/Resume-Matcher.git",
     "category": "Annex III 6(a) — recruitment/candidate ranking"},
    # Healthcare — Annex III 5(c)
    {"name": "app_monai", "repo": "https://github.com/Project-MONAI/MONAI.git",
     "category": "Annex III 5(c) — medical imaging/diagnosis"},
    # Biometrics — Article 5 / Annex III
    {"name": "app_deepface", "repo": "https://github.com/serengil/deepface.git",
     "category": "Article 5 / Annex III — facial recognition, emotion detection"},
    # Chatbot — Article 50 transparency
    {"name": "app_rasa", "repo": "https://github.com/RasaHQ/rasa.git",
     "category": "Article 50 — conversational AI/chatbot"},
    # Computer vision in production — surveillance/detection
    {"name": "app_frigate", "repo": "https://github.com/blakeblackshear/frigate.git",
     "category": "Annex III — real-time CV object detection/surveillance"},
    # Credit scoring — Annex III 5(b)
    {"name": "app_toad", "repo": "https://github.com/amphibian-dev/toad.git",
     "category": "Annex III 5(b) — credit scorecard development"},
    # Education/proctoring — Annex III 3(a)
    {"name": "app_proctoring", "repo": "https://github.com/vardanagarwal/Proctoring-AI.git",
     "category": "Annex III 3(a) — automated exam proctoring"},
]


def clone_project(project, base_dir):
    dest = base_dir / project["name"]
    if dest.exists():
        return dest
    subprocess.run(
        ["git", "clone", "--depth=1", project["repo"], str(dest)],
        capture_output=True, timeout=120,
    )
    return dest


def scan_project(project_path):
    from report import scan_files
    return scan_files(str(project_path))


def _run_projects(projects, output_dir, tmp_path):
    """Scan a list of projects, return summary dict."""
    summary = {}
    for project in projects:
        name = project["name"]
        category = project.get("category", "")
        cat_label = f" ({category})" if category else ""
        print(f"\n{'='*60}")
        print(f"Benchmarking: {name}{cat_label}")
        print(f"{'='*60}")

        start = time.time()
        try:
            project_path = clone_project(project, tmp_path)
            clone_time = time.time() - start
        except subprocess.TimeoutExpired:
            print(f"  SKIPPED: clone timed out after 120s")
            summary[name] = {"skipped": True, "reason": "clone timeout"}
            continue

        start = time.time()
        findings = scan_project(str(project_path))
        scan_time = time.time() - start

        active = [f for f in findings if not f.get("suppressed")]

        by_tier = {}
        for f in active:
            tier = f.get("tier", "unknown")
            by_tier.setdefault(tier, []).append(f)

        print(f"  Clone: {clone_time:.1f}s | Scan: {scan_time:.1f}s")
        print(f"  Total findings: {len(active)}")
        for tier, items in sorted(by_tier.items()):
            print(f"    {tier}: {len(items)}")

        output_file = output_dir / f"{name}.json"
        output_file.write_text(
            json.dumps(active, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"  Saved: {output_file}")

        summary[name] = {
            "total_findings": len(active),
            "by_tier": {t: len(items) for t, items in by_tier.items()},
            "scan_seconds": round(scan_time, 1),
        }
        if category:
            summary[name]["category"] = category

    return summary


def main():
    parser = argparse.ArgumentParser(description="Benchmark Regula against OSS projects")
    parser.add_argument("--corpus", choices=["lib", "app", "all"], default="all",
                        help="Which corpus to scan (default: all)")
    args = parser.parse_args()

    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    projects = []
    if args.corpus in ("lib", "all"):
        projects.extend(LIBRARY_PROJECTS)
    if args.corpus in ("app", "all"):
        projects.extend(APP_PROJECTS)

    summary = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        summary = _run_projects(projects, output_dir, tmp_path)

    # Write summary
    summary_file = output_dir / "SUMMARY.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"Summary saved: {summary_file}")
    for name, data in summary.items():
        if data.get("skipped"):
            print(f"  {name}: SKIPPED ({data['reason']})")
        else:
            print(f"  {name}: {data['total_findings']} findings ({data['scan_seconds']}s)")


if __name__ == "__main__":
    main()
