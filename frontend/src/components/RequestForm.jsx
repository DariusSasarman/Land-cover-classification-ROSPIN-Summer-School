import { useState } from 'react'

const INITIAL = {
  name: '',
  email: '',
  organization: '',
  region: '',
  areaDescription: '',
  frequency: 'quarterly',
  notes: '',
}

export default function RequestForm() {
  const [form, setForm] = useState(INITIAL)
  const [submitted, setSubmitted] = useState(false)

  function handleChange(e) {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <section className="request-form" id="request">
        <div className="request-form__success">
          <h2>Request received</h2>
          <p>
            Thanks, {form.name || 'there'}. Your personal area-of-interest request
            has been queued. We&apos;ll contact you at{' '}
            <strong>{form.email || 'your email'}</strong> with a quote and timeline.
          </p>
          <button
            type="button"
            className="btn btn--secondary"
            onClick={() => {
              setSubmitted(false)
              setForm(INITIAL)
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
      <div className="section-header" style={{ gridColumn: 1 }}>
        <h2>Request a personal AOI</h2>
        <p>
          Need monitoring for your own farm, watershed, or project site? Submit a
          request and we&apos;ll set up custom ResNet inference on your area.
        </p>
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

        <div className="form__row">
          <label htmlFor="organization">Organization (optional)</label>
          <input
            id="organization"
            name="organization"
            type="text"
            value={form.organization}
            onChange={handleChange}
            placeholder="University / NGO / Company"
          />
        </div>

        <div className="form__row">
          <label htmlFor="region">Region / country</label>
          <input
            id="region"
            name="region"
            type="text"
            required
            value={form.region}
            onChange={handleChange}
            placeholder="e.g. Tuscany, Italy"
          />
        </div>

        <div className="form__row form__row--full">
          <label htmlFor="areaDescription">Area description</label>
          <textarea
            id="areaDescription"
            name="areaDescription"
            required
            rows={3}
            value={form.areaDescription}
            onChange={handleChange}
            placeholder="Describe the polygon, size, and what land-cover changes you want to track."
          />
        </div>

        <div className="form__row">
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

        <button type="submit" className="btn btn--primary">
          Submit request
        </button>
        <p className="form__disclaimer">
          This is a front-end stub — no data is sent to a server.
        </p>
      </form>
    </section>
  )
}