"""Stub suite: proves the test harness runs green from the first commit."""

import nadiloka


def test_package_imports():
    assert nadiloka.__doc__ is not None
