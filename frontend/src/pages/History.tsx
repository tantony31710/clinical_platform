import { useEffect, useState } from 'react'
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion'
import { getHistory, exportCsv, HistoryEntry } from '../lib/api'
import RiskGauge from '../components/RiskGauge'

export default function History() {
  const reduced = useReducedMotion() ?? false
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<Set<number>>(new Set())
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    getHistory()
      .then(data => setHistory([...data].reverse()))  // newest first
      .finally(() => setLoading(false))
  }, [])

  const toggle = (id: number) => {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const handleExport = async () => {
    setExporting(true)
    try { await exportCsv() } finally { setExporting(false) }
  }

  return (
    <div className="min-h-screen bg-clinical-900 text-slate-200">
      {/* Header */}
      <header className="sticky top-0 z-30 border-b border-white/10 bg-clinical-800/80 backdrop-blur">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <a href="/dashboard" className="text-slate-400 hover:text-teal-400 transition text-sm">← Dashboard</a>
            <h1 className="text-base font-bold text-white">Assessment History</h1>
          </div>
          <motion.button
            onClick={handleExport}
            disabled={exporting || history.length === 0}
            whileHover={reduced ? {} : { scale: 1.03 }}
            whileTap={reduced ? {} : { scale: 0.97 }}
            className="flex items-center gap-2 rounded-lg bg-teal-500/20 border border-teal-500/30 px-4 py-2 text-xs font-semibold text-teal-300 hover:bg-teal-500/30 transition disabled:opacity-40"
          >
            {exporting ? '⏳' : '⬇'} Export CSV
          </motion.button>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-10">
        {loading ? (
          <div className="flex justify-center py-20">
            <motion.div
              className="h-8 w-8 rounded-full border-2 border-teal-400 border-t-transparent"
              animate={reduced ? {} : { rotate: 360 }}
              transition={{ repeat: Infinity, duration: 0.8, ease: 'linear' }}
            />
          </div>
        ) : history.length === 0 ? (
          <motion.div
            initial={reduced ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20 text-slate-500"
          >
            <div className="mb-4 text-5xl">📋</div>
            <p className="text-lg font-semibold text-slate-400">No assessments yet</p>
            <p className="mt-1 text-sm">Run your first assessment from the dashboard.</p>
          </motion.div>
        ) : (
          <div className="relative">
            {/* Vertical timeline line */}
            <div className="absolute left-5 top-0 bottom-0 w-px bg-teal-500/20" />

            <div className="space-y-4 pl-14">
              {history.map((entry, i) => {
                const isOpen = expanded.has(entry.id)
                const resultEntries = Object.entries(entry.results).filter(([, v]) => v && typeof v === 'object')

                return (
                  <motion.div
                    key={entry.id}
                    initial={reduced ? false : { opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06, duration: 0.3 }}
                    className="relative"
                  >
                    {/* Timeline dot */}
                    <div className="absolute -left-9 top-4 h-3 w-3 rounded-full border-2 border-teal-400 bg-clinical-900" />

                    <div className="rounded-2xl border border-white/10 bg-clinical-800 overflow-hidden">
                      {/* Entry header */}
                      <button
                        onClick={() => toggle(entry.id)}
                        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-white/5 transition"
                      >
                        <div className="flex items-center gap-4">
                          <div>
                            <div className="text-sm font-semibold text-white">
                              {new Date(entry.timestamp).toLocaleDateString('en-US', {
                                year: 'numeric', month: 'short', day: 'numeric',
                                hour: '2-digit', minute: '2-digit',
                              })}
                            </div>
                            <div className="mt-1 flex flex-wrap gap-1.5">
                              {resultEntries.map(([specialty, data]) => {
                                const score = typeof data.risk_score === 'number'
                                  ? Math.round(data.risk_score * 100)
                                  : typeof data.confidence === 'number'
                                    ? Math.round(data.confidence * 100)
                                    : 0
                                const color = score < 40 ? '#22c55e' : score < 70 ? '#f59e0b' : '#ef4444'
                                return (
                                  <span
                                    key={specialty}
                                    className="rounded-md px-2 py-0.5 text-[10px] font-bold uppercase"
                                    style={{ color, background: `${color}18`, border: `1px solid ${color}40` }}
                                  >
                                    {specialty.replace(/_/g, ' ')}: {score}%
                                  </span>
                                )
                              })}
                            </div>
                          </div>
                        </div>
                        <span className={`text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>▾</span>
                      </button>

                      {/* Expanded details */}
                      <AnimatePresence initial={false}>
                        {isOpen && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.28 }}
                            className="overflow-hidden"
                          >
                            <div className="border-t border-white/10 px-5 py-5 space-y-5">
                              {/* Risk gauges */}
                              <div className="flex flex-wrap gap-4 justify-center">
                                {resultEntries.map(([specialty, data]) => {
                                  const score = typeof data.risk_score === 'number'
                                    ? Math.round(data.risk_score * 100)
                                    : typeof data.confidence === 'number'
                                      ? Math.round(data.confidence * 100)
                                      : 0
                                  const level = (data.risk_level as string) || (data.prediction as string) || '—'
                                  return <RiskGauge key={specialty} disease={specialty} riskScore={score} riskLevel={level} />
                                })}
                              </div>

                              {/* Profile fields */}
                              <div>
                                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Patient Profile</p>
                                <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                                  {Object.entries(entry.profile).map(([k, v]) => (
                                    <div key={k} className="flex justify-between rounded-lg border border-white/5 bg-clinical-900 px-3 py-1.5 text-xs">
                                      <span className="text-slate-500 capitalize">{k.replace(/_/g, ' ')}</span>
                                      <span className="font-mono text-teal-400">{String(v)}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
