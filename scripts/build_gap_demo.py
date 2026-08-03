#!/usr/bin/env python3
# regula-ignore
"""Produce the landing page's terminal demo from real command output.

CLASS 1. `site/index.html` showed a `regula gap .` block behind a `$`
prompt, with per-article percentages 20/40/60/80/0/30/50 and a headline
"Overall compliance score: 42/100" in the adjacent `regula comply` panel.
No scan produced any of those numbers. A visitor reads a `$` prompt as real
output; that is what makes it a claim rather than a mock-up.

This script is the only writer of `data/gap_demo.json`. It runs both
commands against a tracked-only snapshot of a COMMITTED fixture and records
what they actually print.
`tests/test_gap_demo.py` re-runs them and fails on any disagreement, and
also fails if the site shows a percentage the artefact does not contain.

WHY THIS FIXTURE
----------------
`tests/fixtures/sample_high_risk` is tracked. The criterion was fixed
before any score was looked at: the target must be committed and must be
scanned as the page depicts it, with no flags.

Choosing a tracked target is not sufficient when ignored content can sit
inside its directory. The builder therefore asks Git for the fixture's
tracked files, copies only those files to a temporary snapshot, and runs both
commands there. Git failure, an empty tracked population, a copy failure, or
a command/build failure is fatal. Local ignored state is never an input.

Two candidates were rejected for reasons independent of their scores:

- `regula gap .` on the Regula repository itself scores 100%, and that
  number is computed partly over `conformity-evidence-project-*`
  directories which are untracked and gitignored. No clone reproduces it.
  Measurement rule 4b: untracked files are not surfaces.
- A purpose-built fixture would be the shop window chosen by its author,
  which is the metric gaming PROGRAMME.md principle 3 forbids.

The tracked fixture scores 6% in both this working tree and a clean clone.
That unflattering result is not why it was chosen and is not a reason to
change it.

WHAT THE REAL OUTPUT CHANGES ON THE PAGE
----------------------------------------
1. The numbers get worse: 20/40/60/80/0/30/50 becomes 0/0/0/0/0/45/0/0,
   and 42/100 becomes 6/100.
2. The real command emits a NOTE the mock-up omitted entirely, saying the
   score measures presence of documentation and cannot offset scan
   findings. That NOTE is the denominator disclosure, and its absence was
   the actual defect.
3. The real output has 8 articles, not 7: it includes Article 17.
4. `regula comply` without `--all` prints no article table at all on this
   fixture, because the project classifies as not_ai. The site's comply
   panel was not a stale rendering of a real command; it depicted output
   the command does not produce. The panel now shows `--all`, which is the
   documented flag for exactly this case, and says so.

Usage:
    python3 scripts/build_gap_demo.py           # write the artefact
    python3 scripts/build_gap_demo.py --check   # compare, do not write

Stdlib only.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

# Self-protection for the bare sibling import in __main__ (tree_guard), per
# .claude/rules/python-scripts.md: without it the module imports only when a
# caller happens to have seeded sys.path first.
sys.path.insert(0, str(Path(__file__).parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = "tests/fixtures/sample_high_risk"
ARTEFACT = REPO_ROOT / "data/gap_demo.json"

# "Article 9   Risk Management   [  0%] NOT FOUND"  (gap)
GAP_ROW = re.compile(
    r"^Article\s+(\d+)\s+(.+?)\s+\[\s*(\d+)%\]\s+(.+?)\s*$", re.MULTILINE)
# "  [x] Article 9   Risk Management     0% NOT FOUND"  (comply --all)
COMPLY_ROW = re.compile(
    r"^\s*\[.\]\s+Article\s+(\d+)\s+(.+?)\s+(\d+)%\s+(.+?)\s*$", re.MULTILINE)
GAP_SCORE = re.compile(r"^Overall score:\s+(\d+)%", re.MULTILINE)
COMPLY_SCORE = re.compile(r"Overall compliance score:\s+(\d+)/100")
NOTE_BLOCK = re.compile(
    r"^\s*NOTE: This score measures.*?questions\.$",
    re.MULTILINE | re.DOTALL)


def _run(args: list[str]) -> str:
    proc = subprocess.run([sys.executable, *args], cwd=str(REPO_ROOT),
                          capture_output=True, text=True, timeout=1800)
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"{args} failed rc={proc.returncode}: "
                           f"{proc.stderr[:400]}")
    if not proc.stdout.strip():
        raise RuntimeError(f"{args} produced no output")
    return proc.stdout


@contextmanager
def _tracked_fixture_snapshot():
    """Yield a directory containing exactly Git's tracked fixture files."""
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--", FIXTURE],
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "Git could not derive the gap-demo inputs: "
            + proc.stderr.decode("utf-8", errors="replace")[:400]
        )
    paths = [Path(raw.decode("utf-8")) for raw in proc.stdout.split(b"\0") if raw]
    if not paths:
        raise RuntimeError(f"Git reported no tracked files under {FIXTURE}")

    with tempfile.TemporaryDirectory(prefix="regula-gap-demo-") as tmp:
        snapshot = Path(tmp) / Path(FIXTURE).name
        for relative in paths:
            try:
                within_fixture = relative.relative_to(FIXTURE)
            except ValueError as exc:
                raise RuntimeError(
                    f"Git returned an input outside {FIXTURE}: {relative}"
                ) from exc
            source = REPO_ROOT / relative
            destination = snapshot / within_fixture
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        yield snapshot


def _rows(pattern: re.Pattern[str], text: str) -> list[dict]:
    return [{"article": m.group(1), "title": m.group(2).strip(),
             "percent": int(m.group(3)), "status": m.group(4).strip()}
            for m in pattern.finditer(text)]


def build() -> dict:
    with _tracked_fixture_snapshot() as snapshot:
        gap_out = _run(["-m", "scripts.cli", "gap", str(snapshot)])
        comply_out = _run(
            ["-m", "scripts.cli", "comply", str(snapshot), "--all"]
        )

    note = NOTE_BLOCK.search(gap_out)
    gap_rows = _rows(GAP_ROW, gap_out)
    comply_rows = _rows(COMPLY_ROW, comply_out)
    gap_score = GAP_SCORE.search(gap_out)
    comply_score = COMPLY_SCORE.search(comply_out)

    for name, value in (("gap rows", gap_rows), ("comply rows", comply_rows),
                        ("gap score", gap_score),
                        ("comply score", comply_score), ("NOTE", note)):
        if not value:
            raise RuntimeError(
                f"could not parse {name} from real output. The commands "
                f"changed shape; fix this parser rather than the site.")

    return {
        "_what_this_is": (
            "The landing page's terminal demo, parsed from real command "
            "output against a committed fixture. Produced by "
            "scripts/build_gap_demo.py. Never hand-edited: "
            "tests/test_gap_demo.py re-runs both commands and fails on "
            "disagreement, and fails if the site shows a percentage this "
            "file does not contain."),
        "_why_it_exists": (
            "The block it replaces was invented output shown behind a $ "
            "prompt. A visitor reads that as a real scan."),
        "fixture": FIXTURE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gap": {
            "command": "regula gap " + FIXTURE,
            "overall_percent": int(gap_score.group(1)),
            "note": " ".join(note.group(0).split()),
            "rows": gap_rows,
        },
        "comply": {
            "command": "regula comply " + FIXTURE + " --all",
            "overall_score": int(comply_score.group(1)),
            "rows": comply_rows,
        },
    }


def _comparable(doc: dict) -> str:
    return json.dumps({k: v for k, v in doc.items() if k != "generated_at"},
                      indent=2, sort_keys=True)


def main(argv: list[str]) -> int:
    fresh = build()
    if "--check" in argv:
        if not ARTEFACT.exists():
            print(f"MISSING: {ARTEFACT.relative_to(REPO_ROOT)}",
                  file=sys.stderr)
            return 1
        committed = json.loads(ARTEFACT.read_text(encoding="utf-8"))
        if _comparable(committed) != _comparable(fresh):
            print("data/gap_demo.json disagrees with a fresh run. Re-run "
                  "scripts/build_gap_demo.py and update the site blocks it "
                  "feeds.", file=sys.stderr)
            return 1
        print("data/gap_demo.json matches a fresh run.")
        return 0

    ARTEFACT.write_text(json.dumps(fresh, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"wrote {ARTEFACT.relative_to(REPO_ROOT)}")
    print(f"  gap    overall {fresh['gap']['overall_percent']}%  "
          f"{len(fresh['gap']['rows'])} article rows")
    print(f"  comply overall {fresh['comply']['overall_score']}/100  "
          f"{len(fresh['comply']['rows'])} article rows")
    return 0


if __name__ == "__main__":
    from tree_guard import stamp
    stamp()
    raise SystemExit(main(sys.argv[1:]))
