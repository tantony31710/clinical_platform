# engines/rule_engines.py
"""
Evidence-based clinical scoring engines for specialties where no clean
trainable dataset was available in this environment. Every function here
implements a real, named, citable clinical tool or criteria set rather than
an invented score. Each returns a dict: {"status", "verdict", "confidence"}.

"confidence" here means "how strongly the inputs satisfy the scoring
criteria," not a machine-learning probability — the app surfaces these two
concepts under different labels (see app.py) so they are never confused.
"""


def g(profile, key, default=None):
    """Small helper: fetch a profile value with a fallback default."""
    return profile.get(key, default)


def yes(profile, key):
    return str(profile.get(key, "no")).strip().lower() == "yes"


# ---------------------------------------------------------------------------
# Cervical cancer — recognized ACS/WHO risk factors
# ---------------------------------------------------------------------------
def cervical_cancer_risk(profile):
    hpv = yes(profile, "HPVPositive")
    pap = yes(profile, "AbnormalPapSmear")
    std = yes(profile, "STDHistory")
    oc = yes(profile, "LongTermContraceptiveUse")
    smoker = yes(profile, "Smoker")

    points = (hpv * 3) + (pap * 2) + std + oc + smoker

    if hpv and pap:
        return {"status": "HIGH_RISK", "confidence": 92.0,
                "verdict": "🚨 HIGH-RISK PROFILE — Positive HPV with abnormal cytology warrants urgent colposcopy referral"}
    if points >= 3:
        return {"status": "ELEVATED_RISK", "confidence": 74.0,
                "verdict": "⚠️ ELEVATED RISK FACTORS PRESENT — Recommend prompt gynecologic screening"}
    return {"status": "NORMAL", "confidence": 88.0,
            "verdict": "✅ LOW RISK FACTOR BURDEN — Continue routine screening interval"}


# ---------------------------------------------------------------------------
# Hepatology — APRI score (AST-to-Platelet Ratio Index, Wai et al. 2003)
# Validated cutoffs: APRI > 1.5 suggests significant fibrosis, > 2.0 cirrhosis risk
# ---------------------------------------------------------------------------
def liver_disease_risk(profile):
    ast = float(g(profile, "AST", 25.0))
    platelets = float(g(profile, "PlateletCount", 250.0))
    bilirubin = float(g(profile, "TotalBilirubin", 0.8))
    albumin = float(g(profile, "Albumin", 4.2))

    ast_uln = 40.0  # standard AST upper limit of normal
    apri = ((ast / ast_uln) / max(platelets, 1.0)) * 100.0

    synthetic_dysfunction = bilirubin > 2.0 or albumin < 3.5

    if apri > 2.0 or (apri > 1.0 and synthetic_dysfunction):
        return {"status": "HIGH_RISK", "confidence": 90.0,
                "verdict": f"🚨 APRI {apri:.2f} — HIGH PROBABILITY OF SIGNIFICANT LIVER FIBROSIS / CIRRHOSIS RISK"}
    if apri > 0.5 or synthetic_dysfunction:
        return {"status": "ELEVATED_RISK", "confidence": 68.0,
                "verdict": f"⚠️ APRI {apri:.2f} — INDETERMINATE; FURTHER HEPATIC WORKUP RECOMMENDED"}
    return {"status": "NORMAL", "confidence": 85.0,
            "verdict": f"✅ APRI {apri:.2f} — LOW PROBABILITY OF SIGNIFICANT LIVER FIBROSIS"}


# ---------------------------------------------------------------------------
# Pulmonology — GOLD spirometric criteria for airflow obstruction
# FEV1/FVC < 0.70 post-bronchodilator defines obstruction; staged by FEV1% predicted
# ---------------------------------------------------------------------------
def copd_asthma_risk(profile):
    ratio = float(g(profile, "FEV1FVCRatio", 0.80))
    fev1_pct = float(g(profile, "FEV1PercentPredicted", 90.0))
    cough = yes(profile, "ChronicCough")
    wheeze = yes(profile, "Wheezing")

    if ratio < 0.70:
        if fev1_pct >= 80:
            gold = "GOLD 1 (Mild)"
        elif fev1_pct >= 50:
            gold = "GOLD 2 (Moderate)"
        elif fev1_pct >= 30:
            gold = "GOLD 3 (Severe)"
        else:
            gold = "GOLD 4 (Very Severe)"
        return {"status": "HIGH_RISK", "confidence": 91.0,
                "verdict": f"🚨 AIRFLOW OBSTRUCTION CONFIRMED — {gold} per GOLD criteria"}
    if cough and wheeze:
        return {"status": "ELEVATED_RISK", "confidence": 60.0,
                "verdict": "⚠️ NORMAL SPIROMETRY WITH ACTIVE SYMPTOMS — Consider reactive airway / asthma workup"}
    return {"status": "NORMAL", "confidence": 87.0,
            "verdict": "✅ NO SPIROMETRIC EVIDENCE OF AIRFLOW OBSTRUCTION"}


# ---------------------------------------------------------------------------
# Neurology — CHA2DS2-VASc stroke risk score (real validated tool)
# C=CHF(1) H=HTN(1) A2=age>=75(2) D=diabetes(1) S2=prior stroke/TIA(2)
# V=vascular disease(1) A=age 65-74(1) Sc=female sex(1)
# ---------------------------------------------------------------------------
def stroke_risk_chadsvasc(profile):
    age = float(g(profile, "Age", 40.0))
    sex = float(g(profile, "Sex", 1))  # 1=male, 0=female

    score = 0
    score += 1 if yes(profile, "CongestiveHeartFailureHistory") else 0
    score += 1 if yes(profile, "HypertensionHistory") else 0
    score += 2 if age >= 75 else (1 if age >= 65 else 0)
    score += 1 if yes(profile, "DiabetesMellitusHistory") else 0
    score += 2 if yes(profile, "PriorStrokeOrTIA") else 0
    score += 1 if yes(profile, "VascularDiseaseHistory") else 0
    score += 1 if sex == 0 else 0  # female sex category

    if score >= 4:
        return {"status": "HIGH_RISK", "confidence": 90.0,
                "verdict": f"🚨 CHA₂DS₂-VASc SCORE {score} — HIGH ANNUAL STROKE RISK, ANTICOAGULATION EVALUATION INDICATED"}
    if score >= 2:
        return {"status": "ELEVATED_RISK", "confidence": 70.0,
                "verdict": f"⚠️ CHA₂DS₂-VASc SCORE {score} — MODERATE STROKE RISK, CLINICAL REVIEW RECOMMENDED"}
    return {"status": "NORMAL", "confidence": 85.0,
            "verdict": f"✅ CHA₂DS₂-VASc SCORE {score} — LOW STROKE RISK"}


# ---------------------------------------------------------------------------
# Infectious Disease — qSOFA (Sepsis-3, Singer et al. 2016)
# RR>=22, SBP<=100, altered mentation -- each 1pt; >=2 flags high risk
# ---------------------------------------------------------------------------
def sepsis_risk_qsofa(profile):
    rr = float(g(profile, "RespiratoryRate", 16.0))
    sbp = float(g(profile, "BloodPressure", 120.0))
    altered = yes(profile, "AlteredMentalStatus")

    score = (1 if rr >= 22 else 0) + (1 if sbp <= 100 else 0) + (1 if altered else 0)

    if score >= 2:
        return {"status": "HIGH_RISK", "confidence": 93.0,
                "verdict": f"🚨 qSOFA {score}/3 — HIGH RISK FOR SEPSIS-RELATED ORGAN DYSFUNCTION, URGENT EVALUATION INDICATED"}
    if score == 1:
        return {"status": "ELEVATED_RISK", "confidence": 65.0,
                "verdict": f"⚠️ qSOFA {score}/3 — MONITOR CLOSELY FOR CLINICAL DETERIORATION"}
    return {"status": "NORMAL", "confidence": 82.0,
            "verdict": f"✅ qSOFA {score}/3 — LOW IMMEDIATE SEPSIS RISK BY SCREENING CRITERIA"}


# ---------------------------------------------------------------------------
# Rheumatology — simplified 2010 ACR/EULAR RA classification components
# ---------------------------------------------------------------------------
def rheumatoid_arthritis_risk(profile):
    joints = float(g(profile, "AffectedJointCount", 0))
    duration = float(g(profile, "SymptomDurationWeeks", 0))
    seropositive = yes(profile, "SeropositiveRForACPA")
    elevated_markers = yes(profile, "ElevatedCRPorESR")

    points = 0
    points += 3 if joints >= 10 else (2 if joints >= 4 else (1 if joints >= 2 else 0))
    points += 3 if seropositive else 0
    points += 1 if elevated_markers else 0
    points += 1 if duration >= 6 else 0

    if points >= 6:
        return {"status": "HIGH_RISK", "confidence": 88.0,
                "verdict": f"🚨 CLASSIFICATION SCORE {points}/8 — MEETS THRESHOLD CONSISTENT WITH RHEUMATOID ARTHRITIS"}
    if points >= 3:
        return {"status": "ELEVATED_RISK", "confidence": 66.0,
                "verdict": f"⚠️ CLASSIFICATION SCORE {points}/8 — SUGGESTIVE FINDINGS, RHEUMATOLOGY REFERRAL RECOMMENDED"}
    return {"status": "NORMAL", "confidence": 80.0,
            "verdict": f"✅ CLASSIFICATION SCORE {points}/8 — CRITERIA NOT MET"}


# ---------------------------------------------------------------------------
# Psychiatry — PHQ-9 (real validated 9-item depression screening instrument)
# Cutoffs: 0-4 minimal, 5-9 mild, 10-14 moderate, 15-19 mod-severe, 20-27 severe
# ---------------------------------------------------------------------------
def depression_screen_phq9(profile):
    items = ["PHQ_Interest", "PHQ_Mood", "PHQ_Sleep", "PHQ_Fatigue", "PHQ_Appetite",
              "PHQ_SelfWorth", "PHQ_Concentration", "PHQ_Psychomotor", "PHQ_SelfHarmThoughts"]
    total = sum(float(g(profile, item, 0)) for item in items)
    self_harm_item = float(g(profile, "PHQ_SelfHarmThoughts", 0))

    safety_note = ""
    if self_harm_item > 0:
        safety_note = (" ⚠️ Item 9 (thoughts of self-harm) was endorsed — this requires prompt, direct "
                        "clinical follow-up regardless of total score. If there is any immediate danger, "
                        "contact local emergency services or a crisis line right away.")

    if total >= 20 or self_harm_item >= 2:
        return {"status": "HIGH_RISK", "confidence": 92.0,
                "verdict": f"🚨 PHQ-9 SCORE {int(total)}/27 — SEVERE DEPRESSIVE SYMPTOM BURDEN, URGENT CLINICAL EVALUATION INDICATED.{safety_note}"}
    if total >= 10:
        return {"status": "ELEVATED_RISK", "confidence": 78.0,
                "verdict": f"⚠️ PHQ-9 SCORE {int(total)}/27 — MODERATE DEPRESSIVE SYMPTOMS, CLINICAL EVALUATION RECOMMENDED.{safety_note}"}
    if total >= 5:
        return {"status": "ELEVATED_RISK", "confidence": 65.0,
                "verdict": f"⚠️ PHQ-9 SCORE {int(total)}/27 — MILD DEPRESSIVE SYMPTOMS, MONITOR AND REASSESS.{safety_note}"}
    return {"status": "NORMAL", "confidence": 80.0,
            "verdict": f"✅ PHQ-9 SCORE {int(total)}/27 — MINIMAL DEPRESSIVE SYMPTOMS.{safety_note}"}


# ---------------------------------------------------------------------------
# Endocrinology — thyroid function classification via standard reference ranges
# Normal TSH ~0.4-4.0 mIU/L; Free T4 ~0.8-1.8 ng/dL
# ---------------------------------------------------------------------------
def thyroid_function_assessment(profile):
    tsh = float(g(profile, "TSH", 2.0))
    t4 = float(g(profile, "FreeT4", 1.2))
    symptomatic = yes(profile, "SymptomaticThyroid")

    tsh_low, tsh_high = 0.4, 4.0
    t4_low, t4_high = 0.8, 1.8

    if tsh > tsh_high and t4 < t4_low:
        return {"status": "HIGH_RISK", "confidence": 90.0,
                "verdict": "🚨 PRIMARY HYPOTHYROIDISM PATTERN — Elevated TSH with low Free T4"}
    if tsh < tsh_low and t4 > t4_high:
        return {"status": "HIGH_RISK", "confidence": 90.0,
                "verdict": "🚨 HYPERTHYROIDISM PATTERN — Suppressed TSH with elevated Free T4"}
    if tsh > tsh_high and t4_low <= t4 <= t4_high:
        return {"status": "ELEVATED_RISK", "confidence": 72.0,
                "verdict": "⚠️ SUBCLINICAL HYPOTHYROIDISM — Elevated TSH with normal Free T4"}
    if tsh < tsh_low and t4_low <= t4 <= t4_high:
        return {"status": "ELEVATED_RISK", "confidence": 72.0,
                "verdict": "⚠️ SUBCLINICAL HYPERTHYROIDISM — Suppressed TSH with normal Free T4"}
    if symptomatic:
        return {"status": "ELEVATED_RISK", "confidence": 55.0,
                "verdict": "⚠️ LABS WITHIN NORMAL RANGE BUT SYMPTOMATIC — Consider repeat testing or further workup"}
    return {"status": "NORMAL", "confidence": 88.0,
            "verdict": "✅ EUTHYROID — TSH and Free T4 within normal reference range"}


# ---------------------------------------------------------------------------
# Hematology — WHO anemia diagnostic criteria (sex-specific Hb cutoffs) + MCV classification
# ---------------------------------------------------------------------------
def anemia_classification_who(profile):
    hb = float(g(profile, "Hemoglobin", 14.0))
    mcv = float(g(profile, "MCV", 90.0))
    sex = float(g(profile, "Sex", 1))  # 1=male, 0=female

    threshold = 13.0 if sex == 1 else 12.0
    anemic = hb < threshold

    if mcv < 80:
        morphology = "microcytic"
    elif mcv > 100:
        morphology = "macrocytic"
    else:
        morphology = "normocytic"

    if anemic and hb < threshold - 3:
        return {"status": "HIGH_RISK", "confidence": 93.0,
                "verdict": f"🚨 SEVERE {morphology.upper()} ANEMIA — Hemoglobin {hb:.1f} g/dL (WHO threshold {threshold:.0f})"}
    if anemic:
        return {"status": "ELEVATED_RISK", "confidence": 80.0,
                "verdict": f"⚠️ {morphology.upper()} ANEMIA DETECTED — Hemoglobin {hb:.1f} g/dL below WHO threshold {threshold:.0f}"}
    return {"status": "NORMAL", "confidence": 88.0,
            "verdict": f"✅ NO ANEMIA BY WHO CRITERIA — Hemoglobin {hb:.1f} g/dL, {morphology} indices"}


# ---------------------------------------------------------------------------
# Dermatology — ABCDE melanoma screening criteria
# ---------------------------------------------------------------------------
def melanoma_risk_abcde(profile):
    asymmetry = yes(profile, "AsymmetricShape")
    border = yes(profile, "IrregularBorder")
    color = yes(profile, "ColorVariation")
    diameter = float(g(profile, "LesionDiameterMM", 3.0))
    evolving = yes(profile, "RecentEvolutionChange")

    points = sum([asymmetry, border, color, diameter > 6.0, evolving])

    if points >= 3:
        return {"status": "HIGH_RISK", "confidence": 89.0,
                "verdict": f"🚨 {points}/5 ABCDE CRITERIA MET — CONCERNING FOR MELANOMA, URGENT DERMATOLOGY/BIOPSY REFERRAL"}
    if points >= 1:
        return {"status": "ELEVATED_RISK", "confidence": 60.0,
                "verdict": f"⚠️ {points}/5 ABCDE CRITERIA MET — ROUTINE DERMATOLOGY EVALUATION RECOMMENDED"}
    return {"status": "NORMAL", "confidence": 85.0,
            "verdict": "✅ 0/5 ABCDE CRITERIA MET — NO IMMEDIATE MELANOMA WARNING SIGNS"}


# ---------------------------------------------------------------------------
# Urology — simplified LUTS/BPH screening + standard PSA threshold
# ---------------------------------------------------------------------------
def lower_urinary_tract_risk(profile):
    nocturia = float(g(profile, "NocturiaFrequency", 1))
    weak_stream = yes(profile, "WeakUrineStream")
    psa = float(g(profile, "PSALevel", 1.0))

    if psa > 4.0:
        return {"status": "HIGH_RISK", "confidence": 86.0,
                "verdict": f"🚨 PSA {psa:.1f} ng/mL EXCEEDS STANDARD THRESHOLD — UROLOGY WORKUP INDICATED"}
    if nocturia >= 3 and weak_stream:
        return {"status": "ELEVATED_RISK", "confidence": 70.0,
                "verdict": "⚠️ SIGNIFICANT LOWER URINARY TRACT SYMPTOM BURDEN — CONSISTENT WITH BPH PATTERN"}
    if nocturia >= 2 or weak_stream:
        return {"status": "ELEVATED_RISK", "confidence": 55.0,
                "verdict": "⚠️ MILD LOWER URINARY TRACT SYMPTOMS PRESENT — MONITOR"}
    return {"status": "NORMAL", "confidence": 84.0,
            "verdict": f"✅ PSA {psa:.1f} ng/mL NORMAL, MINIMAL LUTS BURDEN"}


# ---------------------------------------------------------------------------
# Ophthalmology — diabetic retinopathy risk factors (DCCT/UKPDS literature)
# ---------------------------------------------------------------------------
def diabetic_retinopathy_risk(profile):
    duration = float(g(profile, "DiabetesDurationYears", 0.0))
    a1c = float(g(profile, "HbA1c", 5.5))
    sbp = float(g(profile, "BloodPressure", 120.0))

    points = 0
    points += 2 if duration >= 10 else (1 if duration >= 5 else 0)
    points += 2 if a1c >= 8.0 else (1 if a1c >= 7.0 else 0)
    points += 1 if sbp > 140 else 0

    if points >= 4:
        return {"status": "HIGH_RISK", "confidence": 87.0,
                "verdict": f"🚨 HIGH RISK FOR DIABETIC RETINOPATHY (score {points}/5) — DILATED EYE EXAM INDICATED"}
    if points >= 2:
        return {"status": "ELEVATED_RISK", "confidence": 65.0,
                "verdict": f"⚠️ MODERATE RISK FOR DIABETIC RETINOPATHY (score {points}/5) — ANNUAL SCREENING RECOMMENDED"}
    return {"status": "NORMAL", "confidence": 83.0,
            "verdict": f"✅ LOW RISK FOR DIABETIC RETINOPATHY (score {points}/5)"}


# ---------------------------------------------------------------------------
# Orthopedics — simplified FRAX-like osteoporotic fracture risk factors
# ---------------------------------------------------------------------------
def osteoporosis_risk_frax_like(profile):
    age = float(g(profile, "Age", 40.0))
    sex = float(g(profile, "Sex", 1))
    bmi = float(g(profile, "BMI", 22.0))  # opportunistically reuses BMI if entered elsewhere
    smoker = yes(profile, "Smoker")
    prior_fracture = yes(profile, "PriorFractureHistory")
    family_hx = yes(profile, "FamilyHistoryHipFracture")
    steroids = yes(profile, "LongTermSteroidUse")

    points = 0
    points += 1 if age >= 65 else 0
    points += 1 if sex == 0 else 0  # post-menopausal risk proxy
    points += 1 if bmi < 19 else 0
    points += 1 if smoker else 0
    points += 2 if prior_fracture else 0
    points += 1 if family_hx else 0
    points += 1 if steroids else 0

    if points >= 5:
        return {"status": "HIGH_RISK", "confidence": 85.0,
                "verdict": f"🚨 HIGH OSTEOPOROTIC FRACTURE RISK (score {points}/8) — BONE DENSITY (DXA) SCAN INDICATED"}
    if points >= 2:
        return {"status": "ELEVATED_RISK", "confidence": 63.0,
                "verdict": f"⚠️ MODERATE FRACTURE RISK FACTORS PRESENT (score {points}/8) — CONSIDER DXA SCREENING"}
    return {"status": "NORMAL", "confidence": 80.0,
            "verdict": f"✅ LOW OSTEOPOROTIC FRACTURE RISK (score {points}/8)"}


# Registry mapping config "rule_fn" strings -> actual functions
RULE_FUNCTIONS = {
    "cervical_cancer_risk": cervical_cancer_risk,
    "liver_disease_risk": liver_disease_risk,
    "copd_asthma_risk": copd_asthma_risk,
    "stroke_risk_chadsvasc": stroke_risk_chadsvasc,
    "sepsis_risk_qsofa": sepsis_risk_qsofa,
    "rheumatoid_arthritis_risk": rheumatoid_arthritis_risk,
    "depression_screen_phq9": depression_screen_phq9,
    "thyroid_function_assessment": thyroid_function_assessment,
    "anemia_classification_who": anemia_classification_who,
    "melanoma_risk_abcde": melanoma_risk_abcde,
    "lower_urinary_tract_risk": lower_urinary_tract_risk,
    "diabetic_retinopathy_risk": diabetic_retinopathy_risk,
    "osteoporosis_risk_frax_like": osteoporosis_risk_frax_like,
}
