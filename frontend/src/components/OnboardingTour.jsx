import { useState, useEffect } from 'react'
import { X, ChevronRight, ChevronLeft, CheckCircle2 } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

const TOUR_STEPS = [
  {
    id: 'dashboard',
    title: 'Welcome to QA Agent!',
    description: 'Your comprehensive QA testing platform. This dashboard gives you an overview of all your tests and system health.',
    target: null,
    position: 'center',
  },
  {
    id: 'quick-test',
    title: 'Quick Test',
    description: 'Run instant QA checks on any website. Perfect for quick validation and baseline testing.',
    target: 'nav-quick-test',
    position: 'bottom',
  },
  {
    id: 'browser-use',
    title: 'Browser Use',
    description: 'Execute complex browser-based tests using natural language commands. The AI agent handles the automation.',
    target: 'nav-browser-use',
    position: 'bottom',
  },
  {
    id: 'results',
    title: 'Test Results',
    description: 'View, filter, and export all your test results. Track performance over time and compare different runs.',
    target: 'nav-results',
    position: 'bottom',
  },
  {
    id: 'command-palette',
    title: 'Command Palette',
    description: 'Press Ctrl+K (or Cmd+K on Mac) to quickly navigate and access features. Try it now!',
    target: 'nav-command',
    position: 'bottom',
  },
]

export function OnboardingTour() {
  const [currentStep, setCurrentStep] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [completed, setCompleted] = useState(false)
  const toast = useToast()

  useEffect(() => {
    const hasSeenTour = localStorage.getItem('hasSeenTour')
    if (!hasSeenTour) {
      // Show tour after a short delay
      setTimeout(() => {
        setIsOpen(true)
      }, 1000)
    }
  }, [])

  const handleNext = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      handleComplete()
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSkip = () => {
    localStorage.setItem('hasSeenTour', 'true')
    setIsOpen(false)
    toast.info('You can restart the tour from Settings')
  }

  const handleComplete = () => {
    localStorage.setItem('hasSeenTour', 'true')
    setCompleted(true)
    setIsOpen(false)
    toast.success('Welcome to QA Agent! 🎉')
  }

  const restartTour = () => {
    localStorage.removeItem('hasSeenTour')
    setCurrentStep(0)
    setIsOpen(true)
    setCompleted(false)
  }

  if (!isOpen) {
    return null
  }

  const step = TOUR_STEPS[currentStep]
  const isFirst = currentStep === 0
  const isLast = currentStep === TOUR_STEPS.length - 1

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9998]" />
      
      {/* Tour Modal */}
      <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 pointer-events-none">
        <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4 pointer-events-auto border border-slate-200 dark:border-slate-700">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                {step.title}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                Step {currentStep + 1} of {TOUR_STEPS.length}
              </p>
            </div>
            <button
              onClick={handleSkip}
              className="p-1 rounded hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
            <div
              className="bg-indigo-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / TOUR_STEPS.length) * 100}%` }}
            />
          </div>

          {/* Content */}
          <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
            {step.description}
          </p>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
            <button
              onClick={handleSkip}
              className="text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
            >
              Skip Tour
            </button>
            <div className="flex items-center gap-2">
              {!isFirst && (
                <button
                  onClick={handlePrevious}
                  className="btn btn-secondary text-sm"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Previous</span>
                </button>
              )}
              <button
                onClick={isLast ? handleComplete : handleNext}
                className="btn btn-primary text-sm"
              >
                <span>{isLast ? 'Get Started' : 'Next'}</span>
                {!isLast && <ChevronRight className="w-4 h-4" />}
                {isLast && <CheckCircle2 className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export function useOnboardingTour() {
  const restartTour = () => {
    localStorage.removeItem('hasSeenTour')
    window.location.reload()
  }

  return { restartTour }
}




