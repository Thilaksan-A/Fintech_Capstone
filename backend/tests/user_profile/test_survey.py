import pytest
from unittest.mock import patch, mock_open
from app.services.user_profile import (
    load_user_profile_scoring_map,
    calculate_user_profile_scores,
    classify_user_profile,
)
from app.constants.survey import SurveyCategory, ScoreType
from app.constants.user import TimeScore, SocialImpact, InvestorType


@pytest.fixture(scope="module")
def mock_yaml_content():
    return """
stress_response:
  "Not knowing what to do when the market drops":
    risk_score: -2
    emotional_score: 3
emotional_reaction:
  "I'd panic but wouldn't know what to do":
    risk_score: -2
    emotional_score: 3
    social_impact: 1
risk_perception:
  "Uncertainty but also potential gain":
    risk_score: -1
income_vs_investment_balance:
  "Between 5% and 15%":
    time_score: 1
debt_situation:
  "No, I have no debt":
    risk_score: -1
    time_score: 1
investment_experience:
  "Stocks":
    rational_score: 1
    social_impact: 1
investment_motivation:
  "To learn and have fun":
    rational_score: 1
    social_impact: 1
knowledge_level:
  "I'm at an intermediate level":
    rational_score: 1
    time_score: 1
investment_personality:
  "Balanced: I can handle some risk, but nothing extreme":
    risk_score: 1
"""


@pytest.fixture(scope="module")
def scoring_map(mock_yaml_content):
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        return load_user_profile_scoring_map()


def test_load_scoring_map_contains_all_categories(mock_yaml_content):
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        scoring_map = load_user_profile_scoring_map()

        for category in SurveyCategory:
            assert category in scoring_map


def test_calculate_scores_simple_case(scoring_map):
    answers = {
        "stress_response": "Not knowing what to do when the market drops",  # risk_score: -2, emotional_score: 3
        "emotional_reaction": "I'd panic but wouldn't know what to do",  # risk_score -2, emotional_score 3, social_impact: 1
        "risk_perception": "Uncertainty but also potential gain",  # risk_score: -1
        "income_vs_investment_balance": "Between 5% and 15%",  # time_score: 1
        "debt_situation": "No, I have no debt",  # risk_score: -1, time_score: 1
        "investment_experience": "Stocks",  # rational_score: 1, social_impact: 1
        "investment_motivation": "To learn and have fun",  # rational_score: 1, social_impact: 1
        "knowledge_level": "I'm at an intermediate level",  # rational_score: 1, time_score: 1
        "investment_personality": "Balanced: I can handle some risk, but nothing extreme",  # risk_score: 1
    }
    scores = calculate_user_profile_scores(answers, scoring_map)

    assert scores[ScoreType.RISK] == -5
    assert scores[ScoreType.EMOTIONAL] == 6
    assert scores[ScoreType.TIME] == 3


def test_classify_user_variants():
    # Low Risk
    scores = {st: 0 for st in ScoreType}
    scores[ScoreType.TIME] = -1
    scores[ScoreType.SOCIAL] = 0
    scores[ScoreType.RISK] = -5
    t, s, inv = classify_user_profile(scores)
    assert t is TimeScore.SHORT
    assert s is SocialImpact.LOW
    assert inv is InvestorType.CAUTIOUS_PRESERVER

    # High Risk
    scores[ScoreType.TIME] = 10
    scores[ScoreType.SOCIAL] = 10
    scores[ScoreType.RISK] = 10
    t, s, inv = classify_user_profile(scores)
    assert t is TimeScore.LONG
    assert s is SocialImpact.HIGH
    assert inv is InvestorType.ADVENTURE_SEEKER

    # Medium Risk
    scores = {st: 0 for st in ScoreType}
    scores[ScoreType.RISK] = 2
    scores[ScoreType.RATIONAL] = 3
    scores[ScoreType.EMOTIONAL] = 1
    scores[ScoreType.FOMO] = 1
    scores[ScoreType.SOCIAL] = 0
    scores[ScoreType.TIME] = 0
    t, s, inv = classify_user_profile(scores)

    assert inv is InvestorType.DATA_DRIVEN_STRATEGIST


def test_load_scoring_map_invalid_category():
    invalid_yaml = """
invalid_category:
  "Some answer":
    risk_score: 1
"""
    with patch("builtins.open", mock_open(read_data=invalid_yaml)):
        with pytest.raises(KeyError, match="Unknown survey category"):
            load_user_profile_scoring_map()


def test_load_scoring_map_invalid_score_type():
    invalid_yaml = """
stress_response:
  "Some answer":
    invalid_score_type: 1
"""
    with patch("builtins.open", mock_open(read_data=invalid_yaml)):
        with pytest.raises(KeyError, match="Unknown score type"):
            load_user_profile_scoring_map()
