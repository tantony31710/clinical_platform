# config/advice.py
"""
Per-specialty, per-status clinical advice shown in the exported report.
Keys match SPECIALTY_FIELDS keys. Each status key maps to a list of
actionable advice bullets. Written for a clinician-review context --
not direct patient instructions.
"""

SPECIALTY_ADVICE = {
    "metabolic": {
        "HIGH_RISK": [
            "Arrange fasting plasma glucose and HbA1c confirmation within 1 week.",
            "Calculate FINDRISC or ADA risk score for formal diabetes risk stratification.",
            "Initiate structured lifestyle intervention: target ≥150 min/week moderate aerobic activity and ≥5–7% weight reduction if BMI > 25.",
            "Evaluate for metabolic syndrome: check lipid panel, waist circumference, BP trend.",
            "Consider metformin if confirmed pre-diabetes (ADA guidelines) and lifestyle alone insufficient.",
            "Refer to endocrinology or diabetes educator if HbA1c ≥ 7% at confirmation.",
        ],
        "ELEVATED_RISK": [
            "Confirm with fasting glucose repeat; rule out stress hyperglycaemia.",
            "Advise dietary modification: reduce refined carbohydrates, increase fibre.",
            "Reassess in 3–6 months with repeat glucose and BMI.",
        ],
        "INDETERMINATE": [
            "Borderline model confidence — do not act on this result alone.",
            "Repeat fasting glucose and check HbA1c for a direct biochemical result.",
        ],
        "NORMAL": [
            "No immediate intervention required. Continue routine annual screening per local guidelines.",
            "Reinforce healthy weight, activity, and low-sugar diet preventively.",
        ],
    },
    "cardio": {
        "HIGH_RISK": [
            "Arrange urgent 12-lead ECG if not recently done; consider same-day cardiology review.",
            "Initiate or optimise antiplatelet, statin, and antihypertensive therapy per local guidelines (e.g. ACC/AHA).",
            "Calculate HEART or TIMI score for chest-pain risk stratification if symptomatic.",
            "Order troponin (high-sensitivity), BNP/NT-proBNP, and comprehensive lipid panel.",
            "Discuss coronary angiography or stress testing referral with supervising cardiologist.",
            "Advise strict smoking cessation, sodium restriction (<2 g/day), and supervised cardiac rehab.",
        ],
        "ELEVATED_RISK": [
            "Order lipid panel and assess 10-year ASCVD risk (Pooled Cohort Equations).",
            "Optimise blood pressure to < 130/80 mmHg; consider ACE-I or ARB if diabetic.",
            "Lifestyle counselling: Mediterranean diet, aerobic exercise ≥ 150 min/week.",
            "Repeat risk assessment in 6–12 months.",
        ],
        "INDETERMINATE": [
            "Borderline result — correlate with clinical symptoms and physical exam.",
            "Consider stress echocardiogram or calcium scoring (CAC) for additional stratification.",
        ],
        "NORMAL": [
            "Maintain current healthy lifestyle. Reassess cardiovascular risk every 4–6 years or if new symptoms arise.",
        ],
    },
    "nephrology": {
        "HIGH_RISK": [
            "Confirm eGFR with CKD-EPI equation using repeat serum creatinine (two measures ≥ 3 months apart per KDIGO).",
            "Quantify proteinuria: spot urine ACR; persistent ACR > 30 mg/g warrants nephrology referral.",
            "Strict BP control: target < 130/80 mmHg; first-line ACE-I or ARB in proteinuric CKD.",
            "Optimise glycaemic control if diabetic (HbA1c target ~7%).",
            "Review and renally-dose all medications; avoid NSAIDs and nephrotoxic agents.",
            "Monitor electrolytes, bicarbonate, phosphate, PTH, Hb for CKD complications.",
            "Refer nephrology if eGFR < 30 or rapidly declining (> 5 mL/min/year).",
        ],
        "ELEVATED_RISK": [
            "Repeat eGFR in 3 months. Check urine ACR and urinalysis.",
            "Ensure BP is controlled; add RAS blockade if proteinuric.",
            "Encourage high fluid intake (unless contraindicated), low-sodium diet.",
        ],
        "INDETERMINATE": [
            "Repeat creatinine and eGFR after adequate hydration to rule out acute pre-renal component.",
        ],
        "NORMAL": [
            "No immediate renal concern. Annual eGFR and urine ACR for high-risk patients (diabetic, hypertensive).",
        ],
    },
    "oncology_breast": {
        "HIGH_RISK": [
            "⚠️ This is a screening-support tool — a HIGH result does NOT constitute a cancer diagnosis.",
            "Refer urgently to a breast surgeon or oncology MDT for clinical breast examination and imaging review.",
            "Ensure diagnostic mammography and/or ultrasound is performed or reviewed.",
            "If not already done, arrange core needle biopsy per imaging-guided protocol.",
            "Assess family history for BRCA1/2 genetic counselling eligibility.",
            "Do not communicate a 'cancer diagnosis' based solely on this tool output.",
        ],
        "ELEVATED_RISK": [
            "Ensure up-to-date mammography screening (annual from age 40 or earlier if family history).",
            "Clinical breast examination by a physician; discuss any palpable changes.",
        ],
        "INDETERMINATE": [
            "Borderline cytology features — requires direct pathologist and radiologist review, not algorithmic triage.",
        ],
        "NORMAL": [
            "Findings consistent with benign features. Continue recommended screening interval.",
            "Reassess if new palpable mass, skin change, nipple discharge, or pain develops.",
        ],
    },
    "oncology_cervical": {
        "HIGH_RISK": [
            "Urgent referral for colposcopy (within 4 weeks per NHSCSP / ASCCP guidelines).",
            "Confirm HPV status with validated reflex HPV testing if not already done.",
            "Counsel on HPV vaccination status; offer if eligible (up to age 45 in many guidelines).",
            "Reinforce condom use and smoking cessation (smoking independently increases cervical cancer risk).",
        ],
        "ELEVATED_RISK": [
            "Ensure cervical screening (Pap smear or primary HPV test) is current.",
            "Advise on HPV vaccination if not previously received.",
            "Repeat screening in 12 months or per local protocol.",
        ],
        "NORMAL": [
            "Continue routine cervical screening at guideline-recommended intervals (every 3–5 years with HPV co-test).",
        ],
    },
    "hepatology": {
        "HIGH_RISK": [
            "Refer to hepatology for formal assessment: liver biopsy or transient elastography (FibroScan) to stage fibrosis.",
            "Screen for viral hepatitis (Hep B sAg, Hep C Ab) and treat if positive.",
            "Arrange abdominal ultrasound ± AFP for hepatocellular carcinoma surveillance (every 6 months if cirrhotic).",
            "Counsel complete alcohol cessation; alcohol accelerates fibrosis in all liver disease aetiologies.",
            "Review all medications for hepatotoxicity risk; avoid statins if ALT > 3× ULN acutely.",
            "Nutritional assessment: liver disease increases protein-calorie malnutrition risk.",
        ],
        "ELEVATED_RISK": [
            "Repeat LFTs, AST, ALT, GGT, and full coagulation profile in 4–6 weeks.",
            "Alcohol use assessment (AUDIT score); advise reduction.",
            "Arrange ultrasound abdomen to assess liver echogenicity.",
        ],
        "NORMAL": [
            "APRI score within low-fibrosis range. Maintain healthy weight and alcohol limits (≤14 units/week).",
        ],
    },
    "pulmonology": {
        "HIGH_RISK": [
            "Confirm COPD diagnosis with post-bronchodilator spirometry (FEV1/FVC < 0.70 required per GOLD).",
            "GOLD staging guides pharmacotherapy: SABA for GOLD 1; add LAMA/LABA for GOLD 2+; ICS if frequent exacerbations.",
            "Absolute smoking cessation is the single most effective intervention to slow FEV1 decline.",
            "Arrange chest X-ray and sputum culture to exclude concurrent infection or malignancy.",
            "Pulmonary rehabilitation referral for GOLD 2–4; oxygen assessment if SpO2 ≤ 88%.",
            "Annual influenza and pneumococcal vaccination.",
        ],
        "ELEVATED_RISK": [
            "Repeat spirometry after bronchodilator trial to distinguish COPD from asthma.",
            "Consider high-resolution CT chest if smoking history > 20 pack-years.",
            "Trial of inhaled SABA; assess response to bronchodilation.",
        ],
        "NORMAL": [
            "No obstruction pattern detected. Maintain smoke-free environment; reassess if new dyspnoea or cough develops.",
        ],
    },
    "neurology_stroke": {
        "HIGH_RISK": [
            "Anticoagulation decision required: CHA₂DS₂-VASc ≥ 2 (male) or ≥ 3 (female) typically warrants DOAC therapy — confirm with prescribing physician.",
            "Arrange ECG and 24h Holter to detect paroxysmal atrial fibrillation if not confirmed.",
            "Tight BP control: target < 130/80 mmHg; systolic > 140 is an independent stroke risk factor.",
            "Statin therapy if LDL > 100 mg/dL or ASCVD risk elevated.",
            "If prior TIA/stroke: urgent DWI-MRI and neurology review within 24 h.",
            "Lifestyle: physical activity ≥ 150 min/week, Mediterranean diet, strict smoking cessation.",
        ],
        "ELEVATED_RISK": [
            "Verify and treat modifiable risk factors: BP, glucose, lipids, smoking.",
            "Repeat CHA₂DS₂-VASc annually or if new AF diagnosis.",
        ],
        "NORMAL": [
            "Low stroke risk by current criteria. Maintain BP, cholesterol, and glucose in target ranges.",
        ],
    },
    "infectious_disease": {
        "HIGH_RISK": [
            "🚨 qSOFA ≥ 2 is a sepsis screening flag — escalate immediately to the clinical team.",
            "Draw blood cultures (2 sets) BEFORE starting antibiotics.",
            "Initiate Sepsis-3 Hour Bundle: IV fluid resuscitation (30 mL/kg crystalloid), broad-spectrum antibiotics within 1 hour, lactate measurement.",
            "ICU/HDU referral if haemodynamically unstable or lactate ≥ 2 mmol/L.",
            "Monitor urine output hourly; consider urinary catheter.",
            "Identify and control source of infection; surgical review if abdominal source suspected.",
        ],
        "ELEVATED_RISK": [
            "Monitor closely for clinical deterioration; reassess qSOFA hourly.",
            "Ensure IV access, cultures, and fluids are prepared.",
        ],
        "NORMAL": [
            "Low qSOFA score at this assessment. Continue standard monitoring if clinically indicated.",
        ],
    },
    "rheumatology": {
        "HIGH_RISK": [
            "Refer to rheumatology for formal 2010 ACR/EULAR RA classification and DMARD initiation.",
            "Start methotrexate (or leflunomide if MTX contraindicated) as first-line DMARD after TB screening and LFTs.",
            "Baseline DAS28/CDAI to track treatment response; target remission or low disease activity.",
            "Rule out septic arthritis if acute monoarthritis — joint aspiration for Gram stain and culture.",
            "Osteoporosis prevention: calcium, vitamin D, DEXA scan if planning long-term steroid use.",
        ],
        "ELEVATED_RISK": [
            "Refer to rheumatology for early inflammatory arthritis assessment.",
            "Order RF, anti-CCP, CRP, ESR, and joint X-rays (hands, feet).",
            "NSAIDs for symptomatic relief while awaiting specialist review.",
        ],
        "NORMAL": [
            "Criteria not met for inflammatory arthritis at this assessment. Reassess if symptoms persist > 6 weeks.",
        ],
    },
    "psychiatry": {
        "HIGH_RISK": [
            "⚠️ PHQ-9 ≥ 15 or item 9 endorsed: arrange same-day or next-day psychiatric or GP review.",
            "Safety assessment required — ask directly about suicidal ideation, plan, and access to means.",
            "If immediate risk: initiate local crisis pathway, do not leave patient alone.",
            "First-line treatment for moderate-severe depression: combined CBT + antidepressant (SSRI/SNRI) per NICE/APA guidelines.",
            "Exclude organic causes: TFTs, FBC, B12, folate, HbA1c.",
            "Follow-up in 1–2 weeks after initiating pharmacotherapy; PHQ-9 at every visit.",
        ],
        "ELEVATED_RISK": [
            "PHQ-9 5–14: discuss watchful waiting, structured self-help, or low-intensity CBT.",
            "Reassess PHQ-9 in 2–4 weeks; escalate if worsening.",
            "Screen for bipolar disorder before starting antidepressants (MDQ questionnaire).",
        ],
        "NORMAL": [
            "Minimal depressive symptoms. Provide psychoeducation; reassess if mood deteriorates.",
        ],
    },
    "endocrinology_thyroid": {
        "HIGH_RISK": [
            "Hypothyroidism pattern: initiate levothyroxine at 1.6 mcg/kg/day; recheck TSH in 6–8 weeks.",
            "Hyperthyroidism pattern: arrange thyroid uptake scan; consider thionamide (carbimazole/PTU), radioiodine, or surgery with endocrinology.",
            "Check thyroid antibodies (TPO-Ab, TRAb) to distinguish Hashimoto's from Graves'.",
            "Assess for atrial fibrillation in overt hyperthyroidism (ECG).",
            "Pregnancy-specific thresholds apply — refer obstetric endocrinology if pregnant.",
        ],
        "ELEVATED_RISK": [
            "Subclinical thyroid dysfunction: recheck TSH and free T4 in 3–6 months.",
            "Treat if TSH > 10 mIU/L or symptomatic (subclinical hypothyroidism).",
        ],
        "NORMAL": [
            "Euthyroid. Routine TSH screening every 5 years in asymptomatic adults, or annually if on lithium/amiodarone.",
        ],
    },
    "hematology": {
        "HIGH_RISK": [
            "Characterise anaemia type from MCV: microcytic → iron studies; macrocytic → B12/folate; normocytic → renal/chronic disease.",
            "Iron-deficiency anaemia: identify source of blood loss (GI endoscopy, menstrual history).",
            "Arrange blood film, reticulocyte count, LDH, and haptoglobin to exclude haemolysis.",
            "Transfusion threshold typically Hb < 7 g/dL (or < 8 g/dL if cardiovascular disease) — confirm with clinical team.",
            "Refer haematology if Hb < 8 g/dL or unexplained cause after initial workup.",
        ],
        "ELEVATED_RISK": [
            "Full iron panel (serum iron, ferritin, TIBC) and haematinics (B12, folate).",
            "Dietary counselling: increase iron-rich foods; ascorbic acid enhances absorption.",
        ],
        "NORMAL": [
            "Haemoglobin within normal range. No anaemia by WHO criteria at this assessment.",
        ],
    },
    "dermatology": {
        "HIGH_RISK": [
            "⚠️ ≥ 3 ABCDE criteria met — urgent dermatology referral (within 2 weeks per NICE urgent cancer pathway).",
            "Do NOT perform shave biopsy on suspected melanoma — excision biopsy with 2 mm margin is standard.",
            "Dermoscopy by an experienced clinician prior to biopsy decision.",
            "If melanoma confirmed: sentinel lymph node biopsy, staging CT, and oncology MDT referral.",
            "Document lesion with calibrated photography for monitoring if excision is deferred.",
        ],
        "ELEVATED_RISK": [
            "Routine dermatology review within 4–6 weeks.",
            "Advise strict sun protection (SPF 50+, protective clothing) and avoid tanning beds.",
            "Annual full-body skin check; monthly self-examination.",
        ],
        "NORMAL": [
            "No ABCDE warning signs at this assessment. Continue annual skin checks and sun protection.",
        ],
    },
    "urology": {
        "HIGH_RISK": [
            "PSA > 4 ng/mL: refer to urology for digital rectal examination and shared decision-making on prostate biopsy.",
            "Do not interpret PSA in isolation — age-specific reference ranges and PSA velocity (rate of rise) add important context.",
            "Multi-parametric MRI prostate (mpMRI) before biopsy where available (PRECISION trial evidence).",
            "For LUTS burden: arrange uroflowmetry and post-void residual ultrasound.",
            "Alpha-blockers (tamsulosin) first-line for LUTS/BPH; 5-alpha reductase inhibitors for large prostates.",
        ],
        "ELEVATED_RISK": [
            "Bladder diary and IPSS questionnaire to quantify LUTS severity.",
            "Urine dipstick and MSU to exclude infection.",
            "Lifestyle: reduce evening fluid intake, caffeine, and alcohol.",
        ],
        "NORMAL": [
            "PSA within normal range and minimal LUTS. Routine PSA screening discussion per age and shared decision-making.",
        ],
    },
    "ophthalmology": {
        "HIGH_RISK": [
            "Refer to ophthalmology for dilated fundus examination within 1 month.",
            "Optimise HbA1c (target < 7%), BP (< 130/80 mmHg), and lipids — all independently reduce retinopathy progression.",
            "If proliferative diabetic retinopathy (PDR) detected: pan-retinal photocoagulation or anti-VEGF injection.",
            "Assess for diabetic macular oedema (DME): OCT imaging; anti-VEGF (ranibizumab/faricimab) first-line.",
            "Annual dilated retinal screening mandatory for all diabetic patients.",
        ],
        "ELEVATED_RISK": [
            "Annual dilated retinal photography or ophthalmology review.",
            "Tighten glycaemic and blood pressure control.",
        ],
        "NORMAL": [
            "Low retinopathy risk at current duration and HbA1c. Annual screening still required per diabetes guidelines.",
        ],
    },
    "orthopedics": {
        "HIGH_RISK": [
            "Arrange DXA (DEXA) bone density scan to confirm osteoporosis (T-score ≤ −2.5).",
            "Calculate FRAX 10-year fracture probability with DXA T-score for treatment threshold guidance.",
            "First-line pharmacotherapy: alendronate (weekly oral bisphosphonate); check renal function and dental health first.",
            "Calcium (1000–1200 mg/day) and vitamin D (800–1000 IU/day) supplementation.",
            "Fall prevention programme: balance training, review medications causing dizziness, home hazard assessment.",
            "Refer endocrinology if secondary cause suspected (hyperparathyroidism, malabsorption).",
        ],
        "ELEVATED_RISK": [
            "DXA scan to establish baseline T-score.",
            "Calcium and vitamin D supplementation.",
            "Weight-bearing exercise (walking, resistance training) to maintain bone density.",
        ],
        "NORMAL": [
            "Low fracture risk factor burden. Weight-bearing exercise and adequate calcium/vitamin D intake preventively.",
        ],
    },
}
