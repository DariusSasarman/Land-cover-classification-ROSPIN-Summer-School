const REQUEST_ENDPOINT = '/api/requests'

export async function createRequest(payload) {
    /// dummy implementation for testing purposes
    return {
		id: 'dummy-request-id',
		...payload,
	}

	// real implementation
	const response = await fetch(REQUEST_ENDPOINT, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(payload),
	})

	if (!response.ok) {
		let message = 'Unable to submit the request.'

		try {
			const errorBody = await response.json()
			message = errorBody?.message || message
		} catch {
			message = response.statusText || message
		}

		throw new Error(message)
	}

	if (response.status === 204) {
		return null
	}

	return response.json()
}

