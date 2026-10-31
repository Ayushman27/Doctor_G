import { useEffect, useState } from 'react'
import { FlaskConical, Cpu, Database, CheckCircle, BarChart2 } from 'lucide-react'
import { getModelInfo } from '../services/api'
import PipelineViz from '../components/PipelineViz'
import { CardSkeleton } from '../components/LoadingSkeleton'

function MetricRow({ label, value, format = 'pct' }) {
  const display = format === 'pct' ? `${(value * 100).toFixed(2)}%` : value
  const pct = format === 'pct' ? value * 100 : 0
  return (
    <div className="flex items-center gap-4 py-2.5 border-b border-slate-50 last:border-0">
      <div className="flex-1">
        <span className="text-sm text-slate-700 font-medium">{label}</span>
      </div>
      <div className="w-32">
        <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-primary-500 transition-all duration-700"
            style={{ width: `${pct}%` }} />
        </div>
      </div>
      <span className="text-sm font-bold text-slate-800 w-16 text-right">{display}</span>
    </div>
  )
}

export default function ModelInfo() {
  const [info, setInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getModelInfo()
      .then(setInfo)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="p-6 lg:p-8 max-w-5xl mx-auto">
        <div className="h-8 bg-slate-200 rounded w-64 mb-8 animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CardSkeleton lines={5} /><CardSkeleton lines={5} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-600">
        <p className="font-semibold mb-1">Failed to load model information</p>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    )
  }

  const { metadata, metrics, version, feature_summary } = info || {}
  const xgbMetrics = metrics?.tuned_xgboost || {}
  const rfMetrics  = metrics?.random_forest  || {}

  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto animate-fade-in">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1">
          <FlaskConical size={22} className="text-primary-600" />
          <h1 className="text-2xl font-bold text-slate-800">Model Information</h1>
        </div>
        <p className="text-sm text-slate-500">Evaluation metrics, architecture details, and feature metadata.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Overview */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Cpu size={15} className="text-primary-600" /> Model Overview
          </h2>
          <dl className="space-y-0">
            {[
              ['Primary Model', metadata?.primary_model],
              ['Secondary Model', metadata?.secondary_model],
              ['Model Version', version?.model_version],
              ['Training Random State', version?.training_random_state],
              ['Risk Classes', version?.risk_classes?.join(', ')],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between py-2.5 border-b border-slate-50 last:border-0">
                <dt className="text-sm text-slate-500">{k}</dt>
                <dd className="text-sm font-semibold text-slate-800">{v ?? '—'}</dd>
              </div>
            ))}
          </dl>
        </div>

        {/* Dataset */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Database size={15} className="text-teal-600" /> Dataset Information
          </h2>
          <dl className="space-y-0">
            {[
              ['Patient Dataset', metadata?.patient_dataset],
              ['Drug Dataset', metadata?.drug_dataset],
              ['Original Features', feature_summary?.total_original_features],
              ['Processed Features', feature_summary?.total_processed_features?.toLocaleString()],
              ['Numeric Features', feature_summary?.numerical_features_count],
              ['Categorical Features', feature_summary?.categorical_features_count],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between py-2.5 border-b border-slate-50 last:border-0">
                <dt className="text-sm text-slate-500">{k}</dt>
                <dd className="text-sm font-semibold text-slate-800 text-right max-w-xs">{v ?? '—'}</dd>
              </div>
            ))}
          </dl>
        </div>

        {/* XGBoost metrics */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <BarChart2 size={15} className="text-primary-600" />
            XGBoost Evaluation Metrics
            <span className="text-xs bg-primary-50 text-primary-600 px-2 py-0.5 rounded-full ml-auto font-medium">Test Set</span>
          </h2>
          <div className="space-y-0">
            {[
              ['Accuracy', xgbMetrics.Accuracy],
              ['Precision', xgbMetrics.Precision],
              ['Recall', xgbMetrics.Recall],
              ['F1 Score', xgbMetrics.F1],
            ].map(([label, value]) => (
              <MetricRow key={label} label={label} value={value ?? 0} />
            ))}
          </div>
        </div>

        {/* Random Forest metrics */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <BarChart2 size={15} className="text-teal-600" />
            Random Forest Evaluation Metrics
            <span className="text-xs bg-teal-50 text-teal-600 px-2 py-0.5 rounded-full ml-auto font-medium">Validation Set</span>
          </h2>
          <div className="space-y-0">
            {[
              ['Accuracy', rfMetrics.Accuracy],
              ['Precision', rfMetrics.Precision],
              ['Recall', rfMetrics.Recall],
              ['F1 Score', rfMetrics.F1],
            ].map(([label, value]) => (
              <MetricRow key={label} label={label} value={value ?? 0} />
            ))}
          </div>
        </div>
      </div>

      {/* Risk mapping */}
      <div className="card mb-6">
        <h2 className="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <CheckCircle size={15} className="text-green-600" /> Risk Class Mapping
        </h2>
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(metadata?.risk_mapping || { '0': 'LOW', '1': 'MEDIUM', '2': 'HIGH' }).map(([cls, label]) => {
            const colors = label === 'LOW' ? 'bg-green-50 border-green-200 text-green-700' :
                           label === 'MEDIUM' ? 'bg-amber-50 border-amber-200 text-amber-700' :
                                                'bg-red-50 border-red-200 text-red-700'
            return (
              <div key={cls} className={`rounded-xl border p-4 text-center ${colors}`}>
                <div className="text-2xl font-bold">{cls}</div>
                <div className="text-xs font-semibold mt-1 uppercase tracking-wide">{label}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Pipeline */}
      <div className="card">
        <h2 className="text-sm font-semibold text-slate-800 mb-6 text-center">Inference Pipeline</h2>
        <PipelineViz />
      </div>
    </div>
  )
}
