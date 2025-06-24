import tempfile

def save_uploaded_image(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name

def delete_temp_image(image_path):
    import os
    if os.path.exists(image_path):
        os.remove(image_path)
