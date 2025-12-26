import os
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
import streamlit as st

class LLMFactory:
    @staticmethod
    def get_model(mode="OPENAI", model_type="text"):
        """
        Factory method to return the configured LLM.
        mode: "OPENAI" or "LOCAL"
        model_type: "text" (standard reasoning) or "vision" (multimodal)
        """

        if mode == "OPENAI":
            # Quick start, high performance
            # GPT-4o is multimodal by default, handling both text and vision
            return ChatOpenAI(
                model="gpt-5.2-2025-12-11",
                temperature=0,
                api_key=st.secrets["openai"]["OPENAI_API_KEY"]
            )

        elif mode == "LOCAL":
            # Cost-effective, private, slower setup
            if model_type == "vision":
                return ChatOllama(model="llava")  # Open source vision
            return ChatOllama(model="llama3")  # Open source text

        else:
            raise ValueError("Unknown LLM Provider")

# Usage in your main app:
# llm = LLMFactory.get_model(mode="OPENAI")