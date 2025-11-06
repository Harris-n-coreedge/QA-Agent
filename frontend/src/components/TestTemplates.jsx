import { useState } from 'react'
import { Save, Play, Trash2, Plus, Zap, Globe, BarChart3, TestTube, Copy } from 'lucide-react'

const DEFAULT_TEMPLATES = [
  {
    id: '1',
    name: 'Full Site Audit',
    description: 'Complete QA check including performance, security, and accessibility',
    command: 'auto check',
    websiteUrl: '',
    provider: 'google',
  },
  {
    id: '2',
    name: 'Performance Test',
    description: 'Test page load times and performance metrics',
    command: 'auto check',
    websiteUrl: '',
    provider: 'google',
  },
  {
    id: '3',
    name: 'Cross-Browser Check',
    description: 'Validate website across multiple browsers',
    command: 'cross-browser',
    websiteUrl: '',
    provider: 'google',
  },
]

export function TestTemplates({ onSelectTemplate, onRunTemplate }) {
  const [templates, setTemplates] = useState(() => {
    const saved = localStorage.getItem('testTemplates')
    return saved ? JSON.parse(saved) : DEFAULT_TEMPLATES
  })
  const [showCreate, setShowCreate] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    command: 'auto check',
    websiteUrl: '',
    provider: 'google',
  })

  const saveTemplates = (newTemplates) => {
    setTemplates(newTemplates)
    localStorage.setItem('testTemplates', JSON.stringify(newTemplates))
  }

  const handleCreate = () => {
    if (!formData.name.trim()) return

    const newTemplate = {
      id: Date.now().toString(),
      ...formData,
    }
    saveTemplates([...templates, newTemplate])
    setFormData({
      name: '',
      description: '',
      command: 'auto check',
      websiteUrl: '',
      provider: 'google',
    })
    setShowCreate(false)
  }

  const handleEdit = (template) => {
    setEditingId(template.id)
    setFormData(template)
    setShowCreate(true)
  }

  const handleUpdate = () => {
    if (!formData.name.trim()) return

    saveTemplates(
      templates.map((t) => (t.id === editingId ? { ...formData, id: editingId } : t))
    )
    setEditingId(null)
    setShowCreate(false)
    setFormData({
      name: '',
      description: '',
      command: 'auto check',
      websiteUrl: '',
      provider: 'google',
    })
  }

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this template?')) {
      saveTemplates(templates.filter((t) => t.id !== id))
    }
  }

  const handleDuplicate = (template) => {
    const duplicated = {
      ...template,
      id: Date.now().toString(),
      name: `${template.name} (Copy)`,
    }
    saveTemplates([...templates, duplicated])
  }

  const getCommandIcon = (command) => {
    switch (command) {
      case 'auto check':
        return Zap
      case 'auto audit':
        return BarChart3
      case 'cross-browser':
        return Globe
      default:
        return TestTube
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Test Templates</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Save and reuse common test configurations
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreate(true)
            setEditingId(null)
            setFormData({
              name: '',
              description: '',
              command: 'auto check',
              websiteUrl: '',
              provider: 'google',
            })
          }}
          className="btn btn-primary text-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Template</span>
        </button>
      </div>

      {/* Create/Edit Form */}
      {showCreate && (
        <div className="card p-6 space-y-4">
          <h4 className="text-base font-semibold text-slate-900 dark:text-white">
            {editingId ? 'Edit Template' : 'Create New Template'}
          </h4>
          <div className="space-y-4">
            <div>
              <label className="label">Template Name</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Production Site Check"
              />
            </div>
            <div>
              <label className="label">Description</label>
              <textarea
                className="input min-h-[80px]"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe what this template tests..."
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Command</label>
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
              <label className="label">Default Website URL (optional)</label>
              <input
                type="url"
                className="input"
                value={formData.websiteUrl}
                onChange={(e) => setFormData({ ...formData, websiteUrl: e.target.value })}
                placeholder="https://example.com"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={editingId ? handleUpdate : handleCreate}
              className="btn btn-primary"
            >
              <Save className="w-4 h-4" />
              <span>{editingId ? 'Update' : 'Create'} Template</span>
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

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.map((template) => {
          const Icon = getCommandIcon(template.command)
          return (
            <div
              key={template.id}
              className="card p-5 hover-lift group cursor-pointer"
              onClick={() => onSelectTemplate && onSelectTemplate(template)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
                    <Icon className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-slate-900 dark:text-white truncate">
                      {template.name}
                    </h4>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                      {template.description || 'No description'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDuplicate(template)
                    }}
                    className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                    title="Duplicate"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEdit(template)
                    }}
                    className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                    title="Edit"
                  >
                    <Save className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(template.id)
                    }}
                    className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-rose-600 dark:text-rose-400"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs px-2 py-1 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400">
                  {template.command}
                </span>
                {template.websiteUrl && (
                  <span className="text-xs text-slate-500 dark:text-slate-500 truncate">
                    {template.websiteUrl}
                  </span>
                )}
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onRunTemplate && onRunTemplate(template)
                }}
                className="w-full mt-3 btn btn-primary text-sm"
              >
                <Play className="w-4 h-4" />
                <span>Run Template</span>
              </button>
            </div>
          )
        })}
      </div>

      {templates.length === 0 && (
        <div className="card p-12 text-center">
          <TestTube className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No Templates Yet
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
            Create your first template to save time on repetitive tests
          </p>
          <button onClick={() => setShowCreate(true)} className="btn btn-primary">
            <Plus className="w-4 h-4" />
            <span>Create Template</span>
          </button>
        </div>
      )}
    </div>
  )
}




