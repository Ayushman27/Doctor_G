import { ArrowDown } from 'lucide-react'

const steps = [
  { label: 'Patient Input', desc: 'Clinical data entry' },
  { label: 'Validation', desc: 'Schema & range checks' },
  { label: 'Preprocessing', desc: 'ColumnTransformer' },
  { label: 'XGBoost', desc: 'Tuned classifier' },
  { label: 'Risk Stratification', desc: 'LOW / MEDIUM / HIGH' },
  { label: 'Condition Matching', desc: 'Drug summary lookup' },
  { label: 'Drug Candidate Ranking', desc: 'Score-based ranking' },
  { label: 'Decision Support', desc: 'Research output' },
]

export default function PipelineViz() {
  return (
    <div className="flex flex-col items-center gap-0 py-2">
      {steps.map((step, idx) => {
        const isFirst = idx === 0
        const isLast = idx === steps.length - 1
        const accent =
          idx === 0 ? 'bg-primary-50 border-primary-200 text-primary-700' :
          idx === 4 ? 'bg-amber-50 border-amber-200 text-amber-700' :
          idx === 6 ? 'bg-teal-50 border-teal-200 text-teal-700' :
          isLast    ? 'bg-green-50 border-green-200 text-green-700' :
                      'bg-slate-50 border-slate-200 text-slate-600'

        return (
          <div key={step.label} className="flex flex-col items-center" style={{ animationDelay: `${idx * 60}ms` }}>
            <div className={`px-5 py-2.5 rounded-xl border font-medium text-sm text-center min-w-56 ${accent}
                             transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 animate-fade-in`}>
              <div className="font-semibold">{step.label}</div>
              <div className="text-xs opacity-70 mt-0.5">{step.desc}</div>
            </div>
            {!isLast && (
              <div className="flex flex-col items-center my-0.5">
                <div className="w-px h-3 bg-slate-200" />
                <ArrowDown size={14} className="text-slate-300" />
                <div className="w-px h-2 bg-slate-200" />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
