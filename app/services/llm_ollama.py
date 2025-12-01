import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

def call_llm_ollama(messages, model: str = "llama3"):
    """
    Call LLaMA 3 model using local Ollama.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, dict) and "message" in data:
        return data["message"]["content"]

    if isinstance(data, list) and len(data) > 0 and "message" in data[-1]:
        return data[-1]["message"]["content"]

    return str(data)
