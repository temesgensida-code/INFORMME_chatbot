import { useEffect, useState } from 'react'
import { authApi } from '../api/clients'
import { getPageFromPath, hasValidAccessToken, isSuperuserFromToken } from '../utils/auth'
import parseError from '../utils/parseError'

function useAuthFlow({ setMessage, setError }) {
  const [isAuthenticated, setIsAuthenticated] = useState(hasValidAccessToken())
  const [isSuperuser, setIsSuperuser] = useState(isSuperuserFromToken())
  const [currentPage, setCurrentPage] = useState(getPageFromPath() || (isSuperuserFromToken() ? 'admin' : 'chatbot'))
  const [mode, setMode] = useState('login')
  const [resetVerified, setResetVerified] = useState(false)
  const [loading, setLoading] = useState(false)

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

  const [resetData, setResetData] = useState({
    uid: '',
    token: '',
    password: '',
    password_confirm: '',
  })

  const getAuthHeaders = () => {
    const token = hasValidAccessToken() ? localStorage.getItem('access_token') : null
    if (!token) {
      return {}
    }

    return {
      Authorization: `Bearer ${token}`,
    }
  }

  const navigateToPage = (page, replace = false) => {
    const nextPath = page === 'admin' ? '/admin' : '/chatbot'
    if (window.location.pathname !== nextPath) {
      const historyMethod = replace ? 'replaceState' : 'pushState'
      window.history[historyMethod]({}, '', nextPath)
    }
    setCurrentPage(page)
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

  useEffect(() => {
    const nextAuthenticated = hasValidAccessToken()
    const nextSuperuser = isSuperuserFromToken()
    const pathPage = getPageFromPath()

    setIsAuthenticated(nextAuthenticated)
    setIsSuperuser(nextSuperuser)

    if (!nextAuthenticated) {
      setCurrentPage('login')
      if (window.location.pathname === '/admin' || window.location.pathname === '/chatbot') {
        window.history.replaceState({}, '', '/')
      }
    } else if (nextSuperuser) {
      if (pathPage === 'chatbot' || pathPage === 'admin') {
        setCurrentPage(pathPage)
      } else {
        navigateToPage('admin', true)
      }
    } else {
      navigateToPage('chatbot', true)
    }

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
    const handlePopState = () => {
      if (!isAuthenticated) {
        return
      }

      const pathPage = getPageFromPath()
      if (isSuperuser) {
        if (pathPage === 'admin' || pathPage === 'chatbot') {
          setCurrentPage(pathPage)
          return
        }
        navigateToPage('admin', true)
        return
      }

      navigateToPage('chatbot', true)
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [isAuthenticated, isSuperuser])

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
  }, [mode, resetData.uid, resetData.token, setError, setMessage])

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
        const nextSuperuser = isSuperuserFromToken()
        setIsSuperuser(nextSuperuser)
        navigateToPage(nextSuperuser ? 'admin' : 'chatbot', true)
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
    setIsSuperuser(false)
    setCurrentPage('login')
    window.history.replaceState({}, '', '/')
    setMessage('Logged out successfully.')
    setError('')
  }

  return {
    isAuthenticated,
    isSuperuser,
    currentPage,
    mode,
    resetVerified,
    loading,
    loginData,
    registerData,
    forgotData,
    resetData,
    getAuthHeaders,
    navigateToPage,
    handleModeChange,
    handleLoginChange,
    handleRegisterChange,
    handleForgotChange,
    handleResetChange,
    handleLogin,
    handleRegister,
    handleForgotPassword,
    handleResetPassword,
    handleLogout,
  }
}

export default useAuthFlow
