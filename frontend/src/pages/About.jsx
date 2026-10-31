import { ShieldAlert, BookOpen, FlaskConical, Users, AlertTriangle, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

function Section({ icon: Icon, title, accent, children }) {
  return (
    <div className={`card border-l-4 ${accent}`}>
      <div className="flex items-start gap-3 mb-3">
        <Icon size={18} className="text-slate-600 mt-0.5 flex-shrink-0" />
        <h2 className="text-base font-semibold text-slate-800">{title}</h2>
      </div>
      <div className="text-sm text-slate-600 leading-relaxed space-y-2 pl-7">
        {children}
      </div>
    </div>
  )
}

export default function About() {
  const navigate = useNavigate()

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center">
            <AlertTriangle size={20} className="text-amber-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">About & Disclaimer</h1>
            <p className="text-sm text-slate-500">Important information about this system</p>
          </div>
        </div>
      </div>

      {/* Primary disclaimer */}
      <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-6 mb-6">
        <div className="flex items-start gap-3">
          <ShieldAlert size={22} className="text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <h2 className="text-base font-bold text-amber-900 mb-2">⚠ Research & Educational Prototype Only</h2>
            <p className="text-sm text-amber-800 leading-relaxed font-medium">
              This application is a <strong>research and educational decision-support prototype</strong>.
              It is NOT approved for clinical use and must NOT be used to:
            </p>
            <ul className="mt-2 space-y-1 text-sm text-amber-800">
              <li className="flex items-start gap-2"><span className="text-amber-600 font-bold mt-0.5">×</span> Diagnose any disease or medical condition</li>
              <li className="flex items-start gap-2"><span className="text-amber-600 font-bold mt-0.5">×</span> Prescribe or recommend medications</li>
              <li className="flex items-start gap-2"><span className="text-amber-600 font-bold mt-0.5">×</span> Replace professional medical judgment</li>
              <li className="flex items-start gap-2"><span className="text-amber-600 font-bold mt-0.5">×</span> Make treatment decisions for any patient</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Sections */}
      <div className="space-y-4 mb-8">
        <Section icon={FlaskConical} title="Patient Risk Stratification" accent="border-primary-300">
          <p>
            The patient risk stratification model predicts <strong>hospital readmission-related risk classes</strong> using
            a machine-learning model trained on the{' '}
            <strong>UCI Diabetes 130-US Hospitals for Years 1999–2008</strong> dataset (public research dataset).
          </p>
          <p>
            The model classifies patients into three risk categories:
            <strong> LOW, MEDIUM, </strong>and<strong> HIGH</strong>.
            These classes reflect readmission risk patterns observed in the training dataset
            and are not a clinical prognosis.
          </p>
          <p>
            The primary inference model is a <strong>tuned XGBoost classifier</strong> with a
            scikit-learn ColumnTransformer preprocessor. A secondary Random Forest model is
            also available for comparison.
          </p>
        </Section>

        <Section icon={BookOpen} title="Drug Candidate Rankings" accent="border-teal-300">
          <p>
            The drug candidate component ranks historical drug-review information sourced from the{' '}
            <strong>UCI Drug Reviews (Druglib.com)</strong> public dataset.
          </p>
          <p>
            Candidates are ranked by a composite score derived from average user ratings,
            self-reported effectiveness, and side-effect data.{' '}
            <strong>This ranking does NOT establish:</strong>
          </p>
          <ul className="list-disc pl-4 space-y-1">
            <li>Clinical efficacy or safety</li>
            <li>Drug interactions or contraindications</li>
            <li>Personalized treatment suitability</li>
            <li>FDA approval or regulatory status</li>
          </ul>
          <p className="font-semibold text-amber-700 bg-amber-50 rounded-lg px-3 py-2">
            Drug candidates are labelled as "Historical Research Candidates" — they are NOT prescriptions.
          </p>
        </Section>

        <Section icon={Users} title="Intended Users" accent="border-indigo-300">
          <p>
            This system is intended for use by:
          </p>
          <ul className="list-disc pl-4 space-y-1">
            <li>Healthcare researchers studying ML-based clinical decision support</li>
            <li>Data science students exploring medical AI applications</li>
            <li>Portfolio demonstration of production-style AI systems</li>
          </ul>
          <p>
            It is <strong>not</strong> intended for use by patients, caregivers, or as a clinical
            decision-support tool in any healthcare setting.
          </p>
        </Section>

        <Section icon={AlertTriangle} title="Limitations" accent="border-red-300">
          <ul className="list-disc pl-4 space-y-1">
            <li>Model trained on data from 1999–2008; clinical practices have evolved significantly</li>
            <li>Demographic representation in the training data may not reflect all populations</li>
            <li>Drug review data represents patient self-reports, not clinical trials</li>
            <li>No external clinical validation has been performed</li>
            <li>The system does not account for drug-drug interactions, allergies, or contraindications</li>
          </ul>
        </Section>
      </div>

      {/* Architecture */}
      <div className="card mb-8">
        <h2 className="text-base font-semibold text-slate-800 mb-4">System Architecture</h2>
        <div className="text-sm text-slate-600 space-y-2">
          <div className="flex items-center gap-2 py-1.5">
            <span className="w-28 text-xs font-semibold text-slate-500">Frontend</span>
            <ArrowRight size={13} className="text-slate-300" />
            <span>React + Vite + Tailwind CSS</span>
          </div>
          <div className="flex items-center gap-2 py-1.5 border-t border-slate-50">
            <span className="w-28 text-xs font-semibold text-slate-500">Backend</span>
            <ArrowRight size={13} className="text-slate-300" />
            <span>FastAPI + Uvicorn (Python)</span>
          </div>
          <div className="flex items-center gap-2 py-1.5 border-t border-slate-50">
            <span className="w-28 text-xs font-semibold text-slate-500">Preprocessing</span>
            <ArrowRight size={13} className="text-slate-300" />
            <span>scikit-learn ColumnTransformer (saved preprocessor.pkl)</span>
          </div>
          <div className="flex items-center gap-2 py-1.5 border-t border-slate-50">
            <span className="w-28 text-xs font-semibold text-slate-500">ML Model</span>
            <ArrowRight size={13} className="text-slate-300" />
            <span>Tuned XGBoost Booster (xgboost.json) + Random Forest (random_forest.pkl)</span>
          </div>
          <div className="flex items-center gap-2 py-1.5 border-t border-slate-50">
            <span className="w-28 text-xs font-semibold text-slate-500">Drug Data</span>
            <ArrowRight size={13} className="text-slate-300" />
            <span>Aggregated drug_summary.pkl — historical review data</span>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="text-center">
        <button
          onClick={() => navigate('/assessment')}
          className="btn-primary"
        >
          Start a Research Assessment
          <ArrowRight size={15} />
        </button>
        <p className="text-xs text-slate-400 mt-3">For educational and research purposes only</p>
      </div>
    </div>
  )
}
