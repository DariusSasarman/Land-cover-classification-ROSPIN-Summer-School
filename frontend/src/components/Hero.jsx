export default function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero__badge">ResNet · EuroSAT</div>
      <h1>Land cover intelligence over time</h1>
      <p className="hero__lead">
        Explore public areas of interest with ResNet classifications on Sentinel-2
        patches. Track EuroSAT land-cover labels and percentages as seasons change.
      </p>
      <div className="hero__stats">
        <div>
          <strong>10</strong>
          <span>EuroSAT classes</span>
        </div>
        <div>
          <strong>64×64</strong>
          <span>patch inference</span>
        </div>
        <div>
          <strong>Quarterly</strong>
          <span>time steps</span>
        </div>
      </div>
    </section>
  )
}
