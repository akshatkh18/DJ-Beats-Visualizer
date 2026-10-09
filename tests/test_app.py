import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from streamlit.testing.v1 import AppTest

from audio_analysis import analyze
from test_audio import encode


class AppTests(unittest.TestCase):
    def test_upload_rerun_and_removal(self):
        from io import BytesIO
        upload = BytesIO(encode(np.zeros(22050 * 3)))
        upload.name = "silence.wav"
        app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"))
        with patch("streamlit.file_uploader", return_value=upload), patch("audio_analysis.analyze", wraps=analyze) as run_analysis:
            app.run(timeout=180)
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, "Not detected")
            self.assertEqual(app.metric[2].value, "Silent")
            app.selectbox[0].select("Coral").run()
            self.assertFalse(app.exception)
            self.assertEqual(run_analysis.call_count, 1)
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)
        self.assertNotIn("analysis", app.session_state)

    def test_corrupt_upload_is_actionable(self):
        from io import BytesIO
        upload = BytesIO(b"not an audio file")
        upload.name = "broken.mp3"
        app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"))
        with patch("streamlit.file_uploader", return_value=upload):
            app.run(timeout=180)
        self.assertFalse(app.exception)
        self.assertIn("decode", app.error[0].value)

    def test_preview_styles_and_palettes(self):
        app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py")).run(timeout=180)
        self.assertFalse(app.exception)
        for palette in ("Electric lime", "Soft violet", "Coral", "Ice blue"):
            for style in ("Energy curve", "Pulse bars", "Beat markers"):
                with self.subTest(palette=palette, style=style):
                    app.selectbox[0].select(palette)
                    app.selectbox[1].select(style).run()
                    self.assertFalse(app.exception)
                    spec = json.loads(app.get("plotly_chart")[0].proto.spec)
                    self.assertEqual(spec["layout"]["paper_bgcolor"], "#17181d")
                    if style == "Beat markers":
                        self.assertEqual(len(spec["data"]), 2)
                    if palette == "Soft violet" and style == "Energy curve":
                        self.assertEqual(spec["data"][0]["fillcolor"], "rgba(187,155,255,0.12)")


if __name__ == "__main__":
    unittest.main()
