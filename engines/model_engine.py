# engines/model_engine.py
import warnings
import json
import numpy as np
import pickle
import os
import logging
from core.exceptions import VectorDimensionDriftError

warnings.filterwarnings("ignore", message="X does not have valid feature names")

logger = logging.getLogger(__name__)


class MLModelEngine:
    """
    Thin, generic wrapper around a fitted, CALIBRATED scikit-learn pipeline.
    No per-disease branching here — every ML specialty goes through the same
    code path. Specialty-specific behavior lives in config/specialties.py.

    Confidence values come from a sigmoid-calibrated classifier (see
    models/train_models.py), not raw uncalibrated model votes, so a "78%"
    here is meant to track real-world observed frequency, not just
    "78% of trees voted yes."
    """

    # Predictions landing in this probability band are reported as
    # INDETERMINATE rather than forced into a high/low verdict — calibrated
    # models near 50/50 genuinely don't know, and pretending otherwise is
    # exactly the kind of overclaiming that makes software unsafe to trust.
    UNCERTAIN_BAND = (0.40, 0.60)

    def __init__(self, model_path, expected_dim, specialty_id):
        self.specialty_id = specialty_id
        self.expected_dim = expected_dim
        self.model = None
        self.load_error = None
        self.feature_importances = []

        if not os.path.exists(model_path):
            self.load_error = f"Model file not found at {model_path}."
            logger.error("[ModelEngine] Model file missing for '%s': %s", specialty_id, model_path)
        else:
            try:
                with open(model_path, "rb") as f:
                    loaded = pickle.load(f)
                if not hasattr(loaded, "predict"):
                    self.load_error = f"Loaded object for '{specialty_id}' has no predict() method."
                    logger.error("[ModelEngine] Invalid model object for '%s'", specialty_id)
                else:
                    self.model = loaded
                    logger.info("[ModelEngine] Successfully loaded model for '%s'", specialty_id)
            except Exception as e:
                self.load_error = f"Failed to load model for '{specialty_id}': {e}"
                logger.error("[ModelEngine] Exception loading model for '%s': %s", specialty_id, e)

        self._load_training_report(model_path)

    def _load_training_report(self, model_path):
        """Pulls this model's feature-importance ranking from the training report, if present."""
        report_path = os.path.join(os.path.dirname(model_path), "training_report.json")
        if not os.path.exists(report_path):
            return
        try:
            with open(report_path) as f:
                report = json.load(f)
            model_filename = os.path.basename(model_path)
            for entry in report.values():
                if entry.get("model_file") == model_filename:
                    self.feature_importances = entry.get("feature_importances", [])
                    logger.debug("[ModelEngine] Loaded feature importances for '%s'", self.specialty_id)
                    break
        except Exception as e:
            logger.error("[ModelEngine] Could not read training report for '%s': %s", self.specialty_id, e)

    def is_available(self):
        return self.model is not None

    def predict(self, ordered_values):
        """
        Returns a dict: {prediction, confidence, uncertain, top_drivers}.
        confidence is the calibrated probability (%) of the predicted class.
        uncertain=True means the calibrated probability fell inside the
        "genuinely unclear" band and should be flagged for clinician review
        rather than reported as a confident verdict.
        """
        if len(ordered_values) != self.expected_dim:
            raise VectorDimensionDriftError(self.expected_dim, len(ordered_values), self.specialty_id)

        if self.model is None:
            raise RuntimeError(self.load_error or "Model unavailable.")

        # 1. Input Validation
        try:
            feature_matrix = np.array(ordered_values, dtype=float)
        except (TypeError, ValueError) as e:
            logger.error("[ModelEngine] Non-numeric feature vector provided for '%s': %s", self.specialty_id, e)
            raise ValueError(f"Non-numeric features provided for {self.specialty_id}")

        # 2. Inference
        try:
            prediction = int(self.model.predict(feature_matrix)[0])
        except Exception as e:
            logger.error("[ModelEngine] Prediction error for '%s': %s", self.specialty_id, e)
            raise RuntimeError(f"Inference failed for {self.specialty_id}")

        # 3. Probability Calibration
        positive_proba = 0.5
        if hasattr(self.model, "predict_proba"):
            try:
                proba_row = self.model.predict_proba(feature_matrix)[0]
                positive_proba = float(proba_row[1]) if len(proba_row) > 1 else float(proba_row[0])
            except Exception as e:
                logger.warning("[ModelEngine] Could not get predict_proba for '%s': %s", self.specialty_id, e)

        confidence_of_prediction = (positive_proba if prediction == 1 else (1.0 - positive_proba)) * 100.0
        uncertain = self.UNCERTAIN_BAND[0] <= positive_proba <= self.UNCERTAIN_BAND[1]

        logger.info("[ModelEngine] Inference success for '%s': Pred=%d, Conf=%.2f%%, Uncertain=%s", 
                    self.specialty_id, prediction, confidence_of_prediction, uncertain)

        return {
            "prediction": prediction,
            "confidence": confidence_of_prediction,
            "uncertain": uncertain,
            "top_drivers": self.feature_importances[:3],
        }

