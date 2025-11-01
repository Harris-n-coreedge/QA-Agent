import axios from 'axios'

const API_BASE_URL = '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Agent API
export const agentAPI = {
  getStatus: async () => {
    const response = await apiClient.get('/qa-tests/agent-status')
    return response.data
  },

  navigateToUrl: async (websiteUrl) => {
    const response = await apiClient.post('/qa-tests/navigate', {
      website_url: websiteUrl,
    })
    return response.data
  },

  executeCommand: async (command) => {
    const response = await apiClient.post('/qa-tests/commands', {
      command,
    })
    return response.data
  },

  mobileTest: async (opts = { deviceName: 'iPhone 17 Pro Max', custom: null }) => {
    const payload = {}
    if (opts?.custom) {
      payload.custom = opts.custom
      if (opts.custom.name) payload.deviceName = opts.custom.name
    } else if (opts?.deviceName) {
      payload.deviceName = opts.deviceName
    }
    const response = await apiClient.post('/qa-tests/mobile-test', payload)
    return response.data
  },

  getBrowserView: async () => {
    const response = await apiClient.get('/qa-tests/browser-view')
    return response.data
  },

  crossBrowserTest: async (websiteUrl, browserType = null) => {
    const response = await apiClient.post('/qa-tests/cross-browser-test', {
      website_url: websiteUrl,
      browser_type: browserType,
    })
    return response.data
  },

  openBrowserExternal: async (websiteUrl, browserType) => {
    const response = await apiClient.post('/qa-tests/open-browser-external', {
      website_url: websiteUrl,
      browser_type: browserType,
    })
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
  list: async (limit = 50) => {
    const params = new URLSearchParams()
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
