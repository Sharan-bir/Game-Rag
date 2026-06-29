"""Fetches games from the RAWG API and turns each into a text document.

This is the KNOWLEDGE SOURCE for the chatbot. Each game becomes one document
that fuses its prose description with structured facts (genres, platforms,
release date, ratings, tags), so the bot can answer both "tell me about X"
and "what are some good roguelikes" style questions from the same store.
"""
from __future__ import annotations

import time

import httpx


class RawgClient:
    def __init__(self, api_key: str, base_url: str = "https://api.rawg.io/api") -> None:
        self.api_key = api_key
        self.base_url = base_url

    def fetch_games(self, total: int = 300, ordering: str = "-added") -> list[dict]:
        """Fetch `total` games (paginated, 40/page), most-popular first."""
        games: list[dict] = []
        page = 1
        with httpx.Client(timeout=30) as client:
            while len(games) < total:
                resp = client.get(
                    f"{self.base_url}/games",
                    params={
                        "key": self.api_key,
                        "ordering": ordering,
                        "page": page,
                        "page_size": 40,
                    },
                )
                resp.raise_for_status()
                results = resp.json().get("results", [])
                if not results:
                    break
                for g in results:
                    games.append(self._fetch_detail(client, g["id"]))
                    if len(games) >= total:
                        break
                page += 1
                time.sleep(0.3)  # be polite to the API
        return games

    def _fetch_detail(self, client: httpx.Client, game_id: int) -> dict:
        # the list endpoint omits description_raw; the detail endpoint has it
        resp = client.get(f"{self.base_url}/games/{game_id}", params={"key": self.api_key})
        resp.raise_for_status()
        return resp.json()


def game_to_document(game: dict) -> tuple[str, dict]:
    """Build (text, metadata) for one game."""
    name = game.get("name", "Unknown")
    released = game.get("released") or "unknown date"
    genres = ", ".join(g["name"] for g in game.get("genres", []) or []) or "n/a"
    platforms = ", ".join(
        p["platform"]["name"] for p in game.get("platforms", []) or []
    ) or "n/a"
    developers = ", ".join(d["name"] for d in game.get("developers", []) or []) or "n/a"
    metacritic = game.get("metacritic") or "n/a"
    rating = game.get("rating") or "n/a"
    tags = ", ".join(t["name"] for t in (game.get("tags") or [])[:10]) or "n/a"
    description = game.get("description_raw") or ""

    text = (
        f"{name} (released {released})\n"
        f"Genres: {genres}\n"
        f"Platforms: {platforms}\n"
        f"Developers: {developers}\n"
        f"Metacritic: {metacritic} | User rating: {rating}/5\n"
        f"Tags: {tags}\n\n"
        f"{description}"
    )
    metadata = {
        "game_id": game.get("id"),
        "name": name,
        "released": released,
        "genres": genres,
        "metacritic": str(metacritic),
    }
    return text, metadata
