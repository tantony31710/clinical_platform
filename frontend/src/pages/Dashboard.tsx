import { lazy, Suspense, useState } from 'react'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import { useAuth } from '../lib/AuthContext'
import { assess, AssessmentResult } from '../lib/api'
import RiskGauge from '../components/RiskGauge'

const DNAHelix3D = lazy(() => import('../components/DNAHelix3D'))

// ── Specialty field definitions ───────────────────────────────────────────────
const SPECIALTIES = {
  diabetes: {
    label: 'Diabetes',
    icon: '🩸',
    fields: [
      { key: 'glucose',       label: 'Glucose (mg/dL)',    type: 'number' },
      { key: 'bmi',           label: 'BMI',                type: 'number' },
      { key: 'age',           label: 'Age',                type: 'number' },
      { key: 'blood_pressure',label: 'Blood Pressure',     type: 'number' },
      { key: 'insulin',       label: 'Insulin (µU/mL)',    type: 'number' },
    ],
  },
  heart: {
    label: 'Heart Disease',
    icon: '❤️',
    fields: [
      { key: 'age',             label: 'Age',                  type: 'number' },
      { key: 'sex',             label: 'Sex (1=M, 0=F)',       type: 'number' },
      { key: 'chest_pain_type', label: 'Chest Pain (0–3)',     type: 'number' },
      { key: 'resting_bp',      label: 'Resting BP (mmHg)',    type: 'number' },
      { key: 'cholesterol',     label: 'Cholesterol (mg/dL)',  type: 'number' },
      { key: 'max_heart_rate',  label: 'Max Heart Rate',       type: 'number' },
    ],
  },
  kidney: {
    label: 'Kidney Disease',
    icon: '🫘',
    fields: [
      { key: 'age',                    label: 'Age',                    type: 'number' },
      { key: 'blood_pressure',         label: 'Blood Pressure',         type: 'number' },
      { key: 'specific_gravity',       label: 'Specific Gravity',       type: 'number' },
      { key: 'albumin',                label: 'Albumin (g/dL)',         type: 'number' },
      { key: 'blood_glucose_random',   label: 'Blood Glucose (mg/dL)',  type: 'number' },
    ],
  },
  breast_cancer: {
    label: 'Breast Cancer',
    icon: '🎗️',
    fields: [
      { key: 'radius_mean',      label: 'Radius Mean',      type: 'number' },
      { key: 'texture_mean',     label: 'Texture Mean',     type: 'number' },
      { key: 'perimeter_mean',   label: 'Perimeter Mean',   type: 'number' },
      { key: 'area_mean',        label: 'Area Mean',        type: 'number' },
      { key: 'smoothness_mean',  label: 'Smoothness Mean',  type: 'number' },
    ],
  },
  ALL: {
    label: 'Full Panel',
    icon: '🔬',
    fields: [],  // full panel uses all fields from all specialties
  },
} as const

type SpecialtyKey = keyof typeof SPECIALTIES

export default function Dashboard() {
  const { patientId, logout } = useAuth()
  const reduced = useReducedMotion() ?? false

  const [activeTab, setActiveTab]   = useState<SpecialtyKey>('diabetes')
  const [formValues, setFormValues] = useState<Record<string, string>>({})
  const [loading, setLoading]       = useState(false)
  const [results, setResults]       = useState<AssessmentResult | null>(null)
  const [profileUsed, setProfileUsed] = useState<Record<string, number | string> | null>(null)
  const [error, setError]           = useState<string | null>(null)
  const [showProfile, setShowProfile] = useState(false)

  const currentSpec = SPECIALTIES[activeTab]
  const fieldsToShow = activeTab === 'ALL'
    ? Object.values(SPECIALTIES).flatMap(s => s.fields).filter(
        (f, i, arr) => arr.findIndex(x => x.key === f.key) === i  // dedupe
      )
    : currentSpec.fields

  const handleField = (key: string, val: string) => {
    setFormValues(prev => ({ ...prev, [key]: val }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResults(null)
    try {
      const profile: Record<string, number> = {}
      for (const [k, v] of Object.entries(formValues)) {
        if (v.trim() !== '') profile[k] = Number(v)
      }
      const { results: res, profile_used } = await assess(activeTab, profile)
      setResults(res)
      setProfileUsed(profile_used)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Assessment failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resultEntries = results
    ? Object.entries(results).filter(([, v]) => v && typeof v === 'object')
    : []

  return (
    <div className="min-h-screen bg-clinical-900 text-slate-200">
      {/* Header */}
      <header className="sticky top-0 z-30 border-b border-white/10 bg-clinical-800/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🧬</span>
            <div>
              <h1 className="text-base font-bold text-white">Clinical Diagnostic Platform</h1>
              <p className="text-[11px] uppercase tracking-widest text-teal-400/70">Multi-Specialty AI Assessment</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="hidden text-xs text-slate-400 sm:block">
              Patient: <span className="font-mono text-teal-400">{patientId}</span>
            </span>
            <a href="/history" className="text-xs text-slate-400 hover:text-teal-400 transition">History</a>
            <button
              onClick={logout}
              className="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-slate-400 hover:bg-white/5 transition"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Hero — DNA helix */}
      <div className="relative overflow-hidden border-b border-white/5 bg-clinical-800">
        <div className="pointer-events-none absolute inset-0"
          style={{ background: 'radial-gradient(ellipse at 50% 0%, rgba(45,212,191,0.07) 0%, transparent 60%)' }} />
        <div className="mx-auto flex max-w-7xl flex-col items-center py-4">
          <Suspense fallback={<div className="h-[350px] flex items-center text-slate-500 text-sm">Loading 3D…</div>}>
            <DNAHelix3D />
          </Suspense>
          <p className="mb-4 text-center text-xs text-slate-500 max-w-md">
            Fill in patient vitals on the left to generate an AI-powered multi-specialty risk assessment.
          </p>
        </div>
      </div>

      {/* Main two-column layout */}
      <main className="mx-auto grid max-w-7xl grid-cols-1 gap-6 p-6 lg:grid-cols-2">

        {/* LEFT — Assessment form */}
        <motion.div
          initial={reduced ? false : { opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="rounded-2xl border border-white/10 bg-clinical-800 p-6"
        >
          <h2 className="mb-4 text-sm font-bold uppercase tracking-wider text-slate-300">Patient Assessment</h2>

          {/* Specialty tabs */}
          <div className="mb-5 flex flex-wrap gap-2">
            {(Object.entries(SPECIALTIES) as [SpecialtyKey, typeof SPECIALTIES[SpecialtyKey]][]).map(([key, spec]) => (
              <button
                key={key}
                onClick={() => { setActiveTab(key); setResults(null); setError(null) }}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                  activeTab === key
                    ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                    : 'border border-white/10 text-slate-400 hover:border-teal-500/30 hover:text-teal-400'
                }`}
              >
                <span>{spec.icon}</span> {spec.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {fieldsToShow.map((field, i) => (
                <motion.div
                  key={field.key}
                  initial={reduced ? false : { opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                >
                  <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                    {field.label}
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={formValues[field.key] ?? ''}
                    onChange={e => handleField(field.key, e.target.value)}
                    className="w-full rounded-lg border border-white/10 bg-clinical-900 px-3 py-2 text-sm text-white outline-none transition focus:border-teal-400/60 focus:ring-1 focus:ring-teal-400/20"
                  />
                </motion.div>
              ))}
            </div>

            {error && (
              <div className="rounded-lg border border-red-500/30 bg-red-950/30 px-4 py-2.5 text-sm text-red-300">{error}</div>
            )}

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={reduced ? {} : { scale: 1.015 }}
              whileTap={reduced ? {} : { scale: 0.98 }}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-teal-500 py-3 text-sm font-bold text-slate-900 shadow-lg shadow-teal-500/20 transition hover:bg-teal-400 disabled:opacity-60"
            >
              {loading ? (
                <>
                  <motion.span
                    className="inline-block h-4 w-4 rounded-full border-2 border-slate-900 border-t-transparent"
                    animate={reduced ? {} : { rotate: 360 }}
                    transition={{ repeat: Infinity, duration: 0.7, ease: 'linear' }}
                  />
                  Running Assessment…
                </>
              ) : (
                `Run ${currentSpec.label} Assessment`
              )}
            </motion.button>
          </form>
        </motion.div>

        {/* RIGHT — Results */}
        <motion.div
          initial={reduced ? false : { opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="rounded-2xl border border-white/10 bg-clinical-800 p-6"
        >
          <h2 className="mb-4 text-sm font-bold uppercase tracking-wider text-slate-300">Assessment Results</h2>

          {!results && !loading && (
            <div className="flex flex-col items-center justify-center py-20 text-slate-500">
              <motion.div
                animate={reduced ? {} : { scale: [1, 1.06, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ repeat: Infinity, duration: 2.5, ease: 'easeInOut' }}
                className="mb-3 text-4xl"
              >
                🔬
              </motion.div>
              <p className="text-sm">Fill in patient data and run an assessment</p>
            </div>
          )}

          {results && (
            <div className="space-y-4">
              {/* Risk gauges */}
              <div className="flex flex-wrap gap-4 justify-center">
                <AnimatePresence>
                  {resultEntries.map(([specialty, data], i) => {
                    const score = typeof data.risk_score === 'number'
                      ? Math.round(data.risk_score * 100)
                      : typeof data.confidence === 'number'
                        ? Math.round(data.confidence * 100)
                        : 0
                    const level = data.risk_level as string || data.prediction as string || '—'
                    return (
                      <motion.div
                        key={specialty}
                        initial={reduced ? false : { opacity: 0, scale: 0.88 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1, type: 'spring', stiffness: 200, damping: 20 }}
                      >
                        <RiskGauge disease={specialty} riskScore={score} riskLevel={level} />
                      </motion.div>
                    )
                  })}
                </AnimatePresence>
              </div>

              {/* Profile summary toggle */}
              <div className="border-t border-white/10 pt-4">
                <button
                  onClick={() => setShowProfile(p => !p)}
                  className="flex items-center gap-2 text-xs text-slate-400 hover:text-teal-400 transition"
                >
                  <span>{showProfile ? '▾' : '▸'}</span>
                  Profile used in assessment
                </button>
                <AnimatePresence>
                  {showProfile && profileUsed && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="mt-3 grid grid-cols-2 gap-2">
                        {Object.entries(profileUsed).map(([k, v]) => (
                          <div key={k} className="flex justify-between rounded-lg border border-white/5 bg-clinical-900 px-3 py-1.5 text-xs">
                            <span className="text-slate-500 capitalize">{k.replace(/_/g, ' ')}</span>
                            <span className="font-mono text-teal-400">{String(v)}</span>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  )
}
