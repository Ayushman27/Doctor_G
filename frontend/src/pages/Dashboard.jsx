import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, Zap, ShieldCheck, BarChart2, BookOpen, ArrowRight, Brain, FlaskConical } from 'lucide-react'
import { getHealth, getModelInfo, getConditions } from '../services/api'
import MetricCard from '../components/MetricCard'
import DisclaimerBanner from '../components/DisclaimerBanner'

export default function Dashboard() {
  const navigate = useNavigate()
  const [health, setHealth] = useState(null)
  const [modelInfo, setModelInfo] = useState(null)
  const [conditionCount, setConditionCount] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [h, m, c] = await Promise.all([getHealth(), getModelInfo(), getConditions()])
        setHealth(h)
        setModelInfo(m)
        setConditionCount(c.total)
      } catch (err) {
        setError(err.message || 'Unable to connect to AI backend.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const version = health?.model_version ?? '—'
  const primaryModel = modelInfo?.metadata?.primary_model ?? 'XGBoost'

  const features = [
    {
      icon: ShieldCheck,
      title: 'Patient Risk Stratification',
      desc: 'ML-based classification of patient readmission risk into LOW, MEDIUM, or HIGH classes using tuned XGBoost.',
      accent: 'text-primary-600 bg-primary-50',
    },
    {
      icon: FlaskConical,
      title: 'Drug Candidate Analysis',
      desc: 'Historical drug ranking by condition using composite scores from effectiveness, rating, and side-effect data.',
      accent: 'text-teal-600 bg-teal-50',
    },
    {
      icon: Brain,
      title: 'Model Explainability',
      desc: 'View actual model metrics, feature metadata, and the full preprocessing pipeline used during inference.',
      accent: 'text-indigo-600 bg-indigo-50',
    },
    {
      icon: BookOpen,
      title: 'Research Decision Support',
      desc: 'Designed as an educational prototype to assist clinical researchers — not a diagnostic or prescription system.',
      accent: 'text-amber-600 bg-amber-50',
    },
  ]

  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-2xl bg-primary-600 flex items-center justify-center shadow-sm">
            <Activity size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Intelligent Patient AI</h1>
            <p className="text-sm text-slate-500">Patient Stratification & Drug Candidate Analysis</p>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && !loading && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-700">
          <strong>Connection Error:</strong> {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard label="Primary Model" value={loading ? '...' : primaryModel}
          subtitle="ML Inference Engine" icon={Zap} accent="primary" loading={loading} />
        <MetricCard label="Risk Classes" value="3"
          subtitle="LOW / MEDIUM / HIGH" icon={BarChart2} accent="teal" loading={false} />
        <MetricCard label="Drug Conditions" value={loading ? '...' : conditionCount}
          subtitle="Historical drug data" icon={FlaskConical} accent="green" loading={loading} />
        <MetricCard label="Model Version" value={loading ? '...' : `v${version}`}
          subtitle="Trained on UCI dataset" icon={Activity} accent="slate" loading={loading} />
      </div>

      {/* CTA */}
      <div className="card bg-gradient-to-br from-primary-600 to-primary-700 border-0 text-white mb-8 shadow-lg">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold mb-1">Start a Patient Assessment</h2>
            <p className="text-primary-200 text-sm max-w-md">
              Enter patient clinical data to receive an ML-based risk stratification and
              historical drug candidate ranking for the selected condition.
            </p>
          </div>
          <button
            id="start-assessment-btn"
            onClick={() => navigate('/assessment')}
            className="flex items-center gap-2 px-6 py-3 bg-white text-primary-700 rounded-xl font-semibold text-sm
                       hover:bg-primary-50 transition-colors duration-150 flex-shrink-0 shadow-sm"
          >
            Start Assessment
            <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
        {features.map(({ icon: Icon, title, desc, accent }) => (
          <div key={title} className="card card-hover">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${accent} mb-3`}>
              <Icon size={18} />
            </div>
            <h3 className="font-semibold text-slate-800 mb-1.5 text-sm">{title}</h3>
            <p className="text-xs text-slate-500 leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      {/* Disclaimer */}
      <DisclaimerBanner />
    </div>
  )
}
