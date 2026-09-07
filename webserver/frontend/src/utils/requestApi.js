const REQUEST_ENDPOINT = '/api/land-cover'

export async function getDemoAreasHistory() {
  const response = await fetch(`${REQUEST_ENDPOINT}/demo`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })

  if (!response.ok) {
    throw new Error(`Land cover request failed: ${response.status}`)
  }

  return response.json()
}

export async function fetchAoiList(jwt) {
  const response = await fetch(`${REQUEST_ENDPOINT}/list`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwt}`,
    },
  })

  if (!response.ok) {
    throw new Error(`AOI list request failed: ${response.status}`)
  }

  return response.json()
}

export async function submitAoiRequest(payload, token) {
  const response = await fetch(`${REQUEST_ENDPOINT}/createaoi`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`AOI request failed: ${response.status}`)
  }

  return response.json()
}

