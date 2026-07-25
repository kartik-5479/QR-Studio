import json
import base64
from pathlib import Path

import streamlit as st

from components.sidebar import render_sidebar
from utils.ui import load_css, set_video_background


BATCH_GALLERY_PATH = Path("output/qr_codes/latest_batch_preview")
SINGLE_GALLERY_PATH = Path("output/qr_codes/single")
METADATA_PATH = Path("output/qr_codes/latest_batch_metadata.json")


def get_batch_count(batch_files):
    if METADATA_PATH.exists():
        try:
            metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
            return int(metadata.get("generated_count", len(batch_files)))
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            return len(batch_files)

    return len(batch_files)


def get_gallery_files():
    single_files = sorted(SINGLE_GALLERY_PATH.glob("*.png")) if SINGLE_GALLERY_PATH.exists() else []
    batch_files = sorted(BATCH_GALLERY_PATH.glob("*.png")) if BATCH_GALLERY_PATH.exists() else []
    return single_files, batch_files


def update_batch_count_after_delete(deleted_path):
    if BATCH_GALLERY_PATH not in deleted_path.parents or not METADATA_PATH.exists():
        return

    try:
        metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        current_count = int(metadata.get("generated_count", 0))
        metadata["generated_count"] = max(0, current_count - 1)
        METADATA_PATH.write_text(json.dumps(metadata), encoding="utf-8")
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return


def delete_gallery_file(image_path):
    try:
        image_path.unlink()
        update_batch_count_after_delete(image_path)
        st.toast(f"Deleted {image_path.stem}")
        st.rerun()
    except OSError as exc:
        st.error(f"Could not delete {image_path.name}: {exc}")


def render_gallery_image(image_bytes, alt_text):
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    st.markdown(
        f"""
<div class="gallery-image-frame">
    <img src="data:image/png;base64,{encoded_image}" alt="{alt_text}">
</div>
""",
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Gallery", page_icon="🖼️", layout="wide")

load_css()
set_video_background()
render_sidebar("gallery")

single_files, batch_files = get_gallery_files()
image_files = single_files + batch_files
total_count = len(single_files) + get_batch_count(batch_files)

st.markdown(
    """
<section class="page-header gallery-header">
    <div class="page-title-row">
        <span class="page-title-icon">QR</span>
        <h1>Gallery</h1>
    </div>
</section>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<section class="count-card">
    <span>Total QR Codes</span>
    <strong>{total_count}</strong>
</section>
""",
    unsafe_allow_html=True,
)

outer_left, outer_center, outer_right = st.columns([1, 10, 1])

with outer_center:
    if not image_files:
        st.info("No QR codes available yet. Generate a QR code or batch first.")
        st.stop()

    columns = st.columns(3)

    for index, image_path in enumerate(image_files):
        with columns[index % 3]:
            image_bytes = image_path.read_bytes()

            with st.container(border=True):
                render_gallery_image(image_bytes, image_path.stem)
                st.markdown(
                    f"<p class='gallery-item-title'>{image_path.stem}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="gallery-actions">', unsafe_allow_html=True)
                download_col, delete_col = st.columns(2, gap="small")

                with download_col:
                    st.download_button(
                        "Download",
                        data=image_bytes,
                        file_name=image_path.name,
                        mime="image/png",
                        key=f"download_{image_path.parent.name}_{image_path.stem}_{index}",
                        use_container_width=True,
                    )

                with delete_col:
                    if st.button(
                        "Delete",
                        key=f"delete_{image_path.parent.name}_{image_path.stem}_{index}",
                        use_container_width=True,
                    ):
                        delete_gallery_file(image_path)
                st.markdown("</div>", unsafe_allow_html=True)
