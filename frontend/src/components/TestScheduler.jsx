import { useState, useEffect } from 'react'
import { Clock, Calendar, Play, Pause, Trash2, Edit, Save, X, Repeat, Zap } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

const FREQUENCY_OPTIONS = [
  { value: 'once', label: 'Once', icon: Clock },
  { value: 'hourly', label: 'Every Hour', cron: '0 * * * *' },
  { value: 'daily', label: 'Daily', cron: '0 0 * * *' },
  { value: 'weekly', label: 'Weekly', cron: '0 0 * * 0' },
  { value: 'monthly', label: 'Monthly', cron: '0 0 1 * *' },
  { value: 'custom', label: 'Custom Cron', cron: '' },
]

export function TestScheduler({ onScheduleTest }) {
  const [schedules, setSchedules] = useState(() => {
    const saved = localStorage.getItem('testSchedules')
    return saved ? JSON.parse(saved) : []
  })
  const [showCreate, setShowCreate] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    websiteUrl: '',
    command: 'auto check',
    provider: 'google',
    frequency: 'daily',
    cronExpression: '0 0 * * *',
    enabled: true,
    nextRun: null,
  })
  const toast = useToast()

  const calculateNextRun = (cron) => {
    // Simple next run calculation (in production, use a proper cron parser)
    const now = new Date()
    const next = new Date(now)
    
    if (cron === '0 * * * *') {
      next.setHours(next.getHours() + 1, 0, 0, 0)
    } else if (cron === '0 0 * * *') {
      next.setDate(next.getDate() + 1)
      next.setHours(0, 0, 0, 0)
    } else if (cron === '0 0 * * 0') {
      const daysUntilSunday = (7 - next.getDay()) % 7 || 7
      next.setDate(next.getDate() + daysUntilSunday)
      next.setHours(0, 0, 0, 0)
    } else if (cron === '0 0 1 * *') {
      next.setMonth(next.getMonth() + 1, 1)
      next.setHours(0, 0, 0, 0)
    } else {
      next.setDate(next.getDate() + 1)
    }
    
    return next
  }

  const saveSchedules = (newSchedules) => {
    setSchedules(newSchedules)
    localStorage.setItem('testSchedules', JSON.stringify(newSchedules))
  }

  const handleCreate = () => {
    if (!formData.name.trim() || !formData.websiteUrl.trim()) {
      toast.error('Please fill in all required fields')
      return
    }

    const frequencyOption = FREQUENCY_OPTIONS.find(f => f.value === formData.frequency)
    const cron = formData.frequency === 'custom' 
      ? formData.cronExpression 
      : (frequencyOption?.cron || '0 0 * * *')

    const newSchedule = {
      id: Date.now().toString(),
      ...formData,
      cronExpression: cron,
      nextRun: calculateNextRun(cron).toISOString(),
      createdAt: new Date().toISOString(),
    }
    
    saveSchedules([...schedules, newSchedule])
    toast.success('Test schedule created successfully')
    setShowCreate(false)
    setFormData({
      name: '',
      description: '',
      websiteUrl: '',
      command: 'auto check',
      provider: 'google',
      frequency: 'daily',
      cronExpression: '0 0 * * *',
      enabled: true,
      nextRun: null,
    })
  }

  const handleUpdate = () => {
    if (!formData.name.trim() || !formData.websiteUrl.trim()) {
      toast.error('Please fill in all required fields')
      return
    }

    const frequencyOption = FREQUENCY_OPTIONS.find(f => f.value === formData.frequency)
    const cron = formData.frequency === 'custom' 
      ? formData.cronExpression 
      : (frequencyOption?.cron || '0 0 * * *')

    saveSchedules(
      schedules.map((s) =>
        s.id === editingId
          ? {
              ...formData,
              cronExpression: cron,
              nextRun: calculateNextRun(cron).toISOString(),
            }
          : s
      )
    )
    toast.success('Schedule updated successfully')
    setEditingId(null)
    setShowCreate(false)
    setFormData({
      name: '',
      description: '',
      websiteUrl: '',
      command: 'auto check',
      provider: 'google',
      frequency: 'daily',
      cronExpression: '0 0 * * *',
      enabled: true,
      nextRun: null,
    })
  }

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this schedule?')) {
      saveSchedules(schedules.filter((s) => s.id !== id))
      toast.success('Schedule deleted')
    }
  }

  const handleToggle = (id) => {
    saveSchedules(
      schedules.map((s) =>
        s.id === id ? { ...s, enabled: !s.enabled } : s
      )
    )
    toast.info(
      schedules.find((s) => s.id === id)?.enabled
        ? 'Schedule paused'
        : 'Schedule enabled'
    )
  }

  const handleRunNow = (schedule) => {
    if (onScheduleTest) {
      onScheduleTest({
        websiteUrl: schedule.websiteUrl,
        command: schedule.command,
        provider: schedule.provider,
      })
      toast.success(`Running scheduled test: ${schedule.name}`)
    }
  }

  const handleEdit = (schedule) => {
    setEditingId(schedule.id)
    setFormData(schedule)
    setShowCreate(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Scheduled Tests</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Automate your tests to run at specific intervals
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreate(true)
            setEditingId(null)
            setFormData({
              name: '',
              description: '',
              websiteUrl: '',
              command: 'auto check',
              provider: 'google',
              frequency: 'daily',
              cronExpression: '0 0 * * *',
              enabled: true,
              nextRun: null,
            })
          }}
          className="btn btn-primary text-sm"
        >
          <Calendar className="w-4 h-4" />
          <span>New Schedule</span>
        </button>
      </div>

      {/* Create/Edit Form */}
      {showCreate && (
        <div className="card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-base font-semibold text-slate-900 dark:text-white">
              {editingId ? 'Edit Schedule' : 'Create New Schedule'}
            </h4>
            <button
              onClick={() => {
                setShowCreate(false)
                setEditingId(null)
              }}
              className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              <X className="w-5 h-5 text-slate-500" />
            </button>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="label">Schedule Name *</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Daily Production Check"
              />
            </div>
            <div>
              <label className="label">Description</label>
              <textarea
                className="input min-h-[80px]"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe this scheduled test..."
              />
            </div>
            <div>
              <label className="label">Website URL *</label>
              <input
                type="url"
                className="input"
                value={formData.websiteUrl}
                onChange={(e) => setFormData({ ...formData, websiteUrl: e.target.value })}
                placeholder="https://example.com"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Test Command</label>
                <select
                  className="input"
                  value={formData.command}
                  onChange={(e) => setFormData({ ...formData, command: e.target.value })}
                >
                  <option value="auto check">Auto Check</option>
                  <option value="auto audit">Auto Audit</option>
                  <option value="cross-browser">Cross-Browser</option>
                </select>
              </div>
              <div>
                <label className="label">Provider</label>
                <select
                  className="input"
                  value={formData.provider}
                  onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="google">Google</option>
                </select>
              </div>
            </div>
            <div>
              <label className="label">Frequency</label>
              <select
                className="input"
                value={formData.frequency}
                onChange={(e) => {
                  const freq = e.target.value
                  const option = FREQUENCY_OPTIONS.find((f) => f.value === freq)
                  setFormData({
                    ...formData,
                    frequency: freq,
                    cronExpression: option?.cron || formData.cronExpression,
                  })
                }}
              >
                {FREQUENCY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            {formData.frequency === 'custom' && (
              <div>
                <label className="label">Cron Expression *</label>
                <input
                  type="text"
                  className="input font-mono text-sm"
                  value={formData.cronExpression}
                  onChange={(e) => setFormData({ ...formData, cronExpression: e.target.value })}
                  placeholder="0 0 * * *"
                />
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Format: minute hour day month weekday
                </p>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={editingId ? handleUpdate : handleCreate}
              className="btn btn-primary"
            >
              <Save className="w-4 h-4" />
              <span>{editingId ? 'Update' : 'Create'} Schedule</span>
            </button>
            <button
              onClick={() => {
                setShowCreate(false)
                setEditingId(null)
              }}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Schedules List */}
      <div className="space-y-3">
        {schedules.map((schedule) => (
          <div
            key={schedule.id}
            className={`card p-5 hover-lift ${
              schedule.enabled
                ? 'border-l-4 border-l-indigo-500'
                : 'opacity-60 border-l-4 border-l-slate-400'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h4 className="font-semibold text-slate-900 dark:text-white">
                    {schedule.name}
                  </h4>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      schedule.enabled
                        ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    {schedule.enabled ? 'Active' : 'Paused'}
                  </span>
                </div>
                {schedule.description && (
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">
                    {schedule.description}
                  </p>
                )}
                <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Zap className="w-4 h-4" />
                    <span>{schedule.command}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Repeat className="w-4 h-4" />
                    <span>
                      {FREQUENCY_OPTIONS.find((f) => f.value === schedule.frequency)?.label ||
                        schedule.cronExpression}
                    </span>
                  </div>
                  {schedule.nextRun && (
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-4 h-4" />
                      <span>
                        Next: {new Date(schedule.nextRun).toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleRunNow(schedule)}
                  className="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                  title="Run Now"
                >
                  <Play className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleToggle(schedule.id)}
                  className={`p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-700 ${
                    schedule.enabled
                      ? 'text-amber-600 dark:text-amber-400'
                      : 'text-emerald-600 dark:text-emerald-400'
                  }`}
                  title={schedule.enabled ? 'Pause' : 'Enable'}
                >
                  {schedule.enabled ? (
                    <Pause className="w-4 h-4" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={() => handleEdit(schedule)}
                  className="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                  title="Edit"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(schedule.id)}
                  className="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-rose-600 dark:text-rose-400"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {schedules.length === 0 && (
        <div className="card p-12 text-center">
          <Calendar className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No Scheduled Tests
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
            Create a schedule to automatically run tests at specified intervals
          </p>
          <button onClick={() => setShowCreate(true)} className="btn btn-primary">
            <Calendar className="w-4 h-4" />
            <span>Create Schedule</span>
          </button>
        </div>
      )}
    </div>
  )
}




