import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import AvatarStage from './components/AvatarStage'
import DemoPanel from './components/DemoPanel'
import IdleScreen from './components/IdleScreen'
import LeadFormModal from './components/LeadFormModal'
import PushToTalk from './components/PushToTalk'
import TranscriptRail, { type TranscriptTurn } from './components/TranscriptRail'
import { fetchDemoCatalog, sendBoothMessage, type BoothLeadResult } from './api'
import { useHeygenAvatar } from './useHeygenAvatar'
import { useSpeechToText } from './useSpeechToText'
import type {
  BoothAction,
  BoothDemo,
  BoothPanelState,
  BoothPhase,
  BoothSlide,
} from './types'

// Auto-return to idle after this many ms of silence.
const IDLE_TIMEOUT_MS = 60_000

export default function BoothPage() {
  const {
    status: avatarStatus,
    videoRef,
    config,
    demoMode,
    start: startAvatar,
    stop: stopAvatar,
    speak,
    interrupt,
  } = useHeygenAvatar()

  const [idle, setIdle] = useState(true)
  const [phase, setPhase] = useState<BoothPhase>('idle')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [panel, setPanel] = useState<BoothPanelState>({ kind: 'idle' })
  const [lastSpoken, setLastSpoken] = useState('')
  const [turns, setTurns] = useState<TranscriptTurn[]>([])
  const [demos, setDemos] = useState<BoothDemo[]>([])
  const [slides, setSlides] = useState<BoothSlide[]>([])
  const [interestTopic, setInterestTopic] = useState<string | null>(null)
  const idleTimerRef = useRef<number | null>(null)

  // Load demo / slide catalog once.
  useEffect(() => {
    fetchDemoCatalog()
      .then((cat) => {
        setDemos(cat.demos)
        setSlides(cat.slides)
      })
      .catch(() => {
        /* booth still works without the catalog */
      })
  }, [])

  const demoById = useMemo(
    () => Object.fromEntries(demos.map((d) => [d.id, d])),
    [demos],
  )
  const slideById = useMemo(
    () => Object.fromEntries(slides.map((s) => [s.id, s])),
    [slides],
  )

  const resetIdleTimer = useCallback(() => {
    if (idleTimerRef.current) window.clearTimeout(idleTimerRef.current)
    idleTimerRef.current = window.setTimeout(() => {
      goIdle()
    }, IDLE_TIMEOUT_MS)
  }, [])

  const goIdle = useCallback(() => {
    setIdle(true)
    setPhase('idle')
    setPanel({ kind: 'idle' })
    setSessionId(null)
    setTurns([])
    setInterestTopic(null)
    setLastSpoken('')
    void stopAvatar()
  }, [stopAvatar])

  const wake = useCallback(async () => {
    if (!idle) return
    setIdle(false)
    setPhase('idle')
    resetIdleTimer()
    await startAvatar()
    // Greet the visitor proactively so the avatar isn't just staring back.
    void handleVisitorMessage('Hello, I just walked up to the booth.', { silentTurn: true })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idle, startAvatar])

  const applyAction = useCallback(
    (action: BoothAction) => {
      switch (action.name) {
        case 'show_demo': {
          const id = action.params.id
          if (!id) return
          const demo = demoById[id]
          if (demo) {
            setPanel({ kind: 'demo', demo })
            setInterestTopic(demo.title)
          }
          break
        }
        case 'show_slide': {
          const id = action.params.id
          if (!id) return
          const slide = slideById[id]
          if (slide) setPanel({ kind: 'slide', slide })
          break
        }
        case 'open_form': {
          setPanel({ kind: 'lead_form' })
          break
        }
        case 'handoff': {
          // Frontend hook for future specialist-agent panels. Logged for now.
          // eslint-disable-next-line no-console
          console.info('[booth] handoff requested ->', action.params.agent)
          break
        }
        case 'end_topic': {
          setPanel({ kind: 'idle' })
          break
        }
      }
    },
    [demoById, slideById],
  )

  const handleVisitorMessage = useCallback(
    async (message: string, opts?: { silentTurn?: boolean }) => {
      const text = message.trim()
      if (!text) return

      resetIdleTimer()

      if (!opts?.silentTurn) {
        setTurns((prev) => [
          ...prev,
          { id: `v-${Date.now()}`, role: 'visitor', content: text },
        ])
      }

      setPhase('thinking')
      try {
        const res = await sendBoothMessage(text, sessionId)
        if (!sessionId) setSessionId(res.session_id)

        res.actions.forEach(applyAction)

        setLastSpoken(res.spoken_text)
        setTurns((prev) => [
          ...prev,
          { id: `a-${Date.now()}`, role: 'avatar', content: res.spoken_text },
        ])

        setPhase('speaking')
        await speak(res.spoken_text)
        setPhase('idle')
      } catch (e) {
        setPhase('error')
        const fallback =
          "Sorry, I lost my connection for a moment. Please try that again."
        setLastSpoken(fallback)
        setTurns((prev) => [
          ...prev,
          { id: `e-${Date.now()}`, role: 'avatar', content: fallback },
        ])
        void speak(fallback)
      }
    },
    [sessionId, speak, applyAction, resetIdleTimer],
  )

  const speechLang = (config?.language || 'en') === 'en' ? 'en-GB' : config!.language
  const stt = useSpeechToText(speechLang, (final) => {
    void handleVisitorMessage(final)
  })

  // Hold-to-talk: interrupt the avatar if it's currently speaking so the
  // visitor doesn't have to wait for it to finish.
  const onMicStart = useCallback(() => {
    if (idle) {
      void wake()
      return
    }
    if (phase === 'speaking') {
      void interrupt()
      setPhase('listening')
    } else {
      setPhase('listening')
    }
    stt.start()
  }, [idle, phase, stt, interrupt, wake])

  const onMicStop = useCallback(() => {
    stt.stop()
    setPhase('thinking')
  }, [stt])

  // Cleanup on unmount.
  useEffect(
    () => () => {
      if (idleTimerRef.current) window.clearTimeout(idleTimerRef.current)
    },
    [],
  )

  const panelHasContent = panel.kind === 'demo' || panel.kind === 'slide'

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-black text-white overflow-hidden">
      {/* Decorative blobs */}
      <div className="absolute inset-0 opacity-30 pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-brand-600/40 blur-3xl rounded-full" />
        <div className="absolute -bottom-40 -right-40 w-[600px] h-[600px] bg-violet-600/30 blur-3xl rounded-full" />
      </div>

      {/* Idle / attract loop */}
      {idle && <IdleScreen onWake={wake} />}

      {/* Active booth UI */}
      {!idle && (
        <div className="relative z-10 h-full w-full p-6 lg:p-10 flex flex-col gap-6">
          {/* Stage */}
          <motion.div
            layout
            transition={{ duration: 0.5, ease: [0.19, 1, 0.22, 1] }}
            className="flex-1 min-h-0 grid gap-6"
            style={{
              gridTemplateColumns: panelHasContent ? '1fr 1.2fr' : '1fr',
            }}
          >
            <AvatarStage
              videoRef={videoRef}
              status={avatarStatus}
              phase={phase}
              demoMode={demoMode}
              spokenText={lastSpoken}
              compact={panelHasContent}
            />

            {panelHasContent && (
              <DemoPanel state={panel} onClose={() => setPanel({ kind: 'idle' })} />
            )}
          </motion.div>

          {/* Transcript */}
          <TranscriptRail turns={turns} />

          {/* Bottom controls */}
          <div className="flex items-center gap-4">
            <PushToTalk
              listening={stt.listening}
              interim={stt.interim}
              disabled={phase === 'thinking' && !stt.listening}
              onStart={onMicStart}
              onStop={onMicStop}
              onTypedSend={(text) => void handleVisitorMessage(text)}
              supported={stt.supported}
              placeholder={
                stt.supported
                  ? 'Hold the mic to talk, or type a question…'
                  : 'Type a question…'
              }
            />
            <button
              onClick={goIdle}
              className="text-sm text-white/60 hover:text-white px-4 py-2 rounded-xl ring-1 ring-white/10 hover:ring-white/30 transition-colors"
            >
              End session
            </button>
          </div>
        </div>
      )}

      {/* Lead capture modal */}
      <LeadFormModal
        open={panel.kind === 'lead_form'}
        interestTopic={interestTopic}
        sessionId={sessionId}
        onClose={() => setPanel({ kind: 'idle' })}
        onSubmitted={(lead: BoothLeadResult) => {
          // Close the loop visibly — have the avatar speak the personalised
          // promise the Lead Management agent generated.
          const intro = "Brilliant, you're in."
          const line = lead.routing.promise_text
            ? `${intro} ${lead.routing.promise_text}`
            : `${intro} Our team will be in touch shortly.`
          setLastSpoken(line)
          setTurns((prev) => [
            ...prev,
            { id: `a-lead-${Date.now()}`, role: 'avatar', content: line },
          ])
          void speak(line)
        }}
      />
    </div>
  )
}
