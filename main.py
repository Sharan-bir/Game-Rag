"""FastAPI app exposing the games-knowledge RAG chatbot.

  GET  /health   -> liveness + how many chunks are indexed
  POST /chat     -> {question} -> {answer, sources}
  POST /search   -> {question} -> the raw retrieved chunks (for learning/debugging)

Run:  uvicorn main:app --reload
Docs: http://localhost:8000/docs   (interactive Swagger UI -- try it here first)
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from config import settings
from embeddings import get_embedder
from llm import get_llm
from rag import RagPipeline
from vector_store import VectorStore

pipeline: RagPipeline | None = None
store: VectorStore | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # build heavy objects once at startup, reuse across requests
    global pipeline, store
    embedder = get_embedder(settings.embedding_model)
    store = VectorStore(settings.chroma_path, settings.collection_name)
    pipeline = RagPipeline(embedder, store, get_llm(), settings.top_k)
    yield


app = FastAPI(title="Games Knowledge RAG", lifespan=lifespan)


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    name: str | None = None
    released: str | None = None
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health():
    return {"status": "ok", "chunks_indexed": store.count() if store else 0}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = pipeline.answer(req.question)
    return ChatResponse(answer=result.answer, sources=result.sources)


@app.post("/search")
def search(req: ChatRequest):
    """Returns raw retrieved chunks so you can SEE what retrieval found."""
    vec = pipeline.embedder.embed_one(req.question)
    return {"hits": store.search(vec, top_k=settings.top_k)}
