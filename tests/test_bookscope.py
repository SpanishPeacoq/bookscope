import os
import unittest
from unittest.mock import Mock, patch

from PIL import Image

import bookscope


class EnvMixin:
    def setUp(self):
        self._env_patcher = patch.dict(
            os.environ,
            {
                key: value
                for key, value in os.environ.items()
                if not key.startswith("BOOKSCOPE_") and key != "HF_TOKEN"
            },
            clear=True,
        )
        self._env_patcher.start()

    def tearDown(self):
        self._env_patcher.stop()


class ScanFlowTests(EnvMixin, unittest.TestCase):
    def test_default_live_failure_returns_empty_table_not_demo_rows(self):
        image = Image.new("RGB", (20, 20), "white")
        with patch.object(bookscope, "_call_hf_gradio_space", side_effect=RuntimeError("boom")):
            frame, status = bookscope.scan_shelf_image(image)

        self.assertTrue(frame.empty)
        self.assertIn("Live scan failed", status)

    def test_demo_mode_returns_demo_rows_only_when_enabled(self):
        os.environ["BOOKSCOPE_DEMO_MODE"] = "true"
        image = Image.new("RGB", (20, 20), "white")

        frame, status = bookscope.scan_shelf_image(image)

        self.assertFalse(frame.empty)
        self.assertEqual(set(frame["source"]), {"demo"})
        self.assertIn("Demo mode is active", status)

    def test_default_provider_uses_minicpm_gradio_space(self):
        image = Image.new("RGB", (20, 20), "white")
        with patch.object(bookscope, "_call_hf_gradio_space", return_value='{"books": []}') as gradio:
            bookscope.scan_shelf_image(image)

        gradio.assert_called_once()

    def test_explicit_hf_model_uses_inference_provider_path(self):
        os.environ["HF_TOKEN"] = "token"
        os.environ["BOOKSCOPE_HF_MODEL"] = "provider/model"

        self.assertFalse(bookscope._should_use_gradio_space())


class EnrichmentTests(EnvMixin, unittest.TestCase):
    def test_open_library_malformed_search_json_is_not_fatal(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.side_effect = ValueError("not json")

        with patch("bookscope.requests.get", return_value=response):
            self.assertIsNone(bookscope._open_library_match("Bad Body", "Unknown"))

    def test_open_library_malformed_editions_json_returns_no_isbn(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.side_effect = ValueError("not json")

        with patch("bookscope.requests.get", return_value=response):
            self.assertEqual(bookscope._isbn_from_editions("/works/OL1W"), "")


if __name__ == "__main__":
    unittest.main()
