import { useQuery } from '@tanstack/react-query'
import { Activity, TestTube, CheckCircle, XCircle, Clock, TrendingUp, Zap } from 'lucide-react'
import { agentAPI, testResultsAPI, healthAPI } from '../api/client'
import { SimpleBarChart, SimpleLineChart, SimplePieChart } from '../components/SimpleChart'
import { ActivityFeed } from '../components/ActivityFeed'
import { AdvancedAnalytics } from '../components/AdvancedAnalytics'

function StatCard({ title, value, icon: Icon, trend, color = 'primary', delay = 0 }) {
  const colorConfig = {
    primary: {
      iconBg: 'bg-purple-500/20',
      iconColor: 'text-purple-400',
      border: 'border-purple-500/30',
    },
    success: {
      iconBg: 'bg-emerald-500/20',
      iconColor: 'text-emerald-400',
      border: 'border-emerald-500/30',
    },
    warning: {
      iconBg: 'bg-amber-500/20',
      iconColor: 'text-amber-400',
      border: 'border-amber-500/30',
    },
    error: {
      iconBg: 'bg-red-500/20',
      iconColor: 'text-red-400',
      border: 'border-red-500/30',
    }
  }

  const config = colorConfig[color]

  return (
    <div
      className={`card-stat hover-lift ${config.border} animate-slide-in-up`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`p-2.5 rounded-lg ${config.iconBg} border ${config.border}`}>
          <Icon className={`w-5 h-5 ${config.iconColor}`} />
        </div>
        {trend && (
          <div className="flex items-center gap-1 text-xs text-emerald-400">
            <TrendingUp className="w-3 h-3" />
            <span>{trend}</span>
          </div>
        )}
      </div>
      <div>
        <p className="text-xs font-medium text-gray-400 mb-1.5 uppercase tracking-wide">{title}</p>
        <p className="text-2xl md:text-3xl font-bold text-white">{value}</p>
      </div>
    </div>
  )
}

function RecentTest({ test, delay = 0 }) {
  const statusConfig = {
    passed: { class: 'badge-success', dot: 'success', icon: CheckCircle, iconColor: 'text-emerald-400' },
    completed: { class: 'badge-warning', dot: 'warning', icon: Clock, iconColor: 'text-amber-400' },
    running: { class: 'badge-info', dot: 'info', icon: Activity, iconColor: 'text-blue-400' },
    failed: { class: 'badge-error', dot: 'error', icon: XCircle, iconColor: 'text-rose-400' },
    pending: { class: 'badge-neutral', dot: 'warning', icon: Clock, iconColor: 'text-slate-400' },
  }

  const config = statusConfig[test.status] || statusConfig.pending
  const Icon = config.icon

  return (
    <div
      className="card hover-lift cursor-pointer group p-4 animate-slide-in-right transition-all duration-300 hover:scale-[1.02]"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg bg-[#1a1a1a] border border-gray-800 flex-shrink-0`}>
          <Icon className={`w-4 h-4 ${config.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`status-dot ${config.dot}`} />
            <span className={`badge ${config.class}`}>{test.status}</span>
          </div>
          <p className="text-sm font-semibold text-white truncate mb-1.5 group-hover:text-gray-300 transition-colors">
            {test.command}
          </p>
          <div className="flex items-center gap-3 md:gap-4 text-xs text-gray-400 flex-wrap">
            <span>{new Date(test.started_at).toLocaleString()}</span>
            {test.duration_ms && (
              <span className="font-mono px-2 py-0.5 rounded bg-[#1a1a1a] border border-gray-800">
                {test.duration_ms.toFixed(0)}ms
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function Dashboard() {
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: healthAPI.check,
    refetchInterval: 5000,
  })

  const { data: agentStatus } = useQuery({
    queryKey: ['agent-status'],
    queryFn: agentAPI.getStatus,
    refetchInterval: 3000,
  })

  const { data: testResults, isLoading: resultsLoading } = useQuery({
    queryKey: ['test-results'],
    queryFn: () => testResultsAPI.list(1000),
    refetchInterval: 3000,
  })

  const totalTests = testResults?.total || 0
  const passedTests = testResults?.results?.filter(r => r.status === 'passed').length || 0
  const completedTests = testResults?.results?.filter(r => r.status === 'completed' || r.status === 'passed' || r.status === 'failed').length || 0
  const failedTests = testResults?.results?.filter(r => r.status === 'failed').length || 0
  
  const recentTests = testResults?.results?.slice(0, 5) || []

  // Chart data
  const statusChartData = [
    { label: 'Passed', value: passedTests, color: '#10b981' },
    { label: 'Failed', value: failedTests, color: '#ef4444' },
    { label: 'Running', value: testResults?.results?.filter(r => r.status === 'running').length || 0, color: '#3b82f6' },
    { label: 'Pending', value: testResults?.results?.filter(r => r.status === 'pending').length || 0, color: '#f59e0b' },
  ].filter(item => item.value > 0)

  // Time series data (last 7 days simulation)
  const timeSeriesData = Array.from({ length: 7 }, (_, i) => ({
    label: `Day ${i + 1}`,
    value: Math.floor(Math.random() * 20) + 5
  }))

  // Trend data
  const trendData = [
    { label: 'Mon', value: 12 },
    { label: 'Tue', value: 19 },
    { label: 'Wed', value: 15 },
    { label: 'Thu', value: 22 },
    { label: 'Fri', value: 18 },
    { label: 'Sat', value: 25 },
    { label: 'Sun', value: 20 },
  ]

  return (
    <div className="space-y-6 fade-in">
      {/* Page Header */}
      <div className="page-header">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="page-title">Dashboard</h1>
            <p className="page-description">
              Real-time monitoring and analytics for your QA automation
            </p>
          </div>
          {agentStatus && (
            <div className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-[#1a1a1a] border border-gray-800">
              <div className="status-dot success" />
              <div>
                <p className="text-xs text-gray-400">Agent Status</p>
                <p className="text-sm font-semibold text-white">{agentStatus.status}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
        <StatCard
          title="Total Tests"
          value={totalTests}
          icon={TestTube}
          color="primary"
          delay={0}
        />
        <StatCard
          title="Passed"
          value={passedTests}
          icon={CheckCircle}
          color="success"
          trend={passedTests > 0 ? "+12%" : null}
          delay={100}
        />
        <StatCard
          title="Completed"
          value={completedTests}
          icon={Clock}
          color="warning"
          delay={200}
        />
        <StatCard
          title="Failed"
          value={failedTests}
          icon={XCircle}
          color="error"
          delay={300}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        <div className="glass-card p-5 md:p-6 animate-fade-in" style={{ animationDelay: '400ms' }}>
          <div className="mb-5 md:mb-6">
            <h2 className="text-base md:text-lg font-semibold text-white mb-1">Test Status Distribution</h2>
            <p className="text-xs md:text-sm text-gray-400">Overview of test results</p>
          </div>
          <div className="chart-container">
            {statusChartData.length > 0 ? (
              <SimplePieChart 
                data={statusChartData}
                size={250}
              />
            ) : (
              <div className="empty-state">
                <Activity className="empty-state-icon" />
                <p className="empty-state-title">No data yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Trend Chart */}
        <div className="glass-card p-5 md:p-6 animate-fade-in" style={{ animationDelay: '500ms' }}>
          <div className="mb-5 md:mb-6">
            <h2 className="text-base md:text-lg font-semibold text-white mb-1">Weekly Trend</h2>
            <p className="text-xs md:text-sm text-gray-400">Test execution over time</p>
          </div>
          <div className="chart-container h-48 md:h-64">
            <SimpleLineChart data={trendData} color="#8b5cf6" />
          </div>
        </div>
      </div>

      {/* Recent Tests & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-5 md:p-6 animate-fade-in" style={{ animationDelay: '600ms' }}>
          <div className="flex items-center justify-between mb-5 md:mb-6">
            <div>
              <h2 className="text-base md:text-lg font-semibold text-white mb-1">Recent Tests</h2>
              <p className="text-xs md:text-sm text-gray-400">Latest test executions</p>
            </div>
            <Zap className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
          </div>
          
          <div className="space-y-3">
            {resultsLoading ? (
              <>
                <div className="skeleton h-20" />
                <div className="skeleton h-20" />
                <div className="skeleton h-20" />
              </>
            ) : recentTests.length > 0 ? (
              recentTests.map((test, idx) => (
                <RecentTest key={test.test_id} test={test} delay={idx * 50} />
              ))
            ) : (
              <div className="empty-state py-12">
                <Activity className="empty-state-icon" />
                <p className="empty-state-title">No test results yet</p>
                <p className="empty-state-description">
                  Run your first test to see results here
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Advanced Analytics */}
        <div className="glass-card p-5 md:p-6 animate-fade-in" style={{ animationDelay: '700ms' }}>
          <AdvancedAnalytics testResults={testResults?.results || []} />
        </div>

        {/* System Health */}
        <div className="glass-card p-5 md:p-6 animate-fade-in" style={{ animationDelay: '800ms' }}>
          <div className="mb-5 md:mb-6">
            <h2 className="text-base md:text-lg font-semibold text-white mb-1">System Health</h2>
            <p className="text-xs md:text-sm text-gray-400">Current system status</p>
          </div>
          
          {health ? (
            <div className="space-y-3">
              <div className="p-3.5 md:p-4 rounded-lg bg-[#1a1a1a] border border-gray-800">
                <p className="text-xs text-gray-400 mb-1.5">Status</p>
                <div className="flex items-center gap-2">
                  <div className="status-dot success" />
                  <p className="text-base md:text-lg font-semibold text-white">{health.status}</p>
                </div>
              </div>
              <div className="p-3.5 md:p-4 rounded-lg bg-[#1a1a1a] border border-gray-800">
                <p className="text-xs text-gray-400 mb-1.5">Total Results</p>
                <p className="text-base md:text-lg font-semibold text-white">{health.total_test_results}</p>
              </div>
              <div className="p-3.5 md:p-4 rounded-lg bg-[#1a1a1a] border border-gray-800">
                <p className="text-xs text-gray-400 mb-1.5">Last Check</p>
                <p className="text-xs md:text-sm font-mono text-white">{new Date(health.timestamp).toLocaleTimeString()}</p>
              </div>
            </div>
          ) : (
            <div className="skeleton h-32" />
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
