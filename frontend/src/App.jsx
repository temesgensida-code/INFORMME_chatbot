import { useState } from 'react'
import './App.css'
import informmeLogo from './assets/INFORMME.png'
import AuthPage from './components/AuthPage'
import AdminPage from './components/AdminPage'
import ChatbotPage from './components/ChatbotPage'
import useAuthFlow from './hooks/useAuthFlow'
import useAdminKnowledge from './hooks/useAdminKnowledge'
import useChatbot from './hooks/useChatbot'

function App() {
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const auth = useAuthFlow({ setMessage, setError })

  const admin = useAdminKnowledge({
    isAuthenticated: auth.isAuthenticated,
    isSuperuser: auth.isSuperuser,
    currentPage: auth.currentPage,
    getAuthHeaders: auth.getAuthHeaders,
    setMessage,
    setError,
  })

  const chatbot = useChatbot({
    isAuthenticated: auth.isAuthenticated,
    currentPage: auth.currentPage,
    getAuthHeaders: auth.getAuthHeaders,
    setError,
  })

  const handleLogout = () => {
    auth.handleLogout()
    admin.clearAdminState()
    chatbot.clearChatState()
  }

  if (auth.isAuthenticated) {
    if (auth.isSuperuser && auth.currentPage === 'admin') {
      return (
        <AdminPage
          adminDocuments={admin.adminDocuments}
          adminLoading={admin.adminLoading}
          resourceLoading={admin.resourceLoading}
          uploadData={admin.uploadData}
          urlData={admin.urlData}
          handlePdfUpload={admin.handlePdfUpload}
          handleUploadChange={admin.handleUploadChange}
          handleUrlIngest={admin.handleUrlIngest}
          handleUrlChange={admin.handleUrlChange}
          handleDeleteDocument={admin.handleDeleteDocument}
          handleRefreshContextCache={admin.handleRefreshContextCache}
          navigateToPage={auth.navigateToPage}
          handleLogout={handleLogout}
          message={message}
          error={error}
        />
      )
    }

    return (
      <ChatbotPage
        isSuperuser={auth.isSuperuser}
        navigateToPage={auth.navigateToPage}
        handleLogout={handleLogout}
        informmeLogo={informmeLogo}
        chatMessages={chatbot.chatMessages}
        chatQuery={chatbot.chatQuery}
        setChatQuery={chatbot.setChatQuery}
        handleChatSubmit={chatbot.handleChatSubmit}
        chatLoading={chatbot.chatLoading}
        message={message}
        error={error}
      />
    )
  }

  return (
    <AuthPage
      mode={auth.mode}
      loading={auth.loading}
      resetVerified={auth.resetVerified}
      message={message}
      error={error}
      loginData={auth.loginData}
      registerData={auth.registerData}
      forgotData={auth.forgotData}
      resetData={auth.resetData}
      handleModeChange={auth.handleModeChange}
      handleLogin={auth.handleLogin}
      handleRegister={auth.handleRegister}
      handleForgotPassword={auth.handleForgotPassword}
      handleResetPassword={auth.handleResetPassword}
      handleLoginChange={auth.handleLoginChange}
      handleRegisterChange={auth.handleRegisterChange}
      handleForgotChange={auth.handleForgotChange}
      handleResetChange={auth.handleResetChange}
    />
  )
}

export default App