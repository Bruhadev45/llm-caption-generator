# 🧠 LLM-Powered Image Caption Generator

A professional, user-friendly Streamlit app to generate intelligent image captions using Salesforce BLIP, and translate them to any language using Google Translate.

## 🚀 Features

- Upload multiple images and get captions instantly
- Select between BLIP base or large models
- Optional: Translate captions to **any language** (over 100 supported)
- Device auto-detection (GPU/CPU)
- Modern, polished UI with side-by-side results, timing, spinners, and cards
- "Regenerate" button for improved caption quality
- Modular codebase, ready for future LLM (e.g. GPT) rewriting

## 🛠 Tech Stack

- Streamlit
- HuggingFace Transformers (BLIP)
- PyTorch
- Googletrans (Translation)
- Python 3.8+

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/llm-caption-generator.git
cd llm-caption-generator
pip install -r requirements.txt
streamlit run app.py
