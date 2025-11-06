import { useState, useMemo } from 'react'
import { History, GitBranch, Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react'

export function TestHistory({ testResults = [], testId }) {
  const [selectedVersion, setSelectedVersion] = useState(null)

  // Filter results for the same test (by command or URL)
  const testHistory = useMemo(() => {
    if (!testId && testResults.length === 0) return []

    const filtered = testId
      ? testResults.filter((r) => r.test_id === testId || r.id === testId)
      : testResults

    // Group by similar tests (same command or URL pattern)
    const grouped = {}
    filtered.forEach((result) => {
      const key = result.command || result.website_url || 'unknown'
      if (!grouped[key]) {
        grouped[key] = []
      }
      grouped[key].push(result)
    })

    // Sort each group by date
    Object.keys(grouped).forEach((key) => {
      grouped[key].sort(
        (a, b) =>
          new Date(b.started_at || b.created_at) -
          new Date(a.started_at || a.created_at)
      )
    })

    return grouped
  }, [testResults, testId])

  const getStatusTrend = (current, previous) => {
    if (!previous) return null
    
    const statusOrder = { passed: 3, completed: 2, failed: 1, running: 0, pending: 0 }
    const currentOrder = statusOrder[current] || 0
    const previousOrder = statusOrder[previous] || 0
    
    if (currentOrder > previousOrder) return { icon: TrendingUp, color: 'text-emerald-500' }
    if (currentOrder < previousOrder) return { icon: TrendingDown, color: 'text-rose-500' }
    return { icon: Minus, color: 'text-slate-400' }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <History className="w-5 h-5" />
          Test History
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          View version history and changes over time
        </p>
      </div>

      {Object.keys(testHistory).length === 0 ? (
        <div className="card p-12 text-center">
          <History className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No History Available
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Test history will appear here as you run more tests
          </p>
        </div>
      ) : (
        Object.entries(testHistory).map(([key, versions]) => (
          <div key={key} className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <GitBranch className="w-4 h-4 text-slate-500" />
              <h4 className="font-semibold text-slate-900 dark:text-white">
                {key}
              </h4>
              <span className="text-xs text-slate-500 dark:text-slate-400">
                ({versions.length} versions)
              </span>
            </div>

            <div className="space-y-3">
              {versions.map((version, index) => {
                const previousVersion = versions[index + 1]
                const trend = getStatusTrend(version.status, previousVersion?.status)
                const TrendIcon = trend?.icon

                return (
                  <div
                    key={version.test_id || version.id || index}
                    className={`card p-4 hover-lift ${
                      selectedVersion === version.test_id || selectedVersion === version.id
                        ? 'ring-2 ring-indigo-500'
                        : ''
                    }`}
                    onClick={() =>
                      setSelectedVersion(
                        selectedVersion === (version.test_id || version.id)
                          ? null
                          : version.test_id || version.id
                      )
                    }
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="flex-shrink-0 mt-1">
                          <Clock className="w-4 h-4 text-slate-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <span
                              className={`badge ${
                                version.status === 'passed'
                                  ? 'badge-success'
                                  : version.status === 'failed'
                                  ? 'badge-error'
                                  : version.status === 'completed'
                                  ? 'badge-warning'
                                  : 'badge-info'
                              }`}
                            >
                              {version.status?.toUpperCase() || 'UNKNOWN'}
                            </span>
                            {trend && TrendIcon && (
                              <TrendIcon className={`w-4 h-4 ${trend.color}`} />
                            )}
                          </div>
                          <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                            {new Date(
                              version.started_at || version.created_at
                            ).toLocaleString()}
                          </p>
                          {version.duration_ms && (
                            <p className="text-xs text-slate-500 dark:text-slate-500 font-mono">
                              Duration: {version.duration_ms.toFixed(0)}ms
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex-shrink-0 text-xs text-slate-500 dark:text-slate-400">
                        v{versions.length - index}
                      </div>
                    </div>

                    {selectedVersion === (version.test_id || version.id) && (
                      <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                        <div className="space-y-2 text-sm">
                          {version.performance_metrics && (
                            <div>
                              <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
                                Performance
                              </p>
                              <div className="grid grid-cols-3 gap-2">
                                {version.performance_metrics.load_time && (
                                  <div>
                                    <span className="text-slate-500 dark:text-slate-400">
                                      Load:
                                    </span>
                                    <span className="ml-1 font-mono text-slate-900 dark:text-white">
                                      {version.performance_metrics.load_time}ms
                                    </span>
                                  </div>
                                )}
                                {version.performance_metrics.first_contentful_paint && (
                                  <div>
                                    <span className="text-slate-500 dark:text-slate-400">
                                      FCP:
                                    </span>
                                    <span className="ml-1 font-mono text-slate-900 dark:text-white">
                                      {version.performance_metrics.first_contentful_paint}ms
                                    </span>
                                  </div>
                                )}
                                {version.performance_metrics.network_requests && (
                                  <div>
                                    <span className="text-slate-500 dark:text-slate-400">
                                      Requests:
                                    </span>
                                    <span className="ml-1 font-mono text-slate-900 dark:text-white">
                                      {version.performance_metrics.network_requests}
                                    </span>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                          {previousVersion && (
                            <div>
                              <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
                                Previous: {previousVersion.status?.toUpperCase()}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        ))
      )}
    </div>
  )
}




