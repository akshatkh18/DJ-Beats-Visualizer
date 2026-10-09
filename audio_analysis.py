"""Bounded, in-memory audio decoding and the studio's Librosa analysis."""

from io import BytesIO
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

MAX_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_SECONDS = 180
SAMPLE_RATE = 22050
HOP_LENGTH = 512


def read_audio(data: bytes, filename: str):
    """Decode only the analysis window; never create an uploaded temporary file."""
    if Path(filename).suffix.lower() not in {".mp3", ".wav"}:
        raise ValueError("Choose an MP3 or WAV file.")
    if not data:
        raise ValueError("This file is empty. Choose another track.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Choose a file smaller than 50 MB.")
    try:
        with sf.SoundFile(BytesIO(data)) as source:
            if source.format not in {"MP3", "WAV", "WAVEX", "RF64"}:
                raise ValueError("The file contents must be MP3 or WAV audio.")
            if not 8000 <= source.samplerate <= 192000 or source.channels > 8:
                raise ValueError("Use audio at 8–192 kHz with up to 8 channels.")
            source_rate = source.samplerate
            duration = source.frames / source_rate
            # PCM is mixed a second at a time to bound multichannel allocations.
            # Read MP3 in one bounded call: repeated reads can trigger libsndfile
            # decoder seeks and corrupt the bit reservoir on some bundled builds.
            chunks = []
            remaining = MAX_SECONDS * source_rate
            block_size = remaining if source.format == "MP3" else source_rate
            while remaining > 0:
                block = source.read(min(block_size, remaining), dtype="float32", always_2d=True)
                if not len(block):
                    break
                chunks.append(block.mean(axis=1))
                remaining -= len(block)
    except (sf.SoundFileError, EOFError) as exc:
        raise ValueError("Couldn't decode this file. Try another MP3 or WAV, or re-export it.") from exc
    if not chunks:
        raise ValueError("This file contains no audio samples.")
    audio = np.concatenate(chunks)
    if not np.isfinite(audio).all():
        raise ValueError("This file contains invalid audio samples. Re-export it and try again.")
    audio = librosa.resample(audio, orig_sr=source_rate, target_sr=SAMPLE_RATE)
    return audio, SAMPLE_RATE, duration


def analyze(audio, sample_rate):
    """Return tempo, beats, RMS energy and a descriptive (not genre) heuristic."""
    # Short clips still have a useful energy plot, but not a reliable tempo.
    duration = len(audio) / sample_rate
    audio = np.pad(audio, (0, max(0, 2048 - len(audio))))
    rms = librosa.feature.rms(y=audio, hop_length=HOP_LENGTH)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sample_rate, hop_length=HOP_LENGTH)
    valid = times < duration
    rms, times = rms[valid], times[valid]
    silent = float(np.max(np.abs(audio))) < 1e-5
    if silent or duration < 2:
        return 0.0, np.array([]), times, rms, "Silent" if silent else "Short clip"
    tempo, frames = librosa.beat.beat_track(y=audio, sr=sample_rate, hop_length=HOP_LENGTH)
    bpm = float(np.asarray(tempo).reshape(-1)[0])
    beats = librosa.frames_to_time(frames, sr=sample_rate, hop_length=HOP_LENGTH)
    beats = beats[beats < duration]
    if not len(beats):
        return 0.0, beats, times, rms, "No clear beat"
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sample_rate)))
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
    if bpm > 140 and centroid > 3000:
        mood = "High energy"
    elif bpm < 90 and zcr < .05:
        mood = "Laid back"
    elif 90 <= bpm <= 120:
        mood = "Mid-tempo"
    else:
        mood = "Rhythmic"
    return bpm, beats, times, rms, mood
