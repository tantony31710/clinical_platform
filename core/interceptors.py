# core/interceptors.py
import sys
from core.exceptions import PhysiologicalBoundsViolation


class MetricSanitizer:
    """
    Validates and normalizes a single incoming chat answer against the
    validation rules declared for that field in config/specialties.py.
    """

    @staticmethod
    def process_and_validate(key, input_value, validation_rules):
        if not validation_rules:
            return input_value

        rule_type = validation_rules.get("type", "numeric")

        if rule_type == "numeric":
            try:
                cleaned_value = float(input_value)
            except (ValueError, TypeError):
                raise ValueError(f"'{key}' requires a numeric value.")

            min_allowed = validation_rules.get("min_allowed", -sys.maxsize)
            max_allowed = validation_rules.get("max_allowed", sys.maxsize)

            if cleaned_value < min_allowed or cleaned_value > max_allowed:
                raise PhysiologicalBoundsViolation(key, cleaned_value, (min_allowed, max_allowed))

            return cleaned_value

        elif rule_type == "choice":
            cleaned_string = str(input_value).strip().lower()
            allowed_choices = validation_rules.get("choices", [])

            if cleaned_string not in allowed_choices:
                raise ValueError(f"'{cleaned_string}' is not valid for '{key}'. Expected one of: {allowed_choices}")

            return cleaned_string

        return input_value
