import { useEffect, useMemo, useState } from 'react'
import LandCoverExplorer from './LandCoverExplorer.jsx'
import { getDemoAreasHistory } from '../utils/requestApi.js'
import { getMainLandType } from '../utils/aoiUtils.js'

export default function DemoExplorer() {
  const [responses, setResponses] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true

    async function loadDemoResponses() {
      try {
        const data = await getDemoAreasHistory()
        if (!active) return
        setResponses(data)
        setSelectedId(data[0]?.id ?? null)
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

  const selected = useMemo(
    () => responses.find((item) => item.id === selectedId) ?? null,
    [responses, selectedId],
  )

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
      ) : error ? (
        <p className="demo-viewer__insight-secondary">Failed to load demo areas: {error}</p>
      ) : (
        <div className="demo-explorer__layout">
          <LandCoverExplorer response={selected} />

          <aside className="demo-list demo-list--stacked demo-list--bottom" aria-label="Demo areas">
            {responses.map((item) => {
              const mainLand = getMainLandType(item)

              return (
                <button
                  key={item.id}
                  type="button"
                  className={`demo-card${item.id === selectedId ? ' demo-card--active' : ''}`}
                  onClick={() => setSelectedId(item.id)}
                >
                  <span className="demo-card__name">{item.title}</span>
                  {mainLand && (
                    <span className="demo-card__tag" style={{ color: mainLand.color }}>
                      {mainLand.label} · {mainLand.percentage.toFixed(1)}%
                    </span>
                  )}
                </button>
              )
            })}
          </aside>
        </div>
      )}
    </section>
  )
}