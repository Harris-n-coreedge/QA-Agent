import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { Activity, TestTube, Zap, BarChart3, Settings as SettingsIcon, Menu, X, Bell, User, Search, LogOut, LogIn, Command } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import BrowserUse from './pages/BrowserUse'
import TestResults from './pages/TestResults'
import QuickTest from './pages/QuickTest'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Settings from './pages/Settings'
import { CommandPalette } from './components/CommandPalette'
import { OnboardingTour } from './components/OnboardingTour'
import { NotificationCenter, useNotifications } from './components/NotificationCenter'
import { ParticleBackground } from './components/ParticleBackground'

function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Activity, label: 'Dashboard' },
    { path: '/browser-use', icon: Zap, label: 'Browser Use' },
    { path: '/results', icon: BarChart3, label: 'Test Results' },
    { path: '/quick-test', icon: Activity, label: 'Quick Test' },
  ]

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/70 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-full bg-[#111111] backdrop-blur-xl border-r border-gray-800 z-50 transition-all duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 w-64 flex flex-col`}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-800">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-purple-600 rounded-lg blur-md opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-500 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform shadow-lg shadow-purple-500/20">
                <TestTube className="w-5 h-5 text-white" />
              </div>
            </div>
            <span className="text-lg font-bold text-white">QA Agent</span>
          </Link>
          <button
            onClick={() => setIsOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-[#1a1a1a] text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 overflow-y-auto">
          <div className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsOpen(false)}
                  className={`sidebar-link ${isActive ? 'active' : ''}`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              )
            })}
          </div>
        </nav>

        {/* Footer */}
        <div className="px-4 py-4 border-t border-gray-800">
          <Link
            to="/settings"
            className="sidebar-link"
          >
            <SettingsIcon className="w-5 h-5 flex-shrink-0" />
            <span className="font-medium">Settings</span>
          </Link>
        </div>
      </aside>
    </>
  )
}

function NotificationButton() {
  const [notificationCenterOpen, setNotificationCenterOpen] = useState(false)
  const { unreadCount } = useNotifications()

  return (
    <>
      <button
        onClick={() => setNotificationCenterOpen(true)}
        className="p-2 rounded-lg hover:bg-[#1a1a1a] text-gray-400 hover:text-white transition-colors relative"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        )}
      </button>
      <NotificationCenter
        isOpen={notificationCenterOpen}
        onClose={() => setNotificationCenterOpen(false)}
      />
    </>
  )
}

function Navbar({ onMenuClick, navigate, onCommandClick }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('authToken')
    setIsAuthenticated(!!token)
  }, [])

  const handleSignOut = () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('rememberMe')
    setIsAuthenticated(false)
    setUserMenuOpen(false)
    navigate('/signin')
  }

  return (
    <nav className="glass border-b border-gray-800 sticky top-0 z-30 backdrop-blur-xl bg-[#111111]/95">
      <div className="h-16 flex items-center justify-between px-4 sm:px-6">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-[#1a1a1a] text-gray-400 hover:text-white transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          {/* Search Bar */}
          <div className="hidden md:flex items-center gap-2 flex-1 max-w-md">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search tests, results..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input pl-10 pr-4 py-2 text-sm w-full bg-[#1a1a1a] border-gray-800 text-white placeholder-gray-500"
              />
            </div>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-2">
          {/* Command Palette Trigger */}
          {isAuthenticated && (
            <button
              onClick={onCommandClick}
              className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-800 bg-[#1a1a1a] hover:bg-[#111111] text-gray-400 hover:text-white text-sm transition-colors"
              title="Command Palette (Ctrl+K)"
            >
              <Command className="w-4 h-4" />
              <span className="hidden lg:inline">Commands</span>
              <kbd className="hidden xl:inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-[#0a0a0a] border border-gray-800 text-xs font-mono text-gray-300">
                ⌘K
              </kbd>
            </button>
          )}
          
          {/* Notifications */}
          {isAuthenticated && (
            <NotificationButton />
          )}

          {/* User Menu / Sign In */}
          {isAuthenticated ? (
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="p-2 rounded-lg hover:bg-[#1a1a1a] text-gray-400 hover:text-white transition-colors"
              >
                <User className="w-5 h-5" />
              </button>

              {/* User Dropdown Menu */}
              {userMenuOpen && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setUserMenuOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-56 bg-[#1a1a1a] border border-gray-800 rounded-lg shadow-xl z-50 py-2">
                    <div className="px-4 py-3 border-b border-gray-800">
                      <p className="text-sm font-semibold text-white">John Doe</p>
                      <p className="text-xs text-gray-400 truncate">john.doe@example.com</p>
                    </div>
                    <Link
                      to="/settings"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-[#111111] hover:text-white transition-colors"
                    >
                      <SettingsIcon className="w-4 h-4" />
                      <span>Settings</span>
                    </Link>
                    <button
                      onClick={handleSignOut}
                      className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-[#111111] hover:text-white transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          ) : (
            <Link
              to="/signin"
              className="btn btn-primary text-sm"
            >
              <LogIn className="w-4 h-4" />
              <span className="hidden sm:inline">Sign In</span>
            </Link>
          )}
        </div>
      </div>
    </nav>
  )
}

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const location = useLocation()
  const isAuthPage = location.pathname === '/signin' || location.pathname === '/signup'

  // Keyboard shortcuts
  useEffect(() => {
    if (isAuthPage) return

    const handleKeyDown = (e) => {
      // Cmd/Ctrl + K for command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isAuthPage])

  if (isAuthPage) {
    return (
      <main className="flex-1 w-full">
        <Routes>
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
        </Routes>
      </main>
    )
  }

  return (
    <>
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <div className="flex-1 flex flex-col lg:ml-64">
        <NavbarWithRouter 
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          onCommandClick={() => setCommandPaletteOpen(true)}
        />
        <main className="flex-1 px-4 sm:px-6 py-6 sm:py-8 relative z-10">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/browser-use" element={<BrowserUse />} />
            <Route path="/results" element={<TestResults />} />
            <Route path="/quick-test" element={<QuickTest />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
      <CommandPalette isOpen={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />
      <OnboardingTour />
    </>
  )
}

// Wrapper to use useNavigate hook
function NavbarWithRouter({ onMenuClick, onCommandClick }) {
  const navigate = useNavigate()
  return <Navbar onMenuClick={onMenuClick} navigate={navigate} onCommandClick={onCommandClick} />
}

function App() {
  return (
    <Router>
      <div className="min-h-screen relative flex">
        <ParticleBackground particleCount={60} color="#8b5cf6" />
        <AppContent />
      </div>
    </Router>
  )
}

export default App
