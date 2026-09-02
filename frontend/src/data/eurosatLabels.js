export const EUROSAT_CLASSES = [
  { id: 'AnnualCrop', label: 'Annual Crop', color: '#eab308' },
  { id: 'Forest', label: 'Forest', color: '#22c55e' },
  { id: 'HerbaceousVegetation', label: 'Herbaceous Vegetation', color: '#84cc16' },
  { id: 'Highway', label: 'Highway', color: '#94a3b8' },
  { id: 'Industrial', label: 'Industrial', color: '#f97316' },
  { id: 'Pasture', label: 'Pasture', color: '#a3e635' },
  { id: 'PermanentCrop', label: 'Permanent Crop', color: '#facc15' },
  { id: 'Residential', label: 'Residential', color: '#ef4444' },
  { id: 'River', label: 'River', color: '#38bdf8' },
  { id: 'SeaLake', label: 'Sea / Lake', color: '#0ea5e9' },
]

export const EUROSAT_CLASS_BY_ID = Object.fromEntries(
  EUROSAT_CLASSES.map((c) => [c.id, c])
)
