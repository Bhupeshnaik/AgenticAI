import { useState, useCallback } from 'react'
import axios from 'axios'
import type {
  Agent, ChatRequest, ChatResponse, Campaign, Lead, Asset,
  ComplianceRecord, DashboardSummary, Phase, Workflow, WorkflowResult
} from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({ baseURL: API_BASE })

// ─── Agents ──────────────────────────────────────────────────────────────────

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAgents = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get<{ agents: Agent[] }>('/agents')
      setAgents(res.data.agents)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to fetch agents')
    } finally {
      setLoading(false)
    }
  }, [])

  return { agents, loading, error, fetchAgents }
}

// ─── Chat ─────────────────────────────────────────────────────────────────────

export function useChat() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (request: ChatRequest): Promise<ChatResponse | null> => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post<ChatResponse>('/chat', request)
      return res.data
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to send message'
      setError(msg)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const createSession = useCallback(async (): Promise<string | null> => {
    try {
      const res = await api.post<{ session_id: string }>('/sessions')
      return res.data.session_id
    } catch {
      return null
    }
  }, [])

  return { sendMessage, createSession, loading, error }
}

// ─── Workflows ────────────────────────────────────────────────────────────────

export function useWorkflows() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [workflows, setWorkflows] = useState<Workflow[]>([])

  const fetchWorkflows = useCallback(async () => {
    try {
      const res = await api.get<{ workflows: Workflow[] }>('/workflows')
      setWorkflows(res.data.workflows)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to fetch workflows')
    }
  }, [])

  const runWorkflow = useCallback(async (
    workflowName: string,
    data: Record<string, unknown>
  ): Promise<WorkflowResult | null> => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post<WorkflowResult>('/workflows/run', {
        workflow_name: workflowName,
        data,
      })
      return res.data
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Workflow failed')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { workflows, runWorkflow, fetchWorkflows, loading, error }
}

// ─── Campaigns ───────────────────────────────────────────────────────────────

export function useCampaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(false)

  const fetchCampaigns = useCallback(async (status?: string) => {
    setLoading(true)
    try {
      const res = await api.get<{ campaigns: Campaign[] }>('/campaigns', { params: { status } })
      setCampaigns(res.data.campaigns)
    } finally {
      setLoading(false)
    }
  }, [])

  return { campaigns, loading, fetchCampaigns }
}

// ─── Leads ────────────────────────────────────────────────────────────────────

export function useLeads() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(false)

  const fetchLeads = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get<{ leads: Lead[] }>('/leads')
      setLeads(res.data.leads)
    } finally {
      setLoading(false)
    }
  }, [])

  return { leads, loading, fetchLeads }
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export function useDashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchDashboard = useCallback(async () => {
    setLoading(true)
    try {
      const res = await api.get<DashboardSummary>('/dashboard')
      setData(res.data)
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, fetchDashboard }
}

// ─── Phases ───────────────────────────────────────────────────────────────────

export function usePhases() {
  const [phases, setPhases] = useState<Phase[]>([])

  const fetchPhases = useCallback(async () => {
    try {
      const res = await api.get<{ phases: Phase[] }>('/phases')
      setPhases(res.data.phases)
    } catch {
      // Use defaults if API fails
    }
  }, [])

  return { phases, fetchPhases }
}
