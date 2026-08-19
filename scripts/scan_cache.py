# regula-ignore
"""Content-hash scan caching for Regula.

Caches scan results keyed by SHA-256 of file content.
Unchanged files skip re-scanning on subsequent runs.
"""
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

# Cache schema/version salt. Bump whenever risk_patterns.py or classify_risk.py
# change detection semantics — existing entries will be invalidated automatically
# on the next scan. This prevents the silent "upgraded Regula still sees
# 0 findings" bug where users keep stale empty results after a pattern update.
_sys_path = sys.path[:]
sys.path.insert(0, str(Path(__file__).parent))
try:
    from constants import VERSION as _REGULA_VERSION  # type: ignore
except Exception:  # pragma: no cover
    _REGULA_VERSION = "unknown"
finally:
    sys.path[:] = _sys_path


def _patterns_fingerprint() -> str:
    """SHA-256 of risk_patterns.py + report.py — invalidates cache on any rule change."""
    try:
        rp = Path(__file__).parent / "risk_patterns.py"
        rep = Path(__file__).parent / "report.py"
        combined = rp.read_bytes() + rep.read_bytes()
        return hashlib.sha256(combined).hexdigest()[:12]
    except OSError:
        return "unknown"


# v4: cache keys carry a scan-context token (see ScanCache.get/put) so
# entries written under one project context (e.g. AI-library self-scan,
# which caps confidence scores) can never be served to a different one.
# The bump also invalidates v3 entries, which could be incomplete when
# written by a --min-tier scan.
#
# v5: cache keys carry a PATH-CONTEXT token as well. The `path` component is
# the path RELATIVE to the scan root, while provenance and the example/init
# confidence penalties are derived from the FULL path, so two byte-identical
# files at the same relative path under different roots shared one key and
# whichever was scanned first decided what the other one read. That is not
# only a priority wobble: `--scope production` filters on provenance, so a
# production file whose entry was written by an `examples/` copy was dropped
# from a production-scope scan entirely. See LEDGER N112. The bump also
# invalidates every v4 entry, which was written under the unsound key.
# v6: cache keys carry the SCOPE the entry was written under. Until 2026-08-17
# `_cache_put` refused to write at all on a `--min-tier` scan, which is correct
# about completeness and had a consequence nobody had measured: `regula check`
# passes `min_tier='limited_risk'`, so **the documented command read the cache
# and never filled it**. Measured on open-webui/open-webui at 01f4282, 5,031
# files: three consecutive `regula check .` runs left the cache at 2 bytes and
# the third took 40.7s, while one bare `regula` wrote 59,079 bytes and the next
# `check` took 4.0s. A user who runs the documented command first pays the cold
# cost on every run, forever (LEDGER N147).
#
# The scope component fixes the class rather than special-casing `check`. A
# partial scan now writes under `mintier-<level>`, so it contributes what it
# actually read; a full scan writes and reads `full` only, so **no full scan can
# ever be served an entry a partial scan wrote**. A partial reader still prefers
# a `full` entry when one exists, because a complete entry is a superset and the
# read path already filters it by tier, which is why `check` after a full scan
# stays fast.
#
# MIGRATION: nothing is migrated. The bump invalidates every v5 entry, so the
# first run after upgrade is a cold scan. That is the same treatment v4 to v5
# received for the same reason: an entry written under an unsound key cannot be
# distinguished from a sound one after the fact.
#
# v7: cache keys carry a SCAN-PARAMETER token. `respect_ignores`, the flag
# behind `regula check --no-ignore`, is threaded into `_parse_suppression_rules`
# and `_scan_agent_autonomy`, so it decides whether a finding is emitted with
# `suppressed: True`. It was not in the key, so both settings shared one entry.
# MEASURED 2026-08-17 on an isolated fixture, one variable moving:
#
#   A. cold cache, --no-ignore   suppressed=False   exit 1   <- correct
#   B. cold cache, default       suppressed=True    exit 0   <- correct
#   C. B's cache,  --no-ignore   suppressed=True    exit 0   <- WRONG
#
# C is a silent false negative on the one command whose purpose is to disregard
# the annotation. The reverse order is a false positive: a `# regula-ignore` the
# user wrote is disregarded and nothing in the output says why. Both directions
# are asserted in tests/test_scan_cache.py. See LEDGER N163.
#
# The token is a separate component rather than more text inside `context` for
# the reason `path_context` is separate: a key can then be read back and
# attributed, and a caller that forgets it produces a visibly different key
# rather than a silently colliding one. Which parameters belong in it, and why
# each of the others does not, is enumerated in `report.CACHE_KEY_SCAN_PARAMS`
# and `report.CACHE_EXEMPT_SCAN_PARAMS` and guarded by a test that reads
# `scan_files`' real signature, so a parameter added later cannot be forgotten
# the way this one was.
#
# MIGRATION: nothing is migrated, for the same reason as every bump above.
_CACHE_SCHEMA = f"v7:{_REGULA_VERSION}:{_patterns_fingerprint()}"

# The scope of a complete scan. Named rather than spelled inline so a caller
# cannot invent a second spelling of it.
FULL_SCOPE = "full"


class ScanCache:
    def __init__(self, cache_dir: Optional[Path] = None):
        # REGULA_CACHE_DIR was already the documented override for the feed
        # cache (scripts/feed.py) but the scan cache ignored it, so the only
        # way to isolate a scan was to move HOME wholesale. MEASURED
        # 2026-08-15: with a warm ambient cache the bundled fixture reported a
        # detector priority of 63 and with a cold one it reported 43, on the
        # same bytes and the same command, because cache keys carry the path
        # RELATIVE to the scan root while provenance is derived from the full
        # path. Honouring the variable here lets a check run on a cold cache
        # and is why scripts/verify_transcripts.py can be deterministic. The
        # key itself is fixed separately, by the v5 path-context component
        # above; this variable remains the way to isolate a scan outright.
        env_dir = os.environ.get("REGULA_CACHE_DIR")
        self._cache_dir = (
            cache_dir
            or (Path(env_dir) if env_dir else Path.home() / ".regula" / "cache")
        )
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory: dict = {}
        self._load()

    def _cache_file(self) -> Path:
        return self._cache_dir / "scan_cache.json"

    def _load(self) -> None:
        cf = self._cache_file()
        if cf.exists():
            try:
                self._memory = json.loads(cf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._memory = {}

    @staticmethod
    def _hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _key(path: str, content_hash: str, context: str, path_context: str,
             scope: str = FULL_SCOPE, params: str = "") -> str:
        """Build a cache key.

        `path_context` carries every classification input derived from the
        FULL path (see report.path_context_token). It is a separate component
        rather than being folded into `context` so that a key can be read back
        and attributed, and so a caller that forgets it produces a visibly
        different key rather than a silently colliding one.

        `scope` records how complete the entry is: `full` for a scan that ran
        every detector pass, `mintier-<level>` for one that did not. It is a key
        component rather than a stored field because a reader must be unable to
        obtain a partial entry by accident, and a field would leave that to the
        caller remembering to check it.

        `params` carries every remaining scan parameter that changes what the
        entry CONTAINS rather than which files are visited (see
        report.scan_params_token). `scope` already covers `min_tier`; this
        covers the rest. LEDGER N163.
        """
        return (f"{path}:{_CACHE_SCHEMA}:{context}:{path_context}:"
                f"{scope}:{params}:{content_hash}")

    def get(self, path: str, content: str, context: str = "",
            path_context: str = "", scopes: tuple = (FULL_SCOPE,),
            params: str = "") -> Optional[list]:
        """First hit across `scopes`, in the order given.

        A partial reader passes `(FULL_SCOPE, "mintier-N")` so that a complete
        entry is preferred and its own narrower entry is the fallback: the read
        path filters a complete entry down by tier, so a superset is always a
        safe answer. A full scan passes `(FULL_SCOPE,)` and can therefore never
        receive an entry some partial scan wrote.

        `params` is NOT varied across the fallback. Scope fallback is sound
        because a complete entry is a superset of a partial one; a differently
        parameterised entry is not a superset of anything, it is a different
        answer, so the only safe response to a miss is a rescan.
        """
        content_hash = self._hash(content)
        for scope in scopes:
            hit = self._memory.get(
                self._key(path, content_hash, context, path_context, scope,
                          params))
            if hit is not None:
                return hit
        return None

    def put(self, path: str, content: str, findings: list, context: str = "",
            path_context: str = "", scope: str = FULL_SCOPE,
            params: str = "") -> None:
        self._memory[
            self._key(path, self._hash(content), context, path_context, scope,
                      params)
        ] = findings

    def flush(self) -> None:
        cf = self._cache_file()
        cf.write_text(json.dumps(self._memory), encoding="utf-8")
