import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import tempfile
import os
import plotly.graph_objects as go
import time

# Set page config
st.set_page_config(page_title="🎧 AI DJ Visualizer", layout="wide")
st.title("🎵 AI DJ Visualizer")

# Theme selector
theme = st.selectbox(
    "🎨 Choose Your Visual Theme",
    ["Default", "Night Mode", "Retro"]
)

# Upload section
st.header("Upload Your Jam")
uploaded_file = st.file_uploader("Choose an audio file (.mp3 or .wav)", type=["mp3", "wav"])

# Load audio from upload
def load_audio(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    try:
        y, sr = librosa.load(tmp_path)
        return y, sr
    finally:
        os.unlink(tmp_path)

# Analyze tempo and beat
def analyse_music(y, sr):
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return float(np.asarray(tempo).reshape(-1)[0]), beat_times

# Genre guess + matching gif
def guess_genre(y, sr):
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(np.asarray(tempo).reshape(-1)[0])

    if tempo > 140 and spectral_centroid > 3000:
        return "EDM / Techno", "assets/edm.gif"
    elif tempo < 90 and zcr < 0.05:
        return "Chill / Ambient", "assets/chill.gif"
    elif 90 < tempo < 120:
        return "Pop / R&B", "assets/pop.gif"
    else:
        return "Hip-Hop / Trap", "assets/hiphop.gif"

# Get background + line colors
def get_theme_colors(theme):
    if theme == "Night Mode":
        return "#1a1a1a", "cyan"
    elif theme == "Retro":
        return "#f7f3e3", "#ff5c5c"
    else:
        return "white", "purple"

# Beat visualizer
def visualize_beats(beat_times, theme):
    bg_color, line_color = get_theme_colors(theme)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=beat_times,
        y=np.sin(2 * np.pi * beat_times),
        mode='lines+markers',
        line=dict(color=line_color, width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        xaxis_title='Time (s)',
        yaxis_title='Beat Pulse',
        title='🟣 Beat Visualizer',
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=line_color),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# Main app logic
if uploaded_file:
    st.audio(uploaded_file)

    y, sr = load_audio(uploaded_file)
    tempo, beat_times = analyse_music(y, sr)

    st.success(f"🎶 Tempo Detected: {round(float(tempo))} BPM")
    st.write(f"🟢 Total Beats Detected: {len(beat_times)}")

    genre, gif_path = guess_genre(y, sr)
    st.info(f"🎧 Genre Guess: **{genre}**")

    st.image(gif_path, use_column_width=True)

    st.write("💃 Live Beat Visualizer below!")
    visualize_beats(beat_times, theme)

    st.write("---")
    st.subheader("🔥 Rate the Beat")

    if 'votes' not in st.session_state:
        st.session_state.votes = {"🔥 Slaps": 0, "😐 Not Vibe": 0}

    col1, col2 = st.columns(2)

    if col1.button("🔥 This Beat Slaps"):
        st.session_state.votes["🔥 Slaps"] += 1

    if col2.button("😐 Not Feeling It"):
        st.session_state.votes["😐 Not Vibe"] += 1

    st.write("🗳️ Current Vote Count:")
    st.write(st.session_state.votes)
