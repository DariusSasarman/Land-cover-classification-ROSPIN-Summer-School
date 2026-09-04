import { useEffect, useState } from 'react'
import LandCoverExplorer from './LandCoverExplorer.jsx'
import { getDemoAreaHistory } from '../utils/requestApi.js'

const DEMO_AREA_IDS = ['po-valley', 'black-forest', 'danube-delta']

export default function DemoExplorer() {
  const [responses, setResponses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    async function loadDemoResponses() {
      const data = await Promise.all(
        DEMO_AREA_IDS.map(async (areaId) => {
          const res = await getDemoAreaHistory({ areaId })
          return { id: areaId, ...res }
        })
      )

      if (!active) return

      setResponses(data)
      setLoading(false)
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