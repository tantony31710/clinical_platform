# ---------------------------------------------------------------------------
# Respiratory — Simplified Lung Function / COPD check (not a full spirometry)
# ---------------------------------------------------------------------------
def respiratory_risk_simplified(profile):
    cough = yes(profile, "ChronicCough")
    wheeze = yes(profile, "Wheezing")
    dyspnea = yes(profile, "Dyspnea") # Shortness of breath

    score = (cough * 1) + (wheeze * 1) + (dyspnea * 2)

    if score >= 3:
        return {"status": "HIGH_RISK", "confidence": 85.0,
                "verdict": "🚨 SIGNIFICANT RESPIRATORY SYMPTOMS DETECTED — Consider spirometry or pulmonary evaluation."}
    if score >= 1:
        return {"status": "ELEVATED_RISK", "confidence": 60.0,
                "verdict": "⚠️ MILD RESPIRATORY SYMPTOMS PRESENT — Monitor symptoms and consult if they persist."}
    return {"status": "NORMAL", "confidence": 88.0,
            "verdict": "✅ NO SIGNIFICANT RESPIRATORY SYMPTOMS DETECTED"}
