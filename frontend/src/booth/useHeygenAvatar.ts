/**
 * useHeygenAvatar — React hook that owns the HeyGen Interactive Avatar
 * streaming session lifecycle.
 *
 * Lifecycle:
 *   1. Browser calls /api/avatar/token to mint a short-lived streaming token.
 *   2. We instantiate StreamingAvatar with that token.
 *   3. createStartAvatar({...}) negotiates a WebRTC stream.
 *   4. On STREAM_READY we attach the MediaStream to the <video> ref.
 *   5. speak(text) drives lip-synced speech.
 *   6. stop() tears it down cleanly when the booth goes idle.
 *
 * If HeyGen is not configured (no API key), the hook stays in demo mode and
 * the BoothPage falls back to showing a static portrait + speech bubble.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import StreamingAvatar, {
  AvatarQuality,
  StreamingEvents,
  TaskMode,
  TaskType,
} from '@heygen/streaming-avatar'
import { fetchAvatarConfig, mintHeygenToken } from './api'
import type { AvatarConfig } from './types'

export type AvatarStatus =
  | 'idle'
  | 'connecting'
  | 'ready'
  | 'speaking'
  | 'disconnected'
  | 'error'

export interface UseHeygenAvatarResult {
  status: AvatarStatus
  videoRef: React.RefObject<HTMLVideoElement>
  config: AvatarConfig | null
  demoMode: boolean
  error: string | null
  start: () => Promise<void>
  stop: () => Promise<void>
  speak: (text: string) => Promise<void>
  interrupt: () => Promise<void>
}

export function useHeygenAvatar(): UseHeygenAvatarResult {
  const videoRef = useRef<HTMLVideoElement>(null)
  const avatarRef = useRef<StreamingAvatar | null>(null)
  const [status, setStatus] = useState<AvatarStatus>('idle')
  const [config, setConfig] = useState<AvatarConfig | null>(null)
  const [demoMode, setDemoMode] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Pull config once on mount so the UI can render the avatar's language
  // and show a "demo mode" banner if the key isn't wired up yet.
  useEffect(() => {
    let cancelled = false
    fetchAvatarConfig()
      .then((c) => {
        if (!cancelled) {
          setConfig(c)
          setDemoMode(!c.configured)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDemoMode(true)
          setError('config_fetch_failed')
        }
      })
    return () => {
      cancelled = true
    }
  }, [])

  const attachStream = useCallback((stream: MediaStream) => {
    const video = videoRef.current
    if (!video) return
    video.srcObject = stream
    video.onloadedmetadata = () => {
      video.play().catch(() => {
        /* autoplay can fail without a user gesture; the kiosk has one */
      })
    }
  }, [])

  const start = useCallback(async () => {
    if (avatarRef.current) return
    if (!config) return
    if (!config.configured) {
      setDemoMode(true)
      setStatus('ready')
      return
    }

    setStatus('connecting')
    setError(null)

    try {
      const { token, demo_mode } = await mintHeygenToken()
      if (demo_mode) {
        setDemoMode(true)
        setStatus('ready')
        return
      }

      const avatar = new StreamingAvatar({ token })
      avatarRef.current = avatar

      avatar.on(StreamingEvents.STREAM_READY, (event: any) => {
        const fromEvent: unknown = event?.detail ?? event
        const stream =
          fromEvent instanceof MediaStream
            ? fromEvent
            : avatar.mediaStream || null
        if (stream) attachStream(stream)
        setStatus('ready')
      })

      avatar.on(StreamingEvents.AVATAR_START_TALKING, () => {
        setStatus('speaking')
      })

      avatar.on(StreamingEvents.AVATAR_STOP_TALKING, () => {
        setStatus((s) => (s === 'speaking' ? 'ready' : s))
      })

      avatar.on(StreamingEvents.STREAM_DISCONNECTED, () => {
        setStatus('disconnected')
      })

      await avatar.createStartAvatar({
        avatarName: config.avatar_id,
        quality: (config.quality as AvatarQuality) || AvatarQuality.High,
        voice: config.voice_id ? { voiceId: config.voice_id } : undefined,
        language: config.language || 'en',
      } as any)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
      setStatus('error')
      avatarRef.current = null
    }
  }, [config, attachStream])

  const stop = useCallback(async () => {
    const avatar = avatarRef.current
    avatarRef.current = null
    if (!avatar) {
      setStatus('idle')
      return
    }
    try {
      await avatar.stopAvatar()
    } catch {
      /* ignore */
    } finally {
      setStatus('idle')
    }
  }, [])

  const speak = useCallback(async (text: string) => {
    const trimmed = (text || '').trim()
    if (!trimmed) return
    const avatar = avatarRef.current
    if (!avatar || demoMode) {
      // Demo mode: simulate speaking timing so the UI still feels alive.
      setStatus('speaking')
      const ms = Math.min(8000, 600 + trimmed.length * 35)
      await new Promise((r) => setTimeout(r, ms))
      setStatus('ready')
      return
    }
    try {
      await avatar.speak({
        text: trimmed,
        task_type: TaskType.REPEAT,
        taskMode: TaskMode.SYNC,
      } as any)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)
    }
  }, [demoMode])

  const interrupt = useCallback(async () => {
    const avatar = avatarRef.current
    if (!avatar) return
    try {
      await avatar.interrupt()
    } catch {
      /* ignore */
    }
  }, [])

  useEffect(
    () => () => {
      void stop()
    },
    [stop],
  )

  return { status, videoRef, config, demoMode, error, start, stop, speak, interrupt }
}
