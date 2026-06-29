"""Central configuration. Secrets come from environment / .env."""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # --- data source (RAWG games API) ---
    rawg_api_key: str = os.getenv("RAWG_API_KEY", "")
    rawg_base_url: str = "https://api.rawg.io/api"

    # --- embeddings (local, free) ---
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # --- vector store ---
    chroma_path: str = os.getenv("CHROMA_PATH", "./chroma_db")
    collection_name: str = "games"

    # --- chunking ---
    chunk_size: int = 800
    chunk_overlap: int = 120

    # --- retrieval ---
    top_k: int = 5

    # --- LLM (generation) ---
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")  # "groq" or "openai"
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


settings = Settings()
