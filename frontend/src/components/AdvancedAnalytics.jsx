import { useMemo } from 'react'
import { TrendingUp, TrendingDown, BarChart3, PieChart, Activity, Clock, Zap, Target } from 'lucide-react'
import { SimpleBarChart, SimpleLineChart, SimplePieChart } from './SimpleChart'

export function AdvancedAnalytics({ testResults = [] }) {
  const analytics = useMemo(() => {
    if (!testResults || testResults.length === 0) {
      return null
    }

    // Calculate metrics
    const total = testResults.length
    const passed = testResults.filter((r) => r.status === 'passed' || r.status === 'completed').length
    const failed = testResults.filter((r) => r.status === 'failed').length
    const successRate = total > 0 ? ((passed / total) * 100).toFixed(1) : 0

    // Average duration
    const durations = testResults
      .filter((r) => r.duration_ms)
      .map((r) => r.duration_ms)
    const avgDuration = durations.length > 0
      ? durations.reduce((a, b) => a + b, 0) / durations.length
      : 0

    // Performance trends (last 7 days)
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - i)
      return date.toISOString().split('T')[0]
    }).reverse()

    const dailyStats = last7Days.map((date) => {
      const dayTests = testResults.filter((r) => {
        const testDate = new Date(r.started_at).toISOString().split('T')[0]
        return testDate === date
      })
      return {
        date,
        total: dayTests.length,
        passed: dayTests.filter((r) => r.status === 'passed' || r.status === 'completed').length,
        failed: dayTests.filter((r) => r.status === 'failed').length,
      }
    })

    // Test type distribution
    const testTypes = {}
    testResults.forEach((r) => {
      const cmd = (r.command || '').toLowerCase()
      let type = 'Other'
      if (cmd.includes('auto check')) type = 'Auto Check'
      else if (cmd.includes('auto audit')) type = 'Auto Audit'
      else if (cmd.includes('cross-browser')) type = 'Cross-Browser'
      else if (cmd.includes('mobile')) type = 'Mobile'
      else if (cmd.includes('browser')) type = 'Browser Use'
      
      testTypes[type] = (testTypes[type] || 0) + 1
    })

    // Hourly distribution
    const hourlyStats = Array.from({ length: 24 }, (_, hour) => {
      const hourTests = testResults.filter((r) => {
        const testHour = new Date(r.started_at).getHours()
        return testHour === hour
      })
      return hourTests.length
    })

    // Performance metrics
    const performanceData = testResults
      .filter((r) => r.performance_metrics || r.performance)
      .map((r) => {
        const perf = r.performance_metrics || r.performance || {}
        return {
          loadTime: perf.load_time || 0,
          fcp: perf.first_contentful_paint || 0,
          requests: perf.network_requests || 0,
        }
      })

    const avgLoadTime = performanceData.length > 0
      ? performanceData.reduce((sum, p) => sum + p.loadTime, 0) / performanceData.length
      : 0

    return {
      total,
      passed,
      failed,
      successRate: parseFloat(successRate),
      avgDuration,
      dailyStats,
      testTypes,
      hourlyStats,
      avgLoadTime,
      performanceData,
    }
  }, [testResults])

  if (!analytics) {
    return (
      <div className="card p-12 text-center">
        <BarChart3 className="w-12 h-12 text-slate-400 mx-auto mb-4" />
        <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          No Analytics Data
        </h4>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Run some tests to see analytics here
        </p>
      </div>
    )
  }

  const testTypeChartData = Object.entries(analytics.testTypes).map(([name, value]) => ({
    label: name,
    value,
  }))

  const trendData = analytics.dailyStats.map((stat) => ({
    date: new Date(stat.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    value: stat.total,
    passed: stat.passed,
    failed: stat.failed,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">Advanced Analytics</h3>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Deep insights into your test performance
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card-stat">
          <div className="flex items-center justify-between mb-2">
            <Target className="w-5 h-5 text-indigo-500" />
            <span className="text-xs text-slate-500 dark:text-slate-400">Success Rate</span>
          </div>
          <div className="flex items-baseline gap-2">
            <p className="text-2xl font-bold text-slate-900 dark:text-white">
              {analytics.successRate}%
            </p>
            {analytics.successRate >= 80 ? (
              <TrendingUp className="w-4 h-4 text-emerald-500" />
            ) : (
              <TrendingDown className="w-4 h-4 text-rose-500" />
            )}
          </div>
        </div>

        <div className="card-stat">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-5 h-5 text-blue-500" />
            <span className="text-xs text-slate-500 dark:text-slate-400">Avg Duration</span>
          </div>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">
            {analytics.avgDuration > 0 ? `${(analytics.avgDuration / 1000).toFixed(1)}s` : 'N/A'}
          </p>
        </div>

        <div className="card-stat">
          <div className="flex items-center justify-between mb-2">
            <Zap className="w-5 h-5 text-amber-500" />
            <span className="text-xs text-slate-500 dark:text-slate-400">Avg Load Time</span>
          </div>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">
            {analytics.avgLoadTime > 0 ? `${analytics.avgLoadTime.toFixed(0)}ms` : 'N/A'}
          </p>
        </div>

        <div className="card-stat">
          <div className="flex items-center justify-between mb-2">
            <Activity className="w-5 h-5 text-purple-500" />
            <span className="text-xs text-slate-500 dark:text-slate-400">Total Tests</span>
          </div>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">
            {analytics.total}
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Type Distribution */}
        <div className="card p-6">
          <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
            Test Type Distribution
          </h4>
          <div className="chart-container h-64">
            {testTypeChartData.length > 0 ? (
              <SimplePieChart data={testTypeChartData} />
            ) : (
              <p className="text-sm text-slate-500 text-center py-12">No data available</p>
            )}
          </div>
        </div>

        {/* Daily Trends */}
        <div className="card p-6">
          <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
            7-Day Test Trends
          </h4>
          <div className="chart-container h-64">
            <SimpleLineChart data={trendData.map((d) => ({ label: d.date, value: d.value }))} />
          </div>
        </div>

        {/* Success/Failure Trends */}
        <div className="card p-6">
          <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
            Success vs Failure Trend
          </h4>
          <div className="chart-container h-64">
            <SimpleBarChart
              data={trendData.map((d) => ({
                label: d.date,
                value: d.passed,
                value2: d.failed,
              }))}
            />
          </div>
        </div>

        {/* Hourly Distribution */}
        <div className="card p-6">
          <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
            Test Execution by Hour
          </h4>
          <div className="chart-container h-64">
            <SimpleBarChart
              data={analytics.hourlyStats.map((count, hour) => ({
                label: `${hour}:00`,
                value: count,
              }))}
            />
          </div>
        </div>
      </div>
    </div>
  )
}




