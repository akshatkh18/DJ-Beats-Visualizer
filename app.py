"""DJ Beats — audio analysis and visual exploration."""

import hashlib
import logging

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from audio_analysis import analyze, read_audio

st.set_page_config(page_title="DJ Beats | Music visualizer", page_icon=":material/graphic_eq:", layout="wide", initial_sidebar_state="collapsed")

PALETTES = {
    "Electric lime": ("#d7ff5f", "#91a945"),
    "Soft violet": ("#bb9bff", "#7865c9"),
    "Coral": ("#ff9478", "#d26a61"),
    "Ice blue": ("#7edcf0", "#4b9cb5"),
}

st.markdown("""
<style>

:root { color-scheme: dark; }
html, body, [data-testid="stApp"] { background: #0d0e11; color: #f4f2ed; font-family: "Segoe UI", sans-serif; }
.block-container { max-width: 1150px; padding-top: 1.5rem; padding-bottom: 2rem; }
[data-testid="stHeader"] { background: transparent; }
h1,h2,h3 { font-family: "Segoe UI", sans-serif; letter-spacing: -.045em; }
h1 { font-size: clamp(2.5rem, 5vw, 4.25rem) !important; line-height: 1.04 !important; font-weight: 600 !important; margin: .25rem 0 1rem !important; }
h2 { font-size: 1.55rem !important; }
p { color: #aaaab1; }
[data-testid="stFileUploader"] { background: #17181d; border: 1px dashed #4b4d55; border-radius: 15px; padding: 1rem; }
[data-testid="stFileUploader"] section { background: transparent; }
[data-testid="stFileUploader"] button { background: #d7ff5f; color: #101113; border: 0; border-radius: 7px; }
[data-testid="stSelectbox"] > div > div { background: #1c1d22; color: #f4f2ed; border-color: #3b3c44; }
[data-testid="stMetric"] { background: #17181d; border: 1px solid #303137; border-radius: 12px; padding: 1.1rem 1.25rem; }
[data-testid="stMetricLabel"] { color: #9b9ba5; }
[data-testid="stMetricValue"] { font-family: "Segoe UI",sans-serif; color: #f4f2ed; }
[data-testid="stAudio"] { border-radius: 10px; }
hr { border-color: #303137; }
.nav { display:flex; justify-content:space-between; align-items:center; padding: 0 0 1.6rem; border-bottom: 1px solid #292a30; margin-bottom: 2.5rem; }
.wordmark { color:#f4f2ed; font: 700 1.35rem "Segoe UI",sans-serif; letter-spacing:-.055em; }
.wordmark i { display:inline-block; width:14px; height:14px; background:#d7ff5f; border-radius:50%; margin-right:9px; }
.nav-right { font-size:.76rem; color:#8f9099; letter-spacing:.11em; text-transform:uppercase; }
.eyebrow { color:#d7ff5f; font-size:.75rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; margin-bottom:1rem; }
.hero-copy { color:#a9aab2; max-width:560px; font-size:1.08rem; line-height:1.8; margin-bottom:1rem; }
.highlight { color:#d7ff5f; }
.section-tag { color:#85858f; font-size:.76rem; letter-spacing:.16em; text-transform:uppercase; margin-top:1rem; margin-bottom:.8rem; }
.panel-note { color:#8e8e97; font-size:.83rem; margin-top:.4rem; }
.footer-note { margin-top:2rem; padding-top:1.5rem; border-top:1px solid #292a30; color:#777781; font-size:.8rem; }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-color: #303137; border-radius: 14px; }
[data-testid="stPlotlyChart"] { border: 1px solid #303137; border-radius: 14px; overflow: hidden; }
[data-testid="stMetricValue"] { font-size: clamp(1.35rem, 2.8vw, 2rem); }
[data-testid="stCaptionContainer"] p { color: #a6a7b0; }
button:focus-visible, input:focus-visible { outline: 2px solid #d7ff5f !important; outline-offset: 3px; }
@media (max-width: 640px) {
    .block-container { padding: 3rem 1rem 2rem; }
    .nav { margin-bottom: 1.75rem; gap: 1rem; }
    .nav-right { max-width: 100px; text-align: right; font-size: .65rem; }
    .hero-copy { font-size: .95rem; line-height: 1.6; }
    [data-testid="stFileUploader"] { padding: .5rem; }
    [data-testid="stMetric"] { padding: .8rem 1rem; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="nav"><div class="wordmark"><i></i>dj beats<span style="color:#8d8e97"> / studio</span></div><div class="nav-right">Audio analysis studio</div></div>', unsafe_allow_html=True)
st.markdown('<div class="eyebrow">Rhythm / energy / detail</div>', unsafe_allow_html=True)
st.markdown('<h1>A closer look<br>at <span class="highlight">your sound.</span></h1>', unsafe_allow_html=True)
st.markdown('<div class="hero-copy">Upload a track. Find its tempo, trace the energy, and explore the beats.</div>', unsafe_allow_html=True)


def chart(x, y, beats, style, accent, secondary):
    fig = go.Figure()
    rgb = tuple(int(accent[i:i+2], 16) for i in (1, 3, 5))
    fill = f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.12)"
    if style == "Energy curve":
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", fill="tozeroy", line=dict(color=accent, width=2.5), fillcolor=fill, hovertemplate="%{x:.1f}s · %{y:.3f}<extra></extra>"))
    elif style == "Pulse bars":
        stride = max(1, int(np.ceil(len(x) / 110)))
        fig.add_trace(go.Bar(x=x[::stride], y=y[::stride], marker_color=accent, marker_line_width=0, hovertemplate="%{x:.1f}s · %{y:.3f}<extra></extra>"))
    else:
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=secondary, width=2), hovertemplate="%{x:.1f}s · %{y:.3f}<extra></extra>"))
        if len(beats):
            indices = np.clip(np.searchsorted(x, beats), 0, len(x)-1)
            fig.add_trace(go.Scatter(x=x[indices], y=y[indices], mode="markers", marker=dict(color=accent, size=6), name="Detected beats", hovertemplate="Beat at %{x:.1f}s<extra></extra>"))
    fig.update_layout(height=370, margin=dict(l=64, r=24, t=28, b=56), paper_bgcolor="#17181d", plot_bgcolor="#17181d", font=dict(color="#9697a1", family="Segoe UI, sans-serif"), showlegend=False, xaxis=dict(title="Time (seconds)", showgrid=False, zeroline=False, linecolor="#44464e"), yaxis=dict(title="RMS energy", rangemode="tozero", showgrid=True, gridcolor="#292a30", zeroline=False), hovermode="x unified", bargap=.22)
    return fig


left, right = st.columns([1.5, 1], gap="large")
with left:
    st.markdown('<div class="section-tag">01 / Your track</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload MP3 or WAV", type=["mp3", "wav"], label_visibility="collapsed", key="track")
    st.markdown('<div class="panel-note">MP3 or WAV · Up to 50 MB · First 3 minutes analyzed</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="section-tag">02 / Visualization controls</div>', unsafe_allow_html=True)
    palette_name = st.selectbox("Color palette", list(PALETTES))
    style = st.selectbox("Visualization", ["Energy curve", "Pulse bars", "Beat markers"])

if uploaded is not None:
    data = uploaded.getvalue()
    fingerprint = hashlib.sha256(data).hexdigest()
    previous = st.session_state.get("analysis")
    if previous is None or previous["fingerprint"] != fingerprint:
        st.session_state.pop("analysis", None)
        try:
            with st.spinner("Finding the rhythm… The first analysis may take a moment."):
                audio, sr, source_duration = read_audio(data, uploaded.name)
                result = analyze(audio, sr)
                st.session_state["analysis"] = {
                    "fingerprint": fingerprint, "result": result,
                    "duration": len(audio) / sr, "source_duration": source_duration,
                }
                del audio
        except ValueError as exc:
            st.error(str(exc))
            st.stop()
        except Exception:
            logging.getLogger(__name__).exception("Audio analysis failed")
            st.error("Analysis couldn't finish. Try a shorter track or reload the page.")
            st.stop()
    current = st.session_state["analysis"]
    bpm, beats, times, rms, mood = current["result"]
    st.markdown('<div class="section-tag">03 / Playback & analysis</div>', unsafe_allow_html=True)
    st.audio(data, format="audio/mpeg" if uploaded.name.lower().endswith(".mp3") else "audio/wav")
    st.caption(f"Analyzed {current['duration']:.1f} seconds · Playback includes the full track.")
    if current["source_duration"] > 180:
        st.info("This track is longer than 3 minutes. The analysis covers its first 3 minutes.")
    a, b, c = st.columns(3)
    a.metric("Tempo", f"{bpm:.0f} BPM" if bpm else "Not detected")
    b.metric("Detected beats", f"{len(beats):,}")
    c.metric("Character", mood)
    st.caption("Tempo is an estimate; half- or double-time results are possible. Character is a simple audio heuristic, not a genre prediction.")
    accent, secondary = PALETTES[palette_name]
    st.markdown('<div class="section-tag">04 / Energy over time</div>', unsafe_allow_html=True)
    st.plotly_chart(chart(times, rms, beats, style, accent, secondary), use_container_width=True, theme=None, config={"displaylogo": False, "responsive": True, "scrollZoom": False})
    st.caption("The chart shows analyzed audio energy, not a live animation synchronized to playback.")
else:
    st.session_state.pop("analysis", None)
    st.markdown('<div class="section-tag">03 / Preview</div>', unsafe_allow_html=True)
    x = np.linspace(0, 30, 400)
    y = .07 + .035*np.sin(x*1.7)**2 + .065*np.exp(-((x-15)/6)**2)*np.sin(x*4)**2
    accent, secondary = PALETTES[palette_name]
    st.plotly_chart(chart(x, y, np.arange(.5, 30, .5), style, accent, secondary), use_container_width=True, theme=None, config={"displaylogo": False, "responsive": True, "scrollZoom": False})
    st.caption("Preview with sample data. Upload a track to see its analysis.")

st.markdown('<div class="footer-note">DJ Beats Studio · Audio is processed on the server in memory. Removing a track clears its saved analysis from this session.</div>', unsafe_allow_html=True)
