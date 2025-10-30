import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart3, Loader, CheckCircle, XCircle, Clock, Filter } from 'lucide-react'
import { testResultsAPI, sessionsAPI } from '../api/client'

function TestResultCard({ result }) {
  const [lightbox, setLightbox] = useState({ open: false, src: '' })
  
  const statusIcons = {
    completed: <CheckCircle className="w-5 h-5 text-green-500" />,
    failed: <XCircle className="w-5 h-5 text-red-500" />,
    running: <Loader className="w-5 h-5 text-blue-500 animate-spin" />,
    pending: <Clock className="w-5 h-5 text-yellow-500" />,
  }

  const statusColors = {
    completed: 'badge-success',
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
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-3xl font-bold text-gradient text-glow">
              {result.command}
            </h3>
            <span className={`badge ${statusColors[result.status]} hover:scale-110 transition-transform duration-500`}>
              {result.status}
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
              <h4 className="text-lg font-bold text-emerald-300 mb-4">Result:</h4>
              <p className="text-white whitespace-pre-wrap leading-relaxed text-base">{result.result}</p>
            </div>
          )}

          {screenshots.length > 0 && (
            <div className="bg-gradient-to-br from-white/10 to-white/5 p-8 rounded-3xl border border-white/15 shadow-xl mt-6">
              <h4 className="text-lg font-bold text-emerald-300 mb-4">Screenshots ({screenshots.length}):</h4>
              <div className="flex flex-row flex-wrap gap-4">
                {screenshots.map((src, idx) => (
                  <button
                    key={idx}
                    onClick={() => setLightbox({ open: true, src: `${src}?t=${Date.now()}` })}
                    className="bg-black/40 border border-white/10 rounded-xl overflow-hidden transform transition-transform hover:scale-[1.03] hover:shadow-lg hover:shadow-black/30"
                  >
                    <img src={`${src}?t=${Date.now()}`} alt={`screenshot-${idx + 1}`} className="h-96 object-contain" />
                  </button>
                ))}
              </div>
            </div>
          )}

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
  const [selectedSession, setSelectedSession] = useState(null)
  const [limit, setLimit] = useState(50)

  const { data: sessions } = useQuery({
    queryKey: ['sessions'],
    queryFn: sessionsAPI.list,
  })

  const { data: results, isLoading } = useQuery({
    queryKey: ['test-results', selectedSession, limit],
    queryFn: () => testResultsAPI.list(selectedSession, limit),
    refetchInterval: 3000,
  })

  const completedTests = results?.results?.filter(r => r.status === 'completed').length || 0
  const failedTests = results?.results?.filter(r => r.status === 'failed').length || 0
  const runningTests = results?.results?.filter(r => r.status === 'running').length || 0

  return (
    <div className="space-y-12 fade-in">
      <div className="slide-in text-center">
        <h1 className="text-8xl font-black text-gradient text-glow mb-8 tracking-tight">
          Test Results
        </h1>
        <p className="text-white/80 text-2xl font-medium tracking-wide">View and analyze test execution history</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="card-stat text-center group cursor-pointer hover-lift">
          <p className="text-6xl font-black text-gradient text-glow mb-4 transition-all duration-700 group-hover:scale-110">
            {results?.total || 0}
          </p>
          <p className="text-sm text-white/70 font-bold tracking-wide uppercase">Total Tests</p>
        </div>
        <div className="card-stat text-center group cursor-pointer hover-lift">
          <p className="text-6xl font-black text-gradient text-glow mb-4 transition-all duration-700 group-hover:scale-110">
            {completedTests}
          </p>
          <p className="text-sm text-white/70 font-bold tracking-wide uppercase">Completed</p>
        </div>
        <div className="card-stat text-center group cursor-pointer hover-lift">
          <p className="text-6xl font-black text-gradient text-glow mb-4 transition-all duration-700 group-hover:scale-110">
            {failedTests}
          </p>
          <p className="text-sm text-white/70 font-bold tracking-wide uppercase">Failed</p>
        </div>
        <div className="card-stat text-center group cursor-pointer hover-lift">
          <p className="text-6xl font-black text-gradient text-glow mb-4 transition-all duration-700 group-hover:scale-110">
            {runningTests}
          </p>
          <p className="text-sm text-white/70 font-bold tracking-wide uppercase">Running</p>
        </div>
      </div>

      <div className="card hover-lift">
        <div className="flex items-center space-x-6 mb-10">
          <div className="bg-gradient-to-br from-indigo-500/25 to-purple-500/15 p-4 rounded-2xl border border-indigo-500/30 shadow-2xl">
            <Filter className="w-8 h-8 text-indigo-300" />
          </div>
          <h2 className="text-4xl font-bold text-gradient text-glow">
            Filters
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <label className="label">Filter by Session</label>
            <select
              className="input text-lg"
              value={selectedSession || ''}
              onChange={(e) => setSelectedSession(e.target.value || null)}
            >
              <option value="">All Sessions</option>
              {sessions?.sessions?.map((session) => (
                <option key={session.session_id} value={session.session_id}>
                  {session.session_name} - {session.website_url}
                </option>
              ))}
            </select>
          </div>

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
            </select>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-32">
          <Loader className="w-20 h-20 animate-spin text-white mb-8" />
          <p className="text-white/80 text-2xl font-bold">Loading test results...</p>
        </div>
      ) : results?.results?.length > 0 ? (
        <div className="space-y-8">
          {results.results.map((result, idx) => (
            <div key={result.test_id} style={{ animationDelay: `${idx * 0.1}s` }}>
              <TestResultCard result={result} />
            </div>
          ))}
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
            {selectedSession
              ? 'No results found for the selected session'
              : 'Execute some tests to see results here'}
          </p>
        </div>
      )}
    </div>
  )
}

export default TestResults
