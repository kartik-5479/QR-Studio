import streamlit as st
import base64


def load_css():
    with open("css/style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


def set_video_background(video_path="assets/videos/background.mp4"):
    with open(video_path, "rb") as video:
        video_base64 = base64.b64encode(video.read()).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{
            background: transparent !important;
        }}

        #bg-video {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            z-index: -1001;
        }}

        </style>

        <video autoplay muted loop playsinline id="bg-video">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
        """,
        unsafe_allow_html=True
    )