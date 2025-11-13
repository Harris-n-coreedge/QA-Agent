import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  TestTube,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  ShieldCheck,
  Layers,
  Sparkles,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'
import { agentAPI, testResultsAPI, healthAPI } from '../api/client'
import { AdvancedAnalytics } from '../components/AdvancedAnalytics'
import { useTestAnalytics } from '../hooks/useTestAnalytics'

function TrendBadge({ change, invert = false, format = 'percent', label }) {
  if (change === undefined || change === null) {
    return null
  }

  const threshold = 0.05
  const effective = invert ? -change : change
  const positive = effective >= threshold
  const negative = effective <= -threshold

  if (!positive && !negative) {
    return (
      <div className="flex flex-col items-end gap-1">
        <span className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-slate-300/80">
          Stable
        </span>
        {label && <span className="text-[10px] uppercase tracking-[0.14em] text-slate-500">{label}</span>}
      </div>
    )
  }

  const Icon = positive ? TrendingUp : TrendingDown
  const tone = positive
    ? 'border-emerald-400/40 bg-emerald-500/15 text-emerald-300'
    : 'border-rose-400/40 bg-rose-500/15 text-rose-300'

  let formatted = ''
  if (format === 'points') {
    formatted = `${change > 0 ? '+' : ''}${change.toFixed(1)} pts`
  } else {
    formatted = `${change > 0 ? '+' : ''}${change.toFixed(1)}%`
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.18em] ${tone}`}>
        <Icon className="h-[10px] w-[10px]" />
        {formatted}
      </span>
      {label && <span className="text-[10px] uppercase tracking-[0.14em] text-slate-500">{label}</span>}
    </div>
  )
}

function StatCard({
  title,
  value,
  icon: Icon,
  change,
  changeLabel,
  invert = false,
  format = 'percent',
  accent = 'from-[#5b21b6]/90 via-[#312e81]/70 to-[#0b1120]/95',
}) {
  return (
    <div className={`relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br ${accent} p-6 shadow-[0_25px_60px_rgba(51,65,255,0.25)] transition-transform duration-300 hover:-translate-y-1`}>
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute -bottom-24 left-6 h-44 w-44 rounded-full bg-purple-500/20 blur-3xl" />
        <div className="absolute -top-24 right-4 h-40 w-40 rounded-full bg-indigo-500/10 blur-3xl" />
      </div>
      <div className="relative flex flex-col gap-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/60">{title}</p>
            <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/10 text-white shadow-lg shadow-purple-900/25 backdrop-blur-md">
            <Icon className="h-5 w-5" />
          </div>
        </div>
        <TrendBadge change={change} invert={invert} format={format} label={changeLabel} />
      </div>
    </div>
  )
}

function RecentTest({ test, delay = 0 }) {
  const statusConfig = {
    passed: { class: 'badge-success', dot: 'success', icon: CheckCircle, iconColor: 'text-emerald-300' },
    completed: { class: 'badge-warning', dot: 'warning', icon: Clock, iconColor: 'text-amber-300' },
    running: { class: 'badge-info', dot: 'info', icon: Activity, iconColor: 'text-sky-300' },
    failed: { class: 'badge-error', dot: 'error', icon: XCircle, iconColor: 'text-rose-300' },
    pending: { class: 'badge-neutral', dot: 'warning', icon: Clock, iconColor: 'text-slate-300' },
  }

  const config = statusConfig[test.status] || statusConfig.pending
  const Icon = config.icon

  return (
    <div
      className="group rounded-3xl border border-white/10 bg-[#0b1120]/70 p-5 shadow-[0_20px_60px_rgba(8,13,28,0.45)] transition-all duration-300 hover:-translate-y-1 hover:border-primary-500/40 hover:bg-[#121933]/80"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start gap-4">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-2.5 text-white/90">
          <Icon className={`h-5 w-5 ${config.iconColor}`} />
        </div>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`status-dot ${config.dot}`} />
            <span className={`badge ${config.class}`}>{test.status}</span>
            {test.duration_ms && (
              <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] uppercase tracking-[0.18em] text-slate-400">
                {formatDuration(test.duration_ms)}
              </span>
            )}
          </div>
          <p className="mt-2 text-sm font-semibold text-white group-hover:text-slate-100">
            {test.command}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-400">
            <span>{new Date(test.started_at).toLocaleString()}</span>
            {test.metadata?.environment && (
              <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] uppercase tracking-[0.18em] text-slate-400">
                {test.metadata.environment}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function formatNumber(value) {
  if (value === null || value === undefined) return '—'
  if (typeof value !== 'number') return value
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`
  if (value >= 10_000) return `${(value / 1_000).toFixed(1)}K`
  if (value >= 1_000) return `${(value / 1_000).toFixed(2)}K`
  return value.toLocaleString()
}

function formatDuration(ms) {
  if (!ms || Number.isNaN(ms)) return 'N/A'
  if (ms < 1000) return `${ms.toFixed(0)}ms`
  if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`
  const minutes = Math.floor(ms / 60_000)
  const seconds = Math.round((ms % 60_000) / 1000)
  return `${minutes}m ${seconds.toString().padStart(2, '0')}s`
}

function formatRelativeTime(date) {
  if (!date) return '—'
  const diff = Date.now() - new Date(date).getTime()
  if (diff < 60_000) return 'moments ago'
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`
  return `${Math.floor(diff / 86_400_000)}d ago`
}

function buildGaugeGradient(segments) {
  const total = segments.reduce((sum, seg) => sum + seg.value, 0)
  if (total === 0) {
    return 'conic-gradient(from 270deg, rgba(255,255,255,0.08) 0deg 360deg)'
  }

  let cumulative = 0
  const stops = segments.map((segment) => {
    const start = (cumulative / total) * 360
    cumulative += segment.value
    const end = (cumulative / total) * 360
    return `${segment.color} ${start}deg ${end}deg`
  })

  return `conic-gradient(from 270deg, ${stops.join(', ')})`
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

  const tests = testResults?.results || []
  const analytics = useTestAnalytics(tests)
  const recentTests = tests.slice(0, 6)

  const summaryCards = [
    {
      title: 'Total Executions',
      value: formatNumber(testResults?.total || 0),
      icon: TestTube,
      change: analytics.throughputTrend,
      changeLabel: 'vs prior 24h',
      format: 'percent',
      accent: 'from-[#5b21b6]/90 via-[#312e81]/70 to-[#0a0f1e]/95',
    },
    {
      title: 'Pass Rate',
      value: `${analytics.successRate.toFixed(1)}%`,
      icon: CheckCircle,
      change: analytics.successRateDelta,
      changeLabel: 'vs previous day',
      format: 'points',
      accent: 'from-[#4c1d95]/90 via-[#1e1b4b]/70 to-[#0b1120]/95',
    },
    {
      title: 'Active Runs',
      value: formatNumber(analytics.running),
      icon: Activity,
      change: analytics.total ? (analytics.running / analytics.total) * 100 : 0,
      changeLabel: 'of today’s load',
      format: 'percent',
      accent: 'from-[#312e81]/90 via-[#1e1b4b]/70 to-[#0a0f1e]/95',
    },
    {
      title: 'Detected Failures',
      value: formatNumber(analytics.failed),
      icon: XCircle,
      change: analytics.total ? (analytics.failed / analytics.total) * 100 : 0,
      changeLabel: 'of total runs',
      format: 'percent',
      accent: 'from-[#581c87]/90 via-[#3b0764]/70 to-[#0a0b1a]/95',
    },
  ]

  const topCommands = analytics.topCommands.slice(0, 3)
  const successLeaders = analytics.commandSuccessLeaders.slice(0, 3)

  const successSegments = [
    { label: 'Passed', value: analytics.passed, color: '#8b5cf6' },
    { label: 'Running', value: analytics.running, color: '#22d3ee' },
    { label: 'Failed', value: analytics.failed, color: '#f97316' },
  ]

  const queueBreakdown = [
    { label: 'Running', value: analytics.running, color: 'bg-sky-500' },
    { label: 'Pending', value: analytics.pending, color: 'bg-amber-500' },
    { label: 'Failed', value: analytics.failed, color: 'bg-rose-500' },
    { label: 'Completed', value: analytics.completed, color: 'bg-emerald-500' },
  ]

  return (
    <div className="relative z-[1] space-y-8 fade-in">
      <div className="page-header">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="page-title">Analytics Control Center</h1>
            <p className="page-description">
              Hyper-visual monitoring for your autonomous QA operation
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            {agentStatus && (
              <div className="flex items-center gap-3 rounded-full border border-emerald-400/30 bg-emerald-500/10 px-4 py-2 text-emerald-200 shadow-[0_16px_40px_rgba(16,185,129,0.18)]">
                <div className="status-dot success" />
                <div className="text-left">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-emerald-200/80">Agent</p>
                  <p className="text-sm font-semibold text-white">{agentStatus.status}</p>
                </div>
              </div>
            )}
            <select className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.18em] text-slate-400 outline-none focus:border-primary-500/60 focus:text-white">
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Quarter to date</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {summaryCards.map((card) => (
          <StatCard key={card.title} {...card} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 2xl:grid-cols-3">
        <div className="2xl:col-span-2">
          <div className="rounded-4xl border border-white/10 bg-[#050713]/80 p-6 shadow-[0_30px_70px_rgba(37,12,97,0.45)] backdrop-blur-xl">
            <AdvancedAnalytics analytics={analytics} testResults={tests} />
          </div>
        </div>
        <div className="space-y-6">
          <div className="rounded-3xl border border-white/10 bg-[#080d1c]/90 p-6 shadow-[0_25px_60px_rgba(8,13,28,0.55)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Top Commands</p>
                <h3 className="mt-1 text-lg font-semibold text-white">High-impact suites</h3>
              </div>
              <Layers className="h-5 w-5 text-slate-400" />
            </div>
            <div className="mt-5 space-y-5">
              {topCommands.length === 0 ? (
                <p className="text-sm text-slate-400">No executions yet.</p>
              ) : (
                topCommands.map((item, index) => (
                  <div key={item.command} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-white">{item.command}</p>
                        <p className="mt-1 text-xs text-slate-400">
                          {item.total} runs • Avg {formatDuration(item.avgDuration)}
                        </p>
                      </div>
                      <span className="text-sm font-semibold text-slate-300">{index + 1}</span>
                    </div>
                    <div className="mt-4 flex items-center gap-3">
                      <div className="relative h-2 w-full overflow-hidden rounded-full bg-white/10">
                        <div
                          className="absolute inset-y-0 left-0 rounded-full bg-emerald-400"
                          style={{ width: `${Math.min(item.successRate, 100)}%` }}
                        />
                      </div>
                      <span className="text-xs font-semibold text-white">{item.successRate.toFixed(0)}%</span>
                    </div>
                    <p className="mt-2 text-[11px] uppercase tracking-[0.16em] text-slate-500">
                      Last run {formatRelativeTime(item.latestRun)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-[#050915]/90 p-6 shadow-[0_25px_60px_rgba(5,9,21,0.55)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Cohort Health</p>
                <h3 className="mt-1 text-lg font-semibold text-white">Stability leaders</h3>
              </div>
              <Sparkles className="h-5 w-5 text-purple-300" />
            </div>
            <div className="mt-5 space-y-4">
              {successLeaders.length === 0 ? (
                <p className="text-sm text-slate-400">Not enough executions yet.</p>
              ) : (
                successLeaders.map((item) => (
                  <div key={item.command} className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-white/80">
                      <ShieldCheck className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-white line-clamp-1">{item.command}</p>
                      <div className="mt-1 flex items-center gap-3 text-xs text-slate-400">
                        <span>{item.total} runs</span>
                        <span className="rounded-full border border-white/10 bg-emerald-500/10 px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] text-emerald-300">
                          {item.successRate.toFixed(1)}% pass
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-[#060a16]/90 p-6 text-center shadow-[0_25px_60px_rgba(6,10,22,0.5)]">
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Success Ratio</p>
            <h3 className="mt-1 text-lg font-semibold text-white">Portfolio Overview</h3>
            <div className="relative mx-auto mt-6 h-44 w-44">
              <div
                className="absolute inset-0 rounded-full border border-white/10 shadow-[0_15px_40px_rgba(104,67,255,0.35)]"
                style={{ background: buildGaugeGradient(successSegments) }}
              />
              <div className="absolute inset-5 flex flex-col items-center justify-center rounded-full border border-white/10 bg-[#040615]/90">
                <span className="text-3xl font-bold text-white">{analytics.successRate.toFixed(0)}%</span>
                <span className="mt-1 text-[11px] uppercase tracking-[0.2em] text-slate-400">Success</span>
                <span className="mt-2 text-xs text-slate-500">Past 7 days</span>
              </div>
            </div>
            <div className="mt-5 flex flex-wrap justify-center gap-4 text-xs text-slate-400">
              {successSegments.map((segment) => (
                <span key={segment.label} className="inline-flex items-center gap-2">
                  <span className="inline-flex h-2 w-2 rounded-full" style={{ backgroundColor: segment.color }} />
                  {segment.label}
                  <span className="text-white/80 font-semibold">
                    {analytics.total ? Math.round((segment.value / analytics.total) * 100) : 0}%
                  </span>
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 2xl:grid-cols-3">
        <div className="2xl:col-span-2 rounded-4xl border border-white/10 bg-[#050915]/85 p-6 shadow-[0_30px_70px_rgba(15,23,42,0.5)]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Live Activity</p>
              <h3 className="mt-1 text-lg font-semibold text-white">Recent executions</h3>
            </div>
            <Zap className="h-5 w-5 text-slate-400" />
          </div>
          <div className="mt-6 space-y-4">
            {resultsLoading ? (
              <>
                <div className="skeleton h-20" />
                <div className="skeleton h-20" />
                <div className="skeleton h-20" />
              </>
            ) : recentTests.length > 0 ? (
              recentTests.map((test, idx) => (
                <RecentTest key={test.test_id} test={test} delay={idx * 40} />
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
        <div className="space-y-6">
          <div className="rounded-3xl border border-white/10 bg-[#040713]/90 p-6 shadow-[0_20px_60px_rgba(4,7,19,0.5)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">System Health</p>
                <h3 className="mt-1 text-lg font-semibold text-white">Infrastructure status</h3>
              </div>
              <ShieldCheck className="h-5 w-5 text-emerald-300" />
            </div>
            {health ? (
              <div className="mt-5 space-y-4">
                <div className="flex items-center justify-between rounded-2xl border border-emerald-400/20 bg-emerald-500/10 px-4 py-3 text-emerald-200">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.18em]">Status</p>
                    <p className="text-base font-semibold text-white">{health.status}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="status-dot success" />
                    <span className="text-xs text-emerald-200/80">Operational</span>
                  </div>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-slate-400">Total Results</p>
                  <p className="mt-1 text-lg font-semibold text-white">{formatNumber(health.total_test_results)}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-slate-400">Last Check</p>
                  <p className="mt-1 font-mono text-sm text-white">
                    {new Date(health.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ) : (
              <div className="mt-6 space-y-3">
                <div className="skeleton h-16" />
                <div className="skeleton h-16" />
                <div className="skeleton h-16" />
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-white/10 bg-[#03050d]/90 p-6 shadow-[0_20px_60px_rgba(3,5,13,0.55)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Execution Pipeline</p>
                <h3 className="mt-1 text-lg font-semibold text-white">Queue distribution</h3>
              </div>
              <Clock className="h-5 w-5 text-slate-400" />
            </div>
            <div className="mt-5 space-y-4">
              {queueBreakdown.map((item) => (
                <div key={item.label}>
                  <div className="flex items-center justify-between text-sm text-slate-300">
                    <span>{item.label}</span>
                    <span className="font-semibold text-white">{formatNumber(item.value)}</span>
                  </div>
                  <div className="mt-2 h-2 rounded-full bg-white/10">
                    <div
                      className={`h-full rounded-full ${item.color}`}
                      style={{
                        width: `${
                          analytics.total ? Math.min((item.value / analytics.total) * 100, 100) : 0
                        }%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
