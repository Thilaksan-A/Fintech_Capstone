from .survey_scoring import (
    load_user_profile_scoring_map,
    calculate_user_profile_scores,
    classify_user_profile,
)

USER_PROFILE_SCORING_MAP = load_user_profile_scoring_map()

__all__ = [
    "calculate_user_profile_scores",
    "classify_user_profile",
    "USER_PROFILE_SCORING_MAP",
]
