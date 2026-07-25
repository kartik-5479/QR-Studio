import streamlit as st

from components.sidebar import render_sidebar
from utils.ui import load_css, set_video_background


st.set_page_config(
    page_title="QR Studio",
    page_icon="QR",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
set_video_background("assets/videos/ai_logo_background.mp4")
render_sidebar("home")

st.markdown(
    """
<style>
.home-action-panel ~ div[data-testid="stHorizontalBlock"] .stButton > button {
    height: 58px !important;
    min-height: 58px !important;
    border-radius: 14px !important;
    border: none !important;
    background: linear-gradient(135deg, #dc2626, #ef4444) !important;
    color: #000000 !important;
    font-size: 24px !important;
    font-weight: 900 !important;
    line-height: 1.1 !important;
    text-shadow: none !important;
    box-shadow: 0 12px 28px rgba(239, 68, 68, .34) !important;
}

.home-action-panel ~ div[data-testid="stHorizontalBlock"] .stButton > button *,
.home-action-panel ~ div[data-testid="stHorizontalBlock"] .stButton > button p,
.home-action-panel ~ div[data-testid="stHorizontalBlock"] .stButton > button span {
    color: #000000 !important;
    font-size: 24px !important;
    font-weight: 900 !important;
    line-height: 1.1 !important;
    text-shadow: none !important;
}

.home-action-panel ~ div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    transform: translateY(-2px);
    background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
    box-shadow: 0 16px 32px rgba(239, 68, 68, .42) !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<section class="page-header">
    <div class="page-title-row">
        <span class="page-title-icon">QR</span>
        <h1>QR Studio</h1>
    </div>
</section>
<p class="page-subtitle">Generate, customize, and download professional QR codes.</p>
""",
    unsafe_allow_html=True,
)

left, center, right = st.columns([1, 3, 1])

with center:
    with st.container(border=True):
        st.markdown('<div class="home-action-panel">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate QR", key="home_generate_qr", use_container_width=True):
                st.switch_page("pages/qr_generator.py")

        with col2:
            if st.button("Batch Generator", key="home_batch_generator", use_container_width=True):
                st.switch_page("pages/batch_generator.py")

        col3, col4, col5 = st.columns([1, 2, 1])

        with col4:
            if st.button("Gallery", key="home_gallery", use_container_width=True):
                st.switch_page("pages/gallery.py")
        st.markdown("</div>", unsafe_allow_html=True)
