import json
from unittest.mock import patch
from llm.ollama import call_ollama


def test_direct_answer_parsing():
    response = {"response": "Hello world"}
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = response
        mock_post.return_value.raise_for_status.return_value = None
        text = call_ollama("hi", functions=None)
        assert isinstance(text, str)
        assert "Hello" in text


def test_function_call_json_extract():
    # The model returns a JSON instruction to call a tool
    model_text = '{"function": "get_weather", "arguments": {"city": "Moscow"}}'
    response = {"response": model_text}
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = response
        mock_post.return_value.raise_for_status.return_value = None
        out = call_ollama("weather?", functions=[{"name": "get_weather", "parameters": {}}])
        assert isinstance(out, dict)
        assert out.get("function") == "get_weather"
        assert out.get("arguments", {}).get("city") == "Moscow"


def test_function_call_fallback_plain_text():
    model_text = "I think you should call get_weather for Moscow."
    response = {"response": model_text}
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = response
        mock_post.return_value.raise_for_status.return_value = None
        out = call_ollama("weather?", functions=[{"name": "get_weather", "parameters": {}}])
        # Fallback returns dict with text
        assert isinstance(out, dict)
        assert out.get("text")
