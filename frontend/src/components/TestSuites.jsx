import { useState } from 'react'
import { FolderOpen, Play, Plus, Trash2, Edit, Save, X, Copy, CheckCircle2, Clock } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

export function TestSuites({ onRunSuite }) {
  const [suites, setSuites] = useState(() => {
    const saved = localStorage.getItem('testSuites')
    return saved ? JSON.parse(saved) : []
  })
  const [showCreate, setShowCreate] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    tests: [],
  })
  const toast = useToast()

  const saveSuites = (newSuites) => {
    setSuites(newSuites)
    localStorage.setItem('testSuites', JSON.stringify(newSuites))
  }

  const handleCreate = () => {
    if (!formData.name.trim()) {
      toast.error('Please enter a suite name')
      return
    }

    const newSuite = {
      id: Date.now().toString(),
      ...formData,
      createdAt: new Date().toISOString(),
      lastRun: null,
    }
    saveSuites([...suites, newSuite])
    toast.success('Test suite created')
    setShowCreate(false)
    setFormData({ name: '', description: '', tests: [] })
  }

  const handleUpdate = () => {
    if (!formData.name.trim()) {
      toast.error('Please enter a suite name')
      return
    }

    saveSuites(
      suites.map((s) =>
        s.id === editingId ? { ...formData, id: editingId } : s
      )
    )
    toast.success('Test suite updated')
    setEditingId(null)
    setShowCreate(false)
    setFormData({ name: '', description: '', tests: [] })
  }

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this test suite?')) {
      saveSuites(suites.filter((s) => s.id !== id))
      toast.success('Test suite deleted')
    }
  }

  const handleDuplicate = (suite) => {
    const duplicated = {
      ...suite,
      id: Date.now().toString(),
      name: `${suite.name} (Copy)`,
      createdAt: new Date().toISOString(),
    }
    saveSuites([...suites, duplicated])
    toast.success('Test suite duplicated')
  }

  const handleRunSuite = (suite) => {
    if (onRunSuite) {
      onRunSuite(suite)
      saveSuites(
        suites.map((s) =>
          s.id === suite.id
            ? { ...s, lastRun: new Date().toISOString() }
            : s
        )
      )
      toast.success(`Running test suite: ${suite.name}`)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Test Suites</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Group and run multiple tests together
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreate(true)
            setEditingId(null)
            setFormData({ name: '', description: '', tests: [] })
          }}
          className="btn btn-primary text-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Suite</span>
        </button>
      </div>

      {/* Create/Edit Form */}
      {showCreate && (
        <div className="card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-base font-semibold text-slate-900 dark:text-white">
              {editingId ? 'Edit Test Suite' : 'Create New Test Suite'}
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
              <label className="label">Suite Name *</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Production Smoke Tests"
              />
            </div>
            <div>
              <label className="label">Description</label>
              <textarea
                className="input min-h-[80px]"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe what this suite tests..."
              />
            </div>
            <div>
              <label className="label">Tests in Suite</label>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">
                {formData.tests.length} test(s) added
              </p>
              <div className="space-y-2">
                {formData.tests.map((test, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-white">
                        {test.name || test.command || 'Test'}
                      </p>
                      {test.websiteUrl && (
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {test.websiteUrl}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => {
                        setFormData({
                          ...formData,
                          tests: formData.tests.filter((_, i) => i !== index),
                        })
                      }}
                      className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-rose-600 dark:text-rose-400"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
                Add tests from templates or create new ones
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={editingId ? handleUpdate : handleCreate}
              className="btn btn-primary"
            >
              <Save className="w-4 h-4" />
              <span>{editingId ? 'Update' : 'Create'} Suite</span>
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

      {/* Suites Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {suites.map((suite) => (
          <div
            key={suite.id}
            className="card p-5 hover-lift group cursor-pointer"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
                  <FolderOpen className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-slate-900 dark:text-white truncate">
                    {suite.name}
                  </h4>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                    {suite.description || 'No description'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDuplicate(suite)
                  }}
                  className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                  title="Duplicate"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setEditingId(suite.id)
                    setFormData(suite)
                    setShowCreate(true)
                  }}
                  className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                  title="Edit"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDelete(suite.id)
                  }}
                  className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-rose-600 dark:text-rose-400"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-4 text-xs text-slate-600 dark:text-slate-400">
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  {suite.tests.length} test(s)
                </span>
                {suite.lastRun && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(suite.lastRun).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation()
                handleRunSuite(suite)
              }}
              className="w-full btn btn-primary text-sm"
            >
              <Play className="w-4 h-4" />
              <span>Run Suite</span>
            </button>
          </div>
        ))}
      </div>

      {suites.length === 0 && (
        <div className="card p-12 text-center">
          <FolderOpen className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No Test Suites Yet
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
            Create your first test suite to group and run multiple tests together
          </p>
          <button onClick={() => setShowCreate(true)} className="btn btn-primary">
            <Plus className="w-4 h-4" />
            <span>Create Suite</span>
          </button>
        </div>
      )}
    </div>
  )
}




