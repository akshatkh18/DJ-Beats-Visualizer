"""DJ Beats — audio analysis and visual exploration."""

import os
import tempfile
from pathlib import Path

import librosa
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="DJ Beats | Music visualizer", page_icon="◉", layout="wide", initial_sidebar_state="collapsed")

PALETTES = {
    "Electric lime": ("#d7ff5f", "#91a945"),
    "Soft violet": ("#bb9bff", "#7865c9"),
    "Coral": ("#ff9478", "#d26a61"),
    "Ice blue": ("#7edcf0", "#4b9cb5"),
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { color-scheme: dark; }
html, body, [data-testid="stApp"] { background: #0d0e11; color: #f4f2ed; font-family: 'DM Sans', sans-serif; }
.block-container { max-width: 1150px; padding-top: 1.5rem; padding-bottom: 5rem; }
[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer { display: none; }
h1,h2,h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -.045em; }
h1 { font-size: clamp(3rem, 7vw, 5.8rem) !important; line-height: 1.04 !important; font-weight: 600 !important; margin: .25rem 0 1rem !important; }
h2 { font-size: 1.55rem !important; }
p { color: #aaaab1; }
[data-testid="stFileUploader"] { background: #17181d; border: 1px dashed #4b4d55; border-radius: 15px; padding: 1rem; }
[data-testid="stFileUploader"] section { background: transparent; }
[data-testid="stFileUploader"] button { background: #d7ff5f; color: #101113; border: 0; border-radius: 7px; }
[data-testid="stSelectbox"] > div > div { background: #1c1d22; color: #f4f2ed; border-color: #3b3c44; }
[data-testid="stMetric"] { background: #17181d; border: 1px solid #303137; border-radius: 12px; padding: 1.1rem 1.25rem; }
[data-testid="stMetricLabel"] { color: #9b9ba5; }
[data-testid="stMetricValue"] { font-family: 'Space Grotesk',sans-serif; color: #f4f2ed; }
[data-testid="stAudio"] { border-radius: 10px; }
hr { border-color: #303137; }
.nav { display:flex; justify-content:space-between; align-items:center; padding: 0 0 1.6rem; border-bottom: 1px solid #292a30; margin-bottom: 4rem; }
.wordmark { color:#f4f2ed; font: 700 1.35rem 'Space Grotesk',sans-serif; letter-spacing:-.055em; }
.wordmark i { display:inline-block; width:14px; height:14px; background:#d7ff5f; border-radius:50%; margin-right:9px; }
.nav-right { font-size:.76rem; color:#8f9099; letter-spacing:.11em; text-transform:uppercase; }
.eyebrow { color:#d7ff5f; font-size:.75rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; margin-bottom:1rem; }
.hero-copy { color:#a9aab2; max-width:560px; font-size:1.08rem; line-height:1.8; margin-bottom:2.5rem; }
.highlight { color:#d7ff5f; }
.section-tag { color:#85858f; font-size:.76rem; letter-spacing:.16em; text-transform:uppercase; margin-top:2.5rem; margin-bottom:.8rem; }
.panel-note { color:#8e8e97; font-size:.83rem; margin-top:.4rem; }
.footer-note { margin-top:3rem; padding-top:1.5rem; border-top:1px solid #292a30; color:#777781; font-size:.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="nav"><div class="wordmark"><i></i>dj beats<span style="color:#8d8e97"> / studio</span></div><div class="nav-right">A little more than listening</div></div>', unsafe_allow_html=True)
st.markdown('<div class="eyebrow">Your sound, in focus</div>', unsafe_allow_html=True)
st.markdown('<h1>See what your<br><span class="highlight">music feels like.</span></h1>', unsafe_allow_html=True)
st.markdown('<div class="hero-copy">Drop in a track to explore its rhythm, energy and frequency. No account, no clutter — just a closer look at the music.</div>', unsafe_allow_html=True)


def read_audio(file):
    suffix = Path(file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as handle:
        handle.write(file.getvalue())
        path = handle.name
    try:
        audio, sample_rate = librosa.load(path, sr=22050, mono=True, duration=180)
    finally:
        os.unlink(path)
    if audio.size == 0:
        raise ValueError("The uploaded audio file is empty.")
    return audio, sample_rate


def analyze(audio, sample_rate):
    tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=sample_rate)
    bpm = float(np.asarray(tempo).reshape(-1)[0])
    beats = librosa.frames_to_time(beat_frames, sr=sample_rate)
    rms = librosa.feature.rms(y=audio)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sample_rate)
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=audio, sr=sample_rate)))
    zcr = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
    if bpm > 140 and centroid > 3000:
        mood = "High energy"
    elif bpm < 90 and zcr < .05:
        mood = "Laid back"
    elif 90 < bpm < 120:
        mood = "Mid-tempo"
    else:
        mood = "Rhythmic"
    return bpm, beats, rms_times, rms, mood


def chart(x, y, beats, style, accent, secondary):
    fig = go.Figure()
    if style == "Energy curve":
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", fill="tozeroy", line=dict(color=accent, width=2.5), fillcolor="rgba(215,255,95,0.10)", hovertemplate="%{x:.1f}s · %{y:.3f}<extra></extra>"))
    elif style == "Pulse bars":
        stride = max(1, len(x) // 110)
        fig.add_trace(go.Bar(x=x[::stride], y=y[::stride], marker_color=accent, marker_line_width=0, hovertemplate="%{x:.1f}s · %{y:.3f}<extra></extra>"))
    else:
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=secondary, width=2), hovertemplate="%{x:.1f}s · %{y:.3f}<extra></extra>"))
        if len(beats):
            indices = np.clip(np.searchsorted(x, beats), 0, len(x)-1)
            fig.add_trace(go.Scatter(x=x[indices], y=y[indices], mode="markers", marker=dict(color=accent, size=6), name="Detected beats", hovertemplate="Beat at %{x:.1f}s<extra></extra>"))
    fig.update_layout(height=370, margin=dict(l=8, r=8, t=18, b=20), paper_bgcolor="#17181d", plot_bgcolor="#17181d", font=dict(color="#9697a1", family="DM Sans"), showlegend=False, xaxis=dict(title="Time (seconds)", showgrid=False, zeroline=False, linecolor="#44464e"), yaxis=dict(title="Energy", showgrid=True, gridcolor="#292a30", zeroline=False), hovermode="x unified", bargap=.22)
    return fig


left, right = st.columns([1.5, 1], gap="large")
with left:
    st.markdown('<div class="section-tag">01 / Your track</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload MP3 or WAV", type=["mp3", "wav"], label_visibility="collapsed")
    st.markdown('<div class="panel-note">MP3 or WAV · First 3 minutes analyzed for responsiveness</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="section-tag">02 / Make it yours</div>', unsafe_allow_html=True)
    palette_name = st.selectbox("Color palette", list(PALETTES))
    style = st.selectbox("Visualization", ["Energy curve", "Pulse bars", "Beat markers"])

if uploaded is not None:
    try:
        with st.spinner("Reading your track…"):
            audio, sr = read_audio(uploaded)
            bpm, beats, times, rms, mood = analyze(audio, sr)
    except Exception:
        st.error("Couldn't read this audio file. Try a different MP3 or WAV.")
        st.stop()

    st.markdown('<div class="section-tag">03 / Playback & analysis</div>', unsafe_allow_html=True)
    st.audio(uploaded)
    a, b, c = st.columns(3)
    a.metric("Tempo", f"{bpm:.0f} BPM")
    b.metric("Detected beats", f"{len(beats):,}")
    c.metric("Character", mood)
    accent, secondary = PALETTES[palette_name]
    st.markdown('<div class="section-tag">04 / Energy over time</div>', unsafe_allow_html=True)
    st.plotly_chart(chart(times, rms, beats, style, accent, secondary), use_container_width=True, config={"displaylogo": False})
    st.caption("The chart shows analyzed audio energy, not a live animation synchronized to playback.")
else:
    st.markdown('<div class="section-tag">03 / Preview</div>', unsafe_allow_html=True)
    x = np.linspace(0, 30, 400)
    y = .07 + .035*np.sin(x*1.7)**2 + .065*np.exp(-((x-15)/6)**2)*np.sin(x*4)**2
    accent, secondary = PALETTES[palette_name]
    st.plotly_chart(chart(x, y, np.array([]), style, accent, secondary), use_container_width=True, config={"displaylogo": False})
    st.caption("Preview with sample data. Upload a track to see its analysis.")

st.markdown('<div class="footer-note">DJ Beats Studio · Built for curious listeners · Audio is analyzed during your session; no account required.</div>', unsafe_allow_html=True)
