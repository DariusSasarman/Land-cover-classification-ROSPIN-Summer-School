const REQUEST_ENDPOINT = '/api/land-cover' // match requestApi.js

export async function loginRequest(email, password) {
  const response = await fetch(`${REQUEST_ENDPOINT}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    throw new Error(response.status === 401 ? 'Invalid email or password.' : 'Login failed.')
  }

  const data = await response.json()
  return data.token
}

export async function signupRequest(name,organization, email, password) {
  const response = await fetch(`${REQUEST_ENDPOINT}/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, organization, email, password }),
  })

  if (!response.ok) {
    throw new Error(response.status === 409 ? 'Account already exists.' : 'Signup failed.')
  }

  const data = await response.json()
  return data.token
}
