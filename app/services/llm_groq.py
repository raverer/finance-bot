import os
from groq import Groq

def call_llm_groq(messages):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "Backend error: Missing GROQ_API_KEY"

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
        )

        # ✅ Correct extraction for new Groq client
        return response.choices[0].message.content

    except Exception as e:
        print("🔥 GROQ ERROR:", e)
        return f"Groq error: {str(e)}"
