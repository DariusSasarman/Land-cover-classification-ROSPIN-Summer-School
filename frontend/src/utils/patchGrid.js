
import { EUROSAT_CLASSES, EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'

/** Deterministic pseudo-random for stable patch layout per period */
function seededPick(seed, weights) {
  const total = weights.reduce((s, w) => s + w.pct, 0)
  let r = (Math.sin(seed * 12.9898) * 43758.5453) % 1
  if (r < 0) r += 1
  r *= total
  for (const w of weights) {
    r -= w.pct
    if (r <= 0) return w.id
  }
  return weights[weights.length - 1].id
}

/** Build a patch grid from snapshot percentages (placeholder until .npy parsing) */
export function buildPatchGrid(snapshot, periodIndex, cols = 14, rows = 10) {
  const weights = EUROSAT_CLASSES.map(({ id }) => ({
    id,
    pct: snapshot[id] ?? 0,
  })).filter((w) => w.pct > 0)

  const patches = []
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const seed = periodIndex * 1000 + row * cols + col
      patches.push({
        row,
        col,
        classId: seededPick(seed, weights),
      })
    }
  }
  return { cols, rows, patches }
}

/** Inline SVG placeholder for a 64×64 patch tile */
export function patchPlaceholderSrc(classId, color) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
    <rect width="64" height="64" fill="${color}" opacity="0.35"/>
    <rect x="2" y="2" width="60" height="60" fill="none" stroke="${color}" stroke-width="1" opacity="0.5"/>
    <path d="M8 48 L24 20 L40 36 L56 12" stroke="${color}" stroke-width="2" fill="none" opacity="0.6"/>
    <circle cx="20" cy="44" r="6" fill="${color}" opacity="0.45"/>
    <circle cx="46" cy="28" r="4" fill="${color}" opacity="0.35"/>
  </svg>`
  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}
