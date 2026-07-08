# engines/orchestrator.py
from config.specialties import GLOBAL_BASELINE_FEATURES, SPECIALTY_FIELDS
from core.exceptions import UnknownEngineTypeError
from engines.rule_engines import RULE_FUNCTIONS


import logging

logger = logging.getLogger(__name__)

def fetch_feature(profile, key, specialty_id):
    """
    Resolves a single feature value for model input: prefers what the patient
    already answered, falls back to the configured default, and normalizes
    yes/no choice answers to 1.0/0.0 for numeric model matrices.
    """
    val = profile.get(key)

    # 1. Resolve value (Profile -> Global -> Specialty -> 0.0)
    if val is None:
        if key in GLOBAL_BASELINE_FEATURES:
            val = GLOBAL_BASELINE_FEATURES[key].get("default", 0.0)
            logger.debug("[Orchestrator] Using global default for '%s': %s", key, val)
        else:
            registry = SPECIALTY_FIELDS.get(specialty_id, {}).get("registry", {})
            val = registry.get(key, {}).get("default", 0.0)
            if val != 0.0:
                logger.debug("[Orchestrator] Using specialty default for '%s': %s", key, val)
            else:
                logger.debug("[Orchestrator] No value or default found for '%s'. Defaulting to 0.0", key)

    # 2. Normalization & Type Conversion
    if isinstance(val, str):
        cleaned = val.strip().lower()
        if cleaned == "yes":
            return 1.0
        if cleaned == "no":
            return 0.0
        try:
            return float(cleaned)
        except ValueError:
            logger.error("[Orchestrator] Failed to convert string '%s' to float for key '%s'.", cleaned, key)
            return 0.0

    try:
        return float(val)
    except (TypeError, ValueError) as e:
        logger.error("[Orchestrator] Type conversion failed for key '%s' with value '%s': %s", key, val, e)
        return 0.0


def compile_comprehensive_diagnostics(profile, ml_engines):
    """
    Runs every registered specialty's engine against the current patient
    profile. Adding a new specialty to config/specialties.py (ML or rule)
    requires zero changes here.

    ml_engines: dict {specialty_id: MLModelEngine} for every "ml"-type specialty.
    Returns: dict {specialty_id: {status, verdict, confidence, engine_type}}
    """
    results = {}

    for specialty_id, spec in SPECIALTY_FIELDS.items():
        engine_cfg = spec["engine"]
        engine_type = engine_cfg["type"]

        try:
            if engine_type == "ml":
                engine = ml_engines.get(specialty_id)
                if engine is None or not engine.is_available():
                    results[specialty_id] = {
                        "status": "SYSTEM_FAULT",
                        "verdict": f"Model unavailable for '{specialty_id}'" + (f": {engine.load_error}" if engine else ""),
                        "confidence": 0.0, "engine_type": "ml", "top_drivers": [],
                    }
                    continue

                ordered_values = [fetch_feature(profile, key, specialty_id) for key in engine_cfg["feature_order"]]
                outcome = engine.predict(ordered_values)

                if outcome["uncertain"]:
                    status = "INDETERMINATE"
                    verdict = ("🟡 INDETERMINATE — Calibrated model confidence falls in the genuinely uncertain "
                               "range. This case should not be resolved by the model; route to a clinician for "
                               "direct evaluation rather than trusting an automated high/low call.")
                else:
                    status = "HIGH_RISK" if outcome["prediction"] == 1 else "NORMAL"
                    verdict = engine_cfg["positive_verdict"] if outcome["prediction"] == 1 else engine_cfg["negative_verdict"]

                results[specialty_id] = {
                    "status": status, "verdict": verdict, "confidence": outcome["confidence"],
                    "engine_type": "ml", "top_drivers": outcome["top_drivers"],
                }

            elif engine_type == "rule":
                rule_fn = RULE_FUNCTIONS.get(engine_cfg["rule_fn"])
                if rule_fn is None:
                    results[specialty_id] = {
                        "status": "SYSTEM_FAULT", "verdict": f"Rule engine '{engine_cfg['rule_fn']}' not registered.",
                        "confidence": 0.0, "engine_type": "rule",
                    }
                    continue
                outcome = rule_fn(profile)
                outcome["engine_type"] = "rule"
                outcome.setdefault("top_drivers", [])
                results[specialty_id] = outcome

            else:
                raise UnknownEngineTypeError(specialty_id, engine_type)

        except Exception as e:
            logger.error("[Orchestrator Fault] '%s' pipeline crashed: %s", specialty_id, e, exc_info=True)
            results[specialty_id] = {
                "status": "SYSTEM_FAULT", 
                "verdict": f"Pipeline fault: {str(e)}",
                "confidence": 0.0, 
                "engine_type": engine_type
            }

    return results
