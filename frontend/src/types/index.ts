// ─── Agent Types ─────────────────────────────────────────────────────────────

export interface AgentTool {
  name: string
  description: string
}

export interface Agent {
  agent_key: string
  name: string
  description: string
  phase: string
  tools: AgentTool[]
  status?: 'active' | 'idle' | 'busy' | 'error'
}

// ─── Chat Types ──────────────────────────────────────────────────────────────

export interface ToolCall {
  tool: string
  args: Record<string, unknown>
  result: Record<string, unknown>
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  agent?: string
  tool_calls?: ToolCall[]
  timestamp: string
  demo_mode?: boolean
}

export interface ChatRequest {
  message: string
  session_id?: string
  agent_name?: string
  context?: Record<string, unknown>
}

export interface ChatResponse {
  session_id: string
  agent: string
  response: string
  tool_calls: ToolCall[]
  timestamp: string
  demo_mode?: boolean
}

// ─── Campaign Types ───────────────────────────────────────────────────────────

export interface Campaign {
  id: string
  campaign_name: string
  product: string
  objective: string
  target_segment: string
  budget_gbp: number
  channels: string[]
  status: CampaignStatus
  kpis?: {
    target_leads: number
    target_cpl_gbp: number
    target_cpa_gbp: number
    target_conversions: number
  }
  start_date?: string
  end_date?: string
  created_at: string
  updated_at?: string
}

export type CampaignStatus =
  | 'draft'
  | 'planning'
  | 'awaiting_compliance'
  | 'approved'
  | 'scheduled'
  | 'live'
  | 'paused'
  | 'completed'
  | 'cancelled'

// ─── Lead Types ───────────────────────────────────────────────────────────────

export interface Lead {
  id: string
  lead_id: string
  source_channel: string
  product_interest: string
  customer_name?: string
  contact_email?: string
  estimated_value_gbp?: number
  lead_score?: number
  score_tier?: 'PRIORITY' | 'HIGH' | 'MEDIUM' | 'LOW'
  assigned_team?: string
  status: string
  priority?: string
  sla_deadline?: string
  campaign_id?: string
  captured_at: string
}

// ─── Asset Types ─────────────────────────────────────────────────────────────

export interface Asset {
  id: string
  campaign_id: string
  asset_name: string
  asset_type: 'image' | 'video' | 'email_template' | 'pdf' | 'html5'
  channel: string
  format_spec: string
  version: number
  url?: string
  compliance_approved: boolean
  expiry_date?: string
  created_at: string
}

// ─── Compliance Types ────────────────────────────────────────────────────────

export interface ComplianceFinding {
  severity: 'HIGH' | 'MEDIUM' | 'LOW'
  category: string
  rule: string
  finding: string
  suggested_amendment?: string
}

export interface ComplianceRecord {
  id: string
  review_id?: string
  certificate_id?: string
  asset_id?: string
  campaign_id?: string
  product_type: string
  channel?: string
  decision?: 'APPROVED' | 'APPROVED_WITH_AMENDMENTS' | 'REJECTED_MINOR' | 'REJECTED_MAJOR'
  findings?: ComplianceFinding[]
  approved?: boolean
  reviewed_at?: string
  submitted_at: string
}

// ─── Phase / Workflow Types ───────────────────────────────────────────────────

export interface Phase {
  id: string
  name: string
  agents: string[]
  sub_phases: string[]
  colour: string
}

export interface Workflow {
  name: string
  description: string
  agents_involved: string[]
}

export interface WorkflowStep {
  step: number
  agent: string
  result: ChatResponse
}

export interface WorkflowResult {
  workflow: string
  session_id: string
  steps?: WorkflowStep[]
  phases?: Record<string, ChatResponse>
  status?: string
  completed_at?: string
}

// ─── Dashboard Types ──────────────────────────────────────────────────────────

export interface DashboardSummary {
  summary: {
    campaigns: { total: number; live: number; draft: number; awaiting_compliance: number }
    leads: { total: number; new: number; priority: number; converted: number }
    assets: { total: number; approved: number; pending_approval: number }
    compliance: { total_reviews: number; approved: number; pending: number }
  }
  agents: { name: string; status: string; phase: string }[]
  recent_activity: { time: string; event: string; type: string }[]
  generated_at: string
}
