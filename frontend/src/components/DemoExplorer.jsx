import { useMemo, useState } from 'react'
import { DEMO_AREAS, getPeriodsForArea, getSnapshot, getTopClasses } from '../data/demoAreas.js'
import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'
import ClassificationChart from './ClassificationChart.jsx'
import TimeSeriesChart from './TimeSeriesChart.jsx'

function AreaSummary({ area, period, snapshot }) {
  const top = getTopClasses(snapshot, 3)
  const dominant = EUROSAT_CLASS_BY_ID[area.dominantClass]

  return (
    <div className="area-summary">
      <div className="area-summary__map" aria-hidden="true">
        <div className="area-summary__grid" />
        <div className="area-summary__pin">
          <span>AOI</span>
        </div>
      </div>
      <div className="area-summary__meta">
        <dl>
          <div>
            <dt>Region</dt>
            <dd>{area.region}</dd>
          </div>
          <div>
            <dt>Coordinates</dt>
            <dd>{area.coordinates}</dd>
          </div>
          <div>
            <dt>Area</dt>
            <dd>{area.areaKm2} km²</dd>
          </div>
          <div>
            <dt>Period</dt>
            <dd>{period}</dd>
          </div>
          <div>
            <dt>Typical dominant class</dt>
            <dd>
              <span
                className="pill"
                style={{
                  '--pill-color': dominant.color,
                }}
              >
                {dominant.label}
              </span>
            </dd>
          </div>
        </dl>
        <p className="area-summary__desc">{area.description}</p>
        <div className="area-summary__chips">
          {top.map(([classId, pct]) => (
            <span
              key={classId}
              className="chip"
              style={{ '--chip-color': EUROSAT_CLASS_BY_ID[classId].color }}
            >
              {EUROSAT_CLASS_BY_ID[classId].label} · {pct.toFixed(1)}%
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function DemoExplorer() {
  const [selectedId, setSelectedId] = useState(DEMO_AREAS[0].id)
  const area = DEMO_AREAS.find((a) => a.id === selectedId)
  const periods = useMemo(() => getPeriodsForArea(area), [area])
  const [period, setPeriod] = useState(periods[periods.length - 1])

  const snapshot = getSnapshot(area, period)

  function selectArea(id) {
    setSelectedId(id)
    const nextArea = DEMO_AREAS.find((a) => a.id === id)
    const nextPeriods = getPeriodsForArea(nextArea)
    setPeriod(nextPeriods[nextPeriods.length - 1])
  }

  return (
    <section className="demo-explorer" id="demos" style={{ 'display' : 'block' }}>
      <div className="section-header">
        <h2>Public areas of interest</h2>
        <p>
          Demo regions with stub ResNet inference. Select an area and scrub through
          time to see EuroSAT label distributions.
        </p>
      </div>

      <div className="demo-explorer__layout">
        <aside className="demo-list" aria-label="Demo areas">
          {DEMO_AREAS.map((demo) => {
            const dominant = EUROSAT_CLASS_BY_ID[demo.dominantClass]
            return (
              <button
                key={demo.id}
                type="button"
                className={`demo-card${demo.id === selectedId ? ' demo-card--active' : ''}`}
                onClick={() => selectArea(demo.id)}
              >
                <span className="demo-card__name">{demo.name}</span>
                <span className="demo-card__region">{demo.region}</span>
                <span
                  className="demo-card__tag"
                  style={{ color: dominant.color }}
                >
                  {dominant.label}
                </span>
              </button>
            )
          })}
        </aside>

        <div className="demo-detail">
          <div className="demo-detail__toolbar">
            <label htmlFor="period-select">Time period</label>
            <input
              id="period-select"
              type="range"
              min={0}
              max={periods.length - 1}
              value={periods.indexOf(period)}
              onChange={(e) => setPeriod(periods[Number(e.target.value)])}
            />
            <output>{period}</output>
          </div>

          <AreaSummary area={area} period={period} snapshot={snapshot} />

          <div className="demo-detail__charts">
            <ClassificationChart snapshot={snapshot} />
            <TimeSeriesChart area={area} classId={area.dominantClass} />
          </div>
        </div>
      </div>
    </section>
  )
}
