import { useEffect, useRef, useState } from 'react'
import LandCoverExplorer from './LandCoverExplorer.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { fetchAoiList } from '../utils/requestApi.js'

const POLL_INTERVAL_MS = 4000

export default function DisplayListAOI() {
  const { token, logout } = useAuth()
  const [responses, setResponses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const pollRef = useRef(null)

  const hasInProgress = responses.some((r) => r.status === 'in_progress')

  async function loadAoiResponses(isInitial = false) {
    try {
      const data = await fetchAoiList(token)
      setResponses(data)
      if (isInitial) setLoading(false)
    } catch (err) {
      setError(err.message)
      if (isInitial) setLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    let active = true

    async function init() {
      try {
        const data = await fetchAoiList(token)
        if (!active) return
        setResponses(data)
      } catch (err) {
        if (active) setError(err.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    init()

    return () => {
      active = false
    }
  }, [token])

  // Polling while any response is in_progress
  useEffect(() => {
    if (!hasInProgress) {
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
      return
    }

    if (pollRef.current) return // already polling

    pollRef.current = setInterval(() => {
      loadAoiResponses(false)
    }, POLL_INTERVAL_MS)

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [hasInProgress, token])

  return (
    <section className="demo-explorer" id="my-aois">
      <div className="section-header">
        <h2>My areas of interest</h2>
        <p>Your requested AOIs and their land-cover history.</p>
        <button type="button" className="btn btn--secondary" onClick={logout}>
          Sign out
        </button>
      </div>

      {loading ? (
        <p className="demo-viewer__insight-secondary">Loading your AOIs...</p>
      ) : error ? (
        <p className="form__error">{error}</p>
      ) : responses.length === 0 ? (
        <p className="demo-viewer__insight-secondary">
          You haven't requested any AOIs yet.
        </p>
      ) : (
        <LandCoverExplorer responses={responses} />
      )}
    </section>
  )
}