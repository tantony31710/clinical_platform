import { lazy, Suspense, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import { useAuth } from '../lib/AuthContext'

const DNAHelix3D = lazy(() => import('../components/DNAHelix3D'))

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const reduced = useReducedMotion() ?? false

  const [patientId, setPatientId] = useState('')
  const [password, setPassword]   = useState('')
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!patientId.trim() || !password.trim()) {
      setError('Please fill in all fields.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      await login(patientId.trim(), password)
      navigate('/dashboard')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed. Check your credentials.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-clinical-900 px-4">
      {/* DNA Helix in the upper background */}
      <div className="pointer-events-none absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-sm opacity-60">
        <Suspense fallback={null}>
          <DNAHelix3D />
        </Suspense>
      </div>

      {/* Gradient overlay so card sits on clean bg */}
      <div className="pointer-events-none absolute inset-0"
        style={{ background: 'linear-gradient(to bottom, transparent 30%, #0a0f1e 65%)' }} />

      {/* Login card */}
      <motion.div
        initial={reduced ? false : { opacity: 0, y: 60 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 180, damping: 22, delay: 0.1 }}
        className="relative z-10 w-full max-w-md rounded-2xl border border-white/10 bg-clinical-800/90 p-8 shadow-2xl backdrop-blur-md"
      >
        {/* Top teal accent */}
        <div className="absolute inset-x-0 top-0 h-px rounded-t-2xl bg-gradient-to-r from-transparent via-teal-400/60 to-transparent" />

        <div className="mb-8 text-center">
          <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-xl bg-teal-500/20 text-teal-400 text-2xl border border-teal-500/30">
            🧬
          </div>
          <h1 className="text-2xl font-bold text-white">Clinical Platform</h1>
          <p className="mt-1 text-sm text-slate-400">Multi-Specialty Diagnostic System</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <motion.div
            initial={reduced ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Patient ID
            </label>
            <input
              type="text"
              value={patientId}
              onChange={e => setPatientId(e.target.value)}
              placeholder="e.g. patient_001"
              className="w-full rounded-lg border border-white/10 bg-clinical-900 px-4 py-3 text-sm text-white placeholder-slate-500 outline-none transition focus:border-teal-400/60 focus:ring-1 focus:ring-teal-400/30"
              autoComplete="username"
            />
          </motion.div>

          <motion.div
            initial={reduced ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.32 }}
          >
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-400">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full rounded-lg border border-white/10 bg-clinical-900 px-4 py-3 text-sm text-white outline-none transition focus:border-teal-400/60 focus:ring-1 focus:ring-teal-400/30"
              autoComplete="current-password"
            />
          </motion.div>

          {/* Error */}
          <AnimatePresence>
            {error && (
              <motion.div
                key={error}
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="rounded-lg border border-red-500/30 bg-red-950/40 px-4 py-2.5 text-sm text-red-300"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <motion.button
            type="submit"
            disabled={loading}
            whileHover={reduced ? {} : { scale: 1.015 }}
            whileTap={reduced ? {} : { scale: 0.98 }}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-teal-500 py-3 text-sm font-bold text-slate-900 shadow-lg shadow-teal-500/20 transition hover:bg-teal-400 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <motion.span
                  className="inline-block h-4 w-4 rounded-full border-2 border-slate-900 border-t-transparent"
                  animate={reduced ? {} : { rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 0.7, ease: 'linear' }}
                />
                Authenticating…
              </>
            ) : (
              'Sign in'
            )}
          </motion.button>
        </form>
      </motion.div>
    </div>
  )
}
