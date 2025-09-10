from enum import Enum


class TimeScore(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class SocialImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InvestorType(str, Enum):
    CAUTIOUS_PRESERVER = "Cautious Preserver"
    ADVENTURE_SEEKER = "Adventure Seeker"
    DATA_DRIVEN_STRATEGIST = "Data-Driven Strategist"
    EMOTIONAL_EXPLORER = "Emotional Explorer"
    BALANCED_LEARNER = "Balanced Learner"
