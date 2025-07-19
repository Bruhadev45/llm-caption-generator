import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv
import base64
import io
from openai import OpenAI
from utils.translator import translate_with_openai
from utils.vectordb import add_caption_to_db, search_similar_captions

# --- Configuration and Initialization ---

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ OPENAI_API_KEY not found. Please set it in your .env or Streamlit secrets.")
    st.stop()

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    st.error(f"Error initializing OpenAI client: {e}")
    st.stop()

st.set_page_config(page_title="🧠  Image Caption + Translator", layout="wide")
st.title("📷  Image Captioning and Translation")

indian_languages = {
    "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "Kannada": "kn", "Malayalam": "ml",
    "Bengali": "bn", "Gujarati": "gu", "Marathi": "mr", "Punjabi": "pa", "Urdu": "ur"
}
caption_styles = [
    "Default", "Concise", "Descriptive", "Humorous", "Poetic", "Professional", "Casual", "Story-like"
]

if 'file_uploader_key_counter' not in st.session_state:
    st.session_state.file_uploader_key_counter = 0

# --- Sidebar Controls (RAG first, then others) ---

# RAG toggle at the top
use_rag_for_caption = st.sidebar.toggle("🔎 Use RAG context for new captions", value=False) if hasattr(st.sidebar, "toggle") else st.sidebar.checkbox("🔎 Use RAG context for new captions", value=False)
rag_top_k = 1 # Fixed value

enable_translation = st.sidebar.checkbox("Enable Translation", False)
selected_language_name = st.sidebar.selectbox("Translate to", list(indian_languages.keys()), index=0)
selected_language_code = indian_languages[selected_language_name]
selected_caption_style = st.sidebar.selectbox("Caption Style", caption_styles, index=0)
num_captions_to_generate = st.sidebar.slider("Number of Captions per Image", 1, 10, 1)

if st.sidebar.button("Clear All"):
    st.session_state.uploaded_images_data = []
    st.session_state.file_uploader_key_counter += 1
    st.rerun()

uploaded_files = st.file_uploader(
    "Upload Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.file_uploader_key_counter}"
)

# --- Helper Functions ---

def encode_image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def generate_openai_captions(image: Image.Image, style: str, num_variations: int, use_rag: bool, rag_k: int) -> (list, list):
    """Generate captions, optionally using RAG context from similar captions in DB."""
    if not OPENAI_API_KEY:
        return ["❌ OpenAI API Key missing. Please set it in Streamlit secrets or .env."], []
    base64_image = encode_image_to_base64(image)

    # Optionally get RAG context
    rag_context = []
    if use_rag and rag_k > 0:
        try:
            rag_results = search_similar_captions("image caption", top_k=rag_k)
            rag_context = [doc for doc in rag_results['documents'][0]]
        except Exception as e:
            rag_context = []

    prompt_text = f"Generate {num_variations} distinct captions for this image."
    if style != "Default":
        prompt_text += f" The captions should have a {style.lower()} tone."
    if use_rag and rag_context:
        prompt_text += (
            "\n\nHere are some relevant captions from my database for context:\n" +
            "\n".join(f"- {c}" for c in rag_context)
        )
    if num_variations > 1:
        prompt_text += " Provide each caption on a new line, prefixed with a number (e.g., '1. Caption one\\n2. Caption two')."
    else:
        prompt_text += " Provide a single, perfect, and descriptive caption, aiming for at least one full sentence. Focus on the main subject and action."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300 * num_variations,
        )
        raw_captions = response.choices[0].message.content.strip()
        if num_variations > 1:
            captions_list = [line.strip() for line in raw_captions.split('\n') if line.strip()]
            cleaned_captions = []
            for cap in captions_list:
                if cap and (cap[0].isdigit() and (cap[1] == '.' or cap[1] == ' ')):
                    cleaned_captions.append(cap[cap.find('.') + 1:].strip() if '.' in cap else cap[cap.find(' ') + 1:].strip())
                elif cap.startswith('- '):
                    cleaned_captions.append(cap[2:].strip())
                else:
                    cleaned_captions.append(cap)
            return cleaned_captions, rag_context
        else:
            return [raw_captions], rag_context
    except Exception as e:
        return [f"❌ OpenAI Captioning Error: {e}"], rag_context

# --- Main Application Flow ---

if 'uploaded_images_data' not in st.session_state:
    st.session_state.uploaded_images_data = []

if uploaded_files:
    current_file_names = sorted([f.name for f in uploaded_files])
    stored_file_names = sorted([img_data['file_name'] for img_data in st.session_state.uploaded_images_data])

    if current_file_names != stored_file_names:
        st.session_state.uploaded_images_data = []
        for uploaded_file in uploaded_files:
            image_pil = Image.open(uploaded_file).convert("RGB")
            st.session_state.uploaded_images_data.append({
                'file_name': uploaded_file.name,
                'image_data': image_pil,
                'captions_data': []
            })
        if st.session_state.uploaded_images_data:
            with st.spinner(f"🧠 Generating initial captions for uploaded images..."):
                for img_entry in st.session_state.uploaded_images_data:
                    if not img_entry['captions_data']:
                        captions, rag_context = generate_openai_captions(
                            img_entry['image_data'],
                            selected_caption_style,
                            num_captions_to_generate,
                            use_rag_for_caption,
                            rag_top_k,
                        )
                        for caption_text in captions:
                            img_entry['captions_data'].append({'caption': caption_text, 'translations': {}, 'rag_context': rag_context})
                            add_caption_to_db(
                                caption_text,
                                metadata={
                                    "file": img_entry['file_name'],
                                    "style": selected_caption_style
                                }
                            )
            st.rerun()

    for img_idx, img_entry in enumerate(st.session_state.uploaded_images_data):
        st.markdown(f"## Image: {img_entry['file_name']}")
        st.image(img_entry['image_data'], caption=f"Uploaded Image: {img_entry['file_name']}", use_container_width=True)

        if img_entry['captions_data']:
            st.markdown("---")
            st.subheader("Generated Captions:")
            for i, caption_entry in enumerate(img_entry['captions_data']):
                caption_text = caption_entry['caption']
                translations = caption_entry['translations']
                rag_context = caption_entry.get('rag_context', [])

                st.markdown(f"**📝 Caption {i+1} ({selected_caption_style} style):** {caption_text}")

                # Show RAG context for this caption if available
                if rag_context and use_rag_for_caption:
                    with st.expander("See RAG (retrieved captions used as context)"):
                        for r in rag_context:
                            st.markdown(f"- {r}")

                if enable_translation and not caption_text.startswith("❌"):
                    if selected_language_code not in translations:
                        with st.spinner(f"🌍 Translating Caption {i+1} to {selected_language_name}..."):
                            translated = translate_with_openai(caption_text, selected_language_code, selected_language_name)
                            translations[selected_language_code] = translated
                    else:
                        translated = translations[selected_language_code]
                    st.markdown(f"**🌐 Translated ({selected_language_name}):** {translated}")
                elif caption_text.startswith("❌"):
                    st.error(f"Caption {i+1} error. Translation skipped.")
            st.markdown("---")

        if st.button(f"Generate Another Caption for {img_entry['file_name']}", key=f"gen_more_btn_{img_idx}"):
            with st.spinner(f"🧠 Generating {num_captions_to_generate} more {selected_caption_style.lower()} captions for {img_entry['file_name']}..."):
                new_captions, rag_context = generate_openai_captions(
                    img_entry['image_data'],
                    selected_caption_style,
                    num_captions_to_generate,
                    use_rag_for_caption,
                    rag_top_k,
                )
                for caption_text in new_captions:
                    img_entry['captions_data'].append({'caption': caption_text, 'translations': {}, 'rag_context': rag_context})
                    add_caption_to_db(
                        caption_text,
                        metadata={
                            "file": img_entry['file_name'],
                            "style": selected_caption_style
                        }
                    )
                st.rerun()

else:
    if st.session_state.uploaded_images_data:
        st.session_state.uploaded_images_data = []
        st.rerun()
    else:
        st.info("📤 Upload one or more images to begin generating captions and translations.")
