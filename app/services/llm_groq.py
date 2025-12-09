import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def call_llm_groq(messages):
    """
    Calls Groq LLM (LLaMA 3 or Mixtral) using ChatCompletion API.
    """

    if not GROQ_API_KEY:
        raise ValueError("Missing GROQ_API_KEY environment variable.")

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": "llama3-8b-8192",   # Or your preferred model
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 300
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=20)
        data = res.json()

        # Extract reply from Groq API
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("Groq LLM Error:", e)
        return "I'm having trouble responding right now. Try again!"
