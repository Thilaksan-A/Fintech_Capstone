import textwrap
from app.constants.user import InvestorType
from app.constants.investor_prompts import INVESTOR_PROMPTS


def construct_gemini_prompt(
    inv_type: InvestorType,
    symbol: str,
    rsi: float,
    macd: float,
    ema: float,
    sentiment: float,
) -> str:
    blurb = INVESTOR_PROMPTS[inv_type].strip()
    return textwrap.dedent(
        f"""
        You are an AI financial advisor for a {inv_type.value} considering {symbol}.
        {blurb}

        Here are the current technicals and sentiment:
        - RSI: {rsi:.5f}
        - MACD: {macd:.5f}
        - EMA: {ema:.5f}
        - Social sentiment score (–1 to +1): {sentiment:.2f}

        Based on these values, what is the probability (0–100%) that:
          1. Price will rise by at least 5% in the next 24 hours?
          2. Price will fall by more than 5% in the next 24 hours?
          3. A clear investment recommendation for the {inv_type.value}: should
              they **buy**, **wait**, or **sell** before taking action? Explain
              briefly why, considering the investor’s risk profile,
              current market data and also the nature of the coin itself.

        Answer in JSON:
        ```json
        {{
          "up_5pct_24h": <number>,
          "down_5pct_24h": <number>,
          "recommendation": "<buy|wait|sell>",
          "reasoning": "<brief explanation tailored to the investor profile>"
        }}
        ```
    """,
    )
