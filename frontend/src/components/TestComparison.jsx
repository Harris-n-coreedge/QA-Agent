import { useState, useMemo } from 'react'
import { GitCompare, TrendingUp, TrendingDown, Minus, X, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

export function TestComparison({ testResults = [] }) {
  const [selectedTests, setSelectedTests] = useState([])
  const [comparisonMode, setComparisonMode] = useState('side-by-side')
  const toast = useToast()

  const availableTests = useMemo(() => {
    return testResults
      .filter((test) => test.status && test.command)
      .sort((a, b) => new Date(b.started_at) - new Date(a.started_at))
  }, [testResults])

  const handleSelectTest = (testId) => {
    setSelectedTests((prev) => {
      if (prev.includes(testId)) {
        return prev.filter((id) => id !== testId)
      }
      if (prev.length >= 2) {
        toast.warning('You can compare up to 2 tests at a time')
        return prev
      }
      return [...prev, testId]
    })
  }

  const selectedTestData = useMemo(() => {
    return selectedTests.map((id) => availableTests.find((t) => t.id === id)).filter(Boolean)
  }, [selectedTests, availableTests])

  const comparisonData = useMemo(() => {
    if (selectedTestData.length !== 2) return null

    const [test1, test2] = selectedTestData

    const getMetric = (test, key) => {
      if (test.performance_metrics) {
        return test.performance_metrics[key]
      }
      if (test.performance) {
        return test.performance[key]
      }
      return null
    }

    return {
      loadTime: {
        test1: getMetric(test1, 'load_time'),
        test2: getMetric(test2, 'load_time'),
        diff: getMetric(test2, 'load_time') - getMetric(test1, 'load_time'),
      },
      firstContentfulPaint: {
        test1: getMetric(test1, 'first_contentful_paint'),
        test2: getMetric(test2, 'first_contentful_paint'),
        diff: getMetric(test2, 'first_contentful_paint') - getMetric(test1, 'first_contentful_paint'),
      },
      networkRequests: {
        test1: getMetric(test1, 'network_requests'),
        test2: getMetric(test2, 'network_requests'),
        diff: getMetric(test2, 'network_requests') - getMetric(test1, 'network_requests'),
      },
      status: {
        test1: test1.status,
        test2: test2.status,
      },
      timestamp: {
        test1: new Date(test1.started_at),
        test2: new Date(test2.started_at),
      },
    }
  }, [selectedTestData])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-emerald-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-rose-500" />
      default:
        return <AlertCircle className="w-5 h-5 text-amber-500" />
    }
  }

  const getDiffColor = (diff, isLowerBetter = true) => {
    if (diff === 0) return 'text-slate-500'
    const isImprovement = isLowerBetter ? diff < 0 : diff > 0
    return isImprovement ? 'text-emerald-500' : 'text-rose-500'
  }

  const getDiffIcon = (diff) => {
    if (diff === 0) return <Minus className="w-4 h-4" />
    return diff > 0 ? (
      <TrendingUp className="w-4 h-4" />
    ) : (
      <TrendingDown className="w-4 h-4" />
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Test Comparison</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Compare two test results side-by-side
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="input text-sm"
            value={comparisonMode}
            onChange={(e) => setComparisonMode(e.target.value)}
          >
            <option value="side-by-side">Side by Side</option>
            <option value="differences">Show Differences</option>
          </select>
        </div>
      </div>

      {/* Test Selection */}
      <div className="card p-6">
        <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
          Select Tests to Compare (2 required)
        </h4>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {availableTests.length === 0 ? (
            <p className="text-sm text-slate-500 dark:text-slate-400 text-center py-4">
              No test results available for comparison
            </p>
          ) : (
            availableTests.map((test) => {
              const isSelected = selectedTests.includes(test.id)
              return (
                <button
                  key={test.id}
                  onClick={() => handleSelectTest(test.id)}
                  className={`
                    w-full text-left p-4 rounded-lg border-2 transition-all
                    ${
                      isSelected
                        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-500/20'
                        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
                    }
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      {getStatusIcon(test.status)}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-slate-900 dark:text-white truncate">
                          {test.command || 'Unknown Test'}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {new Date(test.started_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div
                      className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                        isSelected
                          ? 'border-indigo-500 bg-indigo-500'
                          : 'border-slate-300 dark:border-slate-600'
                      }`}
                    >
                      {isSelected && <CheckCircle2 className="w-3 h-3 text-white" />}
                    </div>
                  </div>
                </button>
              )
            })
          )}
        </div>
      </div>

      {/* Comparison Results */}
      {comparisonData && selectedTestData.length === 2 && (
        <div className="space-y-4">
          {comparisonMode === 'side-by-side' ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {selectedTestData.map((test, index) => (
                <div key={test.id} className="card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold text-slate-900 dark:text-white">
                      Test {index + 1}
                    </h4>
                    {getStatusIcon(test.status)}
                  </div>
                  <div className="space-y-3 text-sm">
                    <div>
                      <p className="text-slate-500 dark:text-slate-400 mb-1">Command</p>
                      <p className="text-slate-900 dark:text-white font-medium">
                        {test.command || 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-500 dark:text-slate-400 mb-1">Status</p>
                      <p className="text-slate-900 dark:text-white font-medium capitalize">
                        {test.status || 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-slate-500 dark:text-slate-400 mb-1">Timestamp</p>
                      <p className="text-slate-900 dark:text-white font-medium">
                        {new Date(test.started_at).toLocaleString()}
                      </p>
                    </div>
                    {test.performance_metrics && (
                      <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
                        <p className="text-slate-500 dark:text-slate-400 mb-2">Performance</p>
                        {test.performance_metrics.load_time && (
                          <div className="flex justify-between mb-1">
                            <span className="text-slate-600 dark:text-slate-400">Load Time:</span>
                            <span className="text-slate-900 dark:text-white font-mono">
                              {test.performance_metrics.load_time}ms
                            </span>
                          </div>
                        )}
                        {test.performance_metrics.first_contentful_paint && (
                          <div className="flex justify-between mb-1">
                            <span className="text-slate-600 dark:text-slate-400">FCP:</span>
                            <span className="text-slate-900 dark:text-white font-mono">
                              {test.performance_metrics.first_contentful_paint}ms
                            </span>
                          </div>
                        )}
                        {test.performance_metrics.network_requests && (
                          <div className="flex justify-between">
                            <span className="text-slate-600 dark:text-slate-400">Requests:</span>
                            <span className="text-slate-900 dark:text-white font-mono">
                              {test.performance_metrics.network_requests}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card p-6">
              <h4 className="font-semibold text-slate-900 dark:text-white mb-4">
                Differences
              </h4>
              <div className="space-y-4">
                {comparisonData.loadTime.test1 !== null && comparisonData.loadTime.test2 !== null && (
                  <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-slate-900 dark:text-white">Load Time</span>
                      <span
                        className={`flex items-center gap-1 font-mono ${getDiffColor(
                          comparisonData.loadTime.diff,
                          true
                        )}`}
                      >
                        {getDiffIcon(comparisonData.loadTime.diff)}
                        {comparisonData.loadTime.diff > 0 ? '+' : ''}
                        {comparisonData.loadTime.diff.toFixed(0)}ms
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-slate-500 dark:text-slate-400">Test 1:</span>
                        <span className="ml-2 font-mono text-slate-900 dark:text-white">
                          {comparisonData.loadTime.test1}ms
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500 dark:text-slate-400">Test 2:</span>
                        <span className="ml-2 font-mono text-slate-900 dark:text-white">
                          {comparisonData.loadTime.test2}ms
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {comparisonData.status.test1 !== comparisonData.status.test2 && (
                  <div className="p-4 rounded-lg bg-amber-50 dark:bg-amber-500/10">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertCircle className="w-5 h-5 text-amber-500" />
                      <span className="font-medium text-slate-900 dark:text-white">Status Changed</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-slate-500 dark:text-slate-400">Test 1:</span>
                        <span className="ml-2 capitalize text-slate-900 dark:text-white">
                          {comparisonData.status.test1}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500 dark:text-slate-400">Test 2:</span>
                        <span className="ml-2 capitalize text-slate-900 dark:text-white">
                          {comparisonData.status.test2}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {selectedTests.length === 1 && (
        <div className="card p-6 text-center">
          <p className="text-slate-600 dark:text-slate-400">
            Select one more test to compare
          </p>
        </div>
      )}
    </div>
  )
}




