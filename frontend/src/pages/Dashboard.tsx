import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  MegaphoneIcon, UserGroupIcon, PhotoIcon, ShieldCheckIcon,
  ArrowTrendingUpIcon, ExclamationTriangleIcon, CpuChipIcon,
} from '@heroicons/react/24/outline'
import { useDashboard, useAgents } from '../hooks/useApi'

const AGENT_COLOURS: Record<string, string> = {
  strategy:    'bg-indigo-600',
  copywriting: 'bg-violet-600',
  compliance:  'bg-red-600',
  asset:       'bg-pink-600',
  segmentation:'bg-cyan-600',
  campaign:    'bg-amber-600',
  lead:        'bg-emerald-600',
  nurture:     'bg-blue-600',
  analytics:   'bg-rose-600',
}

function StatCard({ label, value, sub, icon: Icon, colour, onClick }: {
  label: string; value: number | string; sub?: string
  icon: React.ElementType; colour: string; onClick?: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`card text-left hover:border-gray-700 transition-all w-full ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="text-2xl font-bold text-white">{value}</div>
          <div className="text-sm text-gray-400 mt-0.5">{label}</div>
          {sub && <div className="text-xs text-gray-600 mt-0.5">{sub}</div>}
        </div>
        <div className={`${colour} w-10 h-10 rounded-lg flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
    </button>
  )
}

export default function Dashboard() {
  const { data, loading, fetchDashboard } = useDashboard()
  const { agents, fetchAgents } = useAgents()
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboard()
    fetchAgents()
  }, [])

  const s = data?.summary

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Marketing AI Platform</h1>
        <p className="text-sm text-gray-500 mt-1">
          9 specialist agents · 8 marketing phases · UK Bank Marketing Operations
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Campaigns"
          value={s?.campaigns.total ?? '—'}
          sub={`${s?.campaigns.live ?? 0} live · ${s?.campaigns.draft ?? 0} draft`}
          icon={MegaphoneIcon}
          colour="bg-brand-600"
          onClick={() => navigate('/campaigns')}
        />
        <StatCard
          label="Total Leads"
          value={s?.leads.total ?? '—'}
          sub={`${s?.leads.priority ?? 0} priority · ${s?.leads.new ?? 0} new`}
          icon={UserGroupIcon}
          colour="bg-emerald-600"
          onClick={() => navigate('/leads')}
        />
        <StatCard
          label="Assets in DAM"
          value={s?.assets.total ?? '—'}
          sub={`${s?.assets.approved ?? 0} approved`}
          icon={PhotoIcon}
          colour="bg-pink-600"
        />
        <StatCard
          label="Compliance Reviews"
          value={s?.compliance.total_reviews ?? '—'}
          sub={`${s?.compliance.approved ?? 0} approved · ${s?.compliance.pending ?? 0} pending`}
          icon={ShieldCheckIcon}
          colour="bg-red-600"
          onClick={() => navigate('/compliance')}
        />
      </div>

      {/* Two column layout */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Agents */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="card-header">Active Agents</div>
            <div className="grid sm:grid-cols-2 gap-3">
              {(agents.length > 0 ? agents : [
                { agent_key: 'strategy',    name: 'Strategy Agent',    description: 'Annual planning & campaign briefs', phase: 'Phase 1', tools: [] },
                { agent_key: 'copywriting', name: 'Copywriting Agent', description: 'All-channel copy generation',        phase: 'Phase 2a', tools: [] },
                { agent_key: 'compliance',  name: 'Compliance Agent',  description: 'FCA financial promotions review',   phase: 'Phase 4', tools: [] },
                { agent_key: 'asset',       name: 'Asset Agent',       description: 'DAM & multi-format production',     phase: 'Phase 2b-f', tools: [] },
                { agent_key: 'segmentation',name: 'Segmentation Agent',description: 'Audience build & suppressions',     phase: 'Phase 3', tools: [] },
                { agent_key: 'campaign',    name: 'Campaign Agent',    description: 'Multi-channel orchestration',       phase: 'Phase 5', tools: [] },
                { agent_key: 'lead',        name: 'Lead Agent',        description: 'Scoring, routing & SLA',            phase: 'Phase 6', tools: [] },
                { agent_key: 'nurture',     name: 'Nurture Agent',     description: 'Personalised journeys & NBA',       phase: 'Phase 7', tools: [] },
                { agent_key: 'analytics',   name: 'Analytics Agent',   description: 'Attribution & ROI reporting',       phase: 'Phase 8', tools: [] },
              ]).map(agent => (
                <button
                  key={agent.agent_key}
                  onClick={() => navigate(`/chat/${agent.agent_key}`)}
                  className="flex items-center gap-3 p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 border border-gray-800 hover:border-gray-700 transition-all text-left"
                >
                  <div className={`w-8 h-8 rounded-lg ${AGENT_COLOURS[agent.agent_key] || 'bg-gray-600'} flex items-center justify-center flex-shrink-0`}>
                    <CpuChipIcon className="w-4 h-4 text-white" />
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-white truncate">{agent.name}</div>
                    <div className="text-xs text-gray-500 truncate">{agent.phase}</div>
                  </div>
                  <div className="ml-auto">
                    <div className="w-2 h-2 rounded-full bg-green-400" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-4">
          {/* Quick actions */}
          <div className="card">
            <div className="card-header">Quick Actions</div>
            <div className="space-y-2">
              {[
                { label: 'Launch full campaign workflow', to: '/workflows', colour: 'bg-brand-600/20 border-brand-800 text-brand-300' },
                { label: 'Chat with Strategy Agent', to: '/chat/strategy', colour: 'bg-indigo-900/30 border-indigo-800 text-indigo-300' },
                { label: 'Review FCA compliance', to: '/chat/compliance', colour: 'bg-red-900/30 border-red-800 text-red-300' },
                { label: 'View analytics & ROI', to: '/analytics', colour: 'bg-rose-900/30 border-rose-800 text-rose-300' },
                { label: 'Build audience segment', to: '/chat/segmentation', colour: 'bg-cyan-900/30 border-cyan-800 text-cyan-300' },
              ].map(action => (
                <button
                  key={action.to}
                  onClick={() => navigate(action.to)}
                  className={`w-full text-left text-xs font-medium px-3 py-2 rounded-lg border transition-all hover:opacity-80 ${action.colour}`}
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>

          {/* Platform stats */}
          <div className="card">
            <div className="card-header">Platform</div>
            <div className="space-y-2 text-sm">
              {[
                { label: 'Agents online', value: '9 / 9', colour: 'text-green-400' },
                { label: 'AI Provider', value: 'Azure OpenAI', colour: 'text-brand-400' },
                { label: 'Data store', value: 'Azure Cosmos DB', colour: 'text-cyan-400' },
                { label: 'Asset storage', value: 'Azure Blob (DAM)', colour: 'text-pink-400' },
                { label: 'Search', value: 'Azure AI Search', colour: 'text-violet-400' },
              ].map(item => (
                <div key={item.label} className="flex items-center justify-between">
                  <span className="text-gray-500">{item.label}</span>
                  <span className={`font-medium ${item.colour}`}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Phases strip */}
      <div className="card">
        <div className="card-header">8-Phase Marketing Lifecycle</div>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
          {[
            { n: 1, label: 'Strategy', colour: 'bg-indigo-600' },
            { n: 2, label: 'Creative', colour: 'bg-violet-600' },
            { n: 3, label: 'Audience', colour: 'bg-cyan-600' },
            { n: 4, label: 'Compliance', colour: 'bg-red-600' },
            { n: 5, label: 'Execution', colour: 'bg-amber-600' },
            { n: 6, label: 'Leads', colour: 'bg-emerald-600' },
            { n: 7, label: 'Nurture', colour: 'bg-blue-600' },
            { n: 8, label: 'Analytics', colour: 'bg-rose-600' },
          ].map(phase => (
            <button
              key={phase.n}
              onClick={() => navigate('/phases')}
              className={`${phase.colour} rounded-lg p-2 text-center hover:opacity-80 transition-opacity`}
            >
              <div className="text-white font-bold text-lg leading-none">{phase.n}</div>
              <div className="text-white/80 text-xs mt-0.5">{phase.label}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
