# regula-ignore
#!/usr/bin/env python3
"""
Reproducible scan-time benchmark for `regula check`.

Shallow-clones a small set of public repositories, runs `regula check`
against each, and prints a markdown table with wall-clock time, file
count, and finding count. Designed to be re-runnable on any machine so
users can verify performance against their own hardware.

Usage:
    python3 scripts/scan_benchmarks.py                    # default repo list
    python3 scripts/scan_benchmarks.py --self             # benchmark this repo only
    python3 scripts/scan_benchmarks.py --repos <url> ...  # custom repo list
    python3 scripts/scan_benchmarks.py --json             # JSON output

Honesty notes:
- Wall-clock time depends on disk speed, CPU, and load. Always print
  the machine specs alongside the numbers.
- Each repo is shallow-cloned (`--depth 1`) at HEAD; commit SHA is
  recorded so the same revision can be benchmarked later.
- This script makes no precision/recall claims. It measures speed only.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from constants import VERSION

# Default benchmark targets — chosen for variety, not size.
# Small/medium Python and TypeScript repos that exercise the main pipeline.
DEFAULT_REPOS = [
    "https://github.com/psf/requests",
    "https://github.com/openai/openai-python",
    "https://github.com/encode/httpx",
]


def _git_head_sha(repo_dir: Path) -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip()[:12]
    except Exception:
        return "unknown"


def _count_scannable_files(repo_dir: Path) -> int:
    from constants import CODE_EXTENSIONS, SKIP_DIRS
    n = 0
    for p in repo_dir.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in CODE_EXTENSIONS:
            n += 1
    return n


def _machine_specs() -> dict:
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "processor": platform.processor() or platform.machine(),
        "regula": VERSION,
    }


def benchmark_path(label: str, path: Path, sha: str = "local") -> dict:
    """Run `regula check` against `path`, return timing + counts."""
    from report import scan_files

    file_count = _count_scannable_files(path)

    t0 = time.perf_counter()
    findings = scan_files(str(path))
    elapsed = time.perf_counter() - t0

    return {
        "target": label,
        "commit": sha,
        "files_scanned": file_count,
        "findings": len(findings),
        "wall_seconds": round(elapsed, 3),
        "files_per_second": round(file_count / elapsed, 1) if elapsed > 0 else 0,
    }


def benchmark_repo(url: str, workdir: Path) -> dict:
    """Shallow-clone `url` into `workdir`, then benchmark."""
    name = url.rstrip("/").split("/")[-1]
    target = workdir / name
    subprocess.check_call(
        ["git", "clone", "--depth", "1", "--quiet", "--", url, str(target)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    sha = _git_head_sha(target)
    result = benchmark_path(name, target, sha)
    result["url"] = url
    return result


def render_markdown(results: list[dict], specs: dict) -> str:
    lines = [
        "## Scan time benchmark",
        "",
        f"Regula `{specs['regula']}` · Python {specs['python']} · {specs['platform']}",
        "",
        "| Target | Commit | Files scanned | Findings | Wall time | Files/sec |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['target']} | `{r['commit']}` | {r['files_scanned']:,} | "
            f"{r['findings']:,} | {r['wall_seconds']:.2f}s | {r['files_per_second']:,} |"
        )
    lines.append("")
    lines.append(
        "_Numbers are from a single run on the machine above. Re-run "
        "`python3 scripts/scan_benchmarks.py` on your own hardware before "
        "citing them._"
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Benchmark regula check scan time.")
    ap.add_argument("--repos", nargs="*", default=None, help="Override repo list (URLs).")
    ap.add_argument("--self", action="store_true", help="Benchmark this repo only.")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of markdown.")
    args = ap.parse_args()

    specs = _machine_specs()
    results: list[dict] = []

    if args.self or (args.repos is None and not _git_available()):
        repo_root = Path(__file__).resolve().parent.parent
        sha = _git_head_sha(repo_root)
        results.append(benchmark_path("getregula (self)", repo_root, sha))
    else:
        repos = args.repos or DEFAULT_REPOS
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            for url in repos:
                try:
                    results.append(benchmark_repo(url, workdir))
                except subprocess.CalledProcessError as e:
                    print(f"WARN: failed to clone {url}: {e}", file=sys.stderr)
                except Exception as e:
                    print(f"WARN: failed to benchmark {url}: {e}", file=sys.stderr)

    if args.json:
        print(json.dumps({"specs": specs, "results": results}, indent=2))
    else:
        print(render_markdown(results, specs))
    return 0


def _git_available() -> bool:
    return shutil.which("git") is not None


def self_benchmark_dict() -> dict:
    """Programmatic entry point for tests/CI: benchmark this repo against itself.

    Returns a small dict with files_scanned, findings, and wall_seconds.
    Network-free (only scans the local checkout).
    """
    repo_root = Path(__file__).resolve().parent.parent
    sha = _git_head_sha(repo_root)
    return benchmark_path("getregula (self)", repo_root, sha)


if __name__ == "__main__":
    sys.exit(main())
