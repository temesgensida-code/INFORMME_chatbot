const parseError = (err) => {
  const payload = err?.response?.data

  if (!payload) {
    return 'Request failed. Please try again.'
  }

  if (typeof payload === 'string') {
    return payload
  }

  if (payload.detail) {
    return payload.detail
  }

  if (payload.error) {
    return payload.error
  }

  const firstEntry = Object.values(payload)[0]
  if (Array.isArray(firstEntry)) {
    return firstEntry[0]
  }

  if (typeof firstEntry === 'string') {
    return firstEntry
  }

  return 'Something went wrong. Please check your input.'
}

export default parseError
