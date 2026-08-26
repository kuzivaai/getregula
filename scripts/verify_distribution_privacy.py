#!/usr/bin/env python3
"""Fail when a wheel or source archive crosses the public privacy boundary.

The repository guard checks the files Git knows about. A release artefact is a
different publication surface: build metadata can repeat README content and an
sdist can include files that are absent from a wheel. This verifier reads both
formats without extracting them, validates member paths, bounds decompression,
and applies the same privacy rules used for the public source tree.

Only paths and rule names are reported. Matched values are never printed.
"""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).parent))

from public_repo_guard import is_text_path, scan_text

MAX_MEMBER_BYTES = 16 * 1024 * 1024
MAX_ARCHIVE_BYTES = 256 * 1024 * 1024
_SDIST_ROOT = re.compile(r"regula[_-]ai-\d+(?:\.\d+)*(?:[A-Za-z0-9.-]*)?", re.I)


class ArchiveSafetyError(ValueError):
    """The artefact cannot be audited safely and must not be published."""


@dataclass(frozen=True)
class DistributionFinding:
    artefact: str
    member: str
    rule: str


def normalise_member(name: str) -> str:
    """Validate an archive name and remove the conventional sdist root."""
    if not name or "\x00" in name or "\\" in name:
        raise ArchiveSafetyError("archive contains an empty or ambiguous member path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part == ".." for part in path.parts):
        raise ArchiveSafetyError("archive contains a path outside its root")
    parts = [part for part in path.parts if part not in {"", "."}]
    if not parts:
        raise ArchiveSafetyError("archive contains an empty member path")
    if len(parts) > 1 and _SDIST_ROOT.fullmatch(parts[0]):
        parts = parts[1:]
    return "/".join(parts)


def _scan_member(
    artefact: Path,
    member: str,
    data: bytes | None,
) -> list[DistributionFinding]:
    rules = set(scan_text(member, ""))
    if data is not None and is_text_path(member):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ArchiveSafetyError(
                f"{member}: public text is not valid UTF-8"
            ) from error
        rules.update(scan_text(member, text))
    return [
        DistributionFinding(artefact.name, finding.path, finding.rule)
        for finding in sorted(rules, key=lambda item: (item.path, item.rule))
    ]


def _check_size(size: int, total: int, member: str) -> int:
    if size < 0 or size > MAX_MEMBER_BYTES:
        raise ArchiveSafetyError(
            f"{member}: member exceeds the {MAX_MEMBER_BYTES}-byte audit limit"
        )
    total += size
    if total > MAX_ARCHIVE_BYTES:
        raise ArchiveSafetyError(
            f"archive exceeds the {MAX_ARCHIVE_BYTES}-byte expanded audit limit"
        )
    return total


def scan_wheel(path: Path) -> list[DistributionFinding]:
    findings: set[DistributionFinding] = set()
    total = 0
    try:
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                member = normalise_member(info.filename)
                if info.is_dir():
                    continue
                if info.flag_bits & 0x1:
                    raise ArchiveSafetyError(f"{member}: encrypted members cannot be audited")
                total = _check_size(info.file_size, total, member)
                data = archive.read(info) if is_text_path(member) else None
                findings.update(_scan_member(path, member, data))
    except (OSError, zipfile.BadZipFile) as error:
        raise ArchiveSafetyError(f"cannot read wheel: {path.name}") from error
    return sorted(findings, key=lambda item: (item.member, item.rule))


def scan_sdist(path: Path) -> list[DistributionFinding]:
    findings: set[DistributionFinding] = set()
    total = 0
    try:
        with tarfile.open(path, "r:gz") as archive:
            for info in archive.getmembers():
                member = normalise_member(info.name)
                if info.isdir():
                    continue
                if not info.isfile():
                    raise ArchiveSafetyError(
                        f"{member}: links and special members cannot be audited"
                    )
                total = _check_size(info.size, total, member)
                data = None
                if is_text_path(member):
                    stream = archive.extractfile(info)
                    if stream is None:
                        raise ArchiveSafetyError(f"{member}: member cannot be read")
                    data = stream.read(MAX_MEMBER_BYTES + 1)
                    if len(data) != info.size:
                        raise ArchiveSafetyError(f"{member}: member size is inconsistent")
                findings.update(_scan_member(path, member, data))
    except (OSError, tarfile.TarError) as error:
        raise ArchiveSafetyError(f"cannot read source archive: {path.name}") from error
    return sorted(findings, key=lambda item: (item.member, item.rule))


def scan_distribution(path: Path) -> list[DistributionFinding]:
    if path.name.endswith(".whl"):
        return scan_wheel(path)
    if path.name.endswith((".tar.gz", ".tgz")):
        return scan_sdist(path)
    raise ArchiveSafetyError(f"unsupported distribution format: {path.name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("artefacts", nargs="+", type=Path)
    args = parser.parse_args(argv)

    findings: list[DistributionFinding] = []
    try:
        for artefact in args.artefacts:
            findings.extend(scan_distribution(artefact))
    except ArchiveSafetyError as error:
        print(f"distribution-privacy: cannot complete scan: {error}")
        return 2

    if findings:
        for finding in findings:
            print(f"{finding.artefact}!{finding.member}: {finding.rule}")
        print(f"distribution-privacy: {len(findings)} finding(s)")
        return 1

    print(f"distribution-privacy: {len(args.artefacts)} artefact(s), 0 findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
