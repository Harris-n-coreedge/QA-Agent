import { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    // Load theme from localStorage or default to 'dark'
    return localStorage.getItem('theme') || 'dark'
  })

  // Apply theme on mount and when theme changes
  useEffect(() => {
    const root = document.documentElement
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    const effectiveTheme = theme === 'system' ? systemTheme : theme

    // Remove all theme classes
    root.classList.remove('light', 'dark')
    
    // Add the effective theme class
    root.classList.add(effectiveTheme)
    
    // Store theme preference
    localStorage.setItem('theme', theme)
    
    // Update color-scheme meta tag
    root.style.colorScheme = effectiveTheme
  }, [theme])

  // Apply theme immediately on mount (before React renders)
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'dark'
    const root = document.documentElement
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    const effectiveTheme = savedTheme === 'system' ? systemTheme : savedTheme
    
    root.classList.remove('light', 'dark')
    root.classList.add(effectiveTheme)
    root.style.colorScheme = effectiveTheme
  }, [])

  // Listen for system theme changes when theme is set to 'system'
  useEffect(() => {
    if (theme !== 'system') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e) => {
      const root = document.documentElement
      root.classList.remove('light', 'dark')
      root.classList.add(e.matches ? 'dark' : 'light')
      root.style.colorScheme = e.matches ? 'dark' : 'light'
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}

