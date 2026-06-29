"""Run ONCE to build the knowledge base:

    fetch games (RAWG) -> build documents -> chunk -> embed -> store in Chroma

Usage:
    python ingest.py --total 300        # ~300 popular games (a good first run)
    python ingest.py --total 2000       # broader coverage (slower)
"""
from __future__ import annotations

import argparse

from chunking import chunk_text
from config import settings
from embeddings import get_embedder
from rawg_client import RawgClient, game_to_document
from vector_store import VectorStore


def main(total: int) -> None:
    if not settings.rawg_api_key:
        raise SystemExit("Set RAWG_API_KEY in .env (get a free key at https://rawg.io/apidocs)")

    print(f"1/4  Fetching {total} games from RAWG...")
    games = RawgClient(settings.rawg_api_key, settings.rawg_base_url).fetch_games(total=total)
    print(f"     got {len(games)} games")

    print("2/4  Chunking documents...")
    ids, documents, metadatas = [], [], []
    for game in games:
        text, meta = game_to_document(game)
        for i, chunk in enumerate(chunk_text(text, settings.chunk_size, settings.chunk_overlap)):
            ids.append(f"{meta['game_id']}-{i}")
            documents.append(chunk)
            metadatas.append(meta)
    print(f"     {len(documents)} chunks")

    print("3/4  Embedding chunks (first run downloads the model)...")
    embeddings = get_embedder(settings.embedding_model).embed(documents)

    print("4/4  Storing in Chroma...")
    store = VectorStore(settings.chroma_path, settings.collection_name)
    BATCH = 1000
    for s in range(0, len(ids), BATCH):
        store.add(ids[s:s + BATCH], embeddings[s:s + BATCH],
                  documents[s:s + BATCH], metadatas[s:s + BATCH])

    print(f"Done. Knowledge base now holds {store.count()} chunks.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--total", type=int, default=300, help="number of games to ingest")
    main(ap.parse_args().total)
