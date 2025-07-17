# 📷 Image Captioning & Translation App with OpenAI

This Streamlit application provides an advanced solution for generating descriptive captions for images and translating them into various Indian languages. It leverages the power of OpenAI's latest multimodal and language models to deliver accurate and contextually relevant results.

## ✨ Features

* **Advanced Image Captioning:** Utilizes OpenAI's `gpt-4o` (Vision) model to generate highly detailed and context-aware captions for uploaded images.
* **Multi-Image Upload:** Supports uploading multiple images at once, allowing for batch processing and comparison of captions.
* **Multiple Caption Variations:** Generate up to 10 distinct caption options for a single image, allowing users to choose the most suitable description.
* **Customizable Caption Style:** Select from various styles (e.g., "Concise," "Descriptive," "Humorous," "Poetic," "Professional") to tailor the tone and focus of the generated captions.
* **Indian Language Translation:** Translate captions into a wide range of Indian languages using OpenAI's `gpt-3.5-turbo` model, with improved accuracy for natural-sounding translations.
* **Interactive UI:** Built with Streamlit for a user-friendly and responsive web interface.
* **Generate More Captions:** A dedicated button to generate additional captions for the same uploaded image without re-uploading.
* **Clear All Functionality:** A "Clear All" button in the sidebar to reset the application, removing all uploaded images and generated content.



## 📂 Project Structure
```
├── .env # Environment variables (e.g., OpenAI API Key - for local dev)
├── .gitignore# Specifies intentionally untracked files to ignore
├── app.py                # Main Streamlit application script
├── captioning.py         # (Legacy) Original local captioning logic (not used in current version)
├── requirements.txt      # Python dependencies required for the project
├── README.md             # Project documentation (this file
└── utils/                # Utility functions
        ├── init.py               # Makes 'utils' a Python package
        └── translator.py         # Contains OpenAI-based translation logic
```
## 🚀 Setup and Installation

Follow these steps to get the application up and running on your local machine.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Bruhadev45/llm-caption-generator.git](https://github.com/Bruhadev45/llm-caption-generator.git)
    cd llm-caption-generator
    # If your app.py is in a subfolder like 'llm-comfyui-captioning', navigate there:
    # cd llm-comfyui-captioning
    ```

2.  **Create a Virtual Environment (Recommended):**
    A virtual environment isolates your project's dependencies from your system's Python packages.
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    * **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Dependencies:**
    Install all required Python libraries using `pip`.
    ```bash
    pip install -r requirements.txt --user
    ```
    * The `--user` flag is recommended to avoid potential permission issues during installation, especially on Windows.

5.  **Configure OpenAI API Key:**
    This application requires an OpenAI API key to access the captioning and translation models. **You must set this up for the app to function.**

    * **Obtain Your API Key:** If you don't have one, get your API key from the [OpenAI Platform](https://platform.openai.com/api-keys).
    * **Create `.env` file for Local Development:**
        For running the app locally, create a new file named `.env` in the root directory of your project (the same directory where `app.py` is located).
        Add your API key to this `.env` file in the following format:
        ```
        OPENAI_API_KEY="YOUR_ACTUAL_OPENAI_API_KEY_HERE"
        ```
        **Important:** Replace `"YOUR_ACTUAL_OPENAI_API_KEY_HERE"` with your real OpenAI API key. **Never commit your `.env` file to public version control, as it contains sensitive information.**
    * **Deployment (Streamlit Community Cloud Secrets):**
        When deploying to Streamlit Community Cloud, you should use their secure secrets management. In your app's settings on the Streamlit dashboard, add a new secret named `OPENAI_API_KEY` and paste your API key as its value. Streamlit will securely provide this to your running app.

6.  **Run the Streamlit Application:**
    Once all dependencies are installed and your API key is configured, run the app:
    ```bash
    streamlit run app.py
    ```
    This command will open the application in your default web browser.

## 💡 Usage

1.  **Upload Images:** Use the file uploader on the left sidebar to select **one or more** images (JPG, JPEG, or PNG).
2.  **Customize Options:**
    * **Caption Style:** Choose a style (e.g., "Humorous", "Professional") from the dropdown to influence the caption's tone.
    * **Number of Captions:** Use the slider to specify how many distinct captions (1 to 10) you want to generate initially for each image.
    * **Enable Translation:** Check this box if you want the captions to be translated.
    * **Translate to:** Select your desired Indian language for translation.
3.  **View Results:** The uploaded images will be displayed, followed by their generated captions and translations (if enabled).
4.  **Generate More:** Click the "Generate Another Caption for [Image Name]" button below each image to get additional captions for that specific image based on your current style and number of captions settings.
5.  **Clear All:** Click the "Clear All" button in the sidebar to reset the application, removing all uploaded images and generated content, and clearing the file uploader.

## 🧠 Models Used

* **Image Captioning:** OpenAI GPT-4o (Vision)
* **Translation:** OpenAI GPT-3.5 Turbo

## ⚠️ Important Notes

* **API Costs:** Using the OpenAI API incurs costs based on your usage (tokens consumed for both image analysis and text generation/translation). Monitor your usage on the [OpenAI Platform](https://platform.openai.com/usage).
* **Internet Connection:** An active internet connection is required for the application to communicate with the OpenAI API.
* **Error Handling:** The app includes basic error handling for API calls. If you encounter issues, check your terminal for debug messages.

## 🤝 Contributing

Feel free to fork this repository, open issues, or submit pull requests to improve the application.

## 📄 License

This project is open-source and available under the MIT License.
