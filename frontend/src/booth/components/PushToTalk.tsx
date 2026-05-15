import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/solid'
import { useEffect, useState } from 'react'

interface Props {
  listening: boolean
  interim: string
  disabled: boolean
  onStart: () => void
  onStop: () => void
  onTypedSend: (text: string) => void
  supported: boolean
  placeholder?: string
}

/**
 * Hold-to-talk button + fallback text input.
 * Keyboard shortcut: spacebar (push-and-hold) when no input is focused.
 */
export default function PushToTalk({
  listening,
  interim,
  disabled,
  onStart,
  onStop,
  onTypedSend,
  supported,
  placeholder = 'Ask anything…',
}: Props) {
  const [typed, setTyped] = useState('')

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.code !== 'Space') return
      const t = e.target as HTMLElement | null
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA')) return
      if (listening || disabled || !supported) return
      e.preventDefault()
      onStart()
    }
    function onKeyUp(e: KeyboardEvent) {
      if (e.code !== 'Space') return
      const t = e.target as HTMLElement | null
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA')) return
      if (!listening) return
      e.preventDefault()
      onStop()
    }
    window.addEventListener('keydown', onKeyDown)
    window.addEventListener('keyup', onKeyUp)
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      window.removeEventListener('keyup', onKeyUp)
    }
  }, [listening, disabled, supported, onStart, onStop])

  function submit() {
    const text = typed.trim()
    if (!text) return
    onTypedSend(text)
    setTyped('')
  }

  return (
    <div className="flex items-center gap-3 w-full">
      {/* Push-to-talk button */}
      <button
        type="button"
        disabled={disabled || !supported}
        onMouseDown={onStart}
        onMouseUp={onStop}
        onMouseLeave={() => listening && onStop()}
        onTouchStart={(e) => {
          e.preventDefault()
          onStart()
        }}
        onTouchEnd={(e) => {
          e.preventDefault()
          onStop()
        }}
        className={`flex-shrink-0 inline-flex items-center justify-center w-16 h-16 rounded-full text-white shadow-lg transition-all select-none ${
          listening
            ? 'bg-red-500 scale-110 ring-4 ring-red-500/30'
            : disabled || !supported
              ? 'bg-slate-600 cursor-not-allowed'
              : 'bg-brand-600 hover:bg-brand-500 active:scale-95'
        }`}
        title={supported ? 'Hold to talk (or press space)' : 'Speech not supported — type instead'}
      >
        {listening ? <StopIcon className="w-6 h-6" /> : <MicrophoneIcon className="w-6 h-6" />}
      </button>

      {/* Text fallback */}
      <div className="flex-1 flex items-center gap-2 bg-white/10 backdrop-blur rounded-2xl px-4 py-3 ring-1 ring-white/15">
        <input
          value={listening ? interim : typed}
          onChange={(e) => setTyped(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') submit()
          }}
          placeholder={listening ? 'Listening…' : placeholder}
          disabled={listening || disabled}
          className="flex-1 bg-transparent text-white placeholder-white/40 text-base focus:outline-none disabled:opacity-60"
        />
        <button
          onClick={submit}
          disabled={!typed.trim() || disabled || listening}
          className="text-sm font-semibold text-white px-4 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  )
}
