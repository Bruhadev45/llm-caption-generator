from googletrans import Translator, LANGUAGES

translator = Translator()

def translate_caption(caption, dest_language='te'):
    try:
        translation = translator.translate(caption, dest=dest_language)
        return translation.text
    except Exception as e:
        return f"Translation failed: {str(e)}"
