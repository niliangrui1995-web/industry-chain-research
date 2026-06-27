from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SecurityHardeningTests(unittest.TestCase):
    def test_safe_zip_rejects_path_escape(self) -> None:
        module = load_module(
            "test_safe_zip_docx",
            ROOT / "skills" / "docx" / "scripts" / "office" / "safe_zip.py",
        )
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "bad.docx"
            out_dir = Path(tmp) / "out"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("../evil.txt", "x")

            with zipfile.ZipFile(archive, "r") as zf:
                with self.assertRaises(module.UnsafeZipError):
                    module.safe_extractall(zf, out_dir)

    def test_safe_zip_rejects_uncompressed_size_budget(self) -> None:
        module = load_module(
            "test_safe_zip_xlsx",
            ROOT / "skills" / "xlsx" / "scripts" / "office" / "safe_zip.py",
        )
        module.MAX_ZIP_TOTAL_BYTES = 8
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "large.xlsx"
            out_dir = Path(tmp) / "out"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("xl/workbook.xml", "0123456789")

            with zipfile.ZipFile(archive, "r") as zf:
                with self.assertRaises(module.UnsafeZipError):
                    module.safe_extractall(zf, out_dir)

    def test_webcast_fetcher_rejects_non_http_scheme(self) -> None:
        module = load_module(
            "webcast_asset_fetcher_for_test",
            ROOT
            / "skills"
            / "earnings-call-investment-analyst"
            / "scripts"
            / "webcast_asset_fetcher.py",
        )

        with self.assertRaises(ValueError):
            module.fetch_bytes("file:///tmp/local.html", "test")

    def test_audio_transcriber_rejects_non_http_scheme(self) -> None:
        module = load_module(
            "audio_transcriber_for_test",
            ROOT
            / "skills"
            / "earnings-call-investment-analyst"
            / "scripts"
            / "audio_transcriber.py",
        )

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                module.download_url("file:///tmp/local.mp3", Path(tmp), "test", 1)


if __name__ == "__main__":
    unittest.main()
