from app.constants.user import InvestorType
from app.services.forecast.prompt_constructor import construct_gemini_prompt


def test_construct_gemini_prompt_includes_all_fields():
    inv_type = InvestorType.BALANCED_LEARNER
    symbol = "DOGEUSDT"
    rsi, macd, ema, sentiment = 42.1, -0.23, 0.05, 0.15

    prompt = construct_gemini_prompt(
        inv_type,
        symbol,
        rsi,
        macd,
        ema,
        sentiment,
    )

    assert (
        f"AI financial advisor for a {inv_type.value} considering {symbol}"
        in prompt
    )
    assert "- RSI: 42.1" in prompt
    assert "- MACD: -0.23" in prompt
    assert "- EMA: 0.05" in prompt
    assert "–1 to +1): 0.15" in prompt
    assert '"up_5pct_24h": <number>' in prompt
    assert '"down_5pct_24h": <number>' in prompt
