import { EUROSAT_CLASSES } from './eurosatLabels.js'

const PERIODS = ['2023-Q1', '2023-Q2', '2023-Q3', '2023-Q4', '2024-Q1', '2024-Q2']

function seededRand(seed) {
  let s = Math.sin(seed) * 10000
  return s - Math.floor(s)
}

function makeSnapshot(seed, dominantClass) {
  const values = {}
  let remaining = 100
  const ids = EUROSAT_CLASSES.map((c) => c.id)
  ids.forEach((id, i) => {
    if (id === dominantClass) return
    const pct = Math.round(seededRand(seed + i) * 8 * 10) / 10
    values[id] = pct
    remaining -= pct
  })
  values[dominantClass] = Math.max(remaining, 0)
  return values
}

export const DEMO_AREAS = [
  {
    id: 'po-valley',
    name: 'Po Valley',
    region: 'Emilia-Romagna, Italy',
    coordinates: '44.83°N, 11.62°E',
    areaKm2: 128,
    description: 'Intensive agricultural plain with seasonal crop rotation.',
    dominantClass: 'AnnualCrop',
  },
  {
    id: 'black-forest',
    name: 'Black Forest',
    region: 'Baden-Württemberg, Germany',
    coordinates: '48.10°N, 8.24°E',
    areaKm2: 96,
    description: 'Dense mixed forest with scattered pasture clearings.',
    dominantClass: 'Forest',
  },
  {
    id: 'danube-delta',
    name: 'Danube Delta',
    region: 'Tulcea, Romania',
    coordinates: '45.15°N, 29.30°E',
    areaKm2: 210,
    description: 'Wetland and river delta with mixed vegetation.',
    dominantClass: 'River',
  },
]

export function getPeriodsForArea() {
  return PERIODS
}

export function getSnapshot(area, period) {
  const seed = area.id.length + PERIODS.indexOf(period) * 3.1
  return makeSnapshot(seed, area.dominantClass)
}

export function getTopClasses(snapshot, n = 3) {
  return Object.entries(snapshot)
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
}

