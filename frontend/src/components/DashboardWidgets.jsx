import { useState } from 'react'
import { LayoutGrid, Plus, X, GripVertical, BarChart3, Activity, TrendingUp, Clock, Zap } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

const WIDGET_TYPES = [
  { id: 'stats', name: 'Stats Overview', icon: BarChart3, default: true },
  { id: 'trends', name: 'Trends Chart', icon: TrendingUp },
  { id: 'activity', name: 'Activity Feed', icon: Activity },
  { id: 'recent', name: 'Recent Tests', icon: Clock },
  { id: 'performance', name: 'Performance', icon: Zap },
]

export function DashboardWidgets({ widgets = [], onWidgetsChange }) {
  const [showAddWidget, setShowAddWidget] = useState(false)
  const toast = useToast()

  const availableWidgets = WIDGET_TYPES.filter(
    (w) => !widgets.some((aw) => aw.id === w.id)
  )

  const handleAddWidget = (widgetType) => {
    const widget = WIDGET_TYPES.find((w) => w.id === widgetType)
    if (widget && onWidgetsChange) {
      onWidgetsChange([...widgets, { ...widget, position: widgets.length }])
      toast.success(`Added ${widget.name} widget`)
      setShowAddWidget(false)
    }
  }

  const handleRemoveWidget = (widgetId) => {
    if (onWidgetsChange) {
      onWidgetsChange(widgets.filter((w) => w.id !== widgetId))
      toast.success('Widget removed')
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <LayoutGrid className="w-5 h-5" />
            Dashboard Widgets
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Customize your dashboard layout
          </p>
        </div>
        <button
          onClick={() => setShowAddWidget(!showAddWidget)}
          className="btn btn-primary text-sm"
        >
          <Plus className="w-4 h-4" />
          <span>Add Widget</span>
        </button>
      </div>

      {showAddWidget && (
        <div className="card p-4">
          <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
            Available Widgets
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {availableWidgets.map((widget) => {
              const Icon = widget.icon
              return (
                <button
                  key={widget.id}
                  onClick={() => handleAddWidget(widget.id)}
                  className="p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-indigo-500 dark:hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-500/10 transition-all text-left"
                >
                  <Icon className="w-5 h-5 text-indigo-500 mb-2" />
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {widget.name}
                  </p>
                </button>
              )
            })}
          </div>
          {availableWidgets.length === 0 && (
            <p className="text-sm text-slate-500 dark:text-slate-400 text-center py-4">
              All widgets are already added
            </p>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {widgets.map((widget) => {
          const Icon = widget.icon
          return (
            <div
              key={widget.id}
              className="card p-4 hover-lift group relative"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <GripVertical className="w-4 h-4 text-slate-400 cursor-move" />
                  <Icon className="w-4 h-4 text-indigo-500" />
                  <span className="text-sm font-semibold text-slate-900 dark:text-white">
                    {widget.name}
                  </span>
                </div>
                <button
                  onClick={() => handleRemoveWidget(widget.id)}
                  className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="h-32 flex items-center justify-center bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {widget.name} content
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {widgets.length === 0 && (
        <div className="card p-12 text-center">
          <LayoutGrid className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No Widgets Added
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
            Add widgets to customize your dashboard
          </p>
          <button onClick={() => setShowAddWidget(true)} className="btn btn-primary">
            <Plus className="w-4 h-4" />
            <span>Add Widget</span>
          </button>
        </div>
      )}
    </div>
  )
}




