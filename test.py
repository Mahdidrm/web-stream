import streamlit as st
from rembg import remove
from PIL import Image
import io

st.set_page_config(page_title="Image Background Remover", layout="centered")

st.title("🖼️ Remove Image Background")
st.markdown("Upload an image and download the version with a transparent background (PNG).")

uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_column_width=True)

    with st.spinner("Removing background..."):
        result = remove(image)
    
    st.success("✅ Background removed!")
    st.image(result, caption="Image without Background", use_column_width=True)

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

st.markdown("---")
st.caption("Made with ❤️ using Streamlit and rembg")
