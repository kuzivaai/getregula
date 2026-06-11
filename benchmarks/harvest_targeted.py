#!/usr/bin/env python3
# regula-ignore
"""Targeted high-risk corpus harvester.

Clones repos from a manifest, scans with Regula, and extracts candidate
findings with surrounding code context for human labelling.

Usage:
    python3 benchmarks/harvest_targeted.py --manifest benchmarks/targeted_manifest.json
    python3 benchmarks/harvest_targeted.py --manifest benchmarks/targeted_manifest.json --output benchmarks/targeted_corpus/

Output: one JSON file per repo in the output directory, plus a combined
candidates.json for labelling. No suggested labels anywhere — raters judge blind.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from constants import VERSION


def clone_repo(url: str, commit: str, dest: Path) -> bool:
    """Shallow clone a repo at a pinned commit."""
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", url, str(dest)],
            capture_output=True, text=True, check=True, timeout=120,
        )
        if commit and commit != "HEAD":
            subprocess.run(
                ["git", "checkout", commit],
                cwd=dest, capture_output=True, text=True, check=True,
            )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"  WARN: clone failed for {url}: {e}", file=sys.stderr)
        return False


def scan_repo(repo_path: Path, domain: str | None = None) -> list[dict]:
    """Run regula check on a cloned repo and return findings."""
    cmd = [sys.executable, "-m", "scripts.cli", "check", str(repo_path),
           "--format", "json", "--skip-tests"]
    if domain:
        cmd.extend(["--domain", domain])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300,
            cwd=REPO_ROOT,
        )
        data = json.loads(result.stdout)
        return data.get("data", {}).get("findings", [])
    except (json.JSONDecodeError, subprocess.TimeoutExpired, KeyError) as e:
        print(f"  WARN: scan failed: {e}", file=sys.stderr)
        return []


def extract_context(repo_path: Path, filepath: str, line: int,
                    context_lines: int = 10) -> str:
    """Extract code context around a finding for blind labelling."""
    full_path = repo_path / filepath
    if not full_path.exists():
        return "[file not found]"
    try:
        lines = full_path.read_text(encoding="utf-8", errors="replace").splitlines()
        start = max(0, line - context_lines - 1)
        end = min(len(lines), line + context_lines)
        numbered = []
        for i in range(start, end):
            marker = " >> " if i == line - 1 else "    "
            numbered.append(f"{i+1:4d}{marker}{lines[i]}")
        return "\n".join(numbered)
    except Exception:
        return "[could not read file]"


def harvest(manifest_path: Path, output_dir: Path) -> dict:
    """Main harvest: clone, scan, extract candidates."""
    manifest = json.load(manifest_path.open())
    output_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "harvested_at": datetime.now(timezone.utc).isoformat(),
        "regula_version": VERSION,
        "manifest": str(manifest_path),
        "scan_config": {
            "skip_tests": True,
            "domain_gating": "per-repo (domain field in manifest)",
        },
    }

    all_candidates = []
    repo_stats = []

    for entry in manifest.get("repos", []):
        url = entry["url"]
        commit = entry.get("commit", "HEAD")
        domain = entry.get("domain")
        repo_name = entry.get("name", url.split("/")[-1])
        licence = entry.get("licence", "unknown")
        annex_iii_category = entry.get("annex_iii_category", "unspecified")

        print(f"Processing {repo_name} ({annex_iii_category})...")

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / repo_name
            if not clone_repo(url, commit, repo_path):
                repo_stats.append({
                    "name": repo_name, "status": "clone_failed",
                    "findings": 0, "high_risk": 0,
                })
                continue

            findings = scan_repo(repo_path, domain=domain)

            # Filter to high_risk tier only
            hr_findings = [f for f in findings
                           if f.get("tier") in ("high_risk", "prohibited")]

            candidates = []
            for i, f in enumerate(hr_findings):
                context = extract_context(
                    repo_path, f.get("file", ""), f.get("line", 0)
                )
                candidate = {
                    "id": f"T-{repo_name}-{i+1:03d}",
                    "repo": repo_name,
                    "repo_url": url,
                    "commit": commit,
                    "file": f.get("file", ""),
                    "line": f.get("line", 0),
                    "tier": f.get("tier", ""),
                    "category": f.get("category", ""),
                    "confidence_score": f.get("confidence_score", 0),
                    "description": f.get("description", ""),
                    "pattern_name": f.get("pattern_name", ""),
                    "code_context": context,
                    "annex_iii_domain": annex_iii_category,
                    "licence": licence,
                    # NO suggested label — raters judge blind
                }
                candidates.append(candidate)

            all_candidates.extend(candidates)

            # Save per-repo results
            repo_output = {
                "repo": repo_name,
                "url": url,
                "commit": commit,
                "domain": domain,
                "annex_iii_category": annex_iii_category,
                "licence": licence,
                "total_findings": len(findings),
                "high_risk_findings": len(hr_findings),
                "candidates": candidates,
            }
            (output_dir / f"{repo_name}.json").write_text(
                json.dumps(repo_output, indent=2, ensure_ascii=False)
            )

            repo_stats.append({
                "name": repo_name,
                "status": "ok",
                "total_findings": len(findings),
                "high_risk": len(hr_findings),
            })

            print(f"  {len(findings)} total findings, "
                  f"{len(hr_findings)} high_risk candidates")

    # Save combined candidates for labelling
    output = {
        **meta,
        "corpus": "targeted_high_risk",
        "total_repos": len(manifest.get("repos", [])),
        "total_candidates": len(all_candidates),
        "repo_stats": repo_stats,
        "candidates": all_candidates,
    }
    candidates_path = output_dir / "candidates.json"
    candidates_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False)
    )

    print(f"\n{'='*60}")
    print(f"Harvest complete: {len(all_candidates)} candidates "
          f"from {len(repo_stats)} repos")
    print(f"Output: {candidates_path}")
    print(f"{'='*60}")

    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--manifest", type=Path, required=True,
                        help="Path to targeted_manifest.json")
    parser.add_argument("--output", type=Path,
                        default=Path("benchmarks/targeted_corpus"),
                        help="Output directory for candidates")
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"Manifest not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    harvest(args.manifest, args.output)


if __name__ == "__main__":
    main()
