"""Smoke tests for package import."""

import splinenorm


def test_version() -> None:
    assert splinenorm.__version__ == "0.1.0"
