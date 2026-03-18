import { useNavigate } from 'react-router-dom'

const PHASES = [
  {
    id: 1, colour: 'border-indigo-600 bg-indigo-950/30', accent: 'text-indigo-400', dot: 'bg-indigo-500',
    name: 'Strategy & Annual Planning', agents: ['Strategy Agent'], duration: '6–10 weeks / Quarterly: 2–3w',
    subPhases: ['1a. Annual Marketing Strategy', '1b. Quarterly Campaign Planning'],
    aiImpact: 'Replaces 6-week manual planning with instant AI-driven strategy, budget optimisation using predictive models, and dynamic campaign calendar generation.',
    painPoints: ['6–8 week planning cycle', 'Budget allocation based on gut feel', 'No scenario modelling', 'Misalignment between product and marketing teams'],
    tools: ['analyse_market_data', 'optimise_budget_allocation', 'generate_campaign_calendar', 'create_campaign_brief'],
  },
  {
    id: 2, colour: 'border-violet-600 bg-violet-950/30', accent: 'text-violet-400', dot: 'bg-violet-500',
    name: 'Campaign Design & Creative Production', agents: ['Copywriting Agent', 'Asset Production Agent'], duration: '7–15 business days',
    subPhases: ['2a. Copywriting', '2b. Design & Assets', '2c. Multi-format Images', '2d. PDF Documents', '2e. Video & Rich Media', '2f. DAM & Distribution', '2g. Landing Pages'],
    aiImpact: 'AI generates all-channel copy in seconds (vs 5–10 days). Auto-generates the full 25–40 asset variant manifest. Dynamic PDF generation eliminates manual InDesign bottleneck.',
    painPoints: ['3–5 revision cycles', '25–40 image variants manually produced', 'Rate change = all assets re-produced', 'No dynamic content capability'],
    tools: ['generate_copy_variants', 'generate_variant_manifest', 'register_asset_in_dam', 'generate_pdf_document'],
  },
  {
    id: 3, colour: 'border-cyan-600 bg-cyan-950/30', accent: 'text-cyan-400', dot: 'bg-cyan-500',
    name: 'Audience Segmentation & Data Preparation', agents: ['Segmentation Agent'], duration: '3–7 business days',
    subPhases: ['3a. Segment Definition & List Build'],
    aiImpact: 'Self-serve segment builder replaces 3–5 day analyst dependency. Automated suppressions applied in real-time. ML propensity scores and GDPR validation built in.',
    painPoints: ['3–5 day analyst bottleneck per list', 'Suppression rules are tribal knowledge', 'Static snapshot segments', 'Data quality issues discovered too late'],
    tools: ['build_audience_segment', 'apply_suppressions', 'calculate_propensity_scores', 'validate_gdpr_compliance'],
  },
  {
    id: 4, colour: 'border-red-600 bg-red-950/30', accent: 'text-red-400', dot: 'bg-red-500',
    name: 'Compliance & Regulatory Review', agents: ['Compliance Agent'], duration: '5–15 days (→ 1–4 days with AI)',
    subPhases: ['4a. Financial Promotions Compliance'],
    aiImpact: 'AI pre-screening reduces formal compliance submissions by ~70%. Estimated turnaround reduced from 11 days to 4 days. Consistent decisions across all reviewers. Automated rate accuracy checks.',
    painPoints: ['5–20 day bottleneck — single biggest time-to-market killer', '2–4 revision cycles per asset', 'No pre-screening tool', 'Inconsistent decisions across reviewers'],
    tools: ['review_financial_promotion', 'verify_consumer_duty_alignment', 'validate_risk_warnings', 'issue_compliance_certificate'],
  },
  {
    id: 5, colour: 'border-amber-600 bg-amber-950/30', accent: 'text-amber-400', dot: 'bg-amber-500',
    name: 'Channel Execution & Campaign Launch', agents: ['Campaign Orchestration Agent'], duration: '1–2 days email · 3–4 weeks DM',
    subPhases: ['5a. Email & CRM Execution', '5b. Paid Media / Digital Advertising', '5c. Direct Mail & Branch Execution'],
    aiImpact: 'Unified orchestration layer coordinates all channels. Cross-channel frequency caps enforced automatically. Pre-launch checklist automated. Branch briefing triggered before customer comms go out.',
    painPoints: ['Siloed execution — no unified orchestration', 'No cross-channel frequency cap', 'RM learns about campaigns after customers', 'No dynamic creative'],
    tools: ['create_channel_launch_plan', 'validate_launch_readiness', 'deploy_email_campaign', 'configure_paid_media', 'apply_frequency_cap'],
  },
  {
    id: 6, colour: 'border-emerald-600 bg-emerald-950/30', accent: 'text-emerald-400', dot: 'bg-emerald-500',
    name: 'Lead Capture, Scoring & Routing', agents: ['Lead Management Agent'], duration: '24–72h → < 1h for priority',
    subPhases: ['6a. Lead Capture & Ingestion', '6b. Lead Scoring & Routing'],
    aiImpact: 'AI scoring ensures £5M commercial enquiry gets different treatment to student account. Real-time RM alerts for high-value leads. Response time from 24-72h to <1h for priority leads.',
    painPoints: ['£5M lead gets same priority as student account', 'Manual triage by junior staff', '24–72 hour response to high-value leads', 'Branch leads never captured in CRM'],
    tools: ['capture_lead', 'score_lead', 'route_lead', 'alert_high_value_lead', 'get_lead_queue'],
  },
  {
    id: 7, colour: 'border-blue-600 bg-blue-950/30', accent: 'text-blue-400', dot: 'bg-blue-500',
    name: 'Nurture, Follow-Up & Conversion', agents: ['Nurture Agent'], duration: '4–12 week nurture cycle',
    subPhases: ['7a. Automated Nurture Journeys', '7b. RM Follow-Up & Conversion Support'],
    aiImpact: 'Behaviour-triggered journeys with individual personalisation replace generic drip campaigns. 89% better conversion rate. Application rescue recovers 23% of abandoned applications. Next-best-action guides RM conversations.',
    painPoints: ['Same generic drip for every customer', 'RM has no visibility into digital touchpoints', '40–60% application drop-off rate', 'No next-best-action for RMs'],
    tools: ['create_nurture_journey', 'get_next_best_action', 'trigger_application_rescue', 'personalise_content'],
  },
  {
    id: 8, colour: 'border-rose-600 bg-rose-950/30', accent: 'text-rose-400', dot: 'bg-rose-500',
    name: 'Measurement, Attribution & Optimisation', agents: ['Analytics Agent'], duration: '2–4 weeks → real-time',
    subPhases: ['8a. Campaign Performance Reporting', '8b. Attribution & ROI Analysis'],
    aiImpact: 'Closes the attribution loop — links marketing spend to originated revenue in core banking. Replaces last-touch (which undervalues display by 7x) with AI data-driven Shapley value attribution. Real-time dashboards replace 2-week manual reports.',
    painPoints: ['No closed-loop attribution to core banking', 'Last-touch ignores multi-touch journeys', 'Reports 2–4 weeks after campaign end', 'Finance and marketing use different numbers'],
    tools: ['aggregate_channel_metrics', 'calculate_attribution', 'calculate_campaign_roi', 'generate_performance_report', 'measure_incrementality'],
  },
]

export default function PhasesPage() {
  const navigate = useNavigate()

  return (
    <div className="space-y-4 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-white">8-Phase Marketing Lifecycle</h1>
        <p className="text-sm text-gray-500 mt-1">
          Complete as-is process map with AI agent assignments, pain points addressed, and tools deployed.
        </p>
      </div>

      {PHASES.map(phase => (
        <div key={phase.id} className={`card border-l-4 ${phase.colour}`}>
          <div className="flex items-start gap-3">
            <div className={`w-8 h-8 rounded-lg ${phase.dot} flex items-center justify-center flex-shrink-0 text-white font-bold text-sm`}>
              {phase.id}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2 flex-wrap">
                <h2 className={`font-semibold ${phase.accent}`}>{phase.name}</h2>
                <span className="badge bg-gray-800 text-gray-500 border border-gray-700 text-xs whitespace-nowrap">
                  {phase.duration}
                </span>
              </div>

              {/* Sub-phases */}
              <div className="flex flex-wrap gap-1 mt-2">
                {phase.subPhases.map(sp => (
                  <span key={sp} className="badge bg-gray-800/60 text-gray-500 border border-gray-700/50 text-xs">{sp}</span>
                ))}
              </div>

              <div className="grid sm:grid-cols-2 gap-3 mt-3">
                {/* Agents */}
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1.5">AI Agents</div>
                  <div className="flex flex-wrap gap-1">
                    {phase.agents.map(a => (
                      <button
                        key={a}
                        onClick={() => navigate(`/chat/${a.toLowerCase().split(' ')[0]}`)}
                        className={`badge ${phase.colour.split(' ')[0].replace('border', 'bg')}/30 ${phase.accent} border ${phase.colour.split(' ')[0]} text-xs cursor-pointer hover:opacity-80`}
                      >
                        {a}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tools */}
                <div>
                  <div className="text-xs font-medium text-gray-500 mb-1.5">Key Tools</div>
                  <div className="flex flex-wrap gap-1">
                    {phase.tools.slice(0, 3).map(t => (
                      <span key={t} className="font-mono text-xs text-gray-600 bg-gray-800/50 px-1.5 py-0.5 rounded border border-gray-700/50">{t}</span>
                    ))}
                    {phase.tools.length > 3 && <span className="text-xs text-gray-600">+{phase.tools.length - 3} more</span>}
                  </div>
                </div>
              </div>

              {/* AI Impact */}
              <div className="mt-3 p-2.5 bg-gray-800/30 rounded-lg border border-gray-700/30">
                <div className="text-xs font-medium text-green-400 mb-1">AI Impact</div>
                <p className="text-xs text-gray-400 leading-relaxed">{phase.aiImpact}</p>
              </div>

              {/* Pain points */}
              <details className="mt-2">
                <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-400">
                  {phase.painPoints.length} as-is pain points addressed ▸
                </summary>
                <ul className="mt-2 space-y-1">
                  {phase.painPoints.map(pp => (
                    <li key={pp} className="flex items-start gap-1.5 text-xs text-gray-500">
                      <span className="text-red-500 mt-0.5">✕</span>
                      {pp}
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
