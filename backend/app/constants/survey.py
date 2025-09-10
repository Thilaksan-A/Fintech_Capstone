from enum import Enum


class ScoreType(str, Enum):
    RISK = "risk_score"
    EMOTIONAL = "emotional_score"
    RATIONAL = "rational_score"
    TIME = "time_score"
    SOCIAL = "social_impact"
    FOMO = "fomo_score"


class SurveyCategory(str, Enum):
    STRESS_RESPONSE = "stress_response"
    EMOTIONAL_REACTION = "emotional_reaction"
    RISK_PERCEPTION = "risk_perception"
    INCOME_VS_INVESTMENT_BALANCE = "income_vs_investment_balance"
    DEBT_SITUATION = "debt_situation"
    INVESTMENT_EXPERIENCE = "investment_experience"
    INVESTMENT_MOTIVATION = "investment_motivation"
    KNOWLEDGE_LEVEL = "knowledge_level"
    INVESTMENT_PERSONALITY = "investment_personality"
