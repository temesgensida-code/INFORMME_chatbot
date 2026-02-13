function ChatbotPage({
  isSuperuser,
  navigateToPage,
  handleLogout,
  informmeLogo,
  chatMessages,
  chatQuery,
  setChatQuery,
  handleChatSubmit,
  chatLoading,
  message,
  error,
}) {
  return (
    <main className="auth-page">
      <section className="dashboard-card">
        <div className="dashboard-header">
          <h1>INFORMME</h1>
          <div>
            {isSuperuser && (
              <button type="button" onClick={() => navigateToPage('admin')}>To /admin</button>
            )}
            <button type="button" onClick={handleLogout}>Logout</button>
          </div>
        </div>

        <div className="chatbot-layout">
          <div className="panel chatbot-brand-panel">
            <img src={informmeLogo} alt="INFORMME" className="chatbot-brand-image" />
          </div>

          <div className="panel chat-panel">
            <h2>Chatbot</h2>
            <div className="chat-box">
              {chatMessages.length === 0 ? (
                <p className="chat-placeholder">Ask a question based on uploaded context.</p>
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

export default ChatbotPage
