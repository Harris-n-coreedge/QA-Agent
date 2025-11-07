import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart3, Loader, CheckCircle, XCircle, Clock, Filter, Download, Search, X, FileDown, GitCompare, History, FileText } from 'lucide-react'
import { testResultsAPI } from '../api/client'
import { usePDFExporter } from '../components/PDFExporter'
import { TestComparison } from '../components/TestComparison'
import { TestHistory } from '../components/TestHistory'
import { ScreenshotGallery } from '../components/ScreenshotGallery'
import { TestTags, TagFilter } from '../components/TestTags'

const normalizeResultText = (value) => {
  if (value == null) return ''
  if (typeof value === 'string') return value
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value)
    } catch {
      return String(value)
    }
  }
  return String(value)
}

function TestResultCard({ result }) {
  const [lightbox, setLightbox] = useState({ open: false, src: '' })
  const { exportTestResult } = usePDFExporter()
  
  const statusIcons = {
    passed: <CheckCircle className="w-5 h-5 text-green-500" />,
    completed: <Clock className="w-5 h-5 text-yellow-500" />,
    failed: <XCircle className="w-5 h-5 text-red-500" />,
    running: <Loader className="w-5 h-5 text-blue-500 animate-spin" />,
    pending: <Clock className="w-5 h-5 text-yellow-500" />,
  }

  const statusColors = {
    passed: 'badge-success',
    completed: 'badge-warning',
    failed: 'badge-error',
    running: 'badge-info',
    pending: 'badge-warning',
  }

  const screenshots = result.screenshots || []
  const device = result.device

  return (
    <div className="card fade-in hover-lift hover-glow">
      <div className="flex items-start space-x-6">
        <div className="mt-2">{statusIcons[result.status]}</div>
        <div className="flex-1">
          <div className="flex items-start justify-between mb-6 gap-6">
            <h3 className="text-3xl font-bold text-gradient text-glow flex-1">
              {result.command}
            </h3>
            <span className={`badge ${statusColors[result.status]} hover:scale-105 transition-transform duration-500 px-4 py-2 text-sm font-semibold tracking-wide uppercase whitespace-nowrap flex-shrink-0`}>
              {result.status === 'passed' ? 'PASSED' : 
               result.status === 'completed' ? 'COMPLETED' :
               result.status === 'failed' ? 'FAILED' :
               result.status === 'running' ? 'RUNNING' :
               result.status === 'pending' ? 'PENDING' :
               result.status?.toUpperCase() || 'UNKNOWN'}
            </span>
          </div>

          {device && (
            <div className="bg-gradient-to-br from-purple-500/15 to-pink-500/10 p-6 rounded-2xl mb-6 border border-purple-500/30 shadow-xl">
              <p className="text-purple-300 text-sm mb-2 font-bold tracking-wide uppercase">Device</p>
              <p className="text-purple-200 font-bold text-lg">{device.name} ({device.width}×{device.height}) @ {device.deviceScaleFactor}x</p>
            </div>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm mb-8">
            <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
              <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">Started</p>
              <p className="text-white font-bold text-lg">{new Date(result.started_at).toLocaleString()}</p>
            </div>
            {result.completed_at && (
              <div className="bg-gradient-to-br from-white/10 to-white/5 p-6 rounded-2xl border border-white/15 shadow-xl">
                <p className="text-white/70 text-sm mb-2 font-bold tracking-wide uppercase">Completed</p>
                <p className="text-white font-bold text-lg">{new Date(result.completed_at).toLocaleString()}</p>
              </div>
            )}
            {result.duration_ms && (
              <div className="bg-gradient-to-br from-emerald-500/15 to-green-500/10 p-6 rounded-2xl border border-emerald-500/30 shadow-xl">
                <p className="text-emerald-300 text-sm mb-2 font-bold tracking-wide uppercase">Duration</p>
                <p className="text-emerald-200 font-black text-lg font-mono">{result.duration_ms.toFixed(0)}ms</p>
              </div>
            )}
            <div className="bg-gradient-to-br from-indigo-500/15 to-blue-500/10 p-6 rounded-2xl border border-indigo-500/30 shadow-xl">
              <p className="text-indigo-300 text-sm mb-2 font-bold tracking-wide uppercase">Test ID</p>
              <p className="text-indigo-200 font-mono text-lg font-bold">{result.test_id.slice(0, 8)}</p>
            </div>
          </div>

          {result.result && (
            <div className="bg-gradient-to-br from-white/10 to-white/5 p-8 rounded-3xl border border-white/15 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-bold text-emerald-300">Result:</h4>
                <button
                  onClick={() => {
                    try {
                      const parsed = JSON.parse(result.result)
                      const formatted = JSON.stringify(parsed, null, 2)
                      const blob = new Blob([formatted], { type: 'application/json' })
                      const url = URL.createObjectURL(blob)
                      const link = document.createElement('a')
                      link.href = url
                      link.download = `test-result-${result.test_id.slice(0, 8)}.json`
                      link.click()
                      URL.revokeObjectURL(url)
                    } catch (e) {
                      // Not JSON, export as text
                      const blob = new Blob([result.result], { type: 'text/plain' })
                      const url = URL.createObjectURL(blob)
                      const link = document.createElement('a')
                      link.href = url
                      link.download = `test-result-${result.test_id.slice(0, 8)}.txt`
                      link.click()
                      URL.revokeObjectURL(url)
                    }
                  }}
                  className="px-3 py-1.5 rounded-lg bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/30 flex items-center gap-2 text-sm"
                  title="Export result"
                >
                  <Download className="w-4 h-4" />
                  JSON
                </button>
                <button
                  onClick={() => exportTestResult(result)}
                  className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 flex items-center gap-2 text-sm"
                  title="Export as PDF"
                >
                  <FileDown className="w-4 h-4" />
                  PDF
                </button>
              </div>
              <div className="bg-black/50 p-6 rounded-2xl border border-white/10 overflow-x-auto">
                {(() => {
                  const rawResult = result.result
                  const resultString = normalizeResultText(rawResult)
                  try {
                    const parsed = JSON.parse(resultString)
                    if (parsed.text && parsed.structured) {
                      // Structured result - show both
                      return (
                        <div className="space-y-4">
                          <details className="bg-black/30 border border-white/10 rounded-lg p-4">
                            <summary className="text-white/70 text-sm cursor-pointer hover:text-white font-semibold mb-2">
                              📊 Structured Data (Click to expand)
                            </summary>
                            <pre className="text-cyan-300 whitespace-pre-wrap leading-relaxed text-xs font-mono mt-2 max-h-[400px] overflow-y-auto">
                              {JSON.stringify(parsed.structured, null, 2)}
                            </pre>
                          </details>
                          <details open className="bg-black/30 border border-white/10 rounded-lg p-4">
                            <summary className="flex items-center gap-2 text-white/70 text-sm cursor-pointer hover:text-white font-semibold mb-2">
                              <FileText className="w-4 h-4 text-slate-400" />
                              <span>Text Output (Click to collapse)</span>
                            </summary>
                            <pre className="text-white/90 whitespace-pre-wrap leading-relaxed text-sm font-mono mt-2 max-h-[400px] overflow-y-auto">
                              {parsed.text}
                            </pre>
                          </details>
                        </div>
                      )
                    }
                    // Valid JSON but not structured format
                    return (
                      <pre className="text-cyan-300 whitespace-pre-wrap leading-relaxed text-sm font-mono max-h-[600px] overflow-y-auto">
                        {JSON.stringify(parsed, null, 2)}
                      </pre>
                    )
                  } catch (e) {
                    const fallbackText =
                      typeof rawResult === 'string'
                        ? rawResult
                        : (() => {
                            try {
                              return JSON.stringify(rawResult, null, 2)
                            } catch {
                              return String(rawResult)
                            }
                          })()
                    // Not JSON, show as plain text
                    return (
                      <pre className="text-white/90 whitespace-pre-wrap leading-relaxed text-sm font-mono max-h-[600px] overflow-y-auto">
                        {fallbackText}
                      </pre>
                    )
                  }
                })()}
              </div>
            </div>
          )}

          {screenshots.length > 0 && (
            <div className="mt-6">
              <ScreenshotGallery screenshots={screenshots} title="Screenshots" />
            </div>
          )}

          {/* Tags */}
          <div className="mt-6">
            <TestTags
              testId={result.test_id}
              selectedTags={result.tags || []}
              onTagsChange={(tags) => {
                // Save tags to result
                const updatedResults = JSON.parse(localStorage.getItem('testResults') || '[]')
                const updated = updatedResults.map((r) =>
                  r.test_id === result.test_id ? { ...r, tags } : r
                )
                localStorage.setItem('testResults', JSON.stringify(updated))
              }}
            />
          </div>

          {result.error && (
            <div className="bg-gradient-to-r from-red-500/25 to-red-500/15 text-red-100 p-8 rounded-3xl mt-6 border border-red-500/40 shadow-2xl">
              <h4 className="text-lg font-bold mb-4 text-red-300">Error:</h4>
              <p className="text-base leading-relaxed">{result.error}</p>
            </div>
          )}
        </div>
      </div>

      {lightbox.open && (
        <div
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-6"
          onClick={() => setLightbox({ open: false, src: '' })}
        >
          <img src={lightbox.src} alt="preview" className="max-h-[90vh] max-w-[90vw] object-contain" />
        </div>
      )}
    </div>
  )
}

function TestResults() {
  const [limit, setLimit] = useState(50)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [testTypeFilter, setTestTypeFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date') // date, duration, status
  const [showComparison, setShowComparison] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [selectedTags, setSelectedTags] = useState([])
  const [selectedItems, setSelectedItems] = useState([])
  const { exportTestResult } = usePDFExporter()

  // Load available tags
  const availableTags = useMemo(() => {
    const saved = localStorage.getItem('testTags')
    return saved ? JSON.parse(saved) : []
  }, [])

  const { data: results, isLoading } = useQuery({
    queryKey: ['test-results', limit],
    queryFn: () => testResultsAPI.list(limit),
    refetchInterval: 3000,
  })

  // Filter and sort results
  const filteredResults = useMemo(() => {
    if (!results?.results) return []
    
    let filtered = [...results.results]
    
    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(r => 
        r.command?.toLowerCase().includes(query) ||
        normalizeResultText(r.result).toLowerCase().includes(query) ||
        r.test_id?.toLowerCase().includes(query)
      )
    }
    
    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(r => r.status === statusFilter)
    }
    
    // Test type filter
    if (testTypeFilter !== 'all') {
      filtered = filtered.filter(r => {
        const cmd = (r.command || '').toLowerCase()
        if (testTypeFilter === 'auto-check') return cmd.includes('auto check') || cmd.includes('auto-check')
        if (testTypeFilter === 'auto-audit') return cmd.includes('auto audit') || cmd.includes('auto-audit')
        if (testTypeFilter === 'browser-use') return cmd.includes('test case') || cmd.includes('verify') || cmd.includes('check')
        if (testTypeFilter === 'mobile') return r.device || r.screenshots?.length > 0
        if (testTypeFilter === 'cross-browser') return cmd.includes('cross-browser') || cmd.includes('cross browser')
        return true
      })
    }
    
    // Sort
    filtered.sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.started_at) - new Date(a.started_at)
      } else if (sortBy === 'duration') {
        return (b.duration_ms || 0) - (a.duration_ms || 0)
      } else if (sortBy === 'status') {
        const statusOrder = { passed: 1, completed: 2, failed: 3, running: 4, pending: 5 }
        return (statusOrder[a.status] || 99) - (statusOrder[b.status] || 99)
      }
      return 0
    })
    
    return filtered
  }, [results?.results, searchQuery, statusFilter, testTypeFilter, sortBy, selectedTags])

  // Export functions
  const exportToJSON = () => {
    const dataStr = JSON.stringify(filteredResults, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test-results-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  const exportToCSV = () => {
    const headers = ['Test ID', 'Command', 'Status', 'Started At', 'Completed At', 'Duration (ms)', 'Error']
    const rows = filteredResults.map(r => [
      r.test_id || '',
      (r.command || '').replace(/"/g, '""'),
      r.status || '',
      r.started_at || '',
      r.completed_at || '',
      r.duration_ms || '',
      (r.error || '').replace(/"/g, '""')
    ])
    
    const csvContent = [
      headers.map(h => `"${h}"`).join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')
    
    const dataBlob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `test-results-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  const passedTests = results?.results?.filter(r => r.status === 'passed').length || 0
  const completedTests = results?.results?.filter(r => r.status === 'completed' || r.status === 'passed' || r.status === 'failed').length || 0
  const failedTests = results?.results?.filter(r => r.status === 'failed').length || 0
  const runningTests = results?.results?.filter(r => r.status === 'running').length || 0

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Test Results</h1>
        <p className="page-description">
          View and analyze test execution history
        </p>
      </div>

      {showComparison && (
        <div className="card p-6">
          <TestComparison testResults={results?.results || []} />
        </div>
      )}

      {showHistory && (
        <div className="card p-6">
          <TestHistory testResults={results?.results || []} />
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 md:gap-4">
        <div className="card-stat bg-slate-800/50 border-slate-700/50">
          <div className="text-center">
            <p className="text-xl md:text-2xl font-bold text-white mb-1">{results?.total || 0}</p>
            <p className="text-xs text-slate-400">Total Tests</p>
          </div>
        </div>
        <div className="card-stat bg-emerald-500/10 border-emerald-500/20">
          <div className="text-center">
            <p className="text-xl md:text-2xl font-bold text-white mb-1">{passedTests}</p>
            <p className="text-xs text-slate-400">Passed</p>
          </div>
        </div>
        <div className="card-stat bg-amber-500/10 border-amber-500/20">
          <div className="text-center">
            <p className="text-xl md:text-2xl font-bold text-white mb-1">{completedTests}</p>
            <p className="text-xs text-slate-400">Completed</p>
          </div>
        </div>
        <div className="card-stat bg-rose-500/10 border-rose-500/20">
          <div className="text-center">
            <p className="text-xl md:text-2xl font-bold text-white mb-1">{failedTests}</p>
            <p className="text-xs text-slate-400">Failed</p>
          </div>
        </div>
        <div className="card-stat bg-blue-500/10 border-blue-500/20 col-span-2 md:col-span-1">
          <div className="text-center">
            <p className="text-xl md:text-2xl font-bold text-white mb-1">{runningTests}</p>
            <p className="text-xs text-slate-400">Running</p>
          </div>
        </div>
      </div>

      <div className="card p-5 md:p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-5 md:mb-6">
          <div>
            <h2 className="text-base md:text-lg font-semibold text-white mb-1">Filters & Search</h2>
            <p className="text-xs md:text-sm text-slate-400">Refine and export your test results</p>
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={exportToJSON}
              className="btn btn-secondary text-sm flex-1 sm:flex-none"
              title="Export to JSON"
            >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">JSON</span>
            </button>
            <button
              onClick={exportToCSV}
              className="btn btn-secondary text-sm flex-1 sm:flex-none"
              title="Export to CSV"
            >
              <Download className="w-4 h-4" />
              <span className="hidden sm:inline">CSV</span>
            </button>
            <button
              onClick={() => {
                setShowComparison(!showComparison)
                setShowHistory(false)
              }}
              className="btn btn-secondary text-sm flex-1 sm:flex-none"
              title="Compare Tests"
            >
              <GitCompare className="w-4 h-4" />
              <span className="hidden sm:inline">Compare</span>
            </button>
            <button
              onClick={() => {
                setShowHistory(!showHistory)
                setShowComparison(false)
              }}
              className="btn btn-secondary text-sm flex-1 sm:flex-none"
              title="View History"
            >
              <Clock className="w-4 h-4" />
              <span className="hidden sm:inline">History</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 md:gap-6 mb-5 md:mb-6">
          {/* Search */}
          <div className="sm:col-span-2 lg:col-span-2">
            <label className="label">Search</label>
            <div className="relative">
              <Search className="absolute left-3 md:left-4 top-1/2 transform -translate-y-1/2 w-4 h-4 md:w-5 md:h-5 text-slate-500" />
              <input
                type="text"
                className="input pl-10 md:pl-12 pr-10 text-sm md:text-base"
                placeholder="Search by command, result, or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-500 hover:text-white transition-colors"
                >
                  <X className="w-4 h-4 md:w-5 md:h-5" />
                </button>
              )}
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <label className="label">Status</label>
            <select
              className="input text-sm md:text-base"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="passed">Passed</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="running">Running</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          {/* Test Type Filter */}
          <div>
            <label className="label">Test Type</label>
            <select
              className="input text-sm md:text-base"
              value={testTypeFilter}
              onChange={(e) => setTestTypeFilter(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="auto-check">Auto Check</option>
              <option value="auto-audit">Auto Audit</option>
              <option value="browser-use">Browser Use</option>
              <option value="mobile">Mobile Test</option>
              <option value="cross-browser">Cross-Browser</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="label">Sort By</label>
            <select
              className="input text-sm md:text-base"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="date">Date (Newest)</option>
              <option value="duration">Duration (Longest)</option>
              <option value="status">Status</option>
            </select>
          </div>
        </div>

        {/* Tag Filter */}
        {availableTags.length > 0 && (
          <div className="mb-5 md:mb-6">
            <TagFilter
              tags={availableTags}
              selectedTags={selectedTags}
              onTagsChange={setSelectedTags}
            />
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="label">Results Limit</label>
            <select
              className="input text-lg"
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
            >
              <option value={10}>10 results</option>
              <option value={25}>25 results</option>
              <option value={50}>50 results</option>
              <option value={100}>100 results</option>
              <option value={500}>500 results</option>
            </select>
          </div>
          <div className="flex items-end">
            <div className="bg-gradient-to-br from-white/10 to-white/5 p-4 rounded-xl border border-white/15 w-full">
              <p className="text-white/70 text-sm mb-1 font-bold">Showing Results</p>
              <p className="text-white font-bold text-xl">
                {filteredResults.length} of {results?.total || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-32">
          <Loader className="w-20 h-20 animate-spin text-white mb-8" />
          <p className="text-white/80 text-2xl font-bold">Loading test results...</p>
        </div>
      ) : filteredResults.length > 0 ? (
        <div className="space-y-8">
          {filteredResults.map((result, idx) => (
            <div key={result.test_id} style={{ animationDelay: `${idx * 0.1}s` }}>
              <TestResultCard result={result} />
            </div>
          ))}
        </div>
      ) : searchQuery || statusFilter !== 'all' || testTypeFilter !== 'all' ? (
        <div className="card text-center py-24 fade-in hover-lift">
          <div className="bg-gradient-to-br from-yellow-500/15 to-amber-500/10 w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-10 border border-yellow-500/25 shadow-2xl">
            <Search className="w-16 h-16 text-yellow-300" />
          </div>
          <h3 className="text-6xl font-black text-gradient text-glow mb-8">
            No Results Found
          </h3>
          <p className="text-white/80 text-2xl font-medium mb-6">
            Try adjusting your filters or search query
          </p>
          <button
            onClick={() => {
              setSearchQuery('')
              setStatusFilter('all')
              setTestTypeFilter('all')
            }}
            className="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20"
          >
            Clear All Filters
          </button>
        </div>
      ) : (
        <div className="card text-center py-24 fade-in hover-lift">
          <div className="bg-gradient-to-br from-indigo-500/15 to-purple-500/10 w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-10 border border-indigo-500/25 shadow-2xl">
            <BarChart3 className="w-16 h-16 text-indigo-300" />
          </div>
          <h3 className="text-6xl font-black text-gradient text-glow mb-8">
            No Test Results
          </h3>
          <p className="text-white/80 text-2xl font-medium">
            Execute some tests to see results here
          </p>
        </div>
      )}
    </div>
  )
}

export default TestResults
