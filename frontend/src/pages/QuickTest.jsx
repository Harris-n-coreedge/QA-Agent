import { useEffect, useState } from 'react'
import { sessionsAPI } from '../api/client'

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
        {session?.session_id ? (
          <div className="text-sm text-white/70">
            Using global session: <span className="font-mono">{session.session_id}</span> (<span>{session.status}</span>)
          </div>
        ) : (
          <div className="text-sm text-white/60">Waiting for global session...</div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-semibold text-white">Auto Check</h2>
          <p className="text-white/70 text-sm">Runs baseline QA checks: load, header/footer, auth buttons, performance, security headers, accessibility, and UI scan.</p>
          <button
            onClick={() => runCommand('auto check')}
            disabled={!session || running}
            className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 disabled:opacity-50"
          >Run Auto Check</button>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-semibold text-white">Auto Audit</h2>
          <p className="text-white/70 text-sm">Performs SEO, link health, images, cookies, resources, and forms audit with actionable suggestions.</p>
          <button
            onClick={() => runCommand('auto audit')}
            disabled={!session || running}
            className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 disabled:opacity-50"
          >Run Auto Audit</button>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-3">
          <h2 className="text-xl font-semibold text-white">Cross-Browser</h2>
          <p className="text-white/70 text-sm">Opens Chromium, Firefox, and WebKit to validate basic load and collect screenshots.</p>
          <button
            onClick={() => runCommand('cross-browser test')}
            disabled={!session || running}
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
              disabled={!session || running}
              className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white border border-white/20 disabled:opacity-50"
            >Run Mobile Test</button>
          </div>
        </div>
      </div>

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


