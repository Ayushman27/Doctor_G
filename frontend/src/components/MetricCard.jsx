export default function MetricCard({ label, value, subtitle, icon: Icon, accent = 'primary', loading = false }) {
  const accentClasses = {
    primary: 'bg-primary-50 text-primary-600',
    teal:    'bg-teal-50 text-teal-600',
    green:   'bg-green-50 text-green-600',
    amber:   'bg-amber-50 text-amber-600',
    red:     'bg-red-50 text-red-600',
    slate:   'bg-slate-100 text-slate-600',
  }

  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-3 bg-slate-200 rounded w-1/2 mb-3"></div>
        <div className="h-7 bg-slate-200 rounded w-2/3 mb-2"></div>
        <div className="h-2.5 bg-slate-100 rounded w-1/3"></div>
      </div>
    )
  }

  return (
    <div className="card card-hover">
      <div className="flex items-start justify-between mb-3">
        <p className="text-sm font-medium text-slate-500">{label}</p>
        {Icon && (
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${accentClasses[accent]}`}>
            <Icon size={16} />
          </div>
        )}
      </div>
      <div className="text-2xl font-bold text-slate-800 mb-1">{value ?? '—'}</div>
      {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
    </div>
  )
}
