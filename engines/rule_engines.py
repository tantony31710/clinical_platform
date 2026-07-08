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


# ---------------------------------------------------------------------------
# Registry — maps each specialty's "rule_fn" string (see config/specialties.py)
# to its implementing function. orchestrator.py imports this by name; its
# absence (not any deployment/environment issue) was the direct cause of the
# ImportError crashing every single request.
#
# STATUS: only 1 of 13 declared rule_fn names below is actually implemented.
# The other 12 are wired to a placeholder that returns a clear
# "not yet implemented" result instead of crashing — orchestrator.py already
# handles a missing rule_fn gracefully (see the `if rule_fn is None` branch),
# but leaving the name out of this dict entirely still means a KeyError-free,
# non-crashing "not implemented" response rather than silence.
# ---------------------------------------------------------------------------
def _not_yet_implemented(name):
    def _stub(profile):
        return {
            "status": "SYSTEM_FAULT",
            "confidence": 0.0,
            "verdict": f"⚠️ '{name}' scoring logic is not implemented yet.",
        }
    return _stub


RULE_FUNCTIONS = {
    "copd_asthma_risk": respiratory_risk_simplified,
    "cervical_cancer_risk": _not_yet_implemented("cervical_cancer_risk"),
    "liver_disease_risk": _not_yet_implemented("liver_disease_risk"),
    "stroke_risk_chadsvasc": _not_yet_implemented("stroke_risk_chadsvasc"),
    "sepsis_risk_qsofa": _not_yet_implemented("sepsis_risk_qsofa"),
    "rheumatoid_arthritis_risk": _not_yet_implemented("rheumatoid_arthritis_risk"),
    "depression_screen_phq9": _not_yet_implemented("depression_screen_phq9"),
    "thyroid_function_assessment": _not_yet_implemented("thyroid_function_assessment"),
    "anemia_classification_who": _not_yet_implemented("anemia_classification_who"),
    "melanoma_risk_abcde": _not_yet_implemented("melanoma_risk_abcde"),
    "lower_urinary_tract_risk": _not_yet_implemented("lower_urinary_tract_risk"),
    "diabetic_retinopathy_risk": _not_yet_implemented("diabetic_retinopathy_risk"),
    "osteoporosis_risk_frax_like": _not_yet_implemented("osteoporosis_risk_frax_like"),
}
