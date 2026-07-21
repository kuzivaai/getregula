#!/usr/bin/env python3
# regula-ignore
"""Shared path-safety gate for scanners that read files from an untrusted
project tree (Phase 5 threat model).

Several scanners walk a project directory and open matched files: `report.py`
(the code scanner) and `sbom.py` (the AI-BOM generator). A scanned repository
is untrusted input — a symlink inside it must not let the process read
arbitrary files reachable outside the repo (CI secrets, SSH keys, /etc/passwd),
and a single huge file must not exhaust memory.

This module is the SINGLE implementation of that check so the walkers cannot
drift. `report.py` grew the guard first (after a reproduction where a symlink
inside the scan root pointing outside it was silently followed and its content
scanned); `sbom.py`'s independent walkers did not have it until this was
centralised here.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import MAX_FILE_SIZE_BYTES


def is_safe_to_scan(filepath: Path, project_root: Path) -> "tuple[bool, str]":
    """Return (safe, reason). reason is "" when safe, otherwise one of:

      "symlink_escape" — the file (or a symlinked ancestor directory) resolves
                         outside project_root. Pass a *resolved* project_root.
      "oversized"      — file size exceeds MAX_FILE_SIZE_BYTES.
      "stat_failed"    — could not resolve/stat the file (race, permissions).

    This does not replace os.walk's followlinks=False default (which prevents
    symlinked-directory traversal); it closes the gap where an individual file
    is a symlink pointing outside the project.
    """
    try:
        resolved = filepath.resolve()
    except OSError:
        return False, "stat_failed"

    try:
        resolved.relative_to(project_root)
    except ValueError:
        return False, "symlink_escape"

    try:
        size = filepath.stat().st_size
    except OSError:
        return False, "stat_failed"

    if size > MAX_FILE_SIZE_BYTES:
        return False, "oversized"

    return True, ""
