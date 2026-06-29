"""The GENERATION step: given the question + retrieved game context, ask an
LLM to write a grounded answer.

The provider is pluggable (Groq by default -- free and fast -- or OpenAI).
The system prompt forces the model to answer ONLY from the supplied context
and to admit when it doesn't know. That instruction is the single biggest
lever against hallucination in a RAG system.
"""
from __future__ import annotations

from config import settings

SYSTEM_PROMPT = (
    "You are a knowledgeable video-game assistant. Answer the user's question "
    "using ONLY the game information in the provided context. If the context "
    "does not contain the answer, say you don't have that game in your knowledge "
    "base -- never invent facts, dates, or ratings. Mention the game names you used."
)


def build_prompt(question: str, contexts: list[str]) -> str:
    joined = "\n\n---\n\n".join(contexts)
    return (
        f"Context (retrieved game info):\n{joined}\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the context above."
    )


class GroqLLM:
    def __init__(self, api_key: str, model: str) -> None:
        from groq import Groq  # lazy import
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(self, question: str, contexts: list[str]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(question, contexts)},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content


class OpenAILLM:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI  # lazy import
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, question: str, contexts: list[str]) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(question, contexts)},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content


def get_llm():
    if settings.llm_provider == "openai":
        return OpenAILLM(settings.openai_api_key, settings.openai_model)
    return GroqLLM(settings.groq_api_key, settings.groq_model)
