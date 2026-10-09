# DJ Beats Visualizer

A Streamlit studio for exploring the rhythm and energy of an MP3 or WAV track.

## Features

- Full-track audio playback; Librosa tempo and beat detection.
- Three interactive RMS energy views: Energy curve, Pulse bars, Beat markers.
- Four chart palettes: Electric lime, Soft violet, Coral, Ice blue.
- Charcoal interface with responsive controls and analysis panels.
- A simple tempo/spectral character heuristic, not an AI genre classifier.

Charts are static analysis views, not animations synchronized to playback. Tempo
estimates can be half/double the perceived tempo. Silence and clips under two
seconds show no tempo. The empty state uses clearly labeled synthetic data.

## Run locally

Use **Python 3.13**, the tested runtime.

```sh
git clone https://github.com/akshatkh18/DJ-Beats-Visualizer.git
cd DJ-Beats-Visualizer
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` on Windows PowerShell, or
`source .venv/bin/activate` on macOS/Linux. Then, from the repository root:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the URL Streamlit prints (normally http://localhost:8501). The first analysis
may take longer while numerical routines initialize.

## Streamlit Community Cloud

1. Push these files to GitHub or merge the production-readiness PR.
2. Create an app at [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select this repository, the branch containing these changes, and **app.py**.
4. Select **Python 3.13** in advanced settings and deploy.

The root `requirements.txt` pins direct dependencies. `.streamlit/config.toml`
supplies the dark theme and a 50 MB upload limit. No secrets or API keys are needed.
Standard SoundFile Windows/Linux wheels bundle libsndfile with MP3 support;
FFmpeg and a `packages.txt` are not required when using these wheels.

## Limits and data handling

- MP3/WAV, up to 50 MB, 8–192 kHz, and up to eight channels.
- Analysis covers the first **180 seconds**, mixed to mono at 22,050 Hz.
- Decoding happens in memory. The app creates **no temporary upload files**.
- Only the latest analysis is saved in each user's Streamlit session. Changing
  chart controls reuses it; removing/replacing the upload clears/replaces it.
- No shared audio cache or database. Streamlit holds uploaded audio and playback
  data in server memory for its session/media lifecycle. Processing is not browser-only.

## Files

```text
app.py                     Streamlit interface and Plotly charts
audio_analysis.py          Validated decoding and Librosa analysis
requirements.txt           Pinned runtime dependencies
.streamlit/config.toml     Theme and upload configuration
tests/test_audio.py        Generated WAV/MP3 and edge-case regression tests
tests/test_app.py          Streamlit rendering and palette/style checks
```

## Checks

```sh
python -m pip check
python -m compileall -q app.py audio_analysis.py tests
python -m unittest discover -s tests -v
```

Tests generate their audio in memory; no sample downloads are needed. Browser checks
should cover desktop/mobile layout, upload, playback, control changes, and removing
a track. The test suite does not replace a deployment smoke test.
