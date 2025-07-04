import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"

def load_caption_model():
    """
    Loads the local image captioning model.
    This file is no longer directly used by app.py for captioning,
    as captioning is now handled by OpenAI within app.py.
    """
    model_name = "nlpconnect/vit-gpt2-image-captioning"
    model = VisionEncoderDecoderModel.from_pretrained(model_name).to(device)
    feature_extractor = ViTImageProcessor.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, feature_extractor, tokenizer

# The model is loaded globally in the original file, but not used by the new app.py
# model, feature_extractor, tokenizer = load_caption_model()

def generate_caption(image, max_length=20):
    """
    Generates a caption using the local model.
    This function is no longer directly used by app.py.
    """
    # Ensure model, feature_extractor, tokenizer are loaded if this function were to be called
    # For now, this is just for reference of the original code.
    # pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
    # output_ids = model.generate(
    #     pixel_values,
    #     max_length=max_length,
    #     do_sample=False,
    #     num_beams=1,
    #     early_stopping=True
    # )
    # caption = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
    # return caption
    return "This function is from the original captioning.py and is not active in the current app.py."

