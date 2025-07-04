import os
from dotenv import load_dotenv
from openai import OpenAI
from openai import OpenAIError # Import specific OpenAI error type for fine-grained error handling

# --- Configuration and Initialization ---

# Load environment variables from .env file (for local development).
# This is typically where the OPENAI_API_KEY would be stored locally.
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Retrieve the API key.

# Initialize the OpenAI client globally within this module.
# This client instance will be reused for all translation requests.
client = None
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("DEBUG (translator.py): OpenAI client initialized successfully.")
except OpenAIError as e:
    # Catch specific OpenAI API errors that occur during client initialization (e.g., invalid key format).
    print(f"DEBUG (translator.py): OpenAI API Error during client initialization: {e}")
    # The `translate_with_openai` function will handle the case where `client` is None or key is invalid.
except Exception as e:
    # Catch any other unexpected errors during the client initialization process.
    print(f"DEBUG (translator.py): Unexpected error during OpenAI client initialization: {e}")


# --- Translation Function ---

def translate_with_openai(text: str, target_lang_code: str, target_lang_name: str) -> str:
    """
    Translates English text to a specified target Indian language using OpenAI's GPT-3.5 Turbo model.
    Includes an improved prompt with a few-shot example for better translation accuracy and naturalness.

    Args:
        text (str): The English text string to be translated.
        target_lang_code (str): The ISO 639-1 language code for the target language (e.g., 'hi' for Hindi, 'te' for Telugu).
        target_lang_name (str): The full, human-readable name of the target language (e.g., 'Hindi', 'Telugu').
                                This is used in the prompt for better model guidance.

    Returns:
        str: The translated text string, or an error message if the translation fails.
    """
    # Check if the OpenAI client was successfully initialized and if the API key is available.
    if not client or not OPENAI_API_KEY:
        print("DEBUG (translator.py): OpenAI client not initialized or API key missing. Returning error.")
        return "❌ OpenAI API Key missing or client not initialized. Please check your .env file."

    try:
        # Determine a simple example translation based on the target language code.
        # This acts as a "few-shot" example to guide the model's translation style and accuracy.
        example_translation = ""
        if target_lang_code == "te":
            example_translation = "నమస్కారం, మీరు ఎలా ఉన్నారు?" # Telugu for "Hello, how are you?"
        elif target_lang_code == "hi":
            example_translation = "नमस्ते, आप कैसे हैं?" # Hindi for "Hello, how are you?"
        else:
            # Fallback for other Indian languages or if no specific example is provided.
            example_translation = "Hello, how are you?"

        # Construct the messages list for the OpenAI Chat Completions API.
        # The system message sets the role and instructions for the AI.
        # The user and assistant messages provide a few-shot example.
        # The final user message is the actual translation request.
        messages = [
            {"role": "system", "content": f"You are an expert translator specializing in translating English to high-quality, natural-sounding {target_lang_name}. Provide only the translated text and nothing else."},
            {"role": "user", "content": f"Translate the following English text to {target_lang_name}: 'Hello, how are you?'"},
            {"role": "assistant", "content": example_translation},
            {"role": "user", "content": f"Translate the following English text to {target_lang_name}: '{text}'"}
        ]
        print(f"DEBUG (translator.py): Sending translation request for text: '{text}' to {target_lang_name}")

        # Make the API call to OpenAI's GPT-3.5 Turbo model for translation.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # A cost-effective model suitable for translation tasks.
            messages=messages,
            max_tokens=150 # Set a maximum token limit for the translated response.
        )
        translated_text = response.choices[0].message.content.strip() # Extract and clean the translated text.
        print(f"DEBUG (translator.py): Received translated text: '{translated_text}'")
        return translated_text
    except OpenAIError as e:
        # Catch specific OpenAI API errors (e.g., network issues, invalid requests, rate limits).
        print(f"DEBUG (translator.py): OpenAI API Error during translation: {e}")
        return f"❌ OpenAI Translation API Error: {e}"
    except Exception as e:
        # Catch any other general exceptions that might occur during the translation process.
        print(f"DEBUG (translator.py): General Error during translation: {e}")
        return f"❌ OpenAI Translation Error in translator.py: {e}"

