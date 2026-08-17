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
_CACHE_SCHEMA = f"v5:{_REGULA_VERSION}:{_patterns_fingerprint()}"


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
    def _key(path: str, content_hash: str, context: str, path_context: str) -> str:
        """Build a cache key.

        `path_context` carries every classification input derived from the
        FULL path (see report.path_context_token). It is a separate component
        rather than being folded into `context` so that a key can be read back
        and attributed, and so a caller that forgets it produces a visibly
        different key rather than a silently colliding one.
        """
        return f"{path}:{_CACHE_SCHEMA}:{context}:{path_context}:{content_hash}"

    def get(self, path: str, content: str, context: str = "",
            path_context: str = "") -> Optional[list]:
        return self._memory.get(
            self._key(path, self._hash(content), context, path_context))

    def put(self, path: str, content: str, findings: list, context: str = "",
            path_context: str = "") -> None:
        self._memory[
            self._key(path, self._hash(content), context, path_context)
        ] = findings

    def flush(self) -> None:
        cf = self._cache_file()
        cf.write_text(json.dumps(self._memory), encoding="utf-8")
