"""Real codec/Librosa regressions; no external samples or test dependencies."""
from io import BytesIO
import unittest
from unittest.mock import patch

import librosa
import numpy as np
import soundfile as sf

from audio_analysis import MAX_SECONDS, SAMPLE_RATE, analyze, read_audio


def encode(audio, rate=SAMPLE_RATE, format="WAV", subtype=None):
    buffer = BytesIO()
    sf.write(buffer, audio, rate, format=format, subtype=subtype)
    return buffer.getvalue()


class AudioTests(unittest.TestCase):
    def test_wav_and_mp3_tempo(self):
        clicks = librosa.clicks(times=np.arange(.5, 12, .5), sr=SAMPLE_RATE,
                                length=12 * SAMPLE_RATE)
        for format in ("WAV", "MP3"):
            with self.subTest(format=format):
                data = encode(clicks, format=format)
                with patch("tempfile.NamedTemporaryFile", side_effect=AssertionError("disk upload")):
                    audio, rate, duration = read_audio(data, f"clicks.{format.lower()}")
                bpm, beats, times, energy, _ = analyze(audio, rate)
                self.assertAlmostEqual(duration, 12, delta=.2)
                self.assertAlmostEqual(bpm, 120, delta=4)
                self.assertGreater(len(beats), 18)
                self.assertTrue(np.all(np.diff(beats) > 0))
                self.assertLess(np.median(np.abs(np.diff(beats) - .5)), .03)
                self.assertEqual(len(times), len(energy))
                self.assertTrue(np.isfinite(energy).all())

    def test_stereo_resample_and_duration_limit(self):
        rate = 8000
        signal = np.zeros(((MAX_SECONDS + 1) * rate, 2), dtype=np.float32)
        audio, sr, duration = read_audio(encode(signal, rate), "long.WAV")
        self.assertEqual(sr, SAMPLE_RATE)
        self.assertEqual(audio.shape, (MAX_SECONDS * SAMPLE_RATE,))
        self.assertEqual(duration, MAX_SECONDS + 1)

    def test_silence_and_tiny_clip(self):
        for signal, label in ((np.zeros(SAMPLE_RATE * 3), "Silent"), (np.ones(10) * .1, "Short clip")):
            audio, sr, _ = read_audio(encode(signal), "sample.wav")
            bpm, beats, times, rms, mood = analyze(audio, sr)
            self.assertEqual(bpm, 0)
            self.assertEqual(len(beats), 0)
            self.assertEqual(mood, label)
            self.assertGreater(len(times), 0)
            self.assertTrue(np.isfinite(rms).all())

    def test_invalid_uploads(self):
        cases = [(b"", "empty.wav"), (b"garbage", "bad.mp3"),
                 (b"garbage", "bad.txt"), (encode(np.array([])), "empty.wav"),
                 (encode(np.zeros(100), format="FLAC"), "renamed.wav"),
                 (encode(np.array([np.nan, np.inf]), subtype="FLOAT"), "invalid.wav")]
        for data, name in cases:
            with self.subTest(name=name), self.assertRaises(ValueError):
                read_audio(data, name)
        with patch("audio_analysis.MAX_UPLOAD_BYTES", 2), self.assertRaises(ValueError):
            read_audio(b"123", "large.wav")


if __name__ == "__main__":
    unittest.main()
