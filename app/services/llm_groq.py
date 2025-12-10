import os
from groq import Groq

# Load API key
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

def call_llm_groq(messages):
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.2,
            max_tokens=300
        )
        return completion.choices[0].message["content"]

    except Exception as e:
        print("Groq Error:", e)
        return "I'm having trouble responding right now. Try again!"
