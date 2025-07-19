
# 📷 Image Captioning & Translation App with OpenAI

This Streamlit application provides an advanced solution for generating descriptive captions for images and translating them into various Indian languages. It leverages the power of OpenAI's latest multimodal and language models, along with Retrieval-Augmented Generation (RAG), to deliver accurate and contextually relevant results.

## ✨ Features

- **Advanced Image Captioning:** Utilizes OpenAI's `gpt-4o` (Vision) model to generate highly detailed and context-aware captions for uploaded images.
- **Retrieval-Augmented Generation (RAG):** Enhances caption quality and relevance by searching your personal caption database for similar images/captions. If enabled, the model uses these previous captions as context, making generated descriptions more accurate and consistent with your own data. If no relevant captions are found, it will clearly indicate so.
- **Multi-Image Upload:** Supports uploading multiple images at once, allowing for batch processing and comparison of captions.
- **Multiple Caption Variations:** Generate up to 10 distinct caption options for a single image, allowing users to choose the most suitable description.
- **Customizable Caption Style:** Select from various styles (e.g., "Concise," "Descriptive," "Humorous," "Poetic," "Professional") to tailor the tone and focus of the generated captions.
- **Indian Language Translation:** Translate captions into a wide range of Indian languages using OpenAI's `gpt-3.5-turbo` model, with improved accuracy for natural-sounding translations.
- **Interactive UI:** Built with Streamlit for a user-friendly and responsive web interface.
- **Generate More Captions:** A dedicated button to generate additional captions for the same uploaded image without re-uploading.
- **Clear All Functionality:** A "Clear All" button in the sidebar to reset the application, removing all uploaded images and generated content.

---

## 🛠️ How to Use the RAG Feature

- **Enable RAG Context:** In the left sidebar, toggle the "Use RAG context for new captions" switch before generating captions.  
- **What It Does:**  
  When enabled, the app will search your personal caption database for previously generated captions that are similar to the current image's generated caption.
- **Automatic Context:**  
  If a relevant match is found, these captions will be shown and used to help the AI create even better, more consistent descriptions.
- **No Match?**  
  If there are no similar captions in your database, the app will display “No relevant caption found for this image.” and proceed without using additional context.
- **Best Use Cases:**  
  Enable RAG if you want your captioning to reflect your style or terminology across many images—great for branding, product catalogs, or domain-specific work.

---

## 📂 Project Structure

.
├── .env                # Environment variables (e.g., OpenAI API Key - for local dev)
├── .gitignore          # Specifies intentionally untracked files to ignore
├── app.py              # Main Streamlit application script
├── captioning.py       # (Legacy) Original local captioning logic (not used in current version)
├── requirements.txt    # Python dependencies required for the project
├── README.md           # Project documentation (this file)
└── utils/              # Utility functions
    ├── __init__.py         # Makes 'utils' a Python package
    ├── translator.py       # Contains OpenAI-based translation logic
    └── vectordb.py         # Contains in-memory vector search (RAG logic)


---

## 🚀 Setup and Installation

_Follow these steps to get the application up and running on your local machine._

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Bruhadev45/llm-caption-generator.git
    cd llm-caption-generator
    ```

2.  **Create a Virtual Environment (Recommended):**
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
    ```bash
    pip install -r requirements.txt --user
    ```

5.  **Configure OpenAI API Key:**

    - **Obtain Your API Key:** Get your API key from the [OpenAI Platform](https://platform.openai.com/api-keys).
    - **Create `.env` file for Local Development:**
        ```
        OPENAI_API_KEY="YOUR_ACTUAL_OPENAI_API_KEY_HERE"
        ```
        > **Never commit your `.env` file to public version control, as it contains sensitive information.
    - **Deployment (Streamlit Community Cloud Secrets):**
        Use Streamlit’s [secrets management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management) to add your `OPENAI_API_KEY`.

6.  **Run the Streamlit Application:**
    ```bash
    streamlit run app.py
    ```
    This command will open the application in your default web browser.

---

## 💡 Usage

1.  **Upload Images:** Use the file uploader on the left sidebar to select **one or more** images (JPG, JPEG, or PNG).
2.  **Customize Options:**
    * **Caption Style:** Choose a style (e.g., "Humorous", "Professional") from the dropdown to influence the caption's tone.
    * **Number of Captions:** Use the slider to specify how many distinct captions (1 to 10) you want to generate for each image.
    * **Enable Translation:** Check this box if you want the captions to be translated.
    * **Translate to:** Select your desired Indian language for translation.
    * **Enable RAG (Use RAG context):** Toggle this feature if you want the model to search your previous captions for relevant examples before generating a new caption. If no relevant context is found, you’ll see a message indicating so.
3.  **View Results:** The uploaded images will be displayed, followed by their generated captions, translations (if enabled), and any retrieved context (if RAG is used).
4.  **Generate More:** Click the "Generate Another Caption for [Image Name]" button below each image to get additional captions for that specific image.
5.  **Clear All:** Click the "Clear All" button in the sidebar to reset the application.

---

## 🧠 Models Used

- **Image Captioning:** OpenAI GPT-4o (Vision)
- **Translation:** OpenAI GPT-3.5 Turbo
- **RAG/Vector Search:** In-memory vector search with sentence-transformers for similarity (no external database needed)

---

## ⚠️ Important Notes

- **API Costs:** Using the OpenAI API incurs costs based on your usage (tokens consumed for both image analysis and text generation/translation). Monitor your usage on the [OpenAI Platform](https://platform.openai.com/usage).
- **Internet Connection:** An active internet connection is required for the application to communicate with the OpenAI API.
- **Error Handling:** The app includes basic error handling for API calls. If you encounter issues, check your terminal for debug messages.

---

## 🤝 Contributing

Feel free to fork this repository, open issues, or submit pull requests to improve the application.

---

## 📄 License

This project is open-source and available under the MIT License.


