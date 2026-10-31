"""
Local Clinical Rules Engine - Maps conditions, lab test results, and ICD-9 diagnosis codes
to disease descriptions, symptom causes, test insights, dietary plans (recommended vs avoid),
and actionable guidelines (what to do vs what NOT to do).
"""

from typing import Dict, List, Any

# Extensive Knowledge Base mapped by Medical Category
CLINICAL_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "diabetes": {
        "disease_name": "Diabetes Mellitus & Metabolic Risk",
        "causes": [
            "Pancreatic beta-cell dysfunction or peripheral insulin resistance.",
            "Chronic hyper-glycemia causing microvascular and macrovascular strain.",
            "Metabolic dysregulation compounded by sedentary habits, age, or elevated BMI."
        ],
        "diet_plan": {
            "recommended": [
                "High-fiber complex carbohydrates (oats, quinoa, brown rice, legumes).",
                "Non-starchy green leafy vegetables (spinach, kale, broccoli, cucumbers).",
                "Lean proteins (grilled chicken, fish rich in Omega-3, tofu, egg whites).",
                "Healthy monounsaturated fats (avocados, extra virgin olive oil, almonds)."
            ],
            "avoid": [
                "Refined sugars, sugary soft drinks, energy drinks, and fruit juices.",
                "High glycemic index simple carbs (white bread, pastries, white rice).",
                "Trans fats, deep-fried snacks, and heavy processed meats.",
                "Excessive sodium and high-fructose corn syrup products."
            ]
        },
        "what_to_do": [
            "Monitor blood glucose levels 2-4 times daily as prescribed by your physician.",
            "Take prescribed anti-diabetic medications or insulin on a strict schedule.",
            "Engage in at least 30 minutes of daily moderate aerobic exercise (brisk walking, cycling).",
            "Perform daily foot checks for cuts, blisters, or skin changes.",
            "Maintain optimal hydration by drinking 2.5 to 3 liters of water daily."
        ],
        "what_not_to_do": [
            "Do NOT skip prescribed doses of insulin or oral hypoglycemic medications.",
            "Do NOT go barefoot indoors or outdoors to prevent unnoticed foot injuries.",
            "Do NOT consume large high-carbohydrate meals in a single sitting.",
            "Do NOT ignore symptoms of hypoglycemia (shakiness, dizziness, cold sweating).",
            "Do NOT smoke or use tobacco products as it severely worsens vascular complications."
        ],
        "lifestyle_advice": [
            "Maintain regular sleep hygiene (7-8 hours per night) to optimize cortisol and insulin sensitivity.",
            "Schedule annual comprehensive eye exams and diabetic kidney screenings.",
            "Keep emergency fast-acting glucose tablets or juice available at all times."
        ]
    },

    "hypertension": {
        "disease_name": "Essential / Secondary Hypertension & Vascular Strain",
        "causes": [
            "Increased peripheral vascular resistance and arterial wall stiffness.",
            "Excess renal sodium retention causing elevated circulating blood volume.",
            "Sympathetic nervous system hyper-reactivity, chronic stress, or vascular disease."
        ],
        "diet_plan": {
            "recommended": [
                "DASH Diet foods (Dietary Approaches to Stop Hypertension).",
                "Potassium-rich foods (bananas, sweet potatoes, spinach, pomegranates).",
                "Magnesium and calcium sources (un-salted seeds, almonds, low-fat Greek yogurt).",
                "Garlic, beetroot, and berries rich in natural nitric oxide precursors."
            ],
            "avoid": [
                "High-sodium foods (>2,000 mg/day limit), packaged soups, pickles, and soy sauce.",
                "Cured, smoked, or processed meats (bacon, sausages, deli slices).",
                "Excessive caffeine, energy drinks, and alcoholic beverages.",
                "Saturated and hydrogenated fats."
            ]
        },
        "what_to_do": [
            "Measure and record blood pressure daily at the same time (target < 120/80 mmHg).",
            "Follow a strict low-sodium diet (< 1,500 - 2,000 mg of sodium daily).",
            "Practice stress-reduction techniques (deep breathing, meditation, yoga).",
            "Engage in regular low-impact cardiovascular activity 5 days a week.",
            "Take prescribed antihypertensive drugs consistently."
        ],
        "what_not_to_do": [
            "Do NOT stop blood pressure medication abruptly without consulting your doctor.",
            "Do NOT add table salt to cooked meals or consume instant processed noodles.",
            "Do NOT consume over-the-counter NSAIDs (like ibuprofen) frequently without medical advice.",
            "Do NOT engage in heavy, unmonitored weightlifting during acute spikes in blood pressure.",
            "Do NOT consume excessive alcohol or energy beverages."
        ],
        "lifestyle_advice": [
            "Maintain a healthy waist-to-hip ratio and target a normal BMI range.",
            "Ensure restful sleep and evaluate for obstructive sleep apnea if snoring occurs.",
            "Keep a daily log of blood pressure readings for physician reviews."
        ]
    },

    "cardiovascular": {
        "disease_name": "Cardiovascular & Coronary Vascular Condition",
        "causes": [
            "Atherosclerotic plaque accumulation in coronary or peripheral arteries.",
            "Myocardial oxygen supply-demand imbalance or altered cardiac perfusion.",
            "Elevated LDL cholesterol, systemic inflammation, and hypertension."
        ],
        "diet_plan": {
            "recommended": [
                "Heart-healthy Mediterranean diet rich in fresh vegetables and legumes.",
                "Omega-3 fatty acid sources (salmon, mackerel, walnuts, chia seeds).",
                "Soluble fiber (oatmeal, barley, apples, psyllium husk) to lower cholesterol.",
                "Antioxidant-rich berries and dark leafy greens."
            ],
            "avoid": [
                "Saturated fats, palm oil, butter, and lard.",
                "Deep-fried foods, fast food, and hydrogenated oils.",
                "Sodium-laden meals and processed meats.",
                "Sugary desserts and refined carbohydrates."
            ]
        },
        "what_to_do": [
            "Take all prescribed cardiac medications (statins, antiplatelets, beta-blockers) faithfully.",
            "Attend structured cardiac rehabilitation or prescribed physical therapy.",
            "Monitor for chest pain, shortness of breath, or swelling in lower extremities.",
            "Keep emergency contact numbers and medical history readily accessible.",
            "Maintain a calm environment and reduce acute physical or emotional stress."
        ],
        "what_not_to_do": [
            "Do NOT ignore chest pressure, discomfort, radiating arm/jaw pain, or severe shortness of breath.",
            "Do NOT perform heavy strenuous exertional labor without medical clearance.",
            "Do NOT smoke or expose yourself to secondhand smoke.",
            "Do NOT skip scheduled cardiology follow-up appointments.",
            "Do NOT abruptly stop blood thinners or antiplatelet therapy."
        ],
        "lifestyle_advice": [
            "Engage in medically supervised light-to-moderate exercise as tolerated.",
            "Monitor lipid panel (LDL, HDL, triglycerides) every 3-6 months.",
            "Maintain cardiac emergency awareness and family CPR knowledge."
        ]
    },

    "respiratory": {
        "disease_name": "Respiratory & Pulmonary Condition (Asthma / COPD / Pneumonia)",
        "causes": [
            "Airway inflammation, bronchospasm, or hyper-responsiveness to environmental triggers.",
            "Alveolar fluid accumulation or impaired gas exchange secondary to pulmonary infection.",
            "Chronic exposure to airborne irritants, smoking, or allergens."
        ],
        "diet_plan": {
            "recommended": [
                "Antioxidant-rich fruits and vegetables (oranges, bell peppers, tomatoes).",
                "Magnesium-rich foods (spinach, pumpkin seeds) to support bronchial relaxation.",
                "Abundant fluids and warm broths to clear mucous secretions.",
                "Lean proteins to maintain respiratory muscle strength."
            ],
            "avoid": [
                "Sulfites found in dried fruits, wine, and processed snacks (can trigger asthma).",
                "Excessive gas-producing foods (cabbage, carbonated drinks) that cause bloating pressure on diaphragm.",
                "Dairy products if they increase phlegm viscosity in sensitive individuals.",
                "Very cold beverages that may trigger reflex bronchospasm."
            ]
        },
        "what_to_do": [
            "Use rescue inhalers or nebulizers exactly as directed during acute dyspnea.",
            "Maintain clean indoor air using HEPA filters and adequate ventilation.",
            "Practice deep breathing exercises and pursed-lip breathing techniques.",
            "Stay up-to-date with annual influenza and pneumococcal vaccinations.",
            "Stay hydrated to thin pulmonary secretions."
        ],
        "what_not_to_do": [
            "Do NOT expose yourself to tobacco smoke, dust, chemical fumes, or strong perfumes.",
            "Do NOT ignore increasing shortness of breath, wheezing, or bluish lip discoloration.",
            "Do NOT exercise outdoors in extreme cold or during high pollen/pollution days.",
            "Do NOT allow indoor dust mites or mold to accumulate in living spaces.",
            "Do NOT stop maintenance steroid inhalers even when feeling symptom-free."
        ],
        "lifestyle_advice": [
            "Keep an updated Asthma / COPD Action Plan at home and work.",
            "Use a peak flow meter daily if recommended by your pulmonologist.",
            "Avoid sudden ambient temperature changes."
        ]
    },

    "renal": {
        "disease_name": "Renal & Nephrological Condition",
        "causes": [
            "Impaired glomerular filtration rate (GFR) and electrolyte filtration imbalance.",
            "Microvascular kidney damage secondary to chronic diabetes or hypertension.",
            "Accumulation of nitrogenous waste products (BUN, creatinine) in blood."
        ],
        "diet_plan": {
            "recommended": [
                "Controlled high-quality protein portions (egg whites, poultry) based on GFR stage.",
                "Low-potassium, low-phosphorus vegetables (cauliflower, cabbage, berries, apples).",
                "Leached vegetables if potassium restriction is indicated.",
                "Refined grains if whole grains exceed phosphorus allowances."
            ],
            "avoid": [
                "High-potassium foods (bananas, oranges, potatoes, tomatoes, salt substitutes).",
                "High-phosphorus foods (dairy, dark colas, nuts, organ meats, processed cheese).",
                "Excessive table salt and sodium-heavy frozen dinners.",
                "Excess protein intake beyond renal dietitian guidelines."
            ]
        },
        "what_to_do": [
            "Adhere strictly to fluid intake allowances prescribed by your nephrologist.",
            "Monitor daily weight to check for rapid fluid retention or edema.",
            "Track blood pressure rigorously to protect remaining kidney nephrons.",
            "Review all over-the-counter drugs with your pharmacist for nephrotoxicity.",
            "Undergo periodic renal function panels (eGFR, BUN, Creatinine, Electrolytes)."
        ],
        "what_not_to_do": [
            "Do NOT take NSAIDs (ibuprofen, naproxen) as they decrease renal blood flow.",
            "Do NOT consume potassium-based salt substitutes without physician approval.",
            "Do NOT over-hydrate or exceed designated fluid caps if on fluid restriction.",
            "Do NOT ignore swelling in ankles, legs, hands, or around eyes.",
            "Do NOT skip nephrology or dialysis appointments."
        ],
        "lifestyle_advice": [
            "Work with a specialized renal dietitian for tailored meal planning.",
            "Avoid herbal supplements that contain unknown heavy metals or nephrotoxins.",
            "Protect vascular access sites if undergoing hemodialysis."
        ]
    },

    "acne_dermatology": {
        "disease_name": "Dermatological & Inflammatory Skin Condition (Acne / Dermatitis)",
        "causes": [
            "Excess sebum production and follicular hyper-keratinization.",
            "Cutibacterium acnes proliferation and cutaneous inflammation.",
            "Hormonal fluctuations, high glycemic dietary triggers, or barrier disruption."
        ],
        "diet_plan": {
            "recommended": [
                "Low glycemic index foods (whole grains, vegetables, pulses).",
                "Zinc-rich foods (pumpkin seeds, lentils, lean beef) to support skin healing.",
                "Omega-3 fatty acids (salmon, flaxseeds) to reduce systemic skin inflammation.",
                "Antioxidant-dense berries and green tea containing EGCG polyphenol."
            ],
            "avoid": [
                "High glycemic sugary foods, chocolates, candy, and white flour products.",
                "Skim milk and whey protein supplements (linked to IGF-1 acne spikes).",
                "Greasy, heavily fried foods and trans fats.",
                "Excessive iodine or unvalidated high-dose biotin supplements."
            ]
        },
        "what_to_do": [
            "Wash affected skin twice daily with a gentle, non-comedogenic cleanser.",
            "Apply oil-free, non-comedogenic moisturizers and broad-spectrum sunscreen daily.",
            "Follow prescribed topical treatments (retinoids, benzoyl peroxide, salicylic acid).",
            "Change pillowcases and facial towels frequently (2-3 times a week).",
            "Keep hair clean and off the face to reduce sebum transfer."
        ],
        "what_not_to_do": [
            "Do NOT squeeze, pick, or pop acne lesions as it causes scarring and secondary infection.",
            "Do NOT scrub face aggressively with harsh physical exfoliants.",
            "Do NOT touch your face repeatedly with unwashed hands.",
            "Do NOT apply thick heavy pore-clogging makeup or oil-based cosmetics.",
            "Do NOT stop topical retinoid treatment during initial purging phase without consulting dermatologist."
        ],
        "lifestyle_advice": [
            "Manage stress levels as cortisol triggers sebaceous gland hyper-activity.",
            "Rinse face immediately after sweating or exercising.",
            "Consult a dermatologist for persistent nodulocystic lesions."
        ]
    },

    "mental_neurological": {
        "disease_name": "Neurological / Mood & Central Nervous System Condition",
        "causes": [
            "Neurotransmitter pathway dysregulation (serotonin, dopamine, norepinephrine).",
            "Neuro-inflammation, chronic stress axis activation (HPA axis), or vascular headache.",
            "Sleep disruption, hormonal shifts, or genetic susceptibility."
        ],
        "diet_plan": {
            "recommended": [
                "Tryptophan and tyrosine sources (turkey, eggs, cheese, oats).",
                "Omega-3 rich fish and chia seeds for neuronal membrane support.",
                "Fermented probiotic foods (yogurt, kefir) supporting gut-brain axis.",
                "Magnesium-rich dark chocolate (>70%), spinach, and pumpkin seeds."
            ],
            "avoid": [
                "Excessive caffeine and energy drinks that trigger anxiety or panic.",
                "Alcohol and recreational substances that disrupt sleep architecture.",
                "Artificial sweeteners and excessive refined sugars.",
                "Processed foods containing high monosodium glutamate (MSG) if sensitive to migraines."
            ]
        },
        "what_to_do": [
            "Take prescribed psychiatric or neurological medications consistently.",
            "Maintain a consistent sleep-wake schedule 7 days a week.",
            "Engage in cognitive behavioral strategies or mindfulness exercises.",
            "Expose yourself to natural sunlight for 15-30 minutes every morning.",
            "Build a supportive social network and check in with mental health professionals."
        ],
        "what_not_to_do": [
            "Do NOT stop antidepressant, anti-anxiety, or mood-stabilizing medications abruptly.",
            "Do NOT isolate yourself during severe mood dips or high anxiety episodes.",
            "Do NOT use alcohol or self-medicate to cope with emotional distress.",
            "Do NOT consume high doses of caffeine late in the afternoon or evening.",
            "Do NOT neglect physical health, nutrition, or basic hydration."
        ],
        "lifestyle_advice": [
            "Keep a daily mood, migraine, or sleep journal to track triggers.",
            "Practice progressive muscle relaxation before sleep.",
            "Establish clear work-rest boundaries to avoid burnout."
        ]
    },

    "gastrointestinal": {
        "disease_name": "Gastrointestinal & Digestive System Condition",
        "causes": [
            "Gastric mucosal irritation, altered gut motility, or acid reflux (GERD).",
            "Gut microbiome dysbiosis, inflammatory bowel activity, or digestive enzyme deficiency.",
            "Dietary triggers, stress, or long-term NSAID usage."
        ],
        "diet_plan": {
            "recommended": [
                "Bland, easily digestible foods (bananas, rice, applesauce, toast - BRAT diet).",
                "Steamed lean meats and non-acidic vegetables.",
                "Probiotic yogurt, kefir, and soluble fiber (oats, psyllium).",
                "Soothing herbal teas (chaimomile, ginger, peppermint - if not triggering GERD)."
            ],
            "avoid": [
                "Spicy foods, chili, hot sauces, and heavy pepper.",
                "Acidic fruits (citrus, tomatoes) and raw onion/garlic during acid flares.",
                "Deep-fried, high-fat, and heavy cream dishes.",
                "Carbonated beverages, alcohol, and caffeine."
            ]
        },
        "what_to_do": [
            "Eat smaller, more frequent meals rather than 3 large heavy meals.",
            "Chew food thoroughly and eat slowly in a relaxed environment.",
            "Stay upright for at least 2-3 hours after eating before lying down.",
            "Elevate the head of your bed by 4-6 inches if suffering from acid reflux.",
            "Maintain adequate fluid intake between meals rather than during meals."
        ],
        "what_not_to_do": [
            "Do NOT lie down or sleep immediately after dinner.",
            "Do NOT wear tight clothing around your waist that compresses the stomach.",
            "Do NOT smoke or chew tobacco as it relaxes the lower esophageal sphincter.",
            "Do NOT overeat or consume late-night heavy snacks.",
            "Do NOT overuse over-the-counter NSAID pain relievers."
        ],
        "lifestyle_advice": [
            "Identify and log individual food sensitivities.",
            "Engage in light walking after meals to aid gastric emptying.",
            "Consult a gastroenterologist if experiencing persistent abdominal pain or blood in stool."
        ]
    },

    "fungal_dermatology": {
        "disease_name": "Fungal Skin & Cutaneous Infection",
        "causes": [
            "Dermatophyte or Candida fungal proliferation in warm, humid skin environments.",
            "Disruption of natural skin barrier function or cutaneous microbiome imbalance.",
            "Direct contact with fungal spores or shared personal items (towels, footwear)."
        ],
        "diet_plan": {
            "recommended": [
                "Probiotic-rich foods (plain Greek yogurt, kefir) to support gut and skin microflora.",
                "Garlic and onions containing natural anti-fungal allicin compounds.",
                "Antioxidant-rich vegetables (spinach, broccoli, bell peppers).",
                "Coconut oil containing caprylic acid."
            ],
            "avoid": [
                "Refined sugars, candy, and sugary drinks that feed fungal yeast growth.",
                "Processed yeast products, beer, and aged fermented cheeses during acute flares.",
                "Refined carbohydrates and high glycemic snacks.",
                "Excessive alcohol consumption."
            ]
        },
        "what_to_do": [
            "Apply prescribed topical anti-fungal cream/powder consistently for full duration.",
            "Keep affected skin areas clean, completely dry, and well-ventilated.",
            "Wear loose, breathable cotton clothing and change daily.",
            "Wash towels, socks, and bedding in hot water regularly.",
            "Dry thoroughly between toes and skin folds after bathing."
        ],
        "what_not_to_do": [
            "Do NOT scratch or rub infected skin lesions as it spreads fungal spores.",
            "Do NOT share personal items like towels, combs, clothes, or shoes.",
            "Do NOT wear damp, sweaty clothes or tight synthetic footwear for long periods.",
            "Do NOT stop anti-fungal treatment early even if skin appearance improves.",
            "Do NOT apply heavy cosmetic oils or greasy occlusive ointments over active lesions."
        ],
        "lifestyle_advice": [
            "Wear protective footwear in public showers, locker rooms, and pool decks.",
            "Use separate clean towels for infected and uninfected body parts.",
            "Consult a dermatologist if lesions spread or show signs of secondary infection."
        ]
    },

    "default": {
        "disease_name": "General Clinical & Metabolic Disorder",
        "causes": [
            "Systemic physiological imbalance identified through laboratory testing and clinical admission.",
            "Multi-factorial health risk requiring comprehensive diagnostic and therapeutic monitoring."
        ],
        "diet_plan": {
            "recommended": [
                "Nutrient-dense whole food diet rich in colorful vegetables, lean proteins, and fiber.",
                "Hydration with clean water (2-3 liters daily unless fluid restricted).",
                "Whole grains and unprocessed nuts in moderate portions."
            ],
            "avoid": [
                "Ultra-processed convenience foods, high sodium meals, and sugary beverages.",
                "Trans fats, hydrogenated oils, and excessive alcohol.",
                "Refined carbohydrates and excessive added sugars."
            ]
        },
        "what_to_do": [
            "Follow all physician prescriptions and dosage instructions carefully.",
            "Schedule regular follow-up visits with your primary care provider.",
            "Engage in moderate daily physical activity as tolerated.",
            "Maintain an updated list of all active medications and allergies."
        ],
        "what_not_to_do": [
            "Do NOT self-medicate or alter drug dosages without consulting your doctor.",
            "Do NOT ignore persistent or worsening symptoms.",
            "Do NOT skip routine clinical blood work and check-ups.",
            "Do NOT rely solely on internet remedies for serious health conditions."
        ],
        "lifestyle_advice": [
            "Prioritize restorative sleep and effective stress management.",
            "Keep emergency contact details accessible.",
            "Maintain an active partnership with your healthcare provider."
        ]
    }
}


def analyze_patient_test_data(patient_data: Dict[str, Any], condition: str = "") -> List[str]:
    """
    Extract key clinical insights from patient lab test results, ICD-9 diagnosis codes,
    and admission parameters.
    """
    insights = []
    
    # 1. Check HbA1c test result
    a1c = str(patient_data.get("A1Cresult") or "").strip()
    if a1c == ">8":
        insights.append("HbA1c Test: >8% - Severe long-term glycemic elevation indicating uncontrolled blood sugar.")
    elif a1c == ">7":
        insights.append("HbA1c Test: >7% - Elevated glycemic level above target range.")
    elif a1c == "Norm":
        insights.append("HbA1c Test: Normal range - Good glycemic baseline control.")

    # 2. Check Glucose Serum result
    glu = str(patient_data.get("max_glu_serum") or "").strip()
    if glu == ">300":
        insights.append("Max Glucose Serum: >300 mg/dL - Acute hyper-glycemic state requiring clinical intervention.")
    elif glu == ">200":
        insights.append("Max Glucose Serum: >200 mg/dL - Elevated blood glucose requiring dietary and medical adjustment.")
    elif glu == "Norm":
        insights.append("Max Glucose Serum: Normal range.")

    # 3. Check Diagnosis Codes (ICD-9)
    diag_1 = str(patient_data.get("diag_1") or "").strip()
    diag_2 = str(patient_data.get("diag_2") or "").strip()
    diag_3 = str(patient_data.get("diag_3") or "").strip()
    
    diag_list = [d for d in [diag_1, diag_2, diag_3] if d and d != "None"]
    if diag_list:
        insights.append(f"Recorded ICD-9 Diagnoses: {', '.join(diag_list)}")
        if any(d.startswith("110") for d in diag_list):
            insights.append("Diagnostic Category: Cutaneous Dermatological / Fungal Infection.")
        if any(d.startswith("250") for d in diag_list):
            insights.append("Diagnostic Category: Diabetes Mellitus with potential vascular or organ complications.")
        if any(d.startswith("401") or d.startswith("402") for d in diag_list):
            insights.append("Diagnostic Category: Hypertensive Vascular Disease.")
        if any(d.startswith("410") or d.startswith("414") or d.startswith("428") for d in diag_list):
            insights.append("Diagnostic Category: Cardiac / Ischemic Heart Disease.")
        if any(d.startswith("480") or d.startswith("486") or d.startswith("491") or d.startswith("496") for d in diag_list):
            insights.append("Diagnostic Category: Respiratory / Pulmonary Disease.")
        if any(d.startswith("585") for d in diag_list):
            insights.append("Diagnostic Category: Chronic Kidney Disease / Renal Impairment.")

    # 4. Check Hospitalization & Lab Procedure Intensity
    time_hosp = patient_data.get("time_in_hospital")
    num_labs = patient_data.get("num_lab_procedures")
    num_meds = patient_data.get("num_medications")
    
    if time_hosp and int(time_hosp) >= 7:
        insights.append(f"Extended Hospitalization: {time_hosp} days - Indicates significant clinical complexity.")
    if num_labs and int(num_labs) >= 50:
        insights.append(f"High Laboratory Workup Volume: {num_labs} lab procedures performed.")
    if num_meds and int(num_meds) >= 15:
        insights.append(f"Poly-pharmacy Alert: {num_meds} distinct active medications prescribed.")

    # 5. Check Active Medications
    insulin = str(patient_data.get("insulin") or "").strip()
    metformin = str(patient_data.get("metformin") or "").strip()
    if insulin in ["Up", "Steady", "Down"]:
        insights.append(f"Insulin Therapy Active (Status: {insulin}).")
    if metformin in ["Up", "Steady", "Down"]:
        insights.append(f"Oral Antidiabetic Active (Metformin Status: {metformin}).")

    if not insights:
        insights.append("Patient parameters evaluated; overall clinical profile logged for stratification.")

    return insights


def get_clinical_guidance(condition: str = "", patient_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Intelligently map condition string, ICD-9 codes, and patient test data
    to disease identification, causes, test insights, diet plan, and action guidelines.
    """
    if patient_data is None:
        patient_data = {}

    cond_lower = (condition or "").lower().strip()
    diag_1 = str(patient_data.get("diag_1") or "").strip()

    matched_key = "default"

    # Priority 1: Match condition string
    if "fungal" in cond_lower or "yeast" in cond_lower or "tinea" in cond_lower or "mycos" in cond_lower:
        matched_key = "fungal_dermatology"
    elif "acne" in cond_lower or "skin" in cond_lower or "eczema" in cond_lower or "dermat" in cond_lower:
        matched_key = "acne_dermatology"
    elif "reflux" in cond_lower or "gerd" in cond_lower or "ulcer" in cond_lower or "gastri" in cond_lower or "crohn" in cond_lower or "gastro" in cond_lower:
        matched_key = "gastrointestinal"
    elif "asthma" in cond_lower or "copd" in cond_lower or "pneumon" in cond_lower or "bronch" in cond_lower:
        matched_key = "respiratory"
    elif "heart" in cond_lower or "cardiac" in cond_lower or "angina" in cond_lower:
        matched_key = "cardiovascular"
    elif "diab" in cond_lower or "glycem" in cond_lower:
        matched_key = "diabetes"
    elif "hyper" in cond_lower or "pressure" in cond_lower:
        matched_key = "hypertension"
    elif "kidney" in cond_lower or "renal" in cond_lower or "nephr" in cond_lower:
        matched_key = "renal"
    elif "depress" in cond_lower or "anxiety" in cond_lower or "bipolar" in cond_lower or "migraine" in cond_lower:
        matched_key = "mental_neurological"
    # Priority 2: Fallback to primary ICD-9 code (diag_1)
    elif diag_1.startswith("110"):
        matched_key = "fungal_dermatology"
    elif diag_1.startswith("250"):
        matched_key = "diabetes"
    elif diag_1.startswith("401") or diag_1.startswith("402"):
        matched_key = "hypertension"
    elif any(diag_1.startswith(d) for d in ["410", "414", "427", "428"]):
        matched_key = "cardiovascular"
    elif any(diag_1.startswith(d) for d in ["486", "491", "496"]):
        matched_key = "respiratory"
    elif diag_1.startswith("530") or diag_1.startswith("558"):
        matched_key = "gastrointestinal"

    # Retrieve base guidance template
    template = CLINICAL_KNOWLEDGE_BASE.get(matched_key, CLINICAL_KNOWLEDGE_BASE["default"])

    # Clean disease title without concatenating secondary conditions
    disease_name = condition.title() if condition else template["disease_name"]

    # Generate patient-specific test insights
    insights = analyze_patient_test_data(patient_data, condition)

    return {
        "disease_name": disease_name,
        "causes": template["causes"],
        "test_insights": insights,
        "diet_plan": template["diet_plan"],
        "what_to_do": template["what_to_do"],
        "what_not_to_do": template["what_not_to_do"],
        "lifestyle_advice": template["lifestyle_advice"]
    }
