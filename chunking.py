"""Tiny, dependency-free text chunker.

WHY CHUNK? Embedding models have a token limit, and -- more importantly --
retrieval works best when each stored piece is a single focused idea.
Splitting long text into overlapping chunks lets a query match the exact
relevant passage instead of a whole document. The overlap stops a sentence
that straddles a boundary from being cut clean in half.
"""
from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    text = " ".join(text.split())  # normalise whitespace
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            # prefer to break on a sentence/word boundary in the back half
            window = text[start:end]
            for sep in (". ", "! ", "? ", " "):
                idx = window.rfind(sep)
                if idx != -1 and idx > chunk_size * 0.5:
                    end = start + idx + len(sep)
                    break
        chunks.append(text[start:end].strip())
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]
