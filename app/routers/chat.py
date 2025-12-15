from fastapi import APIRouter, HTTPException
from ..schemas import ChatRequest, ChatResponse
import json
import os
import requests

# ============================================================
# USE GROQ ONLY (Railway compatible)
# ============================================================

from ..services.llm_groq import call_llm_groq as call_llm

router = APIRouter(prefix="/chat", tags=["Chat / LLM"])

INTERNAL_BASE = os.getenv("INTERNAL_BASE_URL", "http://127.0.0.1:8000")

# ============================================================
# SYSTEM PROMPTS
# ============================================================

BASE_PROMPT = (
    "You are NiveshBuddy, a modern Indian personal finance assistant. "
    "You explain EMIs, SIPs, budgeting, and mutual funds in clear English. "
    "You do NOT recommend specific mutual funds or stocks. "
    "You suggest categories and allocation logic only. "
    "Always assume Direct mutual fund plans. "
    "Do not mention NAV values. "
    "Add a short educational disclaimer once per response."
)

INTENT_PROMPT = (
    "Extract user intent as JSON only.\n"
    "Supported intents: emi, sip, mf_recommendation, general\n\n"
    "Return format:\n"
    "{\n"
    '  "intent": "emi" | "sip" | "mf_recommendation" | "general",\n'
    '  "income": number or null,\n'
    '  "monthly_amount": number or null,\n'
    '  "years": number or null\n'
    "}"
)

# ============================================================
# INTENT EXTRACTION
# ============================================================

def extract_intent(message: str):
    try:
        res = call_llm([
            {"role": "system", "content": INTENT_PROMPT},
            {"role": "user", "content": message},
        ])
        return json.loads(res)
    except:
        return {"intent": "general"}

# ============================================================
# MAIN CHAT ENDPOINT
# ============================================================

@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest):
    try:
        user_msg = payload.message
        parsed = extract_intent(user_msg)
        intent = parsed.get("intent", "general")

        # ================= SIP BASED ON INCOME =================
        if intent == "mf_recommendation" or intent == "sip":
            income = parsed.get("income")

            if income:
                sip_amount = round(income * 0.12)

                reply = (
                    f"Based on a monthly income of ₹{income:,}, "
                    f"a healthy SIP amount would be around ₹{sip_amount:,} "
                    f"(approximately 10–15% of income).\n\n"
                    "You may consider Direct mutual fund plans across these categories:\n\n"
                    "• A Flexi Cap fund for long-term growth\n"
                    "• A Nifty 50 Index fund for stability\n"
                    "• An ELSS fund if you want tax benefits under Section 80C\n\n"
                    "A long-term horizon of 5–10 years works best for SIP investing.\n\n"
                    "Note: This is for educational purposes only and not investment advice."
                )
                return ChatResponse(reply=reply)

        # ================= GENERAL FINANCE =================
        reply = call_llm([
            {"role": "system", "content": BASE_PROMPT},
            {"role": "user", "content": user_msg},
        ])

        return ChatResponse(reply=reply)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
