# regula-ignore
"""Shared test helpers for Regula's custom test runner and pytest.

Every test file that uses assert_eq / assert_true / assert_false / assert_in
should import from here instead of duplicating the helpers.

Usage:
    from helpers import assert_eq, assert_true, assert_false, assert_in, assert_gte, assert_lte
"""
import sys

_PYTEST_MODE = "pytest" in sys.modules

passed = 0
failed = 0


def assert_eq(actual, expected, msg=""):
    global passed, failed
    if actual == expected:
        passed += 1
    else:
        failed += 1
        if _PYTEST_MODE:
            raise AssertionError(f"{msg} — expected {expected!r}, got {actual!r}")
        print(f"  FAIL: {msg} — expected {expected}, got {actual}")


def assert_true(val, msg=""):
    assert_eq(val, True, msg)


def assert_false(val, msg=""):
    assert_eq(val, False, msg)


def assert_in(item, collection, msg=""):
    global passed, failed
    if item in collection:
        passed += 1
    else:
        failed += 1
        if _PYTEST_MODE:
            raise AssertionError(f"{msg} — {item!r} not in {collection!r}")
        print(f"  FAIL: {msg} — {item!r} not in {collection!r}")


def assert_gte(actual, minimum, msg=""):
    global passed, failed
    if actual >= minimum:
        passed += 1
    else:
        failed += 1
        if _PYTEST_MODE:
            raise AssertionError(f"{msg} — {actual} < {minimum}")
        print(f"  FAIL: {msg} — {actual} < {minimum}")


def assert_none(val, msg=""):
    assert_eq(val, None, msg)


def assert_lte(actual, maximum, msg=""):
    global passed, failed
    if actual <= maximum:
        passed += 1
    else:
        failed += 1
        if _PYTEST_MODE:
            raise AssertionError(f"{msg} — {actual} > {maximum}")
        print(f"  FAIL: {msg} — {actual} > {maximum}")
