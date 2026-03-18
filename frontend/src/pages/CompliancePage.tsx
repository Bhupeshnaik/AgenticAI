import { useNavigate } from 'react-router-dom'
import { ShieldCheckIcon, ExclamationCircleIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

export default function CompliancePage() {
  const navigate = useNavigate()

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Compliance</h1>
        <p className="text-sm text-gray-500 mt-1">FCA financial promotions review · COBS 4 · Consumer Duty · Risk warnings</p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {[
          { icon: CheckCircleIcon, label: 'Approved', value: '0', colour: 'text-green-400', bg: 'bg-green-900/20 border-green-900/50' },
          { icon: ExclamationCircleIcon, label: 'Pending Review', value: '0', colour: 'text-yellow-400', bg: 'bg-yellow-900/20 border-yellow-900/50' },
          { icon: ShieldCheckIcon, label: 'Certificates Issued', value: '0', colour: 'text-brand-400', bg: 'bg-brand-900/20 border-brand-900/50' },
        ].map(stat => (
          <div key={stat.label} className={`card border ${stat.bg}`}>
            <stat.icon className={`w-6 h-6 ${stat.colour} mb-2`} />
            <div className="text-2xl font-bold text-white">{stat.value}</div>
            <div className="text-sm text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header">FCA Compliance Agent</div>
        <p className="text-sm text-gray-400 mb-4">
          The Compliance Agent reviews all customer-facing content for FCA COBS 4 compliance, Consumer Duty alignment,
          risk warning accuracy, representative APR verification, and vulnerable customer considerations.
          It issues formal compliance certificates and maintains an audit trail for FCA inspection readiness.
        </p>
        <div className="grid sm:grid-cols-2 gap-3 mb-4">
          {[
            'Review copy for FCA financial promotions rules',
            'Verify representative APR calculations',
            'Check mandatory risk warnings (mortgage, investment)',
            'Consumer Duty fair value assessment',
            'Issue compliance approval certificate',
            'Get approved disclaimer templates',
          ].map(capability => (
            <div key={capability} className="flex items-start gap-2 text-sm">
              <CheckCircleIcon className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
              <span className="text-gray-400">{capability}</span>
            </div>
          ))}
        </div>
        <button onClick={() => navigate('/chat/compliance')} className="btn-primary">
          Open Compliance Agent
        </button>
      </div>

      <div className="card">
        <div className="card-header">Key Regulatory Framework</div>
        <div className="grid sm:grid-cols-2 gap-3">
          {[
            { rule: 'COBS 4.2.1', label: 'Fair, Clear and Not Misleading', desc: 'All financial promotions must be fair, clear and not misleading.' },
            { rule: 'COBS 4.5.2', label: 'Representative APR', desc: 'Credit promotions must include representative APR at equal prominence.' },
            { rule: 'MCOB 3A.4', label: 'Mortgage Risk Warning', desc: '"Your home may be repossessed if you do not keep up repayments."' },
            { rule: 'Consumer Duty 2023', label: 'Fair Value & Good Outcomes', desc: 'Marketing must not exploit behavioural biases or create false urgency.' },
            { rule: 'UK GDPR 2018', label: 'Marketing Consent', desc: 'Email/SMS requires explicit opt-in. Legitimate interest for direct mail.' },
            { rule: 'FG21/1', label: 'Vulnerable Customers', desc: 'Must consider and protect vulnerable customer needs in all communications.' },
          ].map(item => (
            <div key={item.rule} className="p-3 bg-gray-800/50 rounded-lg border border-gray-700/50">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-brand-400">{item.rule}</span>
              </div>
              <div className="text-sm font-medium text-white mb-0.5">{item.label}</div>
              <div className="text-xs text-gray-500">{item.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
