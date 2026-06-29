"""The RAG pipeline, end to end -- this file IS retrieval-augmented generation:

  1. embed the user's question with the SAME model used for the documents
  2. search the vector store for the top-k most similar chunks
  3. hand those chunks to the LLM as grounding context
  4. return the generated answer PLUS the sources it was built from

Steps 1-2 are "retrieval", step 3 is "augmented generation". That's the
whole idea: the LLM answers from facts you fetched, not just its memory.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RagAnswer:
    answer: str
    sources: list[dict]


class RagPipeline:
    def __init__(self, embedder, store, llm, top_k: int = 5) -> None:
        self.embedder = embedder
        self.store = store
        self.llm = llm
        self.top_k = top_k

    def answer(self, question: str) -> RagAnswer:
        query_vec = self.embedder.embed_one(question)          # 1. embed query
        hits = self.store.search(query_vec, top_k=self.top_k)  # 2. retrieve
        contexts = [h["document"] for h in hits]
        if not contexts:
            return RagAnswer("My knowledge base is empty -- run ingest.py first.", [])
        answer = self.llm.generate(question, contexts)         # 3. generate
        sources = [                                            # 4. cite
            {
                "name": h["metadata"].get("name"),
                "released": h["metadata"].get("released"),
                "genres": h["metadata"].get("genres"),
                "metacritic": h["metadata"].get("metacritic"),
                "background_image": h["metadata"].get("background_image"),
                "platforms": h["metadata"].get("platforms"),
                "developers": h["metadata"].get("developers"),
                "rating": h["metadata"].get("rating"),
                "tags": h["metadata"].get("tags"),
                "score": round(1 - h["distance"], 3),  # cosine distance -> similarity
            }
            for h in hits
        ]
        return RagAnswer(answer=answer, sources=sources)
