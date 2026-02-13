import { useEffect, useState } from 'react'
import { chatbotApi } from '../api/clients'
import parseError from '../utils/parseError'

function useChatbot({ isAuthenticated, currentPage, getAuthHeaders, setError }) {
  const [chatLoading, setChatLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [chatQuery, setChatQuery] = useState('')

  const clearChatState = () => {
    setSessionId(null)
    setChatMessages([])
    setChatQuery('')
  }

  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!isAuthenticated || currentPage !== 'chatbot') {
        return
      }

      try {
        const response = await chatbotApi.get('/history/', {
          headers: getAuthHeaders(),
        })

        const nextSessionId = response?.data?.session_id || null
        const messages = Array.isArray(response?.data?.messages)
          ? response.data.messages.map((item) => ({
              role: item.role,
              content: item.content,
            }))
          : []

        setSessionId(nextSessionId)
        setChatMessages(messages)
      } catch (err) {
        setError(parseError(err))
      }
    }

    fetchChatHistory()
  }, [isAuthenticated, currentPage])

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

      setChatMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: '',
          sources: [],
          streaming: true,
        },
      ])

      const streamUrl = `${chatbotApi.defaults.baseURL}/ask/stream/`
      const streamResponse = await fetch(streamUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(payload),
      })

      if (!streamResponse.ok) {
        let backendError = 'Request failed. Please try again.'
        try {
          const errorPayload = await streamResponse.json()
          backendError = errorPayload?.error || errorPayload?.detail || backendError
        } catch {
          backendError = `Request failed with status ${streamResponse.status}.`
        }
        throw new Error(backendError)
      }

      if (!streamResponse.body) {
        throw new Error('Streaming is not supported by this browser.')
      }

      const reader = streamResponse.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      const appendChunk = (chunkText) => {
        setChatMessages((prev) => {
          if (prev.length === 0) {
            return prev
          }

          const next = [...prev]
          const last = { ...next[next.length - 1] }

          if (last.role !== 'ai') {
            return prev
          }

          last.content = `${last.content || ''}${chunkText}`
          next[next.length - 1] = last
          return next
        })
      }

      const finalizeStream = (sources = []) => {
        setChatMessages((prev) => {
          if (prev.length === 0) {
            return prev
          }

          const next = [...prev]
          const last = { ...next[next.length - 1] }

          if (last.role !== 'ai') {
            return prev
          }

          delete last.streaming
          last.sources = Array.isArray(sources) ? sources : []
          next[next.length - 1] = last
          return next
        })
      }

      while (true) {
        const { value, done } = await reader.read()
        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed) {
            continue
          }

          let eventData
          try {
            eventData = JSON.parse(trimmed)
          } catch {
            continue
          }

          if (eventData.type === 'chunk') {
            appendChunk(eventData.content || '')
          } else if (eventData.type === 'done') {
            if (eventData.session_id && !sessionId) {
              setSessionId(eventData.session_id)
            }
            finalizeStream(eventData.sources)
          } else if (eventData.type === 'error') {
            throw new Error(eventData.error || 'AI service is currently unavailable.')
          }
        }
      }

      if (buffer.trim()) {
        try {
          const eventData = JSON.parse(buffer.trim())
          if (eventData.type === 'done') {
            if (eventData.session_id && !sessionId) {
              setSessionId(eventData.session_id)
            }
            finalizeStream(eventData.sources)
          }
        } catch {
          // ignore trailing incomplete data
        }
      }
    } catch (err) {
      setError(err?.message || parseError(err))
      setChatMessages((prev) => {
        if (prev.length === 0) {
          return prev
        }

        const next = [...prev]
        const last = { ...next[next.length - 1] }
        if (last.role === 'ai' && last.streaming) {
          delete last.streaming
          next[next.length - 1] = last
        }
        return next
      })
    } finally {
      setChatLoading(false)
    }
  }

  return {
    chatLoading,
    chatMessages,
    chatQuery,
    setChatQuery,
    clearChatState,
    handleChatSubmit,
  }
}

export default useChatbot
