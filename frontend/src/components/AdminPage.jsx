function AdminPage({
  adminDocuments,
  adminLoading,
  resourceLoading,
  uploadData,
  urlData,
  handlePdfUpload,
  handleUploadChange,
  handleUrlIngest,
  handleUrlChange,
  handleDeleteDocument,
  handleRefreshContextCache,
  navigateToPage,
  handleLogout,
  message,
  error,
}) {
  const pdfDocuments = adminDocuments.filter((doc) => doc.source_type === 'pdf')
  const urlDocuments = adminDocuments.filter((doc) => doc.source_type === 'url')

  return (
    <main className="auth-page">
      <section className="dashboard-card">
        <div className="dashboard-header">
          <h1>Admin Page</h1>
          <div>
            <button type="button" onClick={handleRefreshContextCache} disabled={resourceLoading}>
              {resourceLoading ? 'Refreshing...' : 'Refresh Cache'}
            </button>
            <button type="button" onClick={() => navigateToPage('chatbot')}>To /chatbot</button>
            <button type="button" onClick={handleLogout}>Logout</button>
          </div>
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

          <div className="panel">
            <h2>Uploaded PDFs</h2>
            {adminLoading ? (
              <p>Loading documents...</p>
            ) : pdfDocuments.length === 0 ? (
              <p>No uploaded PDFs found.</p>
            ) : (
              pdfDocuments.map((doc) => (
                <div key={doc.id} className="chat-message ai">
                  <p>{doc.title}</p>
                  <small>{doc.is_processed ? 'Processed' : 'Pending processing'}</small>
                  <div>
                    <button
                      type="button"
                      onClick={() => handleDeleteDocument(doc.id)}
                      disabled={resourceLoading}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ))
            )}

            <h2 style={{ marginTop: '1rem' }}>Processed URLs</h2>
            {adminLoading ? (
              <p>Loading documents...</p>
            ) : urlDocuments.length === 0 ? (
              <p>No processed URLs found.</p>
            ) : (
              urlDocuments.map((doc) => (
                <div key={doc.id} className="chat-message ai">
                  <p>{doc.url || doc.title}</p>
                  <small>{doc.is_processed ? 'Processed' : 'Pending processing'}</small>
                  <div>
                    <button
                      type="button"
                      onClick={() => handleDeleteDocument(doc.id)}
                      disabled={resourceLoading}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {message && <p className="status success">{message}</p>}
        {error && <p className="status error">{error}</p>}
      </section>
    </main>
  )
}

export default AdminPage
