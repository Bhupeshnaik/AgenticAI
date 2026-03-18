import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronDownIcon, ChevronUpIcon, WrenchScrewdriverIcon, ChatBubbleLeftIcon } from '@heroicons/react/24/outline'
import type { Agent } from '../types'

interface Props {
  agent: Agent
  compact?: boolean
}

const AGENT_COLOURS: Record<string, string> = {
  strategy:    'from-indigo-600 to-indigo-800',
  copywriting: 'from-violet-600 to-violet-800',
  compliance:  'from-red-600 to-red-800',
  asset:       'from-pink-600 to-pink-800',
  segmentation:'from-cyan-600 to-cyan-800',
  campaign:    'from-amber-600 to-amber-800',
  lead:        'from-emerald-600 to-emerald-800',
  nurture:     'from-blue-600 to-blue-800',
  analytics:   'from-rose-600 to-rose-800',
}

const PHASE_LABELS: Record<string, string> = {
  strategy:    'Phase 1',
  copywriting: 'Phase 2a',
  compliance:  'Phase 4',
  asset:       'Phase 2b–2f',
  segmentation:'Phase 3',
  campaign:    'Phase 5',
  lead:        'Phase 6',
  nurture:     'Phase 7',
  analytics:   'Phase 8',
}

export default function AgentCard({ agent, compact = false }: Props) {
  const [expanded, setExpanded] = useState(false)
  const navigate = useNavigate()
  const gradient = AGENT_COLOURS[agent.agent_key] || 'from-gray-600 to-gray-800'
  const phaseLabel = PHASE_LABELS[agent.agent_key] || ''

  return (
    <div className="card hover:border-gray-700 transition-all duration-150 group">
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center flex-shrink-0 shadow-lg`}>
          <span className="text-white text-sm font-bold">
            {agent.name.charAt(0)}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-white text-sm truncate">{agent.name}</h3>
            {phaseLabel && (
              <span className="badge bg-gray-800 text-gray-400 border border-gray-700 text-xs">
                {phaseLabel}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-0.5 leading-relaxed line-clamp-2">
            {agent.description}
          </p>
        </div>
      </div>

      {/* Tools count */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-xs text-gray-500">
          <WrenchScrewdriverIcon className="w-3.5 h-3.5" />
          <span>{agent.tools.length} tools</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => navigate(`/chat/${agent.agent_key}`)}
            className="flex items-center gap-1 text-xs text-brand-400 hover:text-brand-300 transition-colors px-2 py-1 rounded hover:bg-brand-900/20"
          >
            <ChatBubbleLeftIcon className="w-3.5 h-3.5" />
            Chat
          </button>
          {!compact && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-gray-500 hover:text-gray-300 transition-colors p-1 rounded"
            >
              {expanded ? (
                <ChevronUpIcon className="w-3.5 h-3.5" />
              ) : (
                <ChevronDownIcon className="w-3.5 h-3.5" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Expanded tools */}
      {expanded && !compact && (
        <div className="mt-3 pt-3 border-t border-gray-800 space-y-1.5 animate-slide-up">
          <div className="text-xs font-medium text-gray-400 mb-2">Available Tools</div>
          {agent.tools.map((tool) => (
            <div key={tool.name} className="flex items-start gap-2 p-2 rounded-lg bg-gray-800/50">
              <WrenchScrewdriverIcon className="w-3.5 h-3.5 text-brand-400 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-xs font-mono text-brand-300">{tool.name}</div>
                <div className="text-xs text-gray-500 leading-relaxed">{tool.description}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
