import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from PIL import Image

# Determine the device to run the model on (GPU if available, otherwise CPU).
device = "cuda" if torch.cuda.is_available() else "cpu"

def load_caption_model():
    """
    Loads a local image captioning model (VisionEncoderDecoderModel from Hugging Face
    transformers library) along with its feature extractor and tokenizer.

    This function is part of the original local captioning logic and is NOT
    used in the current version of app.py, which uses OpenAI's Vision API.
    It's kept here for reference to the previous implementation.
    """
    model_name = "nlpconnect/vit-gpt2-image-captioning"
    # Load the pre-trained model and move it to the determined device (CPU/GPU).
    model = VisionEncoderDecoderModel.from_pretrained(model_name).to(device)
    # Load the feature extractor, responsible for preparing images for the model.
    feature_extractor = ViTImageProcessor.from_pretrained(model_name)
    # Load the tokenizer, responsible for converting model output IDs back to text.
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, feature_extractor, tokenizer

# The following lines would typically load the model globally if this file were actively used.
# They are commented out because app.py no longer imports/uses this model.
# model, feature_extractor, tokenizer = load_caption_model()

def generate_caption(image, max_length=20):
    """
    Generates a caption for an image using the locally loaded model.

    This function is also part of the original local captioning logic and is NOT
    used by the current app.py. It's included for historical context.

    Args:
        image (PIL.Image.Image): The input image to caption.
        max_length (int): The maximum length of the generated caption.

    Returns:
        str: The generated caption.
    """
    # If this function were active, it would process the image and generate a caption.
    # The actual implementation details are commented out as they are superseded by OpenAI.
    # pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)
    # output_ids = model.generate(
    #     pixel_values,
    #     max_length=max_length,
    #     do_sample=False,       # Use greedy search (no sampling for deterministic output)
    #     num_beams=1,           # Set beam to 1 to avoid errors with certain configurations
    #     early_stopping=True    # Stop generation once a full sentence is formed
    # )
    # caption = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
    # return caption
    return "This function is from the original captioning.py and is not active in the current app.py."

