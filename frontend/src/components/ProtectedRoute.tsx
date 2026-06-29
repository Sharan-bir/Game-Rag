import { type ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "../auth"

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { loggedIn } = useAuth()
  if (!loggedIn) return <Navigate to="/login" replace />
  return <>{children}</>
}
