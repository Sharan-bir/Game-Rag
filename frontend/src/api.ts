const BASE = ""

function token(): string | null {
  return localStorage.getItem("token")
}

export function setToken(t: string) {
  localStorage.setItem("token", t)
}

export function clearToken() {
  localStorage.removeItem("token")
}

export function isAuthenticated(): boolean {
  return !!token()
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  const t = token()
  if (t) headers["Authorization"] = `Bearer ${t}`
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const detail = (await res.json().catch(() => ({}))).detail || res.statusText
    throw new Error(detail)
  }
  return res.json()
}

export interface User {
  id: number
  username: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export function register(username: string, password: string) {
  return request<User>("POST", "/auth/register", { username, password })
}

export async function login(username: string, password: string) {
  const data = await request<TokenResponse>("POST", "/auth/login", { username, password })
  setToken(data.access_token)
  return data
}

export interface Source {
  name: string | null
  released: string | null
  genres: string | null
  metacritic: string | null
  background_image: string | null
  platforms: string | null
  developers: string | null
  rating: string | null
  tags: string | null
  score: number
}

export interface ChatResponse {
  answer: string
  sources: Source[]
}

export function chat(question: string) {
  return request<ChatResponse>("POST", "/chat", { question })
}

export interface SearchHit {
  document: string
  metadata: Record<string, unknown>
  distance: number
}

export interface SearchResponse {
  hits: SearchHit[]
}

export function search(question: string) {
  return request<SearchResponse>("POST", "/search", { question })
}

export interface HealthResponse {
  status: string
  chunks_indexed: number
}

export function health() {
  return request<HealthResponse>("GET", "/health")
}
