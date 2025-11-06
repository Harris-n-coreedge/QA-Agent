import { useEffect, useState } from 'react'
import { CheckCircle2, Loader2, XCircle, Clock } from 'lucide-react'

export function ProgressIndicator({ steps = [], currentStep = 0, status = 'running' }) {
  const [animatedSteps, setAnimatedSteps] = useState([])

  useEffect(() => {
    setAnimatedSteps(steps.map((_, index) => ({
      ...steps[index],
      completed: index < currentStep,
      current: index === currentStep,
    })))
  }, [steps, currentStep])

  const getStepIcon = (step, index) => {
    if (step.completed) {
      return <CheckCircle2 className="w-5 h-5 text-emerald-500" />
    }
    if (step.current) {
      if (status === 'running') {
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      }
      if (status === 'error') {
        return <XCircle className="w-5 h-5 text-rose-500" />
      }
    }
    return <Clock className="w-5 h-5 text-slate-400" />
  }

  const getStepStatus = (step, index) => {
    if (step.completed) return 'completed'
    if (step.current) return status
    return 'pending'
  }

  return (
    <div className="space-y-4">
      {animatedSteps.map((step, index) => {
        const stepStatus = getStepStatus(step, index)
        return (
          <div
            key={index}
            className={`
              flex items-start gap-4 p-4 rounded-lg border transition-all
              ${
                stepStatus === 'completed'
                  ? 'bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/30'
                  : stepStatus === 'running'
                  ? 'bg-blue-50 dark:bg-blue-500/10 border-blue-200 dark:border-blue-500/30'
                  : stepStatus === 'error'
                  ? 'bg-rose-50 dark:bg-rose-500/10 border-rose-200 dark:border-rose-500/30'
                  : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700'
              }
            `}
          >
            <div className="flex-shrink-0 mt-0.5">
              {getStepIcon(step, index)}
            </div>
            <div className="flex-1 min-w-0">
              <h4
                className={`
                  font-semibold mb-1
                  ${
                    stepStatus === 'completed'
                      ? 'text-emerald-900 dark:text-emerald-400'
                      : stepStatus === 'running'
                      ? 'text-blue-900 dark:text-blue-400'
                      : stepStatus === 'error'
                      ? 'text-rose-900 dark:text-rose-400'
                      : 'text-slate-600 dark:text-slate-400'
                  }
                `}
              >
                {step.title}
              </h4>
              {step.description && (
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  {step.description}
                </p>
              )}
              {step.details && stepStatus === 'running' && (
                <p className="text-xs text-slate-500 dark:text-slate-500 mt-1 italic">
                  {step.details}
                </p>
              )}
            </div>
            {step.progress !== undefined && stepStatus === 'running' && (
              <div className="flex-shrink-0 w-16">
                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${step.progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export function SimpleProgress({ progress = 0, label = '', showPercentage = true }) {
  return (
    <div className="space-y-2">
      {label && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600 dark:text-slate-400">{label}</span>
          {showPercentage && (
            <span className="text-slate-900 dark:text-white font-semibold">{progress}%</span>
          )}
        </div>
      )}
      <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
        <div
          className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full transition-all duration-500 ease-out relative"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </div>
      </div>
    </div>
  )
}




