import json
import re
from typing import Any, Dict, List, Optional, Union
import requests

DEFAULT_TIMEOUT = 30


def _extract_json_block(text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to find the first JSON object in the text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return None
    return None


def call_ollama(
    prompt: str,
    functions: Optional[List[Dict[str, Any]]] = None,
    context: Optional[List[str]] = None,
    host: str = None,
    model: str = None,
    max_tokens: int = 512,
    temperature: float = 0.2,
) -> Union[str, Dict[str, Any]]:
    """
    Call the Ollama HTTP API to generate text.

    - If `functions` is provided, instruct the model to decide on a tool call and
      return a JSON object {"function": "name", "arguments": {...}}.
    - Otherwise, return the generated text directly.
    """
    from bot.config import get_settings

    settings = get_settings()
    base_url = (host or settings.ollama_host).rstrip("/")
    model_name = model or settings.ollama_model

    tool_instructions = ""
    if functions:
        tool_list = []
        for f in functions:
            name = f.get("name")
            description = f.get("description", "")
            params = f.get("parameters", {})
            tool_list.append(f"- {name}: {description}. Parameters: {json.dumps(params)}")
        tool_instructions = (
            "You can use tools to get information. If the user's question requires one of the tools, "
            "respond ONLY with a JSON object describing which tool to call in the form: "
            "{\"function\": \"name\", \"arguments\": { ... }}. "
            "If not, respond directly in natural language.\n\nAvailable tools:\n" + "\n".join(tool_list)
        )

    ctx_text = ""
    if context:
        ctx_text = "\n\nContext:\n" + "\n".join(context[-20:])

    final_prompt = prompt
    if functions:
        final_prompt = tool_instructions + "\n\nUser:\n" + prompt + ctx_text
    else:
        final_prompt = prompt + ctx_text

    payload = {
        "model": model_name,
        "prompt": final_prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.Timeout:
        if functions:
            return {"function": None, "arguments": {}, "error": "timeout"}
        return "Request to LLM timed out. Please try again."
    except requests.RequestException as e:
        if functions:
            return {"function": None, "arguments": {}, "error": str(e)}
        return "LLM service unavailable."

    try:
        data = resp.json()
        generated = data.get("response") or data.get("text") or ""
    except Exception:
        generated = resp.text

    if not functions:
        return generated.strip()

    parsed = _extract_json_block(generated)
    if isinstance(parsed, dict) and "function" in parsed:
        # ensure arguments is dict
        args = parsed.get("arguments")
        if not isinstance(args, dict):
            try:
                args = json.loads(args) if args else {}
            except Exception:
                args = {}
        return {"function": parsed.get("function"), "arguments": args}

    # Fallback: no tool call, treat as direct answer
    return {"function": None, "arguments": {}, "text": generated.strip()}
