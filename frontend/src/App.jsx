import { useEffect, useState } from 'react'
import axios from 'axios'
import './App.css'

const authApi = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/auth',
  withCredentials: true,
})

const chatbotApi = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/chatbot',
  withCredentials: true,
})

const knowledgeApi = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/knowledge-base',
  withCredentials: true,
})

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(localStorage.getItem('access_token')))
  const [mode, setMode] = useState('login')
  const [resetVerified, setResetVerified] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [resourceLoading, setResourceLoading] = useState(false)

  const [sessionId, setSessionId] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [chatQuery, setChatQuery] = useState('')

  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
  })

  const [registerData, setRegisterData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: '',
  })

  const [forgotData, setForgotData] = useState({
    email: '',
  })

  const [uploadData, setUploadData] = useState({
    title: '',
    file: null,
  })

  const [urlData, setUrlData] = useState({
    url: '',
  })

  const [resetData, setResetData] = useState({
    uid: '',
    token: '',
    password: '',
    password_confirm: '',
  })

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

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token')
    return {
      Authorization: `Bearer ${token}`,
    }
  }

  const handleModeChange = (nextMode) => {
    setMode(nextMode)
    setResetVerified(false)
    setMessage('')
    setError('')
  }

  const handleLoginChange = (event) => {
    const { name, value } = event.target
    setLoginData((prev) => ({ ...prev, [name]: value }))
  }

  const handleRegisterChange = (event) => {
    const { name, value } = event.target
    setRegisterData((prev) => ({ ...prev, [name]: value }))
  }

  const handleForgotChange = (event) => {
    const { name, value } = event.target
    setForgotData((prev) => ({ ...prev, [name]: value }))
  }

  const handleResetChange = (event) => {
    const { name, value } = event.target
    setResetData((prev) => ({ ...prev, [name]: value }))
  }

  const handleUploadChange = (event) => {
    const { name, value, files } = event.target

    if (name === 'file') {
      setUploadData((prev) => ({ ...prev, file: files?.[0] || null }))
      return
    }

    setUploadData((prev) => ({ ...prev, [name]: value }))
  }

  const handleUrlChange = (event) => {
    const { name, value } = event.target
    setUrlData((prev) => ({ ...prev, [name]: value }))
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const nextMode = params.get('mode')
    const uid = params.get('uid')
    const token = params.get('token')

    if (nextMode === 'reset' && uid && token) {
      setMode('reset')
      setResetData((prev) => ({
        ...prev,
        uid,
        token,
      }))
    }
  }, [])

  useEffect(() => {
    const verifyToken = async () => {
      if (mode !== 'reset' || !resetData.uid || !resetData.token) {
        return
      }

      setLoading(true)
      setMessage('')
      setError('')

      try {
        const response = await authApi.get('/reset-password/verify/', {
          params: {
            uid: resetData.uid,
            token: resetData.token,
          },
        })
        setResetVerified(true)
        setMessage(response?.data?.message || 'Reset token is valid.')
      } catch (err) {
        setResetVerified(false)
        setError(parseError(err))
      } finally {
        setLoading(false)
      }
    }

    verifyToken()
  }, [mode, resetData.uid, resetData.token])

  const handleLogin = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    setError('')

    try {
      const response = await authApi.post('/login/', loginData)
      const access = response?.data?.access

      if (access) {
        localStorage.setItem('access_token', access)
        setIsAuthenticated(true)
      }

      setMessage('Login successful.')
    } catch (err) {
      setError(parseError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    setError('')

    try {
      const response = await authApi.post('/register/', registerData)
      setMessage(response?.data?.message || 'Registration successful.')
      setRegisterData({
        email: '',
        first_name: '',
        last_name: '',
        password: '',
        password_confirm: '',
      })
      setMode('login')
    } catch (err) {
      setError(parseError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleForgotPassword = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    setError('')

    try {
      const response = await authApi.post('/forgot-password/', forgotData)
      setMessage(response?.data?.message || 'If this email exists, a reset link has been sent.')
    } catch (err) {
      setError(parseError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (event) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    setError('')

    try {
      const response = await authApi.post('/reset-password/', resetData)
      setMessage(response?.data?.message || 'Password reset successful.')
      setResetData({
        uid: '',
        token: '',
        password: '',
        password_confirm: '',
      })
      setMode('login')
      setResetVerified(false)
      window.history.replaceState({}, '', '/')
    } catch (err) {
      setError(parseError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setIsAuthenticated(false)
    setSessionId(null)
    setChatMessages([])
    setChatQuery('')
    setMessage('Logged out successfully.')
    setError('')
  }

  const handlePdfUpload = async (event) => {
    event.preventDefault()
    if (!uploadData.file) {
      setError('Please select a PDF file.')
      return
    }

    setResourceLoading(true)
    setError('')
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('title', uploadData.title)
      formData.append('file', uploadData.file)

      const response = await knowledgeApi.post('/upload/', formData, {
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'multipart/form-data',
        },
      })

      setMessage(response?.data?.message || 'PDF uploaded and processed.')
      setUploadData({ title: '', file: null })
    } catch (err) {
      setError(parseError(err))
    } finally {
      setResourceLoading(false)
    }
  }

  const handleUrlIngest = async (event) => {
    event.preventDefault()
    setResourceLoading(true)
    setError('')
    setMessage('')

    try {
      const response = await knowledgeApi.post('/website-link/', urlData, {
        headers: getAuthHeaders(),
      })
      setMessage(response?.data?.message || 'Website content processed.')
      setUrlData({ url: '' })
    } catch (err) {
      setError(parseError(err))
    } finally {
      setResourceLoading(false)
    }
  }

  const handleChatSubmit = async (event) => {
    event.preventDefault()
    if (!chatQuery.trim()) {
      return
    }

    const userText = chatQuery.trim()
    setChatMessages((prev) => [...prev, { role: 'user', content: userText }])
    setChatQuery('')
    setChatLoading(true)
    setError('')

    try {
      const payload = { query: userText }
      if (sessionId) {
        payload.session_id = sessionId
      }

      const response = await chatbotApi.post('/ask/', payload, {
        headers: getAuthHeaders(),
      })

      const nextSessionId = response?.data?.session_id
      const answer = response?.data?.answer || 'No response from AI.'
      const sources = response?.data?.sources || []

      if (nextSessionId && !sessionId) {
        setSessionId(nextSessionId)
      }

      setChatMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: answer,
          sources,
        },
      ])
    } catch (err) {
      setError(parseError(err))
    } finally {
      setChatLoading(false)
    }
  }

  if (isAuthenticated) {
    return (
      <main className="auth-page">
        <section className="dashboard-card">
          <div className="dashboard-header">
            <h1>AI Knowledge Chat</h1>
            <button type="button" onClick={handleLogout}>Logout</button>
          </div>

          <div className="dashboard-grid">
            <div className="panel">
              <h2>Add PDF Context</h2>
              <form className="auth-form" onSubmit={handlePdfUpload}>
                <input
                  type="text"
                  name="title"
                  placeholder="Optional title"
                  value={uploadData.title}
                  onChange={handleUploadChange}
                />
                <input
                  type="file"
                  name="file"
                  accept="application/pdf"
                  onChange={handleUploadChange}
                  required
                />
                <button type="submit" disabled={resourceLoading}>
                  {resourceLoading ? 'Processing...' : 'Upload PDF'}
                </button>
              </form>

              <h2>Add URL Context</h2>
              <form className="auth-form" onSubmit={handleUrlIngest}>
                <input
                  type="url"
                  name="url"
                  placeholder="https://example.com"
                  value={urlData.url}
                  onChange={handleUrlChange}
                  required
                />
                <button type="submit" disabled={resourceLoading}>
                  {resourceLoading ? 'Processing...' : 'Process URL'}
                </button>
              </form>
            </div>

            <div className="panel chat-panel">
              <h2>Chatbot</h2>
              <div className="chat-box">
                {chatMessages.length === 0 ? (
                  <p className="chat-placeholder">Upload PDF or process a URL, then ask a question.</p>
                ) : (
                  chatMessages.map((item, index) => (
                    <div key={`${item.role}-${index}`} className={`chat-message ${item.role}`}>
                      <p>{item.content}</p>
                      {item.role === 'ai' && Array.isArray(item.sources) && item.sources.length > 0 && (
                        <small>Sources: {item.sources.join(', ')}</small>
                      )}
                    </div>
                  ))
                )}
              </div>

              <form className="chat-form" onSubmit={handleChatSubmit}>
                <input
                  type="text"
                  placeholder="Ask based on uploaded PDF or URL content"
                  value={chatQuery}
                  onChange={(event) => setChatQuery(event.target.value)}
                  required
                />
                <button type="submit" disabled={chatLoading}>
                  {chatLoading ? 'Thinking...' : 'Send'}
                </button>
              </form>
            </div>
          </div>

          {message && <p className="status success">{message}</p>}
          {error && <p className="status error">{error}</p>}
        </section>
      </main>
    )
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <h1>Authentication</h1>

        <div className="auth-tabs">
          <button
            type="button"
            className={mode === 'login' ? 'active' : ''}
            onClick={() => handleModeChange('login')}
          >
            Login
          </button>
          <button
            type="button"
            className={mode === 'register' ? 'active' : ''}
            onClick={() => handleModeChange('register')}
          >
            Register
          </button>
          <button
            type="button"
            className={mode === 'forgot' ? 'active' : ''}
            onClick={() => handleModeChange('forgot')}
          >
            Forgot
          </button>
        </div>

        {mode === 'login' ? (
          <form className="auth-form" onSubmit={handleLogin}>
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={loginData.email}
              onChange={handleLoginChange}
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={loginData.password}
              onChange={handleLoginChange}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Please wait...' : 'Login'}
            </button>
            <button
              type="button"
              className="link-btn"
              onClick={() => handleModeChange('forgot')}
            >
              Forgot password?
            </button>
          </form>
        ) : mode === 'register' ? (
          <form className="auth-form" onSubmit={handleRegister}>
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={registerData.email}
              onChange={handleRegisterChange}
              required
            />
            <input
              type="text"
              name="first_name"
              placeholder="First name"
              value={registerData.first_name}
              onChange={handleRegisterChange}
            />
            <input
              type="text"
              name="last_name"
              placeholder="Last name"
              value={registerData.last_name}
              onChange={handleRegisterChange}
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={registerData.password}
              onChange={handleRegisterChange}
              required
            />
            <input
              type="password"
              name="password_confirm"
              placeholder="Confirm password"
              value={registerData.password_confirm}
              onChange={handleRegisterChange}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Please wait...' : 'Register'}
            </button>
          </form>
        ) : mode === 'forgot' ? (
          <form className="auth-form" onSubmit={handleForgotPassword}>
            <input
              type="email"
              name="email"
              placeholder="Enter your account email"
              value={forgotData.email}
              onChange={handleForgotChange}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Please wait...' : 'Send reset email'}
            </button>
          </form>
        ) : (
          <form className="auth-form" onSubmit={handleResetPassword}>
            <input
              type="password"
              name="password"
              placeholder="New password"
              value={resetData.password}
              onChange={handleResetChange}
              required
              disabled={!resetVerified}
            />
            <input
              type="password"
              name="password_confirm"
              placeholder="Confirm new password"
              value={resetData.password_confirm}
              onChange={handleResetChange}
              required
              disabled={!resetVerified}
            />
            <button type="submit" disabled={loading || !resetVerified}>
              {loading ? 'Please wait...' : 'Reset password'}
            </button>
          </form>
        )}

        {message && <p className="status success">{message}</p>}
        {error && <p className="status error">{error}</p>}
      </section>
    </main>
  )
}

export default App
