from typing import Dict
from app.constants.user import InvestorType

INVESTOR_PROMPTS: Dict[InvestorType, str] = {
    InvestorType.CAUTIOUS_PRESERVER: """
        The investor is highly risk‑averse, dislikes volatility, and will only
        take very small, safe positions.
        They respond poorly to uncertainty and prefer capital preservation over
        gains.
        """,
    InvestorType.ADVENTURE_SEEKER: """
        The investor loves high‑risk, high‑reward plays.
        They are comfortable with large price swings, driven by the thrill of
        big upside.
    """,
    InvestorType.DATA_DRIVEN_STRATEGIST: """
        The investor bases decisions on logical analysis and clear data.
        They want statistical probabilities and tend to ignore FOMO or hype.
        They are patient and have long-term horizons.
    """,
    InvestorType.EMOTIONAL_EXPLORER: """
        The investor follows gut feelings and social buzz/trends.
        They’re swayed by headlines, influencer sentiment, and novelty.
    """,
    InvestorType.BALANCED_LEARNER: """
        The investor values a middle path: some risk, some caution, and will
        balance social signals with data.
        They are new but curious and open to learning.
    """,
}
