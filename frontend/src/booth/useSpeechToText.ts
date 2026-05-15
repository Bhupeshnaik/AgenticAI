/**
 * useSpeechToText — minimal push-to-talk wrapper over the browser's
 * Web Speech API (SpeechRecognition).
 *
 * Production booth deployments should swap this for a Deepgram or
 * AssemblyAI streaming client — browser STT is fine for a quiet
 * meeting room demo but loses lock in noisy trade-show conditions.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

type SpeechRecognitionLike = {
  continuous: boolean
  interimResults: boolean
  lang: string
  start: () => void
  stop: () => void
  onresult: ((ev: any) => void) | null
  onerror: ((ev: any) => void) | null
  onend: (() => void) | null
}

interface BrowserSpeechCtor {
  new (): SpeechRecognitionLike
}

function getRecognitionCtor(): BrowserSpeechCtor | null {
  if (typeof window === 'undefined') return null
  const w = window as unknown as {
    SpeechRecognition?: BrowserSpeechCtor
    webkitSpeechRecognition?: BrowserSpeechCtor
  }
  return w.SpeechRecognition || w.webkitSpeechRecognition || null
}

export interface UseSpeechToTextResult {
  supported: boolean
  listening: boolean
  interim: string
  start: () => void
  stop: () => void
  error: string | null
}

export function useSpeechToText(
  language: string,
  onFinalTranscript: (text: string) => void,
): UseSpeechToTextResult {
  const Ctor = getRecognitionCtor()
  const supported = Ctor !== null

  const [listening, setListening] = useState(false)
  const [interim, setInterim] = useState('')
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
  const finalCb = useRef(onFinalTranscript)
  finalCb.current = onFinalTranscript

  const ensure = useCallback(() => {
    if (!Ctor) return null
    if (recognitionRef.current) return recognitionRef.current

    const rec = new Ctor()
    rec.continuous = false
    rec.interimResults = true
    rec.lang = language || 'en-US'

    rec.onresult = (event: any) => {
      let interimText = ''
      let finalText = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        const transcript = result[0]?.transcript || ''
        if (result.isFinal) {
          finalText += transcript
        } else {
          interimText += transcript
        }
      }
      if (interimText) setInterim(interimText)
      if (finalText) {
        setInterim('')
        finalCb.current(finalText.trim())
      }
    }

    rec.onerror = (event: any) => {
      setError(event?.error || 'speech_error')
      setListening(false)
    }

    rec.onend = () => {
      setListening(false)
      setInterim('')
    }

    recognitionRef.current = rec
    return rec
  }, [Ctor, language])

  const start = useCallback(() => {
    setError(null)
    const rec = ensure()
    if (!rec) {
      setError('speech_not_supported')
      return
    }
    rec.lang = language || 'en-US'
    try {
      rec.start()
      setListening(true)
    } catch {
      // Already started — ignore.
    }
  }, [ensure, language])

  const stop = useCallback(() => {
    const rec = recognitionRef.current
    if (!rec) return
    try {
      rec.stop()
    } catch {
      /* ignore */
    }
  }, [])

  useEffect(() => () => stop(), [stop])

  return { supported, listening, interim, start, stop, error }
}
