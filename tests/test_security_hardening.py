from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]

SAFE_ZIP_PATHS = [
    ROOT / "plugins" / "document-skills" / "skills" / "docx" / "scripts" / "office" / "safe_zip.py",
    ROOT / "plugins" / "document-skills" / "skills" / "pptx" / "scripts" / "office" / "safe_zip.py",
    ROOT / "plugins" / "document-skills" / "skills" / "xlsx" / "scripts" / "office" / "safe_zip.py",
]

SIMPLIFY_REDLINES_PATHS = [
    path.parent / "helpers" / "simplify_redlines.py"
    for path in SAFE_ZIP_PATHS
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_office_helper(name: str, path: Path):
    old_path = list(sys.path)
    sys.modules.pop("safe_zip", None)
    sys.path.insert(0, str(path.parents[1]))
    try:
        return load_module(name, path)
    finally:
        sys.path[:] = old_path
        sys.modules.pop("safe_zip", None)


class SecurityHardeningTests(unittest.TestCase):
    def test_safe_zip_rejects_path_escape_in_document_plugin(self) -> None:
        for index, path in enumerate(SAFE_ZIP_PATHS):
            with self.subTest(path=path):
                module = load_module(f"test_safe_zip_escape_{index}", path)
                with tempfile.TemporaryDirectory() as tmp:
                    archive = Path(tmp) / "bad.docx"
                    out_dir = Path(tmp) / "out"
                    with zipfile.ZipFile(archive, "w") as zf:
                        zf.writestr("../evil.txt", "x")

                    with zipfile.ZipFile(archive, "r") as zf:
                        with self.assertRaises(module.UnsafeZipError):
                            module.safe_extractall(zf, out_dir)

    def test_safe_zip_rejects_uncompressed_size_budget_in_document_plugin(self) -> None:
        for index, path in enumerate(SAFE_ZIP_PATHS):
            with self.subTest(path=path):
                module = load_module(f"test_safe_zip_size_{index}", path)
                module.MAX_ZIP_TOTAL_BYTES = 8
                with tempfile.TemporaryDirectory() as tmp:
                    archive = Path(tmp) / "large.xlsx"
                    out_dir = Path(tmp) / "out"
                    with zipfile.ZipFile(archive, "w") as zf:
                        zf.writestr("xl/workbook.xml", "0123456789")

                    with zipfile.ZipFile(archive, "r") as zf:
                        with self.assertRaises(module.UnsafeZipError):
                            module.safe_extractall(zf, out_dir)

    def test_redline_author_reader_rejects_oversized_document_xml_in_document_plugin(self) -> None:
        for index, path in enumerate(SIMPLIFY_REDLINES_PATHS):
            with self.subTest(path=path):
                module = load_office_helper(f"test_simplify_redlines_{index}", path)
                module.MAX_ZIP_MEMBER_BYTES = 4
                with tempfile.TemporaryDirectory() as tmp:
                    archive = Path(tmp) / "large.docx"
                    with zipfile.ZipFile(archive, "w") as zf:
                        zf.writestr("word/document.xml", "<w:document/>")

                    with self.assertRaises(module.UnsafeZipError):
                        module._get_authors_from_docx(archive)

    def test_webcast_fetcher_rejects_non_http_scheme(self) -> None:
        module = load_module(
            "webcast_asset_fetcher_for_test",
            ROOT
            / ".agents"
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
            / ".agents"
            / "skills"
            / "earnings-call-investment-analyst"
            / "scripts"
            / "audio_transcriber.py",
        )

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                module.download_url("file:///tmp/local.mp3", Path(tmp), "test", 1)

    def test_source_discovery_rejects_non_http_scheme(self) -> None:
        module = load_module(
            "source_discovery_for_scheme_test",
            ROOT
            / ".agents"
            / "skills"
            / "earnings-call-investment-analyst"
            / "scripts"
            / "source_discovery.py",
        )

        with self.assertRaises(ValueError):
            module.fetch_json("file:///tmp/company_tickers.json", "test")

    def test_source_discovery_rejects_oversized_json_without_content_length(self) -> None:
        module = load_module(
            "source_discovery_for_size_test",
            ROOT
            / ".agents"
            / "skills"
            / "earnings-call-investment-analyst"
            / "scripts"
            / "source_discovery.py",
        )

        class Response:
            headers: dict[str, str] = {}

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, _size: int) -> bytes:
                return b'{"ok": true}'

        with mock.patch.object(module.urllib.request, "urlopen", return_value=Response()):
            with self.assertRaises(ValueError):
                module.fetch_json("https://www.sec.gov/files/company_tickers.json", "test", max_bytes=4)

    def test_caption_playlist_rejects_total_segment_budget(self) -> None:
        module = load_module(
            "caption_playlist_fetcher_for_size_test",
            ROOT
            / ".agents"
            / "skills"
            / "earnings-call-investment-analyst"
            / "scripts"
            / "caption_playlist_fetcher.py",
        )
        module.MAX_TOTAL_SEGMENT_BYTES = 3

        with self.assertRaises(ValueError):
            module.checked_segment_size(2, "xx")


if __name__ == "__main__":
    unittest.main()
