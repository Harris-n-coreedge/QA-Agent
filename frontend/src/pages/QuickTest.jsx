import { useEffect, useState } from 'react'
import { agentAPI } from '../api/client'

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
  const [mobileImages, setMobileImages] = useState([])
  const [selectedDevice, setSelectedDevice] = useState('iPhone 17 Pro Max')
  const [custom, setCustom] = useState({ width: '', height: '', deviceScaleFactor: '1', name: '' })
  const [lightbox, setLightbox] = useState({ open: false, src: '' })
  const [showBrowser, setShowBrowser] = useState(false)
  const [browserScreenshot, setBrowserScreenshot] = useState(null)
  const [browserUrl, setBrowserUrl] = useState(null)
  const [currentBrowser, setCurrentBrowser] = useState(null) // For cross-browser test
  const [crossBrowserResults, setCrossBrowserResults] = useState(null)

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
        
        setResultText(res?.result || 'Completed')
        
        // Hide browser when results arrive
        setShowBrowser(false)
        setBrowserScreenshot(null)
        setBrowserUrl(null)
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
    } finally {
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
      const resultLines = ["🌐 Cross-Browser Test Results:"]
      for (const [browser, result] of Object.entries(testResults)) {
        if (result.status === 'success') {
          resultLines.push(`   ✅ ${browser.charAt(0).toUpperCase() + browser.slice(1)}: Success - ${result.title}`)
        } else {
          resultLines.push(`   ❌ ${browser.charAt(0).toUpperCase() + browser.slice(1)}: Failed - ${result.error || 'Unknown error'}`)
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

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Quick Test</h1>
        <p className="text-white/70">Enter a website and quickly run core QA checks powered by the agent.</p>
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="col-span-2">
            <label className="block text-sm text-white/70 mb-1">Website URL</label>
            <input
              className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-white/20"
              placeholder="https://example.com"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm text-white/70 mb-1">AI Provider</label>
            <select
              className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-white/20"
              value={aiProvider}
              onChange={(e) => setAiProvider(e.target.value)}
            >
              {providers.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
        </div>
        {agentStatus ? (
          <div className="text-sm text-white/70">
            Agent Status: <span className="font-mono">{agentStatus.status}</span>
            {agentStatus.commands_executed > 0 && (
              <span className="ml-4">({agentStatus.commands_executed} commands executed)</span>
            )}
          </div>
        ) : (
          <div className="text-sm text-white/60">Waiting for agent...</div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-semibold text-white">Auto Check</h2>
          <p className="text-white/70 text-sm">Runs baseline QA checks: load, header/footer, auth buttons, performance, security headers, accessibility, and UI scan.</p>
          <button
            onClick={() => runCommand('auto check')}
            disabled={running}
            className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 disabled:opacity-50"
          >Run Auto Check</button>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-semibold text-white">Auto Audit</h2>
          <p className="text-white/70 text-sm">Performs SEO, link health, images, cookies, resources, and forms audit with actionable suggestions.</p>
          <button
            onClick={() => runCommand('auto audit')}
            disabled={running}
            className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 disabled:opacity-50"
          >Run Auto Audit</button>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-semibold text-white">Cross-Browser</h2>
          <p className="text-white/70 text-sm">Opens Chromium, Firefox, and WebKit to validate basic load and collect screenshots.</p>
          <button
            onClick={() => runCrossBrowserTest()}
            disabled={running}
            className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 disabled:opacity-50"
          >Run Cross-Browser</button>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-semibold text-white">Mobile</h2>
          <p className="text-white/70 text-sm">Simulates a mobile viewport, scrolls the page, and captures screenshots to validate responsiveness. Images render below.</p>
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
                    const browserIcons = {
                      chromium: '🌐',
                      firefox: '🦊',
                      webkit: '🧭'
                    }
                    return (
                      <>
                        <span className="text-2xl">
                          {browserIcons[browserName] || '🌐'}
                        </span>
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
          <h3 className="text-lg font-semibold text-white mb-2">Latest Result</h3>
          <pre className="whitespace-pre-wrap text-white/80 text-sm">{resultText}</pre>
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




