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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Debugging: Print whether API key is loaded
print(f"DEBUG: OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

# Initialize OpenAI client for captioning
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("DEBUG: OpenAI client initialized successfully.")
except Exception as e:
    print(f"DEBUG: Error initializing OpenAI client: {e}")
    st.error(f"Error initializing OpenAI client. Please check your OPENAI_API_KEY in .env. Details: {e}")
    st.stop() # Stop the app if client cannot be initialized

st.set_page_config(page_title="🧠 Image Caption + Translator (OpenAI 🚀)", layout="wide")
st.title("📷 Image Captioning & Translation")

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
# Changed default value to False (off)
enable_translation = st.sidebar.checkbox("Enable Translation", False)
selected_language_name = st.sidebar.selectbox("Translate to", list(indian_languages.keys()), index=0)
selected_language_code = indian_languages[selected_language_name]
selected_caption_style = st.sidebar.selectbox("Caption Style", caption_styles, index=0)
# Changed max value of slider to 10
num_captions_to_generate = st.sidebar.slider("Number of Captions", 1, 10, 1) # Generate 1 to 10 captions

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# Function to encode image to base64 for OpenAI Vision API
def encode_image_to_base64(image: Image.Image) -> str:
    """Converts a PIL Image object to a base64 encoded string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# 📸 Caption generator function using OpenAI GPT-4o Vision
def generate_openai_captions(image: Image.Image, style: str, num_variations: int) -> list[str]:
    """
    Generates multiple captions for an image based on a specified style using OpenAI's GPT-4o Vision model.
    """
    if not OPENAI_API_KEY:
        print("DEBUG: OPENAI_API_KEY is missing inside generate_openai_captions.")
        return ["❌ OPENAI_API_KEY missing in .env. Please provide your API key."]

    base64_image = encode_image_to_base64(image)
    print(f"DEBUG: Image encoded to base64. Size: {len(base64_image)} bytes.")

    # Adjust prompt based on selected style and number of variations
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

        # Split multiple captions if requested
        if num_variations > 1:
            # Split by newline and clean up numbering
            captions_list = [line.strip() for line in raw_captions.split('\n') if line.strip()]
            # Remove numbering (e.g., "1. " or " - ")
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
            return [raw_captions] # Return as a list even for single caption

    except Exception as e:
        print(f"DEBUG: Exception during OpenAI caption generation: {e}")
        return [f"❌ OpenAI Captioning Error: {e}"]

# 🔄 Main app flow
# Initialize session state variables if they don't exist
if 'uploaded_image_data' not in st.session_state:
    st.session_state.uploaded_image_data = None
if 'generated_captions_data' not in st.session_state:
    st.session_state.generated_captions_data = [] # Stores list of dicts: {'caption': '...', 'translations': {...}}
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

# Handle new image upload
if uploaded_file:
    # Check if a new file is uploaded or if the file is different from the one in session state
    if st.session_state.uploaded_image_data is None or \
       st.session_state.uploaded_image_data.name != uploaded_file.name or \
       st.session_state.uploaded_image_data.size != uploaded_file.size:

        print("DEBUG: New file uploaded or file changed. Resetting state.")
        st.session_state.uploaded_image_data = uploaded_file
        st.session_state.generated_captions_data = [] # Clear previous captions for new image
        st.session_state.current_image = Image.open(uploaded_file).convert("RGB") # Store PIL image
        
        # Trigger initial caption generation for the new image
        with st.spinner(f"🧠 Generating {num_captions_to_generate} {selected_caption_style.lower()} captions with OpenAI..."):
            captions = generate_openai_captions(st.session_state.current_image, selected_caption_style, num_captions_to_generate)
            for caption_text in captions:
                st.session_state.generated_captions_data.append({'caption': caption_text, 'translations': {}})
            print("DEBUG: Initial captions generated. Rerunning app.")
            st.rerun() # Rerun to display the first set of captions immediately

    st.image(st.session_state.current_image, caption="Uploaded Image", use_container_width=True)

    # Display all generated captions and their translations
    if st.session_state.generated_captions_data:
        st.markdown("---") # Separator for captions
        st.subheader("Generated Captions:")
        for i, caption_entry in enumerate(st.session_state.generated_captions_data):
            caption_text = caption_entry['caption']
            translations = caption_entry['translations']

            st.markdown(f"**📝 Caption {i+1} ({selected_caption_style} style):** {caption_text}")

            # Translate the current caption if translation is enabled and not already translated for current language
            if enable_translation and not caption_text.startswith("❌"):
                if selected_language_code not in translations:
                    print(f"DEBUG: Translating caption {i+1} to {selected_language_name}.")
                    with st.spinner(f"🌍 Translating Caption {i+1} to {selected_language_name}..."):
                        translated = translate_with_openai(caption_text, selected_language_code, selected_language_name)
                        translations[selected_language_code] = translated # Store translation
                        # No st.rerun() here, as we want to translate all displayed captions
                else:
                    translated = translations[selected_language_code] # Use cached translation
                    print(f"DEBUG: Using cached translation for caption {i+1}.")
                st.markdown(f"**🌐 Translated ({selected_language_name}):** {translated}")
            elif caption_text.startswith("❌"):
                st.error(f"Caption {i+1} error. Translation skipped.")
        st.markdown("---") # Separator

    # Add a button to generate more captions
    if st.session_state.current_image is not None:
        if st.button("Generate Another Caption"):
            with st.spinner(f"🧠 Generating {num_captions_to_generate} more {selected_caption_style.lower()} captions..."):
                new_captions = generate_openai_captions(st.session_state.current_image, selected_caption_style, num_captions_to_generate)
                for caption_text in new_captions:
                    st.session_state.generated_captions_data.append({'caption': caption_text, 'translations': {}})
                print("DEBUG: Additional captions generated. Rerunning app.")
                st.rerun() # Rerun to display the new captions

else:
    # Clear session state if no file is uploaded (e.g., on initial load or clear)
    print("DEBUG: No file uploaded. Clearing session state.")
    st.session_state.uploaded_image_data = None
    st.session_state.generated_captions_data = []
    st.session_state.current_image = None # Ensure current_image is cleared
    st.info("📤 Upload an image")

