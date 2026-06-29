# Games Knowledge RAG Chatbot

A question-answering chatbot that knows about **video games** — "tell me about
Hollow Knight", "what are some good roguelikes?", "when did Elden Ring release
and what's its Metacritic?" — built with **FastAPI** and **Retrieval-Augmented
Generation (RAG)** over the real [RAWG](https://rawg.io/apidocs) games database
(350,000+ games). Every answer is grounded in retrieved facts and comes with its
**sources**, so it doesn't make things up.

This repo is also a **RAG tutorial in code**: each file is one stage of the
pipeline, with comments explaining *why* it exists. Read the files in this order:
`chunking.py` → `embeddings.py` → `vector_store.py` → `rag.py`.

---

## RAG (read this first)

An LLM on its own only knows what it saw during training. It doesn't know your
data, and it will confidently make up answers ("hallucinate"). **RAG fixes this
by fetching relevant facts at question-time and putting them in front of the model
before it answers.** Three ideas make it work:

1. **Embeddings** — a model turns any text into a vector (a list of numbers) that
   captures its *meaning*. Texts about similar things end up close together in
   vector space. This is how we find relevant info by *meaning*, not keywords —
   "soulslike" can match "Dark Souls" even with no shared words.

2. **Vector store** — a database that holds those vectors and, given a query
   vector, returns the closest ones fast. It IS the knowledge base.

3. **Grounded generation** — we retrieve the top-k closest chunks, paste them into
   the prompt as context, and tell the LLM "answer using only this." The model
   writes fluent prose; the facts come from your data.

The full flow:

```
INGEST (once):
  RAWG games ──► build documents ──► chunk ──► embed ──► store in vector DB

ASK (every question):
  question ──► embed ──► search vector DB ──► top-k chunks ──► LLM ──► answer + sources
                         (retrieval)                          (augmented generation)
```

That last line is literally what `rag.py` does.

---

## How each file maps to the pipeline

| File              | Pipeline stage           | What to learn from it                          |
|-------------------|--------------------------|------------------------------------------------|
| `rawg_client.py`  | Load                     | turning a data source into documents + metadata|
| `chunking.py`     | Split                    | why/how to break text into overlapping chunks  |
| `embeddings.py`   | Embed                    | text → vectors with a free local model         |
| `vector_store.py` | Store + Search           | the heart of RAG; the swap-seam for pgvector   |
| `ingest.py`       | the whole INGEST flow    | how the pieces compose into a build step       |
| `llm.py`          | Generate                 | the prompt that stops hallucination            |
| `rag.py`          | retrieve → generate      | RAG itself, in ~30 lines                        |
| `main.py`         | serve                    | exposing it as a FastAPI API                    |

---

## Tech stack 

- **FastAPI** + Uvicorn — the API layer
- **sentence-transformers** `all-MiniLM-L6-v2` — embeddings, runs **locally for free**
- **ChromaDB** — local vector store (persists to disk, zero config)
- **Groq** (Llama 3.3, free tier) — the LLM for generation; OpenAI is a drop-in option
- **RAWG API** — the games knowledge source (free key)

Why these: they're the standard RAG building blocks, and every one is free to run
so you can learn the concepts without a bill. Each is swappable (see the roadmap).

---

## Setup

```bash
# 1. Get two free API keys:
#    - RAWG: https://rawg.io/apidocs   (the games data)
#    - Groq: https://console.groq.com  (the LLM)
cp .env.example .env        # then paste your keys into .env

# 2. Install
python -m venv venv && source venv/scripts/activate
uv pip install -r requirements.txt

# 3. Build the knowledge base (downloads the embedding model on first run)
python ingest.py --total 1000        # ~1000 popular games; bump to 2000 for breadth

# 4. Run the API
uvicorn main:app --reload

# 5. for Frontend -- optional but recommended
cd frontend 
npm install
npm run dev

```

Open **http://localhost:8000/docs** — FastAPI's interactive Swagger UI. Try `/chat`
right there, no frontend needed.

---

## Using it

```bash
# Ask a question
curl -X POST localhost:8000/chat -H "Content-Type: application/json" \
  -d '{"question": "what are some good soulslike games?"}'

# See what retrieval actually found (great for understanding RAG)
curl -X POST localhost:8000/search -H "Content-Type: application/json" \
  -d '{"question": "open world RPG with dragons"}'
```

`/chat` returns `{"answer": "...", "sources": [{"name": "...", "score": 0.83}, ...]}`.
The `/search` endpoint exists on purpose: it shows the raw retrieved chunks, so when
an answer is wrong you can see whether the problem was **retrieval** (wrong chunks
came back) or **generation** (right chunks, bad answer). That distinction is the
core skill of RAG debugging.

Run the tests anytime: `pytest test_rag.py`

---

## Build roadmap (how to go from "works" to "impressive")

**Phase 1 — Working RAG (you are here).** Local embeddings + Chroma + Groq, grounded
answers with sources, served over FastAPI. Goal: ask real questions, watch `/search`.

**Phase 2 — Swap Chroma for pgvector (plays to your Postgres strength).** Re-implement
`vector_store.py` against PostgreSQL + the `pgvector` extension. Same interface, real
database, and it shows you understand vector search at the SQL level — a strong signal
given your background.

**Phase 3 — Better retrieval.** Add a **reranker** (a cross-encoder that re-scores the
top-20 down to the best 5) and **hybrid search** (combine keyword + vector). Add
**conversation memory** so follow-ups like "what about its sequel?" work. This is where
answer quality jumps.

**Phase 4 — Evaluation (the part most portfolios skip).** Build a small eval set of
question→expected-answer pairs and measure retrieval + answer quality with **RAGAS**
(faithfulness, answer relevancy, context precision). Put the before/after numbers in
this README — that's what makes it look like real engineering.

**Phase 5 — Deploy + observe.** Containerise with Docker, add request logging and
token/cost metering, and deploy. Add a tiny chat UI (or keep it API-only and show the
Swagger docs in your demo).


## Project layout

```
games-rag/
├── config.py          # settings + env/keys
├── rawg_client.py     # fetch games -> documents (the knowledge source)
├── chunking.py        # split long text into overlapping chunks
├── embeddings.py      # text -> vectors (local, free)
├── vector_store.py    # ChromaDB: store + similarity search  (swap seam)
├── ingest.py          # run once: fetch -> chunk -> embed -> store
├── llm.py             # the grounded-answer prompt + provider (Groq/OpenAI)
├── rag.py             # retrieve -> generate -> answer + sources  (RAG itself)
├── main.py            # FastAPI app: /health /chat /search
├── test_rag.py        # offline tests (no API keys needed)
├── requirements.txt
├── .env.example
└── .gitignore
```
