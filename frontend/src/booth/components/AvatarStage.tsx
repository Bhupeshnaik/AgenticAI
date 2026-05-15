import { motion } from 'framer-motion'
import type { RefObject } from 'react'
import type { AvatarStatus } from '../useHeygenAvatar'
import type { BoothPhase } from '../types'

interface Props {
  videoRef: RefObject<HTMLVideoElement>
  status: AvatarStatus
  phase: BoothPhase
  demoMode: boolean
  spokenText: string
  compact: boolean
}

function StatusDot({ status, phase }: { status: AvatarStatus; phase: BoothPhase }) {
  const label =
    status === 'connecting'
      ? 'Connecting…'
      : status === 'error'
        ? 'Connection error'
        : status === 'disconnected'
          ? 'Disconnected'
          : phase === 'listening'
            ? 'Listening'
            : phase === 'thinking'
              ? 'Thinking'
              : phase === 'speaking'
                ? 'Speaking'
                : 'Ready'

  const colour =
    status === 'error' || status === 'disconnected'
      ? 'bg-red-500'
      : phase === 'listening'
        ? 'bg-amber-400 animate-pulse'
        : phase === 'thinking'
          ? 'bg-violet-400 animate-pulse'
          : phase === 'speaking'
            ? 'bg-emerald-400 animate-pulse'
            : 'bg-emerald-500'

  return (
    <div className="flex items-center gap-2 text-white/80 text-sm">
      <span className={`w-2.5 h-2.5 rounded-full ${colour}`} />
      <span>{label}</span>
    </div>
  )
}

export default function AvatarStage({
  videoRef,
  status,
  phase,
  demoMode,
  spokenText,
  compact,
}: Props) {
  return (
    <motion.div
      layout
      transition={{ duration: 0.5, ease: [0.19, 1, 0.22, 1] }}
      className={`relative bg-black rounded-3xl overflow-hidden shadow-2xl ring-1 ring-white/10 ${
        compact ? 'w-full h-full' : 'w-full h-full'
      }`}
    >
      {/* Live HeyGen video */}
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted={false}
        className="absolute inset-0 w-full h-full object-cover"
      />

      {/* Demo-mode placeholder — shown when no HeyGen key is configured */}
      {demoMode && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-800 via-slate-900 to-black">
          <div className="text-center px-8">
            <div className="w-32 h-32 mx-auto rounded-full bg-gradient-to-br from-brand-500 to-violet-500 flex items-center justify-center text-5xl font-bold text-white shadow-2xl">
              AI
            </div>
            <p className="mt-6 text-white/70 text-sm max-w-sm">
              Demo mode — connect a HeyGen API key in the environment to stream
              your photoreal avatar.
            </p>
          </div>
        </div>
      )}

      {/* Top bar */}
      <div className="absolute top-0 inset-x-0 p-4 flex items-center justify-between bg-gradient-to-b from-black/60 to-transparent">
        <div className="flex items-center gap-3">
          <div className="px-3 py-1 rounded-full bg-white/10 backdrop-blur text-white text-xs font-semibold tracking-wider uppercase">
            Bank Marketing AI · Live
          </div>
          {demoMode && (
            <span className="text-xs text-amber-300 font-semibold">demo</span>
          )}
        </div>
        <StatusDot status={status} phase={phase} />
      </div>

      {/* Subtitle of what the avatar is saying */}
      {spokenText && phase === 'speaking' && !compact && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className="absolute bottom-8 inset-x-8 p-4 rounded-2xl bg-black/55 backdrop-blur-md text-white text-lg leading-snug max-w-3xl mx-auto"
        >
          {spokenText}
        </motion.div>
      )}
    </motion.div>
  )
}
