export default function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero__eyebrow">
        <span className="hero__dot" />
        Sentinel-2 · EuroSAT · ResNet
      </div>

      <h1>
        See how the land
        <br />
        <em>changes over time.</em>
      </h1>

      <p className="hero__lead">
        LandObservator turns satellite imagery into clear land-cover insights.
        Explore public areas of interest, classify Sentinel-2 patches with
        ResNet, and track how landscapes evolve across the seasons.
      </p>

      <div className="hero__stats">
        <div className="hero__stat">
          <strong>10</strong>
          <span>land-cover classes</span>
        </div>

        <div className="hero__stat">
          <strong>640 × 640 m²</strong>
          <span>patch resolution</span>
        </div>

        <div className="hero__stat">
          <strong>4×</strong>
          <span>seasonal observations</span>
        </div>
      </div>
    </section>
  )
}
