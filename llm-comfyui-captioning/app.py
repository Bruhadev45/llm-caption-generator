# app.py

import streamlit as st
from captioning import generate_caption
from PIL import Image
import os

st.set_page_config(page_title="🧠 LLM Image Captioning", layout="wide")
st.title("🧠 LLM-Powered Image Caption Generator")
st.markdown("Upload one or more images to generate captions using the BLIP model.")

# Sidebar options
st.sidebar.header("⚙️ Options")
model_choice = st.sidebar.selectbox("Select BLIP Model Variant", ["base", "large"])
translate = st.sidebar.checkbox("Translate captions to Telugu (🇮🇳)", value=False)

# Upload multiple images
uploaded_files = st.file_uploader("📤 Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.divider()
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        # Save temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            caption = generate_caption(temp_path, model_size=model_choice)

            if translate:
                from googletrans import Translator
                translator = Translator()
                translation = translator.translate(caption, dest="te")
                caption = f"{caption} \n\n👉 **Telugu:** {translation.text}"

            st.success("📝 Generated Caption:")
            st.markdown(f"**{caption}**")

        except Exception as e:
            st.error(f"❌ Error: {e}")

        os.remove(temp_path)
