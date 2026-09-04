/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useMemo, useState } from 'react'

const STORAGE_USER = 'landobservator_user'
const STORAGE_REQUESTS = 'landobservator_aoi_requests'

const AccountContext = createContext(null)

function loadJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

export function AccountProvider({ children }) {
  const [user, setUser] = useState(() => loadJson(STORAGE_USER, null))
  const [requests, setRequests] = useState(() => loadJson(STORAGE_REQUESTS, []))

  function persistUser(next) {
    setUser(next)
    if (next) localStorage.setItem(STORAGE_USER, JSON.stringify(next))
    else localStorage.removeItem(STORAGE_USER)
  }

  function persistRequests(next) {
    setRequests(next)
    localStorage.setItem(STORAGE_REQUESTS, JSON.stringify(next))
  }

  function signIn(email, password) {
    const existing = loadJson(STORAGE_USER, null)
    if (!existing || existing.email !== email) {
      return { ok: false, error: 'No account found for this email. Sign up first.' }
    }
    if (existing.password !== password) {
      return { ok: false, error: 'Incorrect password.' }
    }
    persistUser(existing)
    return { ok: true }
  }

  function signUp(name, email, password) {
    const stored = loadJson(STORAGE_USER, null)
    if (stored?.email === email) {
      return { ok: false, error: 'An account with this email already exists.' }
    }
    const account = {
      id: crypto.randomUUID(),
      name,
      email,
      password,
      createdAt: new Date().toISOString(),
    }
    persistUser(account)
    return { ok: true }
  }

  function signOut() {
    persistUser(null)
  }

  function submitAoiRequest(payload) {
    if (!user) return { ok: false, error: 'Sign in to request a personal AOI.' }
    const entry = {
      id: crypto.randomUUID(),
      userId: user.id,
      ...payload,
      status: 'pending',
      submittedAt: new Date().toISOString(),
    }
    persistRequests([entry, ...requests])
    return { ok: true, entry }
  }

  const userRequests = useMemo(
    () => (user ? requests.filter((r) => r.userId === user.id) : []),
    [requests, user],
  )

  const value = {
    user,
    userRequests,
    signIn,
    signUp,
    signOut,
    submitAoiRequest,
  }

  return (
    <AccountContext.Provider value={value}>{children}</AccountContext.Provider>
  )
}

export function useAccount() {
  const ctx = useContext(AccountContext)
  if (!ctx) throw new Error('useAccount must be used within AccountProvider')
  return ctx
}
