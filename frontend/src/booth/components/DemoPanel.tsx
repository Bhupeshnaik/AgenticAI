import { motion, AnimatePresence } from 'framer-motion'
import { XMarkIcon } from '@heroicons/react/24/outline'
import type { BoothPanelState } from '../types'

interface Props {
  state: BoothPanelState
  onClose: () => void
}

export default function DemoPanel({ state, onClose }: Props) {
  return (
    <AnimatePresence mode="wait">
      {state.kind === 'demo' && (
        <motion.div
          key={`demo-${state.demo.id}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.35, ease: [0.19, 1, 0.22, 1] }}
          className="w-full h-full bg-slate-900 rounded-3xl overflow-hidden ring-1 ring-white/10 shadow-2xl flex flex-col"
        >
          <PanelHeader title={state.demo.title} subtitle={state.demo.tagline} onClose={onClose} />
          <div className="flex-1 bg-black flex items-center justify-center">
            <video
              key={state.demo.video_url}
              src={state.demo.video_url}
              poster={state.demo.poster_url}
              autoPlay
              controls
              playsInline
              className="w-full h-full object-contain"
            />
          </div>
        </motion.div>
      )}

      {state.kind === 'slide' && (
        <motion.div
          key={`slide-${state.slide.id}`}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 20 }}
          transition={{ duration: 0.35, ease: [0.19, 1, 0.22, 1] }}
          className="w-full h-full bg-white rounded-3xl overflow-hidden ring-1 ring-white/10 shadow-2xl flex flex-col"
        >
          <PanelHeader title={state.slide.title} dark onClose={onClose} />
          <div className="flex-1 bg-white flex items-center justify-center p-6">
            <img
              src={state.slide.image_url}
              alt={state.slide.title}
              className="max-w-full max-h-full object-contain"
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

function PanelHeader({
  title,
  subtitle,
  dark = false,
  onClose,
}: {
  title: string
  subtitle?: string
  dark?: boolean
  onClose: () => void
}) {
  return (
    <div
      className={`px-6 py-4 flex items-center justify-between border-b ${
        dark ? 'bg-slate-100 border-slate-200 text-slate-900' : 'bg-slate-900 border-white/10 text-white'
      }`}
    >
      <div className="min-w-0">
        <div className="text-xs font-semibold uppercase tracking-wider opacity-60">Side panel</div>
        <div className="text-lg font-semibold truncate">{title}</div>
        {subtitle && <div className="text-sm opacity-70 truncate">{subtitle}</div>}
      </div>
      <button
        onClick={onClose}
        className={`flex-shrink-0 p-2 rounded-full hover:bg-black/10 transition-colors ${
          dark ? 'text-slate-700' : 'text-white/80'
        }`}
        aria-label="Close panel"
      >
        <XMarkIcon className="w-5 h-5" />
      </button>
    </div>
  )
}
