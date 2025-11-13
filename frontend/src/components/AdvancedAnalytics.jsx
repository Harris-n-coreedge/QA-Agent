import { useMemo } from 'react'
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  Clock,
  Zap,
  Target,
  Gauge,
  Flame,
} from 'lucide-react'
import { SimpleBarChart, SimpleLineChart, SimplePieChart } from './SimpleChart'
import { useTestAnalytics } from '../hooks/useTestAnalytics'

function TrendPill({ change, invert = false, format = 'percent' }) {
  if (change === undefined || change === null) {
    return null
  }

  const threshold = 0.05
  const effectiveChange = invert ? -change : change
  const isPositive = effectiveChange >= threshold
  const isNegative = effectiveChange <= -threshold

  if (!isPositive && !isNegative) {
    return (
      <span className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] uppercase tracking-wider text-slate-300">
        Stable
      </span>
    )
  }

  const Icon = isPositive ? TrendingUp : TrendingDown
  const tone = isPositive ? 'text-emerald-300 border-emerald-400/40 bg-emerald-500/15' : 'text-rose-300 border-rose-400/40 bg-rose-500/15'

  let valueLabel = ''
  if (format === 'points') {
    valueLabel = `${change > 0 ? '+' : ''}${change.toFixed(1)} pts`
  } else {
    valueLabel = `${change > 0 ? '+' : ''}${change.toFixed(1)}%`
  }

  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${tone}`}>
      <Icon className="h-[10px] w-[10px]" />
      {valueLabel}
    </span>
  )
}

function MetricCard({ icon: Icon, label, value, change, invertTrend = false, format = 'percent', accent = 'from-[#6d28d9]/80 via-[#4338ca]/70 to-[#1e1b4b]/90' }) {
  return (
    <div className={`relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br ${accent} p-5 shadow-[0_25px_60px_rgba(79,70,229,0.25)] transition-transform duration-300 hover:-translate-y-1`}>
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute -bottom-20 -right-6 h-40 w-40 rounded-full bg-purple-500/20 blur-3xl" />
        <div className="absolute -top-24 -left-16 h-44 w-44 rounded-full bg-indigo-500/10 blur-3xl" />
      </div>
      <div className="relative flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-white/60">{label}</p>
          <p className="mt-2 text-2xl font-bold text-white">{value}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/20 bg-white/10 text-white shadow-lg shadow-purple-900/30 backdrop-blur-md">
            <Icon className="h-5 w-5" />
          </div>
          <TrendPill change={change} invert={invertTrend} format={format} />
        </div>
      </div>
    </div>
  )
}

function SectionCard({ title, description, icon: Icon }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        {Icon && <Icon className="h-4 w-4 text-purple-300" />}
        <h4 className="text-sm font-semibold uppercase tracking-[0.14em] text-white/80">{title}</h4>
      </div>
      {description && <p className="text-xs text-slate-400">{description}</p>}
    </div>
  )
}

function formatRelativeTime(date) {
  if (!date) return 'No recent runs'
  const diff = Date.now() - date.getTime()
  if (diff < 60_000) return 'Moments ago'
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)} min ago`
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)} h ago`
  return `${Math.floor(diff / 86_400_000)} d ago`
}

export function AdvancedAnalytics({ testResults = [], analytics: analyticsProp }) {
  const computedAnalytics = useTestAnalytics(testResults)
  const analytics = analyticsProp ?? computedAnalytics

  const hasData = analytics && analytics.total > 0

  const statusDistribution = useMemo(() => {
    if (!analytics) return []

    return [
      { label: 'Passed', value: analytics.passed, color: '#8b5cf6' },
      { label: 'Failed', value: analytics.failed, color: '#ef4444' },
      { label: 'Running', value: analytics.running, color: '#22d3ee' },
      { label: 'Pending', value: analytics.pending, color: '#fbbf24' },
    ].filter((item) => item.value > 0)
  }, [analytics])

  const stackedTrendData = useMemo(() => {
    if (!analytics) return []
    return analytics.dailyStats.map((stat) => ({
      label: stat.label,
      value: stat.passed,
      value2: stat.failed,
    }))
  }, [analytics])

  const throughputLine = useMemo(() => {
    if (!analytics) return []
    return analytics.dailyStats.map((stat) => ({
      label: stat.label,
      value: stat.total,
    }))
  }, [analytics])

  const hourlyChartData = useMemo(() => {
    if (!analytics) return []
    return analytics.hourlyStats.map((count, hour) => ({
      label: hour % 3 === 0 ? `${hour.toString().padStart(2, '0')}:00` : '',
      value: count,
    }))
  }, [analytics])

  if (!hasData) {
    return (
      <div className="rounded-3xl border border-white/10 bg-[#0b0f1e]/80 px-8 py-16 text-center shadow-[0_20px_60px_rgba(59,7,115,0.35)]">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full border border-dashed border-white/10 bg-white/5">
          <BarChart3 className="h-7 w-7 text-slate-300" />
        </div>
        <h4 className="mt-6 text-xl font-semibold text-white">No Analytics Data</h4>
        <p className="mt-2 text-sm text-slate-400">
          Run your first automated test to unlock advanced analytics
        </p>
      </div>
    )
  }

  const summaryMetrics = [
    {
      icon: Target,
      label: 'Success Rate',
      value: `${analytics.successRate.toFixed(1)}%`,
      change: analytics.successRateDelta,
      format: 'points',
      accent: 'from-[#5b21b6]/90 via-[#2e1065]/80 to-[#111827]/95',
    },
    {
      icon: Zap,
      label: '24h Throughput',
      value: analytics.testsLast24h,
      change: analytics.throughputTrend,
      format: 'percent',
      accent: 'from-[#7c3aed]/90 via-[#3730a3]/80 to-[#0f172a]/95',
    },
    {
      icon: Clock,
      label: 'Avg Duration',
      value: analytics.avgDuration > 0 ? `${(analytics.avgDuration / 1000).toFixed(1)}s` : 'N/A',
      change: analytics.avgDurationTrend,
      invertTrend: true,
      format: 'percent',
      accent: 'from-[#4c1d95]/90 via-[#1e1b4b]/80 to-[#0b1120]/95',
    },
    {
      icon: Activity,
      label: 'Peak Hour',
      value:
        analytics.peakHour?.hour !== null
          ? `${analytics.peakHour.hour.toString().padStart(2, '0')}:00`
          : '—',
      change:
        analytics.peakHour?.count && analytics.total
          ? ((analytics.peakHour.count / analytics.total) * 100)
          : 0,
      format: 'percent',
      accent: 'from-[#6b21a8]/90 via-[#312e81]/80 to-[#1e1b4b]/95',
    },
  ]

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white">Advanced Analytics</h3>
          <p className="text-sm text-slate-400">
            Deep insights into how your autonomous QA operations are performing
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="inline-flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
            <span className="relative inline-flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400/60 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>
            Live
          </span>
          <span className="text-xs text-slate-400">
            Updated {formatRelativeTime(analytics.latestRun)}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {summaryMetrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-[#090c1a]/90 p-6 shadow-[0_30px_60px_rgba(67,56,202,0.25)]">
          <div className="pointer-events-none absolute inset-0 opacity-50">
            <div className="absolute -left-16 top-10 h-40 w-40 rounded-full bg-purple-500/15 blur-3xl" />
            <div className="absolute -bottom-20 right-0 h-48 w-48 rounded-full bg-indigo-500/10 blur-3xl" />
          </div>
          <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <SectionCard
                title="Execution Overview"
                description="Breakdown of current run distribution"
                icon={Gauge}
              />
              <div className="mt-5 flex flex-wrap gap-4">
                {statusDistribution.map((item) => (
                  <div key={item.label} className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                    {item.label}
                    <span className="text-white/70">•</span>
                    <span className="font-semibold text-white">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative flex items-center justify-center">
              <SimplePieChart data={statusDistribution} size={240} />
            </div>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-[#0a0f24]/90 p-6 shadow-[0_30px_60px_rgba(17,24,51,0.5)]">
          <div className="pointer-events-none absolute inset-0 opacity-40">
            <div className="absolute -top-16 right-2 h-40 w-40 rounded-full bg-violet-500/10 blur-3xl" />
            <div className="absolute -bottom-20 left-10 h-36 w-36 rounded-full bg-fuchsia-500/10 blur-3xl" />
          </div>
          <div className="relative">
            <SectionCard
              title="7-Day Success Balance"
              description="Passed vs failed test outcomes"
              icon={Activity}
            />
            <div className="mt-6 h-64">
              <SimpleBarChart
                data={stackedTrendData}
                colors={['#8b5cf6', '#f97316', '#22d3ee']}
              />
            </div>
            <div className="mt-4 flex items-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[#8b5cf6]" />
                Passed
              </span>
              <span className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[#f97316]" />
                Failed
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-[#0b1120]/90 p-6 shadow-[0_30px_60px_rgba(15,23,42,0.45)]">
          <div className="pointer-events-none absolute inset-0 opacity-40">
            <div className="absolute -top-16 left-4 h-36 w-36 rounded-full bg-sky-500/10 blur-3xl" />
            <div className="absolute -bottom-24 right-8 h-48 w-48 rounded-full bg-purple-500/10 blur-3xl" />
          </div>
          <div className="relative">
            <SectionCard
              title="Throughput"
              description="Tests executed each day"
              icon={Flame}
            />
            <div className="mt-6 h-64">
              <SimpleLineChart data={throughputLine} color="#38bdf8" />
            </div>
            <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
              <div>
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">Current Velocity</p>
                <p className="mt-1 text-lg font-semibold text-white">
                  {analytics.testsLast24h} / 24h
                </p>
              </div>
              <TrendPill change={analytics.throughputTrend} />
            </div>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-[#080d1c]/90 p-6 shadow-[0_25px_60px_rgba(12,10,75,0.55)]">
          <div className="pointer-events-none absolute inset-0 opacity-35">
            <div className="absolute -left-20 top-1/2 h-40 w-40 -translate-y-1/2 rounded-full bg-indigo-500/10 blur-3xl" />
            <div className="absolute -right-12 top-10 h-36 w-36 rounded-full bg-fuchsia-500/15 blur-3xl" />
          </div>
          <div className="relative">
            <SectionCard
              title="Execution Window"
              description="Hourly distribution of test runs"
              icon={Clock}
            />
            <div className="mt-6 h-64">
              <SimpleBarChart
                data={hourlyChartData}
                colors={['#6366f1', '#a855f7', '#38bdf8']}
              />
            </div>
            <div className="mt-4 text-xs text-slate-400">
              Peak concurrency at{' '}
              <span className="font-semibold text-white">
                {analytics.peakHour?.hour !== null
                  ? `${analytics.peakHour.hour.toString().padStart(2, '0')}:00`
                  : '—'}
              </span>
              , handling{' '}
              <span className="font-semibold text-white">{analytics.peakHour?.count || 0}</span>{' '}
              tests.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}