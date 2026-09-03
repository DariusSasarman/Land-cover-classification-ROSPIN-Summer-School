import { useEffect, useMemo, useState } from 'react'
import { DEMO_AREAS, getPeriodsForArea, getSnapshot } from '../data/demoAreas.js'
import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'
import ClassificationChart from './ClassificationChart.jsx'
import TimeSeriesChart from './TimeSeriesChart.jsx'
import { createRequest } from '../utils/requestApi.js'

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

function buildFrame(area, period) {
  const snapshot = getSnapshot(area, period)
  const dominant = Object.entries(snapshot).reduce((best, [classId, pct]) => {
    return pct > (snapshot[best] ?? -1) ? classId : best
  }, Object.keys(snapshot)[0])

  const confidence = snapshot[dominant] ?? 0
  const cloud = Math.max(
    4,
    Math.min(38, Math.round(8 + (snapshot.Highway ?? 0) * 0.6 + (snapshot.Industrial ?? 0) * 0.4)),
  )

  return {
    period,
    snapshot,
    dominant,
    confidence,
    cloud,
  }
}

function buildInsights(area, frame, response) {
  const topClasses = Object.entries(frame.snapshot)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([classId, pct]) => ({
      classId,
      label: EUROSAT_CLASS_BY_ID[classId].label,
      color: EUROSAT_CLASS_BY_ID[classId].color,
      pct,
    }))

  const vegetation = (frame.snapshot.Forest ?? 0) + (frame.snapshot.HerbaceousVegetation ?? 0)
  const water = (frame.snapshot.River ?? 0) + (frame.snapshot.SeaLake ?? 0)

  return {
    requestId: response?.id ?? 'demo-request',
    summary: `${EUROSAT_CLASS_BY_ID[frame.dominant].label} is the leading class over ${area.name}.`,
    secondary: `Vegetation covers ${vegetation.toFixed(1)}% of the frame, with water at ${water.toFixed(1)}%.`,
    topClasses,
    cloud: frame.cloud,
    confidence: frame.confidence,
    period: frame.period,
  }
}

function AreaViewer({ area, onFrameChange, insights }) {
  const periods = useMemo(() => getPeriodsForArea(area), [area])
  const frames = useMemo(() => periods.map((period) => buildFrame(area, period)), [area, periods])
  const [index, setIndex] = useState(Math.max(periods.length - 1, 0))
  const [scrubValue, setScrubValue] = useState(Math.max(periods.length - 1, 0))
  const [playing, setPlaying] = useState(false)
  const [layer, setLayer] = useState('mask')

  useEffect(() => {
    const lastIndex = Math.max(periods.length - 1, 0)
    setIndex(lastIndex)
    setScrubValue(lastIndex)
    setPlaying(false)
  }, [area.id, periods.length])

  useEffect(() => {
    if (!playing || frames.length < 2) return

    const timer = window.setInterval(() => {
      setIndex((current) => (current + 1) % frames.length)
      setScrubValue((current) => (Math.round(current) + 1) % frames.length)
    }, 1200)

    return () => window.clearInterval(timer)
  }, [playing, frames.length])

  const activeIndex = Math.max(0, Math.min(frames.length - 1, Math.round(scrubValue)))
  const frame = frames[activeIndex] ?? frames[0]
  const prev = frames[Math.max(activeIndex - 1, 0)] ?? frame
  const dominant = EUROSAT_CLASS_BY_ID[frame.dominant]
  const riverDelta = (frame.snapshot.River ?? 0) - (prev.snapshot.River ?? 0)

  useEffect(() => {
    onFrameChange?.(frame)
  }, [frame, onFrameChange])

  function moveTo(nextIndex) {
    const boundedIndex = Math.max(0, Math.min(frames.length - 1, nextIndex))
    setIndex(boundedIndex)
    setScrubValue(boundedIndex)
  }

  return (
    <div className="demo-viewer">
      <div className="demo-viewer__stage">
        <div className="demo-viewer__media">
          <div className="demo-viewer__canvas" aria-hidden="true">
            <div className="demo-viewer__base" />
            <div className={layer === 'mask' ? 'demo-viewer__mask demo-viewer__mask--visible' : 'demo-viewer__mask'}>
              <div className="demo-viewer__swath demo-viewer__swath--forest" />
              <div
                className="demo-viewer__swath demo-viewer__swath--crop"
                style={{ width: `${42 + (frame.snapshot.AnnualCrop ?? 0) * 0.45}%` }}
              />
              <div
                className="demo-viewer__swath demo-viewer__swath--river"
                style={{ width: `${30 + (frame.snapshot.River ?? 0) * 0.65}%` }}
              />
              <div
                className="demo-viewer__swath demo-viewer__swath--urban"
                style={{ width: `${22 + (frame.snapshot.Residential ?? 0) * 0.7}%` }}
              />
            </div>

            <div className="demo-viewer__frame-badge">
              <span className="demo-viewer__frame-index">FR {String(index + 1).padStart(2, '0')}</span>
              <span>{frame.period}</span>
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

            <div className="demo-viewer__footer">
              <span>
                Δ vs {prev.period} · {riverDelta >= 0 ? '+' : ''}
                {riverDelta.toFixed(1)}% river
              </span>
              <span>
                cl {frame.cloud}% · {dominant.label}
              </span>
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
            max={Math.max(frames.length - 1, 0)}
            step={1}
            value={scrubValue}
            onChange={(event) => moveTo(Number(event.target.value))}
            aria-label="Time slider"
            style={{ '--slider-value': activeIndex / Math.max(frames.length - 1, 1) }}
          />
        </div>
      </div>

      <aside className="demo-viewer__sidebar">
        <div className="demo-viewer__header">
          <div>
            <div className="demo-viewer__eyebrow">Fixed-extent viewer</div>
            <h3>{area.name}</h3>
          </div>
          <div className="demo-viewer__meta-right">
            <span>{area.coordinates}</span>
            <span>{area.region}</span>
          </div>
        </div>

        <ClassificationChart snapshot={frame.snapshot} />
      </aside>
    </div>
  )
}

export default function DemoExplorer() {
  const [selectedId, setSelectedId] = useState(DEMO_AREAS[0].id)
  const area = useMemo(() => DEMO_AREAS.find((item) => item.id === selectedId) ?? DEMO_AREAS[0], [selectedId])
  const periods = useMemo(() => getPeriodsForArea(area), [area])
  const [currentFrame, setCurrentFrame] = useState(() => buildFrame(area, periods[periods.length - 1]))
  const [selectedGraphId, setSelectedGraphId] = useState(DEMO_AREAS[0].dominantClass)
  const [insights, setInsights] = useState(null)

  useEffect(() => {
    const nextFrame = buildFrame(area, periods[periods.length - 1])
    setCurrentFrame(nextFrame)
    setSelectedGraphId(nextFrame.dominant)
  }, [area, periods])

  useEffect(() => {
    let active = true

    async function loadInsights() {
      const response = await createRequest({
        areaId: area.id,
        areaName: area.name,
        period: currentFrame.period,
        dominantClass: currentFrame.dominant,
        snapshot: currentFrame.snapshot,
      })

      if (!active) return

      setInsights(buildInsights(area, currentFrame, response))
    }

    loadInsights()

    return () => {
      active = false
    }
  }, [area, currentFrame])

  const graphChoices = useMemo(() => {
    return CLASS_ORDER.map((classId) => ({
      id: classId,
      label: EUROSAT_CLASS_BY_ID[classId].label,
    }))
  }, [])

  return (
    <section className="demo-explorer" id="demos">
      <div className="section-header">
        <h2>Public areas of interest</h2>
        <p>
          Demo regions with stub ResNet inference. Select an area and scrub through
          time to see EuroSAT label distributions.
        </p>
      </div>

      <div className="demo-explorer__layout">
        <div className="demo-detail">
          <AreaViewer area={area} onFrameChange={setCurrentFrame} insights={insights} />
            <aside className="demo-viewer__sidebar">
                <div className="demo-viewer__insights">
                    <div className="demo-viewer__legend-title">API insights</div>
                    {insights ? (
                        <>
                        <p className="demo-viewer__insight-summary">{insights.summary}</p>
                        <p className="demo-viewer__insight-secondary">{insights.secondary}</p>
                        <div className="demo-viewer__insight-meta">
                            <span>Request {insights.requestId}</span>
                            <span>Frame {String(currentFrame.period + 1).padStart(2, '0')} · {insights.period}</span>
                            <span>Confidence {insights.confidence.toFixed(1)}% · Cloud {insights.cloud}%</span>
                        </div>
                        </>
                    ) : (
                        <p className="demo-viewer__insight-secondary">Loading insights...</p>
                    )}
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
            
                <TimeSeriesChart area={area} classId={selectedGraphId} />
            </div>
            </aside>
          

          <aside className="demo-list demo-list--stacked demo-list--bottom" aria-label="Demo areas">
            {DEMO_AREAS.map((demo) => {
              const dominant = EUROSAT_CLASS_BY_ID[demo.dominantClass]

              return (
                <button
                  key={demo.id}
                  type="button"
                  className={`demo-card${demo.id === selectedId ? ' demo-card--active' : ''}`}
                  onClick={() => setSelectedId(demo.id)}
                >
                  <span className="demo-card__name">{demo.name}</span>
                  <span className="demo-card__region">{demo.region}</span>
                  <span className="demo-card__tag" style={{ color: dominant.color }}>
                    {dominant.label}
                  </span>
                </button>
              )
            })}
          </aside>
        </div>
      </div>
    </section>
  )
}
