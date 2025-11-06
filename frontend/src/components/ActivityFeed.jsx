import { useState, useMemo } from 'react'
import { Activity, Zap, CheckCircle2, XCircle, Clock, FileText, Settings, User, Calendar } from 'lucide-react'

const ACTIVITY_TYPES = {
  test_started: { icon: Zap, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-500/10' },
  test_completed: { icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-500/10' },
  test_failed: { icon: XCircle, color: 'text-rose-500', bg: 'bg-rose-50 dark:bg-rose-500/10' },
  test_pending: { icon: Clock, color: 'text-amber-500', bg: 'bg-amber-50 dark:bg-amber-500/10' },
  result_exported: { icon: FileText, color: 'text-indigo-500', bg: 'bg-indigo-50 dark:bg-indigo-500/10' },
  settings_changed: { icon: Settings, color: 'text-slate-500', bg: 'bg-slate-50 dark:bg-slate-700' },
  user_action: { icon: User, color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-500/10' },
}

export function ActivityFeed({ activities = [], limit = 50 }) {
  const [filter, setFilter] = useState('all')

  const filteredActivities = useMemo(() => {
    let filtered = activities
    if (filter !== 'all') {
      filtered = filtered.filter((a) => a.type === filter)
    }
    return filtered.slice(0, limit)
  }, [activities, filter, limit])

  const groupedActivities = useMemo(() => {
    const groups = {}
    filteredActivities.forEach((activity) => {
      const date = new Date(activity.timestamp).toLocaleDateString()
      if (!groups[date]) {
        groups[date] = []
      }
      groups[date].push(activity)
    })
    return groups
  }, [filteredActivities])

  const getActivityIcon = (type) => {
    const config = ACTIVITY_TYPES[type] || ACTIVITY_TYPES.user_action
    const Icon = config.icon
    return { Icon, config }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Activity Feed</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Recent activity and events
          </p>
        </div>
        <select
          className="input text-sm"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="all">All Activity</option>
          <option value="test_started">Tests Started</option>
          <option value="test_completed">Tests Completed</option>
          <option value="test_failed">Tests Failed</option>
          <option value="result_exported">Exports</option>
          <option value="settings_changed">Settings</option>
        </select>
      </div>

      <div className="space-y-6">
        {Object.entries(groupedActivities).length === 0 ? (
          <div className="card p-12 text-center">
            <Activity className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              No Activity Yet
            </h4>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Activity will appear here as you use the platform
            </p>
          </div>
        ) : (
          Object.entries(groupedActivities).map(([date, dayActivities]) => (
            <div key={date} className="space-y-4">
              <div className="flex items-center gap-3">
                <Calendar className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                <h4 className="text-sm font-semibold text-slate-600 dark:text-slate-400">
                  {date}
                </h4>
              </div>
              <div className="space-y-3">
                {dayActivities.map((activity) => {
                  const { Icon, config } = getActivityIcon(activity.type)
                  return (
                    <div
                      key={activity.id}
                      className="card p-4 hover-lift"
                    >
                      <div className="flex items-start gap-4">
                        <div className={`flex-shrink-0 p-2.5 rounded-lg ${config.bg}`}>
                          <Icon className={`w-5 h-5 ${config.color}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-slate-900 dark:text-white mb-1">
                            {activity.title}
                          </p>
                          {activity.description && (
                            <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                              {activity.description}
                            </p>
                          )}
                          <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-500">
                            <span>{new Date(activity.timestamp).toLocaleTimeString()}</span>
                            {activity.user && (
                              <span className="flex items-center gap-1">
                                <User className="w-3 h-3" />
                                {activity.user}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

// Generate activity from test result
export function generateActivityFromTest(test) {
  let type = 'test_pending'
  let title = 'Test Started'
  
  if (test.status === 'passed' || test.status === 'completed') {
    type = 'test_completed'
    title = 'Test Completed Successfully'
  } else if (test.status === 'failed') {
    type = 'test_failed'
    title = 'Test Failed'
  } else if (test.status === 'running') {
    type = 'test_started'
    title = 'Test Started Running'
  }

  return {
    id: `test-${test.test_id}`,
    type,
    title,
    description: `Test: ${test.command || 'Unknown'}`,
    timestamp: test.started_at || new Date().toISOString(),
    user: 'Current User',
    metadata: {
      testId: test.test_id,
      command: test.command,
      status: test.status,
    },
  }
}




