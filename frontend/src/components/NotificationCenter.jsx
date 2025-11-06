import { useState, useEffect } from 'react'
import { Bell, X, CheckCircle2, XCircle, AlertCircle, Info, Clock, Zap, Trash2, Check } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

const NOTIFICATION_TYPES = {
  success: { icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-50 dark:bg-emerald-500/10' },
  error: { icon: XCircle, color: 'text-rose-500', bg: 'bg-rose-50 dark:bg-rose-500/10' },
  warning: { icon: AlertCircle, color: 'text-amber-500', bg: 'bg-amber-50 dark:bg-amber-500/10' },
  info: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-500/10' },
  test: { icon: Zap, color: 'text-indigo-500', bg: 'bg-indigo-50 dark:bg-indigo-500/10' },
}

export function NotificationCenter({ isOpen, onClose }) {
  const [notifications, setNotifications] = useState(() => {
    const saved = localStorage.getItem('notifications')
    return saved ? JSON.parse(saved) : []
  })
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    localStorage.setItem('notifications', JSON.stringify(notifications))
  }, [notifications])

  const markAsRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    )
  }

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
  }

  const deleteNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }

  const clearAll = () => {
    setNotifications([])
  }

  const filteredNotifications = notifications.filter((n) => {
    if (filter === 'all') return true
    if (filter === 'unread') return !n.read
    return n.type === filter
  })

  const unreadCount = notifications.filter((n) => !n.read).length

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[10000] flex items-start justify-end pt-16 pr-4">
      <div className="bg-black/50 backdrop-blur-sm fixed inset-0" onClick={onClose} />
      <div className="relative w-full max-w-md bg-white dark:bg-slate-800 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 flex flex-col max-h-[80vh]">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <Bell className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <h3 className="font-semibold text-slate-900 dark:text-white">Notifications</h3>
            {unreadCount > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-rose-500 text-white text-xs font-semibold">
                {unreadCount}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
                title="Mark all as read"
              >
                <Check className="w-4 h-4" />
              </button>
            )}
            {notifications.length > 0 && (
              <button
                onClick={clearAll}
                className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-rose-600 dark:text-rose-400"
                title="Clear all"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 p-3 border-b border-slate-200 dark:border-slate-700 overflow-x-auto scrollbar-hide">
          {['all', 'unread', 'test', 'success', 'error', 'warning'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                filter === f
                  ? 'bg-indigo-100 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-400'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {/* Notifications List */}
        <div className="flex-1 overflow-y-auto">
          {filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 px-4">
              <Bell className="w-12 h-12 text-slate-400 mb-3" />
              <p className="text-sm text-slate-500 dark:text-slate-400 text-center">
                {filter === 'unread' ? 'No unread notifications' : 'No notifications'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-200 dark:divide-slate-700">
              {filteredNotifications.map((notification) => {
                const config = NOTIFICATION_TYPES[notification.type] || NOTIFICATION_TYPES.info
                const Icon = config.icon
                return (
                  <div
                    key={notification.id}
                    className={`p-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors ${
                      !notification.read ? 'bg-blue-50 dark:bg-blue-500/10' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`flex-shrink-0 p-2 rounded-lg ${config.bg}`}
                      >
                        <Icon className={`w-5 h-5 ${config.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <p className="font-semibold text-slate-900 dark:text-white text-sm">
                            {notification.title}
                          </p>
                          {!notification.read && (
                            <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0 mt-1" />
                          )}
                        </div>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-500 dark:text-slate-500">
                            {new Date(notification.timestamp).toLocaleString()}
                          </span>
                          <div className="flex items-center gap-2">
                            {!notification.read && (
                              <button
                                onClick={() => markAsRead(notification.id)}
                                className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                              >
                                Mark as read
                              </button>
                            )}
                            <button
                              onClick={() => deleteNotification(notification.id)}
                              className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-500"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Hook to add notifications
export function useNotifications() {
  const [notifications, setNotifications] = useState(() => {
    const saved = localStorage.getItem('notifications')
    return saved ? JSON.parse(saved) : []
  })

  const addNotification = (title, message, type = 'info') => {
    const notification = {
      id: Date.now() + Math.random(),
      title,
      message,
      type,
      read: false,
      timestamp: new Date().toISOString(),
    }
    setNotifications((prev) => [notification, ...prev].slice(0, 100)) // Keep last 100
    localStorage.setItem('notifications', JSON.stringify([notification, ...notifications].slice(0, 100)))
    return notification.id
  }

  const unreadCount = notifications.filter((n) => !n.read).length

  return { notifications, addNotification, unreadCount }
}




