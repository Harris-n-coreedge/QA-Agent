import { useState, useEffect } from 'react'

/**
 * Custom hook to get current window size and detect breakpoints
 * @returns {object} - Window dimensions and breakpoint flags
 */
export function useWindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  })

  useEffect(() => {
    if (typeof window === 'undefined') return

    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      })
    }

    // Add event listener with passive option for better performance
    window.addEventListener('resize', handleResize, { passive: true })

    // Call handler right away so state gets updated with initial window size
    handleResize()

    // Cleanup
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Common breakpoints
  const breakpoints = {
    isMobile: windowSize.width < 640,
    isTablet: windowSize.width >= 640 && windowSize.width < 1024,
    isDesktop: windowSize.width >= 1024,
    isLargeDesktop: windowSize.width >= 1280,
    isExtraLarge: windowSize.width >= 1536,
  }

  return {
    ...windowSize,
    ...breakpoints,
  }
}

/**
 * Custom hook to detect if user prefers reduced motion
 * @returns {boolean} - True if user prefers reduced motion
 */
export function usePrefersReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    const handleChange = (event) => {
      setPrefersReducedMotion(event.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return prefersReducedMotion
}

/**
 * Custom hook to detect dark mode preference
 * @returns {boolean} - True if user prefers dark mode
 */
export function usePrefersDarkMode() {
  const [prefersDarkMode, setPrefersDarkMode] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    setPrefersDarkMode(mediaQuery.matches)

    const handleChange = (event) => {
      setPrefersDarkMode(event.matches)
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  return prefersDarkMode
}
