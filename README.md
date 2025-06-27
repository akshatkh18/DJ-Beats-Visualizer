# 🎧 AI DJ Visualizer

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
![Built by Akshat](https://img.shields.io/badge/Built%20by-Akshat%20Gupta-blue)

A fun and interactive Streamlit web app that:
- 🌀 Visualizes the **tempo and beat structure** of uploaded songs
- 🎼 **Guesses the genre** using spectral features (like tempo, ZCR, etc.)
- 🕺 Shows **dancing GIFs** that change based on detected genre
- 🎨 Supports **Retro**, **Night Mode**, and **Default** visual themes
- 🔥 Lets users **vote** if the beat slaps or not

---

## 🚀 Features

- Upload `.mp3` or `.wav` file
- Detect tempo and total beat count
- Genre detection based on audio features
- Dynamic visualizer powered by Plotly
- Genre-specific dancing animations (GIFs)
- Light/Dark/Retro UI themes
- Voting panel (Slaps / Not Vibe)

---

## 🧠 Tech Stack

- [Streamlit](https://streamlit.io/)
- [Librosa](https://librosa.org/) for audio analysis
- [Plotly](https://plotly.com/python/) for visualizations
- Python (Backend + Visualization)

---

## 📁 Project Structure

<pre>
AI-DJ-Visualizer/
├── app.py
├── requirements.txt
├── README.md
└── assets/
    ├── edm.gif
    ├── chill.gif
    ├── hiphop.gif
    └── pop.gif
</pre>


## 🌐 Optional: Deployment

You can deploy this to [Streamlit Cloud](https://streamlit.io/cloud) with one click 👇

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)


---

## 🛠️ Installation

```bash
git clone https://github.com/akshatkh18/DJ-Beats-Visulaizer.git
cd DJ-Beats-Visualizer
pip install -r requirements.txt
streamlit run app.py
```
