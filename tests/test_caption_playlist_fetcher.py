from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents/skills/earnings-call-investment-analyst/scripts/caption_playlist_fetcher.py"
spec = importlib.util.spec_from_file_location("caption_playlist_completeness_tests", SCRIPT)
caption = importlib.util.module_from_spec(spec)
spec.loader.exec_module(caption)

PLAYLIST_URL = "https://captions.example.test/subtitles.m3u8"
VTT = "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nRevenue increased.\n"


class CaptionCompletenessTests(unittest.TestCase):
    def run_download(self, playlist, responses, **limits):
        def fetch(url, _user_agent, _max_bytes):
            if url == PLAYLIST_URL:
                return playlist
            response = responses[url.rsplit("/", 1)[-1]]
            if isinstance(response, Exception):
                raise response
            return response

        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            sys, "argv", [str(SCRIPT), "--playlist-url", PLAYLIST_URL, "--out-dir", tmp]
        ), mock.patch.object(caption, "fetch_text", side_effect=fetch), contextlib.redirect_stdout(io.StringIO()):
            with contextlib.ExitStack() as stack:
                for name, value in limits.items():
                    stack.enter_context(mock.patch.object(caption, name, value))
                result = caption.main()
            manifest = json.loads((Path(tmp) / "captions_manifest.json").read_text(encoding="utf-8"))
            return result, manifest

    def test_all_ended_segments_succeed(self):
        code, manifest = self.run_download(
            "#EXTM3U\n#EXTINF:1,\na.vtt\n#EXTINF:1,\nb.vtt\n#EXT-X-ENDLIST\n",
            {"a.vtt": VTT, "b.vtt": "\ufeffWEBVTT comment\n\n"},
        )
        self.assertEqual(code, 0)
        self.assertTrue(manifest["playlist_ended"])
        self.assertTrue(manifest["download_complete"])
        self.assertTrue(manifest["playlist_complete"])
        self.assertEqual(manifest["warning"], "")

    def test_missing_segment_cannot_publish_complete(self):
        code, manifest = self.run_download(
            "#EXTM3U\n#EXTINF:1,\na.vtt\n#EXTINF:1,\nb.vtt\n#EXT-X-ENDLIST\n",
            {"a.vtt": VTT, "b.vtt": OSError("upstream unavailable")},
        )
        self.assertEqual(code, 1)
        self.assertTrue(manifest["playlist_ended"])
        self.assertFalse(manifest["download_complete"])
        self.assertFalse(manifest["playlist_complete"])
        self.assertEqual(manifest["downloaded_count"], 1)
        self.assertIn("1/2", manifest["warning"])

    def test_live_window_returns_incomplete(self):
        code, manifest = self.run_download("#EXTM3U\n#EXTINF:1,\na.vtt\n", {"a.vtt": VTT})
        self.assertEqual(code, 1)
        self.assertFalse(manifest["playlist_complete"])
        self.assertTrue(manifest["download_complete"])
        self.assertIn("EXT-X-ENDLIST", manifest["warning"])

    def test_empty_ended_playlist_is_incomplete(self):
        code, manifest = self.run_download("#EXTM3U\n#EXT-X-ENDLIST\n", {})
        self.assertEqual(code, 1)
        self.assertFalse(manifest["playlist_complete"])
        self.assertFalse(manifest["download_complete"])

    def test_size_failure_is_incomplete(self):
        code, manifest = self.run_download(
            "#EXTM3U\n#EXTINF:1,\na.vtt\n#EXTINF:1,\nb.vtt\n#EXT-X-ENDLIST\n",
            {"a.vtt": VTT, "b.vtt": VTT}, MAX_TOTAL_SEGMENT_BYTES=len(VTT.encode("utf-8")),
        )
        self.assertEqual(code, 1)
        self.assertFalse(manifest["playlist_complete"])
        self.assertEqual(manifest["downloaded_count"], 1)

    def test_http_success_with_html_is_not_a_caption(self):
        code, manifest = self.run_download(
            "#EXTM3U\n#EXTINF:1,\na.vtt\n#EXT-X-ENDLIST\n", {"a.vtt": "<html>Access denied</html>"},
        )
        self.assertEqual(code, 1)
        self.assertFalse(manifest["download_complete"])
        self.assertEqual(manifest["downloaded_count"], 0)

    def test_endlist_substring_is_not_an_end_tag(self):
        code, manifest = self.run_download(
            "#EXTM3U\n#COMMENT:#EXT-X-ENDLIST\n#EXTINF:1,\na.vtt\n", {"a.vtt": VTT},
        )
        self.assertEqual(code, 1)
        self.assertFalse(manifest["playlist_complete"])

    def test_error_text_with_vtt_header_is_not_valid(self):
        code, manifest = self.run_download(
            "#EXTM3U\n#EXTINF:1,\na.vtt\n#EXT-X-ENDLIST\n",
            {"a.vtt": "WEBVTT\n\nupstream request failed\n"},
        )
        self.assertEqual(code, 1)
        self.assertFalse(manifest["download_complete"])

    def test_malformed_playlist_is_incomplete(self):
        for playlist in (
            "#EXTINF:1,\na.vtt\n#EXT-X-ENDLIST\n",
            "#EXTM3U\n#EXTINF:NaN,\na.vtt\n#EXT-X-ENDLIST\n",
            "#EXTM3U\n#EXTINF:-1,\na.vtt\n#EXT-X-ENDLIST\n",
            "#EXTM3U\na.vtt\n#EXT-X-ENDLIST\n",
            "#EXTM3U\n#EXTINF:1,\n#EXT-X-GAP\na.vtt\n#EXT-X-ENDLIST\n",
        ):
            with self.subTest(playlist=playlist):
                code, manifest = self.run_download(playlist, {"a.vtt": VTT})
                self.assertEqual(code, 1)
                self.assertFalse(manifest["playlist_complete"])


if __name__ == "__main__":
    unittest.main()
