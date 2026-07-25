import streamlit as st


NAV_ITEMS = [
    ("home", "Home", "app.py"),
    ("qr", "QR Generator", "pages/qr_generator.py"),
    ("batch", "Batch Generator", "pages/batch_generator.py"),
    ("gallery", "Gallery", "pages/gallery.py"),
]


def render_sidebar(active):
    with st.sidebar:
        st.markdown(
            """
<div class="sidebar-brand">
    <div class="sidebar-logo">QR</div>
    <div>
        <div class="sidebar-title">QR Studio</div>
        <div class="sidebar-subtitle">Professional QR Toolkit</div>
    </div>
</div>
<div class="sidebar-divider"></div>
<div class="sidebar-section-label">Navigation</div>
""",
            unsafe_allow_html=True,
        )

        for page_key, label, target in NAV_ITEMS:
            button_type = "primary" if page_key == active else "secondary"
            if st.button(
                label,
                key=f"sidebar_{page_key}",
                type=button_type,
                use_container_width=True,
                disabled=page_key == active,
            ):
                st.switch_page(target)
