import { createContext, useContext, useState, type ReactNode } from "react"
import { isAuthenticated, clearToken, setToken } from "./api"

interface AuthContext {
  loggedIn: boolean
  login: (token: string) => void
  logout: () => void
}

const AuthCtx = createContext<AuthContext>(null!)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [loggedIn, setLoggedIn] = useState(isAuthenticated())

  const login = (t: string) => {
    setToken(t)
    setLoggedIn(true)
  }

  const logout = () => {
    clearToken()
    setLoggedIn(false)
  }

  return (
    <AuthCtx.Provider value={{ loggedIn, login, logout }}>
      {children}
    </AuthCtx.Provider>
  )
}

export function useAuth() {
  return useContext(AuthCtx)
}
