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


def _isolated_scan(monkeypatch, tmp_path):
    """Route scan_files' cache to an isolated dir and return scan_files."""
    import report
    from scan_cache import ScanCache
    cache_dir = tmp_path / "cache"

    class _IsolatedCache(ScanCache):
        def __init__(self):
            super().__init__(cache_dir=cache_dir)

    monkeypatch.setattr(report, "ScanCache", _IsolatedCache)
    return report.scan_files


def test_min_tier_scan_does_not_poison_cache(monkeypatch, tmp_path):
    """A --min-tier scan must not write cache entries: it skips whole
    detector passes, so its per-file findings lists are incomplete and
    would silently under-report on every later full scan of the same
    content. Regression for the v3-schema leak."""
    scan_files = _isolated_scan(monkeypatch, tmp_path)
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "app.py").write_text(
        "import openai\nimport langchain\n"
        "from langchain.chat_models import ChatOpenAI\n"
        "chatbot = ChatOpenAI(model='gpt-4')\n"
        "response = chatbot.predict('hello user')\n",
        encoding="utf-8",
    )
    full_first = scan_files(str(proj))
    baseline = {(f["file"], f["tier"], f["line"]) for f in full_first}

    proj2 = tmp_path / "proj2"
    proj2.mkdir()
    (proj2 / "app.py").write_text((proj / "app.py").read_text(), encoding="utf-8")
    scan_files(str(proj2), min_tier="prohibited")           # partial scan
    full_after = scan_files(str(proj2))                     # full scan, same content
    got = {(f["file"], f["tier"], f["line"]) for f in full_after}
    assert got == baseline, (
        f"full scan after a --min-tier scan lost findings: {baseline - got}"
    )


def test_domain_gated_finding_survives_cache(monkeypatch, tmp_path):
    """A plain scan gates opt-in employment findings; a later scan with
    the domain declared must still surface them ON A CACHE HIT. The
    entry must therefore store the finding ungated (read path re-gates)."""
    import shutil as _sh
    scan_files = _isolated_scan(monkeypatch, tmp_path)
    proj = tmp_path / "proj"
    proj.mkdir()
    repo = Path(__file__).resolve().parent.parent
    _sh.copy(repo / "scripts" / "demos" / "cv_screening_app.py", proj / "app.py")

    plain = scan_files(str(proj))
    assert sum(1 for f in plain if f["tier"] == "high_risk") == 0, \
        "employment finding should be domain-gated on a plain scan"

    stats = getattr(scan_files, "last_stats", {})
    assert stats.get("domain_gated_count", 0) >= 1, "gating should be counted"

    with_domain = scan_files(str(proj), declared_domains={"employment"})
    assert sum(1 for f in with_domain if f["tier"] == "high_risk") >= 1, \
        "declared domain must recover the gated finding from the cache"


def test_cache_context_isolates_entries():
    """Entries written under one scan context (AI-library self-scan caps
    confidence scores) must be invisible to the other context."""
    from scan_cache import ScanCache
    tmp = Path(tempfile.mkdtemp())
    try:
        cache = ScanCache(cache_dir=tmp)
        cache.put("x.py", "content", [{"tier": "high_risk"}], context="lib")
        assert cache.get("x.py", "content", context="lib") == [{"tier": "high_risk"}]
        assert cache.get("x.py", "content", context="app") is None
        print("  PASS  test_cache_context_isolates_entries")
    finally:
        shutil.rmtree(tmp)
