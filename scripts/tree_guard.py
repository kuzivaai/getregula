#!/usr/bin/env python3
"""Working-tree drift detection between a recorded baseline and now.

Why this exists. On 30 July 2026 twelve tracked files changed in this
working tree with no session record in this repository: a session running
from a different project context wrote them (attributed afterwards from its
transcript, `docs/improvement/LEDGER.md`). Every figure this programme
publishes is measured from this tree, so an unattributed mutation between
two measurements silently changes what the numbers describe. This module
makes that drift detectable at the moment a measurement runs instead of
whenever a cache-staleness refusal happens to fire.

What it can and cannot do. It detects THAT the tree changed between a
recorded baseline and a check, and names every path. It cannot say WHO
changed it; actor attribution needs an OS-level watcher and belongs to the
session harness, not to this repository.

Usage:
    python3 scripts/tree_guard.py --record [--note TEXT]   # session start
    python3 scripts/tree_guard.py --check                  # exit 3 on drift
    python3 scripts/tree_guard.py --status                 # human summary

Measurement scripts call `stamp()` from their CLI entry points: it prints
one stderr line naming any drift since the recorded baseline, and never
alters the host command's behaviour or exit code. It is silent when no
baseline has been recorded, so test environments and fresh clones are
unaffected. Set REGULA_TREE_GUARD=0 to silence it entirely.

The baseline lives at .claude/tree-state.json, which is gitignored
(.gitignore line 43, `.claude/*`): recording state must not itself change
the tree being measured.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = REPO_ROOT / ".claude" / "tree-state.json"


def _git(args, cwd=None):
    """Run git and return stdout; raise on failure so drift in the apparatus
    is loud rather than absorbed into a wrong answer."""
    result = subprocess.run(
        ["git", *args], cwd=str(cwd or REPO_ROOT),
        capture_output=True, text=True, check=True,
    )
    return result.stdout


# An ignored directory with at most this many files is hashed file by file;
# above it, only presence and file count are recorded. This is a stated
# budget, not a hand-maintained path list: it makes a one-file .regula/
# registry fully checkable while a many-thousand-file .venv/ costs one
# count. The motivating instance is recorded in docs/improvement/LEDGER.md:
# a gitignored .regula/ inside a tracked fixture changed the published
# gap-demo figures, invisibly to a plain-porcelain guard.
IGNORED_DIR_HASH_BUDGET = 200


def snapshot(root=None):
    """Return the current tree state: HEAD, HEAD's tree, and a content hash
    for every path git sees as modified, added, deleted, untracked, or
    ignored-by-pattern.

    A tracked file reverting to byte-identical HEAD content disappears from
    `git status --porcelain`; comparing the recorded path SET against the
    current one is what catches that class, which a pure content diff of
    surviving entries would miss.

    Ignored entries are included because ignored files are exactly the ones
    no other mechanism watches, and they have already changed a published
    number in this repository (the gap-demo Article 11 component).
    """
    root = Path(root or REPO_ROOT)
    head = _git(["rev-parse", "HEAD"], cwd=root).strip()
    head_tree = _git(["rev-parse", "HEAD^{tree}"], cwd=root).strip()
    entries = {}

    # The baseline itself lives in an ignored directory. Hashing it would
    # make every --record generate drift against its own previous content,
    # so it is the one path the snapshot excludes.
    self_rel = None
    try:
        self_rel = STATE_PATH.relative_to(root).as_posix()
    except ValueError:
        pass

    def _hash_file(path):
        try:
            return _git(["hash-object", "--", path], cwd=root).strip()
        except subprocess.CalledProcessError:
            return "unhashable"

    porcelain = _git(["status", "--porcelain", "--ignored=matching"], cwd=root)
    for line in porcelain.splitlines():
        status, path = line[:2], line[3:]
        # A rename line reads "R  old -> new"; hash the new path.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path == self_rel:
            continue
        full = root / path
        if full.is_file():
            entries[path] = {"status": status.strip() or "??",
                             "blob": _hash_file(path)}
        elif full.is_dir():
            files = [p for p in sorted(full.rglob("*")) if p.is_file()]
            if len(files) <= IGNORED_DIR_HASH_BUDGET:
                for p in files:
                    rel = p.relative_to(root).as_posix()
                    if rel == self_rel:
                        continue
                    entries[rel] = {"status": status.strip() or "??",
                                    "blob": _hash_file(rel)}
            else:
                entries[path] = {"status": (status.strip() or "??") + "dir",
                                 "blob": f"count:{len(files)}"}
        else:
            entries[path] = {"status": status.strip() or "??",
                             "blob": "absent"}
    return {"head": head, "head_tree": head_tree, "entries": entries}


def record(note=""):
    state = snapshot()
    state["recorded_at"] = datetime.now(timezone.utc).isoformat()
    state["note"] = note
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=1, sort_keys=True))
    return state


def compare(recorded=None, current=None):
    """Return a list of human-readable drift lines; empty means no drift."""
    if recorded is None:
        if not STATE_PATH.is_file():
            return None  # no baseline: nothing to compare against
        recorded = json.loads(STATE_PATH.read_text())
    current = current or snapshot()
    drift = []
    if recorded["head"] != current["head"]:
        drift.append(
            f"HEAD moved {recorded['head'][:7]} -> {current['head'][:7]}")
    old, new = recorded["entries"], current["entries"]
    for path in sorted(set(old) - set(new)):
        drift.append(f"no longer modified (committed, restored or deleted): {path}")
    for path in sorted(set(new) - set(old)):
        drift.append(f"newly changed since record: {path}")
    for path in sorted(set(old) & set(new)):
        if old[path]["blob"] != new[path]["blob"]:
            drift.append(f"content changed again since record: {path}")
    return drift


def stamp(stream=None):
    """One observability line for measurement scripts. Never raises, never
    changes the caller's exit code: a broken guard must not break a gate,
    it must say so and get out of the way."""
    import os
    if os.environ.get("REGULA_TREE_GUARD") == "0":
        return
    stream = stream or sys.stderr
    try:
        drift = compare()
    except Exception as exc:  # noqa: BLE001 - observability must not throw
        print(f"tree-guard: unavailable ({exc})", file=stream)
        return
    if drift is None:
        return  # no baseline recorded; stay silent
    recorded = json.loads(STATE_PATH.read_text())
    when = recorded.get("recorded_at", "?")
    if not drift:
        print(f"tree-guard: tree matches baseline recorded {when}", file=stream)
    else:
        print(f"tree-guard: TREE CHANGED since baseline {when}:", file=stream)
        for line in drift:
            print(f"tree-guard:   {line}", file=stream)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--record", action="store_true",
                       help="record the current tree as the baseline")
    group.add_argument("--check", action="store_true",
                       help="compare against the baseline; exit 3 on drift")
    group.add_argument("--status", action="store_true",
                       help="human-readable summary, always exit 0")
    parser.add_argument("--note", default="",
                        help="free-text note stored with --record")
    args = parser.parse_args(argv)

    if args.record:
        state = record(note=args.note)
        print(f"tree-guard: recorded {len(state['entries'])} changed path(s) "
              f"at HEAD {state['head'][:7]}")
        return 0

    drift = compare()
    if drift is None:
        print("tree-guard: no baseline recorded (run --record first)")
        return 0 if args.status else 2
    if not drift:
        print("tree-guard: tree matches baseline")
        return 0
    print("tree-guard: TREE CHANGED since baseline:")
    for line in drift:
        print(f"  {line}")
    return 0 if args.status else 3


if __name__ == "__main__":
    sys.exit(main())
