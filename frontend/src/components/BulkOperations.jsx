import { useState } from 'react'
import { CheckSquare, Square, Play, Trash2, Download, FileText, X } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

export function BulkOperations({ items = [], onBulkAction, itemLabel = 'item' }) {
  const [selectedItems, setSelectedItems] = useState([])
  const [showBulkMenu, setShowBulkMenu] = useState(false)
  const toast = useToast()

  const toggleSelectAll = () => {
    if (selectedItems.length === items.length) {
      setSelectedItems([])
    } else {
      setSelectedItems(items.map((item) => item.id || item.test_id))
    }
  }

  const toggleSelectItem = (id) => {
    setSelectedItems((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    )
  }

  const handleBulkAction = (action) => {
    if (selectedItems.length === 0) {
      toast.warning(`Please select at least one ${itemLabel}`)
      return
    }

    if (onBulkAction) {
      onBulkAction(action, selectedItems)
      setSelectedItems([])
      setShowBulkMenu(false)
      toast.success(`Bulk ${action} completed for ${selectedItems.length} ${itemLabel}(s)`)
    }
  }

  if (items.length === 0) return null

  return (
    <div className="space-y-4">
      {/* Bulk Actions Bar */}
      {selectedItems.length > 0 && (
        <div className="card p-4 bg-indigo-50 dark:bg-indigo-500/10 border-indigo-200 dark:border-indigo-500/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-indigo-900 dark:text-indigo-300">
                {selectedItems.length} {itemLabel}(s) selected
              </span>
              <button
                onClick={() => setSelectedItems([])}
                className="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
              >
                Clear selection
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowBulkMenu(!showBulkMenu)}
                className="btn btn-primary text-sm"
              >
                Actions
              </button>
              {showBulkMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 py-2 z-50">
                  <button
                    onClick={() => handleBulkAction('run')}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    Run Selected
                  </button>
                  <button
                    onClick={() => handleBulkAction('export')}
                    className="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Export Selected
                  </button>
                  <button
                    onClick={() => handleBulkAction('delete')}
                    className="w-full text-left px-4 py-2 text-sm text-rose-600 dark:text-rose-400 hover:bg-slate-100 dark:hover:bg-slate-700 flex items-center gap-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Selected
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Select All Checkbox */}
      <div className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50">
        <button
          onClick={toggleSelectAll}
          className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
        >
          {selectedItems.length === items.length ? (
            <CheckSquare className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          ) : (
            <Square className="w-5 h-5" />
          )}
          <span>Select All ({items.length})</span>
        </button>
      </div>
    </div>
  )
}

export function SelectableItem({ item, isSelected, onToggle, children }) {
  return (
    <div
      className={`relative group ${
        isSelected ? 'ring-2 ring-indigo-500 rounded-lg' : ''
      }`}
    >
      <button
        onClick={() => onToggle(item.id || item.test_id)}
        className={`absolute top-2 left-2 z-10 p-1 rounded ${
          isSelected
            ? 'bg-indigo-500 text-white'
            : 'bg-white dark:bg-slate-800 text-slate-400 opacity-0 group-hover:opacity-100'
        } transition-opacity`}
      >
        {isSelected ? (
          <CheckSquare className="w-4 h-4" />
        ) : (
          <Square className="w-4 h-4" />
        )}
      </button>
      {children}
    </div>
  )
}




