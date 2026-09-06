import { useEffect, useState } from 'react'
import LandCoverExplorer from './LandCoverExplorer.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { fetchAoiList } from '../utils/requestApi.js'

export default function DisplayListAOI() {
  const { token, logout } = useAuth()
  const [responses, setResponses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadAoiResponses() {
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

    loadAoiResponses()

    return () => {
      active = false
    }
  }, [token])

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