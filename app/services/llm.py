import requests

OLLAMA_URL = "http://localhost:11434/api/chat"


def call_llm(messages, model: str = "llama3:latest") -> str:
    """
    messages: list of dicts like:
      [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    Returns the final assistant message as a string.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()

    # Ollama returns {"message": {"role":"assistant","content":"..."} , ...}
    # or a list in some versions; handle both patterns.
    if isinstance(data, dict) and "message" in data:
        return data["message"]["content"]

    # Fallback: if data is list-like or different structure
    if isinstance(data, list) and len(data) > 0 and "message" in data[-1]:
        return data[-1]["message"]["content"]

    # Fallback generic
    return str(data)
