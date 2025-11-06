import { useEffect, useState } from 'react'
import { X, CheckCircle2, XCircle, AlertCircle, Info, Loader2 } from 'lucide-react'

const TOAST_TYPES = {
  success: { icon: CheckCircle2, bg: 'bg-emerald-500', iconColor: 'text-white' },
  error: { icon: XCircle, bg: 'bg-rose-500', iconColor: 'text-white' },
  warning: { icon: AlertCircle, bg: 'bg-amber-500', iconColor: 'text-white' },
  info: { icon: Info, bg: 'bg-blue-500', iconColor: 'text-white' },
  loading: { icon: Loader2, bg: 'bg-slate-500', iconColor: 'text-white' },
}

export function Toast({ id, message, type = 'info', duration = 5000, onClose }) {
  const [isExiting, setIsExiting] = useState(false)
  const config = TOAST_TYPES[type] || TOAST_TYPES.info
  const Icon = config.icon

  useEffect(() => {
    if (type !== 'loading' && duration > 0) {
      const timer = setTimeout(() => {
        handleClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, type])

  const handleClose = () => {
    setIsExiting(true)
    setTimeout(() => {
      onClose(id)
    }, 300)
  }

  return (
    <div
      className={`
        toast-item ${isExiting ? 'toast-exit' : 'toast-enter'}
        flex items-start gap-3 p-4 rounded-lg shadow-xl border
        bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700
        min-w-[300px] max-w-[500px]
      `}
    >
      <div className={`flex-shrink-0 p-1.5 rounded-lg ${config.bg}`}>
        <Icon
          className={`w-4 h-4 ${config.iconColor} ${type === 'loading' ? 'animate-spin' : ''}`}
        />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-900 dark:text-white break-words">
          {message}
        </p>
      </div>
      {type !== 'loading' && (
        <button
          onClick={handleClose}
          className="flex-shrink-0 p-1 rounded-md hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
        >
          <X className="w-4 h-4 text-slate-500 dark:text-slate-400" />
        </button>
      )}
    </div>
  )
}

export function ToastContainer({ toasts, removeToast }) {
  return (
    <div className="fixed top-20 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <Toast {...toast} onClose={removeToast} />
        </div>
      ))}
    </div>
  )
}

