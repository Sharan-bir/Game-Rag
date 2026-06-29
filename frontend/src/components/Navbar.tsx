import { Link, useLocation, useNavigate } from "react-router-dom"
import { useAuth } from "../auth"

export default function Navbar() {
  const { loggedIn, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  if (!loggedIn) return null

  const linkClass = (path: string) =>
    `nav-link${location.pathname === path ? " active" : ""}`

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">Game RAG</Link>
      <div className="nav-links">
        <Link to="/" className={linkClass("/")}>Chat</Link>
        <Link to="/search" className={linkClass("/search")}>Search</Link>
        <button className="btn-outline btn-sm" onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  )
}
