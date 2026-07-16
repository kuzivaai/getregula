# regula-ignore
"""Shared pytest fixtures for the whole suite.

Audit-store isolation (P1 follow-up, 2026-07-16): no test may read from
or write to the operator's real audit store (~/.regula/audit). Before
this fixture existed, tests that exercised documentation generation and
pack surfaces appended real events to the machine store and created
per-project chain directories there (observed as tmp* chains and empty
projects/<slug>/ dirs in the live store). The autouse fixture below
points REGULA_AUDIT_DIR at a per-test temporary directory so the
default is never the real store. Tests that need a specific store
still override the variable themselves (their own fixtures/env run
after this one and win).
"""

import pytest


@pytest.fixture(autouse=True)
def _isolated_audit_store(tmp_path_factory, monkeypatch):
    root = tmp_path_factory.mktemp("audit-isolated")
    monkeypatch.setenv("REGULA_AUDIT_DIR", str(root))
    monkeypatch.delenv("REGULA_PROJECT_DIR", raising=False)
    monkeypatch.delenv("REGULA_PROJECT", raising=False)
    yield
