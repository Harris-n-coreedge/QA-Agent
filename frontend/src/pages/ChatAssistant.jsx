import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Send,
  Sparkles,
  Wand2,
  Loader2,
  Search,
  Plus,
  MessageSquare,
  ShieldCheck,
  Bug,
  CheckCircle2,
  Cpu,
  ListChecks,
  Clock,
  Phone,
  PhoneCall,
  Users,
  CalendarClock,
} from 'lucide-react'
import { chatAPI } from '../api/client'

const generateClientId = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `id_${Date.now()}_${Math.random().toString(16).slice(2)}`)

const createInitialConversation = () => {
  const conversationId = generateClientId()
  return {
    conversation: {
      id: conversationId,
      title: 'Release QA Planning',
      subtitle: 'Gemini QA Copilot',
      avatarGradient: 'from-[#7c3aed]/80 to-[#6366f1]/80',
      persona: 'Release QA',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      pinned: true,
    },
    messages: [
      {
        id: generateClientId(),
        role: 'assistant',
        content:
          "Hey there! I'm your QA copilot. Share the feature, release, or risk you're focused on and I'll help you assemble test ideas, automation strategies, and stakeholder-ready summaries.",
        timestamp: new Date().toISOString(),
      },
    ],
    suggestions: [
      'Generate acceptance criteria for this feature',
      'Outline a regression sweep for the release',
      'Summarize key risks for leadership',
    ],
  }
}

const quickPrompts = [
  'Create end-to-end test cases for payments',
  'What exploratory charters should I run?',
  'Design data sets for negative testing',
  'Summarize today’s automation gaps',
  'Schedule a quick QA call to unblock this',
]

const qaHighlights = [
  {
    icon: ShieldCheck,
    title: 'Coverage',
    value: '92%',
    caption: 'Critical workflows monitored',
    gradient: 'from-emerald-500/20 to-emerald-400/10',
  },
  {
    icon: Bug,
    title: 'Open Defects',
    value: '14',
    caption: 'Priority items awaiting triage',
    gradient: 'from-rose-500/20 to-rose-400/10',
  },
  {
    icon: CheckCircle2,
    title: 'Confidence',
    value: 'High',
    caption: 'Scenario readiness score',
    gradient: 'from-sky-500/20 to-indigo-500/10',
  },
]

const assistantBadges = [
  { icon: Cpu, label: 'Gemini 1.5', tone: 'from-purple-500/20 to-blue-500/10' },
  { icon: ListChecks, label: 'QA Playbooks', tone: 'from-slate-500/20 to-slate-400/10' },
  { icon: Clock, label: 'Real-time insights', tone: 'from-fuchsia-500/20 to-purple-500/10' },
]

const getInitials = (label = '') =>
  label
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase() || 'QA'

const mapHistoryForApi = (history = []) =>
  history.map((item) => ({
    role: item.role,
    content: item.content,
    timestamp: item.timestamp,
  }))

function ConversationListItem({
  conversation,
  isActive,
  onClick,
  unread,
}) {
  const initials = getInitials(conversation.title)
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-3xl border border-white/5 p-4 text-left transition hover:border-primary-500/40 hover:bg-white/4 ${
        isActive ? 'border-primary-500/60 bg-primary-500/10 shadow-[0_20px_50px_-20px_rgba(129,71,255,0.65)]' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br ${
              conversation.avatarGradient || 'from-[#7c3aed]/80 to-[#6366f1]/80'
            } text-sm font-semibold text-white shadow-lg shadow-purple-900/30`}
          >
            {initials}
          </div>
          <div>
            <p className="text-sm font-semibold text-white">{conversation.title}</p>
            <p className="text-xs text-slate-400 line-clamp-1">
              {conversation.lastMessage || conversation.subtitle || 'Tap to continue the dialog'}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          {conversation.pinned && (
            <span className="rounded-full border border-white/10 bg-white/10 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-white/70">
              Pin
            </span>
          )}
          {unread && <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400" />}
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {(conversation.tags || []).map((tag) => (
          <span
            key={tag}
            className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-[10px] uppercase tracking-[0.18em] text-slate-400"
          >
            {tag}
          </span>
        ))}
      </div>
    </button>
  )
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[75%] rounded-3xl border px-4 py-3 text-sm leading-relaxed shadow-lg transition ${
          isUser
            ? 'border-primary-500/50 bg-gradient-to-br from-primary-500/80 via-indigo-500/70 to-sky-500/70 text-white shadow-primary-900/40'
            : 'border-white/10 bg-white/[0.06] text-slate-100 shadow-slate-900/20'
        } ${message.failed ? 'border-rose-500/60 text-rose-100' : ''}`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        <div className={`mt-2 flex items-center gap-2 text-[11px] uppercase tracking-[0.2em] ${isUser ? 'text-white/60' : 'text-slate-500'}`}>
          <span>{new Date(message.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          {message.failed && <span className="text-rose-200">Retry failed</span>}
        </div>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 text-slate-400">
      <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
        <Sparkles className="h-4 w-4 animate-pulse text-purple-300" />
      </div>
      <div className="flex items-center gap-1 rounded-3xl border border-white/10 bg-white/5 px-3 py-2 text-[11px] uppercase tracking-[0.18em] text-slate-300">
        <Loader2 className="h-4 w-4 animate-spin" />
        Drafting QA insight...
      </div>
    </div>
  )
}

function ChatAssistant() {
  const initialData = useMemo(() => createInitialConversation(), [])
  const [conversations, setConversations] = useState([initialData.conversation])
  const [messagesById, setMessagesById] = useState({
    [initialData.conversation.id]: initialData.messages,
  })
  const [suggestionsById, setSuggestionsById] = useState({
    [initialData.conversation.id]: initialData.suggestions,
  })
  const [callInfoById, setCallInfoById] = useState({})
  const [activeConversationId, setActiveConversationId] = useState(initialData.conversation.id)
  const [inputValue, setInputValue] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [pendingAssistant, setPendingAssistant] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)
  const [isRequestingCall, setIsRequestingCall] = useState(false)
  const [callError, setCallError] = useState(null)

  const messagesEndRef = useRef(null)
  const activeMessages = messagesById[activeConversationId] || []
  const activeSuggestions = suggestionsById[activeConversationId] || []
  const activeCallInfo = callInfoById[activeConversationId]
  const activeConversation = conversations.find((conversation) => conversation.id === activeConversationId)

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [activeConversationId, activeMessages.length, pendingAssistant])

  useEffect(() => {
    setCallError(null)
  }, [activeConversationId])

  const sortedConversations = useMemo(() => {
    const copy = [...conversations]
    copy.sort((a, b) => {
      if (a.pinned && !b.pinned) return -1
      if (!a.pinned && b.pinned) return 1
      return new Date(b.updatedAt || b.createdAt) - new Date(a.updatedAt || a.createdAt)
    })
    return copy
  }, [conversations])

  const filteredConversations = useMemo(() => {
    const query = searchTerm.trim().toLowerCase()
    if (!query) return sortedConversations
    return sortedConversations.filter((conversation) =>
      [conversation.title, conversation.subtitle, conversation.lastMessage]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(query))
    )
  }, [searchTerm, sortedConversations])

  const handleStartCall = async (mode = 'voice') => {
    if (!activeConversationId || isRequestingCall) return

    setIsRequestingCall(true)
    setCallError(null)

    const lastUserMessage = [...activeMessages].reverse().find((msg) => msg.role === 'user')
    const inferredTopic =
      (lastUserMessage?.content && lastUserMessage.content.slice(0, 140)) ||
      activeConversation?.title ||
      'QA collaboration sync'

    const participants = Array.from(
      new Set([
        'You',
        'QA Copilot',
        ...(activeConversation?.persona ? [activeConversation.persona] : []),
      ])
    )

    try {
      const response = await chatAPI.startCall({
        conversationId: activeConversationId,
        topic: inferredTopic,
        participants,
        mode,
        preferredTime: null,
        durationMinutes: 30,
        notes: lastUserMessage?.content,
      })

      setCallInfoById((prev) => ({
        ...prev,
        [activeConversationId]: response,
      }))

      const callMessage = {
        id: response.call_id,
        role: 'assistant',
        content: `I've scheduled a ${response.mode} call about **${response.topic}** for ${new Date(
          response.scheduled_for
        ).toLocaleString()}. Join via ${response.join_url} or dial ${response.dial_in}.`,
        timestamp: new Date().toISOString(),
      }

      setMessagesById((prev) => ({
        ...prev,
        [activeConversationId]: [...(prev[activeConversationId] || []), callMessage],
      }))

      setSuggestionsById((prev) => ({
        ...prev,
        [activeConversationId]: [
          'Draft the call agenda',
          'Capture follow-up actions after the call',
          'Summarize decisions for leadership',
        ],
      }))
    } catch (error) {
      setCallError(error?.response?.data?.detail || error?.message || 'Unable to start the call.')
    } finally {
      setIsRequestingCall(false)
    }
  }

  const handleSendMessage = async () => {
    if (!activeConversationId || !inputValue.trim() || isSending) return

    const messageText = inputValue.trim()
    const newUserMessage = {
      id: generateClientId(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    }

    const updatedMessages = [...activeMessages, newUserMessage]
    setMessagesById((prev) => ({
      ...prev,
      [activeConversationId]: updatedMessages,
    }))

    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === activeConversationId
          ? {
              ...conversation,
              lastMessage: messageText,
              updatedAt: newUserMessage.timestamp,
              title:
                conversation.title === 'New QA Session'
                  ? `Session • ${messageText.slice(0, 24)}${messageText.length > 24 ? '…' : ''}`
                  : conversation.title,
            }
          : conversation
      )
    )

    setInputValue('')
    setErrorMessage(null)
    setIsSending(true)
    setPendingAssistant(true)

    try {
      const response = await chatAPI.sendMessage({
        conversationId: activeConversationId,
        message: messageText,
        history: mapHistoryForApi(updatedMessages.slice(-15)),
        persona: conversations.find((c) => c.id === activeConversationId)?.persona,
      })

      const replyMessage = {
        id: response?.reply?.id || generateClientId(),
        role: 'assistant',
        content: response?.reply?.content || 'I have an update for you.',
        timestamp: response?.reply?.timestamp || new Date().toISOString(),
      }

      setMessagesById((prev) => ({
        ...prev,
        [activeConversationId]: [...(prev[activeConversationId] || []), replyMessage],
      }))

      setConversations((prev) =>
        prev.map((conversation) =>
          conversation.id === activeConversationId
            ? {
                ...conversation,
                lastMessage: replyMessage.content,
                updatedAt: replyMessage.timestamp,
              }
            : conversation
        )
      )

      if (response?.suggestions?.length) {
        setSuggestionsById((prev) => ({
          ...prev,
          [activeConversationId]: response.suggestions,
        }))
      }
    } catch (error) {
      const message = error?.response?.data?.detail || error?.message || 'Something went wrong.'
      setErrorMessage(message)
      setMessagesById((prev) => ({
        ...prev,
        [activeConversationId]: (prev[activeConversationId] || []).map((msg) =>
          msg.id === newUserMessage.id ? { ...msg, failed: true } : msg
        ),
      }))
    } finally {
      setIsSending(false)
      setPendingAssistant(false)
    }
  }

  const handleNewConversation = () => {
    const newConversationId = generateClientId()
    const timestamp = new Date().toISOString()
    const starterMessage = {
      id: generateClientId(),
      role: 'assistant',
      content:
        'Welcome! Tell me what you are shipping or validating and I will help design builds, data, and coverage tailored to your QA goals.',
      timestamp,
    }

    const newConversation = {
      id: newConversationId,
      title: 'New QA Session',
      subtitle: 'Start with a goal or question',
      avatarGradient: 'from-[#a855f7]/80 to-[#6366f1]/70',
      createdAt: timestamp,
      updatedAt: timestamp,
      tags: ['unassigned'],
    }

    setConversations((prev) => [newConversation, ...prev])
    setMessagesById((prev) => ({
      ...prev,
      [newConversationId]: [starterMessage],
    }))
    setSuggestionsById((prev) => ({
      ...prev,
      [newConversationId]: [
        'Draft a smoke test outline',
        'Identify high-risk regression areas',
        'Summarize outstanding QA blockers',
      ],
    }))
    setActiveConversationId(newConversationId)
    setInputValue('')
    setErrorMessage(null)
  }

  const handleQuickPrompt = (prompt) => {
    setInputValue(prompt)
  }

  const handleComposerKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="page-title">QA Copilot Messenger</h1>
          <p className="page-description">
            Collaborate with a Gemini-powered engineer to finalize test strategy, automation focus, and risk coverage.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {assistantBadges.map((badge) => (
            <span
              key={badge.label}
              className={`inline-flex items-center gap-2 rounded-full border border-white/10 bg-gradient-to-r ${badge.tone} px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white/70`}
            >
              <badge.icon className="h-4 w-4 text-white/80" />
              {badge.label}
            </span>
          ))}
          <button
            onClick={handleNewConversation}
            className="inline-flex items-center gap-2 rounded-full border border-primary-500/40 bg-primary-500/20 px-4 py-2 text-sm font-semibold text-white transition hover:border-primary-500/60 hover:bg-primary-500/30"
          >
            <Plus className="h-4 w-4" />
            New session
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-7">
        <div className="xl:col-span-2">
          <div className="rounded-4xl border border-white/10 bg-[#07091c]/90 p-5 shadow-[0_25px_60px_rgba(9,7,38,0.55)]">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Message Hub</p>
                <h2 className="mt-1 text-lg font-semibold text-white">Your QA Dialogs</h2>
              </div>
              <button
                onClick={handleNewConversation}
                className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold text-white/70 transition hover:bg-white/10 hover:text-white"
              >
                <MessageSquare className="h-4 w-4" />
                Fresh chat
              </button>
            </div>

            <div className="mt-5">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  placeholder="Search QA threads"
                  className="w-full rounded-3xl border border-white/10 bg-white/5 py-2 pl-9 pr-4 text-sm text-white placeholder:text-slate-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                />
              </div>
            </div>

            <div className="mt-6 flex items-center justify-between text-xs uppercase tracking-[0.2em] text-slate-500">
              <span>Active</span>
              <span>{conversations.length} sessions</span>
            </div>

            <div className="mt-4 space-y-3">
              {filteredConversations.map((conversation) => (
                <ConversationListItem
                  key={conversation.id}
                  conversation={conversation}
                  isActive={conversation.id === activeConversationId}
                  onClick={() => setActiveConversationId(conversation.id)}
                  unread={conversation.id !== activeConversationId && !conversation.read}
                />
              ))}
              {filteredConversations.length === 0 && (
                <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.04] p-6 text-center text-sm text-slate-400">
                  No conversations yet. Start a new QA session to see it listed here.
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="xl:col-span-5">
          <div className="flex flex-col gap-6">
            <div className="rounded-4xl border border-white/10 bg-[#060b1a]/90 p-6 shadow-[0_30px_80px_rgba(13,9,54,0.6)]">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex items-start gap-4">
                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${
                      activeConversation?.avatarGradient || 'from-[#7c3aed]/80 to-[#6366f1]/80'
                    } text-base font-semibold text-white shadow-lg shadow-purple-900/40`}
                  >
                    {getInitials(activeConversation?.title)}
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-white">{activeConversation?.title}</h2>
                    <p className="text-sm text-slate-400">
                      {activeConversation?.subtitle || 'Share context to tailor the QA strategy.'}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {(activeConversation?.tags || ['qa', 'strategy']).map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-slate-400"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <div className="mt-4 flex flex-wrap items-center gap-3">
                      <button
                        onClick={() => handleStartCall('voice')}
                        disabled={isRequestingCall}
                        className="inline-flex items-center gap-2 rounded-full border border-primary-500/40 bg-primary-500/20 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:border-primary-500/60 hover:bg-primary-500/30 disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        {isRequestingCall ? <Loader2 className="h-4 w-4 animate-spin" /> : <PhoneCall className="h-4 w-4" />}
                        {isRequestingCall ? 'Scheduling…' : 'Start QA Call'}
                      </button>
                      <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[10px] uppercase tracking-[0.18em] text-slate-400">
                        <Phone className="h-3.5 w-3.5 text-emerald-300" />
                        {activeCallInfo ? `${activeCallInfo.status.toUpperCase()} • ${activeCallInfo.mode}` : 'Voice-ready'}
                      </span>
                    </div>
                    {callError && (
                      <div className="mt-3 rounded-2xl border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-xs text-rose-100">
                        {callError}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  {qaHighlights.map((item) => (
                    <div
                      key={item.title}
                      className={`flex items-center gap-3 rounded-3xl border border-white/10 bg-gradient-to-br ${item.gradient} px-3 py-2`}
                    >
                      <item.icon className="h-5 w-5 text-white/80" />
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/70">{item.title}</p>
                        <p className="text-sm font-semibold text-white">{item.value}</p>
                        <p className="text-[11px] text-slate-400">{item.caption}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {activeCallInfo && (
                <div className="mt-6 rounded-3xl border border-white/10 bg-white/[0.04] p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <div className="flex items-center gap-3 text-xs uppercase tracking-[0.18em] text-slate-400">
                        <CalendarClock className="h-4 w-4" />
                        Scheduled for {new Date(activeCallInfo.scheduled_for).toLocaleString()}
                      </div>
                      <h3 className="mt-2 text-base font-semibold text-white">{activeCallInfo.topic}</h3>
                      <p className="text-sm text-slate-400">
                        {activeCallInfo.summary || 'We will focus on current QA risks, coverage, and next decisions.'}
                      </p>
                      <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-400">
                        <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1">
                          <Clock className="h-3.5 w-3.5 text-white/70" />
                          {activeCallInfo.duration_minutes} minutes
                        </span>
                        <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1">
                          <Users className="h-3.5 w-3.5 text-white/70" />
                          {activeCallInfo.participants.join(', ')}
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-col gap-3 rounded-3xl border border-white/10 bg-black/30 p-4 text-xs text-slate-300">
                      <div>
                        <span className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Join URL</span>
                        <button
                          onClick={() => window.open(activeCallInfo.join_url, '_blank', 'noopener,noreferrer')}
                          className="mt-1 inline-flex items-center gap-2 text-left text-white/80 underline decoration-dotted underline-offset-4 hover:text-white"
                        >
                          {activeCallInfo.join_url}
                        </button>
                      </div>
                      <div>
                        <span className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Dial in</span>
                        <p className="mt-1 font-mono text-sm text-white">{activeCallInfo.dial_in}</p>
                      </div>
                      <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/40 bg-emerald-500/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300">
                        {activeCallInfo.status.toUpperCase()}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-6 flex flex-wrap gap-3">
                {activeSuggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => handleQuickPrompt(suggestion)}
                    className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-white/70 transition hover:border-primary-500/40 hover:text-white"
                  >
                    <Wand2 className="h-4 w-4 text-primary-300" />
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded-4xl border border-white/10 bg-[#050916]/90 p-6 shadow-[0_30px_80px_rgba(8,10,29,0.55)]">
              <div className="flex flex-col gap-4">
                <div className="h-[420px] overflow-y-auto pr-1 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-white/10">
                  <div className="space-y-6">
                    {activeMessages.map((message) => (
                      <MessageBubble key={message.id} message={message} />
                    ))}
                    {pendingAssistant && <TypingIndicator />}
                    <div ref={messagesEndRef} />
                  </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    {quickPrompts.map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => handleQuickPrompt(prompt)}
                        className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/60 transition hover:border-primary-500/40 hover:text-white"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                  <div className="mt-4 rounded-2xl border border-white/10 bg-black/40 px-4">
                    <textarea
                      value={inputValue}
                      onChange={(event) => setInputValue(event.target.value)}
                      onKeyDown={handleComposerKeyDown}
                      placeholder="Ask about plans, automation, edge cases, or summaries for stakeholders…"
                      rows={3}
                      className="min-h-[120px] w-full resize-none bg-transparent py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none"
                    />
                    <div className="flex items-center justify-between border-t border-white/5 py-3">
                      <div className="flex items-center gap-3 text-xs text-slate-500">
                        <Sparkles className="h-4 w-4 text-primary-300" />
                        <span>Shift + Enter for newline</span>
                        <span>Gemini tuned for QA reasoning</span>
                      </div>
                      <button
                        onClick={handleSendMessage}
                        disabled={isSending || !inputValue.trim()}
                        className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-primary-500 to-indigo-500 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-primary-900/30 transition hover:shadow-primary-600/40 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                        {isSending ? 'Sending…' : 'Send insight'}
                      </button>
                    </div>
                  </div>
                  {errorMessage && (
                    <div className="mt-3 rounded-2xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
                      {errorMessage}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatAssistant

