import streamlit as st
from rembg import remove
from PIL import Image
import io
import os

# App config
st.set_page_config(page_title="Image Background Remover", layout="centered")
st.title("🖼️ Remove Image Background")
st.markdown("Upload an image and download it with transparent background.")

# Create folder to save uploads
UPLOAD_FOLDER = "uploaded_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Upload image
uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save uploaded image
    input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    image = Image.open(input_path)
    st.image(image, caption="Original Image", use_container_width=True)

    with st.spinner("Removing background..."):
        result = remove(image)

    st.success("✅ Background removed!")
    st.image(result, caption="Transparent Background", use_container_width=True)

    # Prepare download
    buffer = io.BytesIO()
    result.save(buffer, format="PNG")
    buffer.seek(0)

    st.download_button(
        label="📥 Download Transparent Image",
        data=buffer,
        file_name="no_background.png",
        mime="image/png"
    )

    # Optional: show saved files
    st.write("📂 Uploaded images this session:")
    st.write(os.listdir(UPLOAD_FOLDER))

st.markdown("---")
st.caption("Made with ❤️ using Streamlit and rembg")
