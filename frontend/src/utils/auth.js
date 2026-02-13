const decodeJwtPayload = (token) => {
  if (!token) {
    return null
  }

  try {
    const payloadPart = token.split('.')[1]
    const base64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/')
    const normalized = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
    return JSON.parse(atob(normalized))
  } catch {
    return null
  }
}

const hasValidAccessToken = () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    return false
  }

  const payload = decodeJwtPayload(token)
  const exp = payload?.exp
  if (!exp) {
    localStorage.removeItem('access_token')
    return false
  }

  const nowInSeconds = Math.floor(Date.now() / 1000)
  const isValid = exp > nowInSeconds

  if (!isValid) {
    localStorage.removeItem('access_token')
  }

  return isValid
}

const isSuperuserFromToken = () => {
  const token = localStorage.getItem('access_token')
  const payload = decodeJwtPayload(token)
  return Boolean(payload?.is_superuser)
}

const getPageFromPath = () => {
  const path = window.location.pathname
  if (path === '/admin') {
    return 'admin'
  }
  if (path === '/chatbot') {
    return 'chatbot'
  }
  return null
}

export {
  decodeJwtPayload,
  hasValidAccessToken,
  isSuperuserFromToken,
  getPageFromPath,
}
