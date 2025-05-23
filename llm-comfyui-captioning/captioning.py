# captioning.py

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import functools

# Cache models to avoid reloading
@functools.lru_cache(maxsize=2)
def load_model(model_size="base"):
    model_id = (
        "Salesforce/blip-image-captioning-base"
        if model_size == "base"
        else "Salesforce/blip-image-captioning-large"
    )
    processor = BlipProcessor.from_pretrained(model_id)
    model = BlipForConditionalGeneration.from_pretrained(model_id)
    return processor, model

def generate_caption(image_path, model_size="base"):
    processor, model = load_model(model_size)
    raw_image = Image.open(image_path).convert("RGB")
    inputs = processor(raw_image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption
