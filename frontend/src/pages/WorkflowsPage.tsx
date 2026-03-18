import { useEffect, useState } from 'react'
import { useWorkflows } from '../hooks/useApi'
import type { WorkflowResult } from '../types'
import { ArrowPathIcon, PlayIcon, CheckCircleIcon, CpuChipIcon } from '@heroicons/react/24/outline'

const WORKFLOW_ICONS: Record<string, string> = {
  campaign_launch:     '🚀',
  compliance_review:   '🛡️',
  audience_build:      '👥',
  full_campaign:       '⚡',
  performance_review:  '📊',
}

const WORKFLOW_COLOURS: Record<string, string> = {
  campaign_launch:    'border-brand-800 hover:border-brand-600',
  compliance_review:  'border-red-900 hover:border-red-700',
  audience_build:     'border-cyan-900 hover:border-cyan-700',
  full_campaign:      'border-amber-900 hover:border-amber-700',
  performance_review: 'border-rose-900 hover:border-rose-700',
}

const SAMPLE_DATA: Record<string, Record<string, unknown>> = {
  campaign_launch:    { product: 'mortgage', product_type: 'mortgage', campaign_description: 'Spring 2026 mortgage rate campaign', target_segment: 'First-time buyers aged 28-40', budget: 500000 },
  compliance_review:  { content: 'Get our best mortgage rate at 4.19% APR. Guaranteed approval for all applicants!', product_type: 'mortgage', channel: 'email' },
  audience_build:     { campaign_id: 'spring-mortgage-2026', product_type: 'mortgage', target_segment: 'first-time-buyers', channels: ['email', 'direct_mail'] },
  full_campaign:      { product: 'personal_loan', product_type: 'personal_loan', segment: 'existing customers with debt consolidation propensity', budget: 250000 },
  performance_review: { campaign_id: 'demo-campaign-001', report_type: 'end_of_campaign' },
}

export default function WorkflowsPage() {
  const { workflows, runWorkflow, fetchWorkflows, loading } = useWorkflows()
  const [result, setResult] = useState<WorkflowResult | null>(null)
  const [running, setRunning] = useState<string | null>(null)

  useEffect(() => { fetchWorkflows() }, [])

  const handleRun = async (workflowName: string) => {
    setRunning(workflowName)
    setResult(null)
    const data = SAMPLE_DATA[workflowName] || {}
    const res = await runWorkflow(workflowName, data)
    setResult(res)
    setRunning(null)
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Multi-Agent Workflows</h1>
        <p className="text-sm text-gray-500 mt-1">
          Pre-built workflows that coordinate multiple agents across the 8-phase marketing lifecycle.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {workflows.map(wf => (
          <div
            key={wf.name}
            className={`card border transition-all ${WORKFLOW_COLOURS[wf.name] || 'border-gray-800 hover:border-gray-700'}`}
          >
            <div className="text-3xl mb-3">{WORKFLOW_ICONS[wf.name] || '⚙️'}</div>
            <h3 className="font-semibold text-white text-sm mb-1">
              {wf.name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
            </h3>
            <p className="text-xs text-gray-500 mb-3 leading-relaxed">{wf.description}</p>

            {/* Agents */}
            <div className="flex flex-wrap gap-1 mb-4">
              {wf.agents_involved.map(a => (
                <span key={a} className="badge bg-gray-800 text-gray-400 border border-gray-700">
                  {a}
                </span>
              ))}
            </div>

            <button
              onClick={() => handleRun(wf.name)}
              disabled={!!running}
              className="btn-primary w-full justify-center"
            >
              {running === wf.name ? (
                <>
                  <ArrowPathIcon className="w-4 h-4 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <PlayIcon className="w-4 h-4" />
                  Run Workflow
                </>
              )}
            </button>
          </div>
        ))}

        {workflows.length === 0 && !loading && (
          <div className="sm:col-span-2 lg:col-span-3 text-center py-12 text-gray-500">
            No workflows loaded. Check API connection.
          </div>
        )}
      </div>

      {/* Results panel */}
      {result && (
        <div className="card animate-slide-up">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircleIcon className="w-5 h-5 text-green-400" />
            <h2 className="font-semibold text-white">
              Workflow Complete: {result.workflow?.replace(/_/g, ' ')}
            </h2>
          </div>

          {result.steps && (
            <div className="space-y-3">
              {result.steps.map((step, i) => (
                <div key={i} className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 rounded-full bg-brand-600 flex items-center justify-center text-xs font-bold text-white">
                      {step.step}
                    </div>
                    <div className="flex items-center gap-1.5">
                      <CpuChipIcon className="w-3.5 h-3.5 text-brand-400" />
                      <span className="text-sm font-medium text-brand-300 capitalize">{step.agent} Agent</span>
                    </div>
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed">
                    {step.result?.response || JSON.stringify(step.result).slice(0, 300) + '...'}
                  </p>
                </div>
              ))}
            </div>
          )}

          {result.phases && (
            <div className="grid sm:grid-cols-2 gap-3">
              {Object.entries(result.phases).map(([agentName, agentResult]) => (
                <div key={agentName} className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                  <div className="flex items-center gap-1.5 mb-2">
                    <CpuChipIcon className="w-3.5 h-3.5 text-brand-400" />
                    <span className="text-sm font-medium text-brand-300 capitalize">{agentName} Agent</span>
                  </div>
                  <p className="text-xs text-gray-400 leading-relaxed line-clamp-3">
                    {(agentResult as { response?: string })?.response?.slice(0, 200) || 'Completed'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
