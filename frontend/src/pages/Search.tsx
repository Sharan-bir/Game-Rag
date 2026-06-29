import { useState, type FormEvent } from "react"
import { search, type SearchHit } from "../api"

export default function Search() {
  const [query, setQuery] = useState("")
  const [hits, setHits] = useState<SearchHit[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault()
    const q = query.trim()
    if (!q || loading) return
    setError("")
    setLoading(true)
    setSearched(true)
    try {
      const data = await search(q)
      setHits(data.hits)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="search-page">
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search games by description..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      {error && <p className="form-error" style={{ textAlign: "center", marginTop: 16 }}>{error}</p>}
      {searched && !loading && hits.length === 0 && !error && (
        <p className="empty-state">No results found.</p>
      )}
      <div className="search-results">
        {hits.map((hit, i) => (
          <GameHitCard key={i} hit={hit} />
        ))}
      </div>
    </div>
  )
}

function GameHitCard({ hit }: { hit: SearchHit }) {
  const meta = hit.metadata as Record<string, string | undefined>
  const img = meta.background_image
  return (
    <div className="hit-card">
      {img && (
        <img className="hit-img" src={img} alt={meta.name ?? ""} loading="lazy" />
      )}
      <div className="hit-body">
        <div className="hit-header">
          <strong>{meta.name ?? "Unknown"}</strong>
          <span className="hit-score">{(1 - hit.distance).toFixed(3)}</span>
        </div>
        <div className="hit-meta">
          {meta.released && <span>{meta.released}</span>}
          {meta.genres && meta.genres !== "n/a" && <span>{meta.genres}</span>}
          {meta.metacritic && meta.metacritic !== "n/a" &&
            <span className="meta-score">MC {meta.metacritic}</span>}
          {meta.rating && meta.rating !== "n/a" &&
            <span>Rating: {meta.rating}/5</span>}
          {meta.platforms && meta.platforms !== "n/a" && <span>{meta.platforms}</span>}
          {meta.developers && meta.developers !== "n/a" && <span>{meta.developers}</span>}
          {meta.tags && meta.tags !== "n/a" && <span className="hit-tags">{meta.tags}</span>}
        </div>
        <p className="hit-doc">{hit.document.slice(0, 400)}...</p>
      </div>
    </div>
  )
}
