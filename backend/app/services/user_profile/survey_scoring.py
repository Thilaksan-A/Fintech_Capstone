import yaml
from pathlib import Path
from typing import Dict, Any, Tuple

from app.constants import (
    ScoreType,
    SurveyCategory,
    TimeScore,
    SocialImpact,
    InvestorType,
)

# Type aliases
ScoreOption = Dict[ScoreType, int]
ScoreOptionMap = Dict[str, ScoreOption]
ScoringMap = Dict[SurveyCategory, ScoreOptionMap]

MODULE_DIR = Path(__file__).parent
SCORE_MAP_PATH = MODULE_DIR / "score_map.yaml"


def load_user_profile_scoring_map() -> ScoringMap:
    """
    Loads the user profile scoring map from a YAML file.
    """

    with open(SCORE_MAP_PATH, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)
    scoring_map: ScoringMap = {}

    # Iterate over survey categories
    for category_key, options_map in config_data.items():
        try:
            category = SurveyCategory(category_key)
        except ValueError:
            raise KeyError(f"Unknown survey category: {category_key}")

        answer_map: ScoreOptionMap = {}
        # Iterate over answer options
        for answer_option, score_map in options_map.items():
            score_option: ScoreOption = {}
            for score_type_key, points in score_map.items():
                try:
                    st = ScoreType(score_type_key)
                except ValueError:
                    raise KeyError(f"Unknown score type: {score_type_key}")
                score_option[st] = int(points)

            answer_map[answer_option] = score_option
        scoring_map[category] = answer_map

    return scoring_map


def calculate_user_profile_scores(
    ans: Dict[str, Any],
    scoring_map: ScoringMap,
) -> Dict[ScoreType, int]:
    """
    Loops over answers and accumulates scores using enums
    """
    totals: Dict[ScoreType, int] = {st: 0 for st in ScoreType}

    for category in SurveyCategory:
        answer = ans.get(category.value, "")
        option_map = scoring_map.get(category, {})
        score_option = option_map.get(answer, {})
        for st, points in score_option.items():
            totals[st] += points

    return totals


def classify_user_profile(
    scores: Dict[ScoreType, int],
) -> Tuple[TimeScore, SocialImpact, InvestorType]:
    """
    Handles enum-based investor profiling
    """

    rs = scores[ScoreType.RISK]
    es = scores[ScoreType.EMOTIONAL]
    ras = scores[ScoreType.RATIONAL]
    fs = scores[ScoreType.FOMO]
    si = scores[ScoreType.SOCIAL]
    ts = scores[ScoreType.TIME]

    if ts <= 0:
        time_enum = TimeScore.SHORT
    elif ts <= 3:
        time_enum = TimeScore.MEDIUM
    else:
        time_enum = TimeScore.LONG

    if si <= 1:
        social_enum = SocialImpact.LOW
    elif si <= 3:
        social_enum = SocialImpact.MEDIUM
    else:
        social_enum = SocialImpact.HIGH

    if rs < 0:
        inv_enum = InvestorType.CAUTIOUS_PRESERVER
    elif rs > 5:
        inv_enum = InvestorType.ADVENTURE_SEEKER
    else:  # medium risk
        strategist_score = ras + (1 if ts >= 5 else 0)
        explorer_score = es + fs + (1 if ts < 5 else 0)
        balanced_score = si

        if (
            strategist_score >= explorer_score
            and strategist_score >= balanced_score
        ):
            inv_enum = InvestorType.DATA_DRIVEN_STRATEGIST
        elif (
            explorer_score >= strategist_score
            and explorer_score >= balanced_score
        ):
            inv_enum = InvestorType.EMOTIONAL_EXPLORER
        else:
            inv_enum = InvestorType.BALANCED_LEARNER

    return time_enum, social_enum, inv_enum
