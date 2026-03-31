#!/usr/bin/env python3
"""Benchmark Regula against real OSS AI projects."""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

PROJECTS = [
    {"name": "instructor", "repo": "https://github.com/jxnl/instructor.git"},
    {"name": "pydantic-ai", "repo": "https://github.com/pydantic/pydantic-ai.git"},
    {"name": "langchain", "repo": "https://github.com/langchain-ai/langchain.git"},
    {"name": "scikit-learn", "repo": "https://github.com/scikit-learn/scikit-learn.git"},
    {"name": "openai-python", "repo": "https://github.com/openai/openai-python.git"},
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


def main():
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    summary = {}
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for project in PROJECTS:
            name = project["name"]
            print(f"\n{'='*60}")
            print(f"Benchmarking: {name}")
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

            # Save for labelling
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
