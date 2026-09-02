import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'

export default function ClassificationChart({ snapshot }) {
  const entries = Object.entries(snapshot)
    .filter(([, pct]) => pct > 0)
    .sort((a, b) => b[1] - a[1])

  return (
    <div className="classification-chart">
      <h3 className="section-label">EuroSAT classification</h3>
      <ul className="classification-chart__list">
        {entries.map(([classId, pct]) => {
          const meta = EUROSAT_CLASS_BY_ID[classId]
          return (
            <li key={classId} className="classification-chart__row">
              <div className="classification-chart__label">
                <span
                  className="classification-chart__swatch"
                  style={{ backgroundColor: meta.color }}
                  aria-hidden="true"
                />
                <span>{meta.label}</span>
              </div>
              <div className="classification-chart__bar-wrap">
                <div
                  className="classification-chart__bar"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: meta.color,
                  }}
                />
              </div>
              <span className="classification-chart__pct">{pct.toFixed(1)}%</span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
