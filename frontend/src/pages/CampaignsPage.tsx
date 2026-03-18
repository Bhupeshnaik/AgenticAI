import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCampaigns } from '../hooks/useApi'
import { MegaphoneIcon, PlusIcon } from '@heroicons/react/24/outline'
import type { CampaignStatus } from '../types'

const STATUS_STYLES: Record<CampaignStatus, string> = {
  live:                'status-live',
  draft:               'status-draft',
  awaiting_compliance: 'status-pending',
  approved:            'status-approved',
  scheduled:           'status-approved',
  paused:              'status-pending',
  completed:           'status-draft',
  cancelled:           'status-error',
  planning:            'status-pending',
}

export default function CampaignsPage() {
  const { campaigns, loading, fetchCampaigns } = useCampaigns()
  const navigate = useNavigate()

  useEffect(() => { fetchCampaigns() }, [])

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Campaigns</h1>
          <p className="text-sm text-gray-500 mt-1">{campaigns.length} campaigns · managed by Strategy Agent</p>
        </div>
        <button
          onClick={() => navigate('/chat/strategy')}
          className="btn-primary"
        >
          <PlusIcon className="w-4 h-4" />
          New Campaign
        </button>
      </div>

      {loading && <div className="text-center py-8 text-gray-500">Loading campaigns...</div>}

      {campaigns.length === 0 && !loading ? (
        <div className="card text-center py-12">
          <MegaphoneIcon className="w-12 h-12 text-gray-700 mx-auto mb-3" />
          <p className="text-gray-500 mb-4">No campaigns yet.</p>
          <button onClick={() => navigate('/chat/strategy')} className="btn-primary mx-auto">
            Create your first campaign with the Strategy Agent
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {campaigns.map(campaign => (
            <div key={campaign.id} className="card hover:border-gray-700 transition-all">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h3 className="font-semibold text-white">{campaign.campaign_name}</h3>
                    <span className={STATUS_STYLES[campaign.status] || 'status-draft'}>
                      {campaign.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">{campaign.objective}</div>
                  <div className="flex gap-3 mt-2 text-xs text-gray-600">
                    <span>Product: <span className="text-gray-400">{campaign.product}</span></span>
                    <span>Budget: <span className="text-gray-400">£{campaign.budget_gbp?.toLocaleString()}</span></span>
                    {campaign.channels && <span>Channels: <span className="text-gray-400">{campaign.channels.join(', ')}</span></span>}
                  </div>
                </div>
                <div className="text-xs text-gray-600 whitespace-nowrap">
                  {campaign.created_at ? new Date(campaign.created_at).toLocaleDateString() : '—'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
