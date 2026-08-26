#!/usr/bin/env python3
"""Fail when tracked public-repository content contains private material.

The guard reports rule names and paths only. It never prints the matched value.
It is intentionally conservative about machine paths, contact details and
internal operating records. Product security and regulatory source files may
describe sensitive *concepts*; the guard looks for actual identifying formats
and prohibited record locations rather than banning domain vocabulary.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[1]

PRIVATE_PREFIXES = (
    ".agents/",
    ".claude/",
    ".codex/",
    "business/",
    "docs/commercial/",
    "docs/distribution/",
    "docs/handover/",
    "docs/improvement/",
    "docs/venture/",
    "handovers/",
    "internal/",
    "private/",
    "session-logs/",
)

PRIVATE_NAME_PARTS = (
    "brain-feed",
    "handover",
    "owner" + "-actions",
    "session-log",
)

TEXT_SUFFIXES = {
    ".cfg", ".css", ".csv", ".html", ".ini", ".js", ".json", ".md",
    ".py", ".rst", ".toml", ".txt", ".yaml", ".yml",
}
TEXT_BASENAMES = {"METADATA", "PKG-INFO"}

MACHINE_PATHS = (
    re.compile(r"/home/(?!USER(?:/|\b))[A-Za-z0-9._-]+"),
    re.compile(r"/mnt/c/Users/(?!USER(?:/|\b))[A-Za-z0-9._-]+", re.I),
    re.compile(r"C:\\Users\\(?!USER(?:\\|\b))[A-Za-z0-9._-]+", re.I),
)

EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED_EMAILS = {
    "security@getregula.com",
    "support@getregula.com",
}
ALLOWED_EMAIL_DOMAINS = {
    "example.com",
    "users.noreply.github.com",
}

# Concrete identifiers, not discussions of these concepts.
IDENTIFIER_FORMATS = (
    ("uk-national-insurance-number", re.compile(
        r"\b(?!BG|GB|KN|NK|NT|TN|ZZ)[A-CEGHJ-PR-TW-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b",
        re.I,
    )),
    ("international-bank-account-number", re.compile(
        r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b"
    )),
)

# High-confidence credential shapes. These deliberately avoid broad patterns
# such as ``password = ...``: a public scanner should not make a release fail
# on documentation prose or harmless variable names. More expansive secret
# scanners remain useful defence in depth, but these formats stop the most
# consequential concrete values from reaching either Git or a distribution.
CREDENTIAL_FORMATS = (
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b")),
    ("google-api-key", re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b")),
    ("openai-api-key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,255}\b")),
    ("private-key-block", re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----")),
)


def _chars(values: tuple[int, ...]) -> str:
    """Construct blocked personal strings without re-publishing them here."""
    return "".join(chr(value) for value in values)


# Known identities previously present in repository records. Character-code
# construction lets the guard prevent reintroduction without keeping the
# personal strings in the public tree it protects.
PRIVATE_IDENTITIES = (
    _chars((112, 104, 117, 108, 117, 115, 111)),
    _chars((107, 117, 122, 105, 118, 97, 32, 109, 117, 122, 111, 110, 100, 111)),
    _chars((107, 117, 122, 105, 118, 97, 45, 109, 117, 122, 111, 110, 100, 111)),
)

PRIVATE_PROGRAM_MARKERS = (
    _chars((112, 114, 111, 100, 117, 99, 116, 95, 98, 117, 105, 108, 100)),
    _chars((112, 97, 121, 109, 101, 110, 116, 95, 103, 97, 116, 101)),
    _chars((98, 117, 115, 105, 110, 101, 115, 115, 32, 100, 111, 115, 115, 105, 101, 114)),
    _chars((111, 119, 110, 101, 114, 45, 97, 99, 116, 105, 111, 110)),
    _chars((111, 119, 110, 101, 114, 95, 97, 99, 116, 105, 111, 110)),
    _chars((111, 119, 110, 101, 114, 32, 97, 99, 116, 105, 111, 110)),
)


@dataclass(frozen=True)
class Finding:
    path: str
    rule: str


def tracked_paths(root: Path = ROOT) -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if proc.returncode:
        raise RuntimeError("git ls-files failed")
    return [
        root / item.decode("utf-8", errors="surrogateescape")
        for item in proc.stdout.split(b"\0")
        if item
        if (root / item.decode("utf-8", errors="surrogateescape")).is_file()
    ]


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def is_text_path(path: str | Path) -> bool:
    """Return whether a repository or archive member should be decoded."""
    candidate = Path(path)
    return (
        candidate.suffix.casefold() in TEXT_SUFFIXES
        or candidate.name in TEXT_BASENAMES
    )


def scan_text(rel: str, text: str) -> list[Finding]:
    """Scan already-decoded public content without echoing matched values."""
    lowered = rel.casefold()
    findings: set[Finding] = set()

    if lowered.startswith(PRIVATE_PREFIXES):
        findings.add(Finding(rel, "private-path"))
    if any(part in Path(lowered).name for part in PRIVATE_NAME_PARTS):
        findings.add(Finding(rel, "private-record-name"))

    if any(pattern.search(text) for pattern in MACHINE_PATHS):
        findings.add(Finding(rel, "personal-machine-path"))

    folded_text = text.casefold()
    if any(identity in folded_text for identity in PRIVATE_IDENTITIES):
        findings.add(Finding(rel, "personal-identity"))
    if any(marker in folded_text for marker in PRIVATE_PROGRAM_MARKERS):
        findings.add(Finding(rel, "private-program-marker"))

    for match in EMAIL.finditer(text):
        address = match.group(0).casefold()
        domain = address.rsplit("@", 1)[1]
        if address not in ALLOWED_EMAILS and domain not in ALLOWED_EMAIL_DOMAINS:
            findings.add(Finding(rel, "non-project-email"))
            break

    for rule, pattern in IDENTIFIER_FORMATS:
        if pattern.search(text):
            findings.add(Finding(rel, rule))

    for rule, pattern in CREDENTIAL_FORMATS:
        if pattern.search(text):
            findings.add(Finding(rel, rule))

    return sorted(findings, key=lambda item: (item.path, item.rule))


def scan_path(path: Path, root: Path = ROOT) -> list[Finding]:
    rel = _relative(path, root)
    if not is_text_path(path):
        return scan_text(rel, "")

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return scan_text(rel, "")
    return scan_text(rel, text)


def scan(paths: list[Path], root: Path = ROOT) -> list[Finding]:
    findings = {finding for path in paths for finding in scan_path(path, root)}
    return sorted(findings, key=lambda item: (item.path, item.rule))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)
    try:
        paths = [path.resolve() for path in args.paths] or tracked_paths()
        findings = scan(paths)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"public-repo-guard: cannot complete scan: {error}", file=sys.stderr)
        return 2

    if findings:
        for finding in findings:
            print(f"{finding.path}: {finding.rule}")
        print(f"public-repo-guard: {len(findings)} finding(s)", file=sys.stderr)
        return 1

    print(f"public-repo-guard: {len(paths)} tracked file(s), 0 findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
