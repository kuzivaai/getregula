# regula-ignore
"""Content-hash scan caching for Regula.

Caches scan results keyed by SHA-256 of file content.
Unchanged files skip re-scanning on subsequent runs.
"""
import hashlib
import json
from pathlib import Path
from typing import Optional


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
        key = f"{path}:{self._hash(content)}"
        return self._memory.get(key)

    def put(self, path: str, content: str, findings: list) -> None:
        key = f"{path}:{self._hash(content)}"
        self._memory[key] = findings

    def flush(self) -> None:
        cf = self._cache_file()
        cf.write_text(json.dumps(self._memory), encoding="utf-8")
