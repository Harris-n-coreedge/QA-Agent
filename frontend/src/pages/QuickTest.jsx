import { useEffect, useState } from 'react'
import { Activity, BarChart3, Globe, Smartphone, CheckCircle2, XCircle, AlertCircle, Search, Link2, Image, Cookie, Package, FileText, ClipboardList, Lightbulb, Chrome, Compass, BookOpen } from 'lucide-react'
import { agentAPI } from '../api/client'
import { TestTemplates } from '../components/TestTemplates'
import { TestSuites } from '../components/TestSuites'
import { ScreenshotGallery } from '../components/ScreenshotGallery'
import { useToast } from '../contexts/ToastContext'
import { useNotifications } from '../components/NotificationCenter'

const providers = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'google', label: 'Google' },
]

export default function QuickTest() {
  const [websiteUrl, setWebsiteUrl] = useState('https://www.w3schools.com/')
  const [aiProvider, setAiProvider] = useState('google')
  const [agentStatus, setAgentStatus] = useState(null)
  const [running, setRunning] = useState(false)
  const [resultText, setResultText] = useState('')
  const [structuredResult, setStructuredResult] = useState(null)
  const [mobileImages, setMobileImages] = useState([])
  const [selectedDevice, setSelectedDevice] = useState('iPhone 17 Pro Max')
  const [custom, setCustom] = useState({ width: '', height: '', deviceScaleFactor: '1', name: '' })
  const [lightbox, setLightbox] = useState({ open: false, src: '' })
  const [showBrowser, setShowBrowser] = useState(false)
  const [browserScreenshot, setBrowserScreenshot] = useState(null)
  const [browserUrl, setBrowserUrl] = useState(null)
  const [currentBrowser, setCurrentBrowser] = useState(null) // For cross-browser test
  const [crossBrowserResults, setCrossBrowserResults] = useState(null)
  const [showTemplates, setShowTemplates] = useState(false)
  const [showSuites, setShowSuites] = useState(false)
  const toast = useToast()
  const { addNotification } = useNotifications()

  // Fetch agent status periodically
  useEffect(() => {
    let alive = true
    const fetchStatus = async () => {
      try {
        const res = await agentAPI.getStatus()
        if (alive) setAgentStatus(res)
      } catch (_) {
        // ignore; dashboard will surface health
      }
    }
    fetchStatus()
    const id = setInterval(fetchStatus, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])

  const runCommand = async (command) => {
    setRunning(true)
    setResultText('')
    setStructuredResult(null)
    const loadingToast = toast.loading(`Running ${command}...`)
    setMobileImages([])
    
    // Show embedded browser before starting test
    setShowBrowser(true)
    
    try {
      // Wait for agent to be ready if initializing
      if (agentStatus?.status === 'initializing') {
        let attempts = 0
        while (attempts < 10) {
          await new Promise(r => setTimeout(r, 1000))
          const status = await agentAPI.getStatus()
          if (status.status === 'active') {
            setAgentStatus(status)
            break
          } else if (status.status === 'failed') {
            throw new Error(status.error || 'Agent initialization failed')
          }
          attempts++
        }
      }

      // Navigate to the website URL before running the command
      if (websiteUrl && websiteUrl.trim()) {
        try {
          const navResult = await agentAPI.navigateToUrl(websiteUrl.trim())
          console.log('Navigation result:', navResult)
          // Update browser URL after navigation
          if (navResult.actual_url) {
            setBrowserUrl(navResult.actual_url)
          }
          // Small delay to ensure navigation completes
          await new Promise(r => setTimeout(r, 1000))
        } catch (navError) {
          console.error('Navigation error:', navError)
          const errorMsg = navError?.response?.data?.detail || navError?.message || 'Navigation failed'
          setResultText(`Navigation failed: ${errorMsg}`)
          throw new Error(`Failed to navigate to ${websiteUrl}: ${errorMsg}`)
        }
      }

      // Start screenshot polling during test execution
      let screenshotInterval = null
      screenshotInterval = setInterval(async () => {
        try {
          const browserView = await agentAPI.getBrowserView()
          if (browserView.active && browserView.screenshot_data_url) {
            setBrowserScreenshot(browserView.screenshot_data_url)
            setBrowserUrl(browserView.page_url)
          }
        } catch (e) {
          console.warn('Could not get browser screenshot:', e)
        }
      }, 500) // Poll every 500ms for smooth view

      try {
        // Execute command
        const res = await agentAPI.executeCommand(command)
        
        // Stop screenshot polling
        if (screenshotInterval) clearInterval(screenshotInterval)
        
        // Parse result - could be JSON string or plain text
        let resultData = res?.result || 'Completed'
        let parsed = null
        
        try {
          parsed = JSON.parse(resultData)
          if (parsed.text && parsed.structured) {
            // Structured result with both text and structured data
            setResultText(parsed.text)
            setStructuredResult(parsed.structured)
          } else {
            // Plain text result
            setResultText(resultData)
            setStructuredResult(null)
          }
        } catch (e) {
          // Not JSON, treat as plain text
          setResultText(resultData)
          setStructuredResult(null)
        }
        
        // Hide browser when results arrive
        setShowBrowser(false)
        setBrowserScreenshot(null)
        setBrowserUrl(null)

        toast.success(`${command} completed`)
      } catch (cmdError) {
        // Stop screenshot polling on error
        if (screenshotInterval) clearInterval(screenshotInterval)
        throw cmdError
      }
    } catch (e) {
      setResultText(`Failed: ${e?.response?.data?.detail || e.message}`)
      // Hide browser on error
      setShowBrowser(false)
      setBrowserScreenshot(null)
      setBrowserUrl(null)

      const errorMessage = e?.response?.data?.detail || e.message || `Failed to run ${command}`
      toast.error(errorMessage)
    } finally {
      if (loadingToast) {
        toast.removeToast(loadingToast)
      }
      setRunning(false)
    }
  }

  const runMobile = async () => {
    setRunning(true)
    setResultText('')
    setMobileImages([])
    
    // Show embedded browser before starting test
    setShowBrowser(true)
    
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

      // Wait for agent to be ready if initializing
      if (agentStatus?.status === 'initializing') {
        let attempts = 0
        while (attempts < 10) {
          await new Promise(r => setTimeout(r, 1000))
          const status = await agentAPI.getStatus()
          if (status.status === 'active') {
            setAgentStatus(status)
            break
          } else if (status.status === 'failed') {
            throw new Error(status.error || 'Agent initialization failed')
          }
          attempts++
        }
      }

      // Navigate to the website URL before running the mobile test
      if (websiteUrl && websiteUrl.trim()) {
        try {
          const navResult = await agentAPI.navigateToUrl(websiteUrl.trim())
          console.log('Navigation result:', navResult)
          // Update browser URL after navigation
          if (navResult.actual_url) {
            setBrowserUrl(navResult.actual_url)
          }
          // Small delay to ensure navigation completes
          await new Promise(r => setTimeout(r, 1000))
        } catch (navError) {
          console.error('Navigation error:', navError)
          const errorMsg = navError?.response?.data?.detail || navError?.message || 'Navigation failed'
          setResultText(`Navigation failed: ${errorMsg}`)
          throw new Error(`Failed to navigate to ${websiteUrl}: ${errorMsg}`)
        }
      }

      // Start screenshot polling during test execution
      let screenshotInterval = null
      screenshotInterval = setInterval(async () => {
        try {
          const browserView = await agentAPI.getBrowserView()
          if (browserView.active && browserView.screenshot_data_url) {
            setBrowserScreenshot(browserView.screenshot_data_url)
            setBrowserUrl(browserView.page_url)
          }
        } catch (e) {
          console.warn('Could not get browser screenshot:', e)
        }
      }, 500) // Poll every 500ms for smooth view

      try {
        const res = await agentAPI.mobileTest(payload)
        
        // Stop screenshot polling
        if (screenshotInterval) clearInterval(screenshotInterval)
        
        setResultText(res?.message || 'Mobile test done')
        // cache-bust each image URL
        const shots = (res?.screenshots || []).map((u) => `${u}?t=${Date.now()}`)
        setMobileImages(shots)
        
        // Hide browser when results arrive
        setShowBrowser(false)
        setBrowserScreenshot(null)
        setBrowserUrl(null)
      } catch (testError) {
        // Stop screenshot polling on error
        if (screenshotInterval) clearInterval(screenshotInterval)
        throw testError
      }
    } catch (e) {
      setResultText(`Failed: ${e?.response?.data?.detail || e.message}`)
      // Hide browser on error
      setShowBrowser(false)
      setBrowserScreenshot(null)
      setBrowserUrl(null)
    } finally {
      setRunning(false)
    }
  }

  const runCrossBrowserTest = async () => {
    setRunning(true)
    setResultText('')
    setMobileImages([])
    setCrossBrowserResults(null)
    
    // Show embedded browser before starting test
    setShowBrowser(true)
    setCurrentBrowser('Initializing...')
    
    try {
      // Wait for agent to be ready if initializing
      if (agentStatus?.status === 'initializing') {
        let attempts = 0
        while (attempts < 10) {
          await new Promise(r => setTimeout(r, 1000))
          const status = await agentAPI.getStatus()
          if (status.status === 'active') {
            setAgentStatus(status)
            break
          } else if (status.status === 'failed') {
            throw new Error(status.error || 'Agent initialization failed')
          }
          attempts++
        }
      }

      // Navigate to the website URL before running the cross-browser test
      if (websiteUrl && websiteUrl.trim()) {
        try {
          const navResult = await agentAPI.navigateToUrl(websiteUrl.trim())
          if (navResult.actual_url) {
            setBrowserUrl(navResult.actual_url)
          }
          await new Promise(r => setTimeout(r, 1000))
        } catch (navError) {
          console.error('Navigation error:', navError)
          const errorMsg = navError?.response?.data?.detail || navError?.message || 'Navigation failed'
          setResultText(`Navigation failed: ${errorMsg}`)
          throw new Error(`Failed to navigate to ${websiteUrl}: ${errorMsg}`)
        }
      }

      // Start screenshot polling during test execution
      let screenshotInterval = null
      screenshotInterval = setInterval(async () => {
        try {
          const browserView = await agentAPI.getBrowserView()
          if (browserView.active && browserView.screenshot_data_url) {
            setBrowserScreenshot(browserView.screenshot_data_url)
            setBrowserUrl(browserView.page_url)
          }
        } catch (e) {
          console.warn('Could not get browser screenshot:', e)
        }
      }, 500)

      // Run cross-browser test - test each browser sequentially
      const browsers = ['chromium', 'firefox', 'webkit']
      const testResults = {}
      
      for (const browserType of browsers) {
        try {
          // Show which browser is being tested
          setCurrentBrowser(`Testing ${browserType.charAt(0).toUpperCase() + browserType.slice(1)}...`)
          
          // Call the cross-browser test endpoint for this specific browser
          const res = await agentAPI.crossBrowserTest(websiteUrl?.trim() || null, browserType)
          
          // Extract result for current browser
          if (res.browsers && res.browsers[browserType]) {
            testResults[browserType] = res.browsers[browserType]
            
            // Update screenshot if available
            if (res.browsers[browserType].screenshot) {
              setBrowserScreenshot(res.browsers[browserType].screenshot)
            }
          }
          
          // Small delay between browsers for visual feedback
          await new Promise(r => setTimeout(r, 500))
        } catch (e) {
          testResults[browserType] = { status: 'failed', error: e.message }
        }
      }
      
      // Stop screenshot polling
      if (screenshotInterval) clearInterval(screenshotInterval)
      
      // Format results
      const resultLines = ["Cross-Browser Test Results:"]
      for (const [browser, result] of Object.entries(testResults)) {
        if (result.status === 'success') {
          resultLines.push(`   ${browser.charAt(0).toUpperCase() + browser.slice(1)}: Success - ${result.title}`)
        } else {
          resultLines.push(`   ${browser.charAt(0).toUpperCase() + browser.slice(1)}: Failed - ${result.error || 'Unknown error'}`)
        }
      }
      
      setResultText(resultLines.join('\n'))
      setCrossBrowserResults(testResults)
      
      // Hide browser when results arrive
      setShowBrowser(false)
      setBrowserScreenshot(null)
      setBrowserUrl(null)
      setCurrentBrowser(null)
    } catch (e) {
      setResultText(`Failed: ${e?.response?.data?.detail || e.message}`)
      // Hide browser on error
      setShowBrowser(false)
      setBrowserScreenshot(null)
      setBrowserUrl(null)
      setCurrentBrowser(null)
    } finally {
      setRunning(false)
    }
  }

  const handleTemplateSelect = (template) => {
    if (template.websiteUrl) {
      setWebsiteUrl(template.websiteUrl)
    }
    setAiProvider(template.provider)
    toast.info(`Template "${template.name}" loaded`)
  }

  const handleRunTemplate = async (template) => {
    if (template.websiteUrl) {
      setWebsiteUrl(template.websiteUrl)
    }
    setAiProvider(template.provider)
    
    // Small delay to ensure state updates
    setTimeout(() => {
      if (template.command === 'auto check') {
        runCommand('auto check')
      } else if (template.command === 'auto audit') {
        runCommand('auto audit')
      } else if (template.command === 'cross-browser') {
        runCrossBrowserTest()
      }
    }, 100)
  }

  return (
    <div className="space-y-6">
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="page-title">Quick Test</h1>
            <p className="page-description">
              Enter a website and quickly run core QA checks
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setShowTemplates(!showTemplates)
                setShowSuites(false)
              }}
              className="btn btn-secondary"
            >
              <BookOpen className="w-4 h-4" />
              <span>{showTemplates ? 'Hide' : 'Show'} Templates</span>
            </button>
            <button
              onClick={() => {
                setShowSuites(!showSuites)
                setShowTemplates(false)
              }}
              className="btn btn-secondary"
            >
              <BookOpen className="w-4 h-4" />
              <span>{showSuites ? 'Hide' : 'Show'} Suites</span>
            </button>
          </div>
        </div>
      </div>

      {showTemplates && (
        <div className="card p-6">
          <TestTemplates
            onSelectTemplate={handleTemplateSelect}
            onRunTemplate={handleRunTemplate}
          />
        </div>
      )}

      {showSuites && (
        <div className="card p-6">
          <TestSuites
            onRunSuite={(suite) => {
              toast.info(`Running test suite: ${suite.name}`)
              // Handle suite execution
            }}
          />
        </div>
      )}

      <div className="card p-5 md:p-6 space-y-5 md:space-y-6">
        <div>
          <h2 className="text-base md:text-lg font-semibold text-white mb-3 md:mb-4">Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="label">Website URL</label>
              <input
                className="input"
                placeholder="https://example.com"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
              />
            </div>
            <div>
              <label className="label">Provider</label>
              <select
                className="input"
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
        {agentStatus ? (
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="status-dot success" />
            <span className="font-medium">System Status:</span>
            <span className="font-mono text-slate-400">{agentStatus.status}</span>
            {agentStatus.commands_executed > 0 && (
              <span className="ml-2 text-slate-400">({agentStatus.commands_executed} commands executed)</span>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <div className="status-dot info" />
            <span>Initializing system...</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card hover-lift p-5 md:p-6 space-y-4">
          <div className="flex items-center gap-3 md:gap-4">
            <div className="p-2.5 md:p-3 rounded-lg bg-slate-700/50 border border-slate-600/50 flex-shrink-0">
              <Activity className="w-5 h-5 md:w-6 md:h-6 text-slate-300" />
            </div>
            <div className="min-w-0">
              <h2 className="text-lg md:text-xl font-semibold text-white mb-0.5">Auto Check</h2>
              <p className="text-xs md:text-sm text-slate-400">Comprehensive QA baseline checks</p>
            </div>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">Runs baseline QA checks: load, header/footer, auth buttons, performance, security headers, accessibility, and UI scan.</p>
          <button
            onClick={() => runCommand('auto check')}
            disabled={running}
            className="btn btn-primary w-full"
          >
            {running ? 'Running...' : 'Run Auto Check'}
          </button>
        </div>

        <div className="card hover-lift p-5 md:p-6 space-y-4">
          <div className="flex items-center gap-3 md:gap-4">
            <div className="p-2.5 md:p-3 rounded-lg bg-slate-700/50 border border-slate-600/50 flex-shrink-0">
              <BarChart3 className="w-5 h-5 md:w-6 md:h-6 text-slate-300" />
            </div>
            <div className="min-w-0">
              <h2 className="text-lg md:text-xl font-semibold text-white mb-0.5">Auto Audit</h2>
              <p className="text-xs md:text-sm text-slate-400">Deep analysis and recommendations</p>
            </div>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">Performs SEO, link health, images, cookies, resources, and forms audit with actionable suggestions.</p>
          <button
            onClick={() => runCommand('auto audit')}
            disabled={running}
            className="btn btn-primary w-full"
          >
            {running ? 'Running...' : 'Run Auto Audit'}
          </button>
        </div>

        <div className="card hover-lift p-5 md:p-6 space-y-4">
          <div className="flex items-center gap-3 md:gap-4">
            <div className="p-2.5 md:p-3 rounded-lg bg-slate-700/50 border border-slate-600/50 flex-shrink-0">
              <Globe className="w-5 h-5 md:w-6 md:h-6 text-slate-300" />
            </div>
            <div className="min-w-0">
              <h2 className="text-lg md:text-xl font-semibold text-white mb-0.5">Cross-Browser</h2>
              <p className="text-xs md:text-sm text-slate-400">Multi-browser validation</p>
            </div>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed">Opens Chromium, Firefox, and WebKit to validate basic load and collect screenshots.</p>
          <button
            onClick={() => runCrossBrowserTest()}
            disabled={running}
            className="btn btn-primary w-full"
          >
            {running ? 'Running...' : 'Run Cross-Browser'}
          </button>
        </div>

        <div className="card-premium space-y-4 group hover:border-pink-400/40">
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-pink-500/30 to-rose-500/30 p-3 rounded-xl border border-pink-400/40">
              <Smartphone className="w-6 h-6 text-pink-200" />
            </div>
            <h2 className="text-2xl font-black text-gradient text-glow">Mobile</h2>
          </div>
          <p className="text-white/80 text-sm leading-relaxed">Simulates a mobile viewport, scrolls the page, and captures screenshots to validate responsiveness. Images render below.</p>
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-sm text-white/70 mb-1">Device</label>
                <select
                  className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white"
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
              {selectedDevice === 'Custom' && (
                <div className="md:col-span-2 grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-sm text-white/70 mb-1">Width</label>
                    <input
                      className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white"
                      value={custom.width}
                      onChange={(e) => setCustom({ ...custom, width: e.target.value })}
                      placeholder="375"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-white/70 mb-1">Height</label>
                    <input
                      className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white"
                      value={custom.height}
                      onChange={(e) => setCustom({ ...custom, height: e.target.value })}
                      placeholder="667"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-white/70 mb-1">Scale</label>
                    <input
                      className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white"
                      value={custom.deviceScaleFactor}
                      onChange={(e) => setCustom({ ...custom, deviceScaleFactor: e.target.value })}
                      placeholder="1"
                    />
                  </div>
                  <div className="col-span-3">
                    <label className="block text-sm text-white/70 mb-1">Name (optional)</label>
                    <input
                      className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white"
                      value={custom.name}
                      onChange={(e) => setCustom({ ...custom, name: e.target.value })}
                      placeholder="My Phone"
                    />
                  </div>
                </div>
              )}
            </div>
            <button
              onClick={runMobile}
              disabled={running}
              className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 disabled:opacity-50"
            >Run Mobile Test</button>
          </div>
        </div>
      </div>

      {/* Embedded Browser View - Shows screenshots during test execution, hides when results arrive */}
      {showBrowser && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Live Browser View</h3>
          
          {/* Browser Title Bar - Shows which browser is being tested */}
          {currentBrowser && currentBrowser.includes('Testing') && (
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 border border-white/20 rounded-t-xl px-4 py-3 mb-0 flex items-center justify-between shadow-lg">
              <div className="flex items-center gap-3">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <span className="text-white font-semibold">
                  {currentBrowser}
                </span>
              </div>
              <div className="flex items-center gap-3">
                {(() => {
                  const browserMatch = currentBrowser.match(/Testing\s+(\w+)/i)
                  if (browserMatch) {
                    const browserName = browserMatch[1].toLowerCase()
                    const BrowserIcon = browserName === 'chromium' ? Chrome : 
                                      browserName === 'firefox' ? Globe : 
                                      browserName === 'webkit' ? Compass : Globe
                    return (
                      <>
                        <BrowserIcon className="w-5 h-5 text-blue-400" />
                        <button
                          onClick={async () => {
                            try {
                              await agentAPI.openBrowserExternal(websiteUrl?.trim() || null, browserName)
                              console.log(`Opened ${browserName} externally`)
                            } catch (e) {
                              console.error(`Failed to open ${browserName} externally:`, e)
                            }
                          }}
                          className="px-3 py-1.5 text-xs bg-white/20 hover:bg-white/30 text-white rounded-lg border border-white/30 transition-colors"
                          title={`Open ${browserName.charAt(0).toUpperCase() + browserName.slice(1)} externally with full browser UI`}
                        >
                          Open Externally
                        </button>
                      </>
                    )
                  }
                  return null
                })()}
              </div>
            </div>
          )}
          
          {browserScreenshot ? (
            <>
              <div 
                className={`bg-black/40 border border-white/10 rounded-xl overflow-hidden ${currentBrowser && currentBrowser.includes('Testing') ? 'rounded-t-none' : ''}`}
                style={{ height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              >
                <img 
                  src={browserScreenshot} 
                  alt="Live Browser View" 
                  className="max-w-full max-h-full object-contain"
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
              </div>
              {browserUrl && (
                <p className="text-white/50 text-sm mt-2">
                  Current URL: <span className="font-mono text-white/70">{browserUrl}</span>
                </p>
              )}
              <p className="text-white/50 text-sm mt-1">Browser view will close automatically when test completes</p>
            </>
          ) : (
            <div className="bg-black/40 border border-white/10 rounded-xl overflow-hidden flex items-center justify-center" style={{ height: '600px' }}>
              <p className="text-white/70">Initializing browser...</p>
            </div>
          )}
        </div>
      )}

      {resultText && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            {structuredResult?.type === 'auto_check' ? 'Auto Check Results' : 
             structuredResult?.type === 'auto_audit' ? 'Auto Audit Results' : 
             'Latest Result'}
          </h3>
          
          {structuredResult ? (
            <div className="space-y-6">
              {/* Summary Stats */}
              {structuredResult.summary && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {structuredResult.summary.total_checks && (
                    <>
                      <div className="bg-blue-500/20 border border-blue-500/30 rounded-xl p-4 text-center">
                        <div className="text-2xl font-bold text-blue-300">{structuredResult.summary.total_checks}</div>
                        <div className="text-sm text-blue-200/70">Total Checks</div>
                      </div>
                      <div className="bg-green-500/20 border border-green-500/30 rounded-xl p-4 text-center">
                        <div className="text-2xl font-bold text-green-300">{structuredResult.summary.passed}</div>
                        <div className="text-sm text-green-200/70">Passed</div>
                      </div>
                      <div className="bg-yellow-500/20 border border-yellow-500/30 rounded-xl p-4 text-center">
                        <div className="text-2xl font-bold text-yellow-300">{structuredResult.summary.warnings || 0}</div>
                        <div className="text-sm text-yellow-200/70">Warnings</div>
                      </div>
                      <div className="bg-red-500/20 border border-red-500/30 rounded-xl p-4 text-center">
                        <div className="text-2xl font-bold text-red-300">{structuredResult.summary.failed || 0}</div>
                        <div className="text-sm text-red-200/70">Failed</div>
                      </div>
                    </>
                  )}
                  {structuredResult.summary.total_audits && (
                    <>
                      <div className="bg-blue-500/20 border border-blue-500/30 rounded-xl p-4 text-center">
                        <div className="text-2xl font-bold text-blue-300">{structuredResult.summary.total_audits}</div>
                        <div className="text-sm text-blue-200/70">Total Audits</div>
                      </div>
                      <div className="bg-green-500/20 border border-green-500/30 rounded-xl p-4 text-center">
                        <div className="text-2xl font-bold text-green-300">{structuredResult.summary.passed}</div>
                        <div className="text-sm text-green-200/70">Passed</div>
                      </div>
                      <div className="bg-yellow-500/20 border border-yellow-500/30 rounded-xl p-4 text-center">
                        <div className="text-2xl font-bold text-yellow-300">{structuredResult.summary.warnings || 0}</div>
                        <div className="text-sm text-yellow-200/70">Warnings</div>
                      </div>
                      <div className="bg-orange-500/20 border border-orange-500/30 rounded-xl p-4 text-center">
                        <div className="text-2xl font-bold text-orange-300">{structuredResult.summary.issues_found || 0}</div>
                        <div className="text-sm text-orange-200/70">Issues</div>
                      </div>
                    </>
                  )}
                </div>
              )}
              
              {/* Check/Audit Details */}
              {structuredResult.checks && structuredResult.checks.length > 0 && (
                <div className="space-y-4">
                  <h4 className="text-md font-semibold text-white">Check Details</h4>
                  {structuredResult.checks.map((check, idx) => (
                    <div key={idx} className="bg-black/30 border border-white/10 rounded-xl p-4">
                      <div className="flex items-center gap-3 mb-2">
                        {check.status === 'passed' ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                        ) : check.status === 'failed' ? (
                          <XCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-amber-400 flex-shrink-0" />
                        )}
                        <h5 className="text-white font-semibold flex-1">{check.title}</h5>
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                          check.status === 'passed' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                          check.status === 'failed' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                          'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        }`}>
                          {check.status.toUpperCase()}
                        </span>
                      </div>
                      {check.details.length > 0 && (
                        <div className="ml-8 space-y-1 mb-2">
                          {check.details.map((detail, dIdx) => (
                            <p key={dIdx} className="text-white/70 text-sm">{detail}</p>
                          ))}
                        </div>
                      )}
                      {check.suggestions.length > 0 && (
                        <div className="ml-8 mt-3 pt-3 border-t border-slate-700/50">
                          <div className="flex items-center gap-2 mb-2">
                            <Lightbulb className="w-4 h-4 text-amber-400" />
                            <p className="text-amber-300 text-sm font-semibold">Suggestions:</p>
                          </div>
                          {check.suggestions.map((suggestion, sIdx) => (
                            <p key={sIdx} className="text-slate-300 text-sm ml-6">{suggestion}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              {structuredResult.audits && structuredResult.audits.length > 0 && (
                <div className="space-y-4">
                  <h4 className="text-md font-semibold text-white">Audit Details</h4>
                  {structuredResult.audits.map((audit, idx) => (
                    <div key={idx} className="bg-black/30 border border-white/10 rounded-xl p-4">
                      <div className="flex items-center gap-3 mb-2">
                        {audit.name === 'SEO' ? (
                          <Search className="w-5 h-5 text-blue-400 flex-shrink-0" />
                        ) : audit.name === 'Links' ? (
                          <Link2 className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                        ) : audit.name === 'Images' ? (
                          <Image className="w-5 h-5 text-purple-400 flex-shrink-0" />
                        ) : audit.name === 'Cookies' ? (
                          <Cookie className="w-5 h-5 text-amber-400 flex-shrink-0" />
                        ) : audit.name === 'Resources' ? (
                          <Package className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                        ) : audit.name === 'Forms' ? (
                          <FileText className="w-5 h-5 text-green-400 flex-shrink-0" />
                        ) : (
                          <ClipboardList className="w-5 h-5 text-slate-400 flex-shrink-0" />
                        )}
                        <h5 className="text-white font-semibold flex-1">{audit.name}</h5>
                      </div>
                      {audit.details.length > 0 && (
                        <div className="ml-8 space-y-1 mb-2">
                          {audit.details.map((detail, dIdx) => (
                            <p key={dIdx} className="text-white/70 text-sm">{detail}</p>
                          ))}
                        </div>
                      )}
                      {audit.suggestions.length > 0 && (
                        <div className="ml-8 mt-3 pt-3 border-t border-slate-700/50">
                          <div className="flex items-center gap-2 mb-2">
                            <Lightbulb className="w-4 h-4 text-amber-400" />
                            <p className="text-amber-300 text-sm font-semibold">Suggestions:</p>
                          </div>
                          {audit.suggestions.map((suggestion, sIdx) => (
                            <p key={sIdx} className="text-slate-300 text-sm ml-6">{suggestion}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              {/* Raw Text (Collapsible) */}
              <details className="bg-black/20 border border-white/10 rounded-xl p-4">
                <summary className="text-white/70 text-sm cursor-pointer hover:text-white">
                  View Raw Text Output
                </summary>
                <pre className="whitespace-pre-wrap text-white/60 text-xs mt-2">{resultText}</pre>
              </details>
            </div>
          ) : (
            <pre className="whitespace-pre-wrap text-white/80 text-sm">{resultText}</pre>
          )}
        </div>
      )}

      {mobileImages?.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Mobile Screenshots</h3>
          <div className="flex flex-row flex-wrap gap-4">
            {mobileImages.map((src, idx) => (
              <button
                key={idx}
                onClick={() => setLightbox({ open: true, src })}
                className="bg-black/40 border border-white/10 rounded-xl overflow-hidden transform transition-transform hover:scale-[1.03] hover:shadow-lg hover:shadow-black/30"
              >
                <img src={src} alt={`mobile-${idx + 1}`} className="h-96 object-contain" />
              </button>
            ))}
          </div>
        </div>
      )}

      {lightbox.open && (
        <div
          className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-6"
          onClick={() => setLightbox({ open: false, src: '' })}
        >
          <img src={lightbox.src} alt="preview" className="max-h-[90vh] max-w-[90vw] object-contain" />
        </div>
      )}
    </div>
  )
}




