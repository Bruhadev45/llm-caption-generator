# 🧠 LLM-Powered Image Caption Generator

A Streamlit web app that uses BLIP (Bootstrapped Language Image Pretraining) from Salesforce to generate intelligent captions for uploaded images. Built with Hugging Face Transformers, PyTorch, and Google Translate API.

## 🚀 Features

- Upload **multiple images**
- Choose between BLIP **base or large** models
- Optional **caption translation** to Telugu 🇮🇳
- Clean UI with live feedback

## 🛠 Tech Stack

- [Streamlit](https://streamlit.io/)
- [HuggingFace Transformers](https://huggingface.co/)
- [BLIP Model](https://huggingface.co/Salesforce/blip-image-captioning-base)
- [googletrans](https://pypi.org/project/googletrans/)

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/llm-caption-generator.git
cd llm-caption-generator
pip install -r requirements.txt
streamlit run app.py
