import { useState } from 'react'
import { Tag, Plus, X, Edit } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

const DEFAULT_TAGS = [
  { id: '1', name: 'Production', color: '#ef4444' },
  { id: '2', name: 'Staging', color: '#f59e0b' },
  { id: '3', name: 'Development', color: '#3b82f6' },
  { id: '4', name: 'Critical', color: '#dc2626' },
  { id: '5', name: 'Smoke Test', color: '#10b981' },
  { id: '6', name: 'Regression', color: '#8b5cf6' },
]

export function TestTags({ testId, selectedTags = [], onTagsChange }) {
  const [tags, setTags] = useState(() => {
    const saved = localStorage.getItem('testTags')
    return saved ? JSON.parse(saved) : DEFAULT_TAGS
  })
  const [showCreate, setShowCreate] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [newTagColor, setNewTagColor] = useState('#3b82f6')
  const toast = useToast()

  const saveTags = (newTags) => {
    setTags(newTags)
    localStorage.setItem('testTags', JSON.stringify(newTags))
  }

  const handleCreateTag = () => {
    if (!newTagName.trim()) {
      toast.error('Please enter a tag name')
      return
    }

    const newTag = {
      id: Date.now().toString(),
      name: newTagName.trim(),
      color: newTagColor,
    }
    saveTags([...tags, newTag])
    setNewTagName('')
    setNewTagColor('#3b82f6')
    setShowCreate(false)
    toast.success('Tag created')
  }

  const handleToggleTag = (tagId) => {
    const newSelected = selectedTags.includes(tagId)
      ? selectedTags.filter((id) => id !== tagId)
      : [...selectedTags, tagId]
    
    if (onTagsChange) {
      onTagsChange(newSelected)
    }
  }

  const handleDeleteTag = (tagId) => {
    if (window.confirm('Delete this tag? It will be removed from all tests.')) {
      saveTags(tags.filter((t) => t.id !== tagId))
      toast.success('Tag deleted')
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="label">Tags</label>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Create Tag Form */}
      {showCreate && (
        <div className="card p-4 space-y-3">
          <input
            type="text"
            className="input"
            placeholder="Tag name"
            value={newTagName}
            onChange={(e) => setNewTagName(e.target.value)}
          />
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={newTagColor}
              onChange={(e) => setNewTagColor(e.target.value)}
              className="w-12 h-10 rounded border border-slate-300 dark:border-slate-600 cursor-pointer"
            />
            <button onClick={handleCreateTag} className="btn btn-primary flex-1 text-sm">
              Create Tag
            </button>
            <button
              onClick={() => {
                setShowCreate(false)
                setNewTagName('')
              }}
              className="btn btn-secondary text-sm"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Tags List */}
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => {
          const isSelected = selectedTags.includes(tag.id)
          return (
            <button
              key={tag.id}
              onClick={() => handleToggleTag(tag.id)}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${
                  isSelected
                    ? 'bg-slate-800 dark:bg-slate-700 text-white border-2 border-slate-900 dark:border-slate-600'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-600 hover:border-slate-400 dark:hover:border-slate-500'
                }
              `}
              style={{
                backgroundColor: isSelected ? tag.color : undefined,
                borderColor: isSelected ? tag.color : undefined,
              }}
            >
              <Tag className="w-3 h-3" />
              <span>{tag.name}</span>
              {isSelected && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteTag(tag.id)
                  }}
                  className="ml-1 p-0.5 rounded hover:bg-white/20"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export function TagFilter({ tags, selectedTags, onTagsChange }) {
  return (
    <div className="space-y-2">
      <label className="label">Filter by Tags</label>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => {
          const isSelected = selectedTags.includes(tag.id)
          return (
            <button
              key={tag.id}
              onClick={() => {
                const newSelected = isSelected
                  ? selectedTags.filter((id) => id !== tag.id)
                  : [...selectedTags, tag.id]
                onTagsChange(newSelected)
              }}
              className={`
                px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${
                  isSelected
                    ? 'bg-indigo-100 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-400 border-2 border-indigo-500'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-600 hover:border-slate-400 dark:hover:border-slate-500'
                }
              `}
            >
              <Tag className="w-3 h-3 inline mr-1" />
              {tag.name}
            </button>
          )
        })}
      </div>
    </div>
  )
}




