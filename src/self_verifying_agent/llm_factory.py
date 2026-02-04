from __future__ import annotations

import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_llm(model_name: str = "llama-3.1-8b-instant", temperature: float = 0.2) -> ChatGroq:
    """Returns a ChatGroq LLM instance.
    
    Defaults to llama-3.1-8b-instant if not specified.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
        
    return ChatGroq(
        model_name=model_name,
        temperature=temperature,
        groq_api_key=api_key
    )
