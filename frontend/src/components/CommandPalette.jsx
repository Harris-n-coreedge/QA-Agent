import { useEffect, useState, useMemo } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Search, Home, TestTube, Globe, List, Settings, Zap, FileText, BarChart3 } from 'lucide-react'

const COMMANDS = [
  { id: 'dashboard', label: 'Go to Dashboard', icon: Home, path: '/' },
  { id: 'quick-test', label: 'Quick Test', icon: Zap, path: '/quick-test' },
  { id: 'browser-use', label: 'Browser Use', icon: Globe, path: '/browser-use' },
  { id: 'results', label: 'Test Results', icon: List, path: '/results' },
  { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
]

export function CommandPalette({ isOpen, onClose }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const navigate = useNavigate()
  const location = useLocation()

  const filteredCommands = useMemo(() => {
    if (!searchQuery.trim()) return COMMANDS
    const query = searchQuery.toLowerCase()
    return COMMANDS.filter(
      (cmd) =>
        cmd.label.toLowerCase().includes(query) ||
        cmd.id.toLowerCase().includes(query)
    )
  }, [searchQuery])

  useEffect(() => {
    if (!isOpen) {
      setSearchQuery('')
      setSelectedIndex(0)
      return
    }
    // Reset selection when commands change
    setSelectedIndex(0)
  }, [isOpen, searchQuery])

  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.min(prev + 1, filteredCommands.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((prev) => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (filteredCommands[selectedIndex]) {
          handleSelect(filteredCommands[selectedIndex])
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredCommands, selectedIndex, onClose])

  const handleSelect = (command) => {
    if (location.pathname !== command.path) {
      navigate(command.path)
    }
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[10000] flex items-start justify-center pt-[20vh]">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Command Palette */}
      <div className="relative w-full max-w-2xl mx-4">
        <div className="card p-0 shadow-2xl border-slate-700 dark:border-slate-600">
          {/* Search Input */}
          <div className="flex items-center gap-3 p-4 border-b border-slate-200 dark:border-slate-700">
            <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
            <input
              type="text"
              placeholder="Type a command or search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 bg-transparent border-none outline-none text-slate-900 dark:text-white placeholder-slate-500 text-lg"
              autoFocus
            />
            <kbd className="hidden sm:flex items-center gap-1 px-2 py-1 rounded bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 text-xs font-mono text-slate-600 dark:text-slate-300">
              ESC
            </kbd>
          </div>

          {/* Commands List */}
          <div className="max-h-96 overflow-y-auto">
            {filteredCommands.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-slate-500 dark:text-slate-400">No commands found</p>
              </div>
            ) : (
              filteredCommands.map((command, index) => {
                const Icon = command.icon
                const isSelected = index === selectedIndex
                return (
                  <button
                    key={command.id}
                    onClick={() => handleSelect(command)}
                    className={`
                      w-full flex items-center gap-3 px-4 py-3 text-left
                      transition-colors
                      ${isSelected
                        ? 'bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400'
                        : 'hover:bg-slate-50 dark:hover:bg-slate-700/50 text-slate-700 dark:text-slate-300'
                      }
                    `}
                  >
                    <Icon className={`w-5 h-5 flex-shrink-0 ${isSelected ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400'}`} />
                    <span className="font-medium">{command.label}</span>
                    {location.pathname === command.path && (
                      <span className="ml-auto text-xs text-slate-400 dark:text-slate-500">
                        Current
                      </span>
                    )}
                  </button>
                )
              })
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-4 py-2 border-t border-slate-200 dark:border-slate-700 text-xs text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600">↑</kbd>
                <kbd className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600">↓</kbd>
                <span>Navigate</span>
              </div>
              <div className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600">Enter</kbd>
                <span>Select</span>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 border border-slate-300 dark:border-slate-600">Esc</kbd>
              <span>Close</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}




