import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { CheckCircleIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { submitBoothLead, type BoothLeadPayload } from '../api'

interface Props {
  open: boolean
  interestTopic?: string | null
  sessionId?: string | null
  onClose: () => void
  onSubmitted: () => void
}

export default function LeadFormModal({
  open,
  interestTopic,
  sessionId,
  onClose,
  onSubmitted,
}: Props) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [notes, setNotes] = useState('')
  const [consent, setConsent] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function reset() {
    setName('')
    setEmail('')
    setCompany('')
    setRole('')
    setNotes('')
    setConsent(true)
    setDone(false)
    setError(null)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim() || !email.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const payload: BoothLeadPayload = {
        name: name.trim(),
        email: email.trim(),
        company: company.trim() || undefined,
        role: role.trim() || undefined,
        notes: notes.trim() || undefined,
        interest_topic: interestTopic || undefined,
        session_id: sessionId || undefined,
        consent,
      }
      await submitBoothLead(payload)
      setDone(true)
      onSubmitted()
      setTimeout(() => {
        reset()
        onClose()
      }, 2200)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-6"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, y: 20, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.95, y: 20, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.19, 1, 0.22, 1] }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden"
          >
            {done ? (
              <div className="p-10 text-center">
                <CheckCircleIcon className="w-16 h-16 mx-auto text-emerald-500" />
                <h3 className="mt-4 text-2xl font-semibold text-slate-900">Got it — thanks!</h3>
                <p className="mt-2 text-slate-600">
                  Our team will be in touch within a couple of business days.
                </p>
              </div>
            ) : (
              <>
                <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-slate-900">Book a follow-up</h3>
                    <p className="text-sm text-slate-500">
                      {interestTopic
                        ? `Interested in: ${interestTopic}`
                        : 'Leave your details and we will follow up.'}
                    </p>
                  </div>
                  <button
                    onClick={onClose}
                    className="p-2 text-slate-400 hover:text-slate-700 rounded-full hover:bg-slate-100"
                  >
                    <XMarkIcon className="w-5 h-5" />
                  </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                  <Field label="Name" required>
                    <input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                      className="form-input"
                      placeholder="Alex Morgan"
                    />
                  </Field>
                  <Field label="Work email" required>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="form-input"
                      placeholder="alex@bank.com"
                    />
                  </Field>
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Company">
                      <input
                        value={company}
                        onChange={(e) => setCompany(e.target.value)}
                        className="form-input"
                      />
                    </Field>
                    <Field label="Role">
                      <input
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        className="form-input"
                      />
                    </Field>
                  </div>
                  <Field label="What would be most useful to see?">
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={3}
                      className="form-input"
                    />
                  </Field>
                  <label className="flex items-start gap-2 text-sm text-slate-600">
                    <input
                      type="checkbox"
                      checked={consent}
                      onChange={(e) => setConsent(e.target.checked)}
                      className="mt-1"
                    />
                    <span>
                      I agree to be contacted about the Bank Marketing AI Platform.
                      Your details are stored in line with GDPR.
                    </span>
                  </label>
                  {error && (
                    <div className="text-sm text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-lg">
                      {error}
                    </div>
                  )}
                  <div className="flex items-center justify-end gap-3 pt-2">
                    <button
                      type="button"
                      onClick={onClose}
                      className="px-4 py-2 text-sm text-slate-600 hover:text-slate-900"
                    >
                      Not now
                    </button>
                    <button
                      type="submit"
                      disabled={submitting || !consent || !name.trim() || !email.trim()}
                      className="px-5 py-2 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold text-sm"
                    >
                      {submitting ? 'Sending…' : 'Send me a follow-up'}
                    </button>
                  </div>
                </form>
              </>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

function Field({
  label,
  required,
  children,
}: {
  label: string
  required?: boolean
  children: React.ReactNode
}) {
  return (
    <label className="block">
      <span className="block text-sm font-medium text-slate-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </span>
      {children}
    </label>
  )
}
