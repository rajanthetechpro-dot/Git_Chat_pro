import os
from typing import Any, Tuple
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.llms.groq import Groq
from llama_index.llms.anthropic import Anthropic
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding

class LLMService:
    @staticmethod
    def get_llm(
        provider: str, 
        model_name: str, 
        api_key: str = "", 
        temperature: float = 0.1
    ) -> Any:
        """
        Instantiates the corresponding LlamaIndex LLM model based on provider and configurations.
        """
        # Clean API Key whitespace
        api_key = api_key.strip() if api_key else ""
        
        # Load key from environment if not provided explicitly
        if not api_key:
            if "OpenAI" in provider:
                api_key = os.getenv("OPENAI_API_KEY", "")
            elif "Groq" in provider:
                api_key = os.getenv("GROQ_API_KEY", "")
            elif "Anthropic" in provider:
                api_key = os.getenv("ANTHROPIC_API_KEY", "")

        if "Ollama" in provider:
            # Local Ollama setup
            return Ollama(
                model=model_name, 
                temperature=temperature,
                request_timeout=180.0
            )
            
        elif "OpenAI" in provider:
            if not api_key:
                raise ValueError("OpenAI API key is missing. Set it in a .env file or input it in the sidebar.")
            return OpenAI(
                model=model_name, 
                api_key=api_key, 
                temperature=temperature
            )

        elif "Groq" in provider:
            if not api_key:
                raise ValueError("Groq API key is missing. Set GROQ_API_KEY in a .env file or input it in the sidebar.")
            return Groq(
                model=model_name,
                api_key=api_key,
                temperature=temperature
            )
            
        elif "Anthropic" in provider:
            if not api_key:
                raise ValueError("Anthropic API key is missing. Set it in a .env file or input it in the sidebar.")
            return Anthropic(
                model=model_name, 
                api_key=api_key, 
                temperature=temperature
            )
            
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def get_embedding(
        provider: str, 
        embed_name: str, 
        api_key: str = ""
    ) -> Any:
        """
        Instantiates the corresponding LlamaIndex Embedding model.
        """
        api_key = api_key.strip() if api_key else ""
        
        # Load key from environment if not provided explicitly
        if not api_key:
            if "OpenAI" in provider:
                api_key = os.getenv("OPENAI_API_KEY", "")

        # Select embedding model
        if "Ollama" in provider or "Anthropic" in provider or "Groq" in provider or embed_name.startswith("BAAI") or "nomic" in embed_name:
            # Local Embedding setup using HuggingFace
            # Note: We fallback to HuggingFace for Anthropic since Anthropic doesn't provide embeddings natively
            model_name = embed_name if embed_name else "BAAI/bge-large-en-v1.5"
            return HuggingFaceEmbedding(
                model_name=model_name, 
                trust_remote_code=True
            )
            
        elif "OpenAI" in provider:
            if not api_key:
                raise ValueError("OpenAI API key is required for OpenAI embeddings. Set it in a .env file or input it in the sidebar.")
            return OpenAIEmbedding(
                model=embed_name, 
                api_key=api_key
            )
            
        else:
            # General fallback to local
            return HuggingFaceEmbedding(
                model_name="BAAI/bge-large-en-v1.5", 
                trust_remote_code=True
            )
