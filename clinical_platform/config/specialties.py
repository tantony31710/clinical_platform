# config/specialties.py
"""
Central clinical configuration registry.

GLOBAL_BASELINE_FEATURES: questions asked once per session, shared across every tab.

SPECIALTY_FIELDS: one entry per medical department/tab. Each entry declares an
"engine":
    - type "ml"   -> a real scikit-learn model trained on a real public dataset
                     (see models/train_models.py). "feature_order" lists the
                     profile keys fed to the model, in the exact order the
                     model was trained on (global keys are mixed in where the
                     model was trained using that shared measurement).
    - type "rule" -> a real, named, validated clinical scoring system (qSOFA,
                     PHQ-9, CHA2DS2-VASc, KDIGO, GOLD, ABCDE, APRI, WHO anemia
                     criteria, etc.) implemented in engines/rule_engines.py.
                     These are not machine-learned, but they are real medicine
                     -- not flavor text -- and are labeled as such in the UI.

Keys are intentionally reused across specialties where the same real-world
measurement applies (e.g. "Hemoglobin" appears in both Nephrology and
Hematology) so the session's smart-skip logic avoids asking the same
question twice.
"""

GLOBAL_BASELINE_FEATURES = {
    "Age": {
        "prompt": "What is the patient's current age in years?",
        "type": "numeric", "min_allowed": 1.0, "max_allowed": 120.0, "default": 40.0,
    },
    "Sex": {
        "prompt": "Biological sex at birth? (1 = Male, 0 = Female)",
        "type": "numeric", "min_allowed": 0, "max_allowed": 1, "default": 1,
    },
    "BloodPressure": {
        "prompt": "Most recent resting systolic blood pressure (mmHg)?",
        "type": "numeric", "min_allowed": 50.0, "max_allowed": 250.0, "max_optimal": 120.0,
        "tip": "Sustained systolic pressure above 120 mmHg is an independent risk multiplier across nearly every organ system.",
        "default": 120.0,
    },
    "Smoker": {
        "prompt": "Current or former regular smoker? (yes/no)",
        "type": "choice", "choices": ["yes", "no"], "default": "no",
    },
}

SPECIALTY_FIELDS = {

    # ======================================================================
    # ML — Pima Indians Diabetes Database (NIDDK, 768 patients, real data)
    # ======================================================================
    "metabolic": {
        "title": "🍬 Metabolic & Endocrinology — Diabetes",
        "category": "Endocrine & Metabolic",
        "description": "Real machine-learning risk model trained on the Pima Indians Diabetes dataset (NIDDK).",
        "engine": {
            "type": "ml",
            "model_file": "models/diabetes_model.pkl",
            "feature_order": ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
                               "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"],
            "positive_verdict": "🚨 HIGH-RISK PATTERN FOR TYPE 2 DIABETES DETECTED",
            "negative_verdict": "✅ LOW-RISK METABOLIC PROFILE",
        },
        "registry": {
            "Pregnancies": {"prompt": "Total number of pregnancies? (Enter 0 if male or not applicable)", "type": "numeric", "min_allowed": 0.0, "max_allowed": 25.0, "default": 0.0},
            "Glucose": {"prompt": "Fasting plasma glucose concentration (mg/dL)?", "type": "numeric", "min_allowed": 30.0, "max_allowed": 600.0, "max_optimal": 100.0, "tip": "Fasting glucose sustained above 100 mg/dL signals early insulin-secretory stress.", "default": 90.0},
            "SkinThickness": {"prompt": "Triceps skin fold thickness (mm)? (Enter 0 if unknown)", "type": "numeric", "min_allowed": 0.0, "max_allowed": 100.0, "default": 20.0},
            "Insulin": {"prompt": "2-hour post-prandial serum insulin (mu U/ml)? (Enter 0 if unknown)", "type": "numeric", "min_allowed": 0.0, "max_allowed": 900.0, "default": 79.0},
            "BMI": {"prompt": "Body Mass Index (kg/m²)?", "type": "numeric", "min_allowed": 10.0, "max_allowed": 80.0, "max_optimal": 24.9, "tip": "BMI over 25 amplifies adipose-driven insulin resistance.", "default": 22.0},
            "DiabetesPedigreeFunction": {"prompt": "Diabetes pedigree function score (family history index, or enter 0.47 if unknown)?", "type": "numeric", "min_allowed": 0.01, "max_allowed": 3.0, "default": 0.47},
        },
    },

    # ======================================================================
    # ML — Statlog/Cleveland-style Heart Disease dataset (1190 patients)
    # ======================================================================
    "cardio": {
        "title": "🫀 Cardiovascular Medicine",
        "category": "Cardiovascular",
        "description": "Real machine-learning risk model trained on a clinical heart-disease cohort dataset.",
        "engine": {
            "type": "ml",
            "model_file": "models/heart_model.pkl",
            "feature_order": ["Age", "Sex", "ChestPainType", "BloodPressure", "Cholesterol",
                               "FastingBloodSugar", "RestingECG", "MaxHeartRate",
                               "ExerciseAngina", "Oldpeak", "STSlope"],
            "positive_verdict": "🚨 HIGH-RISK PATTERN FOR CORONARY HEART DISEASE DETECTED",
            "negative_verdict": "✅ LOW-RISK CARDIOVASCULAR PROFILE",
        },
        "registry": {
            "ChestPainType": {"prompt": "Chest pain classification? (1: Typical angina, 2: Atypical angina, 3: Non-anginal pain, 4: Asymptomatic)", "type": "numeric", "min_allowed": 1, "max_allowed": 4, "default": 2},
            "Cholesterol": {"prompt": "Total serum cholesterol (mg/dL)?", "type": "numeric", "min_allowed": 80.0, "max_allowed": 600.0, "max_optimal": 200.0, "tip": "Sustained high cholesterol accelerates atheromatous plaque formation in major vessels.", "default": 190.0},
            "FastingBloodSugar": {"prompt": "Is fasting blood sugar above 120 mg/dL? (1: Yes, 0: No)", "type": "numeric", "min_allowed": 0, "max_allowed": 1, "default": 0},
            "RestingECG": {"prompt": "Resting ECG result? (0: Normal, 1: ST-T wave abnormality, 2: Probable ventricular hypertrophy)", "type": "numeric", "min_allowed": 0, "max_allowed": 2, "default": 0},
            "MaxHeartRate": {"prompt": "Maximum heart rate achieved during stress testing?", "type": "numeric", "min_allowed": 50.0, "max_allowed": 250.0, "default": 150.0},
            "ExerciseAngina": {"prompt": "Does physical exertion trigger chest pain? (1: Yes, 0: No)", "type": "numeric", "min_allowed": 0, "max_allowed": 1, "default": 0},
            "Oldpeak": {"prompt": "Exercise-induced ST depression relative to rest?", "type": "numeric", "min_allowed": 0.0, "max_allowed": 10.0, "default": 0.0},
            "STSlope": {"prompt": "Peak exercise ST segment slope? (1: Upsloping, 2: Flat, 3: Downsloping)", "type": "numeric", "min_allowed": 1, "max_allowed": 3, "default": 1},
        },
    },

    # ======================================================================
    # ML — UCI Chronic Kidney Disease dataset (158 patients, real data)
    # ======================================================================
    "nephrology": {
        "title": "🫘 Nephrology & Renal Care",
        "category": "Renal",
        "description": "Real machine-learning risk model trained on the UCI Chronic Kidney Disease dataset.",
        "engine": {
            "type": "ml",
            "model_file": "models/kidney_model.pkl",
            "feature_order": ["Age", "DiastolicBP", "SpecificGravity", "Albumin", "Sugar",
                               "BloodGlucoseRandom", "BloodUrea", "SerumCreatinine",
                               "Hemoglobin", "HypertensionHistory", "DiabetesMellitusHistory"],
            "positive_verdict": "🚨 HIGH-RISK PATTERN FOR CHRONIC KIDNEY DISEASE DETECTED",
            "negative_verdict": "✅ LOW-RISK RENAL PROFILE",
        },
        "registry": {
            "DiastolicBP": {"prompt": "Most recent diastolic blood pressure (mmHg)?", "type": "numeric", "min_allowed": 40.0, "max_allowed": 180.0, "default": 80.0},
            "SpecificGravity": {"prompt": "Urinalysis specific gravity (typically 1.005–1.025)?", "type": "numeric", "min_allowed": 1.000, "max_allowed": 1.040, "default": 1.020},
            "Albumin": {"prompt": "Urinalysis albumin grade (0–5, 0 = none detected)?", "type": "numeric", "min_allowed": 0, "max_allowed": 5, "default": 0},
            "Sugar": {"prompt": "Urinalysis glucose grade (0–5, 0 = none detected)?", "type": "numeric", "min_allowed": 0, "max_allowed": 5, "default": 0},
            "BloodGlucoseRandom": {"prompt": "Random blood glucose (mg/dL)?", "type": "numeric", "min_allowed": 40.0, "max_allowed": 600.0, "default": 100.0},
            "BloodUrea": {"prompt": "Blood urea (mg/dL)?", "type": "numeric", "min_allowed": 5.0, "max_allowed": 300.0, "max_optimal": 40.0, "tip": "Elevated blood urea is an early marker of declining nephron clearance.", "default": 30.0},
            "SerumCreatinine": {"prompt": "Serum creatinine (mg/dL)?", "type": "numeric", "min_allowed": 0.2, "max_allowed": 20.0, "max_optimal": 1.2, "tip": "Rising serum creatinine directly reflects falling glomerular filtration rate.", "default": 1.0},
            "Hemoglobin": {"prompt": "Hemoglobin level (g/dL)?", "type": "numeric", "min_allowed": 2.0, "max_allowed": 20.0, "default": 14.0},
            "HypertensionHistory": {"prompt": "Diagnosed history of hypertension? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "DiabetesMellitusHistory": {"prompt": "Diagnosed history of diabetes mellitus? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },

    # ======================================================================
    # ML — Breast Cancer Wisconsin (Diagnostic) dataset, scikit-learn built-in
    # ======================================================================
    "oncology_breast": {
        "title": "🔬 Oncology — Breast Imaging & Cytology",
        "category": "Oncology",
        "description": "Real machine-learning model trained on the Breast Cancer Wisconsin (Diagnostic) dataset, using 10 tumor measurements from a biopsy/imaging report.",
        "engine": {
            "type": "ml",
            "model_file": "models/breast_cancer_model.pkl",
            "feature_order": ["MeanRadius", "MeanTexture", "MeanPerimeter", "MeanArea", "MeanSmoothness",
                               "MeanCompactness", "MeanConcavity", "MeanConcavePoints", "MeanSymmetry",
                               "MeanFractalDimension"],
            "positive_verdict": "🚨 HIGH-RISK PATTERN FOR MALIGNANCY DETECTED — URGENT BIOPSY/SPECIALIST REVIEW INDICATED",
            "negative_verdict": "✅ FEATURES CONSISTENT WITH BENIGN FINDING",
        },
        "registry": {
            "MeanRadius": {"prompt": "Mean tumor cell nucleus radius (from imaging/cytology report)?", "type": "numeric", "min_allowed": 3.0, "max_allowed": 40.0, "default": 14.0},
            "MeanTexture": {"prompt": "Mean nucleus texture (gray-scale value standard deviation)?", "type": "numeric", "min_allowed": 5.0, "max_allowed": 45.0, "default": 19.0},
            "MeanPerimeter": {"prompt": "Mean tumor cell nucleus perimeter?", "type": "numeric", "min_allowed": 20.0, "max_allowed": 220.0, "default": 92.0},
            "MeanArea": {"prompt": "Mean tumor cell nucleus area?", "type": "numeric", "min_allowed": 100.0, "max_allowed": 2600.0, "default": 655.0},
            "MeanSmoothness": {"prompt": "Mean smoothness (local variation in nucleus radius lengths)?", "type": "numeric", "min_allowed": 0.02, "max_allowed": 0.20, "default": 0.096},
            "MeanCompactness": {"prompt": "Mean compactness (perimeter² / area − 1.0)?", "type": "numeric", "min_allowed": 0.0, "max_allowed": 0.40, "default": 0.104},
            "MeanConcavity": {"prompt": "Mean concavity (severity of concave portions of the contour)?", "type": "numeric", "min_allowed": 0.0, "max_allowed": 0.50, "default": 0.089},
            "MeanConcavePoints": {"prompt": "Mean number of concave portions of the contour?", "type": "numeric", "min_allowed": 0.0, "max_allowed": 0.25, "default": 0.048},
            "MeanSymmetry": {"prompt": "Mean symmetry of the tumor cell nucleus?", "type": "numeric", "min_allowed": 0.05, "max_allowed": 0.35, "default": 0.181},
            "MeanFractalDimension": {"prompt": "Mean fractal dimension (\"coastline approximation\" − 1)?", "type": "numeric", "min_allowed": 0.04, "max_allowed": 0.12, "default": 0.063},
        },
    },

    # ======================================================================
    # RULE — Cervical cancer risk factors (ACS/WHO recognized risk factors)
    # ======================================================================
    "oncology_cervical": {
        "title": "🎗️ Oncology — Gynecologic Screening",
        "category": "Oncology",
        "description": "Evidence-based cervical cancer risk-factor scoring (ACS/WHO recognized risk factors). Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "cervical_cancer_risk"},
        "registry": {
            "HPVPositive": {"prompt": "Confirmed positive HPV test? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "AbnormalPapSmear": {"prompt": "Any prior abnormal Pap smear result? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "STDHistory": {"prompt": "History of any sexually transmitted infection? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "LongTermContraceptiveUse": {"prompt": "Oral contraceptive use for 5+ years? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },

    # ======================================================================
    # RULE — APRI score (AST-to-Platelet Ratio Index, Wai et al. 2003)
    # ======================================================================
    "hepatology": {
        "title": "🧪 Hepatology & Liver Care",
        "category": "Hepatic & Digestive",
        "description": "Evidence-based liver fibrosis risk scoring using the validated APRI index (AST-to-Platelet Ratio). Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "liver_disease_risk"},
        "registry": {
            "AST": {"prompt": "Serum AST / SGOT level (U/L)?", "type": "numeric", "min_allowed": 5.0, "max_allowed": 2000.0, "max_optimal": 40.0, "tip": "AST above the normal upper limit (~40 U/L) signals hepatocellular stress.", "default": 25.0},
            "PlateletCount": {"prompt": "Platelet count (×10⁹/L)?", "type": "numeric", "min_allowed": 5.0, "max_allowed": 800.0, "default": 250.0},
            "TotalBilirubin": {"prompt": "Total bilirubin (mg/dL)?", "type": "numeric", "min_allowed": 0.1, "max_allowed": 40.0, "max_optimal": 1.2, "tip": "Bilirubin above 1.2 mg/dL suggests impaired hepatic clearance or excretion.", "default": 0.8},
            "Albumin": {"prompt": "Serum albumin (g/dL)?", "type": "numeric", "min_allowed": 1.0, "max_allowed": 6.0, "default": 4.2},
        },
    },

    # ======================================================================
    # RULE — GOLD criteria for airflow obstruction (COPD/asthma pattern)
    # ======================================================================
    "pulmonology": {
        "title": "🫁 Pulmonology & Respiratory Care",
        "category": "Respiratory",
        "description": "Evidence-based airway obstruction staging using GOLD spirometry criteria. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "copd_asthma_risk"},
        "registry": {
            "FEV1FVCRatio": {"prompt": "Post-bronchodilator FEV1/FVC ratio from spirometry?", "type": "numeric", "min_allowed": 0.2, "max_allowed": 1.0, "default": 0.80},
            "FEV1PercentPredicted": {"prompt": "FEV1 as a percentage of predicted normal value?", "type": "numeric", "min_allowed": 10.0, "max_allowed": 130.0, "default": 90.0},
            "ChronicCough": {"prompt": "Chronic cough present (3+ months)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "Wheezing": {"prompt": "Recurrent wheezing episodes? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },

    # ======================================================================
    # RULE — CHA2DS2-VASc stroke risk score (real validated clinical tool)
    # ======================================================================
    "neurology_stroke": {
        "title": "🧠 Neurology — Cerebrovascular Risk",
        "category": "Neurological",
        "description": "Evidence-based stroke risk stratification using the validated CHA₂DS₂-VASc score. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "stroke_risk_chadsvasc"},
        "registry": {
            "CongestiveHeartFailureHistory": {"prompt": "History of congestive heart failure? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "HypertensionHistory": {"prompt": "Diagnosed history of hypertension? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "DiabetesMellitusHistory": {"prompt": "Diagnosed history of diabetes mellitus? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "PriorStrokeOrTIA": {"prompt": "Prior stroke or transient ischemic attack (TIA)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "VascularDiseaseHistory": {"prompt": "History of vascular disease (prior MI, peripheral artery disease, or aortic plaque)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },

    # ======================================================================
    # RULE — qSOFA (quick Sequential Organ Failure Assessment, Sepsis-3, 2016)
    # ======================================================================
    "infectious_disease": {
        "title": "🦠 Infectious Disease & Critical Care",
        "category": "Infectious & Critical Care",
        "description": "Evidence-based sepsis risk screening using the validated qSOFA score (Sepsis-3 criteria). Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "sepsis_risk_qsofa"},
        "registry": {
            "RespiratoryRate": {"prompt": "Respiratory rate (breaths per minute)?", "type": "numeric", "min_allowed": 6.0, "max_allowed": 60.0, "default": 16.0},
            "AlteredMentalStatus": {"prompt": "Any new alteration in mental status (confusion, reduced responsiveness)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },

    # ======================================================================
    # RULE — Simplified 2010 ACR/EULAR rheumatoid arthritis classification
    # ======================================================================
    "rheumatology": {
        "title": "🔥 Rheumatology & Autoimmune Care",
        "category": "Musculoskeletal & Autoimmune",
        "description": "Evidence-based inflammatory arthritis risk scoring based on 2010 ACR/EULAR classification components. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "rheumatoid_arthritis_risk"},
        "registry": {
            "AffectedJointCount": {"prompt": "Number of swollen or tender joints currently affected?", "type": "numeric", "min_allowed": 0, "max_allowed": 50, "default": 0},
            "SymptomDurationWeeks": {"prompt": "Duration of joint symptoms (weeks)?", "type": "numeric", "min_allowed": 0, "max_allowed": 520, "default": 1},
            "SeropositiveRForACPA": {"prompt": "Positive rheumatoid factor (RF) or anti-CCP/ACPA antibody test? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "ElevatedCRPorESR": {"prompt": "Elevated CRP or ESR (inflammatory markers)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },

    # ======================================================================
    # RULE — PHQ-9 depression screening (real validated 9-item instrument)
    # ======================================================================
    "psychiatry": {
        "title": "💭 Psychiatry & Behavioral Health",
        "category": "Mental Health",
        "description": "PHQ-9, a real validated 9-item depression screening instrument used widely in primary care. Not a machine-learning model. Educational/screening use only — not a diagnosis.",
        "engine": {"type": "rule", "rule_fn": "depression_screen_phq9"},
        "registry": {
            "PHQ_Interest": {"prompt": "Over the last 2 weeks, how often has the patient had little interest or pleasure in doing things? (0=not at all, 1=several days, 2=more than half the days, 3=nearly every day)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
            "PHQ_Mood": {"prompt": "How often feeling down, depressed, or hopeless? (0–3 scale as above)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
            "PHQ_Sleep": {"prompt": "How often trouble falling/staying asleep, or sleeping too much? (0–3 scale)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
            "PHQ_Fatigue": {"prompt": "How often feeling tired or having little energy? (0–3 scale)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
            "PHQ_Appetite": {"prompt": "How often poor appetite or overeating? (0–3 scale)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
            "PHQ_SelfWorth": {"prompt": "How often feeling bad about themselves, or like a failure? (0–3 scale)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
            "PHQ_Concentration": {"prompt": "How often trouble concentrating on things? (0–3 scale)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
            "PHQ_Psychomotor": {"prompt": "How often moving/speaking noticeably slower, or unusually fidgety/restless? (0–3 scale)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
            "PHQ_SelfHarmThoughts": {"prompt": "How often thoughts of self-harm or that they would be better off dead? (0–3 scale)", "type": "numeric", "min_allowed": 0, "max_allowed": 3, "default": 0},
        },
    },

    # ======================================================================
    # RULE — Thyroid function classification using standard reference ranges
    # ======================================================================
    "endocrinology_thyroid": {
        "title": "🦋 Endocrinology — Thyroid Care",
        "category": "Endocrine & Metabolic",
        "description": "Evidence-based thyroid function classification using standard TSH/Free T4 reference ranges. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "thyroid_function_assessment"},
        "registry": {
            "TSH": {"prompt": "Serum TSH level (mIU/L)?", "type": "numeric", "min_allowed": 0.001, "max_allowed": 100.0, "default": 2.0},
            "FreeT4": {"prompt": "Free T4 level (ng/dL)?", "type": "numeric", "min_allowed": 0.1, "max_allowed": 10.0, "default": 1.2},
            "SymptomaticThyroid": {"prompt": "Any thyroid-related symptoms present (fatigue, weight change, palpitations, temperature intolerance)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },

    # ======================================================================
    # RULE — WHO anemia diagnostic criteria
    # ======================================================================
    "hematology": {
        "title": "🩸 Hematology",
        "category": "Hematologic",
        "description": "Evidence-based anemia classification using WHO hemoglobin diagnostic thresholds. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "anemia_classification_who"},
        "registry": {
            "Hemoglobin": {"prompt": "Hemoglobin level (g/dL)?", "type": "numeric", "min_allowed": 2.0, "max_allowed": 20.0, "default": 14.0},
            "MCV": {"prompt": "Mean corpuscular volume / MCV (fL)?", "type": "numeric", "min_allowed": 50.0, "max_allowed": 130.0, "default": 90.0},
        },
    },

    # ======================================================================
    # RULE — ABCDE criteria for melanoma risk (real dermatologic mnemonic)
    # ======================================================================
    "dermatology": {
        "title": "🩹 Dermatology — Skin Lesion Screening",
        "category": "Dermatologic",
        "description": "Evidence-based melanoma risk screening using the validated ABCDE clinical criteria. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "melanoma_risk_abcde"},
        "registry": {
            "AsymmetricShape": {"prompt": "Is the lesion asymmetric (one half doesn't match the other)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "IrregularBorder": {"prompt": "Are the lesion borders irregular, scalloped, or poorly defined? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "ColorVariation": {"prompt": "Does the lesion have varied coloring (multiple shades of brown/black/red/white/blue)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "LesionDiameterMM": {"prompt": "Lesion diameter (mm)?", "type": "numeric", "min_allowed": 0.5, "max_allowed": 80.0, "max_optimal": 6.0, "tip": "Diameters over 6mm (about a pencil eraser) are a recognized melanoma warning sign.", "default": 3.0},
            "RecentEvolutionChange": {"prompt": "Has the lesion recently changed in size, shape, or color? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },

    # ======================================================================
    # RULE — Simplified LUTS/BPH screening + PSA threshold
    # ======================================================================
    "urology": {
        "title": "💧 Urology",
        "category": "Genitourinary",
        "description": "Evidence-based lower urinary tract symptom screening with standard PSA threshold flagging. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "lower_urinary_tract_risk"},
        "registry": {
            "NocturiaFrequency": {"prompt": "Typical number of times waking at night to urinate?", "type": "numeric", "min_allowed": 0, "max_allowed": 15, "default": 1},
            "WeakUrineStream": {"prompt": "Noticeably weak or interrupted urine stream? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "PSALevel": {"prompt": "Serum PSA level (ng/mL)?", "type": "numeric", "min_allowed": 0.0, "max_allowed": 100.0, "max_optimal": 4.0, "tip": "PSA above 4.0 ng/mL is a traditional threshold prompting further urologic workup.", "default": 1.0},
        },
    },

    # ======================================================================
    # RULE — Diabetic retinopathy risk factors (DCCT/UKPDS literature)
    # ======================================================================
    "ophthalmology": {
        "title": "👁️ Ophthalmology — Diabetic Retinopathy",
        "category": "Ophthalmic",
        "description": "Evidence-based diabetic retinopathy risk factors drawn from the DCCT/UKPDS landmark studies. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "diabetic_retinopathy_risk"},
        "registry": {
            "DiabetesDurationYears": {"prompt": "Years since diabetes diagnosis?", "type": "numeric", "min_allowed": 0.0, "max_allowed": 70.0, "default": 0.0},
            "HbA1c": {"prompt": "Most recent HbA1c (%)?", "type": "numeric", "min_allowed": 3.5, "max_allowed": 18.0, "max_optimal": 7.0, "tip": "HbA1c sustained above 7% accelerates microvascular retinal damage.", "default": 5.5},
        },
    },

    # ======================================================================
    # RULE — Simplified FRAX-like osteoporosis risk factors
    # ======================================================================
    "orthopedics": {
        "title": "🦴 Orthopedics — Bone Health",
        "category": "Musculoskeletal & Autoimmune",
        "description": "Evidence-based osteoporotic fracture risk factors modeled on the FRAX clinical risk tool. Not a machine-learning model.",
        "engine": {"type": "rule", "rule_fn": "osteoporosis_risk_frax_like"},
        "registry": {
            "PriorFractureHistory": {"prompt": "Any prior fragility fracture (low-trauma break) as an adult? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "FamilyHistoryHipFracture": {"prompt": "Parental history of hip fracture? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
            "LongTermSteroidUse": {"prompt": "Long-term oral corticosteroid use (3+ months)? (yes/no)", "type": "choice", "choices": ["yes", "no"], "default": "no"},
        },
    },
}
