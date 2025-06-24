from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import streamlit as st

device = "cuda" if torch.cuda.is_available() else "cpu"

@st.cache_resource(show_spinner="Loading BLIP model...")
def load_model(model_size="base"):
    model_id = (
        "Salesforce/blip-image-captioning-base"
        if model_size == "base"
        else "Salesforce/blip-image-captioning-large"
    )
    processor = BlipProcessor.from_pretrained(model_id)
    model = BlipForConditionalGeneration.from_pretrained(model_id).to(device)
    return processor, model

def generate_caption(image_path, model_size="base", beam_size=5):
    processor, model = load_model(model_size)
    raw_image = Image.open(image_path).convert("RGB")
    inputs = processor(raw_image, return_tensors="pt").to(device)
    output_ids = model.generate(
        **inputs,
        max_length=64,
        num_beams=beam_size,
        early_stopping=True,
        no_repeat_ngram_size=2,
        length_penalty=1.0
    )
    caption = processor.decode(output_ids[0], skip_special_tokens=True)
    return caption
