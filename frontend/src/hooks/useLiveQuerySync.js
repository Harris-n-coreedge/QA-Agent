import { useEffect, useMemo } from 'react'

/**
 * Lightweight helper to keep React Query data feeling “live” without WebSockets.
 * It listens for focus, visibility, and network regain events, throttling calls
 * so we avoid hammering the backend while still refreshing promptly.
 */
export function useLiveQuerySync(refetchers = [], options = {}) {
  const { throttleMs = 2500 } = options

  const stableRefetchers = useMemo(
    () => refetchers.filter((fn) => typeof fn === 'function'),
    [refetchers],
  )

  useEffect(() => {
    if (!stableRefetchers.length) {
      return undefined
    }

    let lastTriggered = 0

    const trigger = () => {
      const now = Date.now()
      if (now - lastTriggered < throttleMs) return
      lastTriggered = now
      stableRefetchers.forEach((fn) => fn())
    }

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') {
        trigger()
      }
    }

    window.addEventListener('focus', trigger)
    window.addEventListener('online', trigger)
    document.addEventListener('visibilitychange', handleVisibility)

    return () => {
      window.removeEventListener('focus', trigger)
      window.removeEventListener('online', trigger)
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [stableRefetchers, throttleMs])
}

