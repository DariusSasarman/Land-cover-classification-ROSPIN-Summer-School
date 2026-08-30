export default function HowItWorks() {
  const steps = [
    {
      title: 'Define your AOI',
      text: 'Draw or upload a polygon for the region you want monitored.',
    },
    {
      title: 'ResNet inference',
      text: 'Sentinel-2 patches are classified into 10 EuroSAT land-cover classes.',
    },
    {
      title: 'Track over time',
      text: 'Quarterly snapshots reveal seasonal shifts in crops, water, and built-up areas.',
    },
  ]

  return (
    <section className="how-it-works" id="how-it-works">
      <div className="section-header">
        <h2>How it works</h2>
        <p>
          LandObservator runs a ResNet trained on EuroSAT to produce land-cover
          statistics for any area of interest.
        </p>
      </div>
      <ol className="steps">
        {steps.map((step, i) => (
          <li key={step.title} className="step">
            <span className="step__num">{i + 1}</span>
            <div>
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </div>
          </li>
        ))}
      </ol>
      <div className="model-note">
        <strong>Model:</strong> ResNet · <strong>Dataset:</strong> EuroSAT (10 classes)
        · <strong>Output:</strong> per-class percentages aggregated over the AOI
      </div>
    </section>
  )
}
