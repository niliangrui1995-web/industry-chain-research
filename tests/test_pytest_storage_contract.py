from __future__ import annotations

import os
import tempfile
from pathlib import Path

from conftest import PYTEST_TEMP_ROOT


def test_pytest_process_temp_is_isolated_under_training_root(tmp_path: Path) -> None:
    expected_session = (PYTEST_TEMP_ROOT / f"pytest-{os.getpid()}").resolve()
    assert tmp_path.resolve().is_relative_to(expected_session)
    assert Path(tempfile.gettempdir()).resolve() == expected_session
    for name in ("TEMP", "TMP", "TMPDIR"):
        assert Path(os.environ[name]).resolve() == expected_session
