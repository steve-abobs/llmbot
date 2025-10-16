import json
import os
import threading
from typing import Dict, List

_lock = threading.Lock()


def _ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _read_all(path: str) -> Dict[str, List[Dict[str, str]]]:
    _ensure_file(path)
    with _lock:
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}


def _write_all(path: str, data: Dict[str, List[Dict[str, str]]]):
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def append_user_message(path: str, user_id: str, text: str):
    data = _read_all(path)
    messages = data.get(user_id, [])
    messages.append({"role": "user", "text": text})
    data[user_id] = messages[-200:]
    _write_all(path, data)


def append_bot_message(path: str, user_id: str, text: str):
    data = _read_all(path)
    messages = data.get(user_id, [])
    messages.append({"role": "assistant", "text": text})
    data[user_id] = messages[-200:]
    _write_all(path, data)


def get_context(path: str, user_id: str, limit: int = 10) -> List[str]:
    data = _read_all(path)
    messages = data.get(user_id, [])
    return [f"{m['role']}: {m['text']}" for m in messages[-limit:]]
