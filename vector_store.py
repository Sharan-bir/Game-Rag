"""The vector store: holds chunk embeddings + metadata and runs the
similarity search at query time.

This is the heart of RAG -- ingestion fills it, the chatbot reads from it,
and nothing else needs to know how it works. Swapping ChromaDB for pgvector
or Qdrant later changes ONLY this file.
"""
from __future__ import annotations

from typing import Any


class VectorStore:
    def __init__(self, path: str, collection_name: str) -> None:
        import chromadb  # lazy import
        self.client = chromadb.PersistentClient(path=path)
        # we supply our own embeddings, so no embedding_function is needed
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def add(self, ids, embeddings, documents, metadatas) -> None:
        self.collection.add(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        res = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        hits: list[dict[str, Any]] = []
        for doc, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            hits.append({"document": doc, "metadata": meta, "distance": dist})
        return hits

    def count(self) -> int:
        return self.collection.count()
