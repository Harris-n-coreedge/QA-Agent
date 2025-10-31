import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Activity, TestTube, Zap, BarChart3, Settings, Menu, X } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import BrowserUse from './pages/BrowserUse'
import TestResults from './pages/TestResults'
import QuickTest from './pages/QuickTest'

function Navigation() {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navItems = [
    { path: '/', icon: Activity, label: 'Dashboard' },
    { path: '/browser-use', icon: Zap, label: 'Browser Use' },
    { path: '/results', icon: BarChart3, label: 'Test Results' },
    { path: '/quick-test', icon: Activity, label: 'Quick Test' },
  ]

  return (
    <nav className="bg-gradient-to-r from-white/10 to-white/5 backdrop-blur-3xl border-b border-white/20 sticky top-0 z-50 shadow-2xl">
      <div className="container mx-auto px-4 md:px-8">
        {/* Desktop Navigation */}
        <div className="hidden lg:flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-white/10 rounded-xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <TestTube className="w-7 h-7 text-white transition-all duration-500 group-hover:scale-110 group-hover:rotate-12 relative z-10" />
              </div>
              <span className="text-xl font-bold text-gradient text-glow group-hover:scale-105 transition-transform duration-300">
                QA Agent
              </span>
            </Link>

            <div className="flex space-x-1">
              {navItems.map((item, idx) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    style={{ animationDelay: `${idx * 0.1}s` }}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 transform relative overflow-hidden group ${
                      isActive
                        ? 'bg-gradient-to-r from-white/15 to-white/10 text-white shadow-xl shadow-white/20 border border-white/30'
                        : 'text-white/70 hover:bg-gradient-to-r hover:from-white/10 hover:to-white/5 hover:text-white hover:border-white/20 border border-transparent'
                    }`}
                  >
                    {isActive && (
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/8 to-transparent animate-shimmer" />
                    )}
                    <Icon className={`w-4 h-4 transition-all duration-300 ${isActive ? 'text-white' : 'group-hover:text-white'}`} />
                    <span className="relative z-10 font-semibold text-sm tracking-wide">{item.label}</span>
                    {isActive && (
                      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-white to-transparent rounded-full" />
                    )}
                  </Link>
                )
              })}
            </div>
          </div>

          <button className="text-white/70 hover:text-white transition-all duration-300 hover:rotate-90 hover:scale-110 p-2 rounded-xl hover:bg-gradient-to-r hover:from-white/10 hover:to-white/5 border border-transparent hover:border-white/20">
            <Settings className="w-5 h-5" />
          </button>
        </div>

        {/* Mobile Navigation */}
        <div className="lg:hidden flex items-center justify-between h-14">
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="relative">
              <TestTube className="w-6 h-6 text-white transition-all duration-300 group-hover:scale-110 relative z-10" />
            </div>
            <span className="text-lg font-bold text-gradient">QA Agent</span>
          </Link>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="text-white p-2 rounded-lg hover:bg-white/10 transition-all duration-300 border border-white/20"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileMenuOpen && (
          <div className="lg:hidden absolute top-14 left-0 right-0 bg-gradient-to-br from-black/95 to-gray-900/95 backdrop-blur-3xl border-b border-white/20 shadow-2xl animate-slideInUp">
            <div className="container mx-auto px-4 py-4 space-y-2">
              {navItems.map((item, idx) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ animationDelay: `${idx * 0.1}s` }}
                    className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                      isActive
                        ? 'bg-gradient-to-r from-white/15 to-white/10 text-white border border-white/30'
                        : 'text-white/70 hover:bg-white/10 hover:text-white border border-transparent'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-semibold text-sm">{item.label}</span>
                  </Link>
                )
              })}
              <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-white/70 hover:bg-white/10 hover:text-white transition-all duration-300 border border-transparent hover:border-white/20">
                <Settings className="w-5 h-5" />
                <span className="font-semibold text-sm">Settings</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen relative overflow-x-hidden">
        {/* Enhanced Background Effects */}
        <div className="fixed inset-0 bg-gradient-to-br from-black via-gray-900 to-black" />
        <div className="fixed inset-0 bg-[radial-gradient(circle_at_20%_50%,rgba(255,255,255,0.1)_0%,transparent_50%)]" />
        <div className="fixed inset-0 bg-[radial-gradient(circle_at_80%_20%,rgba(99,102,241,0.05)_0%,transparent_50%)]" />
        <div className="fixed inset-0 bg-[radial-gradient(circle_at_40%_80%,rgba(255,255,255,0.03)_0%,transparent_50%)]" />
        
        {/* Grid Pattern Overlay */}
        <div className="fixed inset-0 grid-pattern opacity-30" />
        
        <Navigation />
        <main className="container mx-auto px-4 sm:px-6 md:px-8 py-6 md:py-8 relative z-10">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/browser-use" element={<BrowserUse />} />
            <Route path="/results" element={<TestResults />} />
            <Route path="/quick-test" element={<QuickTest />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
