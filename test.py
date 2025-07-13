import streamlit as st
from rembg import remove
from PIL import Image
import io
import os

# App config
st.set_page_config(page_title="Image Background Remover", layout="centered")

# Header
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 0.3em;
    }
    .description {
        font-size: 1.1em;
        color: #555;
        margin-bottom: 1.5em;
    }
    .footer {
        color: #888;
        font-size: 0.9em;
        margin-top: 3em;
        text-align: center;
    }
    </style>
    <div class="main-title">Image Background Remover</div>
    <div class="description">Upload an image to get a transparent-background version in seconds.</div>
    """,
    unsafe_allow_html=True
)

# Upload folder setup
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Upload section
uploaded_file = st.file_uploader("Select an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save image
    input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    image = Image.open(input_path)

    # Display original
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original")
        st.image(image, use_container_width=True)

    # Process
    with st.spinner("Removing background..."):
        output_image = remove(image)

    with col2:
        st.subheader("Without Background")
        st.image(output_image, use_container_width=True)

    # Download
    buffer = io.BytesIO()
    output_image.save(buffer, format="PNG")
    buffer.seek(0)

    st.download_button(
        label="Download Transparent Image",
        data=buffer,
        file_name="no_background.png",
        mime="image/png",
        type="primary"
    )

# Footer
st.markdown(
    """<div class="footer">Built with ❤️ using Streamlit & rembg | 2025</div>""",
    unsafe_allow_html=True
)
