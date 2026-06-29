import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { register as apiRegister } from "../api"

export default function Register() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPw, setConfirmPw] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError("")
    if (password !== confirmPw) {
      setError("Passwords do not match")
      return
    }
    setLoading(true)
    try {
      await apiRegister(username, password)
      navigate("/login")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Game RAG</h1>
        <p className="auth-subtitle">Create a new account</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input id="username" type="text" value={username}
              onChange={e => setUsername(e.target.value)} required minLength={3} />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={password}
              onChange={e => setPassword(e.target.value)} required minLength={6} />
          </div>
          <div className="form-group">
            <label htmlFor="confirm">Confirm Password</label>
            <input id="confirm" type="password" value={confirmPw}
              onChange={e => setConfirmPw(e.target.value)} required minLength={6} />
          </div>
          {error && <p className="form-error">{error}</p>}
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create Account"}
          </button>
        </form>
        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
