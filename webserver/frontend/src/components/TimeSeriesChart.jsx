import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'

function parsePercentages(historyItem, classId) {
  const meta = EUROSAT_CLASS_BY_ID[classId]
  const percentages = historyItem?.Classification?.Percentages ?? {}

  if (percentages[classId] !== undefined) {
    return Number.parseFloat(String(percentages[classId]).replace('%', '')) || 0
  }
  if (meta?.label && percentages[meta.label] !== undefined) {
    return Number.parseFloat(String(percentages[meta.label]).replace('%', '')) || 0
  }

  const found = Object.entries(percentages).find(([key]) => {
    return key === classId || key === meta?.label || key.replace(/\s+/g, '') === classId
  })

  if (found) {
    return Number.parseFloat(String(found[1]).replace('%', '')) || 0
  }

  return 0
}

export default function TimeSeriesChart({ history, classId }) {
  const meta = EUROSAT_CLASS_BY_ID[classId]

  if (!history.length || !meta) {
    return (
      <div className="time-series">
        <h3 className="section-label">Time series</h3>
        <p className="demo-viewer__insight-secondary">No history is available yet.</p>
      </div>
    )
  }

  const periods = history.map((item) => item?.Classification?.['period desc'] ?? '')
  const values = history.map((item) => parsePercentages(item, classId))
  const max = Math.max(...values, 1)

  const width = 320
  const height = 120
  const padX = 26
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

  return (
    <div className="time-series">
      <h3 className="section-label">{meta.label} over time</h3>
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
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <text
            key={`label-${t}`}
            x={2}
            y={padY + innerH * (1 - t) - 2}
            className="time-series__ylabel"
          >
            {Math.round(max * t)}%
          </text>
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
    </div>
  )
}