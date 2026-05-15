import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export interface TranscriptTurn {
  id: string
  role: 'visitor' | 'avatar'
  content: string
}

interface Props {
  turns: TranscriptTurn[]
}

/**
 * Live transcript shown along the side of the kiosk. Helps deaf visitors
 * follow along and gives sales a record of what the avatar promised.
 */
export default function TranscriptRail({ turns }: Props) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [turns])

  if (turns.length === 0) return null

  return (
    <div className="bg-white/5 backdrop-blur rounded-2xl ring-1 ring-white/10 p-4 max-h-48 overflow-y-auto text-sm space-y-2">
      <AnimatePresence initial={false}>
        {turns.slice(-6).map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-2"
          >
            <span
              className={`text-xs font-semibold tracking-wider uppercase shrink-0 mt-0.5 ${
                t.role === 'visitor' ? 'text-amber-300' : 'text-emerald-300'
              }`}
            >
              {t.role === 'visitor' ? 'You' : 'AI'}
            </span>
            <span className="text-white/90">{t.content}</span>
          </motion.div>
        ))}
      </AnimatePresence>
      <div ref={endRef} />
    </div>
  )
}
