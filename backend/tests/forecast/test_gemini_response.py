import pytest
from unittest.mock import patch, MagicMock

from app.services.forecast.gemini_client import ask_gemini
from app.constants.user import InvestorType


@patch('app.services.forecast.gemini_client.client')
def test_gemini_api_response_format(mock_client):
    """Test that ask_gemini returns properly formatted response"""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.text = '''```json
    {
        "up_5pct_24h": 65.5,
        "down_5pct_24h": 25.0,
        "recommendation": "buy",
        "reasoning": "Strong technical indicators suggest upward momentum for data-driven investors."
    }
    ```'''

    mock_client.models.generate_content.return_value = mock_response

    # Test data
    inv_type = InvestorType.DATA_DRIVEN_STRATEGIST
    symbol = "BTCUSDT"
    indicators = {
        "rsi": 50.0,
        "macd": 0.0,
        "ema": 0.0,
        "sentiment": 0.0,
    }

    # Call the function
    result = ask_gemini(inv_type, symbol, indicators)

    # Verify the result structure
    assert isinstance(result, dict), "Expected a dict from ask_gemini"
    assert "up_5pct_24h" in result, "Missing 'up_5pct_24h' key"
    assert "down_5pct_24h" in result, "Missing 'down_5pct_24h' key"
    assert "recommendation" in result, "Missing 'recommendation' key"
    assert "reasoning" in result, "Missing 'reasoning' key"

    # Verify value ranges and types
    for key in ("up_5pct_24h", "down_5pct_24h"):
        val = result[key]
        assert isinstance(val, (int, float)), f"{key} should be a number"
        assert 0 <= val <= 100, f"{key} should be between 0 and 100, got {val}"

    assert result["recommendation"] in [
        "buy",
        "wait",
        "sell",
    ], "Invalid recommendation"
    assert isinstance(result["reasoning"], str), "Reasoning should be a string"

    # Verify the API was called with correct parameters
    mock_client.models.generate_content.assert_called_once()
    call_args = mock_client.models.generate_content.call_args
    assert call_args[1]["model"] == "gemini-2.0-flash-lite"
    assert symbol in call_args[1]["contents"]


@patch('app.services.forecast.gemini_client.client')
def test_gemini_json_parse_error(mock_client):
    """Test that ask_gemini handles invalid JSON responses"""
    # Mock invalid JSON response
    mock_response = MagicMock()
    mock_response.text = "Invalid JSON response"
    mock_client.models.generate_content.return_value = mock_response

    inv_type = InvestorType.DATA_DRIVEN_STRATEGIST
    symbol = "BTCUSDT"
    indicators = {"rsi": 50.0, "macd": 0.0, "ema": 0.0, "sentiment": 0.0}

    with pytest.raises(
        RuntimeError,
        match="Failed to parse Gemini response as JSON",
    ):
        ask_gemini(inv_type, symbol, indicators)
