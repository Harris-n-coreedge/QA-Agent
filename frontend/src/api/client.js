import axios from 'axios'

const API_BASE_URL = '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Sessions API
export const sessionsAPI = {
  create: async (data) => {
    const response = await apiClient.post('/qa-tests/sessions', data)
    return response.data
  },

  list: async () => {
    const response = await apiClient.get('/qa-tests/sessions')
    return response.data
  },

  get: async (sessionId) => {
    const response = await apiClient.get(`/qa-tests/sessions/${sessionId}`)
    return response.data
  },

  executeCommand: async (sessionId, command) => {
    const response = await apiClient.post(`/qa-tests/sessions/${sessionId}/commands`, {
      session_id: sessionId,
      command,
    })
    return response.data
  },

  close: async (sessionId) => {
    const response = await apiClient.delete(`/qa-tests/sessions/${sessionId}`)
    return response.data
  },
}

// Browser Use API
export const browserUseAPI = {
  execute: async (task, aiProvider = 'google') => {
    const response = await apiClient.post('/qa-tests/browser-use/execute', {
      task,
      ai_provider: aiProvider,
    })
    return response.data
  },
}

// Test Results API
export const testResultsAPI = {
  list: async (sessionId = null, limit = 50) => {
    const params = new URLSearchParams()
    if (sessionId) params.append('session_id', sessionId)
    if (limit) params.append('limit', limit)

    const response = await apiClient.get(`/qa-tests/test-results?${params}`)
    return response.data
  },

  get: async (testId) => {
    const response = await apiClient.get(`/qa-tests/test-results/${testId}`)
    return response.data
  },
}

// Health Check
export const healthAPI = {
  check: async () => {
    const response = await apiClient.get('/qa-tests/health')
    return response.data
  },
}

export default apiClient
