# core/exceptions.py

class ClinicalEngineException(Exception):
    """Base domain exception for all input-processing and inference pipelines."""
    def __init__(self, message, error_code="GENERIC_ERROR"):
        super().__init__(message)
        self.error_code = error_code


class PhysiologicalBoundsViolation(ClinicalEngineException):
    """Raised when an incoming input exceeds the configured plausible physiological range."""
    def __init__(self, key, val, bounds):
        msg = f"Physiological boundary alert: '{key}' value '{val}' is outside the expected range {bounds}."
        super().__init__(msg, "PHYSIOLOGICAL_OUT_OF_BOUNDS")


class VectorDimensionDriftError(ClinicalEngineException):
    """Raised when a feature vector's length doesn't match what a model was trained on."""
    def __init__(self, expected, received, model_name=""):
        msg = f"Vector dimension mismatch for '{model_name}': expected {expected} features, got {received}."
        super().__init__(msg, "VECTOR_DIMENSION_MISMATCH")


class UnknownEngineTypeError(ClinicalEngineException):
    """Raised when a specialty config declares an engine type the orchestrator doesn't recognize."""
    def __init__(self, specialty_id, engine_type):
        msg = f"Specialty '{specialty_id}' declared unknown engine type '{engine_type}'."
        super().__init__(msg, "UNKNOWN_ENGINE_TYPE")
