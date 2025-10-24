import { useQuery } from '@tanstack/react-query'
import { Activity, TestTube, CheckCircle, XCircle, Clock } from 'lucide-react'
import { sessionsAPI, testResultsAPI, healthAPI } from '../api/client'

function StatCard({ title, value, icon: Icon, color = 'primary' }) {
  const colors = {
    primary: 'text-white',
    success: 'text-green-200',
    error: 'text-red-200',
    warning: 'text-yellow-200',
  }

  const bgColors = {
    primary: 'from-white/15 to-white/10',
    success: 'from-green-500/25 to-emerald-500/15',
    error: 'from-red-500/25 to-rose-500/15',
    warning: 'from-yellow-500/25 to-amber-500/15',
  }

  const glowColors = {
    primary: 'shadow-white/20',
    success: 'shadow-green-500/30',
    error: 'shadow-red-500/30',
    warning: 'shadow-yellow-500/30',
  }

  return (
    <div className={`card-stat group cursor-pointer fade-in hover-lift hover-glow ${glowColors[color]}`}>
      <div className="flex items-center justify-between relative z-10">
        <div>
          <p className="text-sm text-white/70 mb-4 font-bold tracking-wide uppercase">{title}</p>
          <p className="text-6xl font-black text-gradient text-glow transition-all duration-700 group-hover:scale-110 group-hover:rotate-2">
            {value}
          </p>
        </div>
        <div className={`bg-gradient-to-br ${bgColors[color]} p-6 rounded-3xl transition-all duration-700 group-hover:scale-125 group-hover:rotate-12 border border-white/20 shadow-2xl`}>
          <Icon className={`w-16 h-16 ${colors[color]} transition-all duration-700 group-hover:scale-125 group-hover:rotate-12`} />
        </div>
      </div>
    </div>
  )
}

function RecentTest({ test }) {
  const statusColors = {
    completed: 'badge-success',
    running: 'badge-info',
    failed: 'badge-error',
    pending: 'badge-warning',
  }

  return (
    <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-2xl p-8 rounded-3xl hover:from-white/15 hover:to-white/10 transition-all duration-700 transform hover:scale-[1.03] hover:-translate-y-2 border border-white/15 hover:border-white/25 cursor-pointer group shadow-xl hover:shadow-2xl">
      <div className="flex items-start justify-between mb-6">
        <p className="text-white font-bold text-lg truncate flex-1 group-hover:text-white/90 transition-colors leading-relaxed">{test.command}</p>
        <span className={`badge ${statusColors[test.status]} ml-4 hover:scale-110 transition-transform duration-500`}>
          {test.status}
        </span>
      </div>
      <div className="flex items-center justify-between text-sm">
        <span className="text-white/70 font-medium">
          {new Date(test.started_at).toLocaleString()}
        </span>
        {test.duration_ms && (
          <span className="text-white/80 font-mono bg-gradient-to-r from-white/10 to-white/5 px-4 py-2 rounded-xl border border-white/20 shadow-lg">
            {test.duration_ms.toFixed(0)}ms
          </span>
        )}
      </div>
    </div>
  )
}

function Dashboard() {
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: healthAPI.check,
    refetchInterval: 5000,
  })

  const { data: sessions, isLoading: sessionsLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: sessionsAPI.list,
    refetchInterval: 3000,
  })

  const { data: testResults, isLoading: resultsLoading } = useQuery({
    queryKey: ['test-results'],
    queryFn: () => testResultsAPI.list(null, 10),
    refetchInterval: 3000,
  })

  const activeSessions = sessions?.sessions?.filter(s => s.status === 'active').length || 0
  const totalTests = testResults?.total || 0
  const completedTests = testResults?.results?.filter(r => r.status === 'completed').length || 0
  const failedTests = testResults?.results?.filter(r => r.status === 'failed').length || 0

  return (
    <div className="space-y-16 fade-in">
      <div className="slide-in text-center">
        <h1 className="text-8xl font-black text-gradient text-glow mb-8 tracking-tight">
          Dashboard
        </h1>
        <p className="text-white/80 text-2xl font-medium tracking-wide">
          Monitor your QA automation in real-time
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
        <StatCard
          title="Active Sessions"
          value={activeSessions}
          icon={Activity}
          color="primary"
        />
        <StatCard
          title="Total Tests"
          value={totalTests}
          icon={TestTube}
          color="primary"
        />
        <StatCard
          title="Completed"
          value={completedTests}
          icon={CheckCircle}
          color="success"
        />
        <StatCard
          title="Failed"
          value={failedTests}
          icon={XCircle}
          color="error"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <div className="card hover-lift">
          <h2 className="text-4xl font-bold text-gradient text-glow mb-10">
            Active Sessions
          </h2>
          <div className="space-y-6">
            {sessionsLoading ? (
              <div className="space-y-6">
                <div className="skeleton h-32 rounded-2xl"></div>
                <div className="skeleton h-32 rounded-2xl"></div>
              </div>
            ) : sessions?.sessions?.length > 0 ? (
              sessions.sessions.map((session, idx) => (
                <div
                  key={session.session_id}
                  style={{ animationDelay: `${idx * 0.15}s` }}
                  className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-2xl p-8 rounded-3xl hover:from-white/15 hover:to-white/10 transition-all duration-700 transform hover:scale-[1.03] hover:-translate-y-2 border border-white/15 hover:border-white/25 fade-in shadow-xl hover:shadow-2xl"
                >
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <p className="text-white font-bold text-xl mb-2">{session.session_name}</p>
                      <p className="text-sm text-white/70 font-medium">{session.website_url}</p>
                    </div>
                    <span className={`badge ${
                      session.status === 'active' ? 'badge-success' :
                      session.status === 'initializing' ? 'badge-info' :
                      'badge-warning'
                    }`}>
                      {session.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm text-white/70 font-medium">
                    <span>Provider: {session.ai_provider}</span>
                    <span>Commands: {session.commands_executed}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-white/70 text-center py-16 text-xl font-medium">No active sessions</p>
            )}
          </div>
        </div>

        <div className="card hover-lift">
          <h2 className="text-4xl font-bold text-gradient text-glow mb-10">
            Recent Tests
          </h2>
          <div className="space-y-6">
            {resultsLoading ? (
              <div className="space-y-6">
                <div className="skeleton h-28 rounded-2xl"></div>
                <div className="skeleton h-28 rounded-2xl"></div>
                <div className="skeleton h-28 rounded-2xl"></div>
              </div>
            ) : testResults?.results?.length > 0 ? (
              testResults.results.map((test, idx) => (
                <div key={test.test_id} style={{ animationDelay: `${idx * 0.15}s` }} className="fade-in">
                  <RecentTest test={test} />
                </div>
              ))
            ) : (
              <p className="text-white/70 text-center py-16 text-xl font-medium">No test results yet</p>
            )}
          </div>
        </div>
      </div>

      {health && (
        <div className="card fade-in hover-lift">
          <h2 className="text-4xl font-bold text-gradient text-glow mb-10">
            System Health
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div className="bg-gradient-to-br from-green-500/25 to-emerald-500/15 p-8 rounded-3xl border border-green-500/40 hover:scale-110 transition-all duration-700 cursor-pointer backdrop-blur-2xl shadow-2xl hover:shadow-green-500/30">
              <p className="text-5xl font-black text-gradient text-glow mb-4">
                {health.status}
              </p>
              <p className="text-sm text-white/70 font-bold tracking-wide uppercase">Status</p>
            </div>
            <div className="bg-gradient-to-br from-white/15 to-white/10 p-8 rounded-3xl border border-white/25 hover:scale-110 transition-all duration-700 cursor-pointer backdrop-blur-2xl shadow-2xl hover:shadow-white/20">
              <p className="text-5xl font-black text-white mb-4">{health.active_sessions}</p>
              <p className="text-sm text-white/70 font-bold tracking-wide uppercase">Active Sessions</p>
            </div>
            <div className="bg-gradient-to-br from-white/15 to-white/10 p-8 rounded-3xl border border-white/25 hover:scale-110 transition-all duration-700 cursor-pointer backdrop-blur-2xl shadow-2xl hover:shadow-white/20">
              <p className="text-5xl font-black text-white mb-4">{health.total_test_results}</p>
              <p className="text-sm text-white/70 font-bold tracking-wide uppercase">Total Results</p>
            </div>
            <div className="bg-gradient-to-br from-white/15 to-white/10 p-8 rounded-3xl border border-white/25 hover:scale-110 transition-all duration-700 cursor-pointer backdrop-blur-2xl shadow-2xl hover:shadow-white/20">
              <p className="text-3xl font-black text-white font-mono mb-4">
                {new Date(health.timestamp).toLocaleTimeString()}
              </p>
              <p className="text-sm text-white/70 font-bold tracking-wide uppercase">Last Check</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
