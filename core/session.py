# core/session.py
from config.specialties import GLOBAL_BASELINE_FEATURES, SPECIALTY_FIELDS


class ClinicalSession:
    """
    Tracks one patient's conversation across the shared global questions and
    whichever specialty tab is currently active. Works for any number of
    specialties registered in config/specialties.py without modification.
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.patient_profile = {}

        self.global_queue = list(GLOBAL_BASELINE_FEATURES.keys())
        self.global_step = 0

        self.fields_state = {}
        for field_id, field_data in SPECIALTY_FIELDS.items():
            self.fields_state[field_id] = {
                "step": 0,
                "queue": list(field_data["registry"].keys()),
            }

    def determine_next_node(self, active_tab):
        """
        Returns ("global", key), ("specialty", key), or ("terminal", None)
        depending on what question (if any) still needs answering.
        """
        if self.global_step < len(self.global_queue):
            return "global", self.global_queue[self.global_step]

        state = self.fields_state[active_tab]
        if state["step"] < len(state["queue"]):
            target_key = state["queue"][state["step"]]

            # Smart skip: if this exact measurement was already captured
            # (globally, or in another specialty tab), don't ask again.
            if target_key in self.patient_profile:
                state["step"] += 1
                return self.determine_next_node(active_tab)

            return "specialty", target_key

        return "terminal", None
