/**
 * Formatting utilities for display values.
 */

export const formatPercent = (value, decimals = 1) => {
  return `${(value * 100).toFixed(decimals)}%`
}

export const formatScore = (value, decimals = 2) => {
  return Number(value).toFixed(decimals)
}

export const formatRating = (value) => {
  return `${Number(value).toFixed(1)} / 10`
}

export const formatEffectiveness = (value) => {
  return `${Number(value).toFixed(1)} / 5`
}

export const getRiskColor = (riskLabel) => {
  switch (riskLabel?.toUpperCase()) {
    case 'LOW':    return { bg: 'bg-green-100',  text: 'text-green-800',  border: 'border-green-300',  dot: 'bg-green-500',  bar: '#16a34a' }
    case 'MEDIUM': return { bg: 'bg-amber-100',  text: 'text-amber-800',  border: 'border-amber-300',  dot: 'bg-amber-500',  bar: '#d97706' }
    case 'HIGH':   return { bg: 'bg-red-100',    text: 'text-red-800',    border: 'border-red-300',    dot: 'bg-red-500',    bar: '#dc2626' }
    default:       return { bg: 'bg-slate-100',  text: 'text-slate-700',  border: 'border-slate-300',  dot: 'bg-slate-500',  bar: '#64748b' }
  }
}

export const getRiskGradient = (riskLabel) => {
  switch (riskLabel?.toUpperCase()) {
    case 'LOW':    return 'from-green-50 to-emerald-50'
    case 'MEDIUM': return 'from-amber-50 to-orange-50'
    case 'HIGH':   return 'from-red-50 to-rose-50'
    default:       return 'from-slate-50 to-slate-100'
  }
}

export const capitalizeFirst = (str) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

export const formatConditionName = (condition) => {
  if (!condition) return ''
  return condition
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
