import { useEffect, useState } from 'react'
import LandCoverExplorer from './LandCoverExplorer.jsx'
import { getDemoAreasHistory } from '../utils/requestApi.js'

export default function DemoExplorer() {
  const [responses, setResponses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

     async function loadDemoResponses() {
      try {
        const data = await getDemoAreasHistory()
        if (!active) return
        setResponses(data)
      } catch (err) {
        if (active) setError(err.message)
      } finally {
        if (active) setLoading(false)
      }
    }

    loadDemoResponses()

    return () => {
      active = false
    }
  }, [])

  return (
    <section className="demo-explorer" id="demos">
      <div className="section-header">
        <h2>Public areas of interest</h2>
        <p>
          Demo regions backed by archive-style API responses. Select an area and scrub through
          time to see EuroSAT label distributions inferred from returned history.
        </p>
      </div>

      {loading ? (
        <p className="demo-viewer__insight-secondary">Loading demo areas...</p>
      ) : (
        <LandCoverExplorer responses={responses} />
      )}
    </section>
  )
}