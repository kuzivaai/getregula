#!/usr/bin/env python3
# regula-ignore
"""Re-scan the random corpus with the current Regula code.

Clones each repo (shallow, depth=1), scans with current Regula,
saves results to benchmarks/results/random_corpus_v2/.

Usage:
    python3 benchmarks/rescan_corpus.py
    python3 benchmarks/rescan_corpus.py --workers 4
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

METHODOLOGY = ROOT / "benchmarks" / "results" / "random_corpus" / "METHODOLOGY.json"
OUTPUT_DIR = ROOT / "benchmarks" / "results" / "random_corpus_v2"


def clone_and_scan(repo_slug):
    """Clone a repo and scan it. Returns (slug, findings, error)."""
    url = f"https://github.com/{repo_slug}.git"
    safe_name = repo_slug.replace("/", "__")
    tmpdir = tempfile.mkdtemp(prefix=f"regula_bench_{safe_name}_")
    try:
        # Shallow clone
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "--single-branch", url, tmpdir],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            return repo_slug, None, f"clone failed: {r.stderr[:200]}"

        # Scan with current Regula
        from report import scan_files
        findings = scan_files(tmpdir)

        # Convert to serialisable format
        clean_findings = []
        for f in findings:
            cf = dict(f)
            # Remove non-serialisable items
            for key in list(cf.keys()):
                if cf[key] is None:
                    cf[key] = None
                elif isinstance(cf[key], set):
                    cf[key] = sorted(cf[key])
            clean_findings.append(cf)

        return repo_slug, clean_findings, None
    except subprocess.TimeoutExpired:
        return repo_slug, None, "clone timed out (120s)"
    except Exception as e:
        return repo_slug, None, str(e)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Re-scan random corpus")
    parser.add_argument("--workers", type=int, default=3, help="Parallel workers")
    args = parser.parse_args()

    # Load repo list
    method = json.loads(METHODOLOGY.read_text())
    repos = method["selection_repos"]
    print(f"Re-scanning {len(repos)} repos with {args.workers} workers...\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results_summary = {}
    total_findings = 0
    errors = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(clone_and_scan, repo): repo for repo in repos}
        for i, future in enumerate(as_completed(futures), 1):
            repo = futures[future]
            slug, findings, error = future.result()
            safe_name = slug.replace("/", "__")

            if error:
                print(f"  [{i}/{len(repos)}] FAIL  {slug}: {error}")
                errors += 1
                results_summary[slug] = {"error": error, "findings_count": 0}
            else:
                count = len(findings)
                total_findings += count
                print(f"  [{i}/{len(repos)}] OK    {slug}: {count} findings")

                # Save per-repo results
                out_path = OUTPUT_DIR / f"{safe_name}.json"
                out_path.write_text(json.dumps(findings, indent=2, default=str))
                results_summary[slug] = {"findings_count": count, "error": None}

    elapsed = time.time() - start

    # Save summary
    summary = {
        "date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
        "regula_version": None,
        "repos_scanned": len(repos) - errors,
        "repos_failed": errors,
        "total_findings": total_findings,
        "elapsed_seconds": round(elapsed, 1),
        "per_repo": results_summary,
    }
    try:
        from constants import VERSION
        summary["regula_version"] = VERSION
    except ImportError:
        pass

    (OUTPUT_DIR / "SUMMARY.json").write_text(json.dumps(summary, indent=2))

    print(f"\nDone: {len(repos) - errors}/{len(repos)} repos scanned, "
          f"{total_findings} findings, {elapsed:.0f}s")
    print(f"Results: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
