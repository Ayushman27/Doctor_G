import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  PlusCircle, Pill, AlertTriangle, Brain, BarChart3, Stethoscope,
  Utensils, CheckCircle2, XCircle, ShieldCheck, AlertOctagon,
  Activity, ListChecks, HeartHandshake, Info
} from 'lucide-react'
import {
  RadialBarChart, RadialBar, ResponsiveContainer, Cell, BarChart, Bar,
  XAxis, YAxis, Tooltip, CartesianGrid
} from 'recharts'
import RiskBadge from '../components/RiskBadge'
import DrugTable from '../components/DrugTable'
import DisclaimerBanner from '../components/DisclaimerBanner'
import { getRiskColor, formatPercent } from '../utils/formatters'

// ─── Probability bar ───────────────────────────────────────────────────────────

function ProbabilityBar({ label, value, isMax }) {
  const colors = getRiskColor(label)
  return (
    <div className={`rounded-xl p-4 border ${isMax ? colors.border + ' ' + colors.bg : 'border-slate-100 bg-slate-50'} transition-all`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={`w-2.5 h-2.5 rounded-full ${colors.dot}`} />
          <span className={`text-sm font-semibold ${isMax ? colors.text : 'text-slate-600'}`}>{label}</span>
          {isMax && <span className="text-xs bg-white/80 rounded-full px-2 py-0.5 text-slate-500 font-medium border">Predicted</span>}
        </div>
        <span className={`text-lg font-bold ${isMax ? colors.text : 'text-slate-700'}`}>
          {formatPercent(value)}
        </span>
      </div>
      <div className="h-2 bg-white/60 rounded-full overflow-hidden border border-white/40">
        <div
          className={`h-full rounded-full ${colors.dot} transition-all duration-700`}
          style={{ width: formatPercent(value) }}
        />
      </div>
    </div>
  )
}

const CHART_COLORS = { LOW: '#16a34a', MEDIUM: '#d97706', HIGH: '#dc2626' }

// ─── Main Component ───────────────────────────────────────────────────────────

export default function PredictionResult() {
  const navigate = useNavigate()
  const [result, setResult] = useState(null)

  useEffect(() => {
    const stored = sessionStorage.getItem('analysisResult')
    if (!stored) { navigate('/assessment'); return }
    setResult(JSON.parse(stored))
  }, [navigate])

  if (!result) return null

  const { patient_risk, condition, clinical_guidance, drug_candidates } = result
  const { risk_label, risk_class, probabilities, model_used, model_version } = patient_risk
  const probs = probabilities
  const maxProb = Math.max(probs.LOW, probs.MEDIUM, probs.HIGH)
  const riskColors = getRiskColor(risk_label)

  const barData = [
    { name: 'LOW',    value: probs.LOW,    pct: Math.round(probs.LOW * 100) },
    { name: 'MEDIUM', value: probs.MEDIUM, pct: Math.round(probs.MEDIUM * 100) },
    { name: 'HIGH',   value: probs.HIGH,   pct: Math.round(probs.HIGH * 100) },
  ]

  const radialData = [
    { name: 'HIGH',   value: Math.round(probs.HIGH * 100),   fill: CHART_COLORS.HIGH },
    { name: 'MEDIUM', value: Math.round(probs.MEDIUM * 100), fill: CHART_COLORS.MEDIUM },
    { name: 'LOW',    value: Math.round(probs.LOW * 100),    fill: CHART_COLORS.LOW },
  ]

  return (
    <div className="p-6 lg:p-8 max-w-5xl mx-auto animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Patient Risk & Clinical Analysis</h1>
          <p className="text-sm text-slate-500 mt-0.5">Comprehensive stratification, diet recommendations, and action plan</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => navigate('/assessment')} className="btn-secondary">
            <PlusCircle size={15} />
            New Assessment
          </button>
        </div>
      </div>

      {/* Risk Hero Card */}
      <div className={`card border-2 ${riskColors.border} bg-gradient-to-br ${
        risk_label === 'LOW' ? 'from-green-50 to-emerald-50' :
        risk_label === 'MEDIUM' ? 'from-amber-50 to-orange-50' : 'from-red-50 to-rose-50'
      }`}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Predicted Risk Class</p>
            <RiskBadge label={risk_label} size="xl" />
            <p className="text-xs text-slate-500 mt-3">
              Risk confidence: <span className="font-semibold text-slate-700">{formatPercent(maxProb)}</span>
            </p>
          </div>

          {/* Radial Chart */}
          <div className="w-44 h-44 flex-shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                cx="50%" cy="50%"
                innerRadius="35%" outerRadius="90%"
                startAngle={90} endAngle={-270}
                data={radialData}
              >
                <RadialBar dataKey="value" cornerRadius={4} background={{ fill: '#f1f5f9' }} />
                <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle"
                  className="text-xl font-bold" fill={CHART_COLORS[risk_label]} fontSize={22} fontWeight={700}>
                  {Math.round(maxProb * 100)}%
                </text>
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 🏥 1. Medical Problem Identification & Test Insights */}
      {clinical_guidance && (
        <div className="card border-l-4 border-l-primary-600 bg-white shadow-sm space-y-5">
          <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Stethoscope size={20} className="text-primary-600" />
                <span className="text-xs font-bold uppercase tracking-wider text-primary-700 bg-primary-50 px-2.5 py-0.5 rounded-full border border-primary-200">
                  Medical Problem Identification
                </span>
              </div>
              <h2 className="text-xl font-bold text-slate-800">
                {clinical_guidance.disease_name}
              </h2>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400 font-medium block">Clinical Severity</span>
              <span className={`inline-block text-xs font-semibold px-3 py-1 rounded-full mt-1 ${
                risk_label === 'HIGH' ? 'bg-red-100 text-red-800 border border-red-200' :
                risk_label === 'MEDIUM' ? 'bg-amber-100 text-amber-800 border border-amber-200' :
                'bg-emerald-100 text-emerald-800 border border-emerald-200'
              }`}>
                {clinical_guidance.severity}
              </span>
            </div>
          </div>

          {/* Test Insights derived from patient test data */}
          {clinical_guidance.test_insights && clinical_guidance.test_insights.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Activity size={14} className="text-primary-600" />
                Key Findings From Patient Test Data
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {clinical_guidance.test_insights.map((insight, idx) => (
                  <div key={idx} className="flex items-start gap-2 bg-slate-50 border border-slate-200/80 rounded-lg p-2.5 text-xs text-slate-700">
                    <Info size={14} className="text-primary-500 mt-0.5 flex-shrink-0" />
                    <span>{insight}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Underlying Causes & Risk Factors */}
          {clinical_guidance.causes && clinical_guidance.causes.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <AlertTriangle size={14} className="text-amber-500" />
                Underlying Causes & Physiological Risk Factors
              </h3>
              <ul className="space-y-1.5 text-sm text-slate-600">
                {clinical_guidance.causes.map((cause, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0" />
                    <span>{cause}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 🥗 2. Diet & Nutritional Guidance (What to Eat vs What NOT to Eat) */}
      {clinical_guidance && clinical_guidance.diet_plan && (
        <div className="card space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <Utensils size={20} className="text-emerald-600" />
            <h2 className="text-lg font-bold text-slate-800">Diet & Nutritional Guidance</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Recommended Diet (What to Eat / Do) */}
            <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3 pb-2 border-b border-emerald-200/80">
                <CheckCircle2 size={18} className="text-emerald-600" />
                <h3 className="text-sm font-bold text-emerald-900">
                  Recommended Foods & Diet (What to Eat)
                </h3>
              </div>
              <ul className="space-y-2 text-xs md:text-sm text-emerald-950">
                {clinical_guidance.diet_plan.recommended.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 size={14} className="text-emerald-600 mt-0.5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Foods to Avoid (What NOT to Eat) */}
            <div className="bg-rose-50/70 border border-rose-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3 pb-2 border-b border-rose-200/80">
                <XCircle size={18} className="text-rose-600" />
                <h3 className="text-sm font-bold text-rose-900">
                  Foods to Avoid & Restrict (What NOT to Eat)
                </h3>
              </div>
              <ul className="space-y-2 text-xs md:text-sm text-rose-950">
                {clinical_guidance.diet_plan.avoid.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <XCircle size={14} className="text-rose-600 mt-0.5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 📋 3. Action Guidelines (What TO Do vs What NOT To Do) */}
      {clinical_guidance && (clinical_guidance.what_to_do || clinical_guidance.what_not_to_do) && (
        <div className="card space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <ListChecks size={20} className="text-teal-600" />
            <h2 className="text-lg font-bold text-slate-800">Action Plan & Clinical Guidelines</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* What TO Do */}
            {clinical_guidance.what_to_do && clinical_guidance.what_to_do.length > 0 && (
              <div className="bg-teal-50/70 border border-teal-200 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3 pb-2 border-b border-teal-200/80">
                  <ShieldCheck size={18} className="text-teal-600" />
                  <h3 className="text-sm font-bold text-teal-900">
                    What TO Do (Recommended Actions)
                  </h3>
                </div>
                <ul className="space-y-2 text-xs md:text-sm text-teal-950">
                  {clinical_guidance.what_to_do.map((action, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <ShieldCheck size={14} className="text-teal-600 mt-0.5 flex-shrink-0" />
                      <span>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* What NOT To Do */}
            {clinical_guidance.what_not_to_do && clinical_guidance.what_not_to_do.length > 0 && (
              <div className="bg-amber-50/80 border border-amber-200 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3 pb-2 border-b border-amber-200/80">
                  <AlertOctagon size={18} className="text-amber-600" />
                  <h3 className="text-sm font-bold text-amber-950">
                    What NOT To Do (Strictly Avoid)
                  </h3>
                </div>
                <ul className="space-y-2 text-xs md:text-sm text-amber-950">
                  {clinical_guidance.what_not_to_do.map((avoidItem, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <AlertOctagon size={14} className="text-amber-600 mt-0.5 flex-shrink-0" />
                      <span>{avoidItem}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 💡 4. Lifestyle & General Recommendations */}
      {clinical_guidance && clinical_guidance.lifestyle_advice && clinical_guidance.lifestyle_advice.length > 0 && (
        <div className="card bg-slate-50/80 border border-slate-200">
          <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
            <HeartHandshake size={16} className="text-primary-600" />
            General Lifestyle & Monitoring Guidelines
          </h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs md:text-sm text-slate-700">
            {clinical_guidance.lifestyle_advice.map((advice, idx) => (
              <li key={idx} className="flex items-start gap-2 bg-white p-2.5 rounded-lg border border-slate-100 shadow-2xs">
                <span className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-2 flex-shrink-0" />
                <span>{advice}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 📊 Risk Probability Breakdown & Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Probability breakdown */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <BarChart3 size={16} className="text-primary-600" />
            Risk Probability Breakdown
          </h2>
          <div className="space-y-3">
            {['LOW', 'MEDIUM', 'HIGH'].map(label => (
              <ProbabilityBar
                key={label}
                label={label}
                value={probs[label]}
                isMax={probs[label] === maxProb}
              />
            ))}
          </div>
        </div>

        {/* Bar chart + model info */}
        <div className="space-y-4">
          <div className="card">
            <h2 className="text-sm font-semibold text-slate-800 mb-4">Probability Comparison</h2>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={barData} barSize={36}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} domain={[0, 100]} tickFormatter={v => `${v}%`} />
                <Tooltip formatter={(v) => [`${v}%`, 'Probability']} />
                <Bar dataKey="pct" radius={[6, 6, 0, 0]}>
                  {barData.map((entry) => (
                    <Cell key={entry.name} fill={CHART_COLORS[entry.name]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h2 className="text-sm font-semibold text-slate-800 mb-3 flex items-center gap-2">
              <Brain size={15} className="text-primary-600" />
              Model Information
            </h2>
            <dl className="space-y-2 text-sm">
              {[
                ['Model', model_used],
                ['Risk Class Index', risk_class],
                ['Model Version', model_version],
                ['Condition', condition || '—'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-1.5 border-b border-slate-50 last:border-0">
                  <dt className="text-slate-500">{k}</dt>
                  <dd className="font-semibold text-slate-800">{v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* 💊 5. Drug Candidates Table */}
      {drug_candidates && (
        <div className="card">
          <div className="flex items-center gap-2 mb-5">
            <Pill size={18} className="text-teal-600" />
            <div>
              <h2 className="text-base font-semibold text-slate-800">Historical Drug Candidates</h2>
              <p className="text-xs text-slate-400 capitalize">
                Condition: <span className="font-medium text-slate-600">{condition}</span>
              </p>
            </div>
          </div>
          <DrugTable candidates={drug_candidates} condition={condition} />
        </div>
      )}

      {/* Disclaimer */}
      <DisclaimerBanner />

      {/* Actions */}
      <div className="flex justify-center pt-2">
        <button onClick={() => navigate('/assessment')} className="btn-primary">
          <PlusCircle size={16} />
          Start New Assessment
        </button>
      </div>
    </div>
  )
}
