import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Activity, TestTube, Zap, BarChart3, Settings } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import BrowserUse from './pages/BrowserUse'
import TestResults from './pages/TestResults'
import QuickTest from './pages/QuickTest'

function Navigation() {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Activity, label: 'Dashboard' },
    { path: '/browser-use', icon: Zap, label: 'Browser Use' },
    { path: '/results', icon: BarChart3, label: 'Test Results' },
    { path: '/quick-test', icon: Activity, label: 'Quick Test' },
  ]

  return (
    <nav className="bg-gradient-to-r from-white/10 to-white/5 backdrop-blur-3xl border-b border-white/20 sticky top-0 z-50 shadow-2xl">
      <div className="container mx-auto px-8">
        <div className="flex items-center justify-between h-24">
          <div className="flex items-center space-x-16">
            <Link to="/" className="flex items-center space-x-4 group">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-white/10 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <TestTube className="w-12 h-12 text-white transition-all duration-700 group-hover:scale-110 group-hover:rotate-12 group-hover:text-white/90 relative z-10" />
              </div>
              <span className="text-3xl font-bold text-gradient text-glow group-hover:scale-105 transition-transform duration-500">
                QA Agent
              </span>
            </Link>

            <div className="flex space-x-3">
              {navItems.map((item, idx) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    style={{ animationDelay: `${idx * 0.15}s` }}
                    className={`flex items-center space-x-4 px-8 py-4 rounded-2xl transition-all duration-700 transform relative overflow-hidden group ${
                      isActive
                        ? 'bg-gradient-to-r from-white/15 to-white/10 text-white shadow-2xl shadow-white/25 border border-white/30 scale-105'
                        : 'text-white/70 hover:bg-gradient-to-r hover:from-white/10 hover:to-white/5 hover:text-white hover:scale-105 hover:border-white/20 border border-transparent'
                    }`}
                  >
                    {isActive && (
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/8 to-transparent animate-shimmer" />
                    )}
                    <Icon className={`w-6 h-6 transition-all duration-500 ${isActive ? 'text-white scale-110' : 'group-hover:scale-125 group-hover:text-white'}`} />
                    <span className="relative z-10 font-bold text-lg tracking-wide">{item.label}</span>
                    {isActive && (
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white to-transparent rounded-full" />
                    )}
                  </Link>
                )
              })}
            </div>
          </div>

          <button className="text-white/70 hover:text-white transition-all duration-500 hover:rotate-90 hover:scale-110 p-4 rounded-2xl hover:bg-gradient-to-r hover:from-white/10 hover:to-white/5 border border-transparent hover:border-white/20 hover:shadow-lg hover:shadow-white/10">
            <Settings className="w-7 h-7" />
          </button>
        </div>
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
        <main className="container mx-auto px-8 py-16 relative z-10">
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
