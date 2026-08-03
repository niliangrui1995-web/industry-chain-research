from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


PYTEST_TEMP_ROOT = Path(
    r"D:\vcp_hunter\产业链投研\_training\kronos_ashare\runtime\tmp\pytest-runs"
).resolve()


def _apply_process_temp_contract() -> Path:
    session_root = (PYTEST_TEMP_ROOT / f"pytest-{os.getpid()}").resolve()
    session_root.mkdir(parents=True, exist_ok=True)
    for name in ("TEMP", "TMP", "TMPDIR"):
        os.environ[name] = str(session_root)
    tempfile.tempdir = str(session_root)
    return session_root


def pytest_configure(config) -> None:
    """Keep every pytest process isolated on D:, including concurrent runs."""

    session_root = _apply_process_temp_contract()
    config.option.basetemp = session_root


@pytest.fixture(autouse=True)
def _restore_process_temp_between_tests():
    """Prevent a runtime-mapping test from leaking its temp root to later tests."""

    _apply_process_temp_contract()
    yield
    _apply_process_temp_contract()
