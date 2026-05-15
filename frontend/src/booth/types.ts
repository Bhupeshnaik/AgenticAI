/**
 * Booth (HeyGen interactive avatar) shared types.
 * Mirrors the action protocol in backend/api/avatar.py.
 */

export type BoothActionName =
  | 'show_demo'
  | 'show_slide'
  | 'open_form'
  | 'handoff'
  | 'end_topic'

export interface BoothAction {
  name: BoothActionName
  params: Record<string, string>
}

export interface BoothChatResponse {
  session_id: string
  spoken_text: string
  raw_response: string
  actions: BoothAction[]
  demo_mode?: boolean
  timestamp: string
}

export interface BoothDemo {
  id: string
  title: string
  duration_seconds: number
  poster_url: string
  video_url: string
  tagline: string
}

export interface BoothSlide {
  id: string
  title: string
  image_url: string
}

export interface AvatarConfig {
  avatar_id: string
  voice_id: string
  quality: 'low' | 'medium' | 'high' | string
  language: string
  configured: boolean
  demo_video_url?: string | null
}

export type BoothPanelState =
  | { kind: 'idle' }
  | { kind: 'demo'; demo: BoothDemo }
  | { kind: 'slide'; slide: BoothSlide }
  | { kind: 'lead_form' }

export type BoothPhase = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error'
