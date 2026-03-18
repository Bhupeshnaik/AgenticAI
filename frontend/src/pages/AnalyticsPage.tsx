import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts'
import { ChartBarIcon } from '@heroicons/react/24/outline'

const CHANNEL_DATA = [
  { channel: 'Email',        roas: 1140, cpa: 5,   colour: '#6366f1' },
  { channel: 'Direct Mail',  roas: 92,   cpa: 167,  colour: '#8b5cf6' },
  { channel: 'Paid Search',  roas: 57,   cpa: 133,  colour: '#06b6d4' },
  { channel: 'Paid Social',  roas: 52,   cpa: 99,   colour: '#3b82f6' },
  { channel: 'Programmatic', roas: 28,   cpa: 179,  colour: '#ec4899' },
]

const ATTRIBUTION_DATA = [
  { channel: 'Email',        last_touch: 5,  data_driven: 18 },
  { channel: 'Paid Search',  last_touch: 35, data_driven: 22 },
  { channel: 'Paid Social',  last_touch: 12, data_driven: 19 },
  { channel: 'Display',      last_touch: 2,  data_driven: 14 },
  { channel: 'Direct Mail',  last_touch: 18, data_driven: 16 },
  { channel: 'Branch',       last_touch: 28, data_driven: 11 },
]

const FUNNEL_DATA = [
  { stage: 'Reach',       value: 5200000 },
  { stage: 'Engaged',     value: 380000 },
  { stage: 'Leads',       value: 24500 },
  { stage: 'Applied',     value: 4900 },
  { stage: 'Converted',   value: 2039 },
]

export default function AnalyticsPage() {
  const navigate = useNavigate()

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics & Attribution</h1>
          <p className="text-sm text-gray-500 mt-1">Multi-touch attribution · ROI analysis · Budget recommendations · Powered by Analytics Agent</p>
        </div>
        <button onClick={() => navigate('/chat/analytics')} className="btn-primary">
          Open Analytics Agent
        </button>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total ROAS', value: '59.4x', sub: 'vs 4.0x target', colour: 'text-green-400' },
          { label: 'Blended CPA', value: '£154', sub: 'vs £280 target', colour: 'text-green-400' },
          { label: 'Total Revenue', value: '£16.7M', sub: 'Marketing attributed', colour: 'text-brand-400' },
          { label: 'Incrementality', value: '57%', sub: 'of conversions incremental', colour: 'text-amber-400' },
        ].map(kpi => (
          <div key={kpi.label} className="card">
            <div className={`text-2xl font-bold ${kpi.colour}`}>{kpi.value}</div>
            <div className="text-sm text-gray-400 mt-0.5">{kpi.label}</div>
            <div className="text-xs text-gray-600">{kpi.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* ROAS by channel */}
        <div className="card">
          <div className="card-header">ROAS by Channel</div>
          <div className="text-xs text-gray-500 mb-3">Email has 1140x ROAS — driven by low marginal cost of additional sends</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={CHANNEL_DATA} layout="vertical">
              <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 11 }} />
              <YAxis dataKey="channel" type="category" tick={{ fill: '#9ca3af', fontSize: 11 }} width={90} />
              <Tooltip
                contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
                formatter={(v: number) => [`${v}x`, 'ROAS']}
              />
              <Bar dataKey="roas" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Attribution comparison */}
        <div className="card">
          <div className="card-header">Attribution: Last-Touch vs Data-Driven</div>
          <div className="text-xs text-gray-500 mb-3">Data-driven shows display is 7x undervalued in last-touch models</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={ATTRIBUTION_DATA} layout="vertical">
              <XAxis type="number" tick={{ fill: '#6b7280', fontSize: 11 }} unit="%" />
              <YAxis dataKey="channel" type="category" tick={{ fill: '#9ca3af', fontSize: 11 }} width={85} />
              <Tooltip
                contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
                formatter={(v: number) => [`${v}%`, '']}
              />
              <Bar dataKey="last_touch" name="Last-Touch" fill="#4b5563" radius={2} />
              <Bar dataKey="data_driven" name="Data-Driven" fill="#6366f1" radius={2} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Conversion funnel */}
      <div className="card">
        <div className="card-header">Campaign Conversion Funnel</div>
        <div className="space-y-2">
          {FUNNEL_DATA.map((item, i) => {
            const maxVal = FUNNEL_DATA[0].value
            const pct = (item.value / maxVal) * 100
            return (
              <div key={item.stage} className="flex items-center gap-3">
                <div className="w-24 text-xs text-gray-400 text-right">{item.stage}</div>
                <div className="flex-1 bg-gray-800 rounded-full h-6 relative">
                  <div
                    className="h-6 rounded-full bg-gradient-to-r from-brand-600 to-brand-500 flex items-center justify-end pr-2 transition-all"
                    style={{ width: `${Math.max(pct, 2)}%` }}
                  >
                    <span className="text-xs text-white font-medium">
                      {item.value.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
        <div className="mt-3 text-xs text-gray-500">
          Overall conversion: <span className="text-green-400 font-medium">0.039%</span> reach to conversion ·
          Application-to-conversion: <span className="text-green-400 font-medium">41.6%</span>
        </div>
      </div>

      {/* Budget recommendations */}
      <div className="card">
        <div className="card-header">AI Budget Recommendations (Q3 2026)</div>
        <div className="space-y-3">
          {[
            { action: 'INCREASE', channel: 'Paid Social', change: '+20%', reason: 'CPA 40% below target, high scalability', colour: 'text-green-400 bg-green-900/20 border-green-900' },
            { action: 'INCREASE', channel: 'Direct Mail', change: '+12%', reason: 'Drives highest-value mortgage leads (avg £198k)', colour: 'text-green-400 bg-green-900/20 border-green-900' },
            { action: 'MAINTAIN', channel: 'Paid Search', change: '0%', reason: 'Strong ROAS, at budget capacity', colour: 'text-yellow-400 bg-yellow-900/20 border-yellow-900' },
            { action: 'REDUCE', channel: 'Programmatic', change: '-30%', reason: 'Lowest ROAS, best used for brand not direct response', colour: 'text-red-400 bg-red-900/20 border-red-900' },
          ].map(rec => (
            <div key={rec.channel} className={`flex items-center gap-3 p-3 rounded-lg border ${rec.colour.split(' ').slice(1).join(' ')}`}>
              <span className={`text-xs font-bold w-16 ${rec.colour.split(' ')[0]}`}>{rec.action}</span>
              <span className="text-sm font-medium text-white w-32">{rec.channel}</span>
              <span className={`text-sm font-bold ${rec.colour.split(' ')[0]}`}>{rec.change}</span>
              <span className="text-xs text-gray-500">{rec.reason}</span>
            </div>
          ))}
        </div>
        <div className="mt-3 text-xs text-gray-500">
          Expected outcome: <span className="text-green-400">+15% revenue</span> · <span className="text-green-400">-18% CPA</span> · <span className="text-green-400">+22% volume</span>
        </div>
      </div>
    </div>
  )
}
