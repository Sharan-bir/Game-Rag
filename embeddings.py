"""Turns text into vectors (embeddings).

An embedding is a list of numbers that captures the *meaning* of text:
passages with similar meaning land close together in vector space, so we
can find relevant text by measuring distance instead of matching keywords.
We use a small open model (all-MiniLM-L6-v2, 384 dims) that runs locally
for free -- no API key, no per-call cost.
"""
from __future__ import annotations

from functools import lru_cache


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer  # lazy import
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        # normalise so cosine similarity == dot product
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return vecs.tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


@lru_cache(maxsize=1)
def get_embedder(model_name: str = "all-MiniLM-L6-v2") -> Embedder:
    return Embedder(model_name)
