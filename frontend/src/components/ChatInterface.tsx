import { useState, useRef, useEffect, useCallback } from 'react'
import { PaperAirplaneIcon, ArrowPathIcon, ChevronDownIcon } from '@heroicons/react/24/outline'
import { SparklesIcon, WrenchScrewdriverIcon } from '@heroicons/react/24/solid'
import ReactMarkdown from 'react-markdown'
import type { ChatMessage, ToolCall } from '../types'
import { useChat } from '../hooks/useApi'

interface Props {
  agentName?: string
  agentDisplayName?: string
  placeholder?: string
  initialMessage?: string
}

const QUICK_PROMPTS: Record<string, string[]> = {
  strategy: [
    'Create a mortgage campaign brief for spring 2026 with £500k budget',
    'Analyse market data for personal loans Q2 2026',
    'Generate a 12-month campaign calendar for 2026',
  ],
  copywriting: [
    'Generate email copy for a 2.89% mortgage rate offer',
    'Write social media posts for our new ISA product',
    'Create SMS copy for personal loan campaign — 160 chars max',
  ],
  compliance: [
    'Review this email copy for FCA compliance: "Best mortgage rates in the UK — guaranteed!"',
    'Generate a compliance certificate for approved mortgage assets',
    'What are the mandatory risk warnings for mortgage promotions?',
  ],
  asset: [
    'Generate asset variant manifest for a mortgage campaign',
    'Search the DAM for approved social media assets',
    'Check which assets are expiring in the next 14 days',
  ],
  segmentation: [
    'Build an audience segment for mortgage prospects aged 30-45',
    'Apply GDPR suppressions to email campaign audience of 500,000',
    'Calculate propensity scores for credit card cross-sell',
  ],
  campaign: [
    'Create channel launch plan for spring mortgage campaign launching 2026-04-01',
    'Monitor campaign health for campaign ID demo-001',
    'Apply frequency caps for retail mass market segment',
  ],
  lead: [
    'Score a lead: mortgage enquiry, £350k estimated value, application started',
    'Get the current lead queue including SLA breaches',
    'Route a PRIORITY commercial lending lead to the RM team',
  ],
  nurture: [
    'Design nurture journey for PRIORITY mortgage leads over 42 days',
    'Get next best action for a lead who opened email but didn\'t apply',
    'Trigger application rescue for abandoned mortgage application',
  ],
  analytics: [
    'Generate end-of-campaign performance report for campaign demo-001',
    'Calculate ROI for the spring mortgage campaign',
    'Recommend budget reallocation for Q3 with £1.2M total budget',
  ],
}

function ToolCallItem({ call }: { call: ToolCall }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <div className="mt-2 border border-gray-700/50 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 bg-gray-800/50 text-left"
      >
        <div className="flex items-center gap-2">
          <WrenchScrewdriverIcon className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-mono text-xs text-amber-300">{call.tool}</span>
        </div>
        <ChevronDownIcon className={`w-3.5 h-3.5 text-gray-500 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>
      {expanded && (
        <div className="p-3 bg-gray-900/50 space-y-2 text-xs">
          <div>
            <div className="text-gray-500 mb-1">Arguments</div>
            <pre className="text-gray-300 bg-gray-800/80 p-2 rounded overflow-x-auto font-mono text-xs">
              {JSON.stringify(call.args, null, 2)}
            </pre>
          </div>
          <div>
            <div className="text-gray-500 mb-1">Result</div>
            <pre className="text-green-300/80 bg-gray-800/80 p-2 rounded overflow-x-auto font-mono text-xs">
              {JSON.stringify(call.result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

function Message({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} animate-slide-up`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
        isUser ? 'bg-brand-600 text-white' : 'bg-gray-700 text-gray-300'
      }`}>
        {isUser ? 'U' : <SparklesIcon className="w-4 h-4 text-brand-400" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        {msg.agent && !isUser && (
          <div className="text-xs text-gray-500 px-1">
            {msg.agent.charAt(0).toUpperCase() + msg.agent.slice(1)} Agent
            {msg.demo_mode && <span className="ml-2 text-amber-500">[Demo Mode]</span>}
          </div>
        )}
        <div className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
          isUser
            ? 'bg-brand-600 text-white rounded-tr-sm'
            : 'bg-gray-800 text-gray-100 rounded-tl-sm'
        }`}>
          {isUser ? (
            <p>{msg.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0.5">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          )}
        </div>
        {/* Tool calls */}
        {msg.tool_calls && msg.tool_calls.length > 0 && (
          <div className="w-full space-y-1">
            {msg.tool_calls.map((call, i) => (
              <ToolCallItem key={i} call={call} />
            ))}
          </div>
        )}
        <div className="text-xs text-gray-600 px-1">
          {new Date(msg.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

export default function ChatInterface({ agentName, agentDisplayName, placeholder, initialMessage }: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const { sendMessage, createSession, loading } = useChat()
  const prompts = QUICK_PROMPTS[agentName || ''] || []

  useEffect(() => {
    createSession().then(id => setSessionId(id))
    if (initialMessage) {
      setMessages([{
        id: 'init',
        role: 'system',
        content: initialMessage,
        timestamp: new Date().toISOString(),
      }])
    }
  }, [agentName])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = useCallback(async (text?: string) => {
    const messageText = text || input.trim()
    if (!messageText || loading) return

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMsg])
    if (!text) setInput('')

    const response = await sendMessage({
      message: messageText,
      session_id: sessionId || undefined,
      agent_name: agentName,
    })

    if (response) {
      if (!sessionId) setSessionId(response.session_id)
      const agentMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response || 'No response from agent.',
        agent: response.agent,
        tool_calls: response.tool_calls,
        timestamp: response.timestamp,
        demo_mode: response.demo_mode,
      }
      setMessages(prev => [...prev, agentMsg])
    }
  }, [input, loading, sessionId, agentName, sendMessage])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const resetChat = () => {
    setMessages([])
    createSession().then(id => setSessionId(id))
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 min-h-0">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-6 text-center">
            <div className="w-16 h-16 bg-brand-600/20 rounded-2xl flex items-center justify-center border border-brand-800/50">
              <SparklesIcon className="w-8 h-8 text-brand-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">
                {agentDisplayName || 'AI Marketing Platform'}
              </h3>
              <p className="text-sm text-gray-500 max-w-xs">
                Ask me anything about UK bank marketing operations, campaigns, compliance, or data.
              </p>
            </div>
            {prompts.length > 0 && (
              <div className="w-full max-w-lg space-y-2">
                <div className="text-xs text-gray-600 font-medium uppercase tracking-wider">Quick prompts</div>
                {prompts.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(prompt)}
                    className="w-full text-left text-sm text-gray-400 hover:text-gray-200 p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50 hover:border-gray-700 transition-all"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          messages.map(msg => <Message key={msg.id} msg={msg} />)
        )}

        {loading && (
          <div className="flex gap-3 animate-slide-up">
            <div className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center">
              <SparklesIcon className="w-4 h-4 text-brand-400 animate-pulse" />
            </div>
            <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <div
                    key={i}
                    className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 px-4 pb-4">
        <div className="flex items-end gap-2 bg-gray-800 rounded-xl border border-gray-700 focus-within:border-brand-600 transition-colors p-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder || `Message ${agentDisplayName || 'AI'}...`}
            rows={1}
            className="flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-500 focus:outline-none resize-none min-h-[36px] max-h-32 py-1.5 px-2"
            style={{ height: 'auto' }}
            onInput={e => {
              const target = e.target as HTMLTextAreaElement
              target.style.height = 'auto'
              target.style.height = Math.min(target.scrollHeight, 128) + 'px'
            }}
          />
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={resetChat}
              className="p-1.5 text-gray-500 hover:text-gray-300 transition-colors"
              title="Reset conversation"
            >
              <ArrowPathIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              className="p-1.5 bg-brand-600 hover:bg-brand-500 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-lg transition-all"
            >
              <PaperAirplaneIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="text-xs text-gray-600 text-center mt-1.5">
          Press Enter to send · Shift+Enter for new line
        </div>
      </div>
    </div>
  )
}
