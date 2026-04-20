# regula-ignore
"""Content-hash scan caching for Regula.

Caches scan results keyed by SHA-256 of file content.
Unchanged files skip re-scanning on subsequent runs.
"""
import hashlib
import json
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


_CACHE_SCHEMA = f"v3:{_REGULA_VERSION}:{_patterns_fingerprint()}"


class ScanCache:
    def __init__(self, cache_dir: Optional[Path] = None):
        self._cache_dir = cache_dir or Path.home() / ".regula" / "cache"
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

    def get(self, path: str, content: str) -> Optional[list]:
        key = f"{path}:{_CACHE_SCHEMA}:{self._hash(content)}"
        return self._memory.get(key)

    def put(self, path: str, content: str, findings: list) -> None:
        key = f"{path}:{_CACHE_SCHEMA}:{self._hash(content)}"
        self._memory[key] = findings

    def flush(self) -> None:
        cf = self._cache_file()
        cf.write_text(json.dumps(self._memory), encoding="utf-8")
