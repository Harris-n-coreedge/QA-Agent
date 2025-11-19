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

// Performance Test API
export const performanceTestAPI = {
  // Load Tests
  runLoadTest: async (params) => {
    const response = await apiClient.post('/qa-tests/load-test', params)
    return response.data
  },
  runStressTest: async (params) => {
    const response = await apiClient.post('/qa-tests/stress-test', params)
    return response.data
  },
  runSpikeTest: async (params) => {
    const response = await apiClient.post('/qa-tests/spike-test', params)
    return response.data
  },
  runSoakTest: async (params) => {
    const response = await apiClient.post('/qa-tests/soak-test', params)
    return response.data
  },
  runRampUpTest: async (params) => {
    const response = await apiClient.post('/qa-tests/ramp-up-test', params)
    return response.data
  },
  runThroughputTest: async (params) => {
    const response = await apiClient.post('/qa-tests/throughput-test', params)
    return response.data
  },
  runEndpointPerformanceTest: async (params) => {
    const response = await apiClient.post('/qa-tests/endpoint-performance-test', params)
    return response.data
  },
  runApiLoadTest: async (params) => {
    const response = await apiClient.post('/qa-tests/api-load-test', params)
    return response.data
  },
  runWebsiteLoadTest: async (params) => {
    const response = await apiClient.post('/qa-tests/website-load-test', params)
    return response.data
  },
  runVolumeTest: async (params) => {
    const response = await apiClient.post('/qa-tests/volume-test', params)
    return response.data
  },
  runConcurrentUserTest: async (params) => {
    const response = await apiClient.post('/qa-tests/concurrent-user-test', params)
    return response.data
  },
  runResponseTimeDistributionTest: async (params) => {
    const response = await apiClient.post('/qa-tests/response-time-distribution-test', params)
    return response.data
  },
  
  // Network Tests
  runSslTlsValidation: async (params) => {
    const response = await apiClient.post('/qa-tests/ssl-tls-validation', params)
    return response.data
  },
  runDnsSecurityTest: async (params) => {
    const response = await apiClient.post('/qa-tests/dns-security-test', params)
    return response.data
  },
  runConnectivityDiagnostics: async (params) => {
    const response = await apiClient.post('/qa-tests/connectivity-diagnostics', params)
    return response.data
  },
  runProtocolTrafficAnalysis: async (params) => {
    const response = await apiClient.post('/qa-tests/protocol-traffic-analysis', params)
    return response.data
  },
  runNetworkSecurityScan: async (params) => {
    const response = await apiClient.post('/qa-tests/network-security-scan', params)
    return response.data
  },
  runEndpointDiscovery: async (params) => {
    const response = await apiClient.post('/qa-tests/endpoint-discovery', params)
    return response.data
  },
  
  // Test Status and Control
  getTestStatus: async (testId) => {
    const response = await apiClient.get(`/qa-tests/test-status/${testId}`)
    return response.data
  },
  cancelTest: async (testId) => {
    const response = await apiClient.post(`/qa-tests/cancel-test/${testId}`)
    return response.data
  },
  
  // Unified method to run any test by config
  runTest: async (testConfig, websiteUrl, customParams = {}) => {
    const params = {
      website_url: websiteUrl,
      test_name: testConfig.name,
      ...testConfig.defaultParams,
      ...customParams
    }
    
    // Map test ID to API method
    const methodMap = {
      'load_test': 'runLoadTest',
      'stress_test': 'runStressTest',
      'spike_test': 'runSpikeTest',
      'soak_test': 'runSoakTest',
      'ramp_up_test': 'runRampUpTest',
      'throughput_test': 'runThroughputTest',
      'endpoint_performance_test': 'runEndpointPerformanceTest',
      'api_load_test': 'runApiLoadTest',
      'website_load_test': 'runWebsiteLoadTest',
      'volume_test': 'runVolumeTest',
      'concurrent_user_test': 'runConcurrentUserTest',
      'response_time_distribution_test': 'runResponseTimeDistributionTest',
      'ssl_tls_validation': 'runSslTlsValidation',
      'dns_security_test': 'runDnsSecurityTest',
      'connectivity_diagnostics': 'runConnectivityDiagnostics',
      'protocol_traffic_analysis': 'runProtocolTrafficAnalysis',
      'network_security_scan': 'runNetworkSecurityScan',
      'endpoint_discovery': 'runEndpointDiscovery'
    }
    
    const method = methodMap[testConfig.id]
    if (!method) {
      throw new Error(`Unknown test type: ${testConfig.id}`)
    }
    
    return await performanceTestAPI[method](params)
  }
}

export default apiClient
