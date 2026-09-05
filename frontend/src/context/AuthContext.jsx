import { createContext, useContext, useState, useMemo } from 'react'
import { jwtDecode } from 'jwt-decode'

const AuthContext = createContext(null)
const STORAGE_KEY = 'landobservator_jwt'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(STORAGE_KEY))

  const user = useMemo(() => {
    if (!token) return null
    try {
      const payload = jwtDecode(token)
      return { name: payload.name, email: payload.email, organization: payload.organization }
    } catch {
      return null
    }
  }, [token])

  function login(jwt) {
    localStorage.setItem(STORAGE_KEY, jwt)
    setToken(jwt)
  }

  function logout() {
    localStorage.removeItem(STORAGE_KEY)
    setToken(null)
  }

  const value = { token, user, isAuthenticated: token !== null, login, logout }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}