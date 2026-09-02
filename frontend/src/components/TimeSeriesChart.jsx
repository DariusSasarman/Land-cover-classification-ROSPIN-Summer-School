import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'
import { getPeriodsForArea, getSnapshot } from '../data/demoAreas.js'

export default function TimeSeriesChart({ area, classId }) {
  const periods = getPeriodsForArea(area)
  const values = periods.map((p) => getSnapshot(area, p)[classId] ?? 0)
  const max = Math.max(...values, 1)

  const width = 320
  const height = 120
  const padX = 8
  const padY = 12
  const innerW = width - padX * 2
  const innerH = height - padY * 2

  const points = values
    .map((v, i) => {
      const x = padX + (i / Math.max(values.length - 1, 1)) * innerW
      const y = padY + innerH - (v / max) * innerH
      return `${x},${y}`
    })
    .join(' ')

  const meta = EUROSAT_CLASS_BY_ID[classId]

  return (
    <div className="time-series">
      <h3 className="section-label">
        {meta.label} over time
      </h3>
      <svg
        className="time-series__svg"
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label={`${meta.label} percentage over ${periods.length} periods`}
      >
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <line
            key={t}
            x1={padX}
            x2={width - padX}
            y1={padY + innerH * (1 - t)}
            y2={padY + innerH * (1 - t)}
            className="time-series__grid"
          />
        ))}
        <polyline
          points={points}
          fill="none"
          stroke={meta.color}
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        {values.map((v, i) => {
          const x = padX + (i / Math.max(values.length - 1, 1)) * innerW
          const y = padY + innerH - (v / max) * innerH
          return (
            <circle
              key={periods[i]}
              cx={x}
              cy={y}
              r="3.5"
              fill={meta.color}
            />
          )
        })}
      </svg>
      <div className="time-series__axis">
        {periods.map((p) => (
          <span key={p}>{p.replace('-', ' ')}</span>
        ))}
      </div>
    </div>
  )
}
