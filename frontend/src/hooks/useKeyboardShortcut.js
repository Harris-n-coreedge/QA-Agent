import { useEffect, useCallback } from 'react'

/**
 * Custom hook for keyboard shortcuts
 * @param {string} key - Key to listen for (e.g., 'k', 'Enter', 'Escape')
 * @param {function} callback - Function to call when key is pressed
 * @param {object} options - Optional modifiers and options
 * @param {boolean} options.ctrl - Require Ctrl key
 * @param {boolean} options.shift - Require Shift key
 * @param {boolean} options.alt - Require Alt key
 * @param {boolean} options.meta - Require Meta/Cmd key
 * @param {boolean} options.preventDefault - Prevent default behavior
 */
export function useKeyboardShortcut(key, callback, options = {}) {
  const {
    ctrl = false,
    shift = false,
    alt = false,
    meta = false,
    preventDefault = true,
  } = options

  const handleKeyDown = useCallback(
    (event) => {
      // Check if all required modifiers are pressed
      const ctrlMatch = ctrl ? event.ctrlKey : true
      const shiftMatch = shift ? event.shiftKey : true
      const altMatch = alt ? event.altKey : true
      const metaMatch = meta ? event.metaKey : true

      // Check if the key matches
      const keyMatch = event.key.toLowerCase() === key.toLowerCase()

      if (keyMatch && ctrlMatch && shiftMatch && altMatch && metaMatch) {
        if (preventDefault) {
          event.preventDefault()
        }
        callback(event)
      }
    },
    [key, callback, ctrl, shift, alt, meta, preventDefault]
  )

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}

/**
 * Custom hook for multiple keyboard shortcuts
 * @param {Array} shortcuts - Array of shortcut objects
 * Example: [{ key: 'k', callback: () => {}, ctrl: true }]
 */
export function useKeyboardShortcuts(shortcuts) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      shortcuts.forEach(({ key, callback, ctrl, shift, alt, meta, preventDefault = true }) => {
        const ctrlMatch = ctrl ? event.ctrlKey || event.metaKey : !event.ctrlKey && !event.metaKey
        const shiftMatch = shift ? event.shiftKey : !event.shiftKey
        const altMatch = alt ? event.altKey : !event.altKey
        const metaMatch = meta ? event.metaKey : !event.metaKey

        const keyMatch = event.key.toLowerCase() === key.toLowerCase()

        if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
          if (preventDefault) {
            event.preventDefault()
          }
          callback(event)
        }
      })
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [shortcuts])
}

/**
 * Hook to detect if user is on Mac
 * @returns {boolean} - True if user is on Mac
 */
export function useIsMac() {
  return typeof window !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0
}

/**
 * Get appropriate modifier key label based on OS
 * @returns {string} - '⌘' for Mac, 'Ctrl' for others
 */
export function useModifierKey() {
  const isMac = useIsMac()
  return isMac ? '⌘' : 'Ctrl'
}
