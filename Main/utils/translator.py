import os
from dotenv import load_dotenv
from openai import OpenAI
from openai import OpenAIError # Import specific error type for better handling

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client globally for the translator module
# This client will be reused for all translation calls.
# Initialize as None and then try to create it in a try-except block.
client = None
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("DEBUG (translator.py): OpenAI client initialized successfully.")
except OpenAIError as e:
    # This catches errors specific to OpenAI client initialization (e.g., invalid API key format)
    print(f"DEBUG (translator.py): OpenAI API Error during client initialization: {e}")
    # Do not stop the app here; the translate_with_openai function will handle the missing/invalid key.
except Exception as e:
    # Catch any other unexpected errors during client initialization
    print(f"DEBUG (translator.py): Unexpected error during OpenAI client initialization: {e}")


def translate_with_openai(text: str, target_lang_code: str, target_lang_name: str) -> str:
    """
    Translates English text to a target Indian language using OpenAI's GPT-3.5 Turbo,
    with an improved prompt for better accuracy.

    Args:
        text (str): The English text to translate.
        target_lang_code (str): The language code for the target language (e.g., 'hi', 'te').
        target_lang_name (str): The full name of the target language (e.g., 'Hindi', 'Telugu').

    Returns:
        str: The translated text or an error message.
    """
    # Check if client was successfully initialized or if API key is missing
    if not client or not OPENAI_API_KEY:
        print("DEBUG (translator.py): OpenAI client not initialized or API key missing. Returning error.")
        return "❌ OpenAI API Key missing or client not initialized. Please check your .env file."

    try:
        # Determine the example translation based on language code
        example_translation = ""
        if target_lang_code == "te":
            example_translation = "నమస్కారం, మీరు ఎలా ఉన్నారు?"
        elif target_lang_code == "hi":
            example_translation = "नमस्ते, आप कैसे हैं?"
        else:
            # Fallback for other Indian languages, indicating a generic translation
            example_translation = "Hello, how are you?"

        messages = [
            {"role": "system", "content": f"You are an expert translator specializing in translating English to high-quality, natural-sounding {target_lang_name}. Provide only the translated text and nothing else."},
            {"role": "user", "content": f"Translate the following English text to {target_lang_name}: 'Hello, how are you?'"},
            {"role": "assistant", "content": example_translation},
            {"role": "user", "content": f"Translate the following English text to {target_lang_name}: '{text}'"}
        ]
        print(f"DEBUG (translator.py): Sending translation request for text: '{text}' to {target_lang_name}")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150
        )
        translated_text = response.choices[0].message.content.strip()
        print(f"DEBUG (translator.py): Received translated text: '{translated_text}'")
        return translated_text
    except OpenAIError as e:
        # Catches specific OpenAI API errors (e.g., invalid request, rate limits)
        print(f"DEBUG (translator.py): OpenAI API Error during translation: {e}")
        return f"❌ OpenAI Translation API Error: {e}"
    except Exception as e:
        # Catches any other general exceptions during the translation process
        print(f"DEBUG (translator.py): General Error during translation: {e}")
        return f"❌ OpenAI Translation Error in translator.py: {e}"

