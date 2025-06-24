import streamlit as st
from captioning import generate_caption
from translator import translate_caption, LANGUAGES
from utils import save_uploaded_image, delete_temp_image
import torch

st.set_page_config(
    page_title="🧠 LLM Image Caption Generator",
    layout="wide",
    page_icon="🧠"
)

st.title("🧠 LLM-Powered Image Caption Generator")
st.caption("Generate intelligent image captions with BLIP and translate them to any language.")

# Sidebar options
st.sidebar.header("⚙️ Options")
st.sidebar.markdown(f"**Device:** {'GPU' if torch.cuda.is_available() else 'CPU'}")
model_choice = st.sidebar.selectbox("BLIP Model", ["base", "large"])
beam_size = st.sidebar.slider("Beam Width", 1, 10, 5)
show_time = st.sidebar.checkbox("Show captioning time", value=False)

# Translation options
st.sidebar.subheader("🌐 Translation")
enable_translation = st.sidebar.checkbox("Translate captions", value=False)
language_codes = sorted(LANGUAGES.keys())
language_names = [f"{LANGUAGES[code].capitalize()} ({code})" for code in language_codes]

if enable_translation:
    default_index = language_codes.index("en") if "en" in language_codes else 0
    target_lang_idx = st.sidebar.selectbox(
        "Choose language",
        options=list(range(len(language_names))),
        format_func=lambda i: language_names[i],
        index=default_index
    )
    target_lang_code = language_codes[target_lang_idx]
else:
    target_lang_code = None

# File uploader
st.markdown("#### 📤 Upload images")
uploaded_files = st.file_uploader(
    "Choose one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

def professional_card(image, original_caption, translated_caption=None, lang_name=None):
    cols = st.columns([1, 2])
    with cols[0]:
        st.image(image, caption="Uploaded Image", use_column_width=True)
    with cols[1]:
        st.markdown("**📝 Original Caption:**")
        st.success(original_caption)
        if translated_caption:
            st.markdown(f"**🌍 Translated ({lang_name}):**")
            st.info(translated_caption)

if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files):
        temp_path = save_uploaded_image(uploaded_file)

        try:
            with st.spinner("Generating caption..."):
                import time
                start = time.time()
                caption = generate_caption(temp_path, model_size=model_choice, beam_size=beam_size)
                elapsed = time.time() - start

            regenerate = st.button("🔄 Regenerate Caption", key=f"regen_{idx}")
            if regenerate:
                caption = generate_caption(temp_path, model_size=model_choice, beam_size=beam_size)

            if enable_translation and target_lang_code:
                with st.spinner(f"Translating to {LANGUAGES[target_lang_code].capitalize()}..."):
                    translated_caption = translate_caption(caption, dest_language=target_lang_code)
                professional_card(uploaded_file, caption, translated_caption, LANGUAGES[target_lang_code].capitalize())
            else:
                professional_card(uploaded_file, caption)

            if show_time:
                st.caption(f"⏱️ Captioning time: {elapsed:.2f} seconds")

        except Exception as e:
            st.error(f"❌ Error: {e}")

        finally:
            delete_temp_image(temp_path)
