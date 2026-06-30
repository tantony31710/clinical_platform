import type { FieldConfig, SpecialtyConfig } from '../types';

// ─── Global Baseline Fields ────────────────────────────────────────────────
export const GLOBAL_BASELINE_FIELDS: Record<string, FieldConfig> = {
  Age: {
    prompt: "Patient's current age (years)",
    type: 'numeric',
    min_allowed: 1,
    max_allowed: 120,
    default: 40,
  },
  Sex: {
    prompt: 'Biological sex at birth (1 = Male, 0 = Female)',
    type: 'numeric',
    min_allowed: 0,
    max_allowed: 1,
    default: 1,
  },
  BloodPressure: {
    prompt: 'Resting systolic blood pressure (mmHg)',
    type: 'numeric',
    min_allowed: 50,
    max_allowed: 250,
    max_optimal: 120,
    default: 120,
    tip: 'Sustained systolic pressure above 120 mmHg is an independent risk multiplier across nearly every organ system.',
  },
  Smoker: {
    prompt: 'Current or former regular smoker?',
    type: 'choice',
    choices: ['yes', 'no'],
    default: 'no',
  },
};

// ─── Specialty Configs ─────────────────────────────────────────────────────
export const SPECIALTY_CONFIGS: Record<string, SpecialtyConfig> = {
  metabolic: {
    title: 'Metabolic & Endocrinology',
    category: 'Endocrine & Metabolic',
    description: 'ML risk model trained on the Pima Indians Diabetes dataset (NIDDK).',
    engine: { type: 'ml', feature_order: ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'] },
    registry: {
      Pregnancies: { prompt: 'Total number of pregnancies (0 if not applicable)', type: 'numeric', min_allowed: 0, max_allowed: 25, default: 0 },
      Glucose: { prompt: 'Fasting plasma glucose (mg/dL)', type: 'numeric', min_allowed: 30, max_allowed: 600, max_optimal: 100, default: 90, tip: 'Fasting glucose above 100 mg/dL signals early insulin-secretory stress.' },
      SkinThickness: { prompt: 'Triceps skin fold thickness (mm) — 0 if unknown', type: 'numeric', min_allowed: 0, max_allowed: 100, default: 20 },
      Insulin: { prompt: '2-hour post-prandial serum insulin (µU/mL) — 0 if unknown', type: 'numeric', min_allowed: 0, max_allowed: 900, default: 79 },
      BMI: { prompt: 'Body Mass Index (kg/m²)', type: 'numeric', min_allowed: 10, max_allowed: 80, max_optimal: 24.9, default: 22, tip: 'BMI over 25 amplifies adipose-driven insulin resistance.' },
      DiabetesPedigreeFunction: { prompt: 'Diabetes pedigree function (family history index)', type: 'numeric', min_allowed: 0.01, max_allowed: 3.0, default: 0.47 },
    },
  },

  cardio: {
    title: 'Cardiovascular Medicine',
    category: 'Cardiovascular',
    description: 'ML risk model trained on a clinical heart-disease cohort dataset.',
    engine: { type: 'ml', feature_order: ['Age', 'Sex', 'ChestPainType', 'BloodPressure', 'Cholesterol', 'FastingBloodSugar', 'RestingECG', 'MaxHeartRate', 'ExerciseAngina', 'Oldpeak', 'STSlope'] },
    registry: {
      ChestPainType: { prompt: 'Chest pain type (1=Typical angina, 2=Atypical, 3=Non-anginal, 4=Asymptomatic)', type: 'numeric', min_allowed: 1, max_allowed: 4, default: 2 },
      Cholesterol: { prompt: 'Total serum cholesterol (mg/dL)', type: 'numeric', min_allowed: 80, max_allowed: 600, max_optimal: 200, default: 190, tip: 'Sustained high cholesterol accelerates atheromatous plaque formation.' },
      FastingBloodSugar: { prompt: 'Fasting blood sugar > 120 mg/dL? (1=Yes, 0=No)', type: 'numeric', min_allowed: 0, max_allowed: 1, default: 0 },
      RestingECG: { prompt: 'Resting ECG result (0=Normal, 1=ST-T abnormality, 2=Ventricular hypertrophy)', type: 'numeric', min_allowed: 0, max_allowed: 2, default: 0 },
      MaxHeartRate: { prompt: 'Maximum heart rate during stress testing', type: 'numeric', min_allowed: 50, max_allowed: 250, default: 150 },
      ExerciseAngina: { prompt: 'Exercise-induced angina (1=Yes, 0=No)', type: 'numeric', min_allowed: 0, max_allowed: 1, default: 0 },
      Oldpeak: { prompt: 'Exercise-induced ST depression (relative to rest)', type: 'numeric', min_allowed: 0, max_allowed: 10, default: 0 },
      STSlope: { prompt: 'Peak exercise ST slope (1=Upsloping, 2=Flat, 3=Downsloping)', type: 'numeric', min_allowed: 1, max_allowed: 3, default: 1 },
    },
  },

  nephrology: {
    title: 'Nephrology & Renal Care',
    category: 'Renal',
    description: 'ML risk model trained on the UCI Chronic Kidney Disease dataset.',
    engine: { type: 'ml', feature_order: ['Age', 'DiastolicBP', 'SpecificGravity', 'Albumin', 'Sugar', 'BloodGlucoseRandom', 'BloodUrea', 'SerumCreatinine', 'Hemoglobin', 'HypertensionHistory', 'DiabetesMellitusHistory'] },
    registry: {
      DiastolicBP: { prompt: 'Diastolic blood pressure (mmHg)', type: 'numeric', min_allowed: 40, max_allowed: 180, default: 80 },
      SpecificGravity: { prompt: 'Urinalysis specific gravity (1.005–1.025)', type: 'numeric', min_allowed: 1.000, max_allowed: 1.040, default: 1.020 },
      Albumin: { prompt: 'Urinalysis albumin grade (0–5)', type: 'numeric', min_allowed: 0, max_allowed: 5, default: 0 },
      Sugar: { prompt: 'Urinalysis glucose grade (0–5)', type: 'numeric', min_allowed: 0, max_allowed: 5, default: 0 },
      BloodGlucoseRandom: { prompt: 'Random blood glucose (mg/dL)', type: 'numeric', min_allowed: 40, max_allowed: 600, default: 100 },
      BloodUrea: { prompt: 'Blood urea (mg/dL)', type: 'numeric', min_allowed: 5, max_allowed: 300, max_optimal: 40, default: 30, tip: 'Elevated blood urea is an early marker of declining nephron clearance.' },
      SerumCreatinine: { prompt: 'Serum creatinine (mg/dL)', type: 'numeric', min_allowed: 0.2, max_allowed: 20, max_optimal: 1.2, default: 1.0, tip: 'Rising creatinine directly reflects falling glomerular filtration rate.' },
      Hemoglobin: { prompt: 'Hemoglobin level (g/dL)', type: 'numeric', min_allowed: 2, max_allowed: 20, default: 14 },
      HypertensionHistory: { prompt: 'History of hypertension?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      DiabetesMellitusHistory: { prompt: 'History of diabetes mellitus?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },

  oncology_breast: {
    title: 'Oncology — Breast Imaging',
    category: 'Oncology',
    description: 'ML model trained on the Breast Cancer Wisconsin (Diagnostic) dataset.',
    engine: { type: 'ml', feature_order: ['MeanRadius', 'MeanTexture', 'MeanPerimeter', 'MeanArea', 'MeanSmoothness', 'MeanCompactness', 'MeanConcavity', 'MeanConcavePoints', 'MeanSymmetry', 'MeanFractalDimension'] },
    registry: {
      MeanRadius: { prompt: 'Mean tumor nucleus radius (imaging/cytology)', type: 'numeric', min_allowed: 3, max_allowed: 40, default: 14 },
      MeanTexture: { prompt: 'Mean nucleus texture (gray-scale std dev)', type: 'numeric', min_allowed: 5, max_allowed: 45, default: 19 },
      MeanPerimeter: { prompt: 'Mean tumor nucleus perimeter', type: 'numeric', min_allowed: 20, max_allowed: 220, default: 92 },
      MeanArea: { prompt: 'Mean tumor nucleus area', type: 'numeric', min_allowed: 100, max_allowed: 2600, default: 655 },
      MeanSmoothness: { prompt: 'Mean smoothness (local radius variation)', type: 'numeric', min_allowed: 0.02, max_allowed: 0.20, default: 0.096 },
      MeanCompactness: { prompt: 'Mean compactness (perimeter² / area − 1)', type: 'numeric', min_allowed: 0, max_allowed: 0.40, default: 0.104 },
      MeanConcavity: { prompt: 'Mean concavity (contour severity)', type: 'numeric', min_allowed: 0, max_allowed: 0.50, default: 0.089 },
      MeanConcavePoints: { prompt: 'Mean concave portions of contour', type: 'numeric', min_allowed: 0, max_allowed: 0.25, default: 0.048 },
      MeanSymmetry: { prompt: 'Mean nucleus symmetry', type: 'numeric', min_allowed: 0.05, max_allowed: 0.35, default: 0.181 },
      MeanFractalDimension: { prompt: 'Mean fractal dimension (coastline approx − 1)', type: 'numeric', min_allowed: 0.04, max_allowed: 0.12, default: 0.063 },
    },
  },

  oncology_cervical: {
    title: 'Oncology — Gynecologic Screening',
    category: 'Oncology',
    description: 'Evidence-based cervical cancer risk-factor scoring (ACS/WHO criteria). Rule-based.',
    engine: { type: 'rule', rule_fn: 'cervical_cancer_risk' },
    registry: {
      HPVPositive: { prompt: 'Confirmed positive HPV test?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      AbnormalPapSmear: { prompt: 'Any prior abnormal Pap smear result?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      STDHistory: { prompt: 'History of any sexually transmitted infection?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      LongTermContraceptiveUse: { prompt: 'Oral contraceptive use for 5+ years?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },

  hepatology: {
    title: 'Hepatology & Liver Care',
    category: 'Hepatic & Digestive',
    description: 'Evidence-based liver fibrosis risk using validated APRI index. Rule-based.',
    engine: { type: 'rule', rule_fn: 'liver_disease_risk' },
    registry: {
      AST: { prompt: 'Serum AST / SGOT (U/L)', type: 'numeric', min_allowed: 5, max_allowed: 2000, max_optimal: 40, default: 25, tip: 'AST above ~40 U/L signals hepatocellular stress.' },
      PlateletCount: { prompt: 'Platelet count (×10⁹/L)', type: 'numeric', min_allowed: 5, max_allowed: 800, default: 250 },
      TotalBilirubin: { prompt: 'Total bilirubin (mg/dL)', type: 'numeric', min_allowed: 0.1, max_allowed: 40, max_optimal: 1.2, default: 0.8, tip: 'Bilirubin above 1.2 mg/dL suggests impaired hepatic clearance.' },
      Albumin: { prompt: 'Serum albumin (g/dL)', type: 'numeric', min_allowed: 1, max_allowed: 6, default: 4.2 },
    },
  },

  pulmonology: {
    title: 'Pulmonology & Respiratory Care',
    category: 'Respiratory',
    description: 'Evidence-based airway obstruction staging using GOLD spirometry criteria. Rule-based.',
    engine: { type: 'rule', rule_fn: 'copd_asthma_risk' },
    registry: {
      FEV1FVCRatio: { prompt: 'Post-bronchodilator FEV1/FVC ratio', type: 'numeric', min_allowed: 0.2, max_allowed: 1.0, default: 0.80 },
      FEV1PercentPredicted: { prompt: 'FEV1 as % of predicted normal', type: 'numeric', min_allowed: 10, max_allowed: 130, default: 90 },
      ChronicCough: { prompt: 'Chronic cough present (3+ months)?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      Wheezing: { prompt: 'Recurrent wheezing episodes?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },

  neurology_stroke: {
    title: 'Neurology — Cerebrovascular Risk',
    category: 'Neurological',
    description: 'Evidence-based stroke risk using validated CHA₂DS₂-VASc score. Rule-based.',
    engine: { type: 'rule', rule_fn: 'stroke_risk_chadsvasc' },
    registry: {
      CongestiveHeartFailureHistory: { prompt: 'History of congestive heart failure?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      HypertensionHistory: { prompt: 'Diagnosed history of hypertension?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      DiabetesMellitusHistory: { prompt: 'Diagnosed history of diabetes mellitus?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      PriorStrokeOrTIA: { prompt: 'Prior stroke or TIA?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      VascularDiseaseHistory: { prompt: 'History of vascular disease (MI, PAD, aortic plaque)?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },

  infectious_disease: {
    title: 'Infectious Disease & Critical Care',
    category: 'Infectious & Critical Care',
    description: 'Evidence-based sepsis risk screening using qSOFA score (Sepsis-3 criteria). Rule-based.',
    engine: { type: 'rule', rule_fn: 'sepsis_risk_qsofa' },
    registry: {
      RespiratoryRate: { prompt: 'Respiratory rate (breaths/min)', type: 'numeric', min_allowed: 6, max_allowed: 60, default: 16 },
      AlteredMentalStatus: { prompt: 'New alteration in mental status?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },

  rheumatology: {
    title: 'Rheumatology & Autoimmune',
    category: 'Musculoskeletal & Autoimmune',
    description: 'Inflammatory arthritis risk scoring (2010 ACR/EULAR classification). Rule-based.',
    engine: { type: 'rule', rule_fn: 'rheumatoid_arthritis_risk' },
    registry: {
      AffectedJointCount: { prompt: 'Number of swollen or tender joints', type: 'numeric', min_allowed: 0, max_allowed: 50, default: 0 },
      SymptomDurationWeeks: { prompt: 'Duration of joint symptoms (weeks)', type: 'numeric', min_allowed: 0, max_allowed: 520, default: 1 },
      SeropositiveRForACPA: { prompt: 'Positive RF or anti-CCP/ACPA test?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      ElevatedCRPorESR: { prompt: 'Elevated CRP or ESR (inflammatory markers)?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },

  psychiatry: {
    title: 'Psychiatry & Behavioral Health',
    category: 'Mental Health',
    description: 'PHQ-9 validated 9-item depression screening instrument. Rule-based. Not a diagnosis.',
    engine: { type: 'rule', rule_fn: 'depression_screen_phq9' },
    registry: {
      PHQ_Interest: { prompt: 'Little interest/pleasure (0=not at all → 3=nearly every day)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
      PHQ_Mood: { prompt: 'Feeling down/depressed/hopeless (0–3)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
      PHQ_Sleep: { prompt: 'Trouble sleeping or sleeping too much (0–3)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
      PHQ_Fatigue: { prompt: 'Tired or little energy (0–3)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
      PHQ_Appetite: { prompt: 'Poor appetite or overeating (0–3)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
      PHQ_SelfWorth: { prompt: 'Feeling like a failure or letting others down (0–3)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
      PHQ_Concentration: { prompt: 'Trouble concentrating (0–3)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
      PHQ_Psychomotor: { prompt: 'Moving/speaking slower or unusually restless (0–3)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
      PHQ_SelfHarmThoughts: { prompt: 'Thoughts of self-harm or being better off dead (0–3)', type: 'numeric', min_allowed: 0, max_allowed: 3, default: 0 },
    },
  },

  endocrinology_thyroid: {
    title: 'Endocrinology — Thyroid',
    category: 'Endocrine & Metabolic',
    description: 'Thyroid function classification using TSH/Free T4 reference ranges. Rule-based.',
    engine: { type: 'rule', rule_fn: 'thyroid_function_assessment' },
    registry: {
      TSH: { prompt: 'Serum TSH level (mIU/L)', type: 'numeric', min_allowed: 0.001, max_allowed: 100, default: 2.0 },
      FreeT4: { prompt: 'Free T4 level (ng/dL)', type: 'numeric', min_allowed: 0.1, max_allowed: 10, default: 1.2 },
      SymptomaticThyroid: { prompt: 'Thyroid-related symptoms present?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },

  hematology: {
    title: 'Hematology',
    category: 'Hematologic',
    description: 'Anemia classification using WHO hemoglobin diagnostic thresholds. Rule-based.',
    engine: { type: 'rule', rule_fn: 'anemia_classification_who' },
    registry: {
      Hemoglobin: { prompt: 'Hemoglobin level (g/dL)', type: 'numeric', min_allowed: 2, max_allowed: 20, default: 14 },
      MCV: { prompt: 'Mean corpuscular volume (fL)', type: 'numeric', min_allowed: 50, max_allowed: 130, default: 90 },
    },
  },

  dermatology: {
    title: 'Dermatology — Skin Lesion',
    category: 'Dermatologic',
    description: 'Melanoma risk screening using validated ABCDE clinical criteria. Rule-based.',
    engine: { type: 'rule', rule_fn: 'melanoma_risk_abcde' },
    registry: {
      AsymmetricShape: { prompt: 'Lesion is asymmetric?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      IrregularBorder: { prompt: 'Borders irregular or poorly defined?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      ColorVariation: { prompt: 'Varied coloring (multiple shades)?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      LesionDiameterMM: { prompt: 'Lesion diameter (mm)', type: 'numeric', min_allowed: 0.5, max_allowed: 80, max_optimal: 6, default: 3, tip: 'Diameters over 6mm are a recognized melanoma warning sign.' },
      RecentEvolutionChange: { prompt: 'Recent change in size, shape, or color?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },

  urology: {
    title: 'Urology & Genitourinary',
    category: 'Genitourinary',
    description: 'Lower urinary tract symptom screening with PSA threshold flagging. Rule-based.',
    engine: { type: 'rule', rule_fn: 'lower_urinary_tract_risk' },
    registry: {
      NocturiaFrequency: { prompt: 'Nightly urination frequency', type: 'numeric', min_allowed: 0, max_allowed: 15, default: 1 },
      WeakUrineStream: { prompt: 'Weak or interrupted urine stream?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      PSALevel: { prompt: 'Serum PSA level (ng/mL)', type: 'numeric', min_allowed: 0, max_allowed: 100, max_optimal: 4, default: 1, tip: 'PSA above 4.0 ng/mL prompts further urologic workup.' },
    },
  },

  ophthalmology: {
    title: 'Ophthalmology — Diabetic Retinopathy',
    category: 'Ophthalmic',
    description: 'Diabetic retinopathy risk factors (DCCT/UKPDS studies). Rule-based.',
    engine: { type: 'rule', rule_fn: 'diabetic_retinopathy_risk' },
    registry: {
      DiabetesDurationYears: { prompt: 'Years since diabetes diagnosis', type: 'numeric', min_allowed: 0, max_allowed: 70, default: 0 },
      HbA1c: { prompt: 'Most recent HbA1c (%)', type: 'numeric', min_allowed: 3.5, max_allowed: 18, max_optimal: 7, default: 5.5, tip: 'HbA1c sustained above 7% accelerates microvascular retinal damage.' },
    },
  },

  orthopedics: {
    title: 'Orthopedics — Bone Health',
    category: 'Musculoskeletal & Autoimmune',
    description: 'Osteoporotic fracture risk factors (FRAX clinical risk tool). Rule-based.',
    engine: { type: 'rule', rule_fn: 'osteoporosis_risk_frax_like' },
    registry: {
      PriorFractureHistory: { prompt: 'Prior fragility (low-trauma) fracture as adult?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      FamilyHistoryHipFracture: { prompt: 'Parental history of hip fracture?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
      LongTermSteroidUse: { prompt: 'Long-term oral corticosteroid use (3+ months)?', type: 'choice', choices: ['yes', 'no'], default: 'no' },
    },
  },
};

// ─── ML Specialties (the 4 with trained models) ────────────────────────────
export const ML_SPECIALTY_IDS = ['metabolic', 'cardio', 'nephrology', 'oncology_breast'] as const;

// ─── Category groupings for UI nav ────────────────────────────────────────
export const CATEGORY_GROUPS: Record<string, string[]> = {
  'Endocrine & Metabolic': ['metabolic', 'endocrinology_thyroid'],
  'Cardiovascular': ['cardio', 'neurology_stroke'],
  'Renal': ['nephrology'],
  'Oncology': ['oncology_breast', 'oncology_cervical'],
  'Respiratory': ['pulmonology'],
  'Hepatic & Digestive': ['hepatology'],
  'Infectious & Critical Care': ['infectious_disease'],
  'Musculoskeletal & Autoimmune': ['rheumatology', 'orthopedics'],
  'Mental Health': ['psychiatry'],
  'Hematologic': ['hematology'],
  'Dermatologic': ['dermatology'],
  'Genitourinary': ['urology'],
  'Ophthalmic': ['ophthalmology'],
  'Neurological': ['neurology_stroke'],
};
