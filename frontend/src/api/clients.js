import axios from 'axios'

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

export { authApi, chatbotApi, knowledgeApi }
