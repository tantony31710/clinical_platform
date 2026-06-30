import { useEffect, useRef, useState } from 'react'
import { motion, useReducedMotion } from 'framer-motion'

interface RiskGaugeProps {
  disease: string
  riskScore: number   // 0–100
  riskLevel: string
}

function riskColor(score: number): string {
  if (score < 40) return '#22c55e'
  if (score < 70) return '#f59e0b'
  return '#ef4444'
}

function riskBg(score: number): string {
  if (score < 40) return 'rgba(34,197,94,0.08)'
  if (score < 70) return 'rgba(245,158,11,0.08)'
  return 'rgba(239,68,68,0.08)'
}

// SVG arc helper — returns a path string for a semicircle arc
function describeArc(cx: number, cy: number, r: number, startAngle: number, endAngle: number): string {
  const toRad = (deg: number) => (deg * Math.PI) / 180
  const x1 = cx + r * Math.cos(toRad(startAngle))
  const y1 = cy + r * Math.sin(toRad(startAngle))
  const x2 = cx + r * Math.cos(toRad(endAngle))
  const y2 = cy + r * Math.sin(toRad(endAngle))
  const largeArc = endAngle - startAngle > 180 ? 1 : 0
  return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`
}

const CX = 100
const CY = 90
const RADIUS = 70
const START_ANGLE = 180
const TOTAL_ANGLE = 180
const CIRCUMFERENCE = Math.PI * RADIUS  // half-circle arc length ≈ 219.9

export default function RiskGauge({ disease, riskScore, riskLevel }: RiskGaugeProps) {
  const reduced = useReducedMotion() ?? false
  const clampedScore = Math.min(100, Math.max(0, riskScore))
  const color = riskColor(clampedScore)
  const bg = riskBg(clampedScore)

  // Count-up display number
  const [displayNum, setDisplayNum] = useState(reduced ? clampedScore : 0)
  const rafRef = useRef<number>(0)

  useEffect(() => {
    if (reduced) { setDisplayNum(clampedScore); return }
    const start = performance.now()
    const duration = 1400
    const animate = (now: number) => {
      const progress = Math.min((now - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)   // cubic ease-out
      setDisplayNum(Math.round(eased * clampedScore))
      if (progress < 1) rafRef.current = requestAnimationFrame(animate)
    }
    rafRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(rafRef.current)
  }, [clampedScore, reduced])

  // Foreground arc length = fraction of total semicircle
  const arcLength = (clampedScore / 100) * CIRCUMFERENCE

  return (
    <motion.div
      initial={reduced ? false : { opacity: 0, scale: 0.92 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className="flex flex-col items-center p-4 rounded-2xl border border-white/10"
      style={{ background: bg, width: 200 }}
    >
      <svg viewBox="0 0 200 110" width="200" height="110" aria-label={`${disease} risk gauge`}>
        {/* Background track */}
        <path
          d={describeArc(CX, CY, RADIUS, START_ANGLE, START_ANGLE + TOTAL_ANGLE)}
          fill="none"
          stroke="#1e293b"
          strokeWidth={10}
          strokeLinecap="round"
        />

        {/* Coloured foreground arc */}
        <motion.path
          d={describeArc(CX, CY, RADIUS, START_ANGLE, START_ANGLE + TOTAL_ANGLE)}
          fill="none"
          stroke={color}
          strokeWidth={10}
          strokeLinecap="round"
          strokeDasharray={`${CIRCUMFERENCE}`}
          initial={{ strokeDashoffset: CIRCUMFERENCE }}
          animate={{ strokeDashoffset: reduced ? CIRCUMFERENCE - arcLength : CIRCUMFERENCE - arcLength }}
          transition={reduced ? { duration: 0 } : { duration: 1.4, ease: [0.22, 1, 0.36, 1] }}
          style={{ filter: `drop-shadow(0 0 4px ${color}88)` }}
        />

        {/* Centre percentage */}
        <text x={CX} y={CY - 4} textAnchor="middle" fontSize="22" fontWeight="700" fill={color} fontFamily="Inter, sans-serif">
          {displayNum}%
        </text>
        <text x={CX} y={CY + 14} textAnchor="middle" fontSize="9" fill="#94a3b8" fontFamily="Inter, sans-serif" letterSpacing="0.1em">
          RISK SCORE
        </text>
      </svg>

      {/* Disease label */}
      <div className="mt-1 text-center">
        <div className="text-sm font-semibold text-slate-200 capitalize">
          {disease.replace(/_/g, ' ')}
        </div>
        <div
          className="mt-1 inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wide"
          style={{ color, background: `${color}20`, border: `1px solid ${color}40` }}
        >
          {riskLevel}
        </div>
      </div>
    </motion.div>
  )
}
