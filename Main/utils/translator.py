import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm_translator = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.4)

def translate_with_openai(text: str, target_lang_code: str, target_lang_name: str) -> str:
    from langchain.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are an expert translator. Translate the following English sentence to high-quality, natural-sounding {target_lang_name}. Reply with only the translation."),
        ("user", "{sentence}")
    ])
    try:
        result = llm_translator.invoke(prompt.format_prompt(sentence=text).to_messages())
        return result.content
    except Exception as e:
        return f"❌ LangChain Translation Error: {e}"

