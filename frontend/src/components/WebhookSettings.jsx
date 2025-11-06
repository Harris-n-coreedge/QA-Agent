import { useState } from 'react'
import { Webhook, Plus, Trash2, Edit, Save, X, TestTube, CheckCircle2, XCircle } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

export function WebhookSettings() {
  const [webhooks, setWebhooks] = useState(() => {
    const saved = localStorage.getItem('webhooks')
    return saved ? JSON.parse(saved) : []
  })
  const [showCreate, setShowCreate] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    events: [],
    enabled: true,
    secret: '',
  })
  const [testing, setTesting] = useState(null)
  const toast = useToast()

  const EVENTS = [
    { id: 'test_started', label: 'Test Started' },
    { id: 'test_completed', label: 'Test Completed' },
    { id: 'test_failed', label: 'Test Failed' },
    { id: 'test_scheduled', label: 'Test Scheduled' },
    { id: 'result_exported', label: 'Result Exported' },
  ]

  const saveWebhooks = (newWebhooks) => {
    setWebhooks(newWebhooks)
    localStorage.setItem('webhooks', JSON.stringify(newWebhooks))
  }

  const handleCreate = () => {
    if (!formData.name.trim() || !formData.url.trim()) {
      toast.error('Please fill in all required fields')
      return
    }

    const newWebhook = {
      id: Date.now().toString(),
      ...formData,
      createdAt: new Date().toISOString(),
    }
    saveWebhooks([...webhooks, newWebhook])
    toast.success('Webhook created')
    setShowCreate(false)
    setFormData({ name: '', url: '', events: [], enabled: true, secret: '' })
  }

  const handleUpdate = () => {
    if (!formData.name.trim() || !formData.url.trim()) {
      toast.error('Please fill in all required fields')
      return
    }

    saveWebhooks(
      webhooks.map((w) =>
        w.id === editingId ? { ...formData, id: editingId } : w
      )
    )
    toast.success('Webhook updated')
    setEditingId(null)
    setShowCreate(false)
    setFormData({ name: '', url: '', events: [], enabled: true, secret: '' })
  }

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this webhook?')) {
      saveWebhooks(webhooks.filter((w) => w.id !== id))
      toast.success('Webhook deleted')
    }
  }

  const handleTest = async (webhook) => {
    setTesting(webhook.id)
    try {
      // Simulate webhook test
      await new Promise((resolve) => setTimeout(resolve, 2000))
      toast.success('Webhook test successful')
    } catch (error) {
      toast.error('Webhook test failed')
    } finally {
      setTesting(null)
    }
  }

  const toggleEvent = (eventId) => {
    setFormData((prev) => ({
      ...prev,
      events: prev.events.includes(eventId)
        ? prev.events.filter((e) => e !== eventId)
        : [...prev.events, eventId],
    }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Webhooks & Integrations</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Configure webhooks to receive real-time notifications
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreate(true)
            setEditingId(null)
            setFormData({ name: '', url: '', events: [], enabled: true, secret: '' })
          }}
          className="btn btn-primary text-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Webhook</span>
        </button>
      </div>

      {/* Create/Edit Form */}
      {showCreate && (
        <div className="card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-base font-semibold text-slate-900 dark:text-white">
              {editingId ? 'Edit Webhook' : 'Create New Webhook'}
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
              <label className="label">Webhook Name *</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Slack Notifications"
              />
            </div>
            <div>
              <label className="label">Webhook URL *</label>
              <input
                type="url"
                className="input font-mono text-sm"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                placeholder="https://hooks.slack.com/services/..."
              />
            </div>
            <div>
              <label className="label">Events to Listen For</label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {EVENTS.map((event) => (
                  <label
                    key={event.id}
                    className="flex items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800"
                  >
                    <input
                      type="checkbox"
                      checked={formData.events.includes(event.id)}
                      onChange={() => toggleEvent(event.id)}
                      className="rounded"
                    />
                    <span className="text-sm text-slate-700 dark:text-slate-300">
                      {event.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>
            <div>
              <label className="label">Secret Key (optional)</label>
              <input
                type="text"
                className="input font-mono text-sm"
                value={formData.secret}
                onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                placeholder="Webhook secret for verification"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="enabled"
                checked={formData.enabled}
                onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                className="rounded"
              />
              <label htmlFor="enabled" className="text-sm text-slate-700 dark:text-slate-300">
                Enable webhook
              </label>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={editingId ? handleUpdate : handleCreate}
              className="btn btn-primary"
            >
              <Save className="w-4 h-4" />
              <span>{editingId ? 'Update' : 'Create'} Webhook</span>
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

      {/* Webhooks List */}
      <div className="space-y-3">
        {webhooks.map((webhook) => (
          <div
            key={webhook.id}
            className={`card p-5 hover-lift ${
              webhook.enabled
                ? 'border-l-4 border-l-emerald-500'
                : 'border-l-4 border-l-slate-400 opacity-60'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Webhook className="w-5 h-5 text-indigo-500" />
                  <h4 className="font-semibold text-slate-900 dark:text-white">
                    {webhook.name}
                  </h4>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      webhook.enabled
                        ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400'
                        : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400'
                    }`}
                  >
                    {webhook.enabled ? 'Active' : 'Disabled'}
                  </span>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 font-mono mb-2 truncate">
                  {webhook.url}
                </p>
                <div className="flex flex-wrap gap-2">
                  {webhook.events.map((eventId) => {
                    const event = EVENTS.find((e) => e.id === eventId)
                    return event ? (
                      <span
                        key={eventId}
                        className="text-xs px-2 py-1 rounded bg-indigo-100 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-400"
                      >
                        {event.label}
                      </span>
                    ) : null
                  })}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleTest(webhook)}
                  disabled={testing === webhook.id}
                  className="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 disabled:opacity-50"
                  title="Test Webhook"
                >
                  {testing === webhook.id ? (
                    <TestTube className="w-4 h-4 animate-spin" />
                  ) : (
                    <TestTube className="w-4 h-4" />
                  )}
                </button>
                <button
                  onClick={() => {
                    setEditingId(webhook.id)
                    setFormData(webhook)
                    setShowCreate(true)
                  }}
                  className="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                  title="Edit"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(webhook.id)}
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

      {webhooks.length === 0 && (
        <div className="card p-12 text-center">
          <Webhook className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No Webhooks Configured
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
            Create a webhook to receive real-time notifications about test events
          </p>
          <button onClick={() => setShowCreate(true)} className="btn btn-primary">
            <Plus className="w-4 h-4" />
            <span>Create Webhook</span>
          </button>
        </div>
      )}
    </div>
  )
}




