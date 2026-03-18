import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLeads } from '../hooks/useApi'
import { UserGroupIcon } from '@heroicons/react/24/outline'

const TIER_STYLES: Record<string, string> = {
  PRIORITY: 'priority-critical',
  HIGH:     'priority-high',
  MEDIUM:   'priority-medium',
  LOW:      'priority-low',
}

export default function LeadsPage() {
  const { leads, loading, fetchLeads } = useLeads()
  const navigate = useNavigate()

  useEffect(() => { fetchLeads() }, [])

  const priorityLeads = leads.filter(l => l.score_tier === 'PRIORITY')

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Leads</h1>
          <p className="text-sm text-gray-500 mt-1">
            {leads.length} total · {priorityLeads.length} priority · managed by Lead Management Agent
          </p>
        </div>
        <button onClick={() => navigate('/chat/lead')} className="btn-primary">
          Manage Leads
        </button>
      </div>

      {priorityLeads.length > 0 && (
        <div className="card border-red-900/50">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
            <span className="text-sm font-semibold text-red-300">Priority Leads — Immediate Action Required</span>
          </div>
          <div className="space-y-2">
            {priorityLeads.map(lead => (
              <div key={lead.id} className="flex items-center justify-between p-2 bg-red-900/20 rounded-lg border border-red-900/40">
                <div>
                  <div className="text-sm font-medium text-white">{lead.customer_name || 'Anonymous'}</div>
                  <div className="text-xs text-gray-500">{lead.product_interest} · £{lead.estimated_value_gbp?.toLocaleString()}</div>
                </div>
                <span className={TIER_STYLES[lead.score_tier || 'LOW']}>
                  Score: {lead.lead_score}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading && <div className="text-center py-8 text-gray-500">Loading leads...</div>}

      {leads.length === 0 && !loading ? (
        <div className="card text-center py-12">
          <UserGroupIcon className="w-12 h-12 text-gray-700 mx-auto mb-3" />
          <p className="text-gray-500 mb-4">No leads yet.</p>
          <button onClick={() => navigate('/chat/lead')} className="btn-primary mx-auto">
            Capture leads with the Lead Management Agent
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {leads.filter(l => l.score_tier !== 'PRIORITY').map(lead => (
            <div key={lead.id} className="card hover:border-gray-700 transition-all">
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-white text-sm">{lead.customer_name || 'Anonymous'}</span>
                    {lead.score_tier && (
                      <span className={TIER_STYLES[lead.score_tier]}>{lead.score_tier}</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {lead.product_interest} · {lead.source_channel?.replace(/_/g, ' ')}
                    {lead.estimated_value_gbp ? ` · £${lead.estimated_value_gbp.toLocaleString()}` : ''}
                  </div>
                </div>
                <div className="text-right">
                  {lead.lead_score && (
                    <div className="text-sm font-bold text-white">{Math.round(lead.lead_score)}</div>
                  )}
                  <div className="text-xs text-gray-500">{lead.status}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
