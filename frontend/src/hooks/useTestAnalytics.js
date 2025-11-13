import { useMemo } from 'react'

const STATUS_PASSED = new Set(['passed', 'completed'])
const STATUS_FAILED = 'failed'
const STATUS_RUNNING = 'running'
const STATUS_PENDING = 'pending'

function toDateKey(value) {
  if (!value) return ''
  try {
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return ''
    return date.toISOString().split('T')[0]
  } catch (error) {
    return ''
  }
}

export function useTestAnalytics(testResults = []) {
  return useMemo(() => {
    const safeResults = Array.isArray(testResults) ? testResults : []

    if (safeResults.length === 0) {
      return {
        total: 0,
        passed: 0,
        failed: 0,
        running: 0,
        pending: 0,
        completed: 0,
        successRate: 0,
        successRateDelta: 0,
        avgDuration: 0,
        avgDurationTrend: 0,
        avgLoadTime: 0,
        throughputTrend: 0,
        testsLast24h: 0,
        testsPrev24h: 0,
        dailyStats: [],
        hourlyStats: Array.from({ length: 24 }, () => 0),
        testTypes: {},
        topCommands: [],
        commandSuccessLeaders: [],
        peakHour: { hour: null, count: 0 },
        latestRun: null,
      }
    }

    const now = Date.now()
    const MS_IN_DAY = 24 * 60 * 60 * 1000

    const counts = {
      total: safeResults.length,
      passed: 0,
      failed: 0,
      running: 0,
      pending: 0,
      completed: 0,
    }

    const commandMap = new Map()
    const testTypes = {}
    const hourlyStats = Array.from({ length: 24 }, () => 0)
    const durationValues = []
    const performanceValues = []
    let latestRun = null

    safeResults.forEach((test) => {
      const status = test?.status || ''
      if (STATUS_PASSED.has(status)) {
        counts.passed += 1
        counts.completed += 1
      } else if (status === STATUS_FAILED) {
        counts.failed += 1
        counts.completed += 1
      } else if (status === STATUS_RUNNING) {
        counts.running += 1
      } else if (status === STATUS_PENDING) {
        counts.pending += 1
      }

      const startedAt = test?.started_at ? new Date(test.started_at) : null
      if (startedAt && !Number.isNaN(startedAt.getTime())) {
        const hour = startedAt.getHours()
        hourlyStats[hour] = (hourlyStats[hour] || 0) + 1

        if (!latestRun || startedAt > latestRun) {
          latestRun = startedAt
        }
      }

      if (typeof test?.duration_ms === 'number') {
        durationValues.push(test.duration_ms)
      }

      const performance = test?.performance_metrics || test?.performance
      if (performance) {
        const loadTime = performance.load_time || performance.loadTime
        if (typeof loadTime === 'number') {
          performanceValues.push(loadTime)
        }
      }

      const cmd = (test?.command || 'Unlabelled Test').trim()
      if (!commandMap.has(cmd)) {
        commandMap.set(cmd, {
          command: cmd,
          total: 0,
          passed: 0,
          failed: 0,
          durations: [],
          latestRun: startedAt,
        })
      }
      const cmdStats = commandMap.get(cmd)
      cmdStats.total += 1
      if (STATUS_PASSED.has(status)) cmdStats.passed += 1
      if (status === STATUS_FAILED) cmdStats.failed += 1
      if (typeof test?.duration_ms === 'number') {
        cmdStats.durations.push(test.duration_ms)
      }
      if (startedAt && (!cmdStats.latestRun || startedAt > cmdStats.latestRun)) {
        cmdStats.latestRun = startedAt
      }

      const lowerCommand = cmd.toLowerCase()
      let type = 'Other'
      if (lowerCommand.includes('regression')) type = 'Regression'
      else if (lowerCommand.includes('smoke')) type = 'Smoke'
      else if (lowerCommand.includes('mobile')) type = 'Mobile'
      else if (lowerCommand.includes('browser')) type = 'Browser'
      else if (lowerCommand.includes('api')) type = 'API'
      else if (lowerCommand.includes('audit')) type = 'Audit'
      else if (lowerCommand.includes('auto check')) type = 'Auto Check'
      else if (lowerCommand.includes('cross-browser')) type = 'Cross Browser'

      testTypes[type] = (testTypes[type] || 0) + 1
    })

    const avgDuration =
      durationValues.length > 0
        ? durationValues.reduce((sum, value) => sum + value, 0) / durationValues.length
        : 0

    const avgLoadTime =
      performanceValues.length > 0
        ? performanceValues.reduce((sum, value) => sum + value, 0) / performanceValues.length
        : 0

    const successRate = counts.total > 0 ? (counts.passed / counts.total) * 100 : 0

    const last7Days = Array.from({ length: 7 }, (_, offset) => {
      const date = new Date()
      date.setDate(date.getDate() - (6 - offset))
      const key = date.toISOString().split('T')[0]
      return { key, date }
    })

    const dailyMap = new Map(last7Days.map(({ key }) => [key, { total: 0, passed: 0, failed: 0 }]))

    safeResults.forEach((test) => {
      const dateKey = toDateKey(test?.started_at)
      if (!dateKey || !dailyMap.has(dateKey)) return

      const stat = dailyMap.get(dateKey)
      stat.total += 1
      if (STATUS_PASSED.has(test?.status)) stat.passed += 1
      else if (test?.status === STATUS_FAILED) stat.failed += 1
    })

    const dailyStats = last7Days.map(({ key, date }) => {
      const stat = dailyMap.get(key) || { total: 0, passed: 0, failed: 0 }
      return {
        date: key,
        total: stat.total,
        passed: stat.passed,
        failed: stat.failed,
        label: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      }
    })

    const lastDay = dailyStats[dailyStats.length - 1]
    const prevDay = dailyStats[dailyStats.length - 2]

    const lastDayRate =
      lastDay && lastDay.total > 0 ? (lastDay.passed / lastDay.total) * 100 : successRate
    const prevDayRate =
      prevDay && prevDay.total > 0 ? (prevDay.passed / prevDay.total) * 100 : lastDayRate
    const successRateDelta = lastDayRate - prevDayRate

    const lastDayDurationValues = safeResults
      .filter((test) => toDateKey(test?.started_at) === lastDay?.date && typeof test?.duration_ms === 'number')
      .map((test) => test.duration_ms)

    const prevDayDurationValues = safeResults
      .filter((test) => toDateKey(test?.started_at) === prevDay?.date && typeof test?.duration_ms === 'number')
      .map((test) => test.duration_ms)

    const lastDayAvgDuration =
      lastDayDurationValues.length > 0
        ? lastDayDurationValues.reduce((sum, value) => sum + value, 0) / lastDayDurationValues.length
        : avgDuration

    const prevDayAvgDuration =
      prevDayDurationValues.length > 0
        ? prevDayDurationValues.reduce((sum, value) => sum + value, 0) / (prevDayDurationValues.length || 1)
        : lastDayAvgDuration

    const avgDurationTrend =
      prevDayAvgDuration === 0
        ? 0
        : ((lastDayAvgDuration - prevDayAvgDuration) / Math.max(prevDayAvgDuration, 1)) * 100

    const testsLast24h = safeResults.filter((test) => {
      const startedAt = test?.started_at ? new Date(test.started_at) : null
      if (!startedAt || Number.isNaN(startedAt.getTime())) return false
      return now - startedAt.getTime() <= MS_IN_DAY
    }).length

    const testsPrev24h = safeResults.filter((test) => {
      const startedAt = test?.started_at ? new Date(test.started_at) : null
      if (!startedAt || Number.isNaN(startedAt.getTime())) return false
      const diff = now - startedAt.getTime()
      return diff > MS_IN_DAY && diff <= MS_IN_DAY * 2
    }).length

    const throughputTrend =
      testsPrev24h === 0 ? 0 : ((testsLast24h - testsPrev24h) / Math.max(testsPrev24h, 1)) * 100

    const commandStats = Array.from(commandMap.values()).map((stats) => {
      const avg = stats.durations.length
        ? stats.durations.reduce((sum, value) => sum + value, 0) / stats.durations.length
        : 0
      const success = stats.total > 0 ? (stats.passed / stats.total) * 100 : 0
      return {
        ...stats,
        avgDuration: avg,
        successRate: success,
      }
    })

    const topCommands = [...commandStats]
      .sort((a, b) => b.total - a.total)
      .slice(0, 5)

    const commandSuccessLeaders = [...commandStats]
      .filter((item) => item.total >= 2)
      .sort((a, b) => b.successRate - a.successRate)
      .slice(0, 4)

    const peakHourIndex = hourlyStats.reduce(
      (acc, value, idx) => {
        if (value > acc.count) {
          return { hour: idx, count: value }
        }
        return acc
      },
      { hour: 0, count: hourlyStats[0] || 0 }
    )

    return {
      total: counts.total,
      passed: counts.passed,
      failed: counts.failed,
      running: counts.running,
      pending: counts.pending,
      completed: counts.completed,
      successRate,
      successRateDelta,
      avgDuration,
      avgDurationTrend,
      avgLoadTime,
      throughputTrend,
      testsLast24h,
      testsPrev24h,
      dailyStats,
      hourlyStats,
      testTypes,
      topCommands,
      commandSuccessLeaders,
      peakHour: peakHourIndex,
      latestRun,
    }
  }, [testResults])
}


