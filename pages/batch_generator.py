from io import BytesIO
import json
from pathlib import Path
import re
import zipfile

import pandas as pd
import qrcode
import streamlit as st
from qrcode.constants import (
    ERROR_CORRECT_H,
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
)

from components.sidebar import render_sidebar
from utils.ui import load_css, set_video_background


ERROR_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}

OUTPUT_DIR = Path("output/qr_codes")
LATEST_ZIP_PATH = OUTPUT_DIR / "latest_batch_qr_codes.zip"
LATEST_PREVIEW_DIR = OUTPUT_DIR / "latest_batch_preview"
LATEST_METADATA_PATH = OUTPUT_DIR / "latest_batch_metadata.json"


def safe_filename(value, fallback):
    name = str(value).strip() or fallback
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", name)
    name = re.sub(r"\s+", "_", name)
    return name[:80].strip("._-") or fallback


def generate_qr_png(data, foreground, background, error_level):
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_LEVELS[error_level],
        box_size=10,
        border=4,
    )
    qr.add_data(str(data))
    qr.make(fit=True)

    qr_image = qr.make_image(
        fill_color=foreground,
        back_color=background,
    )
    image = qr_image.get_image().convert("RGB")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def make_sample_csv():
    sample_df = pd.DataFrame(
        {
            "Name": ["Google", "YouTube", "OpenAI"],
            "Data": [
                "https://google.com",
                "https://youtube.com",
                "https://openai.com",
            ],
        }
    )
    return sample_df.to_csv(index=False).encode("utf-8")


def load_saved_batch_output():
    if "batch_zip_bytes" in st.session_state:
        return

    if not LATEST_ZIP_PATH.exists():
        return

    previews = []
    if LATEST_PREVIEW_DIR.exists():
        for path in sorted(LATEST_PREVIEW_DIR.glob("*.png"))[:3]:
            previews.append((path.name, path.read_bytes()))

    generated_count = len(previews)
    if LATEST_METADATA_PATH.exists():
        try:
            metadata = json.loads(LATEST_METADATA_PATH.read_text(encoding="utf-8"))
            generated_count = int(metadata.get("generated_count", generated_count))
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            generated_count = len(previews)

    st.session_state.batch_zip_bytes = LATEST_ZIP_PATH.read_bytes()
    st.session_state.batch_preview_images = previews
    st.session_state.batch_generated_count = generated_count


def save_batch_output(zip_bytes, previews, generated_count):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    LATEST_ZIP_PATH.write_bytes(zip_bytes)
    LATEST_METADATA_PATH.write_text(
        json.dumps({"generated_count": generated_count}),
        encoding="utf-8",
    )

    for old_preview in LATEST_PREVIEW_DIR.glob("*.png"):
        old_preview.unlink()

    for filename, image_bytes in previews:
        (LATEST_PREVIEW_DIR / safe_filename(filename, "preview.png")).write_bytes(image_bytes)

    st.session_state.batch_zip_bytes = zip_bytes
    st.session_state.batch_preview_images = previews
    st.session_state.batch_generated_count = generated_count


def render_batch_output():
    zip_bytes = st.session_state.get("batch_zip_bytes")
    previews = st.session_state.get("batch_preview_images", [])
    generated_count = st.session_state.get("batch_generated_count", 0)

    if not zip_bytes:
        st.info("Click Generate ZIP when your settings are ready.")
        return

    st.success(f"{generated_count} QR codes are ready.")
    st.download_button(
        "Download QR ZIP",
        data=zip_bytes,
        file_name="batch_qr_codes.zip",
        mime="application/zip",
        use_container_width=True,
    )

    if previews:
        st.divider()
        st.markdown("### Preview")
        preview_columns = st.columns(len(previews))
        for column, (filename, image_bytes) in zip(preview_columns, previews):
            with column:
                st.image(image_bytes, caption=Path(filename).stem)


st.set_page_config(
    page_title="Batch Generator",
    page_icon="📦",
    layout="wide",
)

load_css()
set_video_background()
render_sidebar("batch")
load_saved_batch_output()

st.markdown(
    """
<section class="page-header">
    <div class="page-title-row">
        <span class="page-title-icon">CSV</span>
        <h1>Batch QR Generator</h1>
    </div>
</section>
<p class="page-subtitle">Generate many QR codes from one CSV file.</p>
""",
    unsafe_allow_html=True,
)

outer_left, outer_center, outer_right = st.columns([1, 10, 1])

with outer_center:
    generate_all = False
    left, right = st.columns([1, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(
                """
<div class="section-title-card">
    <span class="section-title-icon">CSV</span>
    <h2>Upload CSV</h2>
</div>
""",
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="card-caption">Upload a CSV and choose which column should become QR data.</p>',
                unsafe_allow_html=True,
            )
            st.divider()

            csv_file = st.file_uploader("Choose a CSV file", type=["csv"])

            if csv_file is None:
                st.info("Upload a CSV file to start batch generation.")
                df = None
            else:
                try:
                    df = pd.read_csv(csv_file)
                except Exception as exc:
                    st.error(f"Could not read this CSV file: {exc}")
                    df = None

            if df is not None:
                df = df.dropna(how="all")
                if df.empty:
                    st.error("The uploaded CSV does not contain any rows.")
                    df = None
                else:
                    st.success(f"Loaded {len(df)} rows and {len(df.columns)} columns.")
                    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

    with right:
        with st.container(border=True):
            st.markdown(
                """
<div class="section-title-card">
    <span class="section-title-icon">QR</span>
    <h2>Batch Settings</h2>
</div>
""",
                unsafe_allow_html=True,
            )
            st.markdown(
                '<p class="card-caption">Select columns, colors, and export options for the ZIP file.</p>',
                unsafe_allow_html=True,
            )
            st.divider()

            if df is None:
                st.download_button(
                    "Download Sample CSV",
                    data=make_sample_csv(),
                    file_name="sample_qr_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                columns = list(df.columns)
                default_data_index = columns.index("Data") if "Data" in columns else 0
                data_column = st.selectbox(
                    "QR Data Column",
                    columns,
                    index=default_data_index,
                )

                name_options = ["Use row number"] + columns
                default_name_index = name_options.index("Name") if "Name" in columns else 0
                name_column = st.selectbox(
                    "File Name Column",
                    name_options,
                    index=default_name_index,
                )

                foreground = st.color_picker("QR Colour", "#000000")
                background = st.color_picker("Background Colour", "#FFFFFF")
                error_level = st.selectbox(
                    "Error Correction",
                    ["L", "M", "Q", "H"],
                    index=3,
                )

                generate_all = st.button("Generate ZIP", use_container_width=True)

                st.download_button(
                    "Download Sample CSV",
                    data=make_sample_csv(),
                    file_name="sample_qr_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    with st.container(border=True):
        st.markdown(
            """
<div class="section-title-card">
    <span class="section-title-icon">ZIP</span>
    <h2>Output</h2>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="card-caption">Generate QR codes and download them together as one ZIP file.</p>',
            unsafe_allow_html=True,
        )
        st.divider()

        if not generate_all or df is None:
            render_batch_output()
        else:
            clean_df = df[df[data_column].notna()].copy()
            clean_df[data_column] = clean_df[data_column].astype(str).str.strip()
            clean_df = clean_df[clean_df[data_column] != ""]

            if clean_df.empty:
                st.error("No usable QR data was found in the selected column.")
                st.stop()

            zip_buffer = BytesIO()
            progress = st.progress(0)
            status = st.empty()
            previews = []
            used_names = set()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                total = len(clean_df)
                for position, (_, row) in enumerate(clean_df.iterrows(), start=1):
                    if name_column == "Use row number":
                        base_name = f"qr_code_{position}"
                    else:
                        base_name = safe_filename(row[name_column], f"qr_code_{position}")

                    filename = f"{base_name}.png"
                    counter = 2
                    while filename.lower() in used_names:
                        filename = f"{base_name}_{counter}.png"
                        counter += 1
                    used_names.add(filename.lower())

                    image_bytes = generate_qr_png(
                        row[data_column],
                        foreground,
                        background,
                        error_level,
                    )
                    zip_file.writestr(filename, image_bytes)

                    if len(previews) < 3:
                        previews.append((filename, image_bytes))

                    progress.progress(position / total)
                    status.write(f"Generated {position} of {total} QR codes")

            zip_buffer.seek(0)
            zip_bytes = zip_buffer.getvalue()
            save_batch_output(zip_bytes, previews, len(clean_df))
            status.success(f"Generated {len(clean_df)} QR codes successfully.")
            render_batch_output()
