import { motion } from 'framer-motion'
import { SparklesIcon } from '@heroicons/react/24/solid'

interface Props {
  onWake: () => void
}

const HEADLINES = [
  '9 specialist AI agents.',
  'One end-to-end bank marketing platform.',
  'Tap or speak to start.',
]

/**
 * Attract-loop screen. Filled in while no one is at the kiosk so the avatar
 * doesn't stream pointlessly. Tapping anywhere or starting to speak wakes it.
 */
export default function IdleScreen({ onWake }: Props) {
  return (
    <button
      onClick={onWake}
      className="absolute inset-0 z-30 flex flex-col items-center justify-center gap-8 bg-gradient-to-br from-slate-900 via-slate-950 to-black text-white cursor-pointer"
    >
      <motion.div
        animate={{ scale: [1, 1.05, 1], opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
        className="w-40 h-40 rounded-full bg-gradient-to-br from-brand-500/30 to-violet-500/30 blur-xl absolute"
      />
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="relative w-28 h-28 rounded-full bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-2xl"
      >
        <SparklesIcon className="w-12 h-12 text-white" />
      </motion.div>

      <div className="text-center max-w-2xl px-6 space-y-1.5">
        {HEADLINES.map((line, i) => (
          <motion.div
            key={line}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 * i + 0.2, duration: 0.5 }}
            className={
              i === HEADLINES.length - 1
                ? 'text-base text-white/60 pt-3'
                : 'text-3xl md:text-4xl font-semibold tracking-tight'
            }
          >
            {line}
          </motion.div>
        ))}
      </div>

      <motion.div
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        className="text-sm text-white/50 tracking-wider uppercase"
      >
        Tap anywhere or hold space to talk
      </motion.div>
    </button>
  )
}
