import { useEffect, useMemo, useState } from 'react'
import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'
import ClassificationChart from './ClassificationChart.jsx'
import TimeSeriesChart from './TimeSeriesChart.jsx'

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

function formatAreaName(id) {
  if (!id) return 'Unknown Area'
  return id
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function getClassificationSnapshot(historyItem) {
  const percentages = historyItem?.Classification?.Percentages ?? {}

  return Object.fromEntries(
    Object.entries(percentages).map(([label, value]) => {
      const classEntry =
        EUROSAT_CLASS_BY_ID[label] ??
        Object.values(EUROSAT_CLASS_BY_ID).find((item) => item.label === label)
      const pct = Number.parseFloat(String(value).replace('%', ''))
      return [classEntry?.id ?? label, Number.isFinite(pct) ? pct : 0]
    }),
  )
}

function getTopClass(snapshot) {
  const entries = Object.entries(snapshot)
  if (entries.length === 0) {
    return null
  }

  return entries.reduce((best, current) => (current[1] > best[1] ? current : best))
}

function AreaViewer({ area, history, onSelectionChange }) {
  const [activeIndex, setActiveIndex] = useState(Math.max(history.length - 1, 0))
  const [layer, setLayer] = useState('rgb')

  const currentHistory = history[activeIndex] ?? history[history.length - 1] ?? null
  const classification = currentHistory?.Classification ?? null
  const snapshot = useMemo(() => getClassificationSnapshot(currentHistory), [currentHistory])

  useEffect(() => {
    onSelectionChange?.({
      areaId: area.id,
      historyItem: currentHistory,
      snapshot,
      activeIndex,
    })
  }, [activeIndex, area.id, currentHistory, onSelectionChange, snapshot])

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
                alt={`${area.name} ${layer === 'rgb' ? 'RGB satellite image' : 'masked land-cover image'}`}
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
          <button
            type="button"
            className="demo-viewer__nav"
            onClick={() => moveTo(activeIndex - 1)}
            aria-label="Previous frame"
          >
            ‹
          </button>
          <button
            type="button"
            className="demo-viewer__nav"
            onClick={() => moveTo(activeIndex + 1)}
            aria-label="Next frame"
          >
            ›
          </button>

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
          <div>
            <h3 className="demo-viewer__eyebrow">{area.name}</h3>
          </div>
          <div className="demo-viewer__meta-right">
            <span>{area.region}</span>
          </div>
        </div>

        <ClassificationChart snapshot={snapshot} />
      </aside>
    </div>
  )
}

/**
 * Displays fetched land-cover API response(s) for area(s).
 *
 * @param {{ responses?: any[], response?: any, area?: any }} props
 */
export default function LandCoverExplorer({ responses, response, area: propArea }) {
  const responseList = useMemo(() => {
    if (Array.isArray(responses) && responses.length > 0) {
      return responses
    }
    if (response) {
      return [{ id: propArea?.id ?? 'default', ...response }]
    }
    return []
  }, [responses, response, propArea])

  // Split into done vs in-progress
  const doneResponses = useMemo(
    () => responseList.filter((r) => !r.status || r.status === 'done'),
    [responseList],
  )
  const hasInProgress = responseList.some((r) => r.status === 'in_progress')

  const [selectedId, setSelectedId] = useState(() => doneResponses[0]?.id)

  const activeId = doneResponses.some((r) => r.id === selectedId) ? selectedId : doneResponses[0]?.id
  const currentResponse = useMemo(() => {
    return doneResponses.find((r) => r.id === activeId) ?? doneResponses[0] ?? null
  }, [doneResponses, activeId])

  const area = useMemo(() => {
    if (!currentResponse) {
      return propArea ?? { id: 'unknown', name: 'Unknown', region: '' }
    }
    return {
      id: currentResponse.id,
      name: propArea?.name ?? formatAreaName(currentResponse.id),
      region: currentResponse.title ?? propArea?.region ?? '',
    }
  }, [currentResponse, propArea])

  const [selectedGraphId, setSelectedGraphId] = useState(CLASS_ORDER[0])
  const [viewerSelection, setViewerSelection] = useState(null)

  const history = currentResponse?.History ?? []
  const latestHistory = history[history.length - 1] ?? null
  const currentHistoryItem = viewerSelection?.areaId === area.id ? viewerSelection.historyItem : latestHistory
  const currentClassification = currentHistoryItem?.Classification ?? null

  const graphChoices = useMemo(() => {
    return CLASS_ORDER.map((classId) => ({
      id: classId,
      label: EUROSAT_CLASS_BY_ID[classId].label,
    }))
  }, [])

  const showBottomList = responseList.length > 1

  return (
    <div className="demo-explorer__layout">
      <div className="demo-detail">
        {currentResponse ? (
          <AreaViewer
            key={`${area.id}-${history.length}`}
            area={area}
            history={history}
            onSelectionChange={setViewerSelection}
          />
        ) : (
          <div className="demo-viewer">
            <div className="demo-viewer__stage">
              <div className="demo-viewer__media">
                <div className="demo-viewer__canvas">
                  <div className="demo-viewer__empty demo-viewer__empty--wip">
                    <span className="wip-spinner" aria-hidden="true" />
                    <span>Your request is being processed…</span>
                  </div>
                </div>
              </div>
            </div>
            <aside className="demo-viewer__sidebar">
              <div className="demo-viewer__header">
                <h3 className="demo-viewer__eyebrow">Work in progress</h3>
              </div>
              <p className="demo-viewer__insight-secondary">
                Your AOI is currently being analysed. Results will appear here once the pipeline finishes.
              </p>
            </aside>
          </div>
        )}

        {currentResponse && (
          <aside className="demo-viewer__sidebar">
            <div className="demo-viewer__insights">
              <div className="demo-viewer__legend-title">Generated insights</div>
              <p className="demo-viewer__insight-summary">{currentResponse.title}</p>
              <ul className="demo-viewer__insight-list">
                {currentResponse.insights.map((insight) => (
                  <li key={insight} className="demo-viewer__insight-secondary">{insight}</li>
                ))}
              </ul>
              <div className="demo-viewer__insight-meta">
                <span>History items {history.length}</span>
                {currentClassification ? (
                  <span>
                    Frame {currentClassification.index} · {currentClassification.period_desc}
                  </span>
                ) : null}
              </div>
            </div>

            <div className="demo-detail__charts">
              <div className="demo-graph-picker">
                <div className="demo-graph-picker__label">Pick a time graph</div>
                <div className="demo-graph-picker__buttons">
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
              </div>

              <TimeSeriesChart history={history} classId={selectedGraphId} />
            </div>
          </aside>
        )}
      </div>

      {showBottomList && (
        <aside className="demo-list demo-list--stacked demo-list--bottom" aria-label="AOI areas">
          {responseList.map((item) => {
            const isDone = !item.status || item.status === 'done'
            const itemHistory = item.History ?? []
            const itemLatest = itemHistory[itemHistory.length - 1]
            const itemSnapshot = getClassificationSnapshot(itemLatest)
            const itemTop = getTopClass(itemSnapshot)
            const dominant = isDone && itemTop ? EUROSAT_CLASS_BY_ID[itemTop[0]] : null
            const name = formatAreaName(item.id)

            if (!isDone) {
              // Non-clickable work-in-progress card
              return (
                <div
                  key={item.id}
                  className="demo-card demo-card--wip"
                  aria-label={`${name} — work in progress`}
                  title="This area is still being processed"
                >
                  <span className="demo-card__name">{name}</span>
                  <span className="demo-card__region">{item.title}</span>
                  <span className="demo-card__tag demo-card__tag--wip">
                    <span className="wip-dot" aria-hidden="true" />
                    Work in progress
                  </span>
                </div>
              )
            }

            return (
              <button
                key={item.id}
                type="button"
                className={`demo-card${item.id === activeId ? ' demo-card--active' : ''}`}
                onClick={() => setSelectedId(item.id)}
              >
                <span className="demo-card__name">{name}</span>
                <span className="demo-card__region">{item.title}</span>
                {dominant && (
                  <span className="demo-card__tag" style={{ color: dominant.color }}>
                    {dominant.label}
                  </span>
                )}
              </button>
            )
          })}
        </aside>
      )}
    </div>
  )
}