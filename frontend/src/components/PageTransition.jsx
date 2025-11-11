import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

/**
 * Page Transition Wrapper Component
 * Provides smooth animated transitions between pages
 */
export function PageTransition({ children }) {
  const location = useLocation()
  const [displayLocation, setDisplayLocation] = useState(location)
  const [transitionStage, setTransitionStage] = useState('fadeIn')

  useEffect(() => {
    if (location !== displayLocation) {
      setTransitionStage('fadeOut')
    }
  }, [location, displayLocation])

  return (
    <div
      className={`page-transition ${transitionStage}`}
      onAnimationEnd={() => {
        if (transitionStage === 'fadeOut') {
          setTransitionStage('fadeIn')
          setDisplayLocation(location)
        }
      }}
    >
      {displayLocation === location ? children : null}
    </div>
  )
}

/**
 * Enhanced Page Wrapper with Scroll Animations
 */
export function AnimatedPage({ children, className = '' }) {
  return (
    <div className={`animate-page-enter ${className}`}>
      {children}
    </div>
  )
}
