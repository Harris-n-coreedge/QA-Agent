import { useEffect, useState, useRef } from 'react'

/**
 * Custom hook for Intersection Observer API
 * Useful for lazy loading, infinite scroll, and animations on scroll
 * @param {object} options - IntersectionObserver options
 * @returns {Array} - [ref, isIntersecting, entry]
 */
export function useIntersectionObserver(options = {}) {
  const {
    threshold = 0,
    root = null,
    rootMargin = '0px',
    freezeOnceVisible = false,
  } = options

  const [entry, setEntry] = useState(null)
  const [isIntersecting, setIsIntersecting] = useState(false)
  const elementRef = useRef(null)
  const frozen = useRef(false)

  useEffect(() => {
    const element = elementRef.current
    const hasIOSupport = !!window.IntersectionObserver

    if (!hasIOSupport || !element) return

    const observerCallback = ([entry]) => {
      const isIntersecting = entry?.isIntersecting ?? false

      // Update state if not frozen
      if (!frozen.current) {
        setEntry(entry)
        setIsIntersecting(isIntersecting)

        // Freeze if element is visible and freezeOnceVisible is true
        if (isIntersecting && freezeOnceVisible) {
          frozen.current = true
        }
      }
    }

    const observerOptions = {
      threshold,
      root,
      rootMargin,
    }

    const observer = new IntersectionObserver(observerCallback, observerOptions)
    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [threshold, root, rootMargin, freezeOnceVisible])

  return [elementRef, isIntersecting, entry]
}

/**
 * Hook for lazy loading images
 * @param {string} src - Image source
 * @returns {object} - { ref, isLoaded, isInView }
 */
export function useLazyImage(src) {
  const [ref, isInView] = useIntersectionObserver({
    threshold: 0,
    freezeOnceVisible: true,
  })
  const [isLoaded, setIsLoaded] = useState(false)
  const [imageSrc, setImageSrc] = useState(null)

  useEffect(() => {
    if (isInView && src) {
      const img = new Image()
      img.src = src
      img.onload = () => {
        setImageSrc(src)
        setIsLoaded(true)
      }
    }
  }, [isInView, src])

  return { ref, isLoaded, isInView, src: imageSrc }
}

/**
 * Hook for animating elements on scroll into view
 * @param {object} options - Animation options
 * @returns {Array} - [ref, isVisible]
 */
export function useScrollAnimation(options = {}) {
  const { threshold = 0.1, delay = 0 } = options
  const [ref, isInView] = useIntersectionObserver({
    threshold,
    freezeOnceVisible: true,
  })
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    if (isInView) {
      const timer = setTimeout(() => {
        setIsVisible(true)
      }, delay)

      return () => clearTimeout(timer)
    }
  }, [isInView, delay])

  return [ref, isVisible]
}
