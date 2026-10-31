/**
 * Field metadata — maps internal feature names to human-readable labels,
 * provides categorical options derived from the preprocessor, and defines
 * numeric field constraints.
 *
 * These values match the categories encoded by the saved preprocessor.pkl.
 * Do NOT modify without re-checking against the preprocessor's categories_.
 */

// ─── Human-readable labels ────────────────────────────────────────────────────

export const FIELD_LABELS = {
  // Patient Information
  race: 'Race / Ethnicity',
  gender: 'Gender',
  age: 'Age Group',
  weight: 'Weight (lbs)',

  // Admission
  admission_type_id: 'Admission Type',
  admission_source_id: 'Admission Source',
  time_in_hospital: 'Days in Hospital',
  payer_code: 'Payer / Insurance Code',
  medical_specialty: 'Admitting Medical Specialty',

  // Lab
  num_lab_procedures: 'Number of Laboratory Procedures',
  num_procedures: 'Number of Non-Lab Procedures',
  num_medications: 'Number of Distinct Medications',
  max_glu_serum: 'Maximum Glucose Serum Test Result',
  A1Cresult: 'HbA1c Test Result',

  // Clinical counts
  number_outpatient: 'Outpatient Visits (Prior Year)',
  number_emergency: 'Emergency Visits (Prior Year)',
  number_inpatient: 'Inpatient Visits (Prior Year)',
  number_diagnoses: 'Number of Diagnoses',

  // Diagnoses
  diag_1: 'Primary Diagnosis (ICD-9)',
  diag_2: 'Secondary Diagnosis (ICD-9)',
  diag_3: 'Tertiary Diagnosis (ICD-9)',

  // Medications
  metformin: 'Metformin',
  repaglinide: 'Repaglinide',
  nateglinide: 'Nateglinide',
  chlorpropamide: 'Chlorpropamide',
  glimepiride: 'Glimepiride',
  acetohexamide: 'Acetohexamide',
  glipizide: 'Glipizide',
  glyburide: 'Glyburide',
  tolbutamide: 'Tolbutamide',
  pioglitazone: 'Pioglitazone',
  rosiglitazone: 'Rosiglitazone',
  acarbose: 'Acarbose',
  miglitol: 'Miglitol',
  troglitazone: 'Troglitazone',
  tolazamide: 'Tolazamide',
  examide: 'Examide',
  citoglipton: 'Citoglipton',
  insulin: 'Insulin',
  'glyburide-metformin': 'Glyburide-Metformin',
  'glipizide-metformin': 'Glipizide-Metformin',
  'glimepiride-pioglitazone': 'Glimepiride-Pioglitazone',
  'metformin-rosiglitazone': 'Metformin-Rosiglitazone',
  'metformin-pioglitazone': 'Metformin-Pioglitazone',

  // Treatment status
  change: 'Change in Diabetic Medications',
  diabetesMed: 'Diabetes Medication Prescribed',
}

// ─── Categorical options ──────────────────────────────────────────────────────

export const CATEGORICAL_OPTIONS = {
  race: ['AfricanAmerican', 'Asian', 'Caucasian', 'Hispanic', 'Other'],
  gender: ['Female', 'Male', 'Unknown/Invalid'],
  age: ['[0-10)', '[10-20)', '[20-30)', '[30-40)', '[40-50)', '[50-60)', '[60-70)', '[70-80)', '[80-90)', '[90-100)'],
  weight: ['>200', '[0-25)', '[100-125)', '[125-150)', '[150-175)', '[175-200)', '[25-50)', '[50-75)', '[75-100)'],
  max_glu_serum: ['>200', '>300', 'Norm'],
  A1Cresult: ['>7', '>8', 'Norm'],

  // Medication dosage options
  metformin: ['No', 'Steady', 'Up', 'Down'],
  repaglinide: ['No', 'Steady', 'Up', 'Down'],
  nateglinide: ['No', 'Steady', 'Up', 'Down'],
  chlorpropamide: ['No', 'Steady', 'Up', 'Down'],
  glimepiride: ['No', 'Steady', 'Up', 'Down'],
  acetohexamide: ['No'],
  glipizide: ['No', 'Steady', 'Up', 'Down'],
  glyburide: ['No', 'Steady', 'Up', 'Down'],
  tolbutamide: ['No', 'Steady'],
  pioglitazone: ['No', 'Steady', 'Up', 'Down'],
  rosiglitazone: ['No', 'Steady', 'Up', 'Down'],
  acarbose: ['No', 'Steady', 'Up', 'Down'],
  miglitol: ['No', 'Steady', 'Up', 'Down'],
  troglitazone: ['No', 'Steady'],
  tolazamide: ['No', 'Steady', 'Up'],
  examide: ['No'],
  citoglipton: ['No'],
  insulin: ['No', 'Steady', 'Up', 'Down'],
  'glyburide-metformin': ['No', 'Steady', 'Up', 'Down'],
  'glipizide-metformin': ['No', 'Steady'],
  'glimepiride-pioglitazone': ['No', 'Steady'],
  'metformin-rosiglitazone': ['No', 'Steady'],
  'metformin-pioglitazone': ['No'],
  change: ['No', 'Ch'],
  diabetesMed: ['No', 'Yes'],
}

// Payer codes with descriptions
export const PAYER_CODES = [
  { value: 'BC', label: 'BC — Blue Cross' },
  { value: 'CH', label: 'CH — Champus' },
  { value: 'CM', label: 'CM — Medicaid' },
  { value: 'CP', label: 'CP — Managed Care' },
  { value: 'DM', label: 'DM — Managed Care' },
  { value: 'FR', label: 'FR — Self-pay' },
  { value: 'HM', label: 'HM — HMO' },
  { value: 'MC', label: 'MC — Medicare' },
  { value: 'MD', label: 'MD — Medicaid' },
  { value: 'MP', label: 'MP — Medicare Private' },
  { value: 'OG', label: 'OG — Other Government' },
  { value: 'OT', label: 'OT — Other' },
  { value: 'PO', label: 'PO — Self-pay' },
  { value: 'SI', label: 'SI — Self-insurance' },
  { value: 'SP', label: 'SP — Self-pay' },
  { value: 'UN', label: 'UN — Unknown' },
  { value: 'WC', label: 'WC — Worker\'s Comp' },
]

// Medical specialties (subset of most common)
export const MEDICAL_SPECIALTIES = [
  'AllergyandImmunology', 'Anesthesiology', 'Cardiology', 'DCPTEAM',
  'Dentistry', 'Dermatology', 'Emergency/Trauma', 'Endocrinology',
  'Family/GeneralPractice', 'Gastroenterology', 'Gynecology', 'Hematology',
  'Hospitalist', 'InternalMedicine', 'Nephrology', 'Neurology',
  'Obsterics&Gynecology-GynecologicOnco', 'ObstetricsandGynecology',
  'Oncology', 'Ophthalmology', 'Orthopedics', 'Orthopedics-Reconstructive',
  'Otolaryngology', 'Pathology', 'Pediatrics', 'Pediatrics-AllergyandImmunology',
  'Perinatology', 'PhysicalMedicineandRehabilitation', 'PhysiatryandRehabitation',
  'Podiatry', 'Proctology', 'Psychiatry', 'Psychology', 'Pulmonology',
  'Radiology', 'Rheumatology', 'SportsMedicine', 'Surgery-Cardiovascular',
  'Surgery-Cardiovascular/Thoracic', 'Surgery-Colon&Rectal', 'Surgery-General',
  'Surgery-Maxillofacial', 'Surgery-Neuro', 'Surgery-Orthopedic',
  'Surgery-Pediatric', 'Surgery-Plastic', 'Surgery-PlasticwithinHead&Neck',
  'Surgery-Thoracic', 'Surgery-Vascular', 'SurgicalSpecialty', 'Urology',
]

// Admission type descriptions
export const ADMISSION_TYPES = [
  { value: 1, label: '1 — Emergency' },
  { value: 2, label: '2 — Urgent' },
  { value: 3, label: '3 — Elective' },
  { value: 4, label: '4 — Newborn' },
  { value: 5, label: '5 — Not Available' },
  { value: 6, label: '6 — NULL' },
  { value: 7, label: '7 — Trauma Center' },
  { value: 8, label: '8 — Not Mapped' },
]

// Admission source descriptions
export const ADMISSION_SOURCES = [
  { value: 1, label: '1 — Physician Referral' },
  { value: 2, label: '2 — Clinic Referral' },
  { value: 3, label: '3 — HMO Referral' },
  { value: 4, label: '4 — Transfer from Hospital' },
  { value: 5, label: '5 — Transfer from SNF' },
  { value: 6, label: '6 — Transfer from Other' },
  { value: 7, label: '7 — Emergency Room' },
  { value: 8, label: '8 — Court/Law Enforcement' },
  { value: 9, label: '9 — Not Available' },
  { value: 11, label: '11 — Normal Delivery' },
  { value: 12, label: '12 — Premature Delivery' },
  { value: 13, label: '13 — Sick Baby' },
  { value: 14, label: '14 — Extramural Birth' },
  { value: 17, label: '17 — NULL' },
  { value: 20, label: '20 — Transfer from ASC' },
  { value: 21, label: '21 — Readmission to Facility' },
  { value: 22, label: '22 — Transfer within Facility' },
  { value: 23, label: '23 — Born inside this hospital' },
  { value: 24, label: '24 — Born outside this hospital' },
  { value: 25, label: '25 — Transfer from Ambulatory Surgery' },
]

// ─── Numeric field constraints ────────────────────────────────────────────────

export const NUMERIC_CONSTRAINTS = {
  time_in_hospital: { min: 1, max: 14, step: 1, placeholder: '1–14' },
  num_lab_procedures: { min: 0, max: 132, step: 1, placeholder: '0–132' },
  num_procedures: { min: 0, max: 6, step: 1, placeholder: '0–6' },
  num_medications: { min: 0, max: 81, step: 1, placeholder: '0–81' },
  number_outpatient: { min: 0, max: 42, step: 1, placeholder: '0–42' },
  number_emergency: { min: 0, max: 76, step: 1, placeholder: '0–76' },
  number_inpatient: { min: 0, max: 21, step: 1, placeholder: '0–21' },
  number_diagnoses: { min: 1, max: 16, step: 1, placeholder: '1–16' },
}

// ─── Default form values ──────────────────────────────────────────────────────

export const DEFAULT_PATIENT_VALUES = {
  race: 'Caucasian',
  gender: 'Male',
  age: '[50-60)',
  weight: '[75-100)',
  admission_type_id: 1,
  admission_source_id: 7,
  time_in_hospital: 3,
  payer_code: 'MC',
  medical_specialty: 'InternalMedicine',
  num_lab_procedures: 40,
  num_procedures: 1,
  num_medications: 12,
  number_outpatient: 0,
  number_emergency: 0,
  number_inpatient: 0,
  diag_1: '',
  diag_2: '',
  diag_3: '',
  number_diagnoses: 1,
  max_glu_serum: 'None',
  A1Cresult: 'None',
  metformin: 'No',
  repaglinide: 'No',
  nateglinide: 'No',
  chlorpropamide: 'No',
  glimepiride: 'No',
  acetohexamide: 'No',
  glipizide: 'No',
  glyburide: 'No',
  tolbutamide: 'No',
  pioglitazone: 'No',
  rosiglitazone: 'No',
  acarbose: 'No',
  miglitol: 'No',
  troglitazone: 'No',
  tolazamide: 'No',
  examide: 'No',
  citoglipton: 'No',
  insulin: 'No',
  'glyburide-metformin': 'No',
  'glipizide-metformin': 'No',
  'glimepiride-pioglitazone': 'No',
  'metformin-rosiglitazone': 'No',
  'metformin-pioglitazone': 'No',
  change: 'No',
  diabetesMed: 'No',
}
