import { useState, useEffect } from 'react'
import { Save, Bell, Shield, User, Globe, Moon, Sun, Monitor, LogOut, Key, Mail, Trash2, Download, Calendar, Webhook } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import { TestScheduler } from '../components/TestScheduler'
import { WebhookSettings } from '../components/WebhookSettings'

export default function Settings() {
  const navigate = useNavigate()
  const { theme, setTheme } = useTheme()
  
  const handleSignOut = () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('rememberMe')
    navigate('/signin')
  }
  const [activeTab, setActiveTab] = useState('general')
  const [saving, setSaving] = useState(false)
  const [settings, setSettings] = useState({
    // General
    theme: theme,
    language: 'en',
    timezone: 'UTC',
    dateFormat: 'MM/DD/YYYY',
    
    // Profile
    name: 'John Doe',
    email: 'john.doe@example.com',
    company: 'Acme Corp',
    role: 'QA Engineer',
    
    // Notifications
    emailNotifications: true,
    testResults: true,
    systemAlerts: true,
    weeklyReports: false,
    
    // Security
    twoFactorEnabled: false,
    sessionTimeout: 30,
    passwordLastChanged: '2024-01-15',
    
    // API
    apiKey: 'qa_••••••••••••••••••••••••••••',
    apiSecret: '••••••••••••••••••••••••••••',
  })

  const handleSave = async () => {
    setSaving(true)
    // TODO: Implement actual settings save API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
  }

  useEffect(() => {
    setSettings(prev => ({ ...prev, theme }))
  }, [theme])

  const handleChange = (key, value) => {
    setSettings({
      ...settings,
      [key]: value,
    })
    
    // Apply theme immediately when changed
    if (key === 'theme') {
      setTheme(value)
    }
  }

  const tabs = [
    { id: 'general', label: 'General', icon: Monitor },
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'scheduler', label: 'Scheduler', icon: Calendar },
    { id: 'webhooks', label: 'Webhooks', icon: Globe },
  ]

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-description">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Tabs */}
        <div className="lg:col-span-1">
          <div className="card p-4 space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-slate-800 text-white dark:bg-slate-800 dark:text-white'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800/50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* General Settings */}
          {activeTab === 'general' && (
            <div className="card p-6 space-y-6">
              <div>
                  <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">General Settings</h2>
                
                <div className="space-y-5">
                  <div>
                    <label className="label">Theme</label>
                    <div className="grid grid-cols-3 gap-3">
                      {[
                        { value: 'light', icon: Sun, label: 'Light' },
                        { value: 'dark', icon: Moon, label: 'Dark' },
                        { value: 'system', icon: Monitor, label: 'System' },
                      ].map((theme) => {
                        const ThemeIcon = theme.icon
                        return (
                          <button
                            key={theme.value}
                            onClick={() => handleChange('theme', theme.value)}
                            className={`p-4 rounded-lg border-2 transition-all ${
                              settings.theme === theme.value
                                ? 'border-indigo-500 bg-indigo-500/10 dark:border-slate-500 dark:bg-slate-800/50'
                                : 'border-slate-300 dark:border-slate-700 hover:border-slate-400 dark:hover:border-slate-600'
                            }`}
                          >
                            <ThemeIcon className={`w-5 h-5 mx-auto mb-2 ${
                              settings.theme === theme.value 
                                ? 'text-indigo-600 dark:text-slate-300' 
                                : 'text-slate-500 dark:text-slate-400'
                            }`} />
                            <p className={`text-sm ${
                              settings.theme === theme.value 
                                ? 'text-slate-900 dark:text-slate-300 font-semibold' 
                                : 'text-slate-600 dark:text-slate-400'
                            }`}>{theme.label}</p>
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  <div>
                    <label className="label">Language</label>
                    <select
                      className="input"
                      value={settings.language}
                      onChange={(e) => handleChange('language', e.target.value)}
                    >
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                      <option value="de">German</option>
                    </select>
                  </div>

                  <div>
                    <label className="label">Timezone</label>
                    <select
                      className="input"
                      value={settings.timezone}
                      onChange={(e) => handleChange('timezone', e.target.value)}
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time</option>
                      <option value="America/Chicago">Central Time</option>
                      <option value="America/Denver">Mountain Time</option>
                      <option value="America/Los_Angeles">Pacific Time</option>
                    </select>
                  </div>

                  <div>
                    <label className="label">Date Format</label>
                    <select
                      className="input"
                      value={settings.dateFormat}
                      onChange={(e) => handleChange('dateFormat', e.target.value)}
                    >
                      <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                      <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                      <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Profile Settings */}
          {activeTab === 'profile' && (
            <div className="card p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Profile Information</h2>
                
                <div className="space-y-5">
                  <div>
                    <label className="label">Full Name</label>
                    <input
                      type="text"
                      className="input"
                      value={settings.name}
                      onChange={(e) => handleChange('name', e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="label">Email Address</label>
                    <input
                      type="email"
                      className="input"
                      value={settings.email}
                      onChange={(e) => handleChange('email', e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="label">Company</label>
                    <input
                      type="text"
                      className="input"
                      value={settings.company}
                      onChange={(e) => handleChange('company', e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="label">Role</label>
                    <input
                      type="text"
                      className="input"
                      value={settings.role}
                      onChange={(e) => handleChange('role', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Notifications Settings */}
          {activeTab === 'notifications' && (
            <div className="card p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Notification Preferences</h2>
                
                <div className="space-y-4">
                  {[
                    { key: 'emailNotifications', label: 'Email Notifications', description: 'Receive notifications via email' },
                    { key: 'testResults', label: 'Test Results', description: 'Get notified when tests complete' },
                    { key: 'systemAlerts', label: 'System Alerts', description: 'Receive system-wide alerts' },
                    { key: 'weeklyReports', label: 'Weekly Reports', description: 'Get weekly summary reports' },
                  ].map((item) => (
                    <div key={item.key} className="flex items-start justify-between p-4 rounded-lg bg-slate-100 dark:bg-slate-800/50 border border-slate-300 dark:border-slate-700/50">
                      <div className="flex-1">
                        <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">{item.label}</h3>
                        <p className="text-xs text-slate-600 dark:text-slate-400">{item.description}</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings[item.key]}
                          onChange={(e) => handleChange(item.key, e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-slate-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-slate-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <div className="card p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Security Settings</h2>
                
                <div className="space-y-5">
                  <div className="p-4 rounded-lg bg-slate-100 dark:bg-slate-800/50 border border-slate-300 dark:border-slate-700/50">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">Two-Factor Authentication</h3>
                        <p className="text-xs text-slate-600 dark:text-slate-400">Add an extra layer of security to your account</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.twoFactorEnabled}
                          onChange={(e) => handleChange('twoFactorEnabled', e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-slate-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-slate-600"></div>
                      </label>
                    </div>
                    {!settings.twoFactorEnabled && (
                      <button className="btn btn-secondary text-sm">
                        <Key className="w-4 h-4" />
                        <span>Enable 2FA</span>
                      </button>
                    )}
                  </div>

                  <div>
                    <label className="label">Session Timeout (minutes)</label>
                    <select
                      className="input"
                      value={settings.sessionTimeout}
                      onChange={(e) => handleChange('sessionTimeout', parseInt(e.target.value))}
                    >
                      <option value={15}>15 minutes</option>
                      <option value={30}>30 minutes</option>
                      <option value={60}>1 hour</option>
                      <option value={120}>2 hours</option>
                      <option value={0}>Never</option>
                    </select>
                  </div>

                  <div className="p-4 rounded-lg bg-slate-100 dark:bg-slate-800/50 border border-slate-300 dark:border-slate-700/50">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">Password</h3>
                        <p className="text-xs text-slate-600 dark:text-slate-400">Last changed: {settings.passwordLastChanged}</p>
                      </div>
                      <button className="btn btn-secondary text-sm">
                        <Key className="w-4 h-4" />
                        <span>Change Password</span>
                      </button>
                    </div>
                  </div>

                  <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30">
                    <h3 className="text-sm font-semibold text-rose-300 mb-2">Danger Zone</h3>
                    <div className="space-y-3">
                      <button className="btn btn-secondary text-sm w-full sm:w-auto">
                        <Download className="w-4 h-4" />
                        <span>Export Data</span>
                      </button>
                      <button className="btn btn-secondary text-sm w-full sm:w-auto text-rose-300 hover:text-rose-200 hover:bg-rose-500/20">
                        <Trash2 className="w-4 h-4" />
                        <span>Delete Account</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Scheduler Settings */}
          {activeTab === 'scheduler' && (
            <div className="card p-6 space-y-6">
              <TestScheduler />
            </div>
          )}

          {/* Webhooks Settings */}
          {activeTab === 'webhooks' && (
            <div className="card p-6 space-y-6">
              <WebhookSettings />
            </div>
          )}

          {/* API Keys Settings */}
          {activeTab === 'api' && (
            <div className="card p-6 space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">API Keys</h2>
                
                <div className="space-y-5">
                  <div>
                    <label className="label">API Key</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        className="input flex-1 font-mono"
                        value={settings.apiKey}
                        readOnly
                      />
                      <button className="btn btn-secondary">
                        <Key className="w-4 h-4" />
                        <span>Regenerate</span>
                      </button>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">Keep your API key secure and never share it publicly</p>
                  </div>

                  <div>
                    <label className="label">API Secret</label>
                    <div className="flex gap-2">
                      <input
                        type="password"
                        className="input flex-1 font-mono"
                        value={settings.apiSecret}
                        readOnly
                      />
                      <button className="btn btn-secondary">
                        <Key className="w-4 h-4" />
                        <span>Regenerate</span>
                      </button>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">Your API secret is only shown once. Store it securely.</p>
                  </div>

                  <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
                    <h3 className="text-sm font-semibold text-blue-300 mb-2">API Documentation</h3>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mb-3">
                      Learn how to integrate QA Agent into your applications using our API.
                    </p>
                    <button className="btn btn-secondary text-sm">
                      <Globe className="w-4 h-4" />
                      <span>View Documentation</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          <div className="flex items-center justify-between">
            <button
              onClick={handleSignOut}
              className="btn btn-secondary text-rose-300 hover:text-rose-200 hover:bg-rose-500/20"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn btn-primary"
              >
                {saving ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Save Changes</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

