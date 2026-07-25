from io import BytesIO
from datetime import datetime
from pathlib import Path
import re

import qrcode
import segno
import streamlit as st
from PIL import Image, ImageDraw
from qrcode.constants import (
    ERROR_CORRECT_H,
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
)

from components.sidebar import render_sidebar
from utils.ui import load_css, set_video_background


SINGLE_QR_GALLERY_DIR = Path("output/qr_codes/single")


def safe_filename(value, fallback):
    name = str(value).strip() or fallback
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", name)
    name = re.sub(r"\s+", "_", name)
    return name[:60].strip("._-") or fallback


def generate_qr_image(data, foreground, background, error_level):
    qr = qrcode.QRCode(
        version=1,
        error_correction={
            "L": ERROR_CORRECT_L,
            "M": ERROR_CORRECT_M,
            "Q": ERROR_CORRECT_Q,
            "H": ERROR_CORRECT_H,
        }[error_level],
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    return qr.make_image(
        fill_color=foreground,
        back_color=background,
    ).get_image().convert("RGBA")


def save_qr_to_gallery(image, data):
    SINGLE_QR_GALLERY_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = safe_filename(data, f"qr_code_{timestamp}")
    output_path = SINGLE_QR_GALLERY_DIR / f"{base_name}.png"

    counter = 2
    while output_path.exists():
        output_path = SINGLE_QR_GALLERY_DIR / f"{base_name}_{counter}.png"
        counter += 1

    image.save(output_path, format="PNG")
    return output_path


st.set_page_config(
    page_title="QR Generator",
    page_icon="QR",
    layout="wide",
)

load_css()
set_video_background()
render_sidebar("qr")

st.markdown(
    """
<section class="page-header">
    <div class="page-title-row">
        <span class="page-title-icon">QR</span>
        <h1>QR Generator</h1>
    </div>
</section>
<p class="page-subtitle">Create beautiful, customizable QR codes in seconds.</p>
""",
    unsafe_allow_html=True,
)

outer_left, outer_center, outer_right = st.columns([1, 10, 1])

with outer_center:
    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                """
<div class="section-title-card">
    <span class="section-title-icon">QR</span>
    <h2>QR Settings</h2>
</div>
""",
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="card-caption">Customize your QR code before generating it.</p>',
                unsafe_allow_html=True,
            )
            st.divider()

            qr_data = st.text_area(
                "Enter Text or URL",
                placeholder="https://example.com",
                height=120,
            )

            with st.expander("Colors", expanded=True):
                foreground = st.color_picker("QR Colour", "#000000")
                background = st.color_picker("Background Colour", "#FFFFFF")

            with st.expander("Logo", expanded=False):
                logo_file = st.file_uploader(
                    "Upload Logo (Optional)",
                    type=["png", "jpg", "jpeg"],
                )
                logo_scale = st.slider(
                    "Logo Size (%)",
                    min_value=10,
                    max_value=35,
                    value=25,
                )

            with st.expander("Advanced", expanded=False):
                error_level = st.selectbox(
                    "Error Correction",
                    ["L", "M", "Q", "H"],
                    index=3,
                )

            generate = st.button("Generate QR", use_container_width=True)

    with right:
        with st.container(border=True):
            st.markdown(
                """
<div class="section-title-card">
    <span class="section-title-icon">QR</span>
    <h2>Preview</h2>
</div>
""",
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="card-caption">Preview and download your generated QR code.</p>',
                unsafe_allow_html=True,
            )
            st.divider()

            if not generate:
                st.info("Generate a QR code to see the preview here.")

            if generate:
                if qr_data.strip() == "":
                    st.warning("Please enter some text or a URL.")
                else:
                    img = generate_qr_image(
                        qr_data,
                        foreground,
                        background,
                        error_level,
                    )

                    svg_buffer = BytesIO()
                    svg_qr = segno.make(qr_data, error=error_level.lower())
                    svg_qr.save(
                        svg_buffer,
                        kind="svg",
                        scale=10,
                        xmldecl=False,
                    )
                    svg_data = svg_buffer.getvalue()

                    if logo_file is not None:
                        logo = Image.open(logo_file).convert("RGBA")
                        logo_size = int(img.size[0] * logo_scale / 100)
                        logo = logo.resize(
                            (logo_size, logo_size),
                            Image.Resampling.LANCZOS,
                        )

                        position = (
                            (img.size[0] - logo_size) // 2,
                            (img.size[1] - logo_size) // 2,
                        )

                        padding = 12
                        badge_size = logo_size + padding * 2
                        background_box = Image.new(
                            "RGBA",
                            (badge_size, badge_size),
                            (255, 255, 255, 0),
                        )

                        draw = ImageDraw.Draw(background_box)
                        draw.rounded_rectangle(
                            [(0, 0), (badge_size, badge_size)],
                            radius=badge_size // 5,
                            fill=(255, 255, 255, 255),
                        )

                        bg_position = (
                            position[0] - padding,
                            position[1] - padding,
                        )

                        img.paste(background_box, bg_position)
                        img.paste(logo, position, logo)

                    gallery_path = save_qr_to_gallery(img, qr_data)
                    st.success(f"QR Code generated successfully and saved to Gallery as {gallery_path.name}")

                    col1, col2, col3 = st.columns([1, 2, 1])

                    with col2:
                        st.image(img, use_container_width=True)

                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    buffer.seek(0)
                    st.divider()

                    info1, info2, info3 = st.columns(3)

                    with info1:
                        st.metric("Format", "PNG")

                    with info2:
                        st.metric("Resolution", f"{img.size[0]} px")

                    with info3:
                        st.metric("Logo", "Yes" if logo_file else "No")

                    st.divider()

                    btn1, btn2 = st.columns(2)

                    with btn1:
                        st.download_button(
                            "PNG",
                            data=buffer,
                            file_name="qr_code.png",
                            mime="image/png",
                            use_container_width=True,
                        )

                    with btn2:
                        st.download_button(
                            "SVG",
                            data=svg_data,
                            file_name="qr_code.svg",
                            mime="image/svg+xml",
                            use_container_width=True,
                        )
