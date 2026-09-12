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

  return found ? Number.parseFloat(String(found[1]).replace('%', '')) || 0 : 0
}

export default function TimeSeriesChart({ history, classId }) {
  const meta = EUROSAT_CLASS_BY_ID[classId]

  if (!history.length || !meta) {
    return (
      <div className="time-series">
        <p className="demo-viewer__insight-secondary">No history is available yet.</p>
      </div>
    )
  }

  const periods = history.map((item) => item?.Classification?.period_desc ?? '')
  const values = history.map((item) => parsePercentages(item, classId))
  const max = Math.max(...values, 1)

  const width = 700
  const height = 320
  const padX = 40
  const padTop = 24
  const padBottom = 36
  const innerW = width - padX * 2
  const innerH = height - padTop - padBottom

  const xFor = (i) => padX + (i / Math.max(values.length - 1, 1)) * innerW
  const yFor = (v) => padTop + innerH - (v / max) * innerH

  const linePoints = values.map((v, i) => `${xFor(i)},${yFor(v)}`).join(' ')
  const areaPoints = `${xFor(0)},${padTop + innerH} ${linePoints} ${xFor(values.length - 1)},${padTop + innerH}`

  // Skip x-axis labels if there are too many, to avoid overlap
  const labelStep = periods.length > 8 ? Math.ceil(periods.length / 8) : 1

  return (
    <div className="time-series">
      <svg
        className="time-series__svg"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label={`${meta.label} percentage over ${periods.length} periods`}
      >
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <line
            key={t}
            x1={padX}
            x2={width - padX}
            y1={padTop + innerH * (1 - t)}
            y2={padTop + innerH * (1 - t)}
            className="time-series__grid"
          />
        ))}

        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <text key={`label-${t}`} x={4} y={padTop + innerH * (1 - t) + 4} className="time-series__ylabel">
            {Math.round(max * t)}%
          </text>
        ))}

        <defs>
          <linearGradient id={`area-fill-${classId}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={meta.color} stopOpacity="0.35" />
            <stop offset="100%" stopColor={meta.color} stopOpacity="0" />
          </linearGradient>
        </defs>

        <polygon points={areaPoints} fill={`url(#area-fill-${classId})`} stroke="none" />

        <polyline
          points={linePoints}
          fill="none"
          stroke={meta.color}
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {values.map((v, i) => (
          <circle key={`pt-${i}`} cx={xFor(i)} cy={yFor(v)} r="3.5" fill={meta.color} stroke="#0b1220" strokeWidth="1.5" />
        ))}

        {periods.map((p, i) =>
          i % labelStep === 0 ? (
            <text key={`date-${i}`} x={xFor(i)} y={height - 12} className="time-series__xlabel" textAnchor="middle">
              {p}
            </text>
          ) : null,
        )}
      </svg>
    </div>
  )
}