export function CardSkeleton({ lines = 3, className = '' }) {
  return (
    <div className={`card animate-pulse ${className}`}>
      <div className="h-3 bg-slate-200 rounded w-1/3 mb-4"></div>
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className={`h-2.5 bg-slate-100 rounded mb-2.5 ${i === lines - 1 ? 'w-1/2' : 'w-full'}`}></div>
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="space-y-2">
      <div className="h-9 bg-slate-100 rounded-xl animate-pulse mb-3" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-12 bg-slate-50 rounded-xl animate-pulse" style={{ opacity: 1 - i * 0.15 }} />
      ))}
    </div>
  )
}

export function FormSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {[1,2,3].map(s => (
        <div key={s} className="card">
          <div className="h-3 bg-slate-200 rounded w-1/4 mb-5" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1,2,3,4].map(f => (
              <div key={f}>
                <div className="h-2.5 bg-slate-100 rounded w-1/3 mb-2" />
                <div className="h-9 bg-slate-100 rounded-lg" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default function LoadingSkeleton({ type = 'card', ...props }) {
  if (type === 'table') return <TableSkeleton {...props} />
  if (type === 'form') return <FormSkeleton />
  return <CardSkeleton {...props} />
}
