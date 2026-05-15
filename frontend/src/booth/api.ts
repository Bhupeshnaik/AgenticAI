/**
 * Booth API client — talks to /api/avatar/* endpoints on the FastAPI backend.
 */

import axios from 'axios'
import type {
  AvatarConfig,
  BoothChatResponse,
  BoothDemo,
  BoothSlide,
} from './types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({ baseURL: API_BASE })

export async function mintHeygenToken(): Promise<{
  token: string
  expires_in_seconds: number
  demo_mode: boolean
}> {
  const { data } = await api.post('/avatar/token')
  return data
}

export async function fetchAvatarConfig(): Promise<AvatarConfig> {
  const { data } = await api.get<AvatarConfig>('/avatar/config')
  return data
}

export async function fetchDemoCatalog(): Promise<{
  demos: BoothDemo[]
  slides: BoothSlide[]
}> {
  const { data } = await api.get<{ demos: BoothDemo[]; slides: BoothSlide[] }>(
    '/avatar/demos',
  )
  return data
}

export async function sendBoothMessage(
  message: string,
  sessionId: string | null,
): Promise<BoothChatResponse> {
  const { data } = await api.post<BoothChatResponse>('/avatar/chat', {
    message,
    session_id: sessionId,
  })
  return data
}

export interface BoothLeadPayload {
  name: string
  email: string
  company?: string
  role?: string
  interest_topic?: string
  notes?: string
  session_id?: string | null
  consent: boolean
}

export async function submitBoothLead(payload: BoothLeadPayload): Promise<{
  lead_id: string
  status: string
}> {
  const { data } = await api.post('/avatar/lead', payload)
  return data
}
