import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { submitAoiRequest } from '../utils/requestApi.js'

const INITIAL = {
  name: '',
  email: '',
  organization: '',
  region: '',
  frequency: 'quarterly',
  startDate: '',
  endDate: '',
  notes: '',
}

const PIXEL_SIZE_M = 10
const TILE_PX = 64
const TILE_SIZE_M = PIXEL_SIZE_M * TILE_PX
const ORIGIN_SHIFT = Math.PI * 6378137

function lonLatToMerc(lon, lat) {
  const x = (lon * ORIGIN_SHIFT) / 180
  let y = Math.log(Math.tan(((90 + lat) * Math.PI) / 360)) / (Math.PI / 180)
  y = (y * ORIGIN_SHIFT) / 180
  return [x, y]
}

function mercToLonLat(x, y) {
  const lon = (x / ORIGIN_SHIFT) * 180
  let lat = (y / ORIGIN_SHIFT) * 180
  lat = (180 / Math.PI) * (2 * Math.atan(Math.exp((lat * Math.PI) / 180)) - Math.PI / 2)
  return [lon, lat]
}

function gridIndex(mx, my) {
  return [Math.floor(mx / TILE_SIZE_M), Math.floor(my / TILE_SIZE_M)]
}

function cellBoundsFromIndex(gx, gy) {
  return {
    minX: gx * TILE_SIZE_M,
    minY: gy * TILE_SIZE_M,
    maxX: (gx + 1) * TILE_SIZE_M,
    maxY: (gy + 1) * TILE_SIZE_M,
  }
}

function selectionFromGrid(gx1, gy1, gx2, gy2) {
  const minGX = Math.min(gx1, gx2)
  const maxGX = Math.max(gx1, gx2)
  const minGY = Math.min(gy1, gy2)
  const maxGY = Math.max(gy1, gy2)

  const minBounds = cellBoundsFromIndex(minGX, minGY)
  const maxBounds = cellBoundsFromIndex(maxGX, maxGY)
  const sw = mercToLonLat(minBounds.minX, minBounds.minY)
  const ne = mercToLonLat(maxBounds.maxX, maxBounds.maxY)
  const tileCountX = maxGX - minGX + 1
  const tileCountY = maxGY - minGY + 1

  return {
    tile_grid_range: { gx: [minGX, maxGX], gy: [minGY, maxGY] },
    tile_count: { x: tileCountX, y: tileCountY, total: tileCountX * tileCountY },
    pixel_size_m: PIXEL_SIZE_M,
    tile_px: TILE_PX,
    area_km2: +((tileCountX * TILE_SIZE_M * tileCountY * TILE_SIZE_M) / 1e6).toFixed(3),
    bbox_lonlat: { west: sw[0], south: sw[1], east: ne[0], north: ne[1] },
    bbox_mercator: {
      minX: minBounds.minX,
      minY: minBounds.minY,
      maxX: maxBounds.maxX,
      maxY: maxBounds.maxY,
    },
  }
}

export default function RequestForm() {
  const [form, setForm] = useState(INITIAL)
  const [submitted, setSubmitted] = useState(false)
  const [selection, setSelection] = useState(null)
  const [drawMode, setDrawMode] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const mapContainerRef = useRef(null)
  const mapRef = useRef(null)
  const rectLayerRef = useRef(null)
  const gridLayerRef = useRef(null)
  const dragStateRef = useRef({ active: false, startGrid: null })
  const drawModeRef = useRef(false)

  function handleChange(e) {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  function clearSelection() {
    dragStateRef.current = { active: false, startGrid: null }
    setSelection(null)

    if (rectLayerRef.current) {
      rectLayerRef.current.remove()
      rectLayerRef.current = null
    }

    if (gridLayerRef.current) {
      gridLayerRef.current.clearLayers()
    }
  }

  function submitAoiRequestPayload() {
    return {
      requester: {
        name: form.name,
        email: form.email,
        organization: form.organization,
        region: form.region,
      },
      monitoring: {
        frequency: form.frequency,
        startDate: form.startDate,
        endDate: form.endDate,
        notes: form.notes,
      },
      area: selection,
    }
  }

  function updateSelection(gx1, gy1, gx2, gy2) {
    const nextSelection = selectionFromGrid(gx1, gy1, gx2, gy2)

    if (rectLayerRef.current) {
      rectLayerRef.current.remove()
      rectLayerRef.current = null
    }

    if (gridLayerRef.current) {
      gridLayerRef.current.clearLayers()
    }

    const minGX = nextSelection.tile_grid_range.gx[0]
    const maxGX = nextSelection.tile_grid_range.gx[1]
    const minGY = nextSelection.tile_grid_range.gy[0]
    const maxGY = nextSelection.tile_grid_range.gy[1]
    const sw = [nextSelection.bbox_lonlat.south, nextSelection.bbox_lonlat.west]
    const ne = [nextSelection.bbox_lonlat.north, nextSelection.bbox_lonlat.east]

    rectLayerRef.current = L.rectangle([sw, ne], {
      color: '#ff6b35',
      weight: 2,
      fillOpacity: 0.12,
    }).addTo(mapRef.current)

    if ((maxGX - minGX + 1) * (maxGY - minGY + 1) <= 4000) {
      for (let gx = minGX; gx <= maxGX; gx += 1) {
        for (let gy = minGY; gy <= maxGY; gy += 1) {
          const bounds = cellBoundsFromIndex(gx, gy)
          const cellSw = mercToLonLat(bounds.minX, bounds.minY)
          const cellNe = mercToLonLat(bounds.maxX, bounds.maxY)
          L.rectangle(
            [[cellSw[1], cellSw[0]], [cellNe[1], cellNe[0]]],
            {
              color: '#ff6b35',
              weight: 0.7,
              fillOpacity: 0,
              opacity: 0.55,
            },
          ).addTo(gridLayerRef.current)
        }
      }
    }

    setSelection(nextSelection)
  }

  async function handleSubmit(e) {
    e.preventDefault()

    if (!selection) {
      setSubmitError('Select a target area on the map before submitting the request.')
      return
    }

    setSubmitError('')
    setSubmitting(true)

    try {
      await submitAoiRequest(submitAoiRequestPayload())
      setSubmitted(true)
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Unable to submit the request.')
    } finally {
      setSubmitting(false)
    }
  }

  useEffect(() => {
    if (submitted) {
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
        gridLayerRef.current = null
        rectLayerRef.current = null
      }

      return undefined
    }

    if (!mapContainerRef.current) {
      return undefined
    }

    if (mapRef.current) {
      mapRef.current.remove()
      mapRef.current = null
      gridLayerRef.current = null
      rectLayerRef.current = null
    }

    const map = L.map(mapContainerRef.current, {
      scrollWheelZoom: false,
    }).setView([46.77, 23.59], 13)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map)

    mapRef.current = map
    gridLayerRef.current = L.layerGroup().addTo(map)

    function snappedGridFromLatLng(latlng) {
      const [mx, my] = lonLatToMerc(latlng.lng, latlng.lat)
      return gridIndex(mx, my)
    }

    function drawSelectionFromEvent(startGrid, currentLatLng) {
      const currentGrid = snappedGridFromLatLng(currentLatLng)
      updateSelection(startGrid[0], startGrid[1], currentGrid[0], currentGrid[1])
    }

    map.on('mousedown', (event) => {
      if (!drawModeRef.current) {
        return
      }

      dragStateRef.current = {
        active: true,
        startGrid: snappedGridFromLatLng(event.latlng),
      }
      drawSelectionFromEvent(dragStateRef.current.startGrid, event.latlng)
    })

    map.on('mousemove', (event) => {
      if (!drawModeRef.current) {
        return
      }

      if (!dragStateRef.current.active || !dragStateRef.current.startGrid) {
        return
      }

      drawSelectionFromEvent(dragStateRef.current.startGrid, event.latlng)
    })

    map.on('mouseup', (event) => {
      if (!drawModeRef.current) {
        return
      }

      if (!dragStateRef.current.active || !dragStateRef.current.startGrid) {
        return
      }

      drawSelectionFromEvent(dragStateRef.current.startGrid, event.latlng)
      dragStateRef.current = { active: false, startGrid: null }
    })

    return () => {
      map.remove()
      mapRef.current = null
      gridLayerRef.current = null
      rectLayerRef.current = null
    }
  }, [submitted])

  useEffect(() => {
    if (!mapRef.current || submitted) {
      return
    }

    drawModeRef.current = drawMode

    const map = mapRef.current
    if (drawMode) {
      map.dragging.disable()
    } else {
      map.dragging.enable()
    }

    map.getContainer().classList.toggle('drawing', drawMode)
  }, [drawMode, submitted])

  if (submitted) {
    return (
      <section className="request-form" id="request">
        <div className="request-form__success">
          <h2>Request received</h2>
          <p>
            Thanks, {form.name || 'there'}. Your personal area-of-interest request
            has been queued. You'll receive an email with a quote and further instructions once the request has been processed.
          </p>
          
          <button
            type="button"
            className="btn btn--secondary"
            onClick={() => {
              setSubmitted(false)
              setForm(INITIAL)
              clearSelection()
              setDrawMode(false)
              setSubmitError('')
            }}
          >
            Submit another request
          </button>
        </div>
      </section>
    )
  }

  return (
    <section
      className="request-form"
      id="request"
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '2rem',
        alignItems: 'start',
      }}
    >
      <div className="request-form__intro" style={{ gridColumn: '1 / -1' }}>

        <h2 style={{marginLeft: '1rem'}}>Request a personal AOI (area of interest)</h2>
        <p className="request-form__intro-text" style={{marginLeft: '1rem'}}>
          Require a personal land cover analysis for your area of interest? Fill out the form below to submit a request. We&apos;ll get back to you as soon as possible.
        </p>
      </div>

      <div className="form__map-picker form__map-picker--standalone" style={{ gridColumn: 1 }}>
        <div className="form__map-shell">
          <div className="form__map-toolbar">
            <button
              type="button"
              className={`btn btn--secondary form__toggle ${drawMode ? 'is-active' : ''}`}
              onClick={() => setDrawMode((prev) => !prev)}
            >
              {drawMode ? 'Selection on' : 'Select area'}
            </button>
            <button
              type="button"
              className="btn btn--secondary form__toggle"
              onClick={() => clearSelection()}
            >
              Clear selection
            </button>
          </div>

          <div className="form__map-hint">
            Click <strong>Select area</strong>, then drag corner-to-corner on the map to snap your target area to the Sentinel-2 tile grid.
          </div>

          <div
            className="form__map"
            ref={mapContainerRef}
            aria-label="Sentinel-2 tile grid picker"
          />
        </div>
      </div>

      <form
        className="form"
        onSubmit={handleSubmit}
        style={{ gridColumn: 2 }}
      >
        <div className="form__row">
          <label htmlFor="name">Full name</label>
          <input
            id="name"
            name="name"
            type="text"
            required
            value={form.name}
            onChange={handleChange}
            placeholder="Jane Doe"
          />
        </div>

        <div className="form__row">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={form.email}
            onChange={handleChange}
            placeholder="jane@example.com"
          />
        </div>

        <div className="form__row form__row--full">
          <label>Chosen land surface</label>
          <div className="form__selection-field">
            {selection ? (
              <dl>
                <div>
                  <dt>Tile count : {selection.tile_count.total} total </dt>
                </div>
                <div>
                  <dt>Grid range : 
                    
                    gx ∈ {'['}{selection.tile_grid_range.gx[0]},{selection.tile_grid_range.gx[1]}{']'} and gy ∈ {'['}{selection.tile_grid_range.gy[0]},{selection.tile_grid_range.gy[1]}{']'}
                  </dt>
                </div>
                <div>
                  <dt>Area : {selection.area_km2} km²</dt>
                </div>
              </dl>
            ) : (
              <p>
                No selection yet. Choose a target area to generate the tile grid and bounding box.
              </p>
            )}
          </div>

          <input
            type="hidden"
            name="areaSelection"
            value={selection ? JSON.stringify(selection) : ''}
            readOnly
          />
        </div>

        <div className="form__row form__row--full">
          <label htmlFor="frequency">Monitoring frequency</label>
          <select
            id="frequency"
            name="frequency"
            value={form.frequency}
            onChange={handleChange}
          >
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="annual">Annual</option>
          </select>
        </div>
        
        <div className="form__row">
          <label> Starting date</label>
          <input
            id="startDate"
            name="startDate"
            type="date"
            value={form.startDate}
            onChange={handleChange}
          />
        </div>

        <div className="form__row">
          <label> End date</label>
          <input
            id="endDate"
            name="endDate"
            type="date"
            value={form.endDate}
            onChange={handleChange}
          />
        </div>

        
        <div className="form__row">
          <label htmlFor="region">Region of interest</label>
          <input
            id="region"
            name="region"
            type="text"
            value={form.region}
            onChange={handleChange}
            placeholder="Cluj-Napoca, Romania"
          />
        </div>
        <div className="form__row">
          <label htmlFor="organization">Organization / affiliation</label>
          <input
            id="organization"
            name="organization"
            type="text"
            value={form.organization}
            onChange={handleChange}
            placeholder="University of Cluj-Napoca"
          />
        </div>
        
        <div className="form__row form__row--full">
          <label htmlFor="notes">Additional notes (optional)</label>
          <textarea
            id="notes"
            name="notes"
            rows={2}
            value={form.notes}
            onChange={handleChange}
            placeholder="Specific classes of interest, date range, deliverable format…"
          />
        </div>

        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? 'Submitting...' : 'Submit request'}
        </button>
        {submitError && <p className="form__error">{submitError}</p>}

      </form>
    </section>
  )
}