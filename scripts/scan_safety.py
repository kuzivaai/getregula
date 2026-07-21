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

import errno
import os
import stat as _stat
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from constants import MAX_FILE_SIZE_BYTES

# O_NOFOLLOW is POSIX and absent on Windows. Where it exists it is what
# closes the check-then-open race: the kernel refuses the open if the final
# path component is a symlink, so an attacker cannot swap a validated
# regular file for a symlink between our check and our read.
_HAS_NOFOLLOW = hasattr(os, "O_NOFOLLOW")

# O_NOFOLLOW raises ELOOP on Linux AND macOS. FreeBSD deliberately deviates
# from POSIX and raises EMLINK, "to distinguish it from the case of too many
# symbolic link traversals" (FreeBSD open(2)). Accepting both is safe: EMLINK
# is not a documented error for open(O_RDONLY) without O_CREAT, so there is no
# false-positive path on Linux.
_SYMLINK_ERRNOS = {errno.ELOOP}
if hasattr(errno, "EMLINK"):
    _SYMLINK_ERRNOS.add(errno.EMLINK)


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


def open_if_safe(filepath: Path, project_root: "Optional[Path]" = None,
                 dir_fd: "Optional[int]" = None) -> "tuple[Optional[int], str]":
    """Open `filepath` for reading, enforcing the guard on the OPENED FILE.

    Returns (fd, "") on success — the caller owns the descriptor and MUST
    close it — or (None, reason) using the same reason vocabulary as
    `is_safe_to_scan`, plus "unreadable".

    Why this exists, when `is_safe_to_scan` already checks the same things:
    that function validates a *name*, and every caller then re-opened the
    same name. Between the two resolutions an attacker with write access to
    the scanned tree can replace the validated file with a symlink pointing
    outside it, so the scanner reads a file the guard never approved — a
    TOCTOU race that defeats the escape protection entirely (issue #31).

    The fix is to stop resolving twice. We open once and derive every
    decision from the descriptor:

      * ``O_NOFOLLOW`` makes the kernel refuse the open outright if the final
        component is a symlink, so the swap cannot succeed rather than being
        detected afterwards.
      * ``fstat(fd)`` measures the file we are actually holding, so the size
        we cap on is the size we read — not a size that was true a moment ago.
      * ``S_ISREG`` rejects FIFOs, devices and directories, which would
        otherwise block the scan or return meaningless bytes.

    Residual gaps, stated rather than papered over:

      * A *hardlink* swap is not prevented — O_NOFOLLOW only concerns
        symlinks. It confers no privilege: creating one requires write access
        inside the repository and read access to the target on the same
        filesystem, so the attacker could already read the content.
      * ``O_NOFOLLOW`` guards only the FINAL component. Swapping an ancestor
        *directory* for a symlink between the name check and the open still
        escapes the root — reproduced against this function. Unlike the
        hardlink case this one does confer privilege, so pass ``dir_fd``:
        opening the basename relative to a descriptor already held on the
        parent directory pins that inode, and re-traversal of the ancestor
        path never happens. Callers get such a descriptor from ``os.fwalk``.
        Without ``dir_fd`` the ancestor race remains open; static ancestor
        symlinks are still caught by the name check and by
        ``os.walk(followlinks=False)``, but a *racing* swap is not.
      * On Windows there is no ``O_NOFOLLOW`` and no ``os.fwalk``; we fall
        back to the name-based check plus ``fstat``, which still closes the
        size race but not the symlink races. Creating symlinks on Windows
        requires privilege or developer mode, so the exposure is materially
        smaller. Silently degrading is deliberate: refusing to scan on
        Windows would trade a local race for a total loss of function.

    Note on the name pre-check: ``Path.resolve()`` goes through
    ``os.path.realpath``, which stops resolving without error once the
    expansion exceeds PATH_MAX (CVE-2025-4517 broke CPython's own tarfile
    filter exactly this way). That is why the pre-check below is explicitly
    NOT the security boundary — the open flags and the descriptor are.
    """
    # Fast, cheap rejection on the name. This is not the security boundary —
    # the flags below are — but it yields the precise "symlink_escape"
    # reason for reporting, and avoids an open() for the common case.
    # project_root is optional. With it we also enforce containment; without
    # it we still get every descriptor-level protection — no symlink follow,
    # no FIFO block, regular files only, size capped. That matters because
    # the FIFO denial-of-service is reachable from any walker, including
    # ones with no project root in scope, and "I cannot do the containment
    # check" is no reason to also skip the ones I can do.
    if project_root is not None:
        safe, reason = is_safe_to_scan(filepath, project_root)
        if not safe:
            return None, reason

    flags = os.O_RDONLY
    if _HAS_NOFOLLOW:
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_NONBLOCK"):
        # MUST be set, and this is not a performance tweak. open(O_RDONLY)
        # on a FIFO blocks until a writer appears — forever, if none does.
        # The S_ISREG check below cannot save us because it runs *after*
        # open() returns. A single named pipe committed to a repository
        # would therefore hang the scanner indefinitely: a trivial denial of
        # service against any CI job scanning untrusted code. O_NONBLOCK
        # makes that open() return immediately so we can reject it. It has
        # no effect on regular files, which are all we go on to read.
        flags |= os.O_NONBLOCK
    if hasattr(os, "O_CLOEXEC"):
        # Do not leak the descriptor into any subprocess the scan spawns.
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_BINARY"):  # Windows: never translate newlines
        flags |= os.O_BINARY

    try:
        # With dir_fd, open the basename relative to a descriptor the caller
        # already holds on the parent directory. That pins the directory
        # inode, so an ancestor swapped for a symlink after the name check
        # cannot be traversed. Without it, only the final component is
        # protected — see "Residual gaps" above.
        if dir_fd is not None:
            fd = os.open(filepath.name, flags, dir_fd=dir_fd)
        else:
            fd = os.open(filepath, flags)
    except OSError as exc:
        if exc.errno in _SYMLINK_ERRNOS:
            # O_NOFOLLOW refused it: the path became a symlink after our
            # name check. This is the race the function exists to stop.
            return None, "symlink_escape"
        if exc.errno in (errno.EACCES, errno.EPERM):
            return None, "unreadable"
        return None, "stat_failed"

    try:
        st = os.fstat(fd)
        if not _stat.S_ISREG(st.st_mode):
            os.close(fd)
            return None, "not_regular_file"
        if st.st_size > MAX_FILE_SIZE_BYTES:
            os.close(fd)
            return None, "oversized"
    except OSError:
        os.close(fd)
        return None, "stat_failed"

    return fd, ""


def read_bytes_if_safe(filepath: Path, project_root: "Optional[Path]" = None,
                       dir_fd: "Optional[int]" = None) -> "tuple[Optional[bytes], str]":
    """Read `filepath` in full, or return (None, reason).

    The convenience wrapper every content-reading caller should use: it
    guarantees the bytes returned came from the descriptor that passed the
    guard, and that the descriptor is closed on every path.

    Note the read is bounded by the cap already verified via fstat, so a
    file growing between fstat and read cannot make us read more than
    MAX_FILE_SIZE_BYTES.
    """
    fd, reason = open_if_safe(filepath, project_root, dir_fd=dir_fd)
    if fd is None:
        return None, reason
    try:
        chunks = []
        remaining = MAX_FILE_SIZE_BYTES
        while remaining > 0:
            chunk = os.read(fd, min(1 << 20, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks), ""
    except OSError:
        return None, "unreadable"
    finally:
        os.close(fd)


def read_text_if_safe(filepath: Path, project_root: "Optional[Path]" = None,
                      encoding: str = "utf-8", errors: str = "ignore",
                      dir_fd: "Optional[int]" = None) -> "Optional[str]":
    """Text convenience over `read_bytes_if_safe`. Returns None if refused.

    The drop-in replacement for `path.read_text(...)` anywhere a scanner
    reads from a tree it does not control. A bare `read_text` on a named
    pipe blocks until a writer appears — forever — so a single FIFO
    committed to a repository hung 15+ commands even after the main scan
    loop had been hardened. Pass `project_root` where it is in scope to get
    symlink-escape containment as well.
    """
    raw, _reason = read_bytes_if_safe(filepath, project_root, dir_fd=dir_fd)
    if raw is None:
        return None
    return raw.decode(encoding, errors=errors)


def walk_project_files(project_root: Path, extensions=None, skip_dirs=None):
    """Yield (path, content_bytes) for every file under `project_root` that
    passes the guard. Unsafe files are skipped silently.

    This exists because the guard was OPT-IN, and that is the single root
    cause behind four separate defects found in July 2026: a FIFO hung 15+
    commands, `regula deps`/`sbom` read an out-of-root requirements.txt,
    `report.py` read an escaping `.env`, and `aibom.py` shipped a clone of
    `sbom.py`'s walker with the guard quietly missing. Each was fixed at
    the call site; each recurred somewhere else, because every new walker
    had to REMEMBER to be safe. A helper that is safe by construction is
    the only version of this fix that stays fixed.

    It also closes the ancestor-directory race that `open_if_safe` alone
    cannot: `os.fwalk` hands back a descriptor for each directory it
    visits, and opening the basename relative to that descriptor pins the
    directory inode, so an ancestor swapped for a symlink mid-scan is never
    re-traversed. `os.fwalk` is POSIX-only (it needs dir_fd support); on
    Windows we fall back to `os.walk` and the guard degrades to protecting
    the final component only, which is documented on `open_if_safe`.

    Args:
        project_root: scan root. Resolved once; containment is checked
            against this.
        extensions: optional set of suffixes to yield (e.g. {".py"}).
            Compared lowercased. None means every file.
        skip_dirs: directory names to prune. Pass `constants.SKIP_DIRS`.
    """
    root = Path(project_root).resolve()
    skip = set(skip_dirs or ())
    exts = {e.lower() for e in extensions} if extensions else None

    use_fwalk = hasattr(os, "fwalk")
    walker = os.fwalk(root) if use_fwalk else os.walk(root)

    for entry in walker:
        if use_fwalk:
            dirpath, dirnames, filenames, dirfd = entry
        else:
            dirpath, dirnames, filenames = entry
            dirfd = None
        dirnames[:] = [d for d in dirnames if d not in skip]
        for filename in filenames:
            if exts is not None and Path(filename).suffix.lower() not in exts:
                continue
            fpath = Path(dirpath) / filename
            raw, _reason = read_bytes_if_safe(fpath, root, dir_fd=dirfd)
            if raw is None:
                continue
            yield fpath, raw
