import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { loginRequest, signupRequest } from '../utils/loginApiCall.js'

export default function Login() {
  const { login } = useAuth()
  const [mode, setMode] = useState('signin') // 'signin' | 'signup'
  const [form, setForm] = useState({ name: '', organization: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const token = mode === 'signin'
        ? await loginRequest(form.email, form.password)
        : await signupRequest(form.name, form.organization, form.email, form.password)
      login(token)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="login">
      <h2>{mode === 'signin' ? 'Sign in' : 'Create account'}</h2>

      <form className="form" onSubmit={handleSubmit}>
        {mode === 'signup' && (
          <>
            <div className="form__row form__row--full">
              <label htmlFor="name">Name</label>
              <input id="name" name="name" value={form.name} onChange={handleChange} required />
            </div>
            <div className="form__row form__row--full">
              <label htmlFor="organization">Organization</label>
              <input id="organization" name="organization" value={form.organization} onChange={handleChange} required />
            </div>
          </>
        )}

        <div className="form__row form__row--full">
          <label htmlFor="email">Email</label>
          <input id="email" name="email" type="email" value={form.email} onChange={handleChange} required />
        </div>

        <div className="form__row form__row--full">
          <label htmlFor="password">Password</label>
          <input id="password" name="password" type="password" value={form.password} onChange={handleChange} required />
        </div>


        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? 'Please wait...' : mode === 'signin' ? 'Sign in' : 'Sign up'}
        </button>

        {error && <p className="form__error">{error}</p>}
      </form>

      <button
        type="button"
        className="btn btn--secondary"
        style={{ marginTop: '1rem' }}
        onClick={() => { setMode(mode === 'signin' ? 'signup' : 'signin'); setError('') }}
      >
        {mode === 'signin' ? 'Need an account? Sign up' : 'Already have an account? Sign in'}
      </button>
    </section>
  )
}
