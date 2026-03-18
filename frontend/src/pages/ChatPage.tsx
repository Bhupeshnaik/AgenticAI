import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAgents } from '../hooks/useApi'
import ChatInterface from '../components/ChatInterface'
import type { Agent } from '../types'

const AGENT_DESCRIPTIONS: Record<string, { displayName: string; intro: string }> = {
  strategy:    { displayName: 'Strategy Agent', intro: 'I can help with annual planning, campaign briefs, budget allocation, market analysis, and campaign calendars.' },
  copywriting: { displayName: 'Copywriting Agent', intro: 'I generate campaign copy for all channels — email, social, display, SMS, direct mail, and landing pages. I include A/B variants and pre-screen for FCA issues.' },
  compliance:  { displayName: 'Compliance Agent', intro: 'I review marketing content for FCA financial promotions compliance (COBS 4), Consumer Duty, risk warnings, and APR accuracy. I issue compliance certificates.' },
  asset:       { displayName: 'Asset Production Agent', intro: 'I manage the Digital Asset Management (DAM) library, generate multi-format asset manifests (25–40 variants per campaign), and track version control and expiry.' },
  segmentation:{ displayName: 'Segmentation Agent', intro: 'I build targetable audience segments, apply GDPR/PECR suppressions, calculate propensity scores, and validate compliance for all marketing channels.' },
  campaign:    { displayName: 'Campaign Orchestration Agent', intro: 'I orchestrate multi-channel campaign execution, enforce cross-channel frequency caps, create launch plans, and monitor campaign health in real-time.' },
  lead:        { displayName: 'Lead Management Agent', intro: 'I capture, score, and route leads from all channels. High-value leads get immediate RM alerts. I track SLAs and prevent leads being lost in generic queues.' },
  nurture:     { displayName: 'Nurture Agent', intro: 'I design personalised nurture journeys, generate next-best-action recommendations, trigger application rescue sequences, and sync retargeting audiences.' },
  analytics:   { displayName: 'Analytics Agent', intro: 'I consolidate campaign metrics, apply multi-touch attribution models, calculate true ROI with closed-loop attribution, and recommend budget reallocation.' },
}

export default function ChatPage() {
  const { agentName } = useParams<{ agentName?: string }>()
  const navigate = useNavigate()
  const { agents, fetchAgents } = useAgents()
  const [selectedAgent, setSelectedAgent] = useState<string>(agentName || '')

  useEffect(() => { fetchAgents() }, [])
  useEffect(() => { if (agentName) setSelectedAgent(agentName) }, [agentName])

  const agentInfo = selectedAgent ? AGENT_DESCRIPTIONS[selectedAgent] : null

  return (
    <div className="flex h-[calc(100vh-4rem)] gap-4 max-w-6xl">
      {/* Agent selector sidebar */}
      <div className="w-56 flex-shrink-0 space-y-2">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-1 mb-3">
          Select Agent
        </div>
        <button
          onClick={() => { setSelectedAgent(''); navigate('/chat') }}
          className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
            !selectedAgent
              ? 'bg-brand-600/20 text-brand-300 border border-brand-800/50'
              : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
          }`}
        >
          Auto-route
          <div className="text-xs text-gray-600 mt-0.5">Best agent selected automatically</div>
        </button>
        {Object.entries(AGENT_DESCRIPTIONS).map(([key, info]) => (
          <button
            key={key}
            onClick={() => { setSelectedAgent(key); navigate(`/chat/${key}`) }}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
              selectedAgent === key
                ? 'bg-brand-600/20 text-brand-300 border border-brand-800/50'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
            }`}
          >
            {info.displayName}
          </button>
        ))}
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col card p-0 overflow-hidden min-w-0">
        {/* Header */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-800 flex-shrink-0">
          <div className="w-2 h-2 rounded-full bg-green-400" />
          <div>
            <div className="text-sm font-semibold text-white">
              {agentInfo?.displayName || 'Marketing AI Platform'}
            </div>
            {agentInfo && (
              <div className="text-xs text-gray-500 truncate max-w-sm">{agentInfo.intro}</div>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <ChatInterface
            key={selectedAgent}
            agentName={selectedAgent || undefined}
            agentDisplayName={agentInfo?.displayName}
            placeholder={`Ask ${agentInfo?.displayName || 'the AI'}...`}
          />
        </div>
      </div>
    </div>
  )
}
