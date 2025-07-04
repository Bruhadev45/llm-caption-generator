import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv
import base64
import io
from openai import OpenAI
from utils.translator import translate_with_openai

# --- Configuration and Initialization ---

# Load environment variables from .env file (for local development).
# In deployment environments (e.g., Streamlit Community Cloud), st.secrets
# is the recommended way to securely manage sensitive information.
load_dotenv()
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Debugging: Print a message to the console indicating if the API key was loaded.
print(f"DEBUG: OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

# Initialize the OpenAI client. This client is used for all API interactions.
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("DEBUG: OpenAI client initialized successfully.")
except Exception as e:
    # If there's an error initializing the client (e.g., missing or invalid API key),
    # display an error message in the Streamlit app and stop its execution.
    st.error(f"Error initializing OpenAI client. Please check your OPENAI_API_KEY in .env (for local) or Streamlit secrets (for deployment). Details: {e}")
    print(f"DEBUG: Error initializing OpenAI client: {e}")
    st.stop() # Halts the Streamlit app execution

# Set Streamlit page configuration for a wide layout and a custom title.
st.set_page_config(page_title="🧠 Advanced Image Caption + Translator (OpenAI 🚀)", layout="wide")
st.title("📷 Advanced Image Captioning & Translation")

# Define a dictionary of Indian languages and their corresponding language codes.
# These codes are used when making translation requests to the OpenAI API.
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

# Define a list of available caption styles for the user to choose from.
# These styles influence the prompt sent to the OpenAI Vision model.
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

# Initialize a counter in Streamlit's session state for the file uploader's key.
# Incrementing this key effectively resets the st.file_uploader widget, clearing selected files.
if 'file_uploader_key_counter' not in st.session_state:
    st.session_state.file_uploader_key_counter = 0

# --- Sidebar Controls ---

# Checkbox to enable or disable translation. It's off by default.
enable_translation = st.sidebar.checkbox("Enable Translation", False)
# Dropdown menu for selecting the target translation language.
selected_language_name = st.sidebar.selectbox("Translate to", list(indian_languages.keys()), index=0)
selected_language_code = indian_languages[selected_language_name] # Retrieve the language code for the selected language.
# Dropdown menu for selecting the desired caption style.
selected_caption_style = st.sidebar.selectbox("Caption Style", caption_styles, index=0)
# Slider to control the number of captions to generate per image (from 1 to 10).
num_captions_to_generate = st.sidebar.slider("Number of Captions per Image", 1, 10, 1)

# Button in the sidebar to clear all uploaded images and generated content.
if st.sidebar.button("Clear All"):
    print("DEBUG: 'Clear All' button clicked. Resetting session state and file uploader.")
    st.session_state.uploaded_images_data = [] # Clear all stored image data and associated captions/translations.
    st.session_state.file_uploader_key_counter += 1 # Increment the key to force the file uploader to reset.
    st.rerun() # Force a full rerun of the Streamlit app to reflect the cleared state.

# File uploader widget, configured to accept multiple image files.
# The 'key' ensures the widget can be reset programmatically.
uploaded_files = st.file_uploader(
    "Upload Images",
    type=["jpg", "jpeg", "png"], # Accepted file types
    accept_multiple_files=True,  # Allow multiple files to be uploaded
    key=f"file_uploader_{st.session_state.file_uploader_key_counter}" # Dynamic key for resetting the uploader.
)

# --- Helper Functions ---

def encode_image_to_base64(image: Image.Image) -> str:
    """
    Converts a PIL (Pillow) Image object into a base64 encoded string.
    This format is required for sending image data to OpenAI's Vision API.
    """
    buffered = io.BytesIO()      # Create an in-memory binary stream.
    image.save(buffered, format="PNG") # Save the PIL Image to the buffer as a PNG.
    return base64.b64encode(buffered.getvalue()).decode("utf-8") # Encode to base64 and decode to a UTF-8 string.

def generate_openai_captions(image: Image.Image, style: str, num_variations: int) -> list[str]:
    """
    Generates one or more captions for a given image using OpenAI's GPT-4o Vision model.
    The captions' style and quantity are customizable.

    Args:
        image (PIL.Image.Image): The input image as a PIL Image object.
        style (str): The desired style/tone for the captions (e.g., "Humorous", "Poetic").
        num_variations (int): The number of distinct captions to generate.

    Returns:
        list[str]: A list of generated captions, or an error message if the API call fails.
    """
    if not OPENAI_API_KEY:
        print("DEBUG: OPENAI_API_KEY is missing inside generate_openai_captions function.")
        return ["❌ OpenAI API Key missing. Please set it in Streamlit secrets or .env."]

    # Encode the input image to base64 format.
    base64_image = encode_image_to_base64(image)
    print(f"DEBUG: Image encoded to base64. Size: {len(base64_image)} bytes.")

    # Construct the prompt text for the OpenAI Vision model.
    # This prompt guides the model on how to generate captions based on user preferences.
    prompt_text = f"Generate {num_variations} distinct captions for this image."
    if style != "Default":
        prompt_text += f" The captions should have a {style.lower()} tone."
    
    if num_variations > 1:
        # For multiple captions, instruct the model to format them clearly (e.g., numbered list).
        prompt_text += " Provide each caption on a new line, prefixed with a number (e.g., '1. Caption one\\n2. Caption two')."
    else:
        # For a single caption, request a concise and descriptive one-sentence output.
        prompt_text += " Provide a single, perfect, and descriptive caption, aiming for at least one full sentence. Focus on the main subject and action."

    print(f"DEBUG: Prompt text for OpenAI: {prompt_text}")

    try:
        # Make the API call to OpenAI's chat completions endpoint.
        # The 'messages' list defines the conversation context, including the image.
        response = client.chat.completions.create(
            model="gpt-4o", # Specify the multimodal model capable of image understanding.
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text}, # The text part of the prompt.
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}", # The image data in base64 format.
                                "detail": "high" # Request high-detail analysis for better caption quality.
                            },
                        },
                    ],
                }
            ],
            max_tokens=300 * num_variations, # Set a maximum token limit for the response, scaled by the number of variations.
        )
        raw_captions = response.choices[0].message.content.strip() # Extract the raw text content from the model's response.
        print(f"DEBUG: Raw captions received from OpenAI: {raw_captions}")

        # Post-process the raw captions, especially if multiple variations were requested.
        if num_variations > 1:
            # Split the raw string into individual captions based on newlines.
            captions_list = [line.strip() for line in raw_captions.split('\n') if line.strip()]
            cleaned_captions = []
            for cap in captions_list:
                # Remove any leading numbers (e.g., "1. ") or bullet points (e.g., "- ") that the model might have added.
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
            return [raw_captions] # Return a list containing the single caption.

    except Exception as e:
        # Catch any exceptions during the API call and return an error message.
        print(f"DEBUG: Exception during OpenAI caption generation: {e}")
        return [f"❌ OpenAI Captioning Error: {e}"]

# --- Main Application Flow ---

# Initialize session state variable to store data for all uploaded images.
# This list will hold dictionaries, where each dict represents an uploaded image
# and its associated captions and translations.
# Example structure:
# [{'file_name': 'img1.png',
#   'image_data': PIL_Image_Object,
#   'captions_data': [{'caption': '...', 'translations': {'hi': '...', 'te': '...'}}]},
#  ...]
if 'uploaded_images_data' not in st.session_state:
    st.session_state.uploaded_images_data = []

# Handle image uploads when files are selected in the uploader.
if uploaded_files:
    # Get the sorted names of files currently selected in the uploader.
    current_file_names = sorted([f.name for f in uploaded_files])
    # Get the sorted names of files already processed and stored in session state.
    stored_file_names = sorted([img_data['file_name'] for img_data in st.session_state.uploaded_images_data])

    # Check if the set of uploaded files has genuinely changed compared to what's stored.
    # This optimization prevents reprocessing the same files on every Streamlit rerun
    # if the user hasn't changed their selection.
    if current_file_names != stored_file_names:
        print("DEBUG: New set of files uploaded or files changed. Resetting state for new upload.")
        st.session_state.uploaded_images_data = [] # Clear all previous images and their data.

        # Iterate through each newly uploaded file.
        for uploaded_file in uploaded_files:
            image_pil = Image.open(uploaded_file).convert("RGB") # Open the uploaded file as a PIL Image.
            # Append a new dictionary for this image to the session state list.
            st.session_state.uploaded_images_data.append({
                'file_name': uploaded_file.name,
                'image_data': image_pil,
                'captions_data': [] # Initialize an empty list to store captions for this specific image.
            })
        
        # Trigger initial caption generation for all newly added images.
        # This loop runs once to generate captions for all new images, then triggers a rerun.
        if st.session_state.uploaded_images_data: # Ensure there are images to process.
            with st.spinner(f"🧠 Generating initial captions for uploaded images..."):
                for img_entry in st.session_state.uploaded_images_data:
                    if not img_entry['captions_data']: # Only generate captions if they haven't been generated yet for this image.
                        captions = generate_openai_captions(img_entry['image_data'], selected_caption_style, num_captions_to_generate)
                        for caption_text in captions:
                            img_entry['captions_data'].append({'caption': caption_text, 'translations': {}}) # Add generated captions.
            print("DEBUG: Initial captions generated. Rerunning app to display.")
            st.rerun() # Force a rerun to update the UI with the newly generated captions.

    # Display results for each uploaded image currently stored in session state.
    for img_idx, img_entry in enumerate(st.session_state.uploaded_images_data):
        st.markdown(f"## Image: {img_entry['file_name']}") # Display the image filename as a prominent header.
        st.image(img_entry['image_data'], caption=f"Uploaded Image: {img_entry['file_name']}", use_container_width=True)

        if img_entry['captions_data']: # Check if captions have been generated for this image.
            st.markdown("---") # Visual separator for clarity.
            st.subheader("Generated Captions:")
            for i, caption_entry in enumerate(img_entry['captions_data']):
                caption_text = caption_entry['caption']
                translations = caption_entry['translations']

                st.markdown(f"**📝 Caption {i+1} ({selected_caption_style} style):** {caption_text}")

                # Translate the current caption if translation is enabled and it hasn't been translated to the current language yet.
                if enable_translation and not caption_text.startswith("❌"): # Ensure no error in caption before translating.
                    if selected_language_code not in translations: # Check if translation for this language is cached.
                        print(f"DEBUG: Translating caption {i+1} of {img_entry['file_name']} to {selected_language_name}.")
                        with st.spinner(f"🌍 Translating Caption {i+1} to {selected_language_name}..."):
                            translated = translate_with_openai(caption_text, selected_language_code, selected_language_name)
                            translations[selected_language_code] = translated # Store the new translation in the cache.
                    else:
                        translated = translations[selected_language_code] # Use the cached translation.
                        print(f"DEBUG: Using cached translation for caption {i+1} of {img_entry['file_name']}.")
                    st.markdown(f"**🌐 Translated ({selected_language_name}):** {translated}")
                elif caption_text.startswith("❌"):
                    st.error(f"Caption {i+1} error. Translation skipped.")
            st.markdown("---") # Visual separator.

        # Button to generate more captions for the current specific image.
        # A unique key is essential for buttons placed inside a loop to prevent Streamlit errors.
        if st.button(f"Generate Another Caption for {img_entry['file_name']}", key=f"gen_more_btn_{img_idx}"):
            with st.spinner(f"🧠 Generating {num_captions_to_generate} more {selected_caption_style.lower()} captions for {img_entry['file_name']}..."):
                new_captions = generate_openai_captions(img_entry['image_data'], selected_caption_style, num_captions_to_generate)
                for caption_text in new_captions:
                    img_entry['captions_data'].append({'caption': caption_text, 'translations': {}}) # Add newly generated captions to the list.
                print(f"DEBUG: Additional captions generated for {img_entry['file_name']}. Rerunning app.")
                st.rerun() # Force a rerun to display the newly added captions.

else:
    # This block executes when no files are currently selected in the Streamlit file uploader.
    # It handles clearing the session state if data from previous uploads is still present.
    if st.session_state.uploaded_images_data: # If there's data in session state from a previous upload.
        print("DEBUG: No files uploaded in uploader. Clearing session state from previous uploads.")
        st.session_state.uploaded_images_data = [] # Clear the stored image data.
        # No need to increment file_uploader_key_counter here, as the uploader
        # is already empty and will naturally reset on the next fresh load.
        st.rerun() # Force a rerun to ensure the UI reflects the cleared state.
    else:
        # Display an initial instruction message when the app starts or is cleared.
        st.info("📤 Upload one or more images to begin generating captions and translations.")

