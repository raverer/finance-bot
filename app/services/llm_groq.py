import os
from groq import Groq

API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

def call_llm_groq(messages):
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.3,
        )
        return completion.choices[0].message["content"]

    except Exception as e:
        print("GROQ ERROR:", e)
        return "I'm having trouble responding right now. Try again!"
