import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv
import base64
import io
from openai import OpenAI
from utils.translator import translate_with_openai

# Load environment variables
load_dotenv()
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Debugging: Print whether API key is loaded
print(f"DEBUG: OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

# Initialize OpenAI client for captioning
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("DEBUG: OpenAI client initialized successfully.")
except Exception as e:
    print(f"DEBUG: Error initializing OpenAI client: {e}")
    st.error(f"Error initializing OpenAI client. Please check your OPENAI_API_KEY in .env (for local) or Streamlit secrets (for deployment). Details: {e}")
    st.stop() # Stop the app if client cannot be initialized

st.set_page_config(page_title="🧠 Advanced Image Caption + Translator (OpenAI 🚀)", layout="wide")
st.title("📷 Advanced Image Captioning & Translation")

# Define Indian language options for translation
indian_languages = {
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Urdu": "ur"
}

# Define caption styles
caption_styles = [
    "Default",
    "Concise",
    "Descriptive",
    "Humorous",
    "Poetic",
    "Professional",
    "Casual",
    "Story-like"
]

# Sidebar controls
enable_translation = st.sidebar.checkbox("Enable Translation", False)
selected_language_name = st.sidebar.selectbox("Translate to", list(indian_languages.keys()), index=0)
selected_language_code = indian_languages[selected_language_name]
selected_caption_style = st.sidebar.selectbox("Caption Style", caption_styles, index=0)
num_captions_to_generate = st.sidebar.slider("Number of Captions per Image", 1, 10, 1) # Generate 1 to 10 captions

# --- MODIFIED: Allow multiple files ---
uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Function to encode image to base64 for OpenAI Vision API
def encode_image_to_base64(image: Image.Image) -> str:
    """Converts a PIL Image object to a base64 encoded string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# 📸 Advanced Caption generator function using OpenAI GPT-4o Vision
def generate_openai_captions(image: Image.Image, style: str, num_variations: int) -> list[str]:
    """
    Generates multiple captions for an image based on a specified style using OpenAI's GPT-4o Vision model.
    """
    if not OPENAI_API_KEY:
        print("DEBUG: OPENAI_API_KEY is missing inside generate_openai_captions.")
        return ["❌ OPENAI_API_KEY missing. Please set it in Streamlit secrets or .env."]

    base64_image = encode_image_to_base64(image)
    print(f"DEBUG: Image encoded to base64. Size: {len(base64_image)} bytes.")

    prompt_text = f"Generate {num_variations} distinct captions for this image."
    if style != "Default":
        prompt_text += f" The captions should have a {style.lower()} tone."
    
    if num_variations > 1:
        prompt_text += " Provide each caption on a new line, prefixed with a number (e.g., '1. Caption one\\n2. Caption two')."
    else:
        prompt_text += " Provide a single, perfect, and descriptive caption, aiming for at least one full sentence. Focus on the main subject and action."

    print(f"DEBUG: Prompt text for OpenAI: {prompt_text}")

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
            max_tokens=300 * num_variations, # Adjust max_tokens based on number of captions
        )
        raw_captions = response.choices[0].message.content.strip()
        print(f"DEBUG: Raw captions received from OpenAI: {raw_captions}")

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
            print(f"DEBUG: Cleaned multiple captions: {cleaned_captions}")
            return cleaned_captions
        else:
            print(f"DEBUG: Single caption generated: {raw_captions}")
            return [raw_captions]

    except Exception as e:
        print(f"DEBUG: Exception during OpenAI caption generation: {e}")
        return [f"❌ OpenAI Captioning Error: {e}"]

# 🔄 Main app flow
# Initialize session state variables if they don't exist
# Stores a list of dictionaries, where each dict represents an uploaded image and its captions/translations
# Example: [{'file_name': 'img1.png', 'image_data': PIL_Image_Object, 'captions_data': [{'caption': '...', 'translations': {}}]}, ...]
if 'uploaded_images_data' not in st.session_state:
    st.session_state.uploaded_images_data = []

# --- MODIFIED: Handle multiple uploaded files ---
if uploaded_files:
    # Check if the set of uploaded files has changed
    current_file_names = sorted([f.name for f in uploaded_files])
    stored_file_names = sorted([img_data['file_name'] for img_data in st.session_state.uploaded_images_data])

    if current_file_names != stored_file_names:
        print("DEBUG: New set of files uploaded or files changed. Resetting state.")
        st.session_state.uploaded_images_data = [] # Clear all previous images

        for uploaded_file in uploaded_files:
            image_pil = Image.open(uploaded_file).convert("RGB")
            st.session_state.uploaded_images_data.append({
                'file_name': uploaded_file.name,
                'image_data': image_pil,
                'captions_data': [] # List of {'caption': '...', 'translations': {...}} for this image
            })
        
        # Trigger initial caption generation for all new images
        # This will cause a rerun for each image, so we generate them sequentially
        # and then rerun once all initial captions are generated.
        all_initial_captions_generated = True
        for img_entry in st.session_state.uploaded_images_data:
            if not img_entry['captions_data']: # If this image doesn't have captions yet
                with st.spinner(f"🧠 Generating {num_captions_to_generate} {selected_caption_style.lower()} captions for {img_entry['file_name']}..."):
                    captions = generate_openai_captions(img_entry['image_data'], selected_caption_style, num_captions_to_generate)
                    for caption_text in captions:
                        img_entry['captions_data'].append({'caption': caption_text, 'translations': {}})
                all_initial_captions_generated = False # Indicate that a generation occurred
        
        if not all_initial_captions_generated:
            st.rerun() # Rerun to display the initial captions

    # Display results for each uploaded image
    for img_idx, img_entry in enumerate(st.session_state.uploaded_images_data):
        st.markdown(f"## Image: {img_entry['file_name']}")
        st.image(img_entry['image_data'], caption=f"Uploaded Image: {img_entry['file_name']}", use_container_width=True)

        if img_entry['captions_data']:
            st.markdown("---")
            st.subheader("Generated Captions:")
            for i, caption_entry in enumerate(img_entry['captions_data']):
                caption_text = caption_entry['caption']
                translations = caption_entry['translations']

                st.markdown(f"**📝 Caption {i+1} ({selected_caption_style} style):** {caption_text}")

                if enable_translation and not caption_text.startswith("❌"):
                    if selected_language_code not in translations:
                        print(f"DEBUG: Translating caption {i+1} of {img_entry['file_name']} to {selected_language_name}.")
                        with st.spinner(f"🌍 Translating Caption {i+1} to {selected_language_name}..."):
                            translated = translate_with_openai(caption_text, selected_language_code, selected_language_name)
                            translations[selected_language_code] = translated
                    else:
                        translated = translations[selected_language_code]
                        print(f"DEBUG: Using cached translation for caption {i+1} of {img_entry['file_name']}.")
                    st.markdown(f"**🌐 Translated ({selected_language_name}):** {translated}")
                elif caption_text.startswith("❌"):
                    st.error(f"Caption {i+1} error. Translation skipped.")
            st.markdown("---")

        # Add a button to generate more captions for THIS specific image
        # Use a unique key for each button if there are multiple images
        if st.button(f"Generate Another Caption for {img_entry['file_name']}", key=f"gen_more_btn_{img_idx}"):
            with st.spinner(f"🧠 Generating {num_captions_to_generate} more {selected_caption_style.lower()} captions for {img_entry['file_name']}..."):
                new_captions = generate_openai_captions(img_entry['image_data'], selected_caption_style, num_captions_to_generate)
                for caption_text in new_captions:
                    img_entry['captions_data'].append({'caption': caption_text, 'translations': {}})
                print(f"DEBUG: Additional captions generated for {img_entry['file_name']}. Rerunning app.")
                st.rerun()

else:
    # Clear session state if no files are uploaded (e.g., on initial load or clear)
    print("DEBUG: No files uploaded. Clearing session state.")
    st.session_state.uploaded_images_data = []
    st.info("📤 Upload one or more images to begin generating advanced captions and translations.")

