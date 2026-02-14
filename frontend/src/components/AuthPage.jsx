import { useEffect, useRef } from 'react'

function AuthPage({
  mode,
  loading,
  resetVerified,
  message,
  error,
  loginData,
  registerData,
  forgotData,
  resetData,
  handleModeChange,
  handleLogin,
  handleRegister,
  handleForgotPassword,
  handleResetPassword,
  handleGoogleLogin,
  handleLoginChange,
  handleRegisterChange,
  handleForgotChange,
  handleResetChange,
}) {
  const googleButtonRef = useRef(null)

  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

    if (mode !== 'login' || !clientId || !handleGoogleLogin) {
      return undefined
    }

    let cancelled = false
    let boundScript = null

    const renderGoogleButton = () => {
      if (cancelled || !window.google?.accounts?.id || !googleButtonRef.current) {
        return
      }

      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response) => {
          if (response?.credential) {
            handleGoogleLogin(response.credential)
          }
        },
      })

      googleButtonRef.current.innerHTML = ''
      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: 'outline',
        size: 'large',
        shape: 'pill',
        width: 320,
        text: 'signin_with',
      })
    }

    if (window.google?.accounts?.id) {
      renderGoogleButton()
      return () => {
        cancelled = true
      }
    }

    const existingScript = document.getElementById('google-identity-script')
    if (existingScript) {
      boundScript = existingScript
      existingScript.addEventListener('load', renderGoogleButton)
      return () => {
        cancelled = true
        existingScript.removeEventListener('load', renderGoogleButton)
      }
    }

    const script = document.createElement('script')
    script.id = 'google-identity-script'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.addEventListener('load', renderGoogleButton)
    document.body.appendChild(script)
    boundScript = script

    return () => {
      cancelled = true
      if (boundScript) {
        boundScript.removeEventListener('load', renderGoogleButton)
      }
    }
  }, [mode, handleGoogleLogin])

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
            <div className="oauth-separator">or</div>
            <div className="google-login-wrapper" ref={googleButtonRef} />
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

export default AuthPage
