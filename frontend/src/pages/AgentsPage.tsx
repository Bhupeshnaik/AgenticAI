import { useEffect } from 'react'
import AgentCard from '../components/AgentCard'
import { useAgents } from '../hooks/useApi'
import { CpuChipIcon } from '@heroicons/react/24/outline'

export default function AgentsPage() {
  const { agents, loading, fetchAgents } = useAgents()

  useEffect(() => { fetchAgents() }, [])

  const totalTools = agents.reduce((sum, a) => sum + a.tools.length, 0)

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">AI Agents</h1>
          <p className="text-sm text-gray-500 mt-1">
            {agents.length} specialist agents · {totalTools} tools · All 8 marketing lifecycle phases
          </p>
        </div>
      </div>

      {loading && (
        <div className="text-center py-12 text-gray-500">Loading agents...</div>
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map(agent => (
          <AgentCard key={agent.agent_key} agent={agent} />
        ))}
        {!loading && agents.length === 0 && (
          <div className="sm:col-span-2 lg:col-span-3 text-center py-12">
            <CpuChipIcon className="w-12 h-12 text-gray-700 mx-auto mb-3" />
            <p className="text-gray-500">No agents loaded. Check API connection.</p>
          </div>
        )}
      </div>
    </div>
  )
}
