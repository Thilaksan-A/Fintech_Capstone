import json
from google import genai
from google.genai import errors
from app.services.forecast.prompt_constructor import construct_gemini_prompt
from app.constants.user import InvestorType
from app.env import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(
    inv_type: InvestorType,
    symbol: str,
    indicators: dict[str, float],
) -> dict:
    prompt = construct_gemini_prompt(
        inv_type,
        symbol,
        indicators["rsi"],
        indicators["macd"],
        indicators["ema"],
        indicators.get("sentiment", 0.0),
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )
    except errors.APIError as e:
        raise RuntimeError("Gemini API call failed") from e

    raw = response.text

    clean = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse Gemini response as JSON. Response content: {clean}",
        ) from e
