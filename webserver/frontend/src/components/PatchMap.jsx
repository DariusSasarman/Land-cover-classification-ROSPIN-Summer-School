import { EUROSAT_CLASS_BY_ID } from '../data/eurosatLabels.js'
import { buildPatchGrid, patchPlaceholderSrc } from '../utils/patchGrid.js'

export default function PatchMap({ areaName, snapshot, periodIndex }) {
  const { cols, rows, patches } = buildPatchGrid(snapshot, periodIndex)

  return (
    <div className="patch-map">
      <div className="patch-map__basemap" aria-label={`Satellite map of ${areaName}`}>
        <img
          className="patch-map__basemap-img"
          src="/placeholders/basemap.svg"
          alt=""
          aria-hidden="true"
        />
        <div
          className="patch-map__grid"
          style={{
            gridTemplateColumns: `repeat(${cols}, 1fr)`,
            gridTemplateRows: `repeat(${rows}, 1fr)`,
          }}
        >
          {patches.map((patch) => {
            const meta = EUROSAT_CLASS_BY_ID[patch.classId]
            return (
              <img
                key={`${patch.row}-${patch.col}`}
                className="patch-map__patch"
                src={patchPlaceholderSrc(patch.classId, meta.color)}
                alt=""
                title={meta.label}
              />
            )
          })}
        </div>
        <span className="patch-map__label">{areaName}</span>
      </div>
      <p className="patch-map__caption">
        Patch overlay placeholder — 64×64 tiles will load from inference output later.
      </p>
    </div>
  )
}
