import { getRiskColor } from '../utils/formatters'

export default function RiskBadge({ label, size = 'md', showDot = true }) {
  const colors = getRiskColor(label)
  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5 font-bold',
    xl: 'text-xl px-6 py-2 font-extrabold tracking-wide',
  }

  return (
    <span className={`inline-flex items-center gap-2 rounded-full border font-semibold
                      ${colors.bg} ${colors.text} ${colors.border} ${sizes[size]}`}>
      {showDot && (
        <span className={`w-2 h-2 rounded-full ${colors.dot} flex-shrink-0`} />
      )}
      {label}
    </span>
  )
}
