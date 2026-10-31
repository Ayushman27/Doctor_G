import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronRight, Loader2, AlertCircle, Info, Sparkles, Wand2, Stethoscope, Activity, Check, X, Search, BrainCircuit } from 'lucide-react'
import { getConditions, analyzePatient, getSymptoms, predictDisease } from '../services/api'
import {
  FIELD_LABELS, CATEGORICAL_OPTIONS, NUMERIC_CONSTRAINTS, DEFAULT_PATIENT_VALUES,
  PAYER_CODES, MEDICAL_SPECIALTIES, ADMISSION_TYPES, ADMISSION_SOURCES
} from '../utils/fieldMeta'
import DisclaimerBanner from '../components/DisclaimerBanner'

// ─── Field components ──────────────────────────────────────────────────────────

function SelectField({ name, label, options, value, onChange, error, required, hint }) {
  return (
    <div>
      <label htmlFor={name} className="form-label">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {hint && <p className="text-xs text-slate-400 mb-1">{hint}</p>}
      <select
        id={name}
        name={name}
        value={value ?? ''}
        onChange={e => onChange(name, e.target.value || null)}
        className={`form-select ${error ? 'border-red-400 focus:ring-red-100' : ''}`}
      >
        <option value="">— Select —</option>
        {options.map(opt => {
          const val = typeof opt === 'object' ? opt.value : opt
          const lbl = typeof opt === 'object' ? opt.label : opt
          return <option key={val} value={val}>{lbl}</option>
        })}
      </select>
      {error && <p className="form-error"><AlertCircle size={11} />{error}</p>}
    </div>
  )
}

function NumberField({ name, label, value, onChange, error, required, hint, min, max, step, placeholder }) {
  return (
    <div>
      <label htmlFor={name} className="form-label">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {hint && <p className="text-xs text-slate-400 mb-1">{hint}</p>}
      <input
        id={name}
        type="number"
        name={name}
        value={value ?? ''}
        min={min}
        max={max}
        step={step || 1}
        placeholder={placeholder}
        onChange={e => onChange(name, e.target.value === '' ? null : Number(e.target.value))}
        className={`form-input ${error ? 'border-red-400 focus:ring-red-100' : ''}`}
      />
      {error && <p className="form-error"><AlertCircle size={11} />{error}</p>}
    </div>
  )
}

function TextSearchField({ name, label, value, onChange, options, error, required, hint }) {
  const [query, setQuery] = useState(value || '')
  const [open, setOpen] = useState(false)

  useEffect(() => {
    setQuery(value || '')
  }, [value])

  const filtered = options.filter(o =>
    o.toLowerCase().includes(query.toLowerCase())
  ).slice(0, 30)

  const select = (opt) => {
    onChange(name, opt)
    setQuery(opt)
    setOpen(false)
  }

  return (
    <div className="relative">
      <label htmlFor={name} className="form-label">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {hint && <p className="text-xs text-slate-400 mb-1">{hint}</p>}
      <input
        id={name}
        type="text"
        value={query}
        autoComplete="off"
        placeholder={`Search or type ${label.toLowerCase()}...`}
        onChange={e => { setQuery(e.target.value); setOpen(true); onChange(name, e.target.value || null) }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        className={`form-input ${error ? 'border-red-400 focus:ring-red-100' : ''}`}
      />
      {open && filtered.length > 0 && (
        <div className="absolute z-20 w-full mt-1 bg-white border border-slate-200 rounded-xl shadow-lg max-h-52 overflow-y-auto">
          {filtered.map(opt => (
            <button
              key={opt}
              type="button"
              onMouseDown={() => select(opt)}
              className="w-full text-left px-3 py-2 text-sm text-slate-700 hover:bg-primary-50 hover:text-primary-700 transition-colors"
            >
              {opt}
            </button>
          ))}
        </div>
      )}
      {error && <p className="form-error"><AlertCircle size={11} />{error}</p>}
    </div>
  )
}

// ─── Section Wrapper ───────────────────────────────────────────────────────────

function Section({ title, subtitle, children }) {
  return (
    <div className="card mb-4">
      <div className="mb-5">
        <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {children}
      </div>
    </div>
  )
}

// ─── Medication row helper ─────────────────────────────────────────────────────

function MedField({ name, value, onChange, options }) {
  const label = FIELD_LABELS[name] || name
  return (
    <div>
      <label className="form-label text-xs">{label}</label>
      <select
        value={value ?? 'No'}
        onChange={e => onChange(name, e.target.value)}
        className="form-select text-xs py-2"
      >
        {options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  )
}

// ─── ICD code sets for diag fields ────────────────────────────────────────────

const DISEASE_ICD9_MAP = {
  'GERD': '530.81',
  'Gastroenteritis': '558.9',
  'Paralysis (Brain Hemorrhage)': '431',
  'Heart Attack': '410.90',
  'Hepatitis D': '070.52',
  'Hepatitis A': '070.1',
  'Hepatitis B': '070.30',
  'Hepatitis C': '070.51',
  'Hepatitis E': '070.53',
  'Bronchial Asthma': '493.90',
  'Pneumonia': '486',
  'Common Cold': '460',
  'Tuberculosis': '011.90',
  'Typhoid': '002.0',
  'Diabetes': '250.00',
  'Hypertension': '401.9',
  'Hyperthyroidism': '242.90',
  'Hypothyroidism': '244.9',
  'Hypoglycemia': '251.2',
  'Fungal Infection': '110.9',
  'Allergy': '995.3',
  'Acne': '706.1',
  'AIDS': '042',
  'Alcoholic Hepatitis': '571.1',
  'Arthritis': '716.90',
  'Cervical Spondylosis': '721.0',
  'Chicken Pox': '052.9',
  'Chronic Cholestasis': '576.2',
  'Dengue': '065.4',
  'Dimorphic Hemmorhoids(Piles)': '455.6',
  'Drug Reaction': '995.20',
  'Impetigo': '684',
  'Jaundice': '782.4',
  'Malaria': '084.6',
  'Migraine': '346.90',
  'Osteoarthristis': '715.90',
  'Peptic Ulcer Diseae': '533.90',
  'Psoriasis': '696.1',
  'Urinary Tract Infection': '599.0',
  'Varicose Veins': '454.9',
  '(Vertigo) Paroymsal Positional Vertigo': '386.11'
}

function getIcd9ForPrediction(p) {
  if (!p) return ''
  if (p.icd9_code) return p.icd9_code
  if (p.disease && DISEASE_ICD9_MAP[p.disease]) return DISEASE_ICD9_MAP[p.disease]
  return '799.9'
}

const COMMON_DIAG_CODES = [
  '250.00', '250.01', '250.02', '250.03', '250.10', '250.40', '250.60',
  '272.4', '401.9', '402.01', '410.01', '410.90', '414.01', '427.31', '428.0',
  '431', '460', '486', '491.21', '493.90', '496', '518.81', '530.81', '558.9', '585.6', '599.0',
  '706.1', '714.0', '715.90', '716.90', '724.2', '780.39', '786.05', '787.01',
  '042', '065.4', '070.52', '110.9', '346.90', '386.11', 'V45.81', 'E11.9'
]

// ─── Preset Symptoms ───────────────────────────────────────────────────────────

const PRESET_SYMPTOMS = [
  { name: 'Diabetes Symptoms', symptoms: ['fatigue', 'weight_loss', 'restlessness', 'irregular_sugar_level'] },
  { name: 'Heart Attack Symptoms', symptoms: ['chest_pain', 'breathlessness', 'sweating', 'vomiting'] },
  { name: 'Fungal Infection', symptoms: ['itching', 'skin_rash', 'nodal_skin_eruptions'] },
  { name: 'Hypertension Symptoms', symptoms: ['headache', 'dizziness', 'chest_pain', 'fatigue'] },
  { name: 'Bronchial Asthma', symptoms: ['cough', 'high_fever', 'breathlessness', 'chest_pain'] }
]

// ─── Main Component ────────────────────────────────────────────────────────────

export default function PatientAssessment() {
  const navigate = useNavigate()
  const [conditions, setConditions] = useState([])
  const [values, setValues] = useState({ ...DEFAULT_PATIENT_VALUES })
  const [condition, setCondition] = useState('')
  const [autoDetected, setAutoDetected] = useState(false)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [apiError, setApiError] = useState(null)

  // Symptom Classifier State (disease_prediction_model.zip)
  const [allSymptoms, setAllSymptoms] = useState([])
  const [selectedSymptoms, setSelectedSymptoms] = useState([])
  const [symptomSearch, setSymptomSearch] = useState('')
  const [diseasePredictions, setDiseasePredictions] = useState(null)
  const [predictingDisease, setPredictingDisease] = useState(false)
  const [detectedSource, setDetectedSource] = useState('symptoms')

  useEffect(() => {
    getConditions().then(d => setConditions(d.conditions)).catch(() => {})
    getSymptoms().then(d => setAllSymptoms(d.symptoms)).catch(() => {})
  }, [])

  const set = (name, val) => {
    setValues(prev => ({ ...prev, [name]: val }))
    setErrors(prev => ({ ...prev, [name]: undefined }))
  }

  // Symptom selector helpers
  const toggleSymptom = (symValue) => {
    if (selectedSymptoms.includes(symValue)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== symValue))
    } else {
      setSelectedSymptoms([...selectedSymptoms, symValue])
    }
  }

  const autoFillIcd9FromPrediction = (diseaseName) => {
    if (!diseaseName) return
    const code = DISEASE_ICD9_MAP[diseaseName] || '799.9'
    setValues(prev => ({
      ...prev,
      diag_1: code,
    }))
    setErrors(prev => ({ ...prev, diag_1: undefined }))
  }

  const selectConditionFromPrediction = (diseaseName) => {
    setCondition(diseaseName)
    setAutoDetected(true)
    setDetectedSource('symptoms')
    setErrors(prev => ({ ...prev, condition: undefined }))
    autoFillIcd9FromPrediction(diseaseName)
  }

  const applyPresetSymptoms = async (preset) => {
    setSelectedSymptoms(preset.symptoms)
    setPredictingDisease(true)
    try {
      const res = await predictDisease(preset.symptoms, 5)
      setDiseasePredictions(res)
      if (res?.top_prediction?.disease) {
        selectConditionFromPrediction(res.top_prediction.disease)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setPredictingDisease(false)
    }
  }

  const handlePredictDiseaseModel = async () => {
    if (selectedSymptoms.length === 0) return
    setPredictingDisease(true)
    try {
      const res = await predictDisease(selectedSymptoms, 5)
      setDiseasePredictions(res)
      if (res?.top_prediction?.disease) {
        selectConditionFromPrediction(res.top_prediction.disease)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setPredictingDisease(false)
    }
  }

  // Predict medical condition based on entered test data & ICD-9 codes
  const predictConditionFromTestData = () => {
    const diag1 = String(values.diag_1 || '')
    const diag2 = String(values.diag_2 || '')
    const diag3 = String(values.diag_3 || '')
    const allDiags = `${diag1} ${diag2} ${diag3}`
    const a1c = values.A1Cresult
    const glu = values.max_glu_serum

    if (allDiags.includes('250') || a1c === '>8' || a1c === '>7' || glu === '>300' || glu === '>200' || values.insulin !== 'No' || values.metformin !== 'No') {
      return 'Diabetes'
    } else if (allDiags.includes('401') || allDiags.includes('402')) {
      return 'Hypertension'
    } else if (allDiags.includes('410') || allDiags.includes('414') || allDiags.includes('428')) {
      return 'Heart Failure'
    } else if (allDiags.includes('486') || allDiags.includes('491') || allDiags.includes('496')) {
      return 'Asthma'
    } else if (allDiags.includes('585')) {
      return 'Kidney Disease'
    }
    return ''
  }

  const handleAutoPredictCondition = () => {
    const predicted = predictConditionFromTestData()
    if (predicted) {
      setCondition(predicted)
      setAutoDetected(true)
      setDetectedSource('lab_data')
      setErrors(prev => ({ ...prev, condition: undefined }))
    } else if (diseasePredictions?.top_prediction?.disease) {
      selectConditionFromPrediction(diseasePredictions.top_prediction.disease)
    } else {
      setErrors(prev => ({ ...prev, condition: 'Select symptoms or enter lab test data to predict.' }))
    }
  }

  const validate = () => {
    const e = {}
    if (!values.gender) e.gender = 'Required'
    if (!values.age) e.age = 'Required'
    if (!values.admission_type_id) e.admission_type_id = 'Required'
    if (!values.time_in_hospital) e.time_in_hospital = 'Required'
    if (!values.num_lab_procedures && values.num_lab_procedures !== 0) e.num_lab_procedures = 'Required'
    
    if (!condition) {
      const autoCond = diseasePredictions?.top_prediction?.disease || predictConditionFromTestData() || 'Diabetes'
      setCondition(autoCond)
    }

    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    setApiError(null)

    try {
      const conditionToSend = condition || diseasePredictions?.top_prediction?.disease || predictConditionFromTestData() || 'Diabetes'

      const patientData = {}
      const hyphenMap = {
        glyburide_metformin: 'glyburide-metformin',
        glipizide_metformin: 'glipizide-metformin',
        glimepiride_pioglitazone: 'glimepiride-pioglitazone',
        metformin_rosiglitazone: 'metformin-rosiglitazone',
        metformin_pioglitazone: 'metformin-pioglitazone',
      }

      for (const [k, v] of Object.entries(values)) {
        const outKey = hyphenMap[k] || k
        patientData[outKey] = v
      }

      const result = await analyzePatient(patientData, conditionToSend, 10)
      sessionStorage.setItem('analysisResult', JSON.stringify(result))
      navigate('/results')
    } catch (err) {
      setApiError(err.message || 'Analysis failed. Please check your inputs.')
    } finally {
      setSubmitting(false)
    }
  }

  const MedOptions = (name) => CATEGORICAL_OPTIONS[name] || ['No', 'Steady', 'Up', 'Down']

  const filteredSymptoms = allSymptoms.filter(s =>
    s.label.toLowerCase().includes(symptomSearch.toLowerCase()) ||
    s.value.toLowerCase().includes(symptomSearch.toLowerCase())
  )

  return (
    <div className="p-6 lg:p-8 max-w-4xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Patient Assessment & AI Diagnosis</h1>
        <p className="text-sm text-slate-500 mt-1">
          Select symptoms to run the Scikit-Learn Disease Classifier or complete clinical data for XGBoost risk stratification.
        </p>
      </div>

      <DisclaimerBanner />
      <div className="mt-6" />

      {/* 🧪 AI Symptom-to-Disease Predictor Widget (disease_prediction_model.zip) */}
      <div className="card mb-6 bg-gradient-to-br from-white via-teal-50/20 to-primary-50/30 border-2 border-teal-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <BrainCircuit size={20} className="text-teal-600" />
              <h2 className="text-base font-bold text-slate-800">
                Symptom-to-Disease AI Classifier
              </h2>
              <span className="text-[10px] font-bold bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full border border-teal-300">
                100% Accuracy ML Model
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Select symptoms to predict 41 distinct diseases using trained Logistic Regression
            </p>
          </div>
          <button
            type="button"
            onClick={handlePredictDiseaseModel}
            disabled={selectedSymptoms.length === 0 || predictingDisease}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-teal-600 text-white font-semibold text-xs rounded-xl shadow-sm hover:bg-teal-700 disabled:opacity-50 transition-all cursor-pointer"
          >
            {predictingDisease ? (
              <><Loader2 size={14} className="animate-spin" /> Predicting...</>
            ) : (
              <><Sparkles size={14} /> Predict Disease from Symptoms ({selectedSymptoms.length})</>
            )}
          </button>
        </div>

        {/* Preset quick buttons */}
        <div>
          <span className="text-xs font-semibold text-slate-500 block mb-2">Quick Symptom Presets:</span>
          <div className="flex flex-wrap gap-2">
            {PRESET_SYMPTOMS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => applyPresetSymptoms(preset)}
                className="text-xs bg-white hover:bg-teal-50 text-slate-700 hover:text-teal-800 border border-slate-200 hover:border-teal-300 rounded-lg px-2.5 py-1.5 font-medium transition-colors"
              >
                ⚡ {preset.name}
              </button>
            ))}
          </div>
        </div>

        {/* Symptom Search & Selector */}
        <div>
          <div className="relative mb-2">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={symptomSearch}
              onChange={e => setSymptomSearch(e.target.value)}
              placeholder="Search 133 supported symptoms (e.g. fatigue, chest pain, itching, fever)..."
              className="form-input pl-9 py-2 text-xs"
            />
          </div>

          {/* Selected symptoms tags */}
          {selectedSymptoms.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-3 p-2 bg-slate-50 rounded-lg border border-slate-100">
              {selectedSymptoms.map(sym => (
                <span key={sym} className="inline-flex items-center gap-1 text-xs font-semibold bg-teal-100 text-teal-800 px-2.5 py-1 rounded-full">
                  {allSymptoms.find(s => s.value === sym)?.label || sym.replace(/_/g, ' ')}
                  <button type="button" onClick={() => toggleSymptom(sym)} className="hover:text-teal-950">
                    <X size={12} />
                  </button>
                </span>
              ))}
              <button
                type="button"
                onClick={() => setSelectedSymptoms([])}
                className="text-[11px] text-slate-400 hover:text-red-500 ml-auto self-center underline"
              >
                Clear all
              </button>
            </div>
          )}

          {/* Symptom chips options */}
          <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto p-1">
            {filteredSymptoms.slice(0, 24).map(s => {
              const active = selectedSymptoms.includes(s.value)
              return (
                <button
                  key={s.value}
                  type="button"
                  onClick={() => toggleSymptom(s.value)}
                  className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
                    active
                      ? 'bg-teal-600 text-white border-teal-600 font-semibold shadow-xs'
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {s.label}
                </button>
              )
            })}
          </div>
        </div>

        {/* Prediction Results Banner */}
        {diseasePredictions && (
          <div className="bg-white border-2 border-teal-300 rounded-xl p-4 shadow-sm animate-fade-in space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-teal-600 bg-teal-50 px-2 py-0.5 rounded-full border border-teal-200">
                  Primary Model Prediction
                </span>
                <h3 className="text-lg font-bold text-slate-800 mt-1">
                  {diseasePredictions.top_prediction.disease}
                </h3>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="text-xs text-slate-400 font-medium block">Confidence</span>
                  <span className="text-base font-extrabold text-teal-700">
                    {diseasePredictions.top_prediction.percentage}%
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => selectConditionFromPrediction(diseasePredictions.top_prediction.disease)}
                  className="px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white font-semibold text-xs rounded-lg shadow-xs transition-colors cursor-pointer"
                >
                  {condition === diseasePredictions.top_prediction.disease ? '✓ Selected' : `Use ${diseasePredictions.top_prediction.disease}`}
                </button>
              </div>
            </div>

            {/* Top 5 breakdown */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-500 block">Top Predicted Candidates (Click to select):</span>
              {diseasePredictions.predictions.map((p, i) => (
                <div
                  key={i}
                  onClick={() => selectConditionFromPrediction(p.disease)}
                  className={`flex items-center justify-between text-xs py-1.5 px-2 rounded-lg cursor-pointer transition-colors border ${
                    condition === p.disease ? 'bg-teal-100/70 border-teal-300 font-semibold' : 'border-transparent hover:bg-slate-50'
                  }`}
                >
                  <span className="font-medium text-slate-700 flex items-center gap-1.5">
                    <span className="w-4 text-center font-bold text-slate-400">{i + 1}.</span>
                    {p.disease}
                    {condition === p.disease && (
                      <span className="text-[10px] bg-teal-600 text-white font-bold px-1.5 py-0.5 rounded">Selected</span>
                    )}
                  </span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-teal-500 h-full rounded-full" style={{ width: `${p.percentage}%` }} />
                    </div>
                    <span className="w-10 text-right font-bold text-slate-600">{p.percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} noValidate>
        {/* 1. Patient Information */}
        <Section title="Patient Information" subtitle="Demographic data">
          <SelectField name="race" label="Race / Ethnicity"
            options={CATEGORICAL_OPTIONS.race} value={values.race} onChange={set} />
          <SelectField name="gender" label="Gender" required
            options={CATEGORICAL_OPTIONS.gender} value={values.gender} onChange={set} error={errors.gender} />
          <SelectField name="age" label="Age Group" required
            options={CATEGORICAL_OPTIONS.age} value={values.age} onChange={set} error={errors.age} />
          <SelectField name="weight" label="Weight Band (lbs)"
            options={CATEGORICAL_OPTIONS.weight} value={values.weight} onChange={set}
            hint="Select the patient's weight range in pounds" />
        </Section>

        {/* 2. Admission Information */}
        <Section title="Admission Information" subtitle="Hospitalization details">
          <SelectField name="admission_type_id" label="Admission Type" required
            options={ADMISSION_TYPES} value={values.admission_type_id} onChange={set} error={errors.admission_type_id} />
          <SelectField name="admission_source_id" label="Admission Source"
            options={ADMISSION_SOURCES} value={values.admission_source_id} onChange={set} />
          <NumberField name="time_in_hospital" label="Days in Hospital" required
            {...NUMERIC_CONSTRAINTS.time_in_hospital}
            value={values.time_in_hospital} onChange={set} error={errors.time_in_hospital} />
          <TextSearchField name="payer_code" label="Payer / Insurance Code"
            options={PAYER_CODES.map(p => p.value)} value={values.payer_code} onChange={set} />
          <div className="md:col-span-2">
            <TextSearchField name="medical_specialty" label="Admitting Medical Specialty"
              options={MEDICAL_SPECIALTIES} value={values.medical_specialty} onChange={set}
              hint="Search for the admitting physician's specialty" />
          </div>
        </Section>

        {/* 3. Diagnosis */}
        <Section title="Diagnosis (ICD-9 Code)" subtitle="Auto-filled based on predicted disease">
          <div className="md:col-span-2">
            <TextSearchField name="diag_1" label="Diagnosis (ICD-9 Code)" required
              options={COMMON_DIAG_CODES} value={values.diag_1} onChange={set}
              hint="Auto-filled on the basis of predicted disease (e.g. 530.81 for GERD)" error={errors.diag_1} />
          </div>
        </Section>

        {/* 4. Laboratory Information */}
        <Section title="Laboratory Information" subtitle="Lab results and test counts">
          <NumberField name="num_lab_procedures" label="Number of Laboratory Procedures" required
            {...NUMERIC_CONSTRAINTS.num_lab_procedures}
            value={values.num_lab_procedures} onChange={set} error={errors.num_lab_procedures} />
          <NumberField name="num_procedures" label="Number of Non-Lab Procedures"
            {...NUMERIC_CONSTRAINTS.num_procedures}
            value={values.num_procedures} onChange={set} />
          <NumberField name="num_medications" label="Number of Distinct Medications"
            {...NUMERIC_CONSTRAINTS.num_medications}
            value={values.num_medications} onChange={set} />
          <SelectField name="max_glu_serum" label="Max Glucose Serum Result"
            options={[...CATEGORICAL_OPTIONS.max_glu_serum, { value: 'None', label: 'None / Not tested' }]}
            value={values.max_glu_serum} onChange={set} />
          <SelectField name="A1Cresult" label="HbA1c Test Result"
            options={[...CATEGORICAL_OPTIONS.A1Cresult, { value: 'None', label: 'None / Not tested' }]}
            value={values.A1Cresult} onChange={set} />
        </Section>

        {/* 5. Visit History */}
        <Section title="Clinical Visit History" subtitle="Prior year hospitalization counts">
          <NumberField name="number_outpatient" label="Outpatient Visits (Prior Year)"
            {...NUMERIC_CONSTRAINTS.number_outpatient}
            value={values.number_outpatient} onChange={set} />
          <NumberField name="number_emergency" label="Emergency Visits (Prior Year)"
            {...NUMERIC_CONSTRAINTS.number_emergency}
            value={values.number_emergency} onChange={set} />
          <NumberField name="number_inpatient" label="Inpatient Visits (Prior Year)"
            {...NUMERIC_CONSTRAINTS.number_inpatient}
            value={values.number_inpatient} onChange={set} />
        </Section>

        {/* 6. Medication Information */}
        <div className="card mb-4">
          <div className="mb-5">
            <h3 className="text-sm font-semibold text-slate-800">Medication Information</h3>
            <p className="text-xs text-slate-400 mt-0.5">Dosage change status for each diabetes medication</p>
            <div className="flex items-start gap-2 mt-2 text-xs text-slate-500 bg-slate-50 rounded-lg px-3 py-2">
              <Info size={12} className="mt-0.5 flex-shrink-0" />
              Options: No = not prescribed, Steady = unchanged, Up = increased, Down = decreased
            </div>
          </div>

          {/* Primary meds */}
          <div className="mb-4">
            <p className="text-xs font-medium text-slate-500 mb-3">Primary Medications</p>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {['metformin','glimepiride','glipizide','glyburide','insulin','pioglitazone','rosiglitazone','repaglinide'].map(med => (
                <MedField key={med} name={med} value={values[med]} onChange={set} options={MedOptions(med)} />
              ))}
            </div>
          </div>

          {/* Secondary meds */}
          <div className="mb-4">
            <p className="text-xs font-medium text-slate-500 mb-3">Secondary Medications</p>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {['nateglinide','chlorpropamide','acarbose','miglitol','tolbutamide','tolazamide',
                'troglitazone','acetohexamide','examide','citoglipton'].map(med => (
                <MedField key={med} name={med} value={values[med]} onChange={set} options={MedOptions(med)} />
              ))}
            </div>
          </div>

          {/* Combination meds */}
          <div>
            <p className="text-xs font-medium text-slate-500 mb-3">Combination Medications</p>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {[
                ['glyburide-metformin', 'glyburide_metformin'],
                ['glipizide-metformin', 'glipizide_metformin'],
                ['glimepiride-pioglitazone', 'glimepiride_pioglitazone'],
                ['metformin-rosiglitazone', 'metformin_rosiglitazone'],
                ['metformin-pioglitazone', 'metformin_pioglitazone'],
              ].map(([displayName, stateKey]) => (
                <MedField key={stateKey} name={stateKey} value={values[stateKey]} onChange={set}
                  options={MedOptions(displayName)} />
              ))}
            </div>
          </div>
        </div>

        {/* 7. Treatment Status */}
        <Section title="Treatment Status" subtitle="Current diabetes medication status">
          <SelectField name="change" label="Change in Diabetic Medications"
            options={[{ value: 'No', label: 'No change' }, { value: 'Ch', label: 'Change made' }]}
            value={values.change} onChange={set}
            hint="Was a change made to diabetes medications during this visit?" />
          <SelectField name="diabetesMed" label="Diabetes Medication Prescribed"
            options={CATEGORICAL_OPTIONS.diabetesMed}
            value={values.diabetesMed} onChange={set}
            hint="Were any diabetes medications prescribed during this visit?" />
        </Section>

        {/* 8. Condition Prediction & Selection */}
        <div className="card mb-6 bg-gradient-to-br from-white to-primary-50/20 border-2 border-primary-100 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
                <Stethoscope size={18} className="text-primary-600" />
                Medical Condition & Diagnosis
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Auto-predict condition from test data or search/select manually
              </p>
            </div>
            <button
              type="button"
              onClick={handleAutoPredictCondition}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-primary-600 to-teal-600 text-white font-semibold text-xs rounded-xl shadow-sm hover:from-primary-700 hover:to-teal-700 transition-all duration-200 cursor-pointer"
            >
              <Wand2 size={14} />
              ✨ Auto-Predict Condition
            </button>
          </div>

          <TextSearchField name="condition" label="Medical Condition"
            options={conditions} value={condition}
            onChange={(_, val) => { setCondition(val || ''); setAutoDetected(false); setErrors(e => ({ ...e, condition: undefined })) }}
            hint="Click button above to auto-predict or search condition manually"
            error={errors.condition} />

          {autoDetected && condition && (
            <div className="mt-3 bg-emerald-50 border border-emerald-200 rounded-lg px-3.5 py-2.5 text-xs text-emerald-800 flex items-center gap-2 animate-fade-in">
              <Sparkles size={15} className="text-emerald-600 flex-shrink-0" />
              <span>
                ✨ Medical condition set as <strong>{condition}</strong>{' '}
                {detectedSource === 'symptoms'
                  ? '(predicted using Symptom-to-Disease AI Classifier)'
                  : '(auto-predicted from ICD-9 codes & lab test data)'}
              </span>
            </div>
          )}
        </div>

        {/* API error */}
        {apiError && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-700 flex items-start gap-2">
            <AlertCircle size={15} className="mt-0.5 flex-shrink-0" />
            <span>{apiError}</span>
          </div>
        )}

        {/* Submit Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-400">
            <span className="text-red-500">*</span> Required fields
          </p>
          <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => {
                handleAutoPredictCondition()
                const btn = document.getElementById('analyze-patient-btn')
                if (btn) btn.click()
              }}
              disabled={submitting}
              className="btn-secondary text-sm px-5 py-3 border-primary-200 text-primary-700 bg-primary-50/50 hover:bg-primary-100 flex-1 sm:flex-none justify-center"
            >
              <Wand2 size={15} className="text-primary-600" />
              Auto-Predict & Analyze
            </button>
            <button
              id="analyze-patient-btn"
              type="submit"
              disabled={submitting}
              className="btn-primary text-base px-8 py-3 flex-1 sm:flex-none justify-center"
            >
              {submitting ? (
                <><Loader2 size={16} className="animate-spin" /> Analyzing Patient...</>
              ) : (
                <><ChevronRight size={16} /> Predict Condition & Analyze</>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
