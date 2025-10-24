import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Send, Trash2, Loader, Globe, Brain, Terminal } from 'lucide-react'
import { sessionsAPI } from '../api/client'

function CreateSessionModal({ isOpen, onClose, onCreate }) {
  const [formData, setFormData] = useState({
    website_url: 'https://www.w3schools.com/',
    ai_provider: 'openai',
    auto_check: true,
    session_name: '',
  })

  const createMutation = useMutation({
    mutationFn: sessionsAPI.create,
    onSuccess: (data) => {
      onCreate(data)
      onClose()
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-2xl flex items-center justify-center z-50 fade-in">
      <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-3xl rounded-3xl p-12 w-full max-w-2xl shadow-2xl border border-white/25 transform scale-100 transition-all duration-700">
        <h2 className="text-5xl font-black text-gradient text-glow mb-10 text-center">
          Create New Session
        </h2>

        <form onSubmit={handleSubmit} className="space-y-8">
          <div>
            <label className="label">Session Name (Optional)</label>
            <input
              type="text"
              className="input text-lg"
              placeholder="My Test Session"
              value={formData.session_name}
              onChange={(e) => setFormData({ ...formData, session_name: e.target.value })}
            />
          </div>

          <div>
            <label className="label">Website URL</label>
            <input
              type="url"
              className="input text-lg"
              required
              value={formData.website_url}
              onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
            />
          </div>

          <div>
            <label className="label">AI Provider</label>
            <select
              className="input text-lg"
              value={formData.ai_provider}
              onChange={(e) => setFormData({ ...formData, ai_provider: e.target.value })}
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="google">Google Gemini</option>
            </select>
          </div>

          <div className="flex items-center space-x-4">
            <input
              type="checkbox"
              id="auto_check"
              className="w-6 h-6 text-white bg-white/10 border-white/25 rounded focus:ring-white/40"
              checked={formData.auto_check}
              onChange={(e) => setFormData({ ...formData, auto_check: e.target.checked })}
            />
            <label htmlFor="auto_check" className="text-lg text-white/90 font-medium">
              Run automatic checks on page load
            </label>
          </div>

          <div className="flex space-x-6 pt-8">
            <button
              type="submit"
              className="btn btn-primary flex-1 text-xl font-bold"
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? (
                <>
                  <Loader className="w-6 h-6 animate-spin inline mr-4" />
                  Creating...
                </>
              ) : (
                'Create Session'
              )}
            </button>
            <button
              type="button"
              className="btn btn-secondary text-xl font-bold"
              onClick={onClose}
              disabled={createMutation.isPending}
            >
              Cancel
            </button>
          </div>

          {createMutation.isError && (
            <div className="bg-gradient-to-r from-red-500/25 to-red-500/15 text-red-100 p-6 rounded-2xl text-base border border-red-500/40 backdrop-blur-xl shadow-2xl">
              <div className="flex items-center space-x-3">
                <XCircle className="w-6 h-6" />
                <span className="font-bold">Error: {createMutation.error.response?.data?.detail || createMutation.error.message}</span>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

function SessionCard({ session, onDelete }) {
  const [command, setCommand] = useState('')
  const [commandResults, setCommandResults] = useState([])

  const commandMutation = useMutation({
    mutationFn: (cmd) => sessionsAPI.executeCommand(session.session_id, cmd),
    onSuccess: (data) => {
      setCommandResults([data, ...commandResults])
      setCommand('')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => sessionsAPI.close(session.session_id),
    onSuccess: onDelete,
  })

  const handleCommand = (e) => {
    e.preventDefault()
    if (command.trim()) {
      commandMutation.mutate(command)
    }
  }

  const statusColors = {
    active: 'bg-emerald-500',
    initializing: 'bg-amber-500',
    failed: 'bg-rose-500',
  }

  const statusPulse = {
    active: 'animate-pulse shadow-emerald-500/50',
    initializing: 'animate-pulse shadow-amber-500/50',
    failed: 'shadow-rose-500/50',
  }

  return (
    <div className="card fade-in hover-lift hover-glow">
      <div className="flex items-start justify-between mb-8">
        <div className="flex-1">
          <div className="flex items-center space-x-6 mb-6">
            <div className={`w-6 h-6 rounded-full ${statusColors[session.status]} ${statusPulse[session.status]} shadow-2xl`} />
            <h3 className="text-4xl font-black text-gradient text-glow">
              {session.session_name}
            </h3>
          </div>
          <div className="flex items-center space-x-8 text-sm text-white/70 font-medium">
            <div className="flex items-center space-x-3">
              <Globe className="w-6 h-6" />
              <span className="truncate max-w-xs">{session.website_url}</span>
            </div>
            <div className="flex items-center space-x-3">
              <Brain className="w-6 h-6" />
              <span>{session.ai_provider}</span>
            </div>
            <div className="flex items-center space-x-3">
              <Terminal className="w-6 h-6" />
              <span>{session.commands_executed} commands</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => deleteMutation.mutate()}
          className="btn btn-danger text-lg font-bold"
          disabled={deleteMutation.isPending}
        >
          {deleteMutation.isPending ? (
            <Loader className="w-5 h-5 animate-spin" />
          ) : (
            <Trash2 className="w-5 h-5" />
          )}
        </button>
      </div>

      {session.status === 'active' && (
        <>
          <form onSubmit={handleCommand} className="mb-8">
            <div className="flex space-x-4">
              <input
                type="text"
                className="input flex-1 text-lg"
                placeholder="Enter command (e.g., 'click the login button')"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                disabled={commandMutation.isPending}
              />
              <button
                type="submit"
                className="btn btn-primary text-lg font-bold"
                disabled={commandMutation.isPending || !command.trim()}
              >
                {commandMutation.isPending ? (
                  <Loader className="w-6 h-6 animate-spin" />
                ) : (
                  <Send className="w-6 h-6" />
                )}
              </button>
            </div>
          </form>

          {commandMutation.isError && (
            <div className="bg-red-500/20 text-red-200 p-4 rounded-xl text-sm mb-6 border border-red-500/30 backdrop-blur-sm">
              Error: {commandMutation.error.response?.data?.detail || commandMutation.error.message}
            </div>
          )}

          {commandResults.length > 0 && (
            <div className="space-y-6">
              <h4 className="text-2xl font-bold text-gradient text-glow">
                Command Results:
              </h4>
              <div className="space-y-6 max-h-80 overflow-y-auto pr-4 scrollbar-thin">
                {commandResults.map((result, idx) => (
                  <div
                    key={idx}
                    style={{ animationDelay: `${idx * 0.15}s` }}
                    className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-2xl p-8 rounded-3xl text-sm border border-white/15 hover:border-white/25 transition-all duration-700 fade-in hover:shadow-2xl hover:-translate-y-1"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-white/90 font-mono text-lg font-bold">{result.command}</span>
                      <span className="text-sm text-green-200 font-mono bg-gradient-to-r from-green-500/25 to-green-500/15 px-4 py-2 rounded-xl border border-green-500/40 shadow-lg">
                        {result.duration_ms?.toFixed(0)}ms
                      </span>
                    </div>
                    <p className="text-white whitespace-pre-wrap leading-relaxed text-base">{result.result}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {session.status === 'initializing' && (
        <div className="flex items-center space-x-4 text-yellow-200">
          <Loader className="w-6 h-6 animate-spin" />
          <span className="text-xl font-bold">Initializing browser session...</span>
        </div>
      )}

      {session.status === 'failed' && session.error && (
        <div className="bg-gradient-to-r from-red-500/25 to-red-500/15 text-red-100 p-6 rounded-2xl text-base border border-red-500/40 backdrop-blur-xl shadow-2xl">
          <div className="flex items-center space-x-3">
            <XCircle className="w-6 h-6" />
            <span className="font-bold">Error: {session.error}</span>
          </div>
        </div>
      )}
    </div>
  )
}

function Sessions() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: sessionsAPI.list,
    refetchInterval: 2000,
  })

  const handleSessionCreated = () => {
    queryClient.invalidateQueries(['sessions'])
  }

  const handleSessionDeleted = () => {
    queryClient.invalidateQueries(['sessions'])
  }

  return (
    <div className="space-y-12 fade-in">
      <div className="flex items-center justify-between slide-in">
        <div>
          <h1 className="text-8xl font-black text-gradient text-glow mb-8 tracking-tight">
            QA Sessions
          </h1>
          <p className="text-white/80 text-2xl font-medium tracking-wide">Manage browser automation sessions</p>
        </div>
        <button
          className="btn btn-primary flex items-center space-x-4 shadow-2xl shadow-white/25 hover:shadow-white/40"
          onClick={() => setIsModalOpen(true)}
        >
          <Plus className="w-7 h-7" />
          <span className="text-lg font-bold">New Session</span>
        </button>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-32">
          <Loader className="w-20 h-20 animate-spin text-white mb-8" />
          <p className="text-white/80 text-2xl font-bold">Loading sessions...</p>
        </div>
      ) : sessions?.sessions?.length > 0 ? (
        <div className="space-y-8">
          {sessions.sessions.map((session, idx) => (
            <div key={session.session_id} style={{ animationDelay: `${idx * 0.15}s` }}>
              <SessionCard
                session={session}
                onDelete={handleSessionDeleted}
              />
            </div>
          ))}
        </div>
      ) : (
        <div className="card text-center py-24 fade-in hover-lift">
          <div className="bg-gradient-to-br from-white/15 to-white/10 w-32 h-32 rounded-full flex items-center justify-center mx-auto mb-10 border border-white/25 shadow-2xl">
            <TestTube className="w-16 h-16 text-white" />
          </div>
          <h3 className="text-6xl font-black text-gradient text-glow mb-8">
            No Active Sessions
          </h3>
          <p className="text-white/80 mb-12 text-2xl font-medium">Create a new session to start testing</p>
          <button
            className="btn btn-primary shadow-2xl shadow-white/25 hover:shadow-white/40 text-xl font-bold"
            onClick={() => setIsModalOpen(true)}
          >
            Create First Session
          </button>
        </div>
      )}

      <CreateSessionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreate={handleSessionCreated}
      />
    </div>
  )
}

export default Sessions
