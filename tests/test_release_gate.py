# regula-ignore
"""Unit tests for scripts/release_gate.py.

Pure logic tests: no git, no subprocess, no repo state. The live
commit-range check runs at release time in release.yml, not here,
because mid-development feat commits legitimately precede the bump.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from release_gate import (  # noqa: E402
    MAJOR, MINOR, PATCH,
    actual_bump,
    classify_subject,
    parse_version,
    required_bump_from_changelog,
    required_bump_from_subjects,
)


def test_parse_version_accepts_v_prefix_and_plain():
    assert parse_version("v1.9.0") == (1, 9, 0)
    assert parse_version("1.7.10") == (1, 7, 10)


def test_parse_version_rejects_non_release_forms():
    for bad in ("1.9", "v1", "1.9.0rc1", "one.two.three", "1.90.0.0"):
        try:
            parse_version(bad)
        except ValueError:
            continue
        raise AssertionError(f"parse_version accepted {bad!r}")


def test_parse_version_orders_numerically_not_lexicographically():
    """The trap behind this whole gate: 1.9.0 < 1.10.0 < 1.90.0 as
    NUMBERS. A string comparison would order them 1.10 < 1.9 < 1.90
    and misread 1.10 as older than 1.9."""
    assert parse_version("1.9.0") < parse_version("1.10.0") < parse_version("1.90.0")


def test_classify_feat_requires_minor():
    assert classify_subject("feat(omnibus): flip OMNIBUS_OJ_DATE")[0] == MINOR
    assert classify_subject("feat: add owasp agentic framework")[0] == MINOR


def test_classify_fix_docs_ci_require_patch():
    for s in ("fix(security): close the hostile-cwd read class",
              "docs(counts): cascade 2789 -> 2791",
              "ci: bump actions/checkout from 6.0.3 to 7.0.1 (#27)",
              "release: v1.7.10"):
        assert classify_subject(s)[0] == PATCH, s


def test_classify_breaking_markers_require_major():
    assert classify_subject("feat!: drop the legacy envelope")[0] == MAJOR
    assert classify_subject("refactor(cli)!: remove regula classify")[0] == MAJOR
    assert classify_subject("BREAKING CHANGE: exit codes renumbered")[0] == MAJOR


def test_classify_unrecognised_counts_as_patch_but_is_flagged():
    bump, recognised = classify_subject("Merge PR #30: RFC 3161 verification")
    assert bump == PATCH
    assert recognised is False


def test_required_bump_strictest_signal_wins():
    subjects = [
        "docs: tidy readme",
        "feat(frameworks): add OWASP ASI",
        "fix: close a race",
    ]
    bump, unrecognised = required_bump_from_subjects(subjects)
    assert bump == MINOR
    assert unrecognised == []


def test_changelog_added_requires_minor_and_removed_requires_major():
    text = (
        "## [Unreleased]\n\n"
        "## [2.0.0] - 2027-01-01\n### Removed\n- old thing\n\n"
        "## [1.9.0] - 2026-07-27\n### Added\n- new thing\n### Fixed\n- bug\n\n"
        "## [1.8.1] - 2026-07-01\n### Fixed\n- bug\n### Security\n- hole\n"
    )
    assert required_bump_from_changelog(text, (2, 0, 0))[0] == MAJOR
    assert required_bump_from_changelog(text, (1, 9, 0))[0] == MINOR
    assert required_bump_from_changelog(text, (1, 8, 1))[0] == PATCH


def test_changelog_deprecated_requires_minor():
    """SemVer 2.0.0 item 7: deprecating public API functionality is a
    MINOR event, not a patch."""
    text = "## [1.9.0] - 2026-07-27\n### Deprecated\n- old flag\n"
    assert required_bump_from_changelog(text, (1, 9, 0))[0] == MINOR


def test_changelog_missing_section_returns_no_types():
    bump, types = required_bump_from_changelog("## [1.0.0]\n### Added\n- x\n", (9, 9, 9))
    assert types == []


def test_actual_bump_classifies_each_step():
    assert actual_bump((1, 7, 9), (1, 7, 10)) == PATCH
    assert actual_bump((1, 7, 10), (1, 8, 0)) == MINOR
    assert actual_bump((1, 7, 10), (1, 9, 0)) == MINOR
    assert actual_bump((1, 9, 0), (2, 0, 0)) == MAJOR


def test_actual_bump_rejects_non_monotonic_targets():
    for prev, tgt in (((1, 9, 0), (1, 9, 0)), ((1, 9, 0), (1, 7, 10))):
        try:
            actual_bump(prev, tgt)
        except ValueError:
            continue
        raise AssertionError(f"actual_bump accepted {prev} -> {tgt}")


def test_the_v1_7_10_misnumbering_would_have_been_caught():
    """Regression pin for the incident this gate exists to prevent: the
    real v1.7.10 release carried feat commits (OWASP ASI framework, the
    Omnibus flip) inside a PATCH bump. With this gate, that release
    fails; the same content as 1.8.0 or above passes."""
    subjects = [
        "feat(frameworks): add OWASP ASI 2026 as the 13th framework + MITRE ATLAS 2026.06 agentic techniques",
        "feat(omnibus): flip OMNIBUS_OJ_DATE: Regulation (EU) 2026/1744 published in the OJ 24 Jul 2026",
        "fix(security): close the hostile-cwd read class; guard the scanned project's policy file",
        "release: v1.7.10",
    ]
    required, _ = required_bump_from_subjects(subjects)
    assert required == MINOR
    assert actual_bump((1, 7, 9), (1, 7, 10)) < required          # the bug
    assert actual_bump((1, 7, 10), (1, 9, 0)) >= required          # the fix


def test_over_bumping_is_always_allowed():
    """Bumping further than required is legal (that is how the
    1.7.10 -> 1.9.0 realignment ships): only under-bumping fails."""
    subjects = ["fix: a one-line fix"]
    required, _ = required_bump_from_subjects(subjects)
    assert actual_bump((1, 7, 10), (1, 9, 0)) >= required


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    raise SystemExit(1 if failures else 0)
