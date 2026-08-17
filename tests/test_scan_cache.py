#!/usr/bin/env python3
"""Tests for scan caching."""
import sys
import tempfile
import shutil
import time
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


def test_cache_key_isolates_by_path_context():
    """N112. Entries must not cross a full-path classification boundary.

    The key's path component is the path RELATIVE to the scan root, so two
    byte-identical files at the same relative path under different roots share
    it. Provenance and the example/init penalties come from the FULL path, so
    without a path-context component the entry written for one is served for
    the other.

    This asserts the isolation directly AND runs the negative control: with the
    component blanked, the same two lookups collide. Without that control the
    test could pass because nothing was ever cached.
    """
    from scan_cache import ScanCache
    tmp = Path(tempfile.mkdtemp())
    try:
        cache = ScanCache(cache_dir=tmp)
        entry = [{"tier": "high_risk", "provenance": "example"}]
        cache.put("app.py", "import openai", entry,
                  context="app", path_context="example|t0|e1|i0")

        assert cache.get("app.py", "import openai", context="app",
                         path_context="example|t0|e1|i0") == entry, \
            "an entry must still be readable under its own path context"

        assert cache.get("app.py", "import openai", context="app",
                         path_context="production|t0|e0|i0") is None, (
            "a production file was served the cache entry of an examples copy "
            "at the same relative path. --scope production filters on "
            "provenance, so this drops a real finding from the scan.")

        # Negative control: the lookup that must miss above is the SAME lookup
        # that hits when the discriminator is removed. Proves the assertion
        # above is testing the key and not an empty cache.
        cache.put("app.py", "import openai", entry, context="app")
        assert cache.get("app.py", "import openai", context="app") == entry, \
            "control failed: the collision could not be reproduced, so the " \
            "assertion above proves nothing"
        print("  PASS  test_cache_key_isolates_by_path_context")
    finally:
        shutil.rmtree(tmp)


def test_path_context_token_separates_every_full_path_classifier():
    """The token must change whenever a full-path classifier changes.

    If a classifier is added to report.py and not to path_context_token, the
    cache silently serves results across the boundary that classifier draws.
    This pins the four that exist.
    """
    from report import path_context_token
    base = path_context_token(Path("/srv/app/api.py"))
    variants = {
        "example": Path("/srv/examples/api.py"),
        "test": Path("/srv/tests/api.py"),
        "init": Path("/srv/app/__init__.py"),
    }
    for label, p in variants.items():
        assert path_context_token(p) != base, (
            f"path_context_token does not distinguish a {label} file from a "
            f"production one, so their cache entries collide")
    assert len({path_context_token(p) for p in variants.values()} | {base}) == 4, \
        "two different full-path classifications produced the same token"
    print("  PASS  test_path_context_token_separates_every_full_path_classifier")


def test_provenance_survives_a_cache_warmed_by_an_examples_copy(monkeypatch, tmp_path):
    """N112, end to end: the defect that made a production finding vanish.

    A full scan (`regula report`, `evidence-pack`, `conform`) populates the
    cache; `regula check` passes min_tier='limited_risk' and so only ever READS
    it. Two byte-identical files, each the root of its own scan, therefore both
    key on 'app.py'. Before the fix the examples copy's entry was served to the
    production file, its provenance became "example", and a --scope production
    scan reported ZERO findings on a file that has one.
    """
    scan_files = _isolated_scan(monkeypatch, tmp_path)
    src = ("import openai\n"
           "client = openai.OpenAI(api_key='sk-test')\n"
           "def decide(applicant):\n"
           "    return client.chat.completions.create(\n"
           "        model='gpt-4',\n"
           "        messages=[{'role': 'user', 'content': applicant}])\n")

    # NOT pytest's tmp_path: it names the directory after the test function, so
    # every segment of the fixture path starts with "test_" and _is_test_file
    # classifies the whole tree as "test" provenance. The fixture would then
    # assert nothing about examples-versus-production. tmp_path is still used
    # for the isolated cache, where the directory name is irrelevant.
    root = Path(tempfile.mkdtemp(prefix="n112-"))
    try:
        demo = root / "examples" / "demoapp"
        prod = root / "plain"
        for d in (demo, prod):
            d.mkdir(parents=True)
            (d / "app.py").write_text(src, encoding="utf-8")

        # The examples copy warms the cache under the shared relative path.
        warm = scan_files(str(demo))
        assert warm and all(f.get("provenance") == "example" for f in warm), (
            f"fixture is wrong: the examples copy must produce findings and "
            f"they must classify as example, got "
            f"{[(f['file'], f.get('provenance')) for f in warm]}")

        after = scan_files(str(prod), skip_tests=True, min_tier="limited_risk")
        assert [f for f in after if f.get("provenance") == "production"], (
            "a production file's finding disappeared from a production-scope "
            "scan because the cache served an examples copy's entry (N112)")
        assert all(f.get("provenance") == "production" for f in after), (
            f"provenance was served from the wrong file: "
            f"{[(f['file'], f.get('provenance')) for f in after]}")
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_regula_cache_dir_env_var_is_honoured():
    """N112. The scan cache must be redirectable without moving HOME.

    `REGULA_CACHE_DIR` was already the documented override for the feed cache
    but the scan cache ignored it, so `scripts/verify_transcripts.py` set the
    variable, changed nothing, and shipped an isolation that was inert. The
    full suite caught it: the gate still failed. An override nobody honours is
    a blank gate, not a green one, so this asserts the variable actually moves
    the file rather than asserting it is merely accepted.
    """
    import os
    from scan_cache import ScanCache
    tmp = Path(tempfile.mkdtemp())
    previous = os.environ.get("REGULA_CACHE_DIR")
    try:
        os.environ["REGULA_CACHE_DIR"] = str(tmp)
        cache = ScanCache()
        assert cache._cache_dir == tmp, (
            f"REGULA_CACHE_DIR was ignored: cache dir is {cache._cache_dir}, "
            f"not {tmp}. A scan cannot then be isolated from the operator's "
            f"ambient cache, and any check that relies on it is inert.")
        # put() only updates memory; flush() persists. Asserting on the file
        # without flushing would have failed for the wrong reason and taught
        # nothing about the variable.
        cache.put("a.py", "import torch", [{"tier": "high_risk"}])
        cache.flush()
        assert (tmp / "scan_cache.json").exists(), \
            "the cache wrote somewhere other than the directory it reported"

        # An explicit argument still wins, so callers that pass a directory
        # are not silently overridden by an operator's environment.
        other = Path(tempfile.mkdtemp())
        try:
            assert ScanCache(cache_dir=other)._cache_dir == other, \
                "an explicit cache_dir must outrank the environment variable"
        finally:
            shutil.rmtree(other)
        print("  PASS  test_regula_cache_dir_env_var_is_honoured")
    finally:
        if previous is None:
            os.environ.pop("REGULA_CACHE_DIR", None)
        else:
            os.environ["REGULA_CACHE_DIR"] = previous
        shutil.rmtree(tmp)
