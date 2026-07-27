# regula-ignore
#!/usr/bin/env python3
"""Release gate: the version bump must match what actually changed.

Why this exists
    The 1.7.x line shipped new features in PATCH releases six times
    (1.7.2, 1.7.3, 1.7.5, 1.7.6, 1.7.8, 1.7.10 all carry "Added" or
    feat content), while the changelog claimed Semantic Versioning.
    SemVer 2.0.0 item 7 says new backward-compatible functionality MUST
    increment MINOR. Nobody caught it because nothing checked it: the
    existing release gate asserts tag == constants.VERSION, which stops
    typos but not misclassified bumps. This gate closes the class.

What it checks, given a target version (the tag being released):
    1. The target parses as X.Y.Z and is strictly greater than the
       previous released tag (PEP 440 numeric ordering on the release
       segment; no strings, no lexicographic traps).
    2. The MINIMUM required bump, derived from TWO independent signals:
         a. conventional-commit subjects between the previous tag and
            HEAD: "feat" requires MINOR; a "!" marker or a
            "BREAKING CHANGE" footer requires MAJOR; everything else
            (fix, docs, ci, chore, perf, refactor, test, style, build,
            release, deps) requires PATCH. Unknown prefixes count as
            PATCH and are listed so a human sees them.
         b. the CHANGELOG section for the target version, read with
            Keep-a-Changelog semantics: "Removed" requires MAJOR;
            "Added" or "Deprecated" requires MINOR (SemVer item 7 makes
            deprecation a MINOR event); "Fixed", "Security" or
            "Changed" alone require PATCH. A "Changed" entry that is
            actually breaking must be recorded under "Removed" or
            flagged BREAKING in the commit, which signal (a) catches.
       The required bump is the STRICTER of the two signals.
    3. The actual bump from previous tag to target is AT LEAST the
       required bump. Bumping further than required is always legal
       (that is how the 1.7.10 -> 1.9.0 realignment shipped); bumping
       less fails the release.

Run modes
    python3 scripts/release_gate.py --target v1.9.0
    python3 scripts/release_gate.py            (target = constants.VERSION)

This is a RELEASE-time gate (release.yml runs it before build/publish).
It is deliberately not part of the per-commit suite: mid-development,
feat commits legitimately sit on main before the version is bumped.
The unit tests in tests/test_release_gate.py cover the logic itself.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ordered so max() picks the strictest requirement.
PATCH, MINOR, MAJOR = 0, 1, 2
_BUMP_NAMES = {PATCH: "patch", MINOR: "minor", MAJOR: "major"}

# Conventional-commit types that only ever require a PATCH bump.
_PATCH_TYPES = {
    "fix", "docs", "ci", "chore", "perf", "refactor", "test", "tests",
    "style", "build", "release", "deps", "revert", "site", "content",
}
_MINOR_TYPES = {"feat"}

_SUBJECT_RE = re.compile(r"^(?P<type>[a-z]+)(?:\([^)]*\))?(?P<bang>!)?:")


def parse_version(text: str) -> "tuple[int, int, int]":
    """Parse vX.Y.Z or X.Y.Z into an int tuple. Raises ValueError."""
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", text.strip())
    if not m:
        raise ValueError(
            f"{text!r} is not a plain X.Y.Z version. The release line uses "
            "exactly three numeric components (PEP 440 release segment)."
        )
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def classify_subject(subject: str) -> "tuple[int, bool]":
    """Return (required_bump, recognised) for one commit subject."""
    if "BREAKING CHANGE" in subject or "BREAKING-CHANGE" in subject:
        return MAJOR, True
    m = _SUBJECT_RE.match(subject)
    if not m:
        # Merge commits, squash titles like "ci: bump x (#27)" DO match;
        # anything unmatched (e.g. "Merge PR #30: ...") counts as PATCH.
        return PATCH, False
    if m.group("bang"):
        return MAJOR, True
    ctype = m.group("type")
    if ctype in _MINOR_TYPES:
        return MINOR, True
    if ctype in _PATCH_TYPES:
        return PATCH, True
    return PATCH, False


def required_bump_from_subjects(subjects: "list[str]") -> "tuple[int, list[str]]":
    """Strictest bump the commit log demands, plus unrecognised subjects."""
    required = PATCH
    unrecognised = []
    for s in subjects:
        bump, recognised = classify_subject(s)
        required = max(required, bump)
        if not recognised:
            unrecognised.append(s)
    return required, unrecognised


def required_bump_from_changelog(changelog_text: str, target: "tuple[int, int, int]") -> "tuple[int, list[str]]":
    """Strictest bump the target version's CHANGELOG section demands.

    Returns (bump, section_types_found). If the section is missing the
    gate fails elsewhere; here we just return PATCH with an empty list.
    """
    tgt = f"{target[0]}.{target[1]}.{target[2]}"
    # Section runs from "## [<tgt>]" to the next "## [" heading.
    m = re.search(
        rf"^## \[{re.escape(tgt)}\][^\n]*\n(.*?)(?=^## \[|\Z)",
        changelog_text, re.M | re.S,
    )
    if not m:
        return PATCH, []
    types = re.findall(r"^### (\w+)", m.group(1), re.M)
    required = PATCH
    for t in types:
        if t == "Removed":
            required = max(required, MAJOR)
        elif t in ("Added", "Deprecated"):
            required = max(required, MINOR)
    return required, types


def actual_bump(prev: "tuple[int, int, int]", target: "tuple[int, int, int]") -> int:
    """Classify the prev -> target step. Raises if target is not greater."""
    if target <= prev:
        raise ValueError(
            f"target {target} is not greater than previous release {prev}; "
            "released versions are immutable and the line must be monotonic."
        )
    if target[0] > prev[0]:
        return MAJOR
    if target[1] > prev[1]:
        return MINOR
    return PATCH


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def previous_release_tag(target: "tuple[int, int, int]") -> "tuple[str, tuple[int, int, int]]":
    """Highest vX.Y.Z tag strictly below the target, by numeric ordering."""
    tags = []
    for line in _git("tag", "--list", "v*").splitlines():
        try:
            tags.append((parse_version(line), line))
        except ValueError:
            continue  # aliases like v1 are not release-line tags
    below = [t for t in tags if t[0] < target]
    if not below:
        raise SystemExit(
            f"release-gate: no release tag below {target} found; "
            "fetch tags first (git fetch --tags)."
        )
    version, name = max(below)
    return name, version


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--target", help="version being released (vX.Y.Z); defaults to constants.VERSION")
    args = parser.parse_args(argv)

    if args.target:
        target = parse_version(args.target)
    else:
        from constants import VERSION
        target = parse_version(VERSION)

    prev_name, prev = previous_release_tag(target)
    # Subjects carry the conventional type; bodies are scanned ONLY for
    # BREAKING CHANGE footers. Classifying body prose as subjects would
    # flood the unrecognised list with false positives.
    subjects = [s for s in _git("log", "--format=%s", f"{prev_name}..HEAD").splitlines() if s.strip()]
    bodies = _git("log", "--format=%b", f"{prev_name}..HEAD")

    commit_bump, unrecognised = required_bump_from_subjects(subjects)
    if "BREAKING CHANGE" in bodies or "BREAKING-CHANGE" in bodies:
        commit_bump = MAJOR
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section_bump, section_types = required_bump_from_changelog(changelog, target)
    if not section_types:
        print(f"release-gate: FAIL: CHANGELOG.md has no section for "
              f"{target[0]}.{target[1]}.{target[2]}; every release is recorded.")
        return 1

    required = max(commit_bump, section_bump)
    actual = actual_bump(prev, target)

    print(f"release-gate: previous release {prev_name}, target "
          f"{target[0]}.{target[1]}.{target[2]}")
    print(f"  commits since {prev_name}: {len(subjects)} subjects, "
          f"require {_BUMP_NAMES[commit_bump]}")
    print(f"  changelog sections {section_types} require {_BUMP_NAMES[section_bump]}")
    if unrecognised:
        print(f"  note: {len(unrecognised)} line(s) without a conventional "
              f"prefix counted as patch: {unrecognised[:3]}")
    print(f"  required bump: {_BUMP_NAMES[required]}; actual bump: {_BUMP_NAMES[actual]}")

    if actual < required:
        print(
            f"release-gate: FAIL: this release needs at least a "
            f"{_BUMP_NAMES[required]} bump from {prev_name} but "
            f"{target[0]}.{target[1]}.{target[2]} is only a "
            f"{_BUMP_NAMES[actual]} bump. SemVer 2.0.0 items 6-8; see "
            "docs/VERSIONING.md."
        )
        return 1
    print("release-gate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
