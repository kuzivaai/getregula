#!/usr/bin/env python3
"""Tests for scan caching."""
import sys, tempfile, shutil, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def test_cache_hit_skips_rescan():
    """Second scan of unchanged file returns cached result."""
    from scan_cache import ScanCache
    tmp = Path(tempfile.mkdtemp())
    try:
        cache = ScanCache(cache_dir=tmp)
        content = "import tensorflow; model.predict(data)"
        path = "test.py"
        assert cache.get(path, content) is None  # miss
        findings = [{"tier": "high_risk", "file": path}]
        cache.put(path, content, findings)
        assert cache.get(path, content) == findings  # hit
        assert cache.get(path, content + " # modified") is None  # miss on change
        print("  PASS  test_cache_hit_skips_rescan")
    finally:
        shutil.rmtree(tmp)

def test_cache_persistence():
    """Cache survives flush and reload."""
    from scan_cache import ScanCache
    tmp = Path(tempfile.mkdtemp())
    try:
        cache1 = ScanCache(cache_dir=tmp)
        cache1.put("a.py", "content", [{"tier": "info"}])
        cache1.flush()
        cache2 = ScanCache(cache_dir=tmp)
        assert cache2.get("a.py", "content") == [{"tier": "info"}]
        print("  PASS  test_cache_persistence")
    finally:
        shutil.rmtree(tmp)

def test_cache_performance():
    """Cache lookup is fast."""
    from scan_cache import ScanCache
    tmp = Path(tempfile.mkdtemp())
    try:
        cache = ScanCache(cache_dir=tmp)
        for i in range(100):
            cache.put(f"file_{i}.py", f"content_{i}", [{"tier": "info"}])
        start = time.time()
        for i in range(100):
            cache.get(f"file_{i}.py", f"content_{i}")
        elapsed = time.time() - start
        assert elapsed < 0.5, f"Too slow: {elapsed:.3f}s"
        print("  PASS  test_cache_performance")
    finally:
        shutil.rmtree(tmp)

if __name__ == "__main__":
    for t in [test_cache_hit_skips_rescan, test_cache_persistence, test_cache_performance]:
        try:
            t()
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
