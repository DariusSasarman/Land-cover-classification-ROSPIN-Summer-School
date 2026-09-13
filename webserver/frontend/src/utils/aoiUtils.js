import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'

function parsePct(raw) {
  return Number.parseFloat(String(raw).replace('%', '')) || 0
}

export function getMainLandType(item) {
  const history = item?.History ?? []
  const latest = history[history.length - 1]
  const percentages = latest?.Classification?.Percentages ?? {}

  const entries = Object.entries(percentages).map(([classId, val]) => [
    classId,
    parsePct(val),
  ])

  if (entries.length === 0) return null

  const top = entries.reduce((best, curr) => (curr[1] > best[1] ? curr : best))
  const meta = EUROSAT_CLASS_BY_ID[top[0]]

  return {
    id: top[0],
    label: meta?.label ?? top[0],
    percentage: top[1],
    color: meta?.color ?? '#888',
  }
}
