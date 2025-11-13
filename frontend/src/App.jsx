import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { Activity, TestTube, Zap, BarChart3, Settings as SettingsIcon, Bell, User, LogOut, LogIn, Command, Menu, X, Home as HomeIcon, MessageSquare } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import BrowserUse from './pages/BrowserUse'
import TestResults from './pages/TestResults'
import QuickTest from './pages/QuickTest'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Settings from './pages/Settings'
import HomePage from './pages/LandingPage'
import ChatAssistant from './pages/ChatAssistant'
import { CommandPalette } from './components/CommandPalette'
import { OnboardingTour } from './components/OnboardingTour'
import { NotificationCenter, useNotifications } from './components/NotificationCenter'
import { ParticleBackground } from './components/ParticleBackground'

const navItems = [
  { path: '/', label: 'Home', icon: HomeIcon },
  { path: '/dashboard', label: 'Dashboard', icon: Activity },
  { path: '/browser-use', label: 'Browser Use', icon: Zap },
  { path: '/results', label: 'Test Results', icon: BarChart3 },
  { path: '/quick-test', label: 'Quick Test', icon: Activity },
  { path: '/assistant', label: 'QA Copilot', icon: MessageSquare },
  { path: '/settings', label: 'Settings', icon: SettingsIcon },
]

const homeSections = [
  { href: '#platform', label: 'Platform' },
  { href: '#workflows', label: 'Workflows' },
  { href: '#insights', label: 'Insights' },
  { href: '#plans', label: 'Plans' },
  { href: '#contact', label: 'Contact' },
]

function NotificationButton() {
  const [notificationCenterOpen, setNotificationCenterOpen] = useState(false)
  const { unreadCount } = useNotifications()

  return (
    <>
      <button
        onClick={() => setNotificationCenterOpen(true)}
        className="hidden sm:inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 p-2 text-white/70 transition hover:bg-white/10 hover:text-white relative"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400" />
        )}
      </button>
      <NotificationCenter
        isOpen={notificationCenterOpen}
        onClose={() => setNotificationCenterOpen(false)}
      />
    </>
  )
}

function Navbar({ onCommandClick, navigate }) {
  const location = useLocation()
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const isHome = location.pathname === '/'

  useEffect(() => {
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

  const renderNavLinks = (orientation = 'horizontal') => {
    const containerClass = orientation === 'horizontal' ? 'items-center gap-1' : 'flex-col gap-2'

    if (isHome) {
      return (
        <div className={`flex ${containerClass} text-sm font-medium text-white/70`}>
          {homeSections.map((section) => (
            <a
              key={section.href}
              href={section.href}
              onClick={() => setMobileMenuOpen(false)}
              className="rounded-full px-4 py-2 transition hover:bg-white/10 hover:text-white"
            >
              {section.label}
            </a>
          ))}
        </div>
      )
    }

    return (
      <div className={`flex ${containerClass} text-sm font-medium text-white/70`}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileMenuOpen(false)}
              className={`inline-flex items-center gap-2 rounded-full px-4 py-2 transition ${
                isActive
                  ? 'bg-gradient-to-r from-purple-500/90 to-indigo-500/90 text-white shadow-lg shadow-purple-500/30'
                  : 'hover:bg-white/10 hover:text-white'
              }`}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          )
        })}
      </div>
    )
  }

  return (
    <header className="relative z-30">
      <div className="w-full">
        <div className="flex items-center justify-between gap-4 rounded-full border border-white/10 bg-black/40 px-4 py-3 backdrop-blur-xl sm:px-6">
          <div className="flex items-center gap-3">
            <Link to="/" className="group flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 rounded-xl bg-purple-500/60 blur-md opacity-60 group-hover:opacity-80 transition" />
                <div className="relative flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 via-purple-400 to-purple-600 shadow-lg shadow-purple-700/40">
                  <TestTube className="h-5 w-5 text-white" />
                </div>
              </div>
              <span className="text-lg font-semibold tracking-tight text-white">QA Agent</span>
            </Link>
          </div>

          <nav className="hidden md:block">
            <div className="flex items-center justify-center">
              <div className="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2 py-1.5">
                {renderNavLinks()}
              </div>
            </div>
          </nav>

          <div className="flex items-center gap-2">
            {isAuthenticated && (
              <button
                onClick={onCommandClick}
                className="hidden lg:inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white/70 transition hover:bg-white/10 hover:text-white"
              >
                <Command className="h-4 w-4" />
                {isHome ? 'Open Console' : 'Commands'}
              </button>
            )}

            {isHome && (
              <Link
                to="/dashboard"
                className="hidden md:inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white/80 transition hover:bg-white/10 hover:text-white"
              >
                <Activity className="h-4 w-4" />
                Go to Dashboard
              </Link>
            )}

            {isAuthenticated && <NotificationButton />}

            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen((prev) => !prev)}
                  className="inline-flex items-center justify-center rounded-full border border-white/10 bg-white/5 p-2 text-white/70 transition hover:bg-white/10 hover:text-white"
                >
                  <User className="h-5 w-5" />
                </button>
                {userMenuOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
                    <div className="absolute right-0 mt-3 w-56 rounded-2xl border border-white/10 bg-black/90 p-4 shadow-2xl shadow-purple-900/30 z-50">
                      <div className="mb-3 border-b border-white/10 pb-3">
                        <p className="text-sm font-semibold text-white">John Doe</p>
                        <p className="text-xs text-white/60">john.doe@example.com</p>
                      </div>
                      <Link
                        to="/settings"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-white/70 transition hover:bg-white/10 hover:text-white"
                      >
                        <SettingsIcon className="h-4 w-4" />
                        Settings
                      </Link>
                      <button
                        onClick={handleSignOut}
                        className="mt-1 flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 px-4 py-2 text-sm font-semibold text-white"
                      >
                        <LogOut className="h-4 w-4" />
                        Sign Out
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <Link
                to="/signin"
                className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-purple-700/40 transition hover:shadow-purple-500/60"
              >
                <LogIn className="h-4 w-4" />
                Sign In
              </Link>
            )}

            <button
              className="inline-flex md:hidden items-center justify-center rounded-full border border-white/10 bg-white/5 p-2 text-white/70 transition hover:bg-white/10 hover:text-white"
              onClick={() => setMobileMenuOpen(true)}
              aria-label="Open navigation"
            >
              <Menu className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-black/80 backdrop-blur-sm">
          <div className="absolute inset-x-4 top-20 rounded-3xl border border-white/10 bg-black/90 p-6">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold uppercase tracking-[0.35em] text-white/60">Menu</p>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="rounded-full border border-white/10 bg-white/5 p-2 text-white/70 transition hover:bg-white/10 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="mt-6 space-y-4">
              {renderNavLinks('vertical')}
            </div>
            <div className="mt-6 border-t border-white/10 pt-6 space-y-3">
              {isHome && (
                <Link
                  to="/dashboard"
                  onClick={() => setMobileMenuOpen(false)}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white/80 transition hover:bg-white/10 hover:text-white"
                >
                  <Activity className="h-4 w-4" />
                  Go to Dashboard
                </Link>
              )}
              {isAuthenticated ? (
                <button
                  onClick={handleSignOut}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 px-4 py-2 text-sm font-semibold text-white"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </button>
              ) : (
                <Link
                  to="/signin"
                  onClick={() => setMobileMenuOpen(false)}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 px-4 py-2 text-sm font-semibold text-white"
                >
                  <LogIn className="h-4 w-4" />
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}

function AppContent() {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const location = useLocation()
  const isAuthPage = location.pathname === '/signin' || location.pathname === '/signup'

  useEffect(() => {
    if (isAuthPage) return

    const handleKeyDown = (e) => {
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
      <div className="relative z-10 flex flex-col gap-0 px-4 sm:px-6">
        <NavbarWithRouter onCommandClick={() => setCommandPaletteOpen(true)} />
        <div className="relative w-full">
          <div className="absolute inset-0 -z-10 rounded-[32px] bg-gradient-to-br from-purple-600/25 via-purple-500/10 to-transparent blur-3xl" />
          <div className="relative overflow-hidden rounded-[32px] border border-white/10 bg-black/85 px-4 pb-6 shadow-[0_35px_120px_-45px_rgba(129,71,255,0.75)] sm:px-8 sm:pb-10 lg:px-12 lg:pb-12">
            <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,#7e22ce40,transparent_60%)]" />
            <div className="absolute -top-20 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-purple-500/20 blur-3xl" />
            <div className="absolute -bottom-24 right-1/4 h-64 w-64 rounded-full bg-indigo-500/20 blur-3xl" />
            <div className="relative z-10 space-y-10">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/browser-use" element={<BrowserUse />} />
                <Route path="/results" element={<TestResults />} />
                <Route path="/quick-test" element={<QuickTest />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/assistant" element={<ChatAssistant />} />
              </Routes>
            </div>
          </div>
        </div>
      </div>
      <CommandPalette isOpen={commandPaletteOpen} onClose={() => setCommandPaletteOpen(false)} />
      <OnboardingTour />
    </>
  )
}

function NavbarWithRouter({ onCommandClick }) {
  const navigate = useNavigate()
  return <Navbar onCommandClick={onCommandClick} navigate={navigate} />
}

function App() {
  return (
    <Router>
      <div className="min-h-screen relative overflow-hidden bg-[#0b031d] text-white">
        <ParticleBackground particleCount={60} color="#8b5cf6" />
        <div className="absolute inset-0 -z-20 bg-gradient-to-br from-[#160642] via-[#1f094f] to-[#2c0d5f]" />
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,#8b5cf6,transparent_60%)] opacity-70" />
        <AppContent />
      </div>
    </Router>
  )
}

export default App
