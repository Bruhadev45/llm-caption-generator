import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv
import base64
import io
from langchain_openai import OpenAI as LangChainOpenAI
from langchain.prompts import PromptTemplate
from utils.translator import translate_with_openai
from utils.vectordb import add_caption_to_db, search_similar_captions

# --- Configuration and Initialization ---

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("❌ OPENAI_API_KEY not found. Please set it in your .env or Streamlit secrets.")
    st.stop()

# --- LangChain LLM setup (for prompt templating, translation) ---
llm_caption = LangChainOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o", temperature=0.5)

st.set_page_config(page_title="🧠  Image Caption + Translator ", layout="wide")
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

# --- Sidebar Controls ---

use_rag_for_caption = st.sidebar.toggle("🔎 Use RAG context for new captions", value=False) if hasattr(st.sidebar, "toggle") else st.sidebar.checkbox("🔎 Use RAG context for new captions", value=False)
rag_top_k = 2

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
    base64_image = encode_image_to_base64(image)

    # Build prompt using LangChain PromptTemplate
    style_add = f"The captions should have a {style.lower()} tone." if style != "Default" else ""
    prompt_template = PromptTemplate(
        input_variables=["num_variations", "style_add"],
        template="""Generate {num_variations} distinct captions for this image. {style_add}
Provide each caption on a new line, prefixed with a number (e.g., '1. Caption one\\n2. Caption two')."""
    )
    prompt_text = prompt_template.format(num_variations=num_captions_to_generate, style_add=style_add)

    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        response = openai.chat.completions.create(
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
            captions = cleaned_captions
        else:
            captions = [raw_captions]
    except Exception as e:
        return [f"❌ OpenAI Captioning Error: {e}"], []

    # Now do RAG retrieval if enabled, using the first caption as the query
    rag_context = []
    min_rag_score = 0.3
    if use_rag and rag_k > 0 and captions:
        rag_results = search_similar_captions(captions[0], top_k=rag_k)
        rag_context = [doc for doc in rag_results['documents'][0]]
        scores = rag_results.get('scores', [[]])[0]
        if not rag_context or all(score < min_rag_score for score in scores):
            rag_context = ["No relevant caption found for this image."]

    return captions, rag_context

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
