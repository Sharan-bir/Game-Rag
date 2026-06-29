import { useState, useRef, useEffect, type FormEvent } from "react"
import { chat, type Source, type ChatResponse } from "../api"

interface Message {
  role: "user" | "bot"
  text: string
  sources?: Source[]
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "bot", text: "Ask me anything about video games!" },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const q = input.trim()
    if (!q || loading) return

    setInput("")
    setError("")
    setMessages(prev => [...prev, { role: "user", text: q }])
    setLoading(true)

    try {
      const data: ChatResponse = await chat(q)
      setMessages(prev => [...prev, { role: "bot", text: data.answer, sources: data.sources }])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed")
      setLoading(false)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="msg-content">{m.text}</div>
            {m.sources && m.sources.length > 0 && (
              <div className="msg-sources">
                <p className="sources-label">Sources:</p>
                <div className="sources-grid">
                  {m.sources.map((s, j) => (
                    <GameSourceCard key={j} source={s} />
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="msg-content typing">
              <span className="dot-pulse" />
            </div>
          </div>
        )}
        {error && <p className="form-error">{error}</p>}
        <div ref={bottomRef} />
      </div>

      <form className="chat-input-bar" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about a game..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

function GameSourceCard({ source }: { source: Source }) {
  const hasImg = source.background_image
  return (
    <div className="source-card">
      {hasImg && (
        <img className="source-img" src={source.background_image!} alt={source.name ?? ""} loading="lazy" />
      )}
      <div className="source-body">
        <strong>{source.name ?? "Unknown"}</strong>
        <div className="source-meta">
          {source.released && <span>{source.released}</span>}
          {source.genres && source.genres !== "n/a" && <span>{source.genres}</span>}
          {source.metacritic && source.metacritic !== "n/a" &&
            <span className="meta-score">MC {source.metacritic}</span>}
          {source.rating && source.rating !== "n/a" &&
            <span>Rating: {source.rating}/5</span>}
          {source.developers && source.developers !== "n/a" && <span>{source.developers}</span>}
        </div>
        <span className="source-score">Relevance: {(source.score * 100).toFixed(0)}%</span>
      </div>
    </div>
  )
}
