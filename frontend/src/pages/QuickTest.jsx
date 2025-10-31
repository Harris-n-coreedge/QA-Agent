import { useEffect, useState } from 'react'
import { Activity, BarChart3, Zap, Loader, CheckCircle, AlertCircle } from 'lucide-react'
import { sessionsAPI } from '../api/client'
import ApprovalPrompt from '../components/ApprovalPrompt'
import ResultVisualization from '../components/ResultVisualization'

const providers = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google' },
]

export default function QuickTest() {
  const [websiteUrl, setWebsiteUrl] = useState('https://www.w3schools.com/')
  const [aiProvider, setAiProvider] = useState('google')
  const [session, setSession] = useState(null)
  const [running, setRunning] = useState(false)
  const [resultText, setResultText] = useState('')
  const [mobileImages, setMobileImages] = useState([])
  const [selectedDevice, setSelectedDevice] = useState('iPhone 17 Pro Max')
  const [custom, setCustom] = useState({ width: '', height: '', deviceScaleFactor: '1', name: '' })
  const [lightbox, setLightbox] = useState({ open: false, src: '' })

  // Use globally shared default session; fetch once and refresh status periodically
  useEffect(() => {
    let alive = true
    const fetchDefault = async () => {
      try {
        const res = await sessionsAPI.sessionDefault()
        if (alive) setSession(res)
      } catch (_) {
        // ignore; dashboard will surface health
      }
    }
    fetchDefault()
    const id = setInterval(fetchDefault, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])

  const runCommand = async (command) => {
    if (!session?.session_id) return
    setRunning(true)
    setResultText('')
    // Show only current test output: clear any previous mobile screenshots
    setMobileImages([])
    try {
      // Ensure session is active; retry briefly if not
      if (session.status !== 'active') {
        try {
          const timeoutAt = Date.now() + 20000
          while (Date.now() < timeoutAt) {
            const s = await sessionsAPI.get(session.session_id)
            if (s.status === 'active') {
              setSession(s)
              break
            }
            await new Promise(r => setTimeout(r, 600))
          }
        } catch (_) {}
      }

      let res
      let attempts = 0
      while (attempts < 3) {
        try {
          res = await sessionsAPI.executeCommand(session.session_id, command)
          break
        } catch (err) {
          const code = err?.response?.status
          if (code === 404) {
            await new Promise(r => setTimeout(r, 800))
            attempts++
            continue
          }
          throw err
        }
      }
      setResultText(res?.result || 'Completed')
    } catch (e) {
      setResultText(`Failed: ${e?.response?.data?.detail || e.message}`)
    } finally {
      setRunning(false)
    }
  }

  const runMobile = async () => {
    if (!session?.session_id) return
    setRunning(true)
    setResultText('')
    setMobileImages([])
    try {
      const isCustom = selectedDevice === 'Custom'
      const payload = isCustom
        ? {
            custom: {
              width: Number(custom.width),
              height: Number(custom.height),
              deviceScaleFactor: Number(custom.deviceScaleFactor || 1),
              name: custom.name || `Custom ${custom.width}x${custom.height}`,
            },
          }
        : { deviceName: selectedDevice }
      // Ensure session is active; retry briefly if not
      if (session.status !== 'active') {
        try {
          const timeoutAt = Date.now() + 20000
          while (Date.now() < timeoutAt) {
            const s = await sessionsAPI.get(session.session_id)
            if (s.status === 'active') {
              setSession(s)
              break
            }
            await new Promise(r => setTimeout(r, 600))
          }
        } catch (_) {}
      }

      let res
      let attempts = 0
      while (attempts < 5) {
        try {
          res = await sessionsAPI.mobileTest(session.session_id, payload)
          break
        } catch (err) {
          const code = err?.response?.status
          if (code === 404) {
            await new Promise(r => setTimeout(r, 900))
            attempts++
            continue
          }
          throw err
        }
      }
      setResultText(res?.message || 'Mobile test done')
      // cache-bust each image URL
      const shots = (res?.screenshots || []).map((u) => `${u}?t=${Date.now()}`)
      setMobileImages(shots)
    } catch (e) {
      setResultText(`Failed: ${e?.response?.data?.detail || e.message}`)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-6 md:space-y-8 fade-in">
      {/* Page Header */}
      <div className="slide-in text-center">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-black text-gradient text-glow mb-3 tracking-tight">
          Quick Test
        </h1>
        <p className="text-white/70 text-sm md:text-base font-medium tracking-wide max-w-2xl mx-auto px-4">
          Enter a website and quickly run core QA checks powered by the agent
        </p>
      </div>

      {/* Configuration Card */}
      <div className="card hover-lift">
        <div className="flex items-center space-x-3 md:space-x-4 mb-5">
          <div className="bg-gradient-to-br from-blue-500/25 to-indigo-500/15 p-3 rounded-2xl border border-blue-500/30 shadow-xl">
            <Activity className="w-6 h-6 md:w-7 md:h-7 text-blue-300" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg md:text-xl font-bold text-gradient text-glow">
              Test Configuration
            </h2>
            <p className="text-xs md:text-sm text-white/60 font-medium hidden md:block">Configure your test environment</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2">
              <label className="label text-xs">Website URL</label>
              <input
                className="input text-sm md:text-base"
                placeholder="https://example.com"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
              />
            </div>
            <div>
              <label className="label text-xs">AI Provider</label>
              <select
                className="input text-sm md:text-base"
                value={aiProvider}
                onChange={(e) => setAiProvider(e.target.value)}
              >
                {providers.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Test Actions Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-5">
        {/* Auto Check */}
        <div className="card-stat group cursor-pointer hover-lift">
          <div className="flex items-start space-x-3 mb-4">
            <div className="bg-gradient-to-br from-green-500/25 to-emerald-500/15 p-3 rounded-2xl border border-green-500/30 shadow-xl group-hover:scale-105 transition-all duration-300">
              <Activity className="w-6 h-6 md:w-7 md:h-7 text-green-300" />
            </div>
            <div className="flex-1">
              <h2 className="text-lg md:text-xl font-bold text-gradient text-glow mb-2">Auto Check</h2>
              <p className="text-white/60 text-xs md:text-sm leading-relaxed">
                Runs baseline QA checks: load, header/footer, auth buttons, performance, security headers, accessibility, and UI scan
              </p>
            </div>
          </div>
          <button
            onClick={() => runCommand('auto check')}
            disabled={!session || running}
            className="btn btn-success w-full text-sm md:text-base"
          >
            {running ? 'Running...' : 'Run Auto Check'}
          </button>
        </div>

        {/* Auto Audit */}
        <div className="card-stat group cursor-pointer hover-lift">
          <div className="flex items-start space-x-3 mb-4">
            <div className="bg-gradient-to-br from-blue-500/25 to-indigo-500/15 p-3 rounded-2xl border border-blue-500/30 shadow-xl group-hover:scale-105 transition-all duration-300">
              <BarChart3 className="w-6 h-6 md:w-7 md:h-7 text-blue-300" />
            </div>
            <div className="flex-1">
              <h2 className="text-lg md:text-xl font-bold text-gradient text-glow mb-2">Auto Audit</h2>
              <p className="text-white/60 text-xs md:text-sm leading-relaxed">
                Performs SEO, link health, images, cookies, resources, and forms audit with actionable suggestions
              </p>
            </div>
          </div>
          <button
            onClick={() => runCommand('auto audit')}
            disabled={!session || running}
            className="btn btn-info w-full text-sm md:text-base"
          >
            {running ? 'Running...' : 'Run Auto Audit'}
          </button>
        </div>

        {/* Cross-Browser */}
        <div className="card-stat group cursor-pointer hover-lift">
          <div className="flex items-start space-x-3 mb-4">
            <div className="bg-gradient-to-br from-purple-500/25 to-pink-500/15 p-3 rounded-2xl border border-purple-500/30 shadow-xl group-hover:scale-105 transition-all duration-300">
              <Zap className="w-6 h-6 md:w-7 md:h-7 text-purple-300" />
            </div>
            <div className="flex-1">
              <h2 className="text-lg md:text-xl font-bold text-gradient text-glow mb-2">Cross-Browser</h2>
              <p className="text-white/60 text-xs md:text-sm leading-relaxed">
                Opens Chromium, Firefox, and WebKit to validate basic load and collect screenshots
              </p>
            </div>
          </div>
          <button
            onClick={() => runCommand('cross-browser test')}
            disabled={!session || running}
            className="btn btn-primary w-full text-sm md:text-base"
          >
            {running ? 'Running...' : 'Run Cross-Browser'}
          </button>
        </div>

        {/* Mobile Test */}
        <div className="card-stat group cursor-pointer hover-lift">
          <div className="flex items-start space-x-3 mb-4">
            <div className="bg-gradient-to-br from-orange-500/25 to-amber-500/15 p-3 rounded-2xl border border-orange-500/30 shadow-xl group-hover:scale-105 transition-all duration-300">
              <Activity className="w-6 h-6 md:w-7 md:h-7 text-orange-300" />
            </div>
            <div className="flex-1">
              <h2 className="text-lg md:text-xl font-bold text-gradient text-glow mb-2">Mobile Test</h2>
              <p className="text-white/60 text-xs md:text-sm leading-relaxed mb-4">
                Simulates a mobile viewport, scrolls the page, and captures screenshots to validate responsiveness
              </p>

              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2 gap-4">
                  <div>
                    <label className="label text-xs md:text-sm">Device</label>
                    <select
                      className="input text-sm md:text-base"
                      value={selectedDevice}
                      onChange={(e) => setSelectedDevice(e.target.value)}
                    >
                      <option>iPhone 17 Pro Max</option>
                      <option>iPhone 17 Pro</option>
                      <option>iPhone 17</option>
                      <option>Samsung Galaxy S25 Ultra</option>
                      <option>iPad</option>
                      <option>iPad Pro</option>
                      <option>Custom</option>
                    </select>
                  </div>
                </div>

                {selectedDevice === 'Custom' && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4 bg-gradient-to-br from-white/10 to-white/5 p-4 md:p-6 rounded-2xl border border-white/15">
                    <div>
                      <label className="label text-xs md:text-sm">Width</label>
                      <input
                        className="input text-sm md:text-base"
                        value={custom.width}
                        onChange={(e) => setCustom({ ...custom, width: e.target.value })}
                        placeholder="375"
                      />
                    </div>
                    <div>
                      <label className="label text-xs md:text-sm">Height</label>
                      <input
                        className="input text-sm md:text-base"
                        value={custom.height}
                        onChange={(e) => setCustom({ ...custom, height: e.target.value })}
                        placeholder="667"
                      />
                    </div>
                    <div>
                      <label className="label text-xs md:text-sm">Scale</label>
                      <input
                        className="input text-sm md:text-base"
                        value={custom.deviceScaleFactor}
                        onChange={(e) => setCustom({ ...custom, deviceScaleFactor: e.target.value })}
                        placeholder="1"
                      />
                    </div>
                    <div className="col-span-2 md:col-span-3">
                      <label className="label text-xs md:text-sm">Name (optional)</label>
                      <input
                        className="input text-sm md:text-base"
                        value={custom.name}
                        onChange={(e) => setCustom({ ...custom, name: e.target.value })}
                        placeholder="My Phone"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={runMobile}
            disabled={!session || running}
            className="btn btn-primary w-full text-sm md:text-base"
          >
            {running ? 'Running...' : 'Run Mobile Test'}
          </button>
        </div>
      </div>

      {/* Results Section - Enhanced Visualization */}
      {resultText && (
        <div className="card fade-in hover-lift">
          <div className="flex items-center space-x-3 md:space-x-4 mb-5">
            <div className="bg-gradient-to-br from-green-500/25 to-emerald-500/15 p-3 rounded-2xl border border-green-500/30 shadow-xl">
              <CheckCircle className="w-6 h-6 md:w-7 md:h-7 text-green-300" />
            </div>
            <div>
              <h3 className="text-lg md:text-xl font-bold text-gradient text-glow">Latest Result</h3>
              <p className="text-white/60 text-xs md:text-sm font-medium hidden md:block">Test execution output</p>
            </div>
          </div>
          <ResultVisualization rawOutput={resultText} />
        </div>
      )}

      {/* Mobile Screenshots Section */}
      {mobileImages?.length > 0 && (
        <div className="card fade-in hover-lift">
          <div className="flex items-center space-x-4 md:space-x-6 mb-8">
            <div className="bg-gradient-to-br from-purple-500/25 to-pink-500/15 p-4 md:p-6 rounded-3xl border border-purple-500/30 shadow-2xl">
              <Activity className="w-10 h-10 md:w-12 md:h-12 text-purple-300" />
            </div>
            <div>
              <h3 className="text-2xl md:text-3xl lg:text-4xl font-bold text-gradient text-glow">
                Mobile Screenshots
              </h3>
              <p className="text-white/70 text-sm md:text-base font-medium hidden md:block">
                {mobileImages.length} {mobileImages.length === 1 ? 'screenshot' : 'screenshots'} captured
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {mobileImages.map((src, idx) => (
              <button
                key={idx}
                onClick={() => setLightbox({ open: true, src })}
                style={{ animationDelay: `${idx * 0.1}s` }}
                className="bg-gradient-to-br from-white/10 to-white/5 border border-white/15 rounded-2xl overflow-hidden transform transition-all duration-500 hover:scale-[1.05] hover:shadow-2xl hover:shadow-purple-500/20 hover:border-white/30 group fade-in"
              >
                <div className="relative overflow-hidden">
                  <img
                    src={src}
                    alt={`Mobile screenshot ${idx + 1}`}
                    className="w-full h-auto object-contain transition-transform duration-700 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  <div className="absolute bottom-4 left-4 right-4 text-white font-bold text-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    Screenshot {idx + 1}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {running && (
        <div className="card text-center py-16 fade-in">
          <div className="flex flex-col items-center justify-center">
            <Loader className="w-16 h-16 md:w-20 md:h-20 text-white animate-spin mb-8" />
            <h3 className="text-3xl md:text-4xl lg:text-5xl font-black text-gradient text-glow mb-4">
              Running Test...
            </h3>
            <p className="text-white/80 text-lg md:text-xl font-medium">
              Please wait while we execute your test
            </p>
          </div>
        </div>
      )}

      {/* Enhanced Lightbox */}
      {lightbox.open && (
        <div
          className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4 md:p-6 animate-fadeIn"
          onClick={() => setLightbox({ open: false, src: '' })}
        >
          <div className="relative max-h-[90vh] max-w-[90vw]">
            <img
              src={lightbox.src}
              alt="Screenshot preview"
              className="max-h-[90vh] max-w-[90vw] object-contain rounded-2xl shadow-2xl border border-white/20"
            />
            <button
              className="absolute -top-4 -right-4 md:-top-6 md:-right-6 bg-white/10 hover:bg-white/20 text-white rounded-full p-3 md:p-4 border border-white/30 backdrop-blur-xl transition-all duration-300 hover:scale-110 hover:rotate-90"
              onClick={(e) => {
                e.stopPropagation()
                setLightbox({ open: false, src: '' })
              }}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Confidence Scoring Approval Prompt */}
      <ApprovalPrompt />
    </div>
  )
}


