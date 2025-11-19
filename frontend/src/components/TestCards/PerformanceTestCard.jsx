import { useState } from 'react'
import { 
  Activity, BarChart3, TrendingUp, Zap, Clock, Gauge, 
  Cpu, Globe, Database, Network, Smartphone, Chrome,
  FileText, Search, Code, Layers, Target, AlertTriangle, Shield
} from 'lucide-react'

const iconMap = {
  Activity, BarChart3, TrendingUp, Zap, Clock, Gauge,
  Cpu, Globe, Database, Network, Smartphone, Chrome,
  FileText, Search, Code, Layers, Target, AlertTriangle, Shield
}

export default function PerformanceTestCard({ testConfig, onRun, disabled, queuePosition, requiresPermission = false }) {
  const [isRunning, setIsRunning] = useState(false)
  const [permissionGranted, setPermissionGranted] = useState(false)
  const [showWarning, setShowWarning] = useState(false)
  const Icon = iconMap[testConfig.icon] || Activity

  const handleRun = async () => {
    if (disabled || isRunning) return
    
    // Check permission for restricted tests
    if (requiresPermission && !permissionGranted) {
      setShowWarning(true)
      return
    }
    
    setIsRunning(true)
    try {
      await onRun(testConfig, { user_permission: requiresPermission ? permissionGranted : false })
    } catch (error) {
      console.error(`Failed to start ${testConfig.name}:`, error)
    } finally {
      setIsRunning(false)
    }
  }
  
  const handlePermissionConfirm = () => {
    setPermissionGranted(true)
    setShowWarning(false)
  }

  const formatParams = () => {
    const params = testConfig.defaultParams
    if (testConfig.category === 'load') {
      if (params.users) {
        return `${params.users} users, ${params.duration || params.duration_hours || 60}${params.duration_hours ? 'h' : 's'}`
      } else if (params.max_users) {
        return `Up to ${params.max_users} users`
      } else if (params.target_rps) {
        return `${params.target_rps} RPS target`
      }
    } else if (testConfig.category === 'benchmark') {
      return `${params.iterations || 100} iterations`
    } else if (testConfig.category === 'combined') {
      return `${params.users || 50} users, ${params.duration || 60}s`
    }
    return 'Default parameters'
  }

  return (
    <div className="card hover-lift p-5 md:p-6 space-y-4">
      <div className="flex items-center gap-3 md:gap-4">
        <div className="p-2.5 md:p-3 rounded-lg bg-slate-700/50 border border-slate-600/50 flex-shrink-0">
          <Icon className="w-5 h-5 md:w-6 md:h-6 text-slate-300" />
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="text-lg md:text-xl font-semibold text-white mb-0.5">{testConfig.name}</h2>
          <p className="text-xs md:text-sm text-slate-400">{testConfig.category.charAt(0).toUpperCase() + testConfig.category.slice(1)} Test</p>
        </div>
      </div>
      
      <p className="text-sm text-slate-300 leading-relaxed">{testConfig.description}</p>
      
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span className="font-mono">{formatParams()}</span>
        {queuePosition !== null && queuePosition > 0 && (
          <span className="text-amber-400">Queue: #{queuePosition}</span>
        )}
      </div>
      
      {requiresPermission && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 space-y-2">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-amber-200">
              This test performs network scanning which may trigger security alerts.
            </p>
          </div>
          {!permissionGranted && (
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={permissionGranted}
                onChange={(e) => setPermissionGranted(e.target.checked)}
                className="w-4 h-4 rounded border-slate-600 bg-slate-700 text-amber-500 focus:ring-amber-500"
              />
              <span className="text-xs text-slate-300">
                I understand this test may be intrusive
              </span>
            </label>
          )}
        </div>
      )}
      
      {showWarning && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <p className="text-xs text-red-200 mb-2">
            Please confirm you understand the risks before running this test.
          </p>
          <div className="flex gap-2">
            <button
              onClick={handlePermissionConfirm}
              className="text-xs px-3 py-1 bg-red-500/20 hover:bg-red-500/30 rounded text-red-200"
            >
              I Understand
            </button>
            <button
              onClick={() => setShowWarning(false)}
              className="text-xs px-3 py-1 bg-slate-700 hover:bg-slate-600 rounded text-slate-300"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
      
      <button
        onClick={handleRun}
        disabled={disabled || isRunning || (requiresPermission && !permissionGranted)}
        className="btn btn-primary w-full"
      >
        {isRunning ? 'Starting...' : disabled ? 'Test Running' : requiresPermission && !permissionGranted ? 'Permission Required' : 'Run Test'}
      </button>
    </div>
  )
}

