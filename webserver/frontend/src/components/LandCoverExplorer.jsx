import { useEffect, useMemo, useState } from 'react'
import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'
import ClassificationChart from './ClassificationChart.jsx'
import TimeSeriesChart from './TimeSeriesChart.jsx'
import InsightsMarkdown from './InsightsMarkdown.jsx'

const CLASS_ORDER = [
  'River',
  'SeaLake',
  'Forest',
  'HerbaceousVegetation',
  'AnnualCrop',
  'PermanentCrop',
  'Pasture',
  'Residential',
  'Industrial',
  'Highway',
]

function parsePct(raw) {
  return Number.parseFloat(String(raw).replace('%', '')) || 0
}

function getClassificationSnapshot(historyItem) {
  const percentages = historyItem?.Classification?.Percentages ?? {}
  return Object.fromEntries(
    Object.entries(percentages).map(([classId, value]) => [classId, parsePct(value)]),
  )
}

function getTopClass(snapshot) {
  const entries = Object.entries(snapshot)
  if (entries.length === 0) return null
  return entries.reduce((best, current) => (current[1] > best[1] ? current : best))
}

function AreaViewer({ id, title, history, onSelectionChange }) {
  const [activeIndex, setActiveIndex] = useState(Math.max(history.length - 1, 0))
  const [layer, setLayer] = useState('rgb')

  const currentHistory = history[activeIndex] ?? history[history.length - 1] ?? null
  const classification = currentHistory?.Classification ?? null
  const snapshot = useMemo(() => getClassificationSnapshot(currentHistory), [currentHistory])

  useEffect(() => {
    onSelectionChange?.({ id, historyItem: currentHistory, snapshot, activeIndex })
  }, [activeIndex, id, currentHistory, onSelectionChange, snapshot])

  function moveTo(nextIndex) {
    const boundedIndex = Math.max(0, Math.min(history.length - 1, nextIndex))
    setActiveIndex(boundedIndex)
  }

  const mediaSrc = layer === 'rgb' ? classification?.RGB_IMAGE : classification?.Masked_IMAGE
  const periodLabel = classification?.period_desc ?? 'Loading archive'
  const topClass = getTopClass(snapshot)
  const topClassMeta = topClass ? EUROSAT_CLASS_BY_ID[topClass[0]] : null

  return (
    <div className="demo-viewer">
      <div className="demo-viewer__stage">
        <div className="demo-viewer__media">
          <div className="demo-viewer__canvas">
            {mediaSrc ? (
              <img
                className={layer === 'mask' ? 'demo-viewer__image demo-viewer__image--mask' : 'demo-viewer__image'}
                src={mediaSrc}
                alt={`${title} ${layer === 'rgb' ? 'RGB satellite image' : 'masked land-cover image'}`}
              />
            ) : (
              <div className="demo-viewer__empty">Loading demo imagery...</div>
            )}

            <div className="demo-viewer__frame-badge">
              <span className="demo-viewer__frame-index">FR {classification?.index ?? '--'}</span>
              <span>{periodLabel}</span>
              {topClassMeta ? <span>{topClassMeta.label} · {topClass[1].toFixed(1)}%</span> : null}
            </div>

            <div className="demo-viewer__layer-toggle" role="group" aria-label="Viewer layer">
              <button
                type="button"
                className={layer === 'rgb' ? 'demo-viewer__toggle demo-viewer__toggle--active' : 'demo-viewer__toggle'}
                onClick={() => setLayer('rgb')}
              >
                RGB
              </button>
              <button
                type="button"
                className={layer === 'mask' ? 'demo-viewer__toggle demo-viewer__toggle--active' : 'demo-viewer__toggle'}
                onClick={() => setLayer('mask')}
              >
                Mask
              </button>
            </div>
          </div>
        </div>

        <div className="demo-viewer__rail">
          <button type="button" className="demo-viewer__nav" onClick={() => moveTo(activeIndex - 1)} aria-label="Previous frame">‹</button>
          <button type="button" className="demo-viewer__nav" onClick={() => moveTo(activeIndex + 1)} aria-label="Next frame">›</button>

          <input
            className="demo-viewer__slider"
            type="range"
            min={0}
            max={Math.max(history.length - 1, 0)}
            step={1}
            value={activeIndex}
            onChange={(event) => moveTo(Number(event.target.value))}
            aria-label="Time slider"
            style={{ '--slider-value': activeIndex / Math.max(history.length - 1, 1) }}
          />
        </div>
      </div>

      <aside className="demo-viewer__sidebar">
        <div className="demo-viewer__header">
          <h3 className="demo-viewer__eyebrow">{title}</h3>
        </div>

        <ClassificationChart snapshot={snapshot} />
      </aside>
    </div>
  )
}

/**
 * Displays a single fetched LandCoverResponse: image viewer, markdown insights,
 * and a time-series chart with a class picker.
 *
 * @param {{ id: string, title: string, insights: string, History: any[] } | null} response
 */
export default function LandCoverExplorer({ response }) {
  const [selectedGraphId, setSelectedGraphId] = useState(CLASS_ORDER[0])
  const [viewerSelection, setViewerSelection] = useState(null)

  const history = response?.History ?? []
  const latestHistory = history[history.length - 1] ?? null
  const currentHistoryItem = viewerSelection?.id === response?.id ? viewerSelection.historyItem : latestHistory
  const currentClassification = currentHistoryItem?.Classification ?? null

  const graphChoices = useMemo(() => {
    return CLASS_ORDER.map((classId) => ({
      id: classId,
      label: EUROSAT_CLASS_BY_ID[classId].label,
    }))
  }, [])

  if (!response) {
    return <p className="demo-viewer__insight-secondary">Loading insights...</p>
  }

  return (
    <div className="demo-detail">
      <AreaViewer
        key={`${response.id}-${history.length}`}
        id={response.id}
        title={response.title}
        history={history}
        onSelectionChange={setViewerSelection}
      />

      <aside className="demo-viewer__sidebar">
        <div className="demo-viewer__insights">
          <div className="demo-viewer__legend-title">AI-generated insights</div>
          <InsightsMarkdown content={response.insights} />
          <div className="demo-viewer__insight-meta">
            <span>History items {history.length}</span>
            {currentClassification ? (
              <span>Frame {currentClassification.index} · {currentClassification.period_desc}</span>
            ) : null}
          </div>
        </div>

        <div className="demo-detail__charts demo-detail__charts--row">
          <div className="demo-graph-picker__label">Pick a time graph</div>
          <div className="demo-graph-picker__buttons demo-graph-picker__buttons--col">
            {graphChoices.map((choice) => (
              <button
                key={choice.id}
                type="button"
                className={selectedGraphId === choice.id ? 'demo-graph-picker__button demo-graph-picker__button--active' : 'demo-graph-picker__button'}
                onClick={() => setSelectedGraphId(choice.id)}
              >
                {choice.label}
              </button>
            ))}
          </div>

          <TimeSeriesChart history={history} classId={selectedGraphId} />
        </div>

      </aside>
    </div>
  )
}