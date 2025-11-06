import { Inbox, TestTube, FileText, BarChart3, Search, AlertCircle } from 'lucide-react'

const EMPTY_STATE_CONFIGS = {
  default: {
    icon: Inbox,
    title: 'No data available',
    description: 'There\'s nothing here yet. Get started by creating your first item.',
  },
  tests: {
    icon: TestTube,
    title: 'No tests yet',
    description: 'Run your first test to see results here. Start with Quick Test or Browser Use.',
    actionLabel: 'Run Test',
  },
  results: {
    icon: FileText,
    title: 'No test results',
    description: 'Your test results will appear here once you run some tests.',
    actionLabel: 'View Tests',
  },
  search: {
    icon: Search,
    title: 'No results found',
    description: 'Try adjusting your search or filters to find what you\'re looking for.',
  },
  analytics: {
    icon: BarChart3,
    title: 'No analytics data',
    description: 'Analytics will appear here once you have test results to analyze.',
  },
  error: {
    icon: AlertCircle,
    title: 'Something went wrong',
    description: 'We encountered an error. Please try again or contact support if the problem persists.',
  },
}

export function EmptyState({
  type = 'default',
  title,
  description,
  icon: CustomIcon,
  actionLabel,
  onAction,
  children,
}) {
  const config = EMPTY_STATE_CONFIGS[type] || EMPTY_STATE_CONFIGS.default
  const Icon = CustomIcon || config.icon
  const displayTitle = title || config.title
  const displayDescription = description || config.description
  const displayActionLabel = actionLabel || config.actionLabel

  return (
    <div className="empty-state">
      <div className="flex flex-col items-center justify-center py-12 px-4">
        <div className="relative mb-6">
          <div className="absolute inset-0 bg-slate-200 dark:bg-slate-700 rounded-full blur-2xl opacity-50" />
          <div className="relative p-6 bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-700 rounded-full">
            <Icon className="w-12 h-12 text-slate-600 dark:text-slate-400" />
          </div>
        </div>
        
        <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2 text-center">
          {displayTitle}
        </h3>
        
        <p className="text-sm text-slate-600 dark:text-slate-400 text-center max-w-md mb-6">
          {displayDescription}
        </p>

        {children || (onAction && displayActionLabel && (
          <button onClick={onAction} className="btn btn-primary">
            {displayActionLabel}
          </button>
        ))}
      </div>
    </div>
  )
}

export function LoadingSkeleton({ lines = 3, showAvatar = false, className = '' }) {
  return (
    <div className={`space-y-4 ${className}`}>
      {showAvatar && (
        <div className="flex items-center gap-4">
          <div className="skeleton w-12 h-12 rounded-full" />
          <div className="flex-1 space-y-2">
            <div className="skeleton h-4 w-3/4" />
            <div className="skeleton h-4 w-1/2" />
          </div>
        </div>
      )}
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeleton h-4" style={{ width: `${100 - i * 10}%` }} />
      ))}
    </div>
  )
}

export function CardSkeleton({ count = 3 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="card p-6 space-y-4">
          <div className="skeleton h-6 w-3/4" />
          <div className="skeleton h-4 w-full" />
          <div className="skeleton h-4 w-2/3" />
          <div className="skeleton h-8 w-1/2" />
        </div>
      ))}
    </div>
  )
}




