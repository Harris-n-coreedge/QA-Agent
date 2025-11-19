/**
 * Test Configuration for all 27 Performance Tests
 * Defines test metadata, descriptions, default parameters, and icons
 * Note: Icons are imported dynamically in components to avoid bundle size issues
 */

export const TEST_CONFIGS = [
  // Load Tests (12 tests)
  {
    id: 'load_test',
    name: 'Load Test',
    category: 'load',
    description: 'Simulate concurrent users to test website performance under normal load conditions. Measures response times, throughput, and success rates.',
    icon: 'Activity',
    defaultParams: { users: 50, duration: 60, ramp_up: 10 },
    endpoint: '/api/v1/qa-tests/load-test',
    testType: 'load_test'
  },
  {
    id: 'stress_test',
    name: 'Stress Test',
    category: 'load',
    description: 'Push system beyond normal capacity to identify breaking points and maximum concurrent user limits.',
    icon: 'AlertTriangle',
    defaultParams: { max_users: 500, step_users: 50, duration: 300 },
    endpoint: '/api/v1/qa-tests/stress-test',
    testType: 'stress_test'
  },
  {
    id: 'spike_test',
    name: 'Spike Test',
    category: 'load',
    description: 'Test system resilience to sudden traffic spikes by instantly increasing load from baseline to peak.',
    icon: 'Zap',
    defaultParams: { initial_users: 10, spike_users: 200, duration: 120 },
    endpoint: '/api/v1/qa-tests/spike-test',
    testType: 'spike_test'
  },
  {
    id: 'soak_test',
    name: 'Soak Test',
    category: 'load',
    description: 'Run sustained load over extended period to detect memory leaks, resource exhaustion, and performance degradation.',
    icon: 'Clock',
    defaultParams: { users: 50, duration_hours: 1 },
    endpoint: '/api/v1/qa-tests/soak-test',
    testType: 'soak_test'
  },
  {
    id: 'ramp_up_test',
    name: 'Ramp-Up Test',
    category: 'load',
    description: 'Gradually increase load from zero to maximum users to test how system handles progressive scaling.',
    icon: 'TrendingUp',
    defaultParams: { max_users: 100, ramp_up_time: 60, duration: 120 },
    endpoint: '/api/v1/qa-tests/ramp-up-test',
    testType: 'ramp_up_test'
  },
  {
    id: 'throughput_test',
    name: 'Throughput Test',
    category: 'load',
    description: 'Measure maximum requests per second (RPS) your system can handle under sustained load.',
    icon: 'Gauge',
    defaultParams: { target_rps: 100, duration: 60 },
    endpoint: '/api/v1/qa-tests/throughput-test',
    testType: 'throughput_test'
  },
  {
    id: 'endpoint_performance_test',
    name: 'Endpoint Performance',
    category: 'load',
    description: 'Test performance of specific API endpoints under load to identify slow endpoints.',
    icon: 'Target',
    defaultParams: { endpoint: '/api/endpoint', users: 50, duration: 60 },
    endpoint: '/api/v1/qa-tests/endpoint-performance-test',
    testType: 'endpoint_performance_test'
  },
  {
    id: 'api_load_test',
    name: 'API Load Test',
    category: 'load',
    description: 'Load test your API endpoints to measure response times, error rates, and throughput under concurrent requests.',
    icon: 'Code',
    defaultParams: { users: 50, duration: 60 },
    endpoint: '/api/v1/qa-tests/api-load-test',
    testType: 'api_load_test'
  },
  {
    id: 'website_load_test',
    name: 'Website Load Test',
    category: 'load',
    description: 'Test website performance under load, measuring page load times and user experience metrics.',
    icon: 'Globe',
    defaultParams: { users: 50, duration: 60 },
    endpoint: '/api/v1/qa-tests/website-load-test',
    testType: 'website_load_test'
  },
  {
    id: 'volume_test',
    name: 'Volume Test',
    category: 'load',
    description: 'Test system with large amounts of data to measure performance under high data volume conditions.',
    icon: 'Database',
    defaultParams: { users: 100, duration: 300 },
    endpoint: '/api/v1/qa-tests/volume-test',
    testType: 'volume_test'
  },
  {
    id: 'concurrent_user_test',
    name: 'Concurrent User Test',
    category: 'load',
    description: 'Test system behavior when multiple users perform the same action simultaneously to detect race conditions.',
    icon: 'Layers',
    defaultParams: { concurrent_users: 100, duration: 60 },
    endpoint: '/api/v1/qa-tests/concurrent-user-test',
    testType: 'concurrent_user_test'
  },
  {
    id: 'response_time_distribution_test',
    name: 'Response Time Distribution',
    category: 'load',
    description: 'Measure response time percentiles (p50, p95, p99) to understand response time distribution patterns.',
    icon: 'BarChart3',
    defaultParams: { users: 50, duration: 60 },
    endpoint: '/api/v1/qa-tests/response-time-distribution-test',
    testType: 'response_time_distribution_test'
  },
  
  // Network Analysis Tests (6 tests)
  {
    id: 'ssl_tls_validation',
    name: 'SSL/TLS Certificate Validation',
    category: 'network',
    description: 'Validate SSL/TLS certificates, cipher suites, and protocol versions. Check certificate expiration and security configuration.',
    icon: 'Shield',
    defaultParams: {},
    endpoint: '/api/v1/qa-tests/ssl-tls-validation',
    testType: 'ssl_tls_validation',
    requiresPermission: false
  },
  {
    id: 'dns_security_test',
    name: 'DNS Security Test',
    category: 'network',
    description: 'Test DNS resolution performance, DNSSEC validation, and detect DNS leaks. Analyze DNS server configuration and privacy.',
    icon: 'Network',
    defaultParams: {},
    endpoint: '/api/v1/qa-tests/dns-security-test',
    testType: 'dns_security_test',
    requiresPermission: false
  },
  {
    id: 'connectivity_diagnostics',
    name: 'Network Connectivity Diagnostics',
    category: 'network',
    description: 'Diagnose network connectivity issues including DNS resolution, routing, firewall, and connection tests.',
    icon: 'Activity',
    defaultParams: {},
    endpoint: '/api/v1/qa-tests/connectivity-diagnostics',
    testType: 'connectivity_diagnostics',
    requiresPermission: false
  },
  {
    id: 'protocol_traffic_analysis',
    name: 'Protocol Traffic Analysis',
    category: 'network',
    description: 'Analyze network traffic at packet level (passive). Identify protocols, packet sizes, and traffic patterns.',
    icon: 'BarChart3',
    defaultParams: { duration: 10 },
    endpoint: '/api/v1/qa-tests/protocol-traffic-analysis',
    testType: 'protocol_traffic_analysis',
    requiresPermission: false
  },
  {
    id: 'network_security_scan',
    name: 'Network Security Scan',
    category: 'network',
    description: 'Perform port scanning, service detection, and vulnerability assessment. Identifies open ports and exposed services.',
    icon: 'Search',
    defaultParams: { ports: null, scan_type: 'stealth' },
    endpoint: '/api/v1/qa-tests/network-security-scan',
    testType: 'network_security_scan',
    requiresPermission: true
  },
  {
    id: 'endpoint_discovery',
    name: 'Endpoint Discovery',
    category: 'network',
    description: 'Auto-discover API endpoints and services. Identifies available endpoints, HTTP methods, and response codes.',
    icon: 'Target',
    defaultParams: { discovery_method: 'passive' },
    endpoint: '/api/v1/qa-tests/endpoint-discovery',
    testType: 'endpoint_discovery',
    requiresPermission: true
  }
]

// Group tests by category
export const TESTS_BY_CATEGORY = {
  load: TEST_CONFIGS.filter(t => t.category === 'load'),
  network: TEST_CONFIGS.filter(t => t.category === 'network')
}

// Get test config by ID
export const getTestConfig = (testId) => {
  return TEST_CONFIGS.find(t => t.id === testId)
}

// Get test config by endpoint
export const getTestConfigByEndpoint = (endpoint) => {
  return TEST_CONFIGS.find(t => t.endpoint === endpoint)
}

