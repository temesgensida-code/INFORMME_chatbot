import { useEffect, useState } from 'react'
import { knowledgeApi } from '../api/clients'
import parseError from '../utils/parseError'

function useAdminKnowledge({ isAuthenticated, isSuperuser, currentPage, getAuthHeaders, setMessage, setError }) {
  const [resourceLoading, setResourceLoading] = useState(false)
  const [adminLoading, setAdminLoading] = useState(false)
  const [adminDocuments, setAdminDocuments] = useState([])

  const [uploadData, setUploadData] = useState({
    title: '',
    file: null,
  })

  const [urlData, setUrlData] = useState({
    url: '',
  })

  const clearAdminState = () => {
    setAdminDocuments([])
    setUploadData({ title: '', file: null })
    setUrlData({ url: '' })
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

  const fetchAdminDocuments = async () => {
    if (!isAuthenticated || !isSuperuser) {
      return
    }

    setAdminLoading(true)
    try {
      const response = await knowledgeApi.get('/admin/documents/', {
        headers: getAuthHeaders(),
      })
      setAdminDocuments(Array.isArray(response?.data) ? response.data : [])
    } catch (err) {
      setError(parseError(err))
    } finally {
      setAdminLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated && isSuperuser && currentPage === 'admin') {
      fetchAdminDocuments()
    }
  }, [isAuthenticated, isSuperuser, currentPage])

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
      await fetchAdminDocuments()
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
      await fetchAdminDocuments()
    } catch (err) {
      setError(parseError(err))
    } finally {
      setResourceLoading(false)
    }
  }

  const handleDeleteDocument = async (documentId) => {
    setResourceLoading(true)
    setError('')
    setMessage('')

    try {
      const response = await knowledgeApi.delete(`/admin/documents/${documentId}/`, {
        headers: getAuthHeaders(),
      })
      setMessage(response?.data?.message || 'Document removed successfully.')
      await fetchAdminDocuments()
    } catch (err) {
      setError(parseError(err))
    } finally {
      setResourceLoading(false)
    }
  }

  const handleRefreshContextCache = async () => {
    setResourceLoading(true)
    setError('')
    setMessage('')

    try {
      const response = await knowledgeApi.post('/admin/refresh-context/', {}, {
        headers: getAuthHeaders(),
      })

      const removedDocuments = response?.data?.removed_documents ?? 0
      const removedVectors = response?.data?.removed_vectors ?? 0

      setMessage(`Context cache refreshed. Removed ${removedDocuments} documents and ${removedVectors} vectors.`)
      setAdminDocuments([])
      await fetchAdminDocuments()
    } catch (err) {
      setError(parseError(err))
    } finally {
      setResourceLoading(false)
    }
  }

  return {
    resourceLoading,
    adminLoading,
    adminDocuments,
    uploadData,
    urlData,
    clearAdminState,
    handleUploadChange,
    handleUrlChange,
    handlePdfUpload,
    handleUrlIngest,
    handleDeleteDocument,
    handleRefreshContextCache,
  }
}

export default useAdminKnowledge
