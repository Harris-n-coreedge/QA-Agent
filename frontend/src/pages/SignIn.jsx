import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { TestTube, Mail, Lock, Eye, EyeOff, LogIn } from 'lucide-react'

export default function SignIn() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // TODO: Implement actual authentication API call
      // For now, simulate authentication
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Store auth token (in real app, this would come from API)
      if (rememberMe) {
        localStorage.setItem('rememberMe', 'true')
      }
      
      // Navigate to dashboard
      navigate('/')
    } catch (err) {
      setError(err.message || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center space-x-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-slate-700 rounded-lg blur-md opacity-50 group-hover:opacity-75 transition-opacity" />
              <div className="relative w-12 h-12 bg-gradient-to-br from-slate-700 to-slate-600 rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform shadow-lg">
                <TestTube className="w-6 h-6 text-white" />
              </div>
            </div>
            <span className="text-2xl font-bold text-white">QA Agent</span>
          </Link>
          <p className="text-slate-400 mt-2">Sign in to your account</p>
        </div>

        {/* Sign In Form */}
        <div className="card p-6 md:p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="label">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type="email"
                  className="input pl-10"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="label">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input pl-10 pr-10"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-500 hover:text-white transition-colors"
                  disabled={loading}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500 focus:ring-2"
                  disabled={loading}
                />
                <span className="text-sm text-slate-400">Remember me</span>
              </label>
              <Link
                to="/forgot-password"
                className="text-sm text-slate-400 hover:text-white transition-colors"
              >
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              className="btn btn-primary w-full"
              disabled={loading || !email || !password}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  <span>Sign In</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-400">
              Don't have an account?{' '}
              <Link
                to="/signup"
                className="text-white font-semibold hover:text-slate-300 transition-colors"
              >
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

